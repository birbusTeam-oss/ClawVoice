package com.birbus.clawvoice.security

import android.content.Context
import android.util.Log

/**
 * Local-only security audit log.
 * Records key events for debugging WITHOUT logging sensitive data.
 * Never transmitted anywhere.
 */
object SecurityAudit {
    private const val TAG = "ClawVoice_Security"

    fun apiKeySet(context: Context) {
        Log.i(TAG, "API key configured [key hidden]")
    }

    fun transcriptionStarted() {
        Log.i(TAG, "Transcription started")
    }

    fun transcriptionComplete(charCount: Int) {
        Log.i(TAG, "Transcription complete: $charCount chars")
    }

    fun apiCallMade(endpoint: String) {
        // Log endpoint but NEVER log the key or response content
        Log.i(TAG, "API call: $endpoint")
    }

    fun textInjected(charCount: Int) {
        Log.i(TAG, "Text injected: $charCount chars")
    }

    fun suspiciousActivity(reason: String) {
        Log.w(TAG, "Security notice: $reason")
    }
}
