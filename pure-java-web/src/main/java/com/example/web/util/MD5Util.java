package com.example.web.util;

import java.security.MessageDigest;
import java.security.NoSuchAlgorithmException;

/**
 * MD5加密工具类
 */
public class MD5Util {

    /**
     * 对字符串进行MD5加密
     */
    public static String encrypt(String input) {
        if (input == null || input.isEmpty()) {
            return null;
        }

        try {
            MessageDigest md = MessageDigest.getInstance("MD5");
            byte[] digest = md.digest(input.getBytes());
            StringBuilder sb = new StringBuilder();
            for (byte b : digest) {
                sb.append(String.format("%02x", b & 0xff));
            }
            return sb.toString();
        } catch (NoSuchAlgorithmException e) {
            throw new RuntimeException("MD5加密失败", e);
        }
    }

    /**
     * 验证密码是否匹配
     */
    public static boolean verify(String input, String encrypted) {
        if (input == null || encrypted == null) {
            return false;
        }
        return encrypt(input).equals(encrypted);
    }

    /**
     * 增强版MD5加密（带盐值）
     */
    public static String encryptWithSalt(String input, String salt) {
        return encrypt(input + salt);
    }

    /**
     * 生成随机盐值
     */
    public static String generateSalt() {
        return Long.toHexString(System.currentTimeMillis());
    }
}
