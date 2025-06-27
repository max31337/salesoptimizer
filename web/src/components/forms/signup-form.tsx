"use client"

import { useState } from "react"
import { useRouter } from "next/navigation"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { PasswordInput } from "@/components/ui/password-input"
import { Label } from "@/components/ui/label"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Alert, AlertDescription } from "@/components/ui/alert"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Separator } from "@/components/ui/separator"
import { authService } from "@/features/auth/services/auth-service"

interface SignupFormData {
  firstName: string
  lastName: string
  email: string
  password: string
  confirmPassword: string
  organizationName: string
  subscriptionTier: 'free' | 'basic' | 'pro'
}

export function SignupForm() {
  const [formData, setFormData] = useState<SignupFormData>({
    firstName: "",
    lastName: "",
    email: "",
    password: "",
    confirmPassword: "",
    organizationName: "",
    subscriptionTier: "free"
  })
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState("")
  const router = useRouter()

  const handleInputChange = (field: keyof SignupFormData, value: string) => {
    setFormData(prev => ({ ...prev, [field]: value }))
    // Clear error when user starts typing
    if (error) setError("")
  }

  const validateForm = () => {
    if (!formData.firstName || !formData.lastName) {
      setError("First name and last name are required")
      return false
    }
    if (!formData.email) {
      setError("Email is required")
      return false
    }
    if (!formData.password) {
      setError("Password is required")
      return false
    }
    if (formData.password !== formData.confirmPassword) {
      setError("Passwords do not match")
      return false
    }
    if (formData.password.length < 8) {
      setError("Password must be at least 8 characters long")
      return false
    }
    if (!formData.organizationName) {
      setError("Organization name is required")
      return false
    }
    return true
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    
    if (!validateForm()) {
      return
    }

    setIsLoading(true)
    setError("")

    try {
      // Call the signup API endpoint
      const response = await authService.signup(formData)
      
      if (response.success) {
        // Redirect to onboarding success or dashboard
        router.push("/auth/signup-success")
      } else {
        setError(response.message || "Signup failed. Please try again.")
      }
    } catch (err: any) {
      console.error("Signup failed:", err)
      setError(err.message || "Signup failed. Please check your information and try again.")
    } finally {
      setIsLoading(false)
    }
  }

  const subscriptionTiers = [
    {
      value: "free",
      label: "Free Trial",
      description: "14 days free, no credit card required"
    },
    {
      value: "basic", 
      label: "Basic Plan",
      description: "$29/month - For small teams"
    },
    {
      value: "pro",
      label: "Pro Plan", 
      description: "$99/month - For growing businesses"
    }
  ]

  return (
    <Card className="w-full border border-border shadow-lg bg-card">
      <CardHeader className="space-y-1">
        <CardTitle className="text-2xl font-bold text-card-foreground">Create Account</CardTitle>
        <CardDescription className="text-muted-foreground">
          Fill in your details to get started with SalesOptimizer
        </CardDescription>
      </CardHeader>
      <CardContent>
        <form onSubmit={handleSubmit} className="space-y-4">
          {error && (
            <Alert variant="destructive" className="border-destructive/50 text-destructive dark:border-destructive [&>svg]:text-destructive">
              <AlertDescription>{error}</AlertDescription>
            </Alert>
          )}

          {/* Personal Information */}
          <div className="space-y-4">
            <h3 className="text-lg font-semibold text-foreground">Personal Information</h3>
            
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="firstName" className="text-sm font-medium text-card-foreground">
                  First Name *
                </Label>
                <Input
                  id="firstName"
                  type="text"
                  placeholder="John"
                  value={formData.firstName}
                  onChange={(e) => handleInputChange("firstName", e.target.value)}
                  required
                  disabled={isLoading}
                  className="bg-background border-border text-foreground placeholder:text-muted-foreground focus:border-primary focus:ring-primary"
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="lastName" className="text-sm font-medium text-card-foreground">
                  Last Name *
                </Label>
                <Input
                  id="lastName"
                  type="text"
                  placeholder="Doe"
                  value={formData.lastName}
                  onChange={(e) => handleInputChange("lastName", e.target.value)}
                  required
                  disabled={isLoading}
                  className="bg-background border-border text-foreground placeholder:text-muted-foreground focus:border-primary focus:ring-primary"
                />
              </div>
            </div>

            <div className="space-y-2">
              <Label htmlFor="email" className="text-sm font-medium text-card-foreground">
                Email Address *
              </Label>
              <Input
                id="email"
                type="email"
                placeholder="john@company.com"
                value={formData.email}
                onChange={(e) => handleInputChange("email", e.target.value)}
                required
                disabled={isLoading}
                className="bg-background border-border text-foreground placeholder:text-muted-foreground focus:border-primary focus:ring-primary"
              />
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="password" className="text-sm font-medium text-card-foreground">
                  Password *
                </Label>
                <PasswordInput
                  id="password"
                  placeholder="Min. 8 characters"
                  value={formData.password}
                  onChange={(e) => handleInputChange("password", e.target.value)}
                  required
                  disabled={isLoading}
                  className="bg-background border-border text-foreground placeholder:text-muted-foreground focus:border-primary focus:ring-primary"
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="confirmPassword" className="text-sm font-medium text-card-foreground">
                  Confirm Password *
                </Label>
                <PasswordInput
                  id="confirmPassword"
                  placeholder="Confirm password"
                  value={formData.confirmPassword}
                  onChange={(e) => handleInputChange("confirmPassword", e.target.value)}
                  required
                  disabled={isLoading}
                  className="bg-background border-border text-foreground placeholder:text-muted-foreground focus:border-primary focus:ring-primary"
                />
              </div>
            </div>
          </div>

          <Separator />

          {/* Organization Information */}
          <div className="space-y-4">
            <h3 className="text-lg font-semibold text-foreground">Organization Setup</h3>
            
            <div className="space-y-2">
              <Label htmlFor="organizationName" className="text-sm font-medium text-card-foreground">
                Organization Name *
              </Label>
              <Input
                id="organizationName"
                type="text"
                placeholder="Acme Corporation"
                value={formData.organizationName}
                onChange={(e) => handleInputChange("organizationName", e.target.value)}
                required
                disabled={isLoading}
                className="bg-background border-border text-foreground placeholder:text-muted-foreground focus:border-primary focus:ring-primary"
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="subscriptionTier" className="text-sm font-medium text-card-foreground">
                Plan Selection
              </Label>
              <Select 
                value={formData.subscriptionTier} 
                onValueChange={(value: 'free' | 'basic' | 'pro') => handleInputChange("subscriptionTier", value)}
              >
                <SelectTrigger className="bg-background border-border text-foreground">
                  <SelectValue placeholder="Select a plan" />
                </SelectTrigger>
                <SelectContent>
                  {subscriptionTiers.map((tier) => (
                    <SelectItem key={tier.value} value={tier.value}>
                      <div className="flex flex-col">
                        <span className="font-medium">{tier.label}</span>
                        <span className="text-xs text-muted-foreground">{tier.description}</span>
                      </div>
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
          </div>

          <Button 
            type="submit" 
            className="w-full bg-primary hover:bg-primary/90 text-primary-foreground" 
            disabled={isLoading}
          >
            {isLoading ? "Creating Account..." : "Create Account & Start Trial"}
          </Button>

          <div className="text-center space-y-2">
            <p className="text-xs text-muted-foreground">
              By creating an account, you agree to our{" "}
              <a href="/terms" className="text-primary hover:underline">Terms of Service</a>
              {" "}and{" "}
              <a href="/privacy" className="text-primary hover:underline">Privacy Policy</a>
            </p>
          </div>
        </form>
      </CardContent>
    </Card>
  )
}
