"use client"

import { useState } from "react"
import { useRouter } from "next/navigation"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Checkbox } from "@/components/ui/checkbox"
import { Alert, AlertDescription } from "@/components/ui/alert"
import { 
  Building2, 
  User, 
  Mail, 
  Lock, 
  ArrowRight, 
  CheckCircle,
  Zap,
  Shield,
  Users,
  Globe,
  Loader2,
  AlertTriangle
} from "lucide-react"
import Link from "next/link"

// Organization signup interface
interface OrganizationSignup {
  organizationName: string
  organizationSlug: string
  industry: string
  organizationSize: string
  website?: string
  firstName: string
  lastName: string
  email: string
  password: string
  confirmPassword: string
  jobTitle: string
  plan: 'trial' | 'basic' | 'pro'
  acceptTerms: boolean
  acceptPrivacy: boolean
  marketingOptIn: boolean
}

const industries = [
  "Technology",
  "Healthcare", 
  "Finance",
  "Manufacturing",
  "Retail",
  "Consulting",
  "Education",
  "Real Estate",
  "Other"
]

const organizationSizes = [
  "1-10 employees",
  "11-50 employees", 
  "51-200 employees",
  "201-500 employees",
  "500+ employees"
]

const plans = [
  {
    id: 'trial',
    name: 'Free Trial',
    price: 'Free for 14 days',
    description: 'Perfect for trying out SalesOptimizer',
    features: ['Up to 5 users', 'Basic reporting', 'Email support', 'Core features'],
    popular: true,
    icon: <Users className="h-5 w-5" />
  },
  {
    id: 'basic', 
    name: 'Basic',
    price: '$29/month',
    description: 'For small teams getting started',
    features: ['Up to 25 users', 'Advanced reporting', 'Priority support', 'Integrations'],
    popular: false,
    icon: <Zap className="h-5 w-5" />
  },
  {
    id: 'pro',
    name: 'Professional', 
    price: '$79/month',
    description: 'For growing sales teams',
    features: ['Unlimited users', 'Custom reporting', 'Phone support', 'Advanced integrations'],
    popular: false,
    icon: <Shield className="h-5 w-5" />
  }
]

export function SignupSection() {
  const router = useRouter()
  const [currentStep, setCurrentStep] = useState(1)
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [formData, setFormData] = useState<OrganizationSignup>({
    organizationName: '',
    organizationSlug: '',
    industry: '',
    organizationSize: '',
    website: '',
    firstName: '',
    lastName: '',
    email: '',
    password: '',
    confirmPassword: '',
    jobTitle: '',
    plan: 'trial',
    acceptTerms: false,
    acceptPrivacy: false,
    marketingOptIn: false
  })

  const updateField = (field: keyof OrganizationSignup, value: any) => {
    setFormData(prev => ({ ...prev, [field]: value }))
    
    // Auto-generate slug from organization name
    if (field === 'organizationName') {
      const slug = value.toLowerCase()
        .replace(/[^a-z0-9\\s-]/g, '')
        .replace(/\\s+/g, '-')
        .replace(/-+/g, '-')
        .trim()
      setFormData(prev => ({ ...prev, organizationSlug: slug }))
    }
  }

  const validateStep = (step: number): boolean => {
    switch (step) {
      case 1:
        return !!(formData.organizationName && formData.industry && formData.organizationSize)
      case 2:
        return !!(formData.firstName && formData.lastName && formData.email && 
                 formData.password && formData.password === formData.confirmPassword &&
                 formData.password.length >= 8)
      case 3:
        return !!(formData.plan)
      case 4:
        return formData.acceptTerms && formData.acceptPrivacy
      default:
        return false
    }
  }

  const handleNext = () => {
    setError(null)
    if (validateStep(currentStep)) {
      setCurrentStep(prev => prev + 1)
    } else {
      setError('Please fill in all required fields')
    }
  }

  const handleBack = () => {
    setCurrentStep(prev => prev - 1)
    setError(null)
  }

  const handleSubmit = async () => {
    if (!validateStep(4)) {
      setError('Please complete all required fields and accept the terms')
      return
    }
    
    setIsLoading(true)
    setError(null)
    
    try {
      const response = await fetch('/api/v1/organizations/register', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify({
          organization_name: formData.organizationName,
          organization_slug: formData.organizationSlug,
          industry: formData.industry,
          organization_size: formData.organizationSize,
          website: formData.website,
          first_name: formData.firstName,
          last_name: formData.lastName,
          email: formData.email,
          password: formData.password,
          job_title: formData.jobTitle,
          plan: formData.plan,
          accept_terms: formData.acceptTerms,
          accept_privacy: formData.acceptPrivacy,
          marketing_opt_in: formData.marketingOptIn
        })
      })
      
      if (response.ok) {
        const result = await response.json()
        console.log('Registration successful:', result)
        router.push('/dashboard')
      } else {
        const contentType = response.headers.get('content-type');
        let errorMsg = 'Registration failed';
        if (contentType && contentType.includes('application/json')) {
          const error = await response.json();
          errorMsg = error.detail || errorMsg;
        } else {
          const text = await response.text();
          errorMsg = text || errorMsg;
        }
        throw new Error(errorMsg);
      }
    } catch (error: any) {
      console.error('Registration error:', error)
      setError(error.message || 'Registration failed. Please try again.')
    } finally {
      setIsLoading(false)
    }
  }

  const getStepTitle = () => {
    switch (currentStep) {
      case 1: return "Organization Details"
      case 2: return "Admin Account"
      case 3: return "Choose Your Plan"
      case 4: return "Legal Agreements"
      default: return "Sign Up"
    }
  }

  const getStepDescription = () => {
    switch (currentStep) {
      case 1: return "Tell us about your organization"
      case 2: return "Create your admin account"
      case 3: return "Select the plan that fits your needs"
      case 4: return "Review and accept our terms"
      default: return ""
    }
  }

  return (
    <section id="signup" className="py-20 px-4 sm:px-6 lg:px-8 bg-gradient-to-b from-blue-50/50 to-purple-50/50 dark:from-gray-900 dark:to-gray-800">
      <div className="max-w-6xl mx-auto">
        <div className="text-center mb-12">
          <h2 className="text-3xl sm:text-4xl font-bold text-foreground mb-4">
            Start Your Free Trial Today
          </h2>
          <p className="text-xl text-muted-foreground max-w-2xl mx-auto">
            Create your organization account and get started with SalesOptimizer in minutes
          </p>
        </div>

        <div className="grid lg:grid-cols-2 gap-12 items-start">
          {/* Benefits Column */}
          <div className="space-y-8">
            <div>
              <h3 className="text-2xl font-semibold text-foreground mb-6">
                Why Choose SalesOptimizer?
              </h3>
              
              <div className="space-y-6">
                <div className="flex items-start space-x-4">
                  <div className="flex-shrink-0 w-12 h-12 bg-blue-100 dark:bg-blue-900/30 rounded-lg flex items-center justify-center">
                    <Zap className="h-6 w-6 text-blue-600" />
                  </div>
                  <div>
                    <h4 className="font-semibold text-foreground mb-2">Quick Setup</h4>
                    <p className="text-muted-foreground">Get your team up and running in under 10 minutes with our guided setup process.</p>
                  </div>
                </div>
                
                <div className="flex items-start space-x-4">
                  <div className="flex-shrink-0 w-12 h-12 bg-green-100 dark:bg-green-900/30 rounded-lg flex items-center justify-center">
                    <Shield className="h-6 w-6 text-green-600" />
                  </div>
                  <div>
                    <h4 className="font-semibold text-foreground mb-2">Enterprise Security</h4>
                    <p className="text-muted-foreground">Bank-level security with encryption, audit logs, and compliance standards.</p>
                  </div>
                </div>
                
                <div className="flex items-start space-x-4">
                  <div className="flex-shrink-0 w-12 h-12 bg-purple-100 dark:bg-purple-900/30 rounded-lg flex items-center justify-center">
                    <Users className="h-6 w-6 text-purple-600" />
                  </div>
                  <div>
                    <h4 className="font-semibold text-foreground mb-2">Team Collaboration</h4>
                    <p className="text-muted-foreground">Multi-tenant architecture with role-based access for seamless teamwork.</p>
                  </div>
                </div>
                
                <div className="flex items-start space-x-4">
                  <div className="flex-shrink-0 w-12 h-12 bg-orange-100 dark:bg-orange-900/30 rounded-lg flex items-center justify-center">
                    <Globe className="h-6 w-6 text-orange-600" />
                  </div>
                  <div>
                    <h4 className="font-semibold text-foreground mb-2">Global Access</h4>
                    <p className="text-muted-foreground">Cloud-based platform accessible anywhere with mobile app support.</p>
                  </div>
                </div>
              </div>
            </div>

            {/* Trust indicators */}
            <div className="bg-white/50 dark:bg-gray-800/50 rounded-lg p-6 border border-gray-200/50 dark:border-gray-700/50">
              <div className="flex items-center justify-center space-x-8 text-sm text-muted-foreground">
                <div className="flex items-center space-x-2">
                  <Shield className="h-4 w-4" />
                  <span>SOC 2 Compliant</span>
                </div>
                <div className="flex items-center space-x-2">
                  <Lock className="h-4 w-4" />
                  <span>GDPR Ready</span>
                </div>
                <div className="flex items-center space-x-2">
                  <CheckCircle className="h-4 w-4" />
                  <span>99.9% Uptime</span>
                </div>
              </div>
            </div>
          </div>

          {/* Signup Form Column */}
          <div>
            <Card className="border border-gray-200/50 dark:border-gray-700/50 shadow-xl">
              <CardHeader className="text-center pb-4">
                <div className="flex items-center justify-center mb-4">
                  <div className="flex space-x-2">
                    {[1, 2, 3, 4].map((step) => (
                      <div
                        key={step}
                        className={`w-3 h-3 rounded-full transition-colors ${
                          step <= currentStep 
                            ? 'bg-blue-600' 
                            : 'bg-gray-200 dark:bg-gray-700'
                        }`}
                      />
                    ))}
                  </div>
                  <span className="ml-3 text-sm text-muted-foreground">
                    Step {currentStep} of 4
                  </span>
                </div>
                <CardTitle className="text-2xl font-bold text-foreground">
                  {getStepTitle()}
                </CardTitle>
                <CardDescription className="text-muted-foreground">
                  {getStepDescription()}
                </CardDescription>
              </CardHeader>
              
              <CardContent className="space-y-6">
                {error && (
                  <Alert className="border-red-200 bg-red-50 dark:bg-red-900/20">
                    <AlertTriangle className="h-4 w-4 text-red-600" />
                    <AlertDescription className="text-red-700 dark:text-red-400">
                      {error}
                    </AlertDescription>
                  </Alert>
                )}

                {/* Step 1: Organization Details */}
                {currentStep === 1 && (
                  <div className="space-y-4">
                    <div className="space-y-2">
                      <Label htmlFor="organizationName">Organization Name *</Label>
                      <Input
                        id="organizationName"
                        value={formData.organizationName}
                        onChange={(e) => updateField('organizationName', e.target.value)}
                        placeholder="Your Company Name"
                        required
                      />
                    </div>
                    
                    <div className="space-y-2">
                      <Label htmlFor="industry">Industry *</Label>
                      <Select onValueChange={(value) => updateField('industry', value)}>
                        <SelectTrigger>
                          <SelectValue placeholder="Select your industry" />
                        </SelectTrigger>
                        <SelectContent>
                          {industries.map(industry => (
                            <SelectItem key={industry} value={industry}>{industry}</SelectItem>
                          ))}
                        </SelectContent>
                      </Select>
                    </div>
                    
                    <div className="space-y-2">
                      <Label htmlFor="organizationSize">Company Size *</Label>
                      <Select onValueChange={(value) => updateField('organizationSize', value)}>
                        <SelectTrigger>
                          <SelectValue placeholder="Select company size" />
                        </SelectTrigger>
                        <SelectContent>
                          {organizationSizes.map(size => (
                            <SelectItem key={size} value={size}>{size}</SelectItem>
                          ))}
                        </SelectContent>
                      </Select>
                    </div>
                    
                    <div className="space-y-2">
                      <Label htmlFor="website">Website (Optional)</Label>
                      <Input
                        id="website"
                        value={formData.website}
                        onChange={(e) => updateField('website', e.target.value)}
                        placeholder="https://yourcompany.com"
                      />
                    </div>
                  </div>
                )}

                {/* Step 2: Admin Account */}
                {currentStep === 2 && (
                  <div className="space-y-4">
                    <div className="grid grid-cols-2 gap-4">
                      <div className="space-y-2">
                        <Label htmlFor="firstName">First Name *</Label>
                        <Input
                          id="firstName"
                          value={formData.firstName}
                          onChange={(e) => updateField('firstName', e.target.value)}
                          required
                        />
                      </div>
                      <div className="space-y-2">
                        <Label htmlFor="lastName">Last Name *</Label>
                        <Input
                          id="lastName"
                          value={formData.lastName}
                          onChange={(e) => updateField('lastName', e.target.value)}
                          required
                        />
                      </div>
                    </div>
                    
                    <div className="space-y-2">
                      <Label htmlFor="email">Email Address *</Label>
                      <Input
                        id="email"
                        type="email"
                        value={formData.email}
                        onChange={(e) => updateField('email', e.target.value)}
                        required
                      />
                    </div>
                    
                    <div className="space-y-2">
                      <Label htmlFor="jobTitle">Job Title</Label>
                      <Input
                        id="jobTitle"
                        value={formData.jobTitle}
                        onChange={(e) => updateField('jobTitle', e.target.value)}
                        placeholder="e.g., Sales Manager, CEO"
                      />
                    </div>
                    
                    <div className="space-y-2">
                      <Label htmlFor="password">Password *</Label>
                      <Input
                        id="password"
                        type="password"
                        value={formData.password}
                        onChange={(e) => updateField('password', e.target.value)}
                        placeholder="Minimum 8 characters"
                        required
                      />
                    </div>
                    
                    <div className="space-y-2">
                      <Label htmlFor="confirmPassword">Confirm Password *</Label>
                      <Input
                        id="confirmPassword"
                        type="password"
                        value={formData.confirmPassword}
                        onChange={(e) => updateField('confirmPassword', e.target.value)}
                        placeholder="Re-enter your password"
                        required
                      />
                    </div>
                  </div>
                )}

                {/* Step 3: Plan Selection */}
                {currentStep === 3 && (
                  <div className="space-y-4">
                    <div className="grid gap-4">
                      {plans.map(plan => (
                        <div
                          key={plan.id}
                          className={`border-2 rounded-lg p-4 cursor-pointer transition-all ${
                            formData.plan === plan.id
                              ? 'border-blue-600 bg-blue-50 dark:bg-blue-900/20'
                              : 'border-gray-200 dark:border-gray-700 hover:border-gray-300'
                          } ${plan.popular ? 'relative' : ''}`}
                          onClick={() => updateField('plan', plan.id)}
                        >
                          {plan.popular && (
                            <div className="absolute -top-3 left-4 bg-blue-600 text-white px-3 py-1 rounded-full text-xs font-semibold">
                              Most Popular
                            </div>
                          )}
                          <div className="flex items-start space-x-3">
                            <div className={`mt-1 ${formData.plan === plan.id ? 'text-blue-600' : 'text-gray-400'}`}>
                              {plan.icon}
                            </div>
                            <div className="flex-1">
                              <div className="flex items-center justify-between mb-1">
                                <h4 className="font-semibold text-foreground">{plan.name}</h4>
                                <span className="font-bold text-foreground">{plan.price}</span>
                              </div>
                              <p className="text-sm text-muted-foreground mb-2">{plan.description}</p>
                              <div className="flex flex-wrap gap-1">
                                {plan.features.slice(0, 3).map((feature, idx) => (
                                  <span key={idx} className="text-xs bg-gray-100 dark:bg-gray-800 px-2 py-1 rounded">
                                    {feature}
                                  </span>
                                ))}
                              </div>
                            </div>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* Step 4: Legal Agreements */}
                {currentStep === 4 && (
                  <div className="space-y-6">
                    <div className="space-y-4">
                      <div className="flex items-start space-x-3">
                        <Checkbox
                          id="acceptTerms"
                          checked={formData.acceptTerms}
                          onCheckedChange={(checked) => updateField('acceptTerms', checked)}
                        />
                        <Label htmlFor="acceptTerms" className="text-sm leading-relaxed">
                          I agree to the{' '}
                          <Link href="/terms" className="text-blue-600 hover:underline">
                            Terms of Service
                          </Link>{' '}
                          *
                        </Label>
                      </div>
                      
                      <div className="flex items-start space-x-3">
                        <Checkbox
                          id="acceptPrivacy"
                          checked={formData.acceptPrivacy}
                          onCheckedChange={(checked) => updateField('acceptPrivacy', checked)}
                        />
                        <Label htmlFor="acceptPrivacy" className="text-sm leading-relaxed">
                          I agree to the{' '}
                          <Link href="/privacy" className="text-blue-600 hover:underline">
                            Privacy Policy
                          </Link>{' '}
                          *
                        </Label>
                      </div>
                      
                      <div className="flex items-start space-x-3">
                        <Checkbox
                          id="marketingOptIn"
                          checked={formData.marketingOptIn}
                          onCheckedChange={(checked) => updateField('marketingOptIn', checked)}
                        />
                        <Label htmlFor="marketingOptIn" className="text-sm leading-relaxed">
                          I would like to receive product updates and marketing communications
                        </Label>
                      </div>
                    </div>
                    
                    <div className="bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 rounded-lg p-4">
                      <div className="flex items-start space-x-3">
                        <CheckCircle className="h-5 w-5 text-green-600 mt-0.5" />
                        <div>
                          <h4 className="font-semibold text-green-800 dark:text-green-200 mb-1">
                            14-Day Free Trial Included
                          </h4>
                          <p className="text-sm text-green-700 dark:text-green-300">
                            No credit card required. Cancel anytime during your trial period.
                          </p>
                        </div>
                      </div>
                    </div>
                  </div>
                )}

                {/* Navigation Buttons */}
                <div className="flex justify-between pt-6">
                  <Button
                    variant="outline"
                    onClick={handleBack}
                    disabled={currentStep === 1}
                    className={currentStep === 1 ? 'invisible' : ''}
                  >
                    Back
                  </Button>
                  
                  {currentStep < 4 ? (
                    <Button onClick={handleNext} disabled={!validateStep(currentStep)}>
                      Next
                      <ArrowRight className="ml-2 h-4 w-4" />
                    </Button>
                  ) : (
                    <Button 
                      onClick={handleSubmit} 
                      disabled={!validateStep(4) || isLoading}
                      className="bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700"
                    >
                      {isLoading ? (
                        <>
                          <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                          Creating Account...
                        </>
                      ) : (
                        <>
                          <CheckCircle className="mr-2 h-4 w-4" />
                          Create Account
                        </>
                      )}
                    </Button>
                  )}
                </div>
              </CardContent>
            </Card>

            {/* Login Link */}
            <div className="text-center mt-6">
              <p className="text-muted-foreground">
                Already have an account?{' '}
                <Link href="/login" className="text-blue-600 hover:underline font-semibold">
                  Sign in
                </Link>
              </p>
            </div>
          </div>
        </div>
      </div>
    </section>
  )
}
