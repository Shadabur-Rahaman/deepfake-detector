import { Button } from "@/components/ui/button"
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"
import { useTheme, themeLabels } from "@/lib/theme"
import { Palette, Sun, Moon, Zap, Minus, Stars } from "lucide-react"

const themeIcons = {
  light: Sun,
  dark: Moon, 
  neon: Zap,
  'deep-space': Stars,
  minimal: Minus
}

export function ThemeToggle() {
  try {
    const { theme, setTheme, themes } = useTheme()
    const CurrentIcon = themeIcons[theme as keyof typeof themeIcons] || Sun

    return (
      <DropdownMenu>
        <DropdownMenuTrigger asChild>
          <Button variant="ghost" size="sm" className="w-9 px-0">
            {CurrentIcon && <CurrentIcon className="h-[1.2rem] w-[1.2rem]" />}
            <span className="sr-only">Toggle theme</span>
          </Button>
        </DropdownMenuTrigger>
        <DropdownMenuContent align="end">
          {themes.map((t) => {
            const Icon = themeIcons[t as keyof typeof themeIcons] || Sun
            return (
              <DropdownMenuItem
                key={t}
                onClick={() => setTheme(t)}
                className={theme === t ? "bg-accent" : ""}
              >
                {Icon && <Icon className="mr-2 h-4 w-4" />}
                {themeLabels[t]}
              </DropdownMenuItem>
            )
          })}
        </DropdownMenuContent>
      </DropdownMenu>
    )
  } catch (error) {
    console.error('ThemeToggle error:', error)
    return (
      <Button variant="ghost" size="sm" className="w-9 px-0">
        <Sun className="h-[1.2rem] w-[1.2rem]" />
        <span className="sr-only">Toggle theme</span>
      </Button>
    )
  }
}

export default ThemeToggle