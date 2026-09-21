import { createContext, useContext } from 'react'

export type Theme = 'light' | 'dark' | 'neon' | 'deep-space' | 'minimal'

export interface ThemeContextType {
  theme: Theme
  setTheme: (theme: Theme) => void
  themes: Theme[]
}

export const ThemeContext = createContext<ThemeContextType | undefined>(undefined)

export const useTheme = () => {
  const context = useContext(ThemeContext)
  if (!context) {
    throw new Error('useTheme must be used within a ThemeProvider')
  }
  return context
}

export const themes: Theme[] = ['light', 'dark', 'neon', 'deep-space', 'minimal']

export const themeLabels: Record<Theme, string> = {
  light: 'Clean',
  dark: 'Dark', 
  neon: 'Neon',
  'deep-space': 'Deep Space',
  minimal: 'Minimal'
}