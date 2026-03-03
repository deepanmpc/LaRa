package com.lara.dashboard.seeder;

import com.lara.dashboard.entity.User;
import com.lara.dashboard.enums.Role;
import com.lara.dashboard.enums.UserStatus;
import com.lara.dashboard.repository.UserRepository;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.boot.ApplicationArguments;
import org.springframework.boot.ApplicationRunner;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Component;
import org.springframework.util.StringUtils;

@Component
@RequiredArgsConstructor
@Slf4j
public class AdminSeeder implements ApplicationRunner {

    private final UserRepository userRepository;
    private final PasswordEncoder passwordEncoder;

    @Value("${app.admin.email}")
    private String adminEmail;

    @Value("${app.admin.password}")
    private String adminPassword;

    @Value("${app.admin.name}")
    private String adminName;

    @Override
    public void run(ApplicationArguments args) {
        // Fail fast if required admin env vars are missing
        if (!StringUtils.hasText(adminEmail) || !StringUtils.hasText(adminPassword)) {
            log.error("❌ ADMIN_EMAIL or ADMIN_PASSWORD environment variables are not set. Admin seeding skipped.");
            return;
        }

        if (!userRepository.existsByEmail(adminEmail)) {
            User admin = User.builder()
                    .name(StringUtils.hasText(adminName) ? adminName : "LaRa System Admin")
                    .email(adminEmail)
                    .password(passwordEncoder.encode(adminPassword))
                    .role(Role.ROLE_ADMIN)
                    .status(UserStatus.ACTIVE)
                    .build();
            userRepository.save(admin);
            // NEVER log the password
            log.info("✅ Admin user seeded: {}", adminEmail);
        } else {
            log.info("ℹ️  Admin user already exists: {}", adminEmail);
        }
    }
}
