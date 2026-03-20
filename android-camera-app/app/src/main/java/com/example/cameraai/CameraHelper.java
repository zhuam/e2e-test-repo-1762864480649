package com.example.cameraai;

import android.content.Context;
import android.graphics.Bitmap;
import android.graphics.BitmapFactory;
import android.graphics.ImageFormat;
import android.graphics.Matrix;
import android.graphics.Rect;
import android.graphics.YuvImage;
import android.media.Image;
import android.util.Log;

import androidx.camera.core.ImageProxy;

import java.io.ByteArrayOutputStream;
import java.nio.ByteBuffer;

/**
 * CameraHelper - Utility class for camera operations
 * Provides image processing utilities for CameraX ImageProxy conversion and manipulation
 */
public class CameraHelper {

    private static final String TAG = "CameraHelper";

    /**
     * Convert ImageProxy (from CameraX) to Bitmap
     * Handles YUV_420_888 format which is the most common
     *
     * @param imageProxy The ImageProxy from CameraX
     * @return Bitmap representation of the image
     */
    public static Bitmap imageProxyToBitmap(ImageProxy imageProxy) {
        Image image = imageProxy.getImage();
        if (image == null) {
            return null;
        }

        int width = imageProxy.getWidth();
        int height = imageProxy.getHeight();
        int format = image.getFormat();

        Bitmap bitmap;

        if (format == ImageFormat.YUV_420_888) {
            bitmap = yuvImageToBitmap(image, width, height);
        } else if (format == ImageFormat.JPEG) {
            bitmap = jpegImageToBitmap(image);
        } else {
            // Try to handle other formats
            bitmap = genericImageToBitmap(image);
        }

        // Apply rotation if needed
        int rotationDegrees = imageProxy.getImageInfo().getRotationDegrees();
        if (rotationDegrees != 0 && bitmap != null) {
            bitmap = rotateBitmap(bitmap, rotationDegrees);
        }

        return bitmap;
    }

    /**
     * Convert YUV_420_888 Image to Bitmap
     */
    private static Bitmap yuvImageToBitmap(Image image, int width, int height) {
        try {
            ByteBuffer yBuffer = image.getPlanes()[0].getBuffer();
            ByteBuffer uBuffer = image.getPlanes()[1].getBuffer();
            ByteBuffer vBuffer = image.getPlanes()[2].getBuffer();

            int ySize = yBuffer.remaining();
            int uSize = uBuffer.remaining();
            int vSize = vBuffer.remaining();

            byte[] nv21 = new byte[ySize + uSize + vSize];

            yBuffer.get(nv21, 0, ySize);
            vBuffer.get(nv21, ySize, vSize);
            uBuffer.get(nv21, ySize + vSize, uSize);

            YuvImage yuvImage = new YuvImage(nv21, ImageFormat.NV21, width, height, null);
            ByteArrayOutputStream outputStream = new ByteArrayOutputStream();
            yuvImage.compressToJpeg(new Rect(0, 0, width, height), 80, outputStream);

            byte[] jpegBytes = outputStream.toByteArray();
            return BitmapFactory.decodeByteArray(jpegBytes, 0, jpegBytes.length);
        } catch (Exception e) {
            Log.e(TAG, "Error converting YUV image", e);
            return null;
        }
    }

    /**
     * Convert JPEG Image to Bitmap
     */
    private static Bitmap jpegImageToBitmap(Image image) {
        ByteBuffer buffer = image.getPlanes()[0].getBuffer();
        byte[] bytes = new byte[buffer.remaining()];
        buffer.get(bytes);
        return BitmapFactory.decodeByteArray(bytes, 0, bytes.length);
    }

    /**
     * Generic Image to Bitmap conversion
     */
    private static Bitmap genericImageToBitmap(Image image) {
        ByteBuffer buffer = image.getPlanes()[0].getBuffer();
        byte[] bytes = new byte[buffer.remaining()];
        buffer.get(bytes);
        return BitmapFactory.decodeByteArray(bytes, 0, bytes.length);
    }

    /**
     * Rotate a bitmap by the specified degrees
     */
    public static Bitmap rotateBitmap(Bitmap bitmap, int rotationDegrees) {
        if (bitmap == null || rotationDegrees == 0) {
            return bitmap;
        }

        Matrix matrix = new Matrix();
        matrix.postRotate(rotationDegrees);

        return Bitmap.createBitmap(
                bitmap, 0, 0, bitmap.getWidth(), bitmap.getHeight(),
                matrix, true);
    }

    /**
     * Resize bitmap to specified dimensions while maintaining aspect ratio
     */
    public static Bitmap resizeBitmap(Bitmap bitmap, int maxWidth, int maxHeight) {
        if (bitmap == null) {
            return null;
        }

        int width = bitmap.getWidth();
        int height = bitmap.getHeight();

        // Calculate new dimensions while maintaining aspect ratio
        float ratio = Math.min(
                (float) maxWidth / width,
                (float) maxHeight / height);

        int newWidth = Math.round(width * ratio);
        int newHeight = Math.round(height * ratio);

        return Bitmap.createScaledBitmap(bitmap, newWidth, newHeight, true);
    }

    /**
     * Convert Bitmap to byte array for API transmission
     */
    public static byte[] bitmapToByteArray(Bitmap bitmap, int quality) {
        ByteArrayOutputStream outputStream = new ByteArrayOutputStream();
        bitmap.compress(Bitmap.CompressFormat.JPEG, quality, outputStream);
        return outputStream.toByteArray();
    }

    /**
     * Get bitmap dimensions that are suitable for AI model input
     * Most models expect specific input sizes (e.g., 224x224, 512x512)
     */
    public static Bitmap prepareBitmapForModel(Bitmap bitmap, int targetSize) {
        return resizeBitmap(bitmap, targetSize, targetSize);
    }

    /**
     * Calculate the center crop region of an image
     * Useful for square cropping before model analysis
     */
    public static Bitmap centerCrop(Bitmap bitmap) {
        if (bitmap == null) {
            return null;
        }

        int width = bitmap.getWidth();
        int height = bitmap.getHeight();
        int size = Math.min(width, height);

        int x = (width - size) / 2;
        int y = (height - size) / 2;

        return Bitmap.createBitmap(bitmap, x, y, size, size);
    }

    /**
     * Convert ImageProxy to JPEG byte array
     * Useful for uploading to API endpoints
     */
    public static byte[] imageProxyToJpeg(ImageProxy imageProxy) {
        Bitmap bitmap = imageProxyToBitmap(imageProxy);
        if (bitmap == null) {
            return null;
        }
        return bitmapToByteArray(bitmap, 85);
    }

    /**
     * Release ImageProxy resources
     * Should be called after processing is complete
     */
    public static void closeImageProxy(ImageProxy imageProxy) {
        if (imageProxy != null) {
            imageProxy.close();
        }
    }
}
