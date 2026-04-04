package com.lara.dashboard.repository;

import com.lara.dashboard.entity.ChildPreference;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.Optional;

@Repository
public interface ChildPreferenceRepository extends JpaRepository<ChildPreference, Long> {

    List<ChildPreference> findByChildId(Long childId);

    Optional<ChildPreference> findByChildIdAndTopic(Long childId, String topic);
}
