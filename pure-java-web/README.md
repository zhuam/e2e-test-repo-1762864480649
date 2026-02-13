# 纯 Java Web 用户管理系统

基于纯 Java Servlet + JSP + JDBC 实现的用户管理系统，不依赖 Spring 等第三方框架。

## 功能特性

- 用户注册（支持表单验证）
- 用户登录（Session 管理）
- 用户注销
- 用户信息查看
- 响应式设计，支持移动端
- 密码加密存储（MD5）
- 表单验证（前端+后端）

## 技术栈

- **后端**：Java Servlet 4.0 + JSP
- **数据库**：MySQL 8.0
- **数据库连接**：JDBC
- **前端**：HTML5 + CSS3 + JavaScript（ES6+）
- **构建工具**：Maven

## 项目结构

```
pure-java-web/
├── src/
│   └── main/
│       ├── java/com/example/web/
│       │   ├── dao/         # 数据访问层
│       │   │   └── UserDao.java
│       │   ├── filter/      # 过滤器
│       │   │   ├── AuthenticationFilter.java
│       │   │   ├── CharacterEncodingFilter.java
│       │   │   └── CORSFilter.java
│       │   ├── model/       # 实体类
│       │   │   └── User.java
│       │   ├── servlet/     # Servlet控制器
│       │   │   ├── LoginServlet.java
│       │   │   ├── LogoutServlet.java
│       │   │   ├── RegisterServlet.java
│       │   │   └── UserInfoServlet.java
│       │   └── util/        # 工具类
│       │       ├── DBUtil.java
│       │       └── MD5Util.java
│       ├── resources/
│       │   └── db.properties
│       └── webapp/
│           ├── css/
│           ├── js/
│           ├── index.html
│           ├── login.html
│           ├── register.html
│           └── WEB-INF/
│               └── web.xml
├── sql/
│   └── init.sql
├── pom.xml
└── README.md
```

## 快速开始

### 1. 环境准备

- JDK 11 或更高版本
- MySQL 8.0
- Maven 3.6+
- Tomcat 9.0+（或使用内置Tomcat插件）

### 2. 数据库配置

创建数据库并导入初始化脚本：

```bash
# 登录MySQL
mysql -u root -p

# 执行初始化脚本
source sql/init.sql
```

### 3. 配置数据库连接

编辑 `src/main/resources/db.properties`：

```properties
db.url=jdbc:mysql://localhost:3306/user_system?useUnicode=true&characterEncoding=utf8&useSSL=false&serverTimezone=Asia/Shanghai
db.username=root
db.password=your_password
db.driver=com.mysql.cj.jdbc.Driver
```

### 4. 构建和运行

使用 Maven 构建：

```bash
# 打包
mvn clean package

# 将生成的 war 包部署到 Tomcat
# 或者直接运行：
mvn tomcat7:run
```

访问地址：
- 首页：http://localhost:8080/user-system/
- 登录：http://localhost:8080/user-system/login.html
- 注册：http://localhost:8080/user-system/register.html

## API 接口

### 用户注册
```
POST /api/register
Content-Type: application/x-www-form-urlencoded

参数:
- username (必填): 用户名，4-20位字母数字下划线
- password (必填): 密码，至少6位
- confirmPassword (必填): 确认密码
- email (可选): 邮箱地址
- phone (可选): 手机号
- realName (可选): 真实姓名
```

### 用户登录
```
POST /api/login
Content-Type: application/x-www-form-urlencoded

参数:
- username (必填): 用户名
- password (必填): 密码

响应:
{
    "success": true,
    "message": "登录成功！",
    "data": {
        "id": 1,
        "username": "admin",
        "email": "admin@example.com",
        "realName": "管理员"
    }
}
```

### 获取用户信息
```
GET /api/user/info

响应:
{
    "success": true,
    "data": {
        "id": 1,
        "username": "admin",
        "email": "admin@example.com",
        "realName": "管理员",
        "phone": "13800138000"
    }
}
```

### 退出登录
```
POST /api/logout

响应:
{
    "success": true,
    "message": "退出登录成功"
}
```

## 安全特性

1. **密码加密**：使用 MD5 加密存储密码
2. **Session 管理**：使用 HttpSession 管理用户登录状态
3. **CSRF 防护**：通过过滤器验证请求来源
4. **SQL 注入防护**：使用 PreparedStatement 防止 SQL 注入
5. **XSS 防护**：对用户输入进行转义处理

## 技术说明

### 纯 Java 实现原则

本项目遵循以下纯 Java 实现原则：

1. **不使用 Spring 框架**：所有依赖注入和对象管理使用原生 Java 实现
2. **不使用 Spring Boot**：通过 web.xml 和注解配置 Servlet
3. **手动管理事务**：通过 JDBC 手动控制数据库事务
4. **原生 Servlet API**：使用标准的 javax.servlet API
5. **手动 JSON 处理**：不使用 Jackson，使用原生 Java 处理 JSON 序列化

### 架构设计

```
前端 (HTML + CSS + JS)
    ↓ HTTP Request
Servlet Controller
    ↓
Service Layer (可选)
    ↓
DAO Layer
    ↓ JDBC
MySQL Database
```

## 开发计划

### 已实现功能
- [x] 项目基础架构搭建
- [x] 数据库连接工具
- [x] 用户注册
- [x] 用户登录
- [x] 用户注销
- [x] 用户信息查询
- [x] 前端界面（登录、注册、首页）

### 待实现功能
- [ ] 用户密码修改
- [ ] 用户信息编辑
- [ ] 用户头像上传
- [ ] 管理员后台
- [ ] 用户列表分页查询
- [ ] 登录日志记录
- [ ] 邮件找回密码

## 贡献指南

欢迎提交 Pull Request 或 Issue 来改进这个项目。

## 许可证

本项目采用 MIT 许可证。

## 联系方式

如有问题或建议，欢迎联系。

---

**注意**：本项目为学习演示项目，实际生产环境请使用更完善的安全措施，如 HTTPS、更强的密码加密算法（如 BCrypt）等。
