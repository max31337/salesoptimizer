import { LoginForm } from "@/components/forms/login-form"
import { ThemeToggle } from "@/components/ui/theme-toggle"

export default function LoginPage() {
  return (
    <div className="min-h-screen flex items-center justify-center py-12 px-4 sm:px-6 lg:px-8 relative w-full">
      {/* Background decoration */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-blue-200 dark:bg-blue-800/20 rounded-full mix-blend-multiply dark:mix-blend-soft-light filter blur-xl opacity-20 animate-pulse"></div>
        <div className="absolute top-3/4 right-1/4 w-96 h-96 bg-purple-200 dark:bg-purple-800/20 rounded-full mix-blend-multiply dark:mix-blend-soft-light filter blur-xl opacity-20 animate-pulse animation-delay-2000"></div>
      </div>
      
      <div className="absolute top-4 right-4 z-50">
        <ThemeToggle />
      </div>
      
      <div className="max-w-md w-full space-y-8 relative z-10">
        <div className="text-center">
          <div className="flex items-center justify-center mb-6">
            <div className="w-16 h-16 bg-gradient-to-r from-blue-600 to-purple-600 rounded-xl flex items-center justify-center shadow-lg">
              <svg
                className="h-10 w-10 text-white"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
                xmlns="http://www.w3.org/2000/svg"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M13 10V3L4 14h7v7l9-11h-7z"
                />
              </svg>
            </div>
          </div>
          <h1 className="text-4xl font-bold text-foreground mb-2">
            SalesOptimizer
          </h1>
          <p className="text-lg text-muted-foreground">
            Welcome back! Sign in to your account
          </p>
        </div>
        <LoginForm />
      </div>
    </div>
  )
}