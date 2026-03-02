package com.lara.dashboard.repository;

import com.lara.dashboard.model.Student;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.Optional;

@Repository
public interface StudentRepository extends JpaRepository<Student, Long> {
    Optional<Student> findByStudentIdHashed(String studentIdHashed);
}
