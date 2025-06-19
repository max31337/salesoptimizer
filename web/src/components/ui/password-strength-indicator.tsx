"use client"

import { useMemo } from "react"
import { Badge } from "@/components/ui/badge"
import { Progress } from "@/components/ui/progress"
import { cn } from "@/lib/utils"

type PasswordStrength = 'weak' | 'medium' | 'strong' | 'very_strong'

interface PasswordStrengthInfo {
  strength: PasswordStrength
  score: number
  feedback: {
    suggestions: string[]
    warnings: string[]
  }
}

interface PasswordStrengthIndicatorProps {
  password: string
  className?: string
  showLabel?: boolean
  showProgress?: boolean
  showFeedback?: boolean
}

// Password strength calculation logic (matches backend domain value object)
function calculatePasswordStrength(password: string): PasswordStrengthInfo {
  if (!password) {
    return {
      strength: 'weak',
      score: 0,
      feedback: { suggestions: ['Enter a password'], warnings: [] }
    }
  }

  // Password must be at least 8 characters (backend validation)
  if (password.length < 8) {
    return {
      strength: 'weak',
      score: 0,
      feedback: { 
        suggestions: ['Password must be at least 8 characters long'], 
        warnings: [] 
      }
    }
  }

  let score = 0
  const suggestions: string[] = []
  const warnings: string[] = []

  // Length scoring (matches backend exactly)
  if (password.length >= 8) score += 1
  if (password.length >= 12) score += 1
  if (password.length >= 16) score += 1

  // Character variety scoring (matches backend exactly)
  const hasLowercase = /[a-z]/.test(password)
  const hasUppercase = /[A-Z]/.test(password)
  const hasDigits = /\d/.test(password)
  const hasSpecialChars = /[!@#$%^&*()_+\-=\[\]{};':"\\|,.<>\/?]/.test(password)

  if (hasLowercase) score += 1
  if (hasUppercase) score += 1
  if (hasDigits) score += 1
  if (hasSpecialChars) score += 1

  // Additional complexity checks (matches backend exactly)
  const hasNoCommonPatterns = _hasNoCommonPatterns(password)
  const hasGoodEntropy = _hasGoodEntropy(password)

  if (hasNoCommonPatterns) score += 1
  if (hasGoodEntropy) score += 1

  // Generate feedback (matches backend suggestions)
  if (password.length < 12) {
    suggestions.push("Use at least 12 characters for better security")
  }

  if (!hasLowercase) suggestions.push("Add lowercase letters")
  if (!hasUppercase) suggestions.push("Add uppercase letters")
  if (!hasDigits) suggestions.push("Add numbers")
  if (!hasSpecialChars) suggestions.push("Add special characters (!@#$%^&*)")

  if (!hasNoCommonPatterns) {
    warnings.push("Avoid common patterns like '123', 'abc', or repeated characters")
  }

  if (/(.)\1{2,}/.test(password)) {
    warnings.push("Avoid repeating the same character multiple times")
  }

  // Determine strength based on score (matches backend exactly)
  let strength: PasswordStrength = 'weak'
  if (score >= 7) {
    strength = 'very_strong'
  } else if (score >= 5) {
    strength = 'strong'
  } else if (score >= 3) {
    strength = 'medium'
  }

  return { strength, score, feedback: { suggestions, warnings } }
}

// Helper function to check for common patterns (matches backend)
function _hasNoCommonPatterns(password: string): boolean {
  const passwordLower = password.toLowerCase()
  
  // Common weak patterns (matches backend exactly)
  const weakPatterns = [
    /123/, /abc/, /qwerty/, /password/, /admin/,
    /000/, /111/, /999/, /aaa/, /zzz/
  ]
  
  for (const pattern of weakPatterns) {
    if (pattern.test(passwordLower)) {
      return false
    }
  }
  
  // Check for repeated characters (more than 2 in a row)
  if (/(.)\1{2,}/.test(password)) {
    return false
  }
  
  return true
}

// Helper function to check for good entropy (matches backend)
function _hasGoodEntropy(password: string): boolean {
  // Check for character variety within the password
  let charTypes = 0
  
  if (/[a-z]/.test(password)) charTypes += 1
  if (/[A-Z]/.test(password)) charTypes += 1
  if (/\d/.test(password)) charTypes += 1
  if (/[^a-zA-Z\d]/.test(password)) charTypes += 1
  
  // Good entropy requires at least 3 character types and length > 10 (matches backend)
  return charTypes >= 3 && password.length > 10
}

function getStrengthInfo(strength: PasswordStrength) {
  switch (strength) {
    case 'weak':
      return {
        label: 'Weak',
        variant: 'destructive' as const,
        color: 'bg-red-500',
        textColor: 'text-red-600',
        progress: 25
      }
    case 'medium':
      return {
        label: 'Medium',
        variant: 'secondary' as const,
        color: 'bg-yellow-500',
        textColor: 'text-yellow-600',
        progress: 50
      }
    case 'strong':
      return {
        label: 'Strong',
        variant: 'outline' as const,
        color: 'bg-green-500',
        textColor: 'text-green-600',
        progress: 75
      }
    case 'very_strong':
      return {
        label: 'Very Strong',
        variant: 'default' as const,
        color: 'bg-green-700',
        textColor: 'text-green-700',
        progress: 100
      }
    default:
      return {
        label: 'Unknown',
        variant: 'outline' as const,
        color: 'bg-gray-500',
        textColor: 'text-gray-600',
        progress: 0
      }
  }
}

export function PasswordStrengthIndicator({
  password,
  className,
  showLabel = true,
  showProgress = true,
  showFeedback = true
}: PasswordStrengthIndicatorProps) {
  const passwordInfo = useMemo(() => calculatePasswordStrength(password), [password])
  const strengthInfo = getStrengthInfo(passwordInfo.strength)

  if (!password) {
    return null
  }

  return (
    <div className={cn("space-y-2", className)}>
      {/* Label and Progress */}
      <div className="flex items-center gap-2">
        {showLabel && (
          <Badge variant={strengthInfo.variant} className="text-xs">
            {strengthInfo.label}
          </Badge>
        )}        {showProgress && (
          <div className="flex-1">
            <Progress 
              value={strengthInfo.progress} 
              className="h-2"
              color={strengthInfo.color}
            />
          </div>
        )}
      </div>

      {/* Feedback */}
      {showFeedback && (passwordInfo.feedback.suggestions.length > 0 || passwordInfo.feedback.warnings.length > 0) && (
        <div className="space-y-1">
          {passwordInfo.feedback.suggestions.length > 0 && (
            <div className="text-xs text-muted-foreground">
              <span className="font-medium">Suggestions: </span>
              {passwordInfo.feedback.suggestions.join(', ')}
            </div>
          )}
          {passwordInfo.feedback.warnings.length > 0 && (
            <div className="text-xs text-amber-600 dark:text-amber-400">
              <span className="font-medium">Warnings: </span>
              {passwordInfo.feedback.warnings.join(', ')}
            </div>
          )}
        </div>
      )}
    </div>
  )
}

export { calculatePasswordStrength, getStrengthInfo }
export type { PasswordStrength, PasswordStrengthInfo }
