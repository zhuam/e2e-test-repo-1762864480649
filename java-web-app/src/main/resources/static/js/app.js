// API Base URL
const API_BASE_URL = '/api/auth';

// Token storage keys
const TOKEN_KEY = 'auth_token';
const USER_KEY = 'user_info';

// Helper Functions
function showLoading(button) {
    const btnText = button.querySelector('.btn-text');
    const btnLoader = button.querySelector('.btn-loader');
    if (btnText) btnText.classList.add('hidden');
    if (btnLoader) btnLoader.classList.remove('hidden');
    button.disabled = true;
}

function hideLoading(button) {
    const btnText = button.querySelector('.btn-text');
    const btnLoader = button.querySelector('.btn-loader');
    if (btnText) btnText.classList.remove('hidden');
    if (btnLoader) btnLoader.classList.add('hidden');
    button.disabled = false;
}

function showMessage(message, type = 'success') {
    const messageEl = document.getElementById('message');
    if (messageEl) {
        messageEl.textContent = message;
        messageEl.className = `message ${type}`;
        messageEl.classList.remove('hidden');

        // Auto hide after 5 seconds
        setTimeout(() => {
            messageEl.classList.add('hidden');
        }, 5000);
    }
}

function hideMessage() {
    const messageEl = document.getElementById('message');
    if (messageEl) {
        messageEl.classList.add('hidden');
    }
}

// Token Management
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

// Authentication Status Check
function checkAuthStatus() {
    const token = getToken();
    const user = getUser();
    const guestNav = document.getElementById('guestNav');
    const userNav = document.getElementById('userNav');
    const welcomeUser = document.getElementById('welcomeUser');

    if (token && user) {
        if (guestNav) guestNav.classList.add('hidden');
        if (userNav) userNav.classList.remove('hidden');
        if (welcomeUser) welcomeUser.textContent = `欢迎, ${user.username}`;
    } else {
        if (guestNav) guestNav.classList.remove('hidden');
        if (userNav) userNav.classList.add('hidden');
    }
}

// API Requests
async function apiRequest(endpoint, method, data) {
    const options = {
        method: method,
        headers: {
            'Content-Type': 'application/json'
        }
    };

    if (data) {
        options.body = JSON.stringify(data);
    }

    const token = getToken();
    if (token) {
        options.headers['Authorization'] = `Bearer ${token}`;
    }

    const response = await fetch(`${API_BASE_URL}${endpoint}`, options);
    return await response.json();
}

// Handle Registration
async function handleRegister(event) {
    event.preventDefault();
    hideMessage();

    const form = event.target;
    const button = form.querySelector('button[type="submit"]');

    // Get form values
    const formData = {
        username: form.username.value.trim(),
        email: form.email.value.trim(),
        password: form.password.value,
        firstName: form.firstName?.value.trim() || '',
        lastName: form.lastName?.value.trim() || ''
    };

    // Validate passwords match
    const confirmPassword = form.confirmPassword.value;
    if (formData.password !== confirmPassword) {
        showMessage('两次输入的密码不一致', 'error');
        return;
    }

    // Validate terms agreement
    const agreeTerms = form.agreeTerms;
    if (agreeTerms && !agreeTerms.checked) {
        showMessage('请同意服务条款和隐私政策', 'error');
        return;
    }

    showLoading(button);

    try {
        const result = await apiRequest('/register', 'POST', formData);

        if (result.success) {
            showMessage('注册成功！正在跳转...', 'success');

            // Save auth info
            if (result.data && result.data.token) {
                saveToken(result.data.token, {
                    username: result.data.username,
                    email: result.data.email
                });
            }

            // Redirect to home after short delay
            setTimeout(() => {
                window.location.href = '/index.html';
            }, 1500);
        } else {
            showMessage(result.message || '注册失败，请重试', 'error');
            hideLoading(button);
        }
    } catch (error) {
        console.error('Registration error:', error);
        showMessage('网络错误，请稍后重试', 'error');
        hideLoading(button);
    }
}

// Handle Login
async function handleLogin(event) {
    event.preventDefault();
    hideMessage();

    const form = event.target;
    const button = form.querySelector('button[type="submit"]');

    // Get form values
    const formData = {
        username: form.username.value.trim(),
        password: form.password.value
    };

    // Basic validation
    if (!formData.username || !formData.password) {
        showMessage('请输入用户名和密码', 'error');
        return;
    }

    showLoading(button);

    try {
        const result = await apiRequest('/login', 'POST', formData);

        if (result.success) {
            showMessage('登录成功！正在跳转...', 'success');

            // Save auth info
            if (result.data && result.data.token) {
                saveToken(result.data.token, {
                    username: result.data.username,
                    email: result.data.email
                });
            }

            // Redirect to home after short delay
            setTimeout(() => {
                window.location.href = '/index.html';
            }, 1000);
        } else {
            showMessage(result.message || '登录失败，请检查用户名和密码', 'error');
            hideLoading(button);
        }
    } catch (error) {
        console.error('Login error:', error);
        showMessage('网络错误，请稍后重试', 'error');
        hideLoading(button);
    }
}

// Handle Logout
function logout() {
    clearAuth();
    window.location.href = '/index.html';
}

// Utility: Redirect if already logged in
function redirectIfAuthenticated() {
    const token = getToken();
    if (token && (window.location.pathname.includes('login.html') || window.location.pathname.includes('register.html'))) {
        window.location.href = '/index.html';
    }
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', function() {
    redirectIfAuthenticated();
});
