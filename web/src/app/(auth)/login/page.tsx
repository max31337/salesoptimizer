import { LoginForm } from "@/components/forms/login-form"
import { ThemeToggle } from "@/components/ui/theme-toggle"
import Link from "next/link"
import { Zap, ArrowLeft } from "lucide-react"

export default function LoginPage() {
  return (
    <div className="min-h-screen flex items-center justify-center py-12 px-4 sm:px-6 lg:px-8 relative w-full">
      {/* Background decoration */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-blue-200 dark:bg-blue-800/20 rounded-full mix-blend-multiply dark:mix-blend-soft-light filter blur-xl opacity-20 animate-pulse"></div>
        <div className="absolute top-3/4 right-1/4 w-96 h-96 bg-purple-200 dark:bg-purple-800/20 rounded-full mix-blend-multiply dark:mix-blend-soft-light filter blur-xl opacity-20 animate-pulse animation-delay-2000"></div>
      </div>
      
      {/* Back to Home Link */}
      <div className="absolute top-4 left-4 z-50">
        <Link 
          href="/" 
          className="inline-flex items-center px-3 py-2 text-sm font-medium text-muted-foreground hover:text-foreground bg-background/80 backdrop-blur-sm rounded-md border border-border hover:bg-accent transition-all duration-200"
        >
          <ArrowLeft className="mr-2 h-4 w-4" />
          Back to Home
        </Link>
      </div>
      
      <div className="absolute top-4 right-4 z-50">
        <ThemeToggle />
      </div>
      
      <div className="max-w-md w-full space-y-8 relative z-10">
        <div className="text-center">
          {/* Clickable SalesOptimizer Banner */}
          <Link 
            href="/" 
            className="inline-block group mb-6 transition-all duration-200 hover:scale-105"
          >
            <div className="flex items-center justify-center space-x-3 mb-4">
              <div className="w-12 h-12 bg-gradient-to-r from-blue-600 to-purple-600 rounded-lg flex items-center justify-center shadow-lg group-hover:shadow-xl transition-shadow duration-200">
                <Zap className="h-7 w-7 text-white" />
              </div>
              <h1 className="text-3xl font-bold text-foreground group-hover:text-transparent group-hover:bg-clip-text group-hover:bg-gradient-to-r group-hover:from-blue-600 group-hover:to-purple-600 transition-all duration-200">
                SalesOptimizer
              </h1>
            </div>
          </Link>
          
          <p className="text-lg text-muted-foreground">
            Welcome back! Sign in to your account
          </p>
        </div>
        <LoginForm />
      </div>
    </div>
  )
}