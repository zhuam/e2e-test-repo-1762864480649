package com.example.web.servlet;

import com.example.web.dao.UserDao;
import com.example.web.model.User;
import com.example.web.util.MD5Util;

import javax.servlet.ServletException;
import javax.servlet.annotation.WebServlet;
import javax.servlet.http.HttpServlet;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;
import javax.servlet.http.HttpSession;
import java.io.IOException;
import java.io.PrintWriter;
import java.util.HashMap;
import java.util.Map;

/**
 * 用户登录 Servlet
 */
@WebServlet("/api/login")
public class LoginServlet extends HttpServlet {

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

        // 查询用户
        User user = userDao.findByUsername(username.trim());
        if (user == null) {
            result.put("success", false);
            result.put("message", "用户名或密码错误");
            out.print(toJson(result));
            return;
        }

        // 验证密码
        if (!MD5Util.verify(password, user.getPassword())) {
            result.put("success", false);
            result.put("message", "用户名或密码错误");
            out.print(toJson(result));
            return;
        }

        // 检查账户状态
        if (!user.isActive()) {
            result.put("success", false);
            result.put("message", "账户已被禁用，请联系管理员");
            out.print(toJson(result));
            return;
        }

        // 更新最后登录时间
        userDao.updateLastLoginTime(user.getId());

        // 创建Session
        HttpSession session = request.getSession();
        session.setAttribute("user", user);
        session.setAttribute("userId", user.getId());
        session.setAttribute("username", user.getUsername());
        session.setMaxInactiveInterval(30 * 60); // 30分钟过期

        // 返回成功信息（不返回密码）
        Map<String, Object> userData = new HashMap<>();
        userData.put("id", user.getId());
        userData.put("username", user.getUsername());
        userData.put("email", user.getEmail());
        userData.put("realName", user.getRealName());

        result.put("success", true);
        result.put("message", "登录成功！");
        result.put("data", userData);

        out.print(toJson(result));
    }

    @Override
    protected void doGet(HttpServletRequest request, HttpServletResponse response)
            throws ServletException, IOException {
        response.sendRedirect("login.html");
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
            } else if (value instanceof Map) {
                json.append(toJson((Map<String, Object>) value));
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
