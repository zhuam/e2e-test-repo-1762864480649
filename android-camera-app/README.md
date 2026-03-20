# Camera AI - Android Application

An Android camera application that can take photos and use AI models to interpret and analyze images.

## Features

- **Camera Preview**: Real-time camera preview using CameraX
- **Photo Capture**: High-quality photo capture with ImageCapture API
- **Gallery Integration**: Select images from device gallery
- **AI Image Analysis**: Send captured images to AI models for interpretation
- **Modern UI**: Clean, intuitive user interface with Material Design

## Project Structure

```
android-camera-app/
├── app/
│   ├── src/main/
│   │   ├── java/com/example/cameraai/
│   │   │   ├── MainActivity.java       # Main activity with camera UI
│   │   │   ├── CameraHelper.java       # Camera utility functions
│   │   │   └── ModelInterpreter.java   # AI model integration
│   │   ├── res/
│   │   │   ├── layout/
│   │   │   │   └── activity_main.xml   # Main layout
│   │   │   ├── values/
│   │   │   │   ├── strings.xml         # String resources
│   │   │   │   ├── colors.xml          # Color definitions
│   │   │   │   └── themes.xml          # App theme
│   │   │   ├── drawable/               # Vector drawables
│   │   │   └── xml/
│   │   │       └── file_paths.xml      # FileProvider paths
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

## Prerequisites

- Android Studio Hedgehog (2023.1.1) or newer
- Android SDK 34 (or newer)
- Minimum SDK 24 (Android 7.0)
- Java 17

## Setup Instructions

### 1. Open in Android Studio

1. Open Android Studio
2. Select "Open an Existing Project"
3. Navigate to the `android-camera-app` folder
4. Wait for Gradle sync to complete

### 2. Configure AI API (Optional)

To use AI image analysis, you need to configure an API key:

1. Open `app/src/main/java/com/example/cameraai/ModelInterpreter.java`
2. Replace `YOUR_API_KEY_HERE` with your API key:

```java
private static final String API_KEY = "your-actual-api-key";
```

3. Select your preferred AI provider:

```java
private AIProvider currentProvider = AIProvider.OPENAI;  // or CLAUDE, CUSTOM, LOCAL_TFLITE
```

### Supported AI Providers

- **OpenAI GPT-4 Vision** (`AIProvider.OPENAI`)
- **Anthropic Claude** (`AIProvider.CLAUDE`)
- **Custom Endpoint** (`AIProvider.CUSTOM`)
- **Local TensorFlow Lite** (`AIProvider.LOCAL_TFLITE`)

> **Security Note**: Never store API keys in production client code. Use a backend server to proxy requests.

### 3. Build and Run

1. Connect an Android device or start an emulator with camera support
2. Click "Run" (or press Shift+F10)
3. Grant camera permission when prompted

## Dependencies

- **CameraX**: `androidx.camera:camera-*` (1.3.1) - Camera functionality
- **OkHttp**: `com.squareup.okhttp3:okhttp` (4.12.0) - HTTP client for API calls
- **Gson**: `com.google.code.gson:gson` (2.10.1) - JSON parsing
- **Material Components**: `com.google.android.material:material` (1.11.0)
- **AndroidX Core**: Various AndroidX libraries

## Usage

### Taking a Photo

1. Tap the **capture button** (center circle) to take a photo
2. Preview the captured image
3. Tap **Analyze with AI** to analyze, or **Retake** to capture again

### Using Gallery Images

1. Tap the **gallery icon** (bottom left) to select an image
2. Choose an image from your gallery
3. Tap **Analyze with AI** to analyze

### Viewing Results

AI analysis results appear in the text area at the bottom of the screen.

## Permissions

The app requires the following permissions:

- `CAMERA` - Required for camera access
- `INTERNET` - Required for AI API calls
- `READ_EXTERNAL_STORAGE` - For gallery access (SDK 32 and below)

## Customization

### Changing AI Model Behavior

Edit the prompt in `ModelInterpreter.java`:

```java
textContent.put("text", "Describe what you see in this image in detail.");
```

### Adding Local TFLite Model

Implement the `callLocalModel()` method in `ModelInterpreter.java`:

```java
private String callLocalModel(Bitmap bitmap) {
    // Load TFLite model
    // Preprocess image
    // Run inference
    // Post-process results
    return result;
}
```

### Modifying UI Theme

Edit `app/src/main/res/values/colors.xml` and `themes.xml` to customize colors.

## Troubleshooting

### Camera Not Working

- Ensure device has a camera
- Check camera permissions in Settings
- Try restarting the app

### AI Analysis Failing

- Verify API key is correct
- Check internet connection
- Ensure API quota is available
- Check Logcat for detailed error messages

### Build Errors

- Sync Gradle files
- Update Android Studio to latest version
- Clean and rebuild project

## License

This project is provided as-is for educational purposes.

## Contributing

Feel free to submit issues and pull requests to improve the app.
