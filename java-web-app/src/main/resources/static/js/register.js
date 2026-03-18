// API Base URL
const API_BASE_URL = '/api/auth';

// Token storage keys
const TOKEN_KEY = 'auth_token';
const USER_KEY = 'user_info';

$(document).ready(function() {
    // 页面加载时检查是否已登录
    redirectIfAuthenticated();
    
    // 绑定表单提交事件
    $('#registerForm').on('submit', handleRegister);
    
    // 绑定注册方式切换事件
    $('input[name="regType"]').on('change', toggleRegType);
    
    // 绑定输入框焦点事件，添加动画效果
    $('.form-group input').on('focus', function() {
        $(this).parent().addClass('focused');
    }).on('blur', function() {
        $(this).parent().removeClass('focused');
    });
    
    // 实时验证用户名
    $('#username').on('blur', function() {
        validateUsername($(this).val());
    });
    
    // 实时验证邮箱
    $('#email').on('blur', function() {
        validateEmail($(this).val());
    });
    
    // 实时验证手机号
    $('#phone').on('blur', function() {
        validatePhone($(this).val());
    });
    
    // 实时验证密码
    $('#password').on('input', function() {
        validatePassword($(this).val());
    });
    
    // 实时验证确认密码
    $('#confirmPassword').on('input', function() {
        validateConfirmPassword($(this).val(), $('#password').val());
    });
});

// 切换注册方式
function toggleRegType() {
    const regType = $('input[name="regType"]:checked').val();
    
    if (regType === 'email') {
        $('#emailGroup').removeClass('hidden');
        $('#phoneGroup').addClass('hidden');
        $('#email').prop('required', true);
        $('#phone').prop('required', false).val('');
    } else {
        $('#emailGroup').addClass('hidden');
        $('#phoneGroup').removeClass('hidden');
        $('#email').prop('required', false).val('');
        $('#phone').prop('required', true);
    }
}

// 处理注册表单提交
function handleRegister(event) {
    event.preventDefault();
    hideMessage();
    
    const $form = $('#registerForm');
    const $button = $form.find('button[type="submit"]');
    
    // 获取注册方式
    const regType = $('input[name="regType"]:checked').val();
    
    // 获取表单值
    const formData = {
        username: $('#username').val().trim(),
        firstName: $('#firstName').val().trim(),
        lastName: $('#lastName').val().trim(),
        password: $('#password').val()
    };
    
    // 根据注册方式添加邮箱或手机号
    if (regType === 'email') {
        formData.email = $('#email').val().trim();
        formData.phone = '';
    } else {
        formData.email = '';
        formData.phone = $('#phone').val().trim();
    }
    
    // 验证密码匹配
    const confirmPassword = $('#confirmPassword').val();
    if (formData.password !== confirmPassword) {
        showMessage('两次输入的密码不一致', 'error');
        return false;
    }
    
    // 验证服务条款
    const agreeTerms = $('#agreeTerms').is(':checked');
    if (!agreeTerms) {
        showMessage('请同意服务条款和隐私政策', 'error');
        return false;
    }
    
    // 显示加载状态
    showLoading($button);
    
    // 发送注册请求
    $.ajax({
        url: API_BASE_URL + '/register',
        type: 'POST',
        contentType: 'application/json',
        data: JSON.stringify(formData),
        success: function(result) {
            if (result.success) {
                showMessage('注册成功！正在跳转...', 'success');
                
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
                }, 1500);
            } else {
                showMessage(result.message || '注册失败，请重试', 'error');
                hideLoading($button);
            }
        },
        error: function(xhr, status, error) {
            console.error('Registration error:', error);
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

// 验证用户名
function validateUsername(username) {
    if (username.length < 3) {
        showInputError($('#username'), '用户名至少 3 个字符');
        return false;
    }
    if (username.length > 50) {
        showInputError($('#username'), '用户名不能超过 50 个字符');
        return false;
    }
    showInputSuccess($('#username'));
    return true;
}

// 验证邮箱
function validateEmail(email) {
    if (email === '') return true; // 允许为空，当选择手机号注册时
    
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(email)) {
        showInputError($('#email'), '请输入有效的邮箱地址');
        return false;
    }
    showInputSuccess($('#email'));
    return true;
}

// 验证手机号
function validatePhone(phone) {
    if (phone === '') return true; // 允许为空，当选择邮箱注册时
    
    const phoneRegex = /^1[3-9]\d{9}$/;
    if (!phoneRegex.test(phone)) {
        showInputError($('#phone'), '请输入有效的 11 位手机号');
        return false;
    }
    showInputSuccess($('#phone'));
    return true;
}

// 验证密码
function validatePassword(password) {
    if (password.length < 6) {
        showInputError($('#password'), '密码至少 6 个字符');
        return false;
    }
    if (password.length > 100) {
        showInputError($('#password'), '密码不能超过 100 个字符');
        return false;
    }
    showInputSuccess($('#password'));
    return true;
}

// 验证确认密码
function validateConfirmPassword(confirmPassword, password) {
    if (confirmPassword === '') return true;
    
    if (confirmPassword !== password) {
        showInputError($('#confirmPassword'), '两次输入的密码不一致');
        return false;
    }
    showInputSuccess($('#confirmPassword'));
    return true;
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
