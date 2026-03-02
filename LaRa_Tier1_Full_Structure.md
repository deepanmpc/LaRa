
# LaRa Dashboard – Tier 1 (Caregiver View)
## Rich but Simple Structure
## Learning Companion Experience with Clinical Intelligence Hidden Underneath

---

# 1. Core Philosophy

Tier 1 is for caregivers.

It must:
- Feel reassuring
- Feel complete
- Avoid technical language
- Avoid predictive risk percentages
- Avoid statistical terminology
- Present progress clearly
- Encourage continued engagement

The caregiver should feel:
"My child is supported."
"I understand what happened."
"I know what to do next."

---

# 2. Full Page Structure

Route:
/dashboard/simple

Page Layout Order:

1. Active Child Overview Card
2. Today’s Session Summary
3. Emotional Overview
4. Engagement Overview
5. Progress Snapshot
6. Intervention Summary
7. Milestones & Achievements
8. Weekly Snapshot
9. Recommended Next Steps
10. Session History
11. Caregiver Notes

---

# 3. Section 1 – Active Child Overview

Display at top.

Fields:

- Child Name
- Age
- Current Learning Theme
- Last Session Date
- Overall Status Badge:
    - Doing Well
    - Needs Extra Support
    - Taking a Break

Backend Mapping:

ZPD + Emotional Stability + Mastery Delta
→ Collapsed into simple 3-state badge.

No numeric score displayed.

---

# 4. Section 2 – Today’s Session Summary

Display:

- Today’s Learning Focus
- Emotional Stability:
    Stable
    Slightly Challenging
    Needs Attention
- Concepts Practiced
- Concepts Mastered
- Short AI Narrative (max 120 words)

Narrative must:
- Be plain English
- Avoid diagnosis
- Avoid probabilities
- Be reassuring

---

# 5. Section 3 – Emotional Overview

Display:

- Recovery Speed:
    Fast
    Moderate
    Slow
- Number of Frustration Moments
- Compared to Last Week:
    Improved
    Similar
    Needs Monitoring

Backend Conversion:

Recovery latency seconds
→ Bucket classification

Volatility index
→ Hidden, used only internally

---

# 6. Section 4 – Engagement Overview

Display:

- Engagement Level:
    Highly Engaged
    Moderately Engaged
    Frequently Distracted
- Participation Score:
    Active
    Responsive
    Quiet

Derived From:

Vision attention tracking
Speech participation frequency
SessionState interaction density

No raw metrics shown.

---

# 7. Section 5 – Progress Snapshot

Display:

- Horizontal Progress Bars per Active Concept
- Mastery Percentage (rounded)
- Trend Arrow:
    ↑ Improving
    → Stable
    ↓ Slowing

No scatter plots.
No radar charts.
No centrality graphs.

Color Coding:

Green – Strong Progress
Yellow – Developing
Red – Needs Support

---

# 8. Section 6 – Intervention Summary

Display:

- Breathing exercise helped 3 out of 4 times.
- Gentle nudges were effective.
- Story mode maintained engagement.

If effectiveness < threshold:

"Consider rotating tools this week."

No decay slopes shown.
No dependency risk metrics shown.

---

# 9. Section 7 – Milestones & Achievements

Display:

Recent Achievements:

- Completed first independent sequence
- Improved recovery time
- Managed frustration without assistance
- Maintained focus for 10 minutes

These are derived from mastery and regulation improvements.

This section builds emotional reward for caregivers.

---

# 10. Section 8 – Weekly Snapshot

Display:

- Sessions Completed This Week
- Total Learning Time
- Concepts Advanced
- Emotional Stability Trend:
    Improving
    Stable
    Slightly Challenging

Short summary sentence:

"This week showed steady progress with improved emotional regulation."

---

# 11. Section 9 – Recommended Next Steps

Display:

"Suggested for this week:"

- Continue counting exercises
- Practice breathing tool twice
- Try new storytelling activity

These suggestions are derived from:

LearningProgress baseline
RegulationState persistence
Intervention effectiveness

No technical explanation shown.

---

# 12. Section 10 – Session History

Display list of recent sessions:

- Date
- Duration
- Emotional Summary
- Progress Indicator

Keep simple card layout.
No detailed logs.
No volatility graphs.

---

# 13. Section 11 – Caregiver Notes

Allow caregiver to add:

- Observations
- External factors
- School notes
- Sleep patterns

Stored in user memory under caregiver_notes table.

These notes influence context but remain invisible to child.

---

# 14. Language Rules

Never display:

- Probability
- Risk percentage
- Bayesian
- Volatility index
- Drift
- Calibration
- Escalation likelihood

Always display:

- Reassurance
- Clear guidance
- Plain English
- Encouraging tone

---

# 15. API Contract

Create endpoint:

GET /api/dashboard/simple?student_id=

Return:

{
  child_overview,
  session_summary,
  emotional_overview,
  engagement_overview,
  progress_snapshot,
  intervention_summary,
  milestones,
  weekly_snapshot,
  recommended_next_steps,
  session_history
}

All complex analytics remain hidden and pre-processed.

---

# 16. Performance Requirements

- Page load under 500ms
- Avoid heavy chart libraries
- Pre-aggregate metrics server-side
- Lazy load session history

---

# 17. Completion Criteria

Tier 1 is complete when:

- A caregiver understands the page in under 60 seconds
- No mathematical jargon appears
- All metrics are converted to plain language
- It feels like a progress journal, not a research console
- It builds confidence in the system

---

End of Tier 1 Full Structure Specification.
