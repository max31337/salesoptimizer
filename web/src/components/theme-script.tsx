"use client"

export function ThemeScript() {
  const script = `
    (function() {
      function getThemePreference() {
        if (typeof localStorage !== 'undefined' && localStorage.getItem('salesoptimizer-ui-theme')) {
          return localStorage.getItem('salesoptimizer-ui-theme')
        }
        return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light'
      }
      
      const theme = getThemePreference()
      const resolvedTheme = theme === 'system' 
        ? (window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light')
        : theme
      
      document.documentElement.classList.remove('light', 'dark')
      document.documentElement.classList.add(resolvedTheme)
      document.documentElement.style.colorScheme = resolvedTheme
      
      if (document.body) {
        document.body.classList.remove('light', 'dark')
        document.body.classList.add(resolvedTheme)
      }
    })()
  `

  return <script dangerouslySetInnerHTML={{ __html: script }} />
}