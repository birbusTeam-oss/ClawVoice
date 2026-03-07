package com.birbus.clawvoice

import android.accessibilityservice.AccessibilityServiceInfo
import android.content.Context
import android.content.Intent
import android.os.Bundle
import android.provider.Settings
import android.view.accessibility.AccessibilityManager
import androidx.appcompat.app.AppCompatActivity
import android.widget.Button
import android.widget.EditText
import android.widget.TextView
import com.birbus.clawvoice.security.SecureStorage
import com.birbus.clawvoice.security.SecurityAudit

class MainActivity : AppCompatActivity() {

    private lateinit var secureStorage: SecureStorage

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        secureStorage = SecureStorage(this)

        // API key input — load from encrypted storage
        val apiKeyInput = findViewById<EditText>(R.id.apiKeyInput)
        apiKeyInput.setText(secureStorage.getApiKey() ?: "")

        // Save API key to encrypted storage
        findViewById<Button>(R.id.saveApiKeyBtn).setOnClickListener {
            val key = apiKeyInput.text.toString().trim()
            if (key.isNotBlank()) {
                secureStorage.saveApiKey(key)
                SecurityAudit.apiKeySet(this)
            }
        }

        // Accessibility service status
        val statusText = findViewById<TextView>(R.id.accessibilityStatus)
        updateAccessibilityStatus(statusText)

        // Open accessibility settings
        findViewById<Button>(R.id.openAccessibilityBtn).setOnClickListener {
            startActivity(Intent(Settings.ACTION_ACCESSIBILITY_SETTINGS))
        }

        // Manual record button (for testing without overlay)
        val recordBtn = findViewById<Button>(R.id.recordBtn)
        recordBtn.setOnClickListener {
            val intent = Intent(this, VoiceRecordingService::class.java)
            intent.action = VoiceRecordingService.ACTION_START
            startForegroundService(intent)
        }

        val stopBtn = findViewById<Button>(R.id.stopBtn)
        stopBtn.setOnClickListener {
            val intent = Intent(this, VoiceRecordingService::class.java)
            intent.action = VoiceRecordingService.ACTION_STOP
            startService(intent)
        }
    }

    override fun onResume() {
        super.onResume()
        val statusText = findViewById<TextView>(R.id.accessibilityStatus)
        updateAccessibilityStatus(statusText)
    }

    private fun updateAccessibilityStatus(tv: TextView) {
        val am = getSystemService(Context.ACCESSIBILITY_SERVICE) as AccessibilityManager
        val enabled = am.getEnabledAccessibilityServiceList(AccessibilityServiceInfo.FEEDBACK_ALL_MASK)
            .any { it.resolveInfo.serviceInfo.packageName == packageName }
        tv.text = if (enabled) "✅ Accessibility Service: ON" else "❌ Accessibility Service: OFF — tap button below to enable"
    }
}
