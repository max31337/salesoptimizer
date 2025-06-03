import './globals.css'
import { Inter } from 'next/font/google'
import { AuthProvider } from '@/features/auth/hooks/useAuth'
import { ThemeProvider } from '@/contexts/theme-context'

const inter = Inter({ subsets: ['latin'] })

export const metadata = {
  title: 'SalesOptimizer',
  description: 'Sales optimization and CRM platform',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body className={inter.className}>
        <ThemeProvider
          defaultTheme="system"
          storageKey="salesoptimizer-ui-theme"
        >
          <AuthProvider>
            {children}
          </AuthProvider>
        </ThemeProvider>
      </body>
    </html>
  )
}