"use client"

import { useEffect, useState } from "react"
import { useRouter } from "next/navigation"
import Link from "next/link"
import { CheckCircle, Mail, ArrowRight, Clock, Users, Zap } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"

export default function SignupSuccessPage() {
  const [countdown, setCountdown] = useState(10)
  const router = useRouter()

  useEffect(() => {
    const timer = setInterval(() => {
      setCountdown((prev) => {
        if (prev <= 1) {
          clearInterval(timer)
          router.push("/dashboard")
          return 0
        }
        return prev - 1
      })
    }, 1000)

    return () => clearInterval(timer)
  }, [router])

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-green-50 via-white to-blue-50 dark:from-gray-900 dark:via-gray-900 dark:to-gray-800 relative overflow-hidden p-4">
      {/* Background decorations */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute -top-40 -right-40 w-80 h-80 bg-gradient-to-br from-green-400/20 to-blue-600/20 rounded-full blur-3xl"></div>
        <div className="absolute -bottom-40 -left-40 w-80 h-80 bg-gradient-to-tr from-blue-400/20 to-green-600/20 rounded-full blur-3xl"></div>
      </div>
      
      <div className="max-w-2xl w-full space-y-8 relative z-10">
        {/* Header */}
        <div className="text-center">
          <div className="flex items-center justify-center space-x-3 mb-6">
            <div className="w-16 h-16 bg-gradient-to-r from-green-500 to-blue-600 rounded-full flex items-center justify-center shadow-lg">
              <CheckCircle className="h-8 w-8 text-white" />
            </div>
          </div>
          <h1 className="text-3xl font-bold text-foreground mb-2">
            🎉 Welcome to SalesOptimizer!
          </h1>
          <p className="text-lg text-muted-foreground">
            Your account and organization have been created successfully
          </p>
        </div>

        {/* Success Card */}
        <Card className="border border-green-200 bg-green-50/50 dark:bg-green-900/20 dark:border-green-800">
          <CardHeader>
            <CardTitle className="text-green-800 dark:text-green-200 flex items-center">
              <CheckCircle className="h-5 w-5 mr-2" />
              Account Created Successfully
            </CardTitle>
            <CardDescription className="text-green-700 dark:text-green-300">
              Your free trial has started and you're ready to explore all features
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="text-center">
                <div className="w-12 h-12 bg-green-100 dark:bg-green-800 rounded-lg flex items-center justify-center mx-auto mb-2">
                  <Clock className="h-6 w-6 text-green-600 dark:text-green-400" />
                </div>
                <h3 className="font-semibold text-green-800 dark:text-green-200">14-Day Trial</h3>
                <p className="text-sm text-green-700 dark:text-green-300">Full access to all features</p>
              </div>
              <div className="text-center">
                <div className="w-12 h-12 bg-green-100 dark:bg-green-800 rounded-lg flex items-center justify-center mx-auto mb-2">
                  <Users className="h-6 w-6 text-green-600 dark:text-green-400" />
                </div>
                <h3 className="font-semibold text-green-800 dark:text-green-200">Organization Ready</h3>
                <p className="text-sm text-green-700 dark:text-green-300">Invite your team members</p>
              </div>
              <div className="text-center">
                <div className="w-12 h-12 bg-green-100 dark:bg-green-800 rounded-lg flex items-center justify-center mx-auto mb-2">
                  <Zap className="h-6 w-6 text-green-600 dark:text-green-400" />
                </div>
                <h3 className="font-semibold text-green-800 dark:text-green-200">No Setup Required</h3>
                <p className="text-sm text-green-700 dark:text-green-300">Start using immediately</p>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Next Steps */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center">
              <Mail className="h-5 w-5 mr-2 text-blue-600" />
              What's Next?
            </CardTitle>
            <CardDescription>
              Here's what you can do to get the most out of SalesOptimizer
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div className="flex items-start space-x-3">
                <div className="w-8 h-8 bg-blue-100 dark:bg-blue-900/50 rounded-full flex items-center justify-center flex-shrink-0">
                  <span className="text-sm font-semibold text-blue-600 dark:text-blue-400">1</span>
                </div>
                <div>
                  <h4 className="font-semibold text-foreground">Check your email</h4>
                  <p className="text-sm text-muted-foreground">We've sent you a welcome email with important information and next steps.</p>
                </div>
              </div>
              <div className="flex items-start space-x-3">
                <div className="w-8 h-8 bg-blue-100 dark:bg-blue-900/50 rounded-full flex items-center justify-center flex-shrink-0">
                  <span className="text-sm font-semibold text-blue-600 dark:text-blue-400">2</span>
                </div>
                <div>
                  <h4 className="font-semibold text-foreground">Explore your dashboard</h4>
                  <p className="text-sm text-muted-foreground">Get familiar with the interface and discover powerful features.</p>
                </div>
              </div>
              <div className="flex items-start space-x-3">
                <div className="w-8 h-8 bg-blue-100 dark:bg-blue-900/50 rounded-full flex items-center justify-center flex-shrink-0">
                  <span className="text-sm font-semibold text-blue-600 dark:text-blue-400">3</span>
                </div>
                <div>
                  <h4 className="font-semibold text-foreground">Invite your team</h4>
                  <p className="text-sm text-muted-foreground">Add team members and start collaborating on your sales process.</p>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Action Buttons */}
        <div className="flex flex-col sm:flex-row gap-4 justify-center">
          <Button 
            onClick={() => router.push("/dashboard")}
            className="bg-primary hover:bg-primary/90 text-primary-foreground flex items-center"
          >
            Go to Dashboard
            <ArrowRight className="ml-2 h-4 w-4" />
          </Button>
          <Button variant="outline" asChild>
            <Link href="/help/getting-started">
              View Getting Started Guide
            </Link>
          </Button>
        </div>

        {/* Auto redirect countdown */}
        <div className="text-center">
          <p className="text-sm text-muted-foreground">
            Redirecting to dashboard in <span className="font-semibold text-primary">{countdown}</span> seconds
          </p>
        </div>
      </div>
    </div>
  )
}
