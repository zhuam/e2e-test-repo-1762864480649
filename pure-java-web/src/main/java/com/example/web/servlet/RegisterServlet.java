package com.example.web.servlet;

import com.example.web.dao.UserDao;
import com.example.web.model.User;
import com.example.web.util.MD5Util;

import javax.servlet.ServletException;
import javax.servlet.annotation.WebServlet;
import javax.servlet.http.HttpServlet;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;
import java.io.IOException;
import java.io.PrintWriter;
import java.util.HashMap;
import java.util.Map;

/**
 * 用户注册 Servlet
 */
@WebServlet("/api/register")
public class RegisterServlet extends HttpServlet {

    private final UserDao userDao = new UserDao();

    @Override
    protected void doPost(HttpServletRequest request, HttpServletResponse response)
            throws ServletException, IOException {

        // 设置字符编码
        request.setCharacterEncoding("UTF-8");
        response.setCharacterEncoding("UTF-8");
        response.setContentType("application/json; charset=UTF-8");

        // 获取参数
        String username = request.getParameter("username");
        String password = request.getParameter("password");
        String confirmPassword = request.getParameter("confirmPassword");
        String email = request.getParameter("email");
        String phone = request.getParameter("phone");
        String realName = request.getParameter("realName");

        // 响应对象
        PrintWriter out = response.getWriter();
        Map<String, Object> result = new HashMap<>();

        // 验证必填字段
        if (username == null || username.trim().isEmpty()) {
            result.put("success", false);
            result.put("message", "用户名不能为空");
            out.print(toJson(result));
            return;
        }

        if (password == null || password.trim().isEmpty()) {
            result.put("success", false);
            result.put("message", "密码不能为空");
            out.print(toJson(result));
            return;
        }

        // 验证密码长度
        if (password.length() < 6) {
            result.put("success", false);
            result.put("message", "密码长度不能少于6位");
            out.print(toJson(result));
            return;
        }

        // 验证确认密码
        if (!password.equals(confirmPassword)) {
            result.put("success", false);
            result.put("message", "两次输入的密码不一致");
            out.print(toJson(result));
            return;
        }

        // 验证用户名格式
        if (!username.matches("^[a-zA-Z0-9_]{4,20}$")) {
            result.put("success", false);
            result.put("message", "用户名只能包含字母、数字和下划线，长度4-20位");
            out.print(toJson(result));
            return;
        }

        // 验证邮箱格式（如果提供了邮箱）
        if (email != null && !email.trim().isEmpty()) {
            if (!email.matches("^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$")) {
                result.put("success", false);
                result.put("message", "邮箱格式不正确");
                out.print(toJson(result));
                return;
            }
        }

        // 检查用户名是否已存在
        if (userDao.existsByUsername(username.trim())) {
            result.put("success", false);
            result.put("message", "用户名已存在");
            out.print(toJson(result));
            return;
        }

        // 检查邮箱是否已存在
        if (email != null && !email.trim().isEmpty()) {
            if (userDao.existsByEmail(email.trim())) {
                result.put("success", false);
                result.put("message", "邮箱已被注册");
                out.print(toJson(result));
                return;
            }
        }

        // 创建用户对象
        User user = new User();
        user.setUsername(username.trim());
        user.setPassword(MD5Util.encrypt(password)); // MD5加密存储
        user.setEmail(email != null ? email.trim() : null);
        user.setPhone(phone != null ? phone.trim() : null);
        user.setRealName(realName != null ? realName.trim() : null);
        user.setStatus(1); // 默认启用

        // 保存用户
        if (userDao.save(user)) {
            result.put("success", true);
            result.put("message", "注册成功！");
            result.put("userId", user.getId());
        } else {
            result.put("success", false);
            result.put("message", "注册失败，请稍后重试");
        }

        out.print(toJson(result));
    }

    @Override
    protected void doGet(HttpServletRequest request, HttpServletResponse response)
            throws ServletException, IOException {
        response.sendRedirect("register.html");
    }

    /**
     * 简单将Map转换为JSON字符串
     */
    private String toJson(Map<String, Object> map) {
        StringBuilder json = new StringBuilder("{");
        boolean first = true;
        for (Map.Entry<String, Object> entry : map.entrySet()) {
            if (!first) {
                json.append(",");
            }
            first = false;
            json.append("\"").append(entry.getKey()).append("\":");
            Object value = entry.getValue();
            if (value instanceof String) {
                json.append("\"").append(escapeJson((String) value)).append("\"");
            } else if (value instanceof Number) {
                json.append(value);
            } else if (value == null) {
                json.append("null");
            } else {
                json.append("\"").append(escapeJson(value.toString())).append("\"");
            }
        }
        json.append("}");
        return json.toString();
    }

    /**
     * JSON字符串转义
     */
    private String escapeJson(String str) {
        if (str == null) return "";
        return str.replace("\\", "\\\\")
                .replace("\"", "\\\"")
                .replace("\n", "\\n")
                .replace("\r", "\\r")
                .replace("\t", "\\t");
    }
}
