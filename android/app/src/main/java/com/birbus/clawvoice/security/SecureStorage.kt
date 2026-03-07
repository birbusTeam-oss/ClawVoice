package com.birbus.clawvoice.security

import android.content.Context
import androidx.security.crypto.EncryptedSharedPreferences
import androidx.security.crypto.MasterKey

/**
 * SecureStorage — Hardware-backed encrypted storage for API keys.
 * Uses Android Keystore (hardware security module on modern devices).
 * API key is NEVER stored in plain text. Ever.
 */
class SecureStorage(context: Context) {

    private val masterKey = MasterKey.Builder(context)
        .setKeyScheme(MasterKey.KeyScheme.AES256_GCM)
        .setUserAuthenticationRequired(false) // don't require biometric per-access
        .build()

    private val prefs = EncryptedSharedPreferences.create(
        context,
        "clawvoice_secure_prefs",
        masterKey,
        EncryptedSharedPreferences.PrefKeyEncryptionScheme.AES256_SIV,
        EncryptedSharedPreferences.PrefValueEncryptionScheme.AES256_GCM
    )

    fun saveApiKey(key: String) {
        // Trim whitespace — common paste mistake
        prefs.edit().putString(KEY_ANTHROPIC, key.trim()).apply()
    }

    fun getApiKey(): String? {
        return prefs.getString(KEY_ANTHROPIC, null)?.takeIf { it.isNotBlank() }
    }

    fun hasApiKey(): Boolean = getApiKey() != null

    fun clearApiKey() {
        prefs.edit().remove(KEY_ANTHROPIC).apply()
    }

    fun saveWhisperApiKey(key: String) {
        prefs.edit().putString(KEY_WHISPER, key.trim()).apply()
    }

    fun getWhisperApiKey(): String? {
        return prefs.getString(KEY_WHISPER, null)?.takeIf { it.isNotBlank() }
    }

    companion object {
        private const val KEY_ANTHROPIC = "anthropic_api_key"
        private const val KEY_WHISPER = "whisper_api_key"
    }
}
