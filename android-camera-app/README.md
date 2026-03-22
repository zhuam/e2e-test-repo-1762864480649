# Camera AI - Android Application

Android 拍照应用，支持拍照并使用 AI 模型分析和解读图片。

## 功能特性

- **相机预览**: 使用 CameraX 实现实时相机预览
- **拍照功能**: 使用 ImageCapture API 拍摄高质量照片
- **图库集成**: 从设备图库选择图片
- **AI 图像分析**: 发送图片到 AI 模型进行解读分析
  - 支持 OpenAI GPT-4 Vision
  - 支持 Anthropic Claude
  - 支持自定义 API 端点
  - 支持本地 TensorFlow Lite 模型
- **现代化 UI**: Material Design 风格的简洁界面
- **响应式设计**: 支持各种 Android 设备

## 项目结构

```
android-camera-app/
├── app/
│   ├── src/main/
│   │   ├── java/com/example/cameraai/
│   │   │   ├── MainActivity.java       # 主界面Activity
│   │   │   ├── CameraHelper.java       # 相机工具类
│   │   │   └── ModelInterpreter.java   # AI 模型调用
│   │   ├── res/
│   │   │   ├── layout/
│   │   │   │   └── activity_main.xml   # 主界面布局
│   │   │   ├── values/
│   │   │   │   ├── strings.xml         # 字符串资源
│   │   │   │   ├── colors.xml          # 颜色定义
│   │   │   │   └── themes.xml          # 应用主题
│   │   │   ├── drawable/               # 矢量图标
│   │   │   └── xml/
│   │   │       └── file_paths.xml      # 文件共享路径
│   │   └── AndroidManifest.xml
│   ├── build.gradle
│   └── proguard-rules.pro
├── gradle/wrapper/
│   └── gradle-wrapper.properties
├── build.gradle
├── settings.gradle
├── gradle.properties
└── README.md
```

## 环境要求

- Android Studio Hedgehog (2023.1.1) 或更新版本
- Android SDK 34 (或更新版本)
- 最低支持 Android 7.0 (API 24)
- Java 17

## 快速开始

### 1. 在 Android Studio 中打开

1. 启动 Android Studio
2. 选择 "Open an Existing Project"
3. 导航到 `android-camera-app` 目录
4. 等待 Gradle 同步完成

### 2. 配置 AI API

#### 获取 API Key

**OpenAI (GPT-4 Vision):**
- 访问 https://platform.openai.com/api-keys
- 创建新的 API Key

**Anthropic (Claude):**
- 访问 https://console.anthropic.com/settings/keys
- 创建新的 API Key

#### 在代码中配置

打开 `app/src/main/java/com/example/cameraai/ModelInterpreter.java`，修改：

```java
// 替换为你的 API Key
private static final String API_KEY = "your-actual-api-key";

// 选择 AI 提供商
private AIProvider currentProvider = AIProvider.OPENAI;  // 或 CLAUDE、CUSTOM、LOCAL_TFLITE
```

#### 支持的 AI 服务

| Provider | 说明 | 文档 |
|----------|------|------|
| OPENAI | GPT-4 Vision 图像识别 | [OpenAI](https://platform.openai.com/docs) |
| CLAUDE | Claude 3 图像理解 | [Anthropic](https://docs.anthropic.com/claude/docs) |
| CUSTOM | 自定义 API 端点 | 自行配置 |
| LOCAL_TFLITE | 本地 TensorFlow Lite | 需要添加.tflite 模型 |

> **安全提示**: 生产环境请勿将 API Key 存储在客户端代码中！应使用后端服务器代理请求。

### 3. 构建和运行

1. 连接 Android 设备或启动带摄像头的模拟器
2. 点击 "Run" 按钮 (或按 Shift+F10)
3. 当提示时授予相机权限

## 使用方法

### 拍照分析

1. 点击底部中央的**拍照按钮**（圆圈图标）
2. 预览拍摄的照片
3. 点击**Analyze with AI**按钮进行分析
4. 或点击**Retake**重新拍摄

### 从图库选择

1. 点击左下角的**图库图标**
2. 从图库中选择图片
3. 点击**Analyze with AI**进行分析

### 查看结果

AI 分析结果会显示在屏幕底部的文本区域。

## 依赖项

```gradle
// CameraX - 相机功能
androidx.camera:camera-core:1.3.1
androidx.camera:camera-camera2:1.3.1
androidx.camera:camera-lifecycle:1.3.1
androidx.camera:camera-view:1.3.1

// OkHttp - HTTP 客户端
com.squareup.okhttp3:okhttp:4.12.0

// Gson - JSON 解析
com.google.code.gson:gson:2.10.1

// Material Design
com.google.android.material:material:1.11.0
```

## 权限说明

应用需要以下权限：

| 权限 | 用途 |
|------|------|
| CAMERA | 访问相机拍照 |
| INTERNET | 调用 AI API 分析图片 |
| READ_EXTERNAL_STORAGE | 访问图库 (Android 12 及以下) |

## 自定义

### 修改 AI 分析提示词

编辑 `ModelInterpreter.java` 中的提示词：

```java
// OpenAI
textContent.put("text", "详细描述这张图片中的内容。");

// Claude
textContent.put("text", "Describe what you see in this image in detail.");
```

### 修改 API 端点

编辑 `ModelInterpreter.java` 中的 URL：

```java
private static final String OPENAI_VISION_URL = "https://api.openai.com/v1/chat/completions";
```

### 自定义 UI 主题

编辑 `app/src/main/res/values/colors.xml` 和 `themes.xml` 修改颜色主题。

## 常见问题

### 相机无法使用

- 确保设备有摄像头
- 在系统设置中检查相机权限
- 尝试重启应用

### AI 分析失败

- 确认 API Key 正确
- 检查网络连接
- 确认 API 配额充足
- 查看 Logcat 详细错误信息

### 构建错误

- 同步 Gradle 文件
- 更新 Android Studio 到最新版本
- Clean and Rebuild 项目

## 许可证

本项目供学习使用。

## 贡献

欢迎提交 Issue 和 Pull Request。
