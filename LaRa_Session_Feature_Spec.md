
# LaRa Caregiver Dashboard – Session Feature Specification
## (Learning Companion Model – Clinical Intelligence Hidden Underneath)

---

# 1. Design Philosophy

The Session Feature must:

- Feel simple, warm, and lightweight.
- Avoid clinical or analytical language.
- Never expose curriculum mechanics to the child.
- Keep intelligence hidden underneath.
- Minimize caregiver friction.
- Ensure strict student data isolation.
- Avoid heavy verification rituals.

The student must feel like they are starting a friendly interaction —
not entering a monitored therapeutic system.

---

# 2. High-Level Flow

Caregiver Dashboard
    → Session
        → Select Child OR Add New Child
            → Soft Identity Confirmation
                → Curriculum Auto-Suggestion (silent default)
                    → Start Session

Maximum interaction depth: 4–5 actions.

---

# 3. Step-by-Step Implementation Tasks

---

## STEP 1 — Create Session Entry Page

Route:
/dashboard/session

UI Requirements:
- Clean interface
- Minimal text
- Warm tone
- No analytics shown here

Display:
- Button: “Start Session”
- List of existing children (card format)
- Button: “Add New Child”

TODO:
- Fetch child list from user_memory table
- Display name, age, last session date
- Do NOT show performance metrics here

---

## STEP 2 — Add New Child Flow

When “Add New Child” is clicked:

Fields required:
- Child Name
- Age
- Optional: Preferred name
- Optional: Notes (hidden from child)

Backend Requirements:
- Generate unique student_id
- Create isolated memory segment
- Create mastery baseline entry
- Create reinforcement baseline entry
- Create regulation state baseline
- Encrypt any stored biometric data if used

DO NOT:
- Ask about diagnosis
- Ask clinical labels
- Overwhelm caregiver with forms

Keep it short.

---

## STEP 3 — Select Existing Child

When a child card is clicked:

Display:
“Start session with [Name]?”

Buttons:
- Continue Learning
- Switch Curriculum (small secondary option)

Default path:
Continue Learning

---

## STEP 4 — Soft Identity Confirmation (Optional but Recommended)

Goal:
Prevent accidental data crossover.

Process:

- Activate camera briefly
- Run face embedding match (if enabled)
- Compute similarity score

IF similarity > threshold:
    Show:
    “This looks like [Name]. Is that correct?”
    Confirm button

IF similarity low:
    Show:
    “Please confirm the student.”
    Allow caregiver manual confirmation

DO NOT:
- Block session automatically
- Use accusatory language
- Expose biometric scores

Security TODO:
- Store embeddings locally
- Encrypt embeddings
- Never send biometric data externally

---

## STEP 5 — Curriculum Handling (Hidden Intelligence)

For New Child:
- Auto-assign age-based curriculum template
- Internally create concept graph
- Set difficulty baseline

For Existing Child:
- Load saved mastery graph
- Continue progression

Expose only this to caregiver:

“Continue learning journey”
OR
“Start a new learning path”

DO NOT expose:
- ZPD Elasticity
- Advancement Velocity
- Difficulty index
- Concept graph

Curriculum remains invisible to student.

---

## STEP 6 — Session Initialization

When session starts:

Initialize:
- SessionState
- RegulationState
- RecoveryStrategy baseline
- Reinforcement style default
- LearningProgress baseline
- Vision engagement tracker
- Audio mood tracker

Create:
session_id (unique)

Bind:
session_id → student_id

Ensure:
No cross-user data bleed.

---

# 4. Backend Requirements Checklist

For each session start:

- Verify student_id exists
- Lock session to student_id
- Initialize fresh short-term memory
- Load long-term memory
- Attach reinforcement metrics
- Attach regulation history
- Attach mastery graph
- Log session start timestamp

---

# 5. Data Isolation Rules

STRICT RULES:

- Each student has separate DB namespace
- Session memory clears after 24 hours
- Long-term memory linked only via student_id
- No session writes allowed without student_id binding
- No fallback to global memory

---

# 6. UX Constraints

Session feature must:

- Be under 5 clicks
- Avoid technical language
- Avoid showing analytics
- Avoid showing risk predictions
- Avoid overwhelming forms
- Feel like a companion starting playtime

---

# 7. What NOT To Implement

- Hard biometric blocking
- Mandatory curriculum branching
- Clinical terminology
- Risk percentages in caregiver view
- Predictive meltdown alerts in session entry

Those belong in clinician or admin view.

---

# 8. Security Considerations

- Encrypt student identifiers
- Encrypt face embeddings (if stored)
- Separate authentication roles
- Prevent caregiver from accessing admin analytics
- Log all session start events

---

# 9. Completion Criteria

Session Feature is considered complete when:

- New child can be added in < 60 seconds
- Existing child can start session in < 3 clicks
- No cross-user memory bleed occurs
- Curriculum runs silently underneath
- Child perceives only a friendly start

---

End of Session Feature Specification.
