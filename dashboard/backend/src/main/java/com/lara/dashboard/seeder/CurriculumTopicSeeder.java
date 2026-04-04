package com.lara.dashboard.seeder;

import com.lara.dashboard.entity.CurriculumTopic;
import com.lara.dashboard.repository.CurriculumTopicRepository;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.boot.ApplicationArguments;
import org.springframework.boot.ApplicationRunner;
import org.springframework.stereotype.Component;

@Component
@RequiredArgsConstructor
@Slf4j
public class CurriculumTopicSeeder implements ApplicationRunner {

    private final CurriculumTopicRepository topicRepository;

    @Override
    public void run(ApplicationArguments args) {
        if (topicRepository.count() > 0) {
            log.info("[CurriculumSeeder] Topics already seeded ({}), skipping.", topicRepository.count());
            return;
        }

        log.info("[CurriculumSeeder] Seeding curriculum topics...");

        // ── Math ──
        seed("Counting", "Math", "Number counting and recognition", 1, 3, 2, 8);
        seed("Addition", "Math", "Basic addition operations", 2, 4, 4, 12);
        seed("Subtraction", "Math", "Basic subtraction operations", 2, 4, 4, 12);
        seed("Shapes", "Math", "Shape recognition and properties", 1, 3, 2, 8);
        seed("Patterns", "Math", "Pattern recognition and creation", 1, 4, 3, 10);
        seed("Numbers 1-10", "Math", "Number recognition 1-10", 1, 2, 2, 6);
        seed("Numbers 1-100", "Math", "Number recognition 1-100", 2, 4, 4, 10);

        // ── Language ──
        seed("Vocabulary", "Language", "Word recognition and usage", 1, 5, 2, 18);
        seed("Reading Comprehension", "Language", "Understanding written text", 2, 5, 5, 18);
        seed("Story Sequencing", "Language", "Ordering events in stories", 2, 4, 4, 14);
        seed("Letter Recognition", "Language", "Identifying letters of the alphabet", 1, 2, 2, 6);
        seed("Phonics", "Language", "Sound-letter correspondence", 1, 3, 3, 8);
        seed("Sight Words", "Language", "High-frequency word recognition", 1, 3, 3, 8);

        // ── Social Skills ──
        seed("Social Scenarios", "Social Skills", "Understanding social situations", 1, 5, 3, 18);
        seed("Emotions Recognition", "Social Skills", "Identifying emotions in self and others", 1, 4, 2, 14);
        seed("Turn-Taking", "Social Skills", "Practicing taking turns", 1, 3, 2, 10);
        seed("Sharing", "Social Skills", "Understanding sharing concepts", 1, 3, 2, 10);
        seed("Greetings", "Social Skills", "Appropriate greeting behavior", 1, 2, 2, 8);

        // ── Cognitive ──
        seed("Memory", "Cognitive", "Working memory and recall", 1, 5, 2, 18);
        seed("Attention", "Cognitive", "Sustained and selective attention", 1, 5, 2, 18);
        seed("Problem Solving", "Cognitive", "Logical thinking and problem solving", 2, 5, 4, 18);
        seed("Categorization", "Cognitive", "Sorting and grouping items", 1, 3, 2, 10);
        seed("Sequencing", "Cognitive", "Ordering steps and events", 1, 4, 3, 14);

        // ── Communication ──
        seed("Verbal Expression", "Communication", "Expressing thoughts verbally", 1, 5, 2, 18);
        seed("Responding to Questions", "Communication", "Answering questions appropriately", 1, 4, 2, 14);
        seed("Following Instructions", "Communication", "Understanding and following directions", 1, 4, 2, 14);

        log.info("[CurriculumSeeder] Seeded {} curriculum topics.", topicRepository.count());
    }

    private void seed(String name, String area, String description, int diffMin, int diffMax, int ageMin, int ageMax) {
        if (!topicRepository.existsByName(name)) {
            topicRepository.save(CurriculumTopic.builder()
                    .name(name)
                    .area(area)
                    .description(description)
                    .difficultyMin(diffMin)
                    .difficultyMax(diffMax)
                    .ageRangeMin(ageMin)
                    .ageRangeMax(ageMax)
                    .isActive(true)
                    .build());
        }
    }
}
