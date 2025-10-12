import { useState, useEffect, ReactNode } from 'react'
import { ThemeContext, Theme } from '@/lib/theme'

interface ThemeProviderProps {
  children: ReactNode
  defaultTheme?: Theme
  storageKey?: string
}

export function ThemeProvider({
  children,
  defaultTheme = 'dark',
  storageKey = 'ifake-theme'
}: ThemeProviderProps) {
  const [theme, setThemeState] = useState<Theme>(defaultTheme)

  useEffect(() => {
    const stored = localStorage.getItem(storageKey) as Theme
    if (stored && ['light', 'dark', 'neon', 'deep-space', 'minimal'].includes(stored)) {
      setThemeState(stored)
    }
  }, [storageKey])

  useEffect(() => {
    const root = window.document.documentElement
    
    // Remove all theme classes
    root.classList.remove('light', 'dark', 'neon', 'deep-space', 'minimal')
    
    // Add current theme class
    root.classList.add(theme)
    
    // Store in localStorage
    localStorage.setItem(storageKey, theme)
  }, [theme, storageKey])

  const setTheme = (newTheme: Theme) => {
    setThemeState(newTheme)
  }

  const themes: Theme[] = ['light', 'dark', 'neon', 'deep-space', 'minimal']

  return (
    <ThemeContext.Provider value={{ theme, setTheme, themes }}>
      {children}
    </ThemeContext.Provider>
  )
}