# ClawVoice ProGuard Rules

# Keep API client and security classes intact
-keep class com.birbus.clawvoice.** { *; }

# OkHttp
-dontwarn okhttp3.**
-keep class okhttp3.** { *; }

# AndroidX Security Crypto
-keep class androidx.security.crypto.** { *; }
-dontwarn androidx.security.crypto.**

# Remove all logging in release builds
-assumenosideeffects class android.util.Log {
    public static int d(...);
    public static int v(...);
    public static int i(...);
    public static int w(...);
    public static int e(...);
}

# Never log API keys
-assumenosideeffects class * {
    *api_key*;
    *apiKey*;
    *API_KEY*;
}

# JSON
-keep class org.json.** { *; }

# Kotlin coroutines
-keepnames class kotlinx.coroutines.** { *; }
-dontwarn kotlinx.coroutines.**
