package com.birbus.clawvoice

import android.app.*
import android.content.Context
import android.content.Intent
import android.media.MediaRecorder
import android.os.IBinder
import androidx.core.app.NotificationCompat
import com.birbus.clawvoice.security.SecureStorage
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.SupervisorJob
import kotlinx.coroutines.launch
import java.io.File

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
        startForeground(NOTIF_ID, buildNotification("🎙️ Recording..."))

        val outputFile = getOutputFile()
        recorder = MediaRecorder(this).apply {
            setAudioSource(MediaRecorder.AudioSource.MIC)
            setOutputFormat(MediaRecorder.OutputFormat.MPEG_4)
            setAudioEncoder(MediaRecorder.AudioEncoder.AAC)
            setAudioSamplingRate(16000)
            setAudioEncodingBitRate(128000)
            setOutputFile(outputFile.absolutePath)
            prepare()
            start()
        }
        isRecording = true
    }

    private fun stopRecordingAndTranscribe() {
        if (!isRecording) return
        try { recorder?.apply { stop(); release() } } catch (e: Exception) {}
        recorder = null
        isRecording = false

        val outputFile = getOutputFile()
        val apiKey = SecureStorage(this).getApiKey() ?: ""

        scope.launch {
            updateNotification("⏳ Transcribing with Claude...")

            if (apiKey.isBlank()) {
                updateNotification("❌ No API key — open ClawVoice to add your Anthropic key")
                return@launch
            }

            val client = ClaudeApiClient(apiKey)
            val result = client.transcribeAudio(outputFile)

            result.onSuccess { text ->
                val injected = TextInjectionService.injectText(text)
                updateNotification(
                    if (injected) "✅ Done! Tap mic to record again"
                    else "⚠️ Transcribed but couldn't inject — is accessibility enabled?"
                )
            }
            result.onFailure {
                updateNotification("❌ Failed: ${it.message}")
            }

            outputFile.delete()
        }
    }

    private fun getOutputFile() = File(cacheDir, "clawvoice_recording.m4a")

    private fun createNotificationChannel() {
        val channel = NotificationChannel(CHANNEL_ID, "ClawVoice Recording",
            NotificationManager.IMPORTANCE_LOW).apply { description = "Recording status" }
        getSystemService(NotificationManager::class.java).createNotificationChannel(channel)
    }

    private fun buildNotification(text: String): Notification {
        val stopIntent = PendingIntent.getService(this, 0,
            Intent(this, VoiceRecordingService::class.java).apply { action = ACTION_STOP },
            PendingIntent.FLAG_UPDATE_CURRENT or PendingIntent.FLAG_IMMUTABLE)

        return NotificationCompat.Builder(this, CHANNEL_ID)
            .setContentTitle("ClawVoice")
            .setContentText(text)
            .setSmallIcon(android.R.drawable.ic_btn_speak_now)
            .addAction(android.R.drawable.ic_media_pause, "Stop", stopIntent)
            .setOngoing(true)
            .build()
    }

    private fun updateNotification(text: String) {
        getSystemService(NotificationManager::class.java).notify(NOTIF_ID, buildNotification(text))
    }

    override fun onDestroy() {
        super.onDestroy()
        job.cancel()
        recorder?.release()
        recorder = null
    }

    override fun onBind(intent: Intent?): IBinder? = null
}
