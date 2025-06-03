"use client"

import { createContext, useContext, useEffect, useState } from "react"

type Theme = "dark" | "light" | "system"

type ThemeProviderProps = {
  children: React.ReactNode
  defaultTheme?: Theme
  storageKey?: string
}

type ThemeProviderState = {
  theme: Theme
  setTheme: (theme: Theme) => void
  resolvedTheme: "dark" | "light"
}

const initialState: ThemeProviderState = {
  theme: "system",
  setTheme: () => null,
  resolvedTheme: "light",
}

const ThemeProviderContext = createContext<ThemeProviderState>(initialState)

export function ThemeProvider({
  children,
  defaultTheme = "system",
  storageKey = "salesoptimizer-ui-theme",
  ...props
}: ThemeProviderProps) {
  // Initialize with defaultTheme to avoid SSR issues
  const [theme, setTheme] = useState<Theme>(defaultTheme)
  const [resolvedTheme, setResolvedTheme] = useState<"dark" | "light">("light")
  const [mounted, setMounted] = useState(false)

  // Handle client-side hydration
  useEffect(() => {
    setMounted(true)
    
    // Only access localStorage after mounting (client-side)
    const storedTheme = localStorage?.getItem(storageKey) as Theme
    if (storedTheme) {
      setTheme(storedTheme)
    }
  }, [storageKey])

  useEffect(() => {
    if (!mounted) return

    const root = window.document.documentElement
    const body = window.document.body
    
    // Remove all theme classes
    root.classList.remove("light", "dark")
    body.classList.remove("light", "dark")

    let systemTheme: "dark" | "light" = "light"
    
    if (theme === "system") {
      systemTheme = window.matchMedia("(prefers-color-scheme: dark)").matches
        ? "dark"
        : "light"
    }

    const resolvedTheme = theme === "system" ? systemTheme : theme
    setResolvedTheme(resolvedTheme)
    
    // Apply theme classes to both html and body
    root.classList.add(resolvedTheme)
    body.classList.add(resolvedTheme)
    
    // Force update of CSS custom properties
    root.style.colorScheme = resolvedTheme
  }, [theme, mounted])

  // Listen for system theme changes
  useEffect(() => {
    if (!mounted) return

    const mediaQuery = window.matchMedia("(prefers-color-scheme: dark)")
    
    const handleChange = () => {
      if (theme === "system") {
        const systemTheme = mediaQuery.matches ? "dark" : "light"
        setResolvedTheme(systemTheme)
        const root = window.document.documentElement
        const body = window.document.body
        
        root.classList.remove("light", "dark")
        body.classList.remove("light", "dark")
        root.classList.add(systemTheme)
        body.classList.add(systemTheme)
        root.style.colorScheme = systemTheme
      }
    }

    mediaQuery.addEventListener("change", handleChange)
    return () => mediaQuery.removeEventListener("change", handleChange)
  }, [theme, mounted])

  const value = {
    theme,
    setTheme: (theme: Theme) => {
      if (mounted) {
        localStorage?.setItem(storageKey, theme)
      }
      setTheme(theme)
    },
    resolvedTheme,
  }

  // Don't render theme-dependent content until mounted
  if (!mounted) {
    return (
      <ThemeProviderContext.Provider {...props} value={initialState}>
        {children}
      </ThemeProviderContext.Provider>
    )
  }

  return (
    <ThemeProviderContext.Provider {...props} value={value}>
      {children}
    </ThemeProviderContext.Provider>
  )
}

export const useTheme = () => {
  const context = useContext(ThemeProviderContext)

  if (context === undefined)
    throw new Error("useTheme must be used within a ThemeProvider")

  return context
}