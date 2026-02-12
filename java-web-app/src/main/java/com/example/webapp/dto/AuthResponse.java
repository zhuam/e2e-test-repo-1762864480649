package com.example.webapp.dto;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class AuthResponse {

    private String message;
    private String token;
    private String username;
    private String email;
    private String tokenType;

    public static AuthResponse success(String message, String token, String username, String email) {
        return AuthResponse.builder()
                .message(message)
                .token(token)
                .username(username)
                .email(email)
                .tokenType("Bearer")
                .build();
    }

    public static AuthResponse success(String message) {
        return AuthResponse.builder()
                .message(message)
                .build();
    }
}
