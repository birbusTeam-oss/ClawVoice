package com.birbus.clawvoice

import android.accessibilityservice.AccessibilityService
import android.os.Bundle
import android.view.accessibility.AccessibilityEvent
import android.view.accessibility.AccessibilityNodeInfo

/**
 * ClawVoice Text Injection Service
 * Uses Android AccessibilityService to inject transcribed text
 * into whatever input field is currently focused — in ANY app.
 */
class TextInjectionService : AccessibilityService() {

    companion object {
        var instance: TextInjectionService? = null

        fun injectText(text: String): Boolean {
            return instance?.performInjection(text) ?: false
        }

        fun isConnected(): Boolean = instance != null
    }

    override fun onServiceConnected() {
        super.onServiceConnected()
        instance = this
    }

    override fun onDestroy() {
        super.onDestroy()
        instance = null
    }

    fun performInjection(text: String): Boolean {
        val root = rootInActiveWindow ?: return false
        val focused = findFocusedInput(root) ?: return false

        // Get current text and append with a space
        val currentText = focused.text?.toString() ?: ""
        val newText = if (currentText.isEmpty()) text else "$currentText $text"

        val args = Bundle()
        args.putCharSequence(
            AccessibilityNodeInfo.ACTION_ARGUMENT_SET_TEXT_CHARSEQUENCE,
            newText
        )

        val success = focused.performAction(AccessibilityNodeInfo.ACTION_SET_TEXT, args)

        // Move cursor to end
        if (success) {
            val moveArgs = Bundle()
            moveArgs.putInt(
                AccessibilityNodeInfo.ACTION_ARGUMENT_MOVEMENT_GRANULARITY_INT,
                AccessibilityNodeInfo.MOVEMENT_GRANULARITY_PAGE
            )
            focused.performAction(AccessibilityNodeInfo.ACTION_NEXT_AT_MOVEMENT_GRANULARITY, moveArgs)
        }

        return success
    }

    private fun findFocusedInput(node: AccessibilityNodeInfo): AccessibilityNodeInfo? {
        if (node.isFocused && node.isEditable) return node
        for (i in 0 until node.childCount) {
            val child = node.getChild(i) ?: continue
            val found = findFocusedInput(child)
            if (found != null) return found
        }
        return null
    }

    override fun onAccessibilityEvent(event: AccessibilityEvent?) {}
    override fun onInterrupt() {}
}
