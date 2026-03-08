package com.birbus.clawvoice

import android.accessibilityservice.AccessibilityServiceInfo
import android.content.Context
import android.content.Intent
import android.net.Uri
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

        val apiKeyInput = findViewById<EditText>(R.id.et_api_key)
        apiKeyInput.setText(secureStorage.getApiKey() ?: "")

        findViewById<Button>(R.id.btn_save).setOnClickListener {
            val key = apiKeyInput.text.toString().trim()
            if (key.isNotBlank()) {
                secureStorage.saveApiKey(key)
                SecurityAudit.apiKeySet(this)
            }
        }

        findViewById<Button>(R.id.btn_grant_overlay).setOnClickListener {
            startActivity(Intent(Settings.ACTION_MANAGE_OVERLAY_PERMISSION,
                Uri.parse("package:$packageName")))
        }

        findViewById<Button>(R.id.btn_grant_accessibility).setOnClickListener {
            startActivity(Intent(Settings.ACTION_ACCESSIBILITY_SETTINGS))
        }

        findViewById<Button>(R.id.btn_start).setOnClickListener {
            val intent = Intent(this, VoiceRecordingService::class.java)
            intent.action = VoiceRecordingService.ACTION_START
            startForegroundService(intent)
        }

        updatePermissionStatus()
    }

    override fun onResume() {
        super.onResume()
        updatePermissionStatus()
    }

    private fun updatePermissionStatus() {
        val overlayStatus = findViewById<TextView>(R.id.iv_overlay_status)
        val overlayGranted = Settings.canDrawOverlays(this)
        overlayStatus.text = if (overlayGranted) "✓" else "○"
        overlayStatus.setTextColor(
            if (overlayGranted) getColor(R.color.success_green) else getColor(R.color.text_secondary)
        )

        val accessibilityStatus = findViewById<TextView>(R.id.iv_accessibility_status)
        val am = getSystemService(Context.ACCESSIBILITY_SERVICE) as AccessibilityManager
        val accessibilityEnabled = am.getEnabledAccessibilityServiceList(
            AccessibilityServiceInfo.FEEDBACK_ALL_MASK
        ).any { it.resolveInfo.serviceInfo.packageName == packageName }
        accessibilityStatus.text = if (accessibilityEnabled) "✓" else "○"
        accessibilityStatus.setTextColor(
            if (accessibilityEnabled) getColor(R.color.success_green) else getColor(R.color.text_secondary)
        )
    }
}
