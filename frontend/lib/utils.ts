import { clsx, type ClassValue } from "clsx"
import { twMerge } from "tailwind-merge"

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

/**
 * Converts ISO 8601 timestamp to human-readable format
 * Returns relative time for recent messages, formatted date for older ones
 */
export function formatTimestamp(created_at: string): string {
  const date = new Date(created_at)
  const now = new Date()
  const diffMs = now.getTime() - date.getTime()
  const diffMinutes = Math.floor(diffMs / 60000)
  const diffHours = Math.floor(diffMs / 3600000)
  const diffDays = Math.floor(diffMs / 86400000)

  // Relative time for messages less than 1 day old
  if (diffDays < 1) {
    if (diffMinutes < 1) return "Just now"
    if (diffMinutes < 60) return `${diffMinutes} minute${diffMinutes === 1 ? "" : "s"} ago`
    return `${diffHours} hour${diffHours === 1 ? "" : "s"} ago`
  }

  // Formatted date for older messages
  const months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
  const month = months[date.getMonth()]
  const day = date.getDate()
  const hours = date.getHours()
  const minutes = date.getMinutes()
  const ampm = hours >= 12 ? "PM" : "AM"
  const displayHours = hours % 12 || 12
  const displayMinutes = minutes.toString().padStart(2, "0")

  return `${month} ${day}, ${displayHours}:${displayMinutes} ${ampm}`
}

/**
 * Converts byte count to human-readable file size
 */
export function formatFileSize(bytes: number): string {
  if (bytes === 0) return "0 B"

  const units = ["B", "KB", "MB", "GB", "TB"]
  const k = 1024
  const i = Math.floor(Math.log(bytes) / Math.log(k))

  if (i === 0) return `${bytes} B`

  return `${(bytes / Math.pow(k, i)).toFixed(2)} ${units[i]}`
}

/**
 * Extracts file extension from filename (without the dot, lowercase)
 */
export function getFileExtension(filename: string): string {
  const lastDotIndex = filename.lastIndexOf(".")
  if (lastDotIndex === -1 || lastDotIndex === filename.length - 1) {
    return ""
  }
  return filename.slice(lastDotIndex + 1).toLowerCase()
}

/**
 * Validates file MIME type against allowed types
 */
export function isValidFileType(file: File, acceptedTypes: Record<string, string[]>): boolean {
  return file.type in acceptedTypes
}

/**
 * Validates file size against maximum limit
 */
export function isValidFileSize(file: File, maxSizeBytes: number): boolean {
  return file.size <= maxSizeBytes
}

/**
 * SSR-safe check if code is running in browser environment
 */
export function isBrowser(): boolean {
  return typeof window !== "undefined"
}

/**
 * Generates a temporary ID for optimistic updates
 * Uses timestamp + random number to ensure uniqueness
 */
export function generateTempId(): string {
  return `temp_${Date.now()}_${Math.random().toString(36).substring(2, 9)}`
}

/**
 * Generates a conversation title from the first message
 * Truncates to 50 characters and adds ellipsis if needed
 */
export function generateConversationTitle(message: string): string {
  const trimmed = message.trim()
  const maxLength = 50

  if (trimmed.length <= maxLength) {
    return trimmed
  }

  // Find the last space before maxLength to avoid cutting words
  const truncated = trimmed.substring(0, maxLength)
  const lastSpace = truncated.lastIndexOf(" ")

  if (lastSpace > 0) {
    return truncated.substring(0, lastSpace) + "..."
  }

  return truncated + "..."
}
