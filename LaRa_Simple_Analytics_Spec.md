
# LaRa Dashboard – Simple Analytics (Caregiver View)
## (Low Cognitive Load – Learning Companion Experience)

---

# 1. Design Philosophy

The Simple Analytics dashboard is for:

- Parents
- Teachers
- Non-technical therapists
- School coordinators

This view must:

- Avoid math-heavy terminology
- Avoid probabilities and percentages unless simplified
- Avoid clinical language
- Avoid predictive risk language
- Focus on clarity and reassurance
- Feel supportive, not analytical

This dashboard answers:

"What happened today?"
"Is my child doing okay?"
"What should we do next?"

It does NOT answer:

"Why did the AI trigger X intervention?"
"What is the volatility variance?"
"What is the Bayesian confidence interval?"

---

# 2. Route Structure

Route:
/dashboard/simple

Sections:

1. Session Summary
2. Emotional Overview
3. Intervention Summary
4. Progress Snapshot

---

# 3. Section 1 – Session Summary

Purpose:
Provide a plain-language overview of today’s session.

Display:

- Today’s Learning Focus
- Emotional Stability Status
- Concepts Practiced
- Concepts Mastered
- Recommended Next Steps

---

## Data Mapping (Backend → Plain Language)

Complex Metric → Simple Output

ZPD Elasticity Score
→ "Your child remained mostly in their optimal learning zone."

Emotional Stability Index
→ "Emotional Stability: Stable / Slightly Challenging / Needs Attention"

Mastery Progress Delta
→ "Concepts Mastered Today: [List]"

Difficulty Adaptation Events
→ Hidden (used internally only)

---

## TODO – Implementation

- Pull session summary from SessionState
- Pull mastery updates from LearningProgress
- Map ZPD metrics to 3-tier classification:
    - Stable
    - Slightly Challenging
    - Needs Attention
- Generate 2–3 sentence AI narrative summary
- Limit summary to 120 words max
- Avoid numeric percentages unless necessary

---

# 4. Section 2 – Emotional Overview

Purpose:
Explain emotional behavior in human language.

Display:

- "How quickly your child recovered from frustration"
    Values:
        - Fast
        - Moderate
        - Slow

- "Number of frustration spikes today"

- "Improvement compared to last week"
    Values:
        - Improved
        - Similar
        - Needs Monitoring

---

## Data Mapping

Recovery Latency (seconds)
→ Convert to:
    < 15 sec → Fast
    15–40 sec → Moderate
    > 40 sec → Slow

Volatility Index
→ Hidden
Used only to determine stability category

EWMA Risk Score
→ NOT shown

---

## TODO – Implementation

- Compute average recovery latency
- Bucket into 3-level classification
- Compare to previous session baseline
- Display simple comparison arrow (↑ ↓ →)
- No raw numbers displayed

---

# 5. Section 3 – Intervention Summary

Purpose:
Show whether robot support tools helped.

Display Examples:

- "Breathing exercise helped 3 out of 4 times."
- "Gentle nudges were effective."
- "Consider rotating tools next week."

---

## Data Mapping

Overarching Success Rate
→ Convert to:
    > 75% → Effective
    50–75% → Moderately Effective
    < 50% → Consider Adjustments

Effectiveness Decay Slope
→ Hidden

Dependency Risk
→ Hidden from caregiver view

---

## TODO – Implementation

- Calculate intervention success counts
- Convert into plain language sentences
- Avoid showing slopes, percentages, or decay curves
- Limit to top 3 tools used in session

---

# 6. Section 4 – Progress Snapshot

Purpose:
Provide visual and intuitive concept progress.

Display:

- Progress bar per active concept
- Simple mastery percentage (rounded)
- Trend arrow:
    ↑ Improving
    → Stable
    ↓ Slowing

---

## Visual Constraints

- No radar charts
- No scatter plots
- No 3D graphs
- No centrality networks

Use:

- Horizontal progress bars
- Simple green/yellow/red indicators
- Small trend arrows

---

## TODO – Implementation

- Pull mastery level per concept
- Convert mastery 0–5 scale → 0–100%
- Calculate weekly delta
- Render progress bars with color coding:
    Green → Strong Progress
    Yellow → Developing
    Red → Needs Support

---

# 7. Language Rules (Critical)

The caregiver dashboard must:

- Avoid the words:
    Risk
    Probability
    Volatility
    Escalation
    Bayesian
    Calibration
    Drift
    ZPD

- Use calm and reassuring tone
- Never imply diagnosis
- Never imply failure
- Never imply system uncertainty

---

# 8. Performance Requirements

- Page load under 500ms
- No heavy chart libraries
- Lazy-load data
- Avoid rendering full session logs

---

# 9. Completion Criteria

Simple Analytics is complete when:

- A caregiver can understand the page in under 60 seconds
- No statistical jargon appears
- All metrics are mapped to plain English
- No predictive risk scores are visible
- The interface feels supportive, not clinical

---

End of Simple Analytics Specification.
