package com.lara.dashboard.repository;

import com.lara.dashboard.enums.Role;
import com.lara.dashboard.enums.UserStatus;
import com.lara.dashboard.entity.User;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.Optional;

@Repository
public interface UserRepository extends JpaRepository<User, Long> {
    Optional<User> findByEmail(String email);
    boolean existsByEmail(String email);
    List<User> findByRoleAndStatus(Role role, UserStatus status);
}
