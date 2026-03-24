// API Base URL
const API_BASE_URL = '/api/auth';

// Token storage keys
const TOKEN_KEY = 'auth_token';
const USER_KEY = 'user_info';

$(document).ready(function() {
    // 页面加载时检查是否已登录
    redirectIfAuthenticated();

    // 绑定表单提交事件
    $('#loginForm').on('submit', handleLogin);

    // 绑定输入框焦点事件，添加动画效果
    $('.form-group input').on('focus', function() {
        $(this).parent().addClass('focused');
    }).on('blur', function() {
        $(this).parent().removeClass('focused');
    });

    // 实时验证输入
    $('#username').on('input', function() {
        validateUsername($(this).val());
    });

    // 密码显示/隐藏切换
    $('.password-toggle').on('click', function() {
        const $input = $(this).siblings('input');
        const type = $input.attr('type') === 'password' ? 'text' : 'password';
        $input.attr('type', type);
        $(this).toggleClass('active');
    });
});

// 验证用户名
function validateUsername(username) {
    if (username.length < 1) {
        showInputError($('#username'), '请输入用户名、邮箱或手机号');
        return false;
    }
    showInputSuccess($('#username'));
    return true;
}

// 处理登录表单提交
function handleLogin(event) {
    event.preventDefault();
    hideMessage();
    
    const $form = $('#loginForm');
    const $button = $form.find('button[type="submit"]');
    
    // 获取表单值
    const formData = {
        username: $('#username').val().trim(),
        password: $('#password').val()
    };
    
    // 基本验证
    if (!formData.username || !formData.password) {
        showMessage('请输入用户名和密码', 'error');
        return false;
    }
    
    // 显示加载状态
    showLoading($button);
    
    // 发送登录请求
    $.ajax({
        url: API_BASE_URL + '/login',
        type: 'POST',
        contentType: 'application/json',
        data: JSON.stringify(formData),
        success: function(result) {
            if (result.success) {
                showMessage('登录成功！正在跳转...', 'success');
                
                // 保存认证信息
                if (result.data && result.data.token) {
                    saveToken(result.data.token, {
                        username: result.data.username,
                        email: result.data.email
                    });
                }
                
                // 延迟跳转到首页
                setTimeout(function() {
                    window.location.href = '/index.html';
                }, 1000);
            } else {
                showMessage(result.message || '登录失败，请检查用户名和密码', 'error');
                hideLoading($button);
            }
        },
        error: function(xhr, status, error) {
            console.error('Login error:', error);
            let errorMsg = '网络错误，请稍后重试';
            
            if (xhr.responseJSON && xhr.responseJSON.message) {
                errorMsg = xhr.responseJSON.message;
            }
            
            showMessage(errorMsg, 'error');
            hideLoading($button);
        }
    });
    
    return false;
}

// 显示输入框错误状态
function showInputError($input, message) {
    const $formGroup = $input.closest('.form-group');
    $formGroup.addClass('has-error').removeClass('has-success');
    
    // 移除现有的错误消息
    $formGroup.find('.error-message').remove();
    
    // 添加错误消息
    $formGroup.append('<span class="error-message">' + message + '</span>');
}

// 显示输入框成功状态
function showInputSuccess($input) {
    const $formGroup = $input.closest('.form-group');
    $formGroup.addClass('has-success').removeClass('has-error');
    $formGroup.find('.error-message').remove();
}

// 显示加载状态
function showLoading($button) {
    $button.find('.btn-text').addClass('hidden');
    $button.find('.btn-loader').removeClass('hidden');
    $button.prop('disabled', true);
}

// 隐藏加载状态
function hideLoading($button) {
    $button.find('.btn-text').removeClass('hidden');
    $button.find('.btn-loader').addClass('hidden');
    $button.prop('disabled', false);
}

// 显示消息
function showMessage(message, type) {
    const $messageEl = $('#message');
    $messageEl.text(message);
    $messageEl.attr('class', 'message ' + type);
    $messageEl.removeClass('hidden');
    
    // 5 秒后自动隐藏
    setTimeout(function() {
        $messageEl.addClass('hidden');
    }, 5000);
}

// 隐藏消息
function hideMessage() {
    $('#message').addClass('hidden');
}

// Token 管理
function saveToken(token, user) {
    localStorage.setItem(TOKEN_KEY, token);
    localStorage.setItem(USER_KEY, JSON.stringify(user));
}

function getToken() {
    return localStorage.getItem(TOKEN_KEY);
}

function getUser() {
    const userStr = localStorage.getItem(USER_KEY);
    return userStr ? JSON.parse(userStr) : null;
}

function clearAuth() {
    localStorage.removeItem(TOKEN_KEY);
    localStorage.removeItem(USER_KEY);
}

// 如果已登录则重定向
function redirectIfAuthenticated() {
    const token = getToken();
    const path = window.location.pathname;
    if (token && (path.includes('login.html') || path.includes('register.html'))) {
        window.location.href = '/index.html';
    }
}

// 退出登录
function logout() {
    clearAuth();
    window.location.href = '/index.html';
}
