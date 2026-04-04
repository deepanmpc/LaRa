package com.lara.dashboard.repository;

import com.lara.dashboard.entity.CurriculumTopic;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.Optional;

@Repository
public interface CurriculumTopicRepository extends JpaRepository<CurriculumTopic, Long> {

    Optional<CurriculumTopic> findByName(String name);

    List<CurriculumTopic> findByIsActiveTrue();

    List<CurriculumTopic> findByArea(String area);

    boolean existsByName(String name);
}
