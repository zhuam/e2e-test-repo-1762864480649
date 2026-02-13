package com.example.web.filter;

import javax.servlet.*;
import javax.servlet.annotation.WebFilter;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;
import javax.servlet.http.HttpSession;
import java.io.IOException;
import java.util.Arrays;
import java.util.List;

/**
 * 登录验证过滤器 - 验证用户是否已登录
 */
@WebFilter("/*")
public class AuthenticationFilter implements Filter {

    private List<String> excludePaths;

    @Override
    public void init(FilterConfig filterConfig) throws ServletException {
        String excludeParam = filterConfig.getInitParameter("excludePaths");
        if (excludeParam != null && !excludeParam.isEmpty()) {
            excludePaths = Arrays.asList(excludeParam.split(","));
        }
    }

    @Override
    public void doFilter(ServletRequest request, ServletResponse response, FilterChain chain)
            throws IOException, ServletException {

        HttpServletRequest httpRequest = (HttpServletRequest) request;
        HttpServletResponse httpResponse = (HttpServletResponse) response;

        String requestURI = httpRequest.getRequestURI();
        String contextPath = httpRequest.getContextPath();

        // 获取请求路径（去除contextPath）
        String path = requestURI.substring(contextPath.length());

        // 检查是否是排除路径
        if (isExcludePath(path)) {
            chain.doFilter(request, response);
            return;
        }

        // 检查静态资源
        if (path.startsWith("/css/") || path.startsWith("/js/") || path.startsWith("/images/") ||
                path.startsWith("/fonts/") || path.endsWith(".html")) {
            chain.doFilter(request, response);
            return;
        }

        // 检查是否已登录
        HttpSession session = httpRequest.getSession(false);
        if (session == null || session.getAttribute("user") == null) {
            // 未登录，返回401或重定向到登录页
            if (path.startsWith("/api/")) {
                httpResponse.setContentType("application/json; charset=UTF-8");
                httpResponse.setStatus(HttpServletResponse.SC_UNAUTHORIZED);
                httpResponse.getWriter().write("{\"success\":false,\"message\":\"用户未登录\",\"code\":401}");
            } else {
                httpResponse.sendRedirect(contextPath + "/login.html");
            }
            return;
        }

        chain.doFilter(request, response);
    }

    private boolean isExcludePath(String path) {
        if (excludePaths == null) {
            return false;
        }
        for (String exclude : excludePaths) {
            if (path.startsWith(exclude)) {
                return true;
            }
        }
        return false;
    }

    @Override
    public void destroy() {
    }
}
