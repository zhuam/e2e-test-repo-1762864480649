# 用户管理系统 - Java Web Application

一个基于 Spring Boot 的用户注册与登录系统，提供安全、美观的用户认证解决方案。

## 技术栈

### 后端
- **Java 17**
- **Spring Boot 3.2.0**
  - Spring Web
  - Spring Data JPA
  - Spring Security
  - Spring Validation
- **MySQL** - 数据库
- **JWT** - JSON Web Token 认证
- **Lombok** - 简化代码

### 前端
- **HTML5**
- **CSS3** (响应式设计)
- **JavaScript (ES6+)**
- **Google Fonts** - Noto Sans SC 字体

## 功能特性

- 用户注册（带表单验证）
- 用户登录（JWT 认证）
- 密码加密存储（BCrypt）
- 美观的响应式界面
- RESTful API 设计

## 项目结构

```
java-web-app/
├── pom.xml                              # Maven 配置
├── schema.sql                           # 数据库建表脚本
├── src/
│   └── main/
│       ├── java/com/example/webapp/
│       │   ├── WebAppApplication.java   # 主应用类
│       │   ├── config/
│       │   │   └── SecurityConfig.java  # 安全配置
│       │   ├── controller/
│       │   │   ├── AuthController.java  # 认证 API
│       │   │   └── PageController.java  # 页面路由
│       │   ├── dto/
│       │   │   ├── ApiResponse.java     # 通用响应
│       │   │   ├── AuthResponse.java    # 认证响应
│       │   │   ├── LoginRequest.java    # 登录请求
│       │   │   └── RegisterRequest.java # 注册请求
│       │   ├── entity/
│       │   │   └── User.java            # 用户实体
│       │   ├── repository/
│       │   │   └── UserRepository.java  # 数据访问层
│       │   └── service/
│       │       ├── JwtService.java      # JWT 服务
│       │       └── UserService.java     # 用户服务
│       └── resources/
│           ├── application.yml          # 应用配置
│           └── static/
│               ├── css/style.css        # 样式文件
│               ├── js/app.js            # 前端脚本
│               ├── index.html           # 首页
│               ├── login.html           # 登录页
│               └── register.html        # 注册页
```

## 快速开始

### 前置条件

- JDK 17+
- Maven 3.6+
- MySQL 8.0+

### 数据库配置

1. 创建 MySQL 数据库：
```sql
CREATE DATABASE webapp CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

2. 或者直接执行建表脚本：
```bash
mysql -u root -p < schema.sql
```

### 修改配置

编辑 `src/main/resources/application.yml`，修改数据库连接信息：

```yaml
spring:
  datasource:
    url: jdbc:mysql://localhost:3306/webapp?useSSL=false&serverTimezone=UTC&allowPublicKeyRetrieval=true
    username: your_username
    password: your_password
```

### 运行应用

```bash
# 编译项目
mvn clean package

# 运行应用
java -jar target/webapp-1.0.0.jar

# 或者使用 Maven 直接运行
mvn spring-boot:run
```

### 访问应用

- 首页：http://localhost:8080
- 登录页：http://localhost:8080/login.html
- 注册页：http://localhost:8080/register.html

## API 接口

### 用户注册
```
POST /api/auth/register
Content-Type: application/json

{
  "username": "testuser",
  "email": "test@example.com",
  "password": "password123",
  "firstName": "张",
  "lastName": "三"
}
```

### 用户登录
```
POST /api/auth/login
Content-Type: application/json

{
  "username": "testuser",
  "password": "password123"
}
```

### 响应格式
```json
{
  "success": true,
  "message": "操作成功",
  "data": {
    "message": "操作成功",
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "username": "testuser",
    "email": "test@example.com",
    "tokenType": "Bearer"
  }
}
```

## 安全特性

- 密码使用 BCrypt 加密存储
- JWT Token 有效期 24 小时
- CORS 跨域配置
- CSRF 保护（API 接口禁用）
- 输入验证和参数校验

## 环境要求

| 环境 | 版本要求 |
|------|---------|
| Java | 17+ |
| Maven | 3.6+ |
| MySQL | 8.0+ |

## License

MIT License
