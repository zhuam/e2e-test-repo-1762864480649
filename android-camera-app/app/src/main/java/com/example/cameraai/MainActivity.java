package com.example.cameraai;

import android.Manifest;
import android.content.Intent;
import android.content.pm.PackageManager;
import android.graphics.Bitmap;
import android.graphics.BitmapFactory;
import android.net.Uri;
import android.os.Bundle;
import android.os.Environment;
import android.provider.MediaStore;
import android.util.Log;
import android.view.View;
import android.widget.Button;
import android.widget.ImageButton;
import android.widget.ImageView;
import android.widget.LinearLayout;
import android.widget.TextView;
import android.widget.Toast;

import androidx.activity.result.ActivityResultLauncher;
import androidx.activity.result.contract.ActivityResultContracts;
import androidx.annotation.NonNull;
import androidx.appcompat.app.AppCompatActivity;
import androidx.camera.core.CameraSelector;
import androidx.camera.core.ImageCapture;
import androidx.camera.core.ImageCaptureException;
import androidx.camera.core.Preview;
import androidx.camera.lifecycle.ProcessCameraProvider;
import androidx.camera.view.PreviewView;
import androidx.core.content.ContextCompat;
import androidx.core.content.FileProvider;

import com.google.common.util.concurrent.ListenableFuture;

import java.io.File;
import java.io.IOException;
import java.text.SimpleDateFormat;
import java.util.Date;
import java.util.Locale;
import java.util.concurrent.ExecutionException;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;

/**
 * MainActivity - Main entry point for the Camera AI application
 * Handles camera preview, photo capture, and AI analysis integration
 */
public class MainActivity extends AppCompatActivity {

    private static final String TAG = "MainActivity";
    private static final int REQUEST_CODE_PERMISSIONS = 10;
    private static final String[] REQUIRED_PERMISSIONS = new String[]{
            Manifest.permission.CAMERA
    };

    // UI Components
    private PreviewView previewView;
    private ImageView capturedImageView;
    private View loadingOverlay;
    private TextView resultTextView;
    private ImageButton captureButton;
    private ImageButton galleryButton;
    private ImageButton analyzeButton;
    private Button retakeButton;
    private Button saveButton;
    private LinearLayout retakeSaveControls;

    // CameraX components
    private ListenableFuture<ProcessCameraProvider> cameraProviderFuture;
    private ImageCapture imageCapture;
    private ExecutorService cameraExecutor;

    // Current photo
    private File photoFile;
    private Bitmap currentBitmap;

    // AI Model Interpreter
    private ModelInterpreter modelInterpreter;

    // Gallery launcher
    private final ActivityResultLauncher<Intent> galleryLauncher =
            registerForActivityResult(new ActivityResultContracts.StartActivityForResult(),
                    result -> {
                        if (result.getResultCode() == RESULT_OK && result.getData() != null) {
                            Uri imageUri = result.getData().getData();
                            if (imageUri != null) {
                                loadGalleryImage(imageUri);
                            }
                        }
                    });

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        initViews();
        initModelInterpreter();

        cameraExecutor = Executors.newSingleThreadExecutor();
        cameraProviderFuture = ProcessCameraProvider.getInstance(this);

        // Request camera permissions
        if (!allPermissionsGranted()) {
            requestPermissions();
        } else {
            startCamera();
        }

        setupClickListeners();
    }

    private void initViews() {
        previewView = findViewById(R.id.previewView);
        capturedImageView = findViewById(R.id.capturedImageView);
        loadingOverlay = findViewById(R.id.loadingOverlay);
        resultTextView = findViewById(R.id.resultTextView);
        captureButton = findViewById(R.id.captureButton);
        galleryButton = findViewById(R.id.galleryButton);
        analyzeButton = findViewById(R.id.analyzeButton);
        retakeButton = findViewById(R.id.retakeButton);
        saveButton = findViewById(R.id.saveButton);
        retakeSaveControls = findViewById(R.id.retakeSaveControls);
    }

    private void initModelInterpreter() {
        // Initialize with default API endpoint
        // You can configure your own API key in ModelInterpreter
        modelInterpreter = new ModelInterpreter();
    }

    private void setupClickListeners() {
        captureButton.setOnClickListener(v -> takePhoto());

        galleryButton.setOnClickListener(v -> openGallery());

        analyzeButton.setOnClickListener(v -> analyzeCapturedImage());

        retakeButton.setOnClickListener(v -> retakePhoto());

        saveButton.setOnClickListener(v -> analyzeCapturedImage());
    }

    private boolean allPermissionsGranted() {
        for (String permission : REQUIRED_PERMISSIONS) {
            if (ContextCompat.checkSelfPermission(this, permission)
                    != PackageManager.PERMISSION_GRANTED) {
                return false;
            }
        }
        return true;
    }

    private void requestPermissions() {
        requestPermissions(REQUIRED_PERMISSIONS, REQUEST_CODE_PERMISSIONS);
    }

    @Override
    public void onRequestPermissionsResult(int requestCode, @NonNull String[] permissions,
                                           @NonNull int[] grantResults) {
        super.onRequestPermissionsResult(requestCode, permissions, grantResults);
        if (requestCode == REQUEST_CODE_PERMISSIONS) {
            if (allPermissionsGranted()) {
                startCamera();
            } else {
                Toast.makeText(this, R.string.permission_required, Toast.LENGTH_SHORT).show();
                finish();
            }
        }
    }

    private void startCamera() {
        cameraProviderFuture.addListener(() -> {
            try {
                ProcessCameraProvider cameraProvider = cameraProviderFuture.get();
                bindCameraUseCases(cameraProvider);
            } catch (ExecutionException | InterruptedException e) {
                Log.e(TAG, "Camera initialization failed", e);
            }
        }, ContextCompat.getMainExecutor(this));
    }

    private void bindCameraUseCases(@NonNull ProcessCameraProvider cameraProvider) {
        // Preview use case
        Preview preview = new Preview.Builder().build();
        preview.setSurfaceProvider(previewView.getSurfaceProvider());

        // ImageCapture use case
        imageCapture = new ImageCapture.Builder()
                .setCaptureMode(ImageCapture.CAPTURE_MODE_MAXIMIZE_QUALITY)
                .build();

        // Camera selector (back camera)
        CameraSelector cameraSelector = CameraSelector.DEFAULT_BACK_CAMERA;

        try {
            cameraProvider.unbindAll();
            cameraProvider.bindToLifecycle(
                    this, cameraSelector, preview, imageCapture);
        } catch (IllegalArgumentException e) {
            Log.e(TAG, "Camera binding failed", e);
        }
    }

    private void takePhoto() {
        if (imageCapture == null) return;

        // Create photo file
        photoFile = createImageFile();

        // Create output options
        ImageCapture.OutputFileOptions options =
                new ImageCapture.OutputFileOptions.Builder(photoFile).build();

        imageCapture.takePicture(options,
                ContextCompat.getMainExecutor(this),
                new ImageCapture.OnImageSavedCallback() {
                    @Override
                    public void onImageSaved(@NonNull ImageCapture.OutputFileResults outputFileResults) {
                        onPhotoCaptured(photoFile);
                    }

                    @Override
                    public void onError(@NonNull ImageCaptureException exception) {
                        Log.e(TAG, getString(R.string.error_taking_photo), exception);
                        Toast.makeText(MainActivity.this,
                                R.string.error_taking_photo, Toast.LENGTH_SHORT).show();
                    }
                });
    }

    private File createImageFile() {
        String timeStamp = new SimpleDateFormat("yyyyMMdd_HHmmss", Locale.getDefault()).format(new Date());
        String imageFileName = "JPEG_" + timeStamp + "_";
        File storageDir = getExternalFilesDir(Environment.DIRECTORY_PICTURES);

        try {
            return File.createTempFile(imageFileName, ".jpg", storageDir);
        } catch (IOException e) {
            Log.e(TAG, "Error creating image file", e);
            return new File(getCacheDir(), "temp_image.jpg");
        }
    }

    private void onPhotoCaptured(File file) {
        // Load and display captured image
        currentBitmap = BitmapFactory.decodeFile(file.getAbsolutePath());

        previewView.setVisibility(View.GONE);
        capturedImageView.setImageBitmap(currentBitmap);
        capturedImageView.setVisibility(View.VISIBLE);

        retakeSaveControls.setVisibility(View.VISIBLE);

        // Clear previous result
        resultTextView.setText("");
    }

    private void openGallery() {
        Intent galleryIntent = new Intent(Intent.ACTION_PICK,
                MediaStore.Images.Media.EXTERNAL_CONTENT_URI);
        galleryIntent.setType("image/*");
        galleryLauncher.launch(galleryIntent);
    }

    private void loadGalleryImage(Uri imageUri) {
        try {
            currentBitmap = MediaStore.Images.Media.getBitmap(
                    getContentResolver(), imageUri);

            previewView.setVisibility(View.GONE);
            capturedImageView.setImageBitmap(currentBitmap);
            capturedImageView.setVisibility(View.VISIBLE);

            retakeSaveControls.setVisibility(View.VISIBLE);
            resultTextView.setText("");
        } catch (IOException e) {
            Log.e(TAG, "Error loading gallery image", e);
            Toast.makeText(this, "Error loading image", Toast.LENGTH_SHORT).show();
        }
    }

    private void retakePhoto() {
        // Reset UI to camera preview
        previewView.setVisibility(View.VISIBLE);
        capturedImageView.setVisibility(View.GONE);
        retakeSaveControls.setVisibility(View.GONE);

        currentBitmap = null;
        photoFile = null;
        resultTextView.setText("");
    }

    private void analyzeCapturedImage() {
        if (currentBitmap == null) {
            Toast.makeText(this, R.string.no_image_captured, Toast.LENGTH_SHORT).show();
            return;
        }

        // Show loading indicator
        loadingOverlay.setVisibility(View.VISIBLE);
        resultTextView.setText("");

        // Call AI model in background
        cameraExecutor.execute(() -> {
            try {
                // Call AI model API
                String result = modelInterpreter.analyzeImage(currentBitmap);

                // Update UI on main thread
                runOnUiThread(() -> {
                    loadingOverlay.setVisibility(View.GONE);
                    if (result != null) {
                        resultTextView.setText(getString(R.string.ai_result, result));
                    } else {
                        resultTextView.setText(R.string.error_analyzing);
                    }
                });
            } catch (Exception e) {
                Log.e(TAG, "AI analysis failed", e);
                runOnUiThread(() -> {
                    loadingOverlay.setVisibility(View.GONE);
                    resultTextView.setText(R.string.error_analyzing);
                });
            }
        });
    }

    @Override
    protected void onDestroy() {
        super.onDestroy();
        cameraExecutor.shutdown();
    }
}
