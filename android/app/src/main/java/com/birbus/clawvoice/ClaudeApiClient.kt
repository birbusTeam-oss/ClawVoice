package com.birbus.clawvoice

import com.birbus.clawvoice.security.SecurityAudit
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import okhttp3.CertificatePinner
import okhttp3.MediaType.Companion.toMediaType
import okhttp3.MultipartBody
import okhttp3.OkHttpClient
import okhttp3.Request
import okhttp3.RequestBody.Companion.asRequestBody
import org.json.JSONObject
import java.io.File
import java.util.concurrent.TimeUnit

/**
 * ClawVoice — Claude API Client
 * Sends audio to Claude/Whisper for transcription.
 * Users provide their own API key — no backend needed.
 */
class ClaudeApiClient(private val apiKey: String) {

    private val client = OkHttpClient.Builder()
        .connectTimeout(30, TimeUnit.SECONDS)
        .readTimeout(60, TimeUnit.SECONDS)
        .certificatePinner(
            CertificatePinner.Builder()
                // Anthropic API certificate pins (DigiCert)
                .add("api.anthropic.com", "sha256/r/mIkG3eEpVdm+u/ko/cwxzOMo1bk4TyHIlByibiA5I=")
                .add("api.anthropic.com", "sha256/Y9mvm0exBk1JoQ57f9Vm28jKo5lFm/woKcVxrYxu80o=")
                .build()
        )
        .build()

    /**
     * Transcribe audio file.
     * Currently uses OpenAI Whisper API.
     * Will migrate to Claude native audio when available.
     */
    suspend fun transcribeAudio(audioFile: File, whisperApiKey: String = ""): Result<String> =
        withContext(Dispatchers.IO) {
            try {
                SecurityAudit.transcriptionStarted()
                // Phase 1: Whisper API transcription
                if (whisperApiKey.isNotBlank()) {
                    val result = transcribeWithWhisper(audioFile, whisperApiKey)
                    result.onSuccess { SecurityAudit.transcriptionComplete(it.length) }
                    return@withContext result
                }

                // Fallback: placeholder until real transcription is configured
                Result.success("[Transcription placeholder — add Whisper API key in settings]")
            } catch (e: Exception) {
                Result.failure(e)
            }
        }

    /**
     * Transcribe via OpenAI Whisper API.
     */
    private fun transcribeWithWhisper(audioFile: File, whisperApiKey: String): Result<String> {
        SecurityAudit.apiCallMade("openai.com/v1/audio/transcriptions")
        val requestBody = MultipartBody.Builder()
            .setType(MultipartBody.FORM)
            .addFormDataPart(
                "file", audioFile.name,
                audioFile.asRequestBody("audio/m4a".toMediaType())
            )
            .addFormDataPart("model", "whisper-1")
            .build()

        val request = Request.Builder()
            .url("https://api.openai.com/v1/audio/transcriptions")
            .addHeader("Authorization", "Bearer $whisperApiKey")
            .post(requestBody)
            .build()

        val response = client.newCall(request).execute()
        val body = response.body?.string() ?: return Result.failure(Exception("Empty response from Whisper"))

        if (!response.isSuccessful) {
            return Result.failure(Exception("Whisper API error ${response.code}: $body"))
        }

        val text = JSONObject(body).getString("text")
        return Result.success(text.trim())
    }

    /**
     * Send transcribed text to Claude for cleanup.
     * Fixes grammar, punctuation, and formatting while preserving meaning.
     */
    suspend fun cleanupTranscription(rawText: String): Result<String> =
        withContext(Dispatchers.IO) {
            try {
                if (apiKey.isBlank()) return@withContext Result.success(rawText)

                SecurityAudit.apiCallMade("api.anthropic.com/v1/messages")

                val json = JSONObject().apply {
                    put("model", "claude-sonnet-4-6")
                    put("max_tokens", 1024)
                    put("messages", org.json.JSONArray().apply {
                        put(JSONObject().apply {
                            put("role", "user")
                            put(
                                "content",
                                "Clean up this voice transcription for readability. " +
                                "Fix punctuation, capitalization, and grammar but preserve meaning. " +
                                "Return ONLY the cleaned text, nothing else:\n\n$rawText"
                            )
                        })
                    })
                }

                val request = Request.Builder()
                    .url("https://api.anthropic.com/v1/messages")
                    .addHeader("x-api-key", apiKey)
                    .addHeader("anthropic-version", "2023-06-01")
                    .addHeader("content-type", "application/json")
                    .post(
                        okhttp3.RequestBody.create(
                            "application/json".toMediaType(),
                            json.toString()
                        )
                    )
                    .build()

                val response = client.newCall(request).execute()
                val body = response.body?.string()
                    ?: return@withContext Result.failure(Exception("Empty response"))

                if (!response.isSuccessful) {
                    return@withContext Result.failure(Exception("Claude API error ${response.code}: $body"))
                }

                val parsed = JSONObject(body)
                val text = parsed.getJSONArray("content").getJSONObject(0).getString("text")
                Result.success(text.trim())
            } catch (e: Exception) {
                Result.failure(e)
            }
        }
}
