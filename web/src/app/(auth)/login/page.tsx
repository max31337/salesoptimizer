import { LoginForm } from "@/components/forms/login-form"
import { ThemeToggle } from "@/components/ui/theme-toggle"

export default function LoginPage() {
  return (
    <div className="min-h-screen flex items-center justify-center bg-background py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-md w-full space-y-8">
        <div className="text-center">
          <div className="absolute top-4 right-4">
            <ThemeToggle />
          </div>
          <h2 className="mt-6 text-3xl font-extrabold text-foreground">
            SalesOptimizer
          </h2>
          <p className="mt-2 text-sm text-muted-foreground">
            Sign in to your account
          </p>
        </div>
        <LoginForm />
      </div>
    </div>
  )
}