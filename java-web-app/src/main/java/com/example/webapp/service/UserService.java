package com.example.webapp.service;

import com.example.webapp.dto.AuthResponse;
import com.example.webapp.dto.LoginRequest;
import com.example.webapp.dto.RegisterRequest;
import com.example.webapp.entity.User;
import com.example.webapp.repository.UserRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.util.StringUtils;

@Service
@RequiredArgsConstructor
public class UserService {

    private final UserRepository userRepository;
    private final PasswordEncoder passwordEncoder;
    private final JwtService jwtService;

    @Transactional
    public AuthResponse register(RegisterRequest request) {
        // Check if username already exists
        if (userRepository.existsByUsername(request.getUsername())) {
            throw new RuntimeException("用户名已存在");
        }

        // Validate that either email or phone is provided
        boolean hasEmail = StringUtils.hasText(request.getEmail());
        boolean hasPhone = StringUtils.hasText(request.getPhone());
        
        if (!hasEmail && !hasPhone) {
            throw new RuntimeException("邮箱或手机号必须填写一项");
        }

        // Check if email already exists
        if (hasEmail && userRepository.existsByEmail(request.getEmail())) {
            throw new RuntimeException("邮箱已被使用");
        }

        // Check if phone already exists
        if (hasPhone && userRepository.existsByPhone(request.getPhone())) {
            throw new RuntimeException("手机号已被使用");
        }

        // Create new user
        User user = User.builder()
                .username(request.getUsername())
                .email(hasEmail ? request.getEmail() : null)
                .phone(hasPhone ? request.getPhone() : null)
                .password(passwordEncoder.encode(request.getPassword()))
                .firstName(request.getFirstName())
                .lastName(request.getLastName())
                .enabled(true)
                .build();

        user = userRepository.save(user);

        // Generate JWT token
        String token = jwtService.generateToken(user.getUsername());

        return AuthResponse.success("注册成功", token, user.getUsername(), user.getEmail());
    }

    @Transactional(readOnly = true)
    public AuthResponse login(LoginRequest request) {
        String input = request.getUsername();
        
        // Try to find user by username, email, or phone
        User user = userRepository.findByUsername(input)
                .orElseGet(() -> {
                    // Try email
                    if (input.contains("@")) {
                        return userRepository.findByEmail(input).orElse(null);
                    }
                    // Try phone
                    if (input.matches("^1[3-9]\\d{9}$")) {
                        return userRepository.findByPhone(input).orElse(null);
                    }
                    return null;
                });
        
        if (user == null) {
            throw new RuntimeException("用户名或密码错误");
        }

        // Verify password
        if (!passwordEncoder.matches(request.getPassword(), user.getPassword())) {
            throw new RuntimeException("用户名或密码错误");
        }

        // Check if user is enabled
        if (!user.getEnabled()) {
            throw new RuntimeException("账户已被禁用");
        }

        // Generate JWT token
        String token = jwtService.generateToken(user.getUsername());

        return AuthResponse.success("登录成功", token, user.getUsername(), user.getEmail());
    }

    @Transactional(readOnly = true)
    public User findByUsername(String username) {
        return userRepository.findByUsername(username)
                .orElseThrow(() -> new RuntimeException("用户不存在"));
    }
}
