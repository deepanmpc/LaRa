package com.lara.dashboard.controller;

import com.lara.dashboard.dto.StudentDto;
import com.lara.dashboard.service.StudentService;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/api/students")
@RequiredArgsConstructor
@CrossOrigin(origins = "http://localhost:5173")
public class StudentController {

    private final StudentService studentService;

    @GetMapping
    public ResponseEntity<List<StudentDto>> getAllStudents() {
        return ResponseEntity.ok(studentService.getAllStudents());
    }

    @PostMapping("/add")
    public ResponseEntity<StudentDto> addStudent(@RequestBody AddStudentRequest request) {
        StudentDto saved = studentService.addStudent(
                request.name(),
                request.age(),
                request.preferredName(),
                request.notes()
        );
        return ResponseEntity.ok(saved);
    }

    record AddStudentRequest(String name, Integer age, String preferredName, String notes) {}
}
