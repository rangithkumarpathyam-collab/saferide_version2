import com.android.build.api.variant.ApplicationAndroidComponentsExtension
import java.util.Properties

plugins {
    id("com.android.application")
}

val envProperties = Properties().apply {
    val envFile = rootProject.file("../.env")
    if (envFile.exists()) {
        envFile.forEachLine { line ->
            val trimmed = line.trim()
            if (trimmed.isNotEmpty() && !trimmed.startsWith("#") && trimmed.contains("=")) {
                val idx = trimmed.indexOf('=')
                val key = trimmed.substring(0, idx).trim()
                val value = trimmed.substring(idx + 1).trim()
                setProperty(key, value)
            }
        }
    }
}

val twilioSid = envProperties.getProperty("TWILIO_ACCOUNT_SID") ?: ""
val twilioToken = envProperties.getProperty("TWILIO_AUTH_TOKEN") ?: ""
val twilioFrom = envProperties.getProperty("TWILIO_PHONE_NUMBER") ?: ""
val emergencyPhone = envProperties.getProperty("EMERGENCY_DISPATCH_PHONE") ?: "+917416960828"
val supabaseUrl = envProperties.getProperty("SUPABASE_URL") ?: ""
val supabaseKey = envProperties.getProperty("SUPABASE_KEY") ?: ""
val renderUrl = envProperties.getProperty("RENDER_DEPLOYMENT_URL") ?: "https://saferide-version2.onrender.com"

android {
    namespace = "com.saferide.rider"
    compileSdk = 35

    defaultConfig {
        applicationId = "com.saferide.rider"
        minSdk = 26
        targetSdk = 35
        versionCode = 1
        versionName = "1.0"
        // Render cloud deployment (production) or local fallback for dev
        buildConfigField("String", "API_BASE_URL", "\"$renderUrl\"")
        buildConfigField("String", "API_TOKEN", "\"\"")
        buildConfigField("String", "EMERGENCY_PHONE", "\"$emergencyPhone\"")
        buildConfigField("String", "TWILIO_ACCOUNT_SID", "\"$twilioSid\"")
        buildConfigField("String", "TWILIO_AUTH_TOKEN", "\"$twilioToken\"")
        buildConfigField("String", "TWILIO_PHONE_NUMBER", "\"$twilioFrom\"")
        buildConfigField("String", "SUPABASE_URL", "\"$supabaseUrl\"")
        buildConfigField("String", "SUPABASE_KEY", "\"$supabaseKey\"")
    }

    buildFeatures {
        buildConfig = true
    }
}

// kotlin {
//    jvmToolchain(17)
// }

val setupAdbReverse = tasks.register<Exec>("setupAdbReverse") {
    description = "Forward host API port 8000 to connected USB device"
    val adb = project.extensions.getByType(ApplicationAndroidComponentsExtension::class.java)
        .sdkComponents.adb.get().asFile.absolutePath
    commandLine(adb, "reverse", "tcp:8000", "tcp:8000")
    isIgnoreExitValue = true
    doLast {
        println("SafeRide: Configured adb reverse tcp:8000 tcp:8000")
    }
}

tasks.matching { it.name.startsWith("install") || it.name.startsWith("assemble") }.configureEach {
    finalizedBy(setupAdbReverse)
}
