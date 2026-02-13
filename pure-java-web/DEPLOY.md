# 部署指南

## 环境要求

- JDK 11 或更高版本
- MySQL 8.0
- Maven 3.6+
- Tomcat 9.0+ (可选)

## 快速部署步骤

### 1. 初始化数据库

```bash
# 登录MySQL
mysql -u root -p

# 执行初始化脚本
source sql/init.sql
```

### 2. 配置数据库连接

编辑 `src/main/resources/db.properties`：

```properties
db.url=jdbc:mysql://localhost:3306/user_system?useUnicode=true&characterEncoding=utf8&useSSL=false&serverTimezone=Asia Shanghai&allowPublicKeyRetrieval=true
db.username=root
db.password=your_password
db.driver=com.mysql.cj.jdbc.Driver
```

### 3. 构建项目

```bash
cd pure-java-web
mvn clean package
```

### 4. 部署运行

**方式一：使用 Tomcat**

将 `target/user-system.war` 复制到 Tomcat 的 `webapps` 目录：

```bash
cp target/user-system.war /path/to/tomcat/webapps/
```

启动 Tomcat 后访问：http://localhost:8080/user-system/

**方式二：使用 Maven Tomcat 插件**

```bash
mvn tomcat7:run
```

访问：http://localhost:8080/user-system/

## 访问地址

- 首页：http://localhost:8080/user-system/
- 登录：http://localhost:8080/user-system/login.html
- 注册：http://localhost:8080/user-system/register.html

## 测试账号

```
用户名: admin
密码: 123456

用户名: test
密码: 123456
```

## 常见问题

### 1. 数据库连接失败

- 检查MySQL服务是否启动
- 检查用户名和密码是否正确
- 检查数据库 `user_system` 是否已创建
- 检查MySQL端口是否为3306

### 2. 中文乱码

- 确保数据库使用 UTF-8 编码
- 确保配置文件中的连接字符串包含 `useUnicode=true&characterEncoding=utf8`

### 3. 无法访问静态资源

- 检查 web.xml 中的 MIME 类型映射
- 确认静态资源文件存在于正确的位置

## 联系方式

如有问题或建议，欢迎反馈。
