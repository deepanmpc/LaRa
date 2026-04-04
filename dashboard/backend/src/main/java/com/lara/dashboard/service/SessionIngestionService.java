package com.lara.dashboard.service;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.lara.dashboard.dto.SessionCompleteRequest;
import com.lara.dashboard.entity.*;
import com.lara.dashboard.enums.DifficultyDirection;
import com.lara.dashboard.enums.SessionStatus;
import com.lara.dashboard.repository.*;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.math.BigDecimal;
import java.math.RoundingMode;
import java.time.DayOfWeek;
import java.time.LocalDate;
import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;
import java.util.List;
import java.util.Optional;

@Service
@RequiredArgsConstructor
@Slf4j
public class SessionIngestionService {

    private final SessionRepository sessionRepository;
    private final SessionTurnMetricRepository turnMetricRepo;
    private final SessionAnalyticsRepository analyticsRepo;
    private final ChildRepository childRepo;
    private final ChildEmotionalHistoryRepository emotionalHistoryRepo;
    private final ChildEngagementHistoryRepository engagementHistoryRepo;
    private final ChildLearningProgressRepository learningProgressRepo;
    private final ChildReinforcementMetricsRepository reinforcementRepo;
    private final ChildVisionMetricsEntityRepository visionMetricsRepo;
    private final ChildVoiceMetricsRepository voiceMetricsRepo;
    private final ChildActivityPerformanceRepository activityRepo;
    private final SessionDifficultyTrajectoryRepository difficultyRepo;
    private final WeeklySessionSummaryRepository weeklySummaryRepo;
    private final ObjectMapper objectMapper;

    @Transactional
    public Long ingestSession(SessionCompleteRequest req) {
        log.info("[SessionIngestion] Processing session UUID={}", req.getSessionUuid());

        // 1. Validate child exists
        Child child = childRepo.findById(req.getChildId())
                .orElseThrow(() -> new RuntimeException("Child not found: " + req.getChildId()));

        // 2. Check for duplicate session UUID
        Optional<Session> existing = sessionRepository.findBySessionUuid(req.getSessionUuid());
        if (existing.isPresent()) {
            log.warn("[SessionIngestion] Duplicate session UUID: {}", req.getSessionUuid());
            throw new RuntimeException("Duplicate session UUID: " + req.getSessionUuid());
        }

        // 3. Create session record
        Session session = createSession(req, child);

        // 4. Insert turn metrics
        if (req.getTurns() != null) {
            insertTurnMetrics(req.getTurns(), session);
        }

        // 5. Insert session analytics
        if (req.getEmotionalData() != null) {
            insertSessionAnalytics(req, session, child);
        }

        // 6. Insert emotional history
        if (req.getEmotionalData() != null) {
            insertEmotionalHistory(req, session, child);
        }

        // 7. Insert engagement history
        if (req.getEngagementData() != null) {
            insertEngagementHistory(req, session, child);
        }

        // 8. Upsert learning progress
        if (req.getLearningProgress() != null) {
            upsertLearningProgress(req.getLearningProgress(), session, child);
        }

        // 9. Upsert reinforcement metrics
        if (req.getReinforcementData() != null) {
            upsertReinforcementMetrics(req.getReinforcementData(), session, child);
        }

        // 10. Insert vision metrics
        if (req.getVisionData() != null) {
            insertVisionMetrics(req.getVisionData(), session, child);
        }

        // 11. Insert voice metrics
        if (req.getVoiceData() != null) {
            insertVoiceMetrics(req.getVoiceData(), session, child);
        }

        // 12. Upsert activity performance
        if (req.getTopActivities() != null) {
            upsertActivityPerformance(req.getTopActivities(), session, child);
        }

        // 13. Insert difficulty trajectory
        if (req.getDifficultyTrajectory() != null) {
            insertDifficultyTrajectory(req.getDifficultyTrajectory(), session, child);
        }

        // 14. Update child record
        updateChildRecord(child, req);

        // 15. Upsert weekly summary
        upsertWeeklySummary(child, req);

        log.info("[SessionIngestion] Session {} ingested successfully (DB ID={})", req.getSessionUuid(), session.getId());
        return session.getId();
    }

    // ──────────────────────────────────────────────────────────────────

    private Session createSession(SessionCompleteRequest req, Child child) {
        Session session = Session.builder()
                .sessionUuid(req.getSessionUuid())
                .child(child)
                .startTime(parseTimestamp(req.getStartTime()))
                .endTime(parseTimestamp(req.getEndTime()))
                .durationSeconds(req.getDurationSeconds())
                .totalTurns(req.getTotalTurns() != null ? req.getTotalTurns() : 0)
                .peakDifficulty(req.getPeakDifficulty() != null ? req.getPeakDifficulty() : 1)
                .avgEngagementScore(req.getAvgEngagementScore() != null ? req.getAvgEngagementScore() : BigDecimal.ZERO)
                .avgMoodConfidenceNew(req.getAvgMoodConfidence() != null ? req.getAvgMoodConfidence() : BigDecimal.ZERO)
                .dominantMood(req.getDominantMood() != null ? req.getDominantMood() : "neutral")
                .totalInterventions(req.getTotalInterventions() != null ? req.getTotalInterventions() : 0)
                .completionStatus(SessionStatus.COMPLETED)
                .wakeWordTriggers(req.getWakeWordTriggers() != null ? req.getWakeWordTriggers() : 0)
                .bargeInCount(req.getBargeInCount() != null ? req.getBargeInCount() : 0)
                .build();
        return sessionRepository.save(session);
    }

    private void insertTurnMetrics(List<SessionCompleteRequest.TurnItem> turns, Session session) {
        for (SessionCompleteRequest.TurnItem turn : turns) {
            SessionTurnMetric metric = SessionTurnMetric.builder()
                    .session(session)
                    .turnNumber(turn.getTurnNumber())
                    .timestamp(parseTimestamp(turn.getTimestamp()))
                    .childUtterance(turn.getChildUtterance())
                    .childUtteranceLength(turn.getChildUtterance() != null ? turn.getChildUtterance().split("\\s+").length : 0)
                    .laraResponse(turn.getLaraResponse())
                    .detectedMood(turn.getDetectedMood())
                    .moodConfidence(turn.getMoodConfidence())
                    .difficultyLevel(turn.getDifficultyLevel())
                    .strategyApplied(turn.getStrategyApplied())
                    .reinforcementStyle(turn.getReinforcementStyle())
                    .promptBuildMs(turn.getPromptBuildMs())
                    .inferenceMs(turn.getInferenceMs())
                    .ttsMs(turn.getTtsMs())
                    .totalLatencyMs(turn.getTotalLatencyMs())
                    .visionPresence(turn.getVisionPresence() != null ? turn.getVisionPresence() : false)
                    .visionAttentionState(turn.getVisionAttentionState())
                    .visionEngagementScore(turn.getVisionEngagementScore())
                    .visionGesture(turn.getVisionGesture())
                    .visionDistractionFrames(turn.getVisionDistractionFrames() != null ? turn.getVisionDistractionFrames() : 0)
                    .build();
            turnMetricRepo.save(metric);
        }
    }

    private void insertSessionAnalytics(SessionCompleteRequest req, Session session, Child child) {
        var ed = req.getEmotionalData();
        var eng = req.getEngagementData();
        var vis = req.getVisionData();
        var voc = req.getVoiceData();

        String topActivitiesJson = null;
        if (req.getTopActivities() != null) {
            try {
                topActivitiesJson = objectMapper.writeValueAsString(req.getTopActivities());
            } catch (Exception e) {
                log.warn("Failed to serialize topActivities", e);
            }
        }

        SessionAnalytics analytics = SessionAnalytics.builder()
                .session(session)
                .child(child)
                // Emotional
                .overallMoodScore(ed.getOverallMoodScore())
                .moodTrend(ed.getMoodTrend())
                .primaryEmotion(ed.getPrimaryEmotion())
                .emotionStabilityScore(ed.getEmotionStabilityScore())
                .anxietyLevel(ed.getAnxietyLevel())
                .selfRegulationScore(ed.getSelfRegulationScore())
                .positiveInteractions(ed.getPositiveInteractions())
                .challengingMoments(ed.getChallengingMoments())
                .pctHappy(ed.getPctHappy() != null ? ed.getPctHappy() : BigDecimal.ZERO)
                .pctCalm(ed.getPctCalm() != null ? ed.getPctCalm() : BigDecimal.ZERO)
                .pctFocused(ed.getPctFocused() != null ? ed.getPctFocused() : BigDecimal.ZERO)
                .pctAnxious(ed.getPctAnxious() != null ? ed.getPctAnxious() : BigDecimal.ZERO)
                .pctFrustrated(ed.getPctFrustrated() != null ? ed.getPctFrustrated() : BigDecimal.ZERO)
                .pctSad(ed.getPctSad() != null ? ed.getPctSad() : BigDecimal.ZERO)
                .pctNeutral(ed.getPctNeutral() != null ? ed.getPctNeutral() : BigDecimal.ZERO)
                // Engagement
                .focusScore(eng != null ? eng.getFocusScore() : null)
                .attentionSpanMinutes(eng != null ? eng.getAttentionSpanMinutes() : null)
                .taskCompletionRate(eng != null ? eng.getTaskCompletionRate() : null)
                .participationLevel(eng != null ? eng.getParticipationLevel() : null)
                .distractionFrequency(eng != null ? eng.getDistractionFrequency() : null)
                .responsivenessScore(eng != null ? eng.getResponsivenessScore() : null)
                .initiativeTakingScore(eng != null ? eng.getInitiativeTakingScore() : null)
                .collaborationScore(eng != null ? eng.getCollaborationScore() : null)
                .weeklyGoalProgress(eng != null ? eng.getWeeklyGoalProgress() : null)
                // Vision
                .avgEngagementScore(vis != null ? vis.getAvgEngagementScore() : null)
                .avgEngagementUiScore(vis != null ? vis.getAvgEngagementUiScore() : null)
                .avgGazeScore(vis != null ? vis.getAvgGazeScore() : null)
                .systemConfidence(vis != null ? vis.getSystemConfidence() : null)
                .totalDistractionFrames(vis != null && vis.getTotalDistractionFrames() != null ? vis.getTotalDistractionFrames() : 0)
                .focusedDurationMinutes(vis != null ? vis.getFocusedDurationMinutes() : null)
                .faceConfidence(vis != null ? vis.getFaceConfidence() : null)
                .gestureConfidence(vis != null ? vis.getGestureConfidence() : null)
                .poseConfidence(vis != null ? vis.getPoseConfidence() : null)
                .objectConfidence(vis != null ? vis.getObjectConfidence() : null)
                // Voice
                .speakingRateWpm(voc != null ? voc.getSpeakingRateWpm() : null)
                .vocalVolume(voc != null ? voc.getAvgVolume() : null)
                .speechStabilityScore(voc != null ? voc.getSpeechStabilityScore() : null)
                .pctVocalNeutral(voc != null && voc.getPctVocalNeutral() != null ? voc.getPctVocalNeutral() : BigDecimal.ZERO)
                .pctVocalArousal(voc != null && voc.getPctVocalArousal() != null ? voc.getPctVocalArousal() : BigDecimal.ZERO)
                .pctVocalWithdrawal(voc != null && voc.getPctVocalWithdrawal() != null ? voc.getPctVocalWithdrawal() : BigDecimal.ZERO)
                // Activities
                .topActivitiesJson(topActivitiesJson)
                // Performance
                .totalEngagementAverage(req.getAvgEngagementScore())
                .laraResponseCount(req.getTurns() != null ? req.getTurns().size() : 0)
                .childUtteranceCount(req.getTurns() != null ? (int) req.getTurns().stream().filter(t -> t.getChildUtterance() != null && !t.getChildUtterance().isEmpty()).count() : 0)
                .build();

        analyticsRepo.save(analytics);
    }

    private void insertEmotionalHistory(SessionCompleteRequest req, Session session, Child child) {
        var ed = req.getEmotionalData();
        ChildEmotionalHistory history = ChildEmotionalHistory.builder()
                .child(child)
                .session(session)
                .recordedDate(LocalDate.now())
                .moodScore(ed.getOverallMoodScore())
                .primaryEmotion(ed.getPrimaryEmotion())
                .frustrationCount(ed.getChallengingMoments() != null ? ed.getChallengingMoments() : 0)
                .recoveryCount(0)
                .stabilityCount(ed.getEmotionStabilityScore() != null ? ed.getEmotionStabilityScore() / 10 : 0)
                .anxietyCount("High".equals(ed.getAnxietyLevel()) ? 3 : "Medium".equals(ed.getAnxietyLevel()) ? 1 : 0)
                .happyCount(ed.getPositiveInteractions() != null ? ed.getPositiveInteractions() : 0)
                .calmCount(0)
                .focusedCount(0)
                .pctPositive(ed.getPctHappy() != null && ed.getPctCalm() != null && ed.getPctFocused() != null
                        ? ed.getPctHappy().add(ed.getPctCalm()).add(ed.getPctFocused()) : BigDecimal.ZERO)
                .pctNegative(ed.getPctAnxious() != null && ed.getPctFrustrated() != null
                        ? ed.getPctAnxious().add(ed.getPctFrustrated()) : BigDecimal.ZERO)
                .regulationIndex(ed.getSelfRegulationScore() != null ? new BigDecimal(ed.getSelfRegulationScore()) : null)
                .build();
        emotionalHistoryRepo.save(history);
    }

    private void insertEngagementHistory(SessionCompleteRequest req, Session session, Child child) {
        var eng = req.getEngagementData();
        var vis = req.getVisionData();

        ChildEngagementHistory history = ChildEngagementHistory.builder()
                .child(child)
                .session(session)
                .recordedDate(LocalDate.now())
                .focusScore(eng.getFocusScore())
                .attentionSpanMinutes(eng.getAttentionSpanMinutes())
                .engagementScore(vis != null ? vis.getAvgEngagementScore() : null)
                .gazeScore(vis != null ? vis.getAvgGazeScore() : null)
                .taskCompletionRate(eng.getTaskCompletionRate())
                .distractionFrames(vis != null && vis.getTotalDistractionFrames() != null ? vis.getTotalDistractionFrames() : 0)
                .build();
        engagementHistoryRepo.save(history);
    }

    private void upsertLearningProgress(List<SessionCompleteRequest.LearningProgressItem> items, Session session, Child child) {
        for (var item : items) {
            Optional<ChildLearningProgress> existing = learningProgressRepo
                    .findByChildIdAndConceptName(child.getId(), item.getConceptName());

            if (existing.isPresent()) {
                ChildLearningProgress lp = existing.get();
                lp.setSession(session);
                lp.setMasteryLevel(item.getMasteryLevel());
                lp.setMasteryPercentage(item.getMasteryPercentage());
                lp.setSuccessRate(item.getSuccessRate());
                lp.setAttemptCount(lp.getAttemptCount() + (item.getAttemptCount() != null ? item.getAttemptCount() : 0));
                lp.setSuccessCount(lp.getSuccessCount() + (item.getSuccessCount() != null ? item.getSuccessCount() : 0));
                lp.setFailureCount(lp.getAttemptCount() - lp.getSuccessCount());
                lp.setCurrentDifficulty(item.getCurrentDifficulty());
                if (item.getMasteryLevel() != null && item.getMasteryLevel() > lp.getHighestMasteryReached()) {
                    lp.setHighestMasteryReached(item.getMasteryLevel());
                }
                if (item.getCurrentDifficulty() != null && item.getCurrentDifficulty() > lp.getPeakDifficultyReached()) {
                    lp.setPeakDifficultyReached(item.getCurrentDifficulty());
                }
                lp.setLastAttemptedAt(LocalDateTime.now());
                lp.setMasteryStatus(deriveMasteryStatus(item.getMasteryPercentage()));
                learningProgressRepo.save(lp);
            } else {
                ChildLearningProgress lp = ChildLearningProgress.builder()
                        .child(child)
                        .session(session)
                        .conceptName(item.getConceptName())
                        .curriculumArea(item.getCurriculumArea())
                        .masteryLevel(item.getMasteryLevel() != null ? item.getMasteryLevel() : 0)
                        .highestMasteryReached(item.getMasteryLevel() != null ? item.getMasteryLevel() : 0)
                        .masteryPercentage(item.getMasteryPercentage() != null ? item.getMasteryPercentage() : BigDecimal.ZERO)
                        .masteryStatus(deriveMasteryStatus(item.getMasteryPercentage()))
                        .attemptCount(item.getAttemptCount() != null ? item.getAttemptCount() : 0)
                        .successCount(item.getSuccessCount() != null ? item.getSuccessCount() : 0)
                        .failureCount(item.getAttemptCount() != null && item.getSuccessCount() != null
                                ? item.getAttemptCount() - item.getSuccessCount() : 0)
                        .successRate(item.getSuccessRate() != null ? item.getSuccessRate() : BigDecimal.ZERO)
                        .firstAttemptedAt(LocalDateTime.now())
                        .lastAttemptedAt(LocalDateTime.now())
                        .currentDifficulty(item.getCurrentDifficulty() != null ? item.getCurrentDifficulty() : 1)
                        .peakDifficultyReached(item.getCurrentDifficulty() != null ? item.getCurrentDifficulty() : 1)
                        .build();
                learningProgressRepo.save(lp);
            }
        }
    }

    private void upsertReinforcementMetrics(SessionCompleteRequest.ReinforcementData data, Session session, Child child) {
        upsertSingleReinforcement(child, session, "calm_validation",
                data.getCalmValidationSuccess(), data.getCalmValidationTotal(),
                "calm_validation".equals(data.getPreferredStyle()));
        upsertSingleReinforcement(child, session, "praise_based",
                data.getPraisedBasedSuccess(), data.getPraisedBasedTotal(),
                "praise_based".equals(data.getPreferredStyle()));
        upsertSingleReinforcement(child, session, "achievement_based",
                data.getAchievementBasedSuccess(), data.getAchievementBasedTotal(),
                "achievement_based".equals(data.getPreferredStyle()));
        upsertSingleReinforcement(child, session, "playful",
                data.getPlayfulSuccess(), data.getPlayfulTotal(),
                "playful".equals(data.getPreferredStyle()));
    }

    private void upsertSingleReinforcement(Child child, Session session, String style,
                                           Integer success, Integer total, boolean preferred) {
        if (success == null) success = 0;
        if (total == null) total = 0;

        Optional<ChildReinforcementMetrics> existing = reinforcementRepo
                .findByChildIdAndStyleName(child.getId(), style);

        if (existing.isPresent()) {
            ChildReinforcementMetrics rm = existing.get();
            rm.setSession(session);
            rm.setSuccessCount(rm.getSuccessCount() + success);
            rm.setTotalUses(rm.getTotalUses() + total);
            rm.setTotalEvents(rm.getTotalEvents() + total);
            rm.setSuccessRate(rm.getTotalUses() > 0
                    ? new BigDecimal(rm.getSuccessCount()).divide(new BigDecimal(rm.getTotalUses()), 4, RoundingMode.HALF_UP)
                    : BigDecimal.ZERO);
            rm.setIsPreferred(preferred);
            rm.setLastUsedAt(LocalDateTime.now());
            reinforcementRepo.save(rm);
        } else {
            ChildReinforcementMetrics rm = ChildReinforcementMetrics.builder()
                    .child(child)
                    .session(session)
                    .styleName(style)
                    .successCount(success)
                    .totalUses(total)
                    .totalEvents(total)
                    .successRate(total > 0
                            ? new BigDecimal(success).divide(new BigDecimal(total), 4, RoundingMode.HALF_UP)
                            : BigDecimal.ZERO)
                    .isPreferred(preferred)
                    .lastUsedAt(LocalDateTime.now())
                    .build();
            reinforcementRepo.save(rm);
        }
    }

    private void insertVisionMetrics(SessionCompleteRequest.VisionData vis, Session session, Child child) {
        ChildVisionMetricsEntity vm = ChildVisionMetricsEntity.builder()
                .child(child)
                .session(session)
                .avgEngagementScore(vis.getAvgEngagementScore())
                .avgEngagementUiScore(vis.getAvgEngagementUiScore())
                .avgGazeScore(vis.getAvgGazeScore())
                .systemConfidence(vis.getSystemConfidence())
                .faceConfidence(vis.getFaceConfidence())
                .gestureConfidence(vis.getGestureConfidence())
                .poseConfidence(vis.getPoseConfidence())
                .objectConfidence(vis.getObjectConfidence())
                .distractionFrames(vis.getTotalDistractionFrames() != null ? vis.getTotalDistractionFrames() : 0)
                .focusedDurationMinutes(vis.getFocusedDurationMinutes())
                .attentionStateFocusedPct(vis.getAttentionFocusedPct())
                .attentionStateDistractedPct(vis.getAttentionDistractedPct())
                .attentionStateAbsentPct(vis.getAttentionAbsentPct())
                .build();
        visionMetricsRepo.save(vm);
    }

    private void insertVoiceMetrics(SessionCompleteRequest.VoiceData voc, Session session, Child child) {
        ChildVoiceMetrics vm = ChildVoiceMetrics.builder()
                .child(child)
                .session(session)
                .avgSpeakingRateWpm(voc.getSpeakingRateWpm())
                .avgVolume(voc.getAvgVolume())
                .speechStabilityScore(voc.getSpeechStabilityScore())
                .utteranceCount(voc.getUtteranceCount() != null ? voc.getUtteranceCount() : 0)
                .pctVocalNeutral(voc.getPctVocalNeutral() != null ? voc.getPctVocalNeutral() : BigDecimal.ZERO)
                .pctVocalArousal(voc.getPctVocalArousal() != null ? voc.getPctVocalArousal() : BigDecimal.ZERO)
                .pctVocalWithdrawal(voc.getPctVocalWithdrawal() != null ? voc.getPctVocalWithdrawal() : BigDecimal.ZERO)
                .build();
        voiceMetricsRepo.save(vm);
    }

    private void upsertActivityPerformance(List<SessionCompleteRequest.ActivityItem> activities, Session session, Child child) {
        for (var activity : activities) {
            Optional<ChildActivityPerformance> existing = activityRepo
                    .findByChildIdAndActivityName(child.getId(), activity.getName());

            if (existing.isPresent()) {
                ChildActivityPerformance ap = existing.get();
                ap.setSession(session);
                ap.setScore(activity.getScore());
                ap.setCompletionCount(ap.getCompletionCount() + (activity.getCompletions() != null ? activity.getCompletions() : 1));
                // Recalculate running average
                BigDecimal oldTotal = ap.getAvgScore() != null
                        ? ap.getAvgScore().multiply(new BigDecimal(ap.getCompletionCount() - (activity.getCompletions() != null ? activity.getCompletions() : 1)))
                        : BigDecimal.ZERO;
                BigDecimal newTotal = oldTotal.add(new BigDecimal(activity.getScore() * (activity.getCompletions() != null ? activity.getCompletions() : 1)));
                ap.setAvgScore(newTotal.divide(new BigDecimal(ap.getCompletionCount()), 2, RoundingMode.HALF_UP));
                ap.setLastPlayedAt(LocalDateTime.now());
                activityRepo.save(ap);
            } else {
                ChildActivityPerformance ap = ChildActivityPerformance.builder()
                        .child(child)
                        .session(session)
                        .activityName(activity.getName())
                        .score(activity.getScore())
                        .completionCount(activity.getCompletions() != null ? activity.getCompletions() : 1)
                        .avgScore(activity.getScore() != null ? new BigDecimal(activity.getScore()) : BigDecimal.ZERO)
                        .lastPlayedAt(LocalDateTime.now())
                        .build();
                activityRepo.save(ap);
            }
        }
    }

    private void insertDifficultyTrajectory(List<SessionCompleteRequest.DifficultyTrajectoryItem> items, Session session, Child child) {
        for (var item : items) {
            DifficultyDirection dir;
            try {
                dir = DifficultyDirection.valueOf(item.getDirection().toUpperCase());
            } catch (Exception e) {
                dir = DifficultyDirection.UNCHANGED;
            }

            SessionDifficultyTrajectory traj = SessionDifficultyTrajectory.builder()
                    .session(session)
                    .child(child)
                    .turnNumber(item.getTurnNumber())
                    .difficultyBefore(item.getBefore())
                    .difficultyAfter(item.getAfter())
                    .direction(dir)
                    .reason(item.getReason())
                    .build();
            difficultyRepo.save(traj);
        }
    }

    private void updateChildRecord(Child child, SessionCompleteRequest req) {
        child.setLastSessionAt(LocalDateTime.now());

        // Set current focus area based on top activity
        if (req.getTopActivities() != null && !req.getTopActivities().isEmpty()) {
            child.setCurrentFocusArea(req.getTopActivities().get(0).getName());
        }

        // Update status badge based on mood score
        if (req.getEmotionalData() != null && req.getEmotionalData().getOverallMoodScore() != null) {
            int moodScore = req.getEmotionalData().getOverallMoodScore();
            if (moodScore >= 70) child.setStatusBadge("Doing Well");
            else if (moodScore >= 50) child.setStatusBadge("Steady Progress");
            else child.setStatusBadge("Needs Support");
        }

        childRepo.save(child);
    }

    private void upsertWeeklySummary(Child child, SessionCompleteRequest req) {
        LocalDate today = LocalDate.now();
        LocalDate weekStart = today.with(DayOfWeek.MONDAY);

        Optional<WeeklySessionSummary> existing = weeklySummaryRepo.findByChildIdAndWeekStartDate(child.getId(), weekStart);

        if (existing.isPresent()) {
            WeeklySessionSummary ws = existing.get();
            ws.setSessionsThisWeek(ws.getSessionsThisWeek() + 1);
            ws.setTotalDurationMinutes(ws.getTotalDurationMinutes() + (req.getDurationSeconds() != null ? req.getDurationSeconds() / 60 : 0));

            // Recalculate averages
            if (req.getEmotionalData() != null && req.getEmotionalData().getOverallMoodScore() != null) {
                int newAvg = ws.getAvgMoodScore() != null
                        ? (ws.getAvgMoodScore() * (ws.getSessionsThisWeek() - 1) + req.getEmotionalData().getOverallMoodScore()) / ws.getSessionsThisWeek()
                        : req.getEmotionalData().getOverallMoodScore();
                ws.setAvgMoodScore(newAvg);
            }
            if (req.getEngagementData() != null && req.getEngagementData().getFocusScore() != null) {
                int newAvg = ws.getAvgFocusScore() != null
                        ? (ws.getAvgFocusScore() * (ws.getSessionsThisWeek() - 1) + req.getEngagementData().getFocusScore()) / ws.getSessionsThisWeek()
                        : req.getEngagementData().getFocusScore();
                ws.setAvgFocusScore(newAvg);
            }

            // Weekly goal progress
            if (child.getWeeklySessionGoal() != null && child.getWeeklySessionGoal() > 0) {
                ws.setWeeklyGoalProgress(Math.min(100, (ws.getSessionsThisWeek() * 100) / child.getWeeklySessionGoal()));
            }

            if (req.getTopActivities() != null && !req.getTopActivities().isEmpty()) {
                ws.setMostRecentActivity(req.getTopActivities().get(0).getName());
                ws.setActivitiesCompleted(ws.getActivitiesCompleted() + req.getTopActivities().size());
            }

            weeklySummaryRepo.save(ws);
        } else {
            WeeklySessionSummary ws = WeeklySessionSummary.builder()
                    .child(child)
                    .weekStartDate(weekStart)
                    .sessionsThisWeek(1)
                    .totalDurationMinutes(req.getDurationSeconds() != null ? req.getDurationSeconds() / 60 : 0)
                    .avgMoodScore(req.getEmotionalData() != null ? req.getEmotionalData().getOverallMoodScore() : null)
                    .avgFocusScore(req.getEngagementData() != null ? req.getEngagementData().getFocusScore() : null)
                    .weeklyGoalProgress(child.getWeeklySessionGoal() != null && child.getWeeklySessionGoal() > 0
                            ? Math.min(100, 100 / child.getWeeklySessionGoal()) : 0)
                    .activitiesCompleted(req.getTopActivities() != null ? req.getTopActivities().size() : 0)
                    .mostRecentActivity(req.getTopActivities() != null && !req.getTopActivities().isEmpty()
                            ? req.getTopActivities().get(0).getName() : null)
                    .build();
            weeklySummaryRepo.save(ws);
        }
    }

    // ── Helpers ──

    private String deriveMasteryStatus(BigDecimal percentage) {
        if (percentage == null || percentage.compareTo(BigDecimal.ZERO) == 0) return "Not Started";
        if (percentage.compareTo(new BigDecimal("90")) >= 0) return "Mastered";
        return "In Progress";
    }

    private LocalDateTime parseTimestamp(String ts) {
        if (ts == null || ts.isEmpty()) return LocalDateTime.now();
        try {
            return LocalDateTime.parse(ts, DateTimeFormatter.ISO_DATE_TIME);
        } catch (Exception e) {
            try {
                return LocalDateTime.parse(ts, DateTimeFormatter.ofPattern("yyyy-MM-dd'T'HH:mm:ss"));
            } catch (Exception e2) {
                return LocalDateTime.now();
            }
        }
    }
}
