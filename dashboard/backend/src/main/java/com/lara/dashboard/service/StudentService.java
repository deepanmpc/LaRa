package com.lara.dashboard.service;

import com.lara.dashboard.dto.StudentDto;
import com.lara.dashboard.model.Student;
import com.lara.dashboard.repository.StudentRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.LocalDateTime;
import java.util.List;
import java.util.stream.Collectors;

@Service
@RequiredArgsConstructor
public class StudentService {

    private final StudentRepository studentRepository;

    @Transactional(readOnly = true)
    public List<StudentDto> getAllStudents() {
        return studentRepository.findAll().stream()
                .map(this::mapToDto)
                .collect(Collectors.toList());
    }

    @Transactional
    public StudentDto addStudent(String name, Integer age, String preferredName, String notes) {
        Student student = new Student();
        student.setName(name);
        student.setAge(age);
        student.setPreferredName(preferredName);
        student.setNotes(notes);
        student.generateHashParams(); // PrePersist generally handles this, but calling explicitly ensures hash exists pre-save

        return mapToDto(studentRepository.save(student));
    }

    @Transactional
    public void updateLastSession(String studentIdHashed) {
        studentRepository.findByStudentIdHashed(studentIdHashed).ifPresent(student -> {
            student.setLastSessionDate(LocalDateTime.now());
            studentRepository.save(student);
        });
    }

    private StudentDto mapToDto(Student student) {
        StudentDto dto = new StudentDto();
        dto.setStudentIdHashed(student.getStudentIdHashed());
        dto.setName(student.getName());
        dto.setAge(student.getAge());
        dto.setPreferredName(student.getPreferredName());
        dto.setLastSessionDate(student.getLastSessionDate());
        return dto;
    }
}
