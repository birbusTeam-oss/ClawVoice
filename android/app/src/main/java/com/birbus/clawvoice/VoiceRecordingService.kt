package com.birbus.clawvoice

import android.app.*
import android.content.Context
import android.content.Intent
import android.media.MediaRecorder
import android.os.IBinder
import androidx.core.app.NotificationCompat
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.SupervisorJob
import kotlinx.coroutines.launch
import java.io.File

/**
 * ClawVoice Recording Service
 * Runs in foreground, captures audio when activated,
 * sends to transcription, injects result into focused field.
 */
class VoiceRecordingService : Service() {

    private var recorder: MediaRecorder? = null
    private var isRecording = false
    private val job = SupervisorJob()
    private val scope = CoroutineScope(Dispatchers.Main + job)

    companion object {
        const val ACTION_START = "com.birbus.clawvoice.START"
        const val ACTION_STOP = "com.birbus.clawvoice.STOP"
        const val CHANNEL_ID = "clawvoice_recording"
        const val NOTIF_ID = 1
    }

    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        when (intent?.action) {
            ACTION_START -> startRecording()
            ACTION_STOP -> stopRecordingAndTranscribe()
        }
        return START_STICKY
    }

    private fun startRecording() {
        if (isRecording) return

        createNotificationChannel()
        startForeground(NOTIF_ID, buildNotification("🎙️ Recording... tap STOP to finish"))

        val outputFile = getOutputFile()
        recorder = MediaRecorder(this).apply {
            setAudioSource(MediaRecorder.AudioSource.MIC)
            setOutputFormat(MediaRecorder.OutputFormat.MPEG_4)
            setAudioEncoder(MediaRecorder.AudioEncoder.AAC)
            setAudioSamplingRate(16000)  // Whisper prefers 16kHz
            setAudioEncodingBitRate(128000)
            setOutputFile(outputFile.absolutePath)
            prepare()
            start()
        }
        isRecording = true
    }

    private fun stopRecordingAndTranscribe() {
        if (!isRecording) return

        try {
            recorder?.apply { stop(); release() }
        } catch (e: Exception) {
            // Recording may have been too short
        }
        recorder = null
        isRecording = false

        val outputFile = getOutputFile()
        val prefs = getSharedPreferences("clawvoice", Context.MODE_PRIVATE)
        val claudeKey = prefs.getString("api_key", "") ?: ""
        val whisperKey = prefs.getString("whisper_api_key", "") ?: ""

        scope.launch {
            updateNotification("⏳ Transcribing...")

            val client = ClaudeApiClient(claudeKey)

            // Step 1: Transcribe
            val transcribeResult = client.transcribeAudio(outputFile, whisperKey)
            transcribeResult.onFailure {
                updateNotification("❌ Transcription failed: ${it.message}")
                return@launch
            }

            val rawText = transcribeResult.getOrThrow()

            // Step 2: Claude cleanup (if API key set)
            val finalText = if (claudeKey.isNotBlank()) {
                val cleanResult = client.cleanupTranscription(rawText)
                cleanResult.getOrElse { rawText }  // Fall back to raw if cleanup fails
            } else {
                rawText
            }

            // Step 3: Inject
            val injected = TextInjectionService.injectText(finalText)
            updateNotification(
                if (injected) "✅ Injected! Tap mic to record again"
                else "⚠️ Transcribed but couldn't inject — is accessibility enabled?"
            )
        }
    }

    private fun getOutputFile() = File(cacheDir, "clawvoice_recording.m4a")

    private fun createNotificationChannel() {
        val channel = NotificationChannel(
            CHANNEL_ID,
            "ClawVoice Recording",
            NotificationManager.IMPORTANCE_LOW
        ).apply {
            description = "Shows recording status"
        }
        getSystemService(NotificationManager::class.java).createNotificationChannel(channel)
    }

    private fun buildNotification(text: String): Notification {
        val stopIntent = Intent(this, VoiceRecordingService::class.java).apply {
            action = ACTION_STOP
        }
        val stopPendingIntent = PendingIntent.getService(
            this, 0, stopIntent, PendingIntent.FLAG_UPDATE_CURRENT or PendingIntent.FLAG_IMMUTABLE
        )

        return NotificationCompat.Builder(this, CHANNEL_ID)
            .setContentTitle("ClawVoice")
            .setContentText(text)
            .setSmallIcon(android.R.drawable.ic_btn_speak_now)
            .addAction(android.R.drawable.ic_media_pause, "Stop", stopPendingIntent)
            .setOngoing(true)
            .build()
    }

    private fun updateNotification(text: String) {
        val notification = buildNotification(text)
        getSystemService(NotificationManager::class.java).notify(NOTIF_ID, notification)
    }

    override fun onDestroy() {
        super.onDestroy()
        job.cancel()
        recorder?.release()
        recorder = null
    }

    override fun onBind(intent: Intent?): IBinder? = null
}
