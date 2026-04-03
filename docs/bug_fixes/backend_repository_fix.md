# Backend Repository Fix
## Missing Spring Data Repository Methods

### Problem
The Spring Boot backend failed to compile due to missing repository query methods referenced by `CausalityAnalyticsService` and `PredictiveAnalyticsService`. Both services called `findByChildIdHashedAndTimestampAfterOrderByTimestampAsc`, which was not declared in the repository interfaces.

### Root Cause
Services attempted to use derived query methods that were never declared in the repository interfaces. Spring Data JPA requires the method signature to exist to auto-generate the SQL queries.

### Fix
Added the method signature to the following repositories:
- `ToolInterventionRepository.java`
- `EmotionalMetricRepository.java`
- `ZpdMetricRepository.java`

```java
List<ToolIntervention> findByChildIdHashedAndTimestampAfterOrderByTimestampAsc(
    String childIdHashed,
    LocalDateTime timestamp
);
```

Also implemented explicit getters in `EmotionalMetric` and `ZpdMetric` entities to resolve Lombok/MapStruct symbol resolution issues.
