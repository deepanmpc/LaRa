"""
LaRa Vector Memory — ChromaDB RAG Layer (Section 16, lara_memory_architecture_full_v2.md)

Provides optional semantic recall of past stories and educational themes.
NEVER stores raw conversation. Stores structured summaries only.

Rules:
- Store summaries only (not dialogue lines)
- Max 3 retrievals per session
- Never inject raw conversation
- Similarity threshold to avoid hallucination (min score 0.6)
- Stories soft-expire after 90 days (via metadata filter)
- Summaries must pass length validation before storage
"""

import logging
import time
import os
from dataclasses import dataclass, field
from typing import Optional

try:
    import chromadb
    from chromadb.config import Settings
    CHROMADB_AVAILABLE = True
except ImportError:
    CHROMADB_AVAILABLE = False
    logging.warning("[VectorMemory] ChromaDB not installed. Vector memory disabled.")


# ── Constants ──────────────────────────────────────────────────────────────────
MAX_RETRIEVALS_PER_SESSION = 3
MIN_SIMILARITY_SCORE       = 0.60   # Only inject if relevance ≥ 60%
MAX_SUMMARY_LENGTH         = 200    # Characters — prevent transcript smuggling
MIN_SUMMARY_LENGTH         = 10     # Reject trivially short summaries
STORY_EXPIRY_DAYS          = 90     # Soft-expire stories after N days
COLLECTION_NAME            = "lara_story_summaries"

# Trigger phrases that indicate the child wants a story / recall
STORY_TRIGGERS = [
    "tell me a story",
    "remember when",
    "the story about",
    "can we do that again",
    "like last time",
    "what was that story",
    "tell me about",
    "i want to hear about",
]


@dataclass
class RetrievedMemory:
    """A single retrieved story/theme memory."""
    summary: str
    concept: str
    relevance: float
    days_ago: float


class VectorMemory:
    """
    ChromaDB-backed semantic memory for story summaries and educational themes.
    Retrieved summaries are injected naturally into the LLM prompt.
    """

    def __init__(self, persist_dir: str = None):
        """
        Args:
            persist_dir: Directory to persist ChromaDB data.
                         Defaults to src/lara_vector_store/
        """
        self._enabled = CHROMADB_AVAILABLE
        self._user_id: Optional[str] = None
        self._session_retrievals = 0        # Counter reset each session
        self._collection = None
        self._client = None

        if not self._enabled:
            return

        # Default persist path next to user_memory.db
        if persist_dir is None:
            persist_dir = os.path.join(
                os.path.dirname(os.path.abspath(__file__)),
                "lara_vector_store"
            )
        os.makedirs(persist_dir, exist_ok=True)

        try:
            self._client = chromadb.PersistentClient(
                path=persist_dir,
                settings=Settings(anonymized_telemetry=False)
            )
            self._collection = self._client.get_or_create_collection(
                name=COLLECTION_NAME,
                metadata={"hnsw:space": "cosine"}
            )
            logging.info(
                f"[VectorMemory] ChromaDB ready at {persist_dir}. "
                f"Documents: {self._collection.count()}"
            )
        except Exception as e:
            logging.error(f"[VectorMemory] Failed to initialize ChromaDB: {e}")
            self._enabled = False

    def set_user(self, user_id: str):
        """Set active user and reset session retrieval counter."""
        self._user_id = user_id
        self._session_retrievals = 0
        logging.info(f"[VectorMemory] User set: {user_id}")

    def reset_session(self):
        """Call at session start to reset the retrieval cap."""
        self._session_retrievals = 0

    # ══════════════════════════════════════════════════════════════════════════
    # STORAGE
    # ══════════════════════════════════════════════════════════════════════════

    def store_story_summary(self, summary: str, concept: str = "general") -> bool:
        """
        Store a story/theme summary in the vector store.

        Args:
            summary: Short STRUCTURED summary (not a transcript). Max 200 chars.
            concept: Educational concept (e.g., "counting", "colors").

        Returns:
            True if stored, False if rejected or disabled.
        """
        if not self._enabled or not self._user_id:
            return False

        # Validation guards (Section 13: all writes pass validation)
        summary = summary.strip()
        if len(summary) < MIN_SUMMARY_LENGTH:
            logging.warning("[VectorMemory] Summary too short — rejected.")
            return False
        if len(summary) > MAX_SUMMARY_LENGTH:
            summary = summary[:MAX_SUMMARY_LENGTH]
            logging.warning("[VectorMemory] Summary truncated to 200 chars.")

        now = time.time()
        doc_id = f"{self._user_id}_{concept}_{int(now)}"

        try:
            self._collection.add(
                ids=[doc_id],
                documents=[summary],
                metadatas=[{
                    "user_id": self._user_id,
                    "concept": concept,
                    "timestamp": now,
                }]
            )
            logging.info(f"[VectorMemory] Stored: [{concept}] {summary[:60]}")
            return True
        except Exception as e:
            logging.error(f"[VectorMemory] Store failed: {e}")
            return False

    # ══════════════════════════════════════════════════════════════════════════
    # RETRIEVAL
    # ══════════════════════════════════════════════════════════════════════════

    def retrieve_relevant(self, query: str, n: int = 1) -> list[RetrievedMemory]:
        """
        Retrieve relevant past story/theme summaries for a query.

        Safety gates:
        - Max 3 retrievals per session (prevents context overflow)
        - Min similarity score 0.60 (prevents hallucination)
        - Stories older than STORY_EXPIRY_DAYS are filtered out

        Args:
            query: The user's utterance or intent.
            n: Number of results to return.

        Returns:
            List of RetrievedMemory objects (may be empty).
        """
        if not self._enabled or not self._user_id:
            return []

        if self._session_retrievals >= MAX_RETRIEVALS_PER_SESSION:
            logging.debug("[VectorMemory] Session retrieval cap reached.")
            return []

        if self._collection.count() == 0:
            return []

        # Expiry filter
        cutoff_ts = time.time() - (STORY_EXPIRY_DAYS * 86400)

        try:
            results = self._collection.query(
                query_texts=[query],
                n_results=min(n, self._collection.count()),
                where={
                    "$and": [
                        {"user_id": {"$eq": self._user_id}},
                        {"timestamp": {"$gte": cutoff_ts}},
                    ]
                },
                include=["documents", "metadatas", "distances"]
            )
        except Exception as e:
            logging.error(f"[VectorMemory] Query failed: {e}")
            return []

        memories = []
        docs  = results.get("documents",  [[]])[0]
        metas = results.get("metadatas",  [[]])[0]
        dists = results.get("distances",  [[]])[0]

        for doc, meta, dist in zip(docs, metas, dists):
            # ChromaDB cosine distance: 0 = identical, 2 = opposite
            # Convert to similarity: 1 - dist/2
            similarity = 1.0 - (dist / 2.0)
            if similarity < MIN_SIMILARITY_SCORE:
                logging.debug(f"[VectorMemory] Low similarity ({similarity:.2f}) — skipped.")
                continue

            days_ago = (time.time() - meta.get("timestamp", 0)) / 86400

            memories.append(RetrievedMemory(
                summary=doc,
                concept=meta.get("concept", "general"),
                relevance=round(similarity, 2),
                days_ago=round(days_ago, 1),
            ))

        if memories:
            self._session_retrievals += len(memories)
            logging.info(
                f"[VectorMemory] Retrieved {len(memories)} memories "
                f"(session total: {self._session_retrievals})"
            )

        return memories

    def get_context_for_llm(self, query: str) -> str:
        """
        Build a ready-to-inject LLM context string from relevant memories.
        Returns empty string if no relevant memories or cap reached.
        """
        memories = self.retrieve_relevant(query, n=MAX_RETRIEVALS_PER_SESSION)
        if not memories:
            return ""

        lines = ["[Past Story Context — reference naturally, do NOT list these:"]
        for m in memories:
            lines.append(f"  • {m.summary} (concept: {m.concept})")
        lines.append("]")

        return "\n".join(lines)

    # ══════════════════════════════════════════════════════════════════════════
    # STORY TRIGGER DETECTION
    # ══════════════════════════════════════════════════════════════════════════

    @staticmethod
    def is_story_trigger(text: str) -> bool:
        """
        Check if the user's utterance indicates they want a story or recall.
        """
        text_lower = text.lower().strip()
        return any(trigger in text_lower for trigger in STORY_TRIGGERS)

    # ══════════════════════════════════════════════════════════════════════════
    # CLEANUP
    # ══════════════════════════════════════════════════════════════════════════

    def cleanup_expired(self):
        """Delete all stories older than STORY_EXPIRY_DAYS. Call periodically."""
        if not self._enabled or not self._user_id:
            return

        cutoff_ts = time.time() - (STORY_EXPIRY_DAYS * 86400)
        try:
            # Get all IDs for this user older than cutoff
            result = self._collection.get(
                where={
                    "$and": [
                        {"user_id": {"$eq": self._user_id}},
                        {"timestamp": {"$lt": cutoff_ts}},
                    ]
                },
                include=["metadatas"]
            )
            ids = result.get("ids", [])
            if ids:
                self._collection.delete(ids=ids)
                logging.info(f"[VectorMemory] Cleaned up {len(ids)} expired stories.")
        except Exception as e:
            logging.warning(f"[VectorMemory] Cleanup failed: {e}")
