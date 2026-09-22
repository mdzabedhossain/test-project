plugins {
    id("com.android.application")
    id("org.jetbrains.kotlin.android")
}
android {
    namespace = "com.zabed.novacart"
    compileSdk = 36
    defaultConfig {
        applicationId = "com.zabed.novacart"
        minSdk = 23
        targetSdk = 36
        versionCode = 1
        versionName = "1.0"
    }
}
