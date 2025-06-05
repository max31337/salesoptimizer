"use client"

import { useState } from "react"
import { useRouter } from "next/navigation"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Alert, AlertDescription } from "@/components/ui/alert"
import { useAuth } from "@/features/auth/hooks/useAuth"

export function LoginForm() {
  const [emailOrUsername, setEmailOrUsername] = useState("")
  const [password, setPassword] = useState("")
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState("")
  const { login } = useAuth()
  const router = useRouter()

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setIsLoading(true)
    setError("")

    try {
      const result = await login({ emailOrUsername, password })
      
      // Redirect based on user role
      if (result.user.role === "super_admin") {
        router.push("/admin")
      } else if (result.user.role === "org_admin") {
        router.push("/dashboard")
      } else {
        router.push("/dashboard")
      }
    } catch (err: any) {
      console.error("Login failed:", err)
      setError(err.message || "Login failed. Please check your credentials.")
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <Card className="w-full max-w-md border border-border shadow-lg bg-card">
      <CardHeader className="space-y-1">
        <CardTitle className="text-2xl font-bold text-card-foreground">Sign In</CardTitle>
        <CardDescription className="text-muted-foreground">
          Enter your credentials to access your account
        </CardDescription>
      </CardHeader>
      <CardContent>
        <form onSubmit={handleSubmit} className="space-y-4">
          {error && (
            <Alert variant="destructive" className="border-destructive/50 text-destructive dark:border-destructive [&>svg]:text-destructive">
              <AlertDescription>{error}</AlertDescription>
            </Alert>
          )}
          
          <div className="space-y-2">
            <Label htmlFor="emailOrUsername" className="text-sm font-medium text-card-foreground">
              Email or Username
            </Label>
            <Input
              id="emailOrUsername"
              type="text"
              placeholder="Enter your email or username"
              value={emailOrUsername}
              onChange={(e) => setEmailOrUsername(e.target.value)}
              required
              disabled={isLoading}
              className="bg-background border-border text-foreground placeholder:text-muted-foreground focus:border-primary focus:ring-primary"
            />
          </div>
          
          <div className="space-y-2">
            <Label htmlFor="password" className="text-sm font-medium text-card-foreground">
              Password
            </Label>
            <Input
              id="password"
              type="password"
              placeholder="Enter your password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              disabled={isLoading}
              className="bg-background border-border text-foreground placeholder:text-muted-foreground focus:border-primary focus:ring-primary"
            />
          </div>
          
          <Button 
            type="submit" 
            className="w-full bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-white font-semibold shadow-lg hover:shadow-xl transition-all duration-200" 
            disabled={isLoading}
          >
            {isLoading ? "Signing in..." : "Sign In"}
          </Button>
        </form>
        
        <div className="mt-6 text-center space-y-2">
          <p className="text-sm text-muted-foreground">
            Forgot your password?{" "}
            <a 
              href="/reset-password" 
              className="text-primary hover:text-primary/80 font-medium hover:underline transition-colors"
            >
              Reset it
            </a>
          </p>
          <p className="text-xs text-muted-foreground">
            Don't have an account? Contact your administrator for access.
          </p>
        </div>
      </CardContent>
    </Card>
  )
}