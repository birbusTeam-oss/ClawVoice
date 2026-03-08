package com.birbus.clawvoice

import android.util.Base64
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import okhttp3.MediaType.Companion.toMediaType
import okhttp3.OkHttpClient
import okhttp3.Request
import okhttp3.RequestBody.Companion.toRequestBody
import org.json.JSONArray
import org.json.JSONObject
import java.io.File
import java.util.concurrent.TimeUnit

/**
 * ClawVoice — Claude-only API Client
 * Sends audio directly to Claude for transcription + cleanup.
 * ONE API key. Zero dependencies on other providers.
 */
class ClaudeApiClient(private val apiKey: String) {

    private val client = OkHttpClient.Builder()
        .connectTimeout(30, TimeUnit.SECONDS)
        .readTimeout(60, TimeUnit.SECONDS)
        .certificatePinner(
            okhttp3.CertificatePinner.Builder()
                .add("api.anthropic.com", "sha256/r/mIkG3eEpVdm+u/ko/cwxzOMo1bk4TyHIlByibiA5I=")
                .add("api.anthropic.com", "sha256/Y9mvm0exBk1JoQ57f9Vm28jKo5lFm/woKcVxrYxu80o=")
                .build()
        )
        .build()

    /**
     * Transcribe audio file using Claude directly.
     * Claude handles both transcription AND cleanup in one call.
     */
    suspend fun transcribeAudio(audioFile: File): Result<String> = withContext(Dispatchers.IO) {
        try {
            // Encode audio as base64
            val audioBytes = audioFile.readBytes()
            val audioBase64 = Base64.encodeToString(audioBytes, Base64.NO_WRAP)

            val requestBody = JSONObject().apply {
                put("model", "claude-haiku-4-5")
                put("max_tokens", 1024)
                put("messages", JSONArray().apply {
                    put(JSONObject().apply {
                        put("role", "user")
                        put("content", JSONArray().apply {
                            put(JSONObject().apply {
                                put("type", "text")
                                put("text", "Transcribe this audio accurately. Fix punctuation and grammar. Remove filler words like uh, um, like. Return ONLY the transcribed text, nothing else.")
                            })
                            put(JSONObject().apply {
                                put("type", "document")
                                put("source", JSONObject().apply {
                                    put("type", "base64")
                                    put("media_type", "audio/wav")
                                    put("data", audioBase64)
                                })
                            })
                        })
                    })
                })
            }.toString()

            val request = Request.Builder()
                .url("https://api.anthropic.com/v1/messages")
                .addHeader("x-api-key", apiKey)
                .addHeader("anthropic-version", "2023-06-01")
                .addHeader("content-type", "application/json")
                .post(requestBody.toRequestBody("application/json".toMediaType()))
                .build()

            val response = client.newCall(request).execute()
            val body = response.body?.string() ?: return@withContext Result.failure(Exception("Empty response"))
            val parsed = JSONObject(body)

            if (parsed.has("error")) {
                val error = parsed.getJSONObject("error").getString("message")
                return@withContext Result.failure(Exception(error))
            }

            val text = parsed.getJSONArray("content")
                .getJSONObject(0)
                .getString("text")
                .trim()

            Result.success(text)
        } catch (e: Exception) {
            Result.failure(e)
        }
    }
}
