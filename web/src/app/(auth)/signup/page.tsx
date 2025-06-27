"use client"

import { useState } from "react"
import Link from "next/link"
import { ArrowLeft, Zap, Check, Star } from "lucide-react"
import { ThemeToggle } from "@/components/ui/theme-toggle"
import { SignupForm } from "@/components/forms/signup-form"

export default function SignupPage() {
  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 via-white to-purple-50 dark:from-gray-900 dark:via-gray-900 dark:to-gray-800 relative overflow-hidden p-4">
      {/* Background decorations */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute -top-40 -right-40 w-80 h-80 bg-gradient-to-br from-blue-400/20 to-purple-600/20 rounded-full blur-3xl"></div>
        <div className="absolute -bottom-40 -left-40 w-80 h-80 bg-gradient-to-tr from-purple-400/20 to-pink-600/20 rounded-full blur-3xl"></div>
      </div>
      
      {/* Back to Home link */}
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
      
      <div className="max-w-4xl w-full space-y-8 relative z-10">
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
          
          <h2 className="text-2xl font-bold text-foreground mb-2">
            Start Your Free Trial
          </h2>
          <p className="text-lg text-muted-foreground mb-8">
            Create your account and set up your organization in minutes
          </p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 items-start">
          {/* Left side - Signup Form */}
          <div className="order-2 lg:order-1">
            <SignupForm />
          </div>

          {/* Right side - Benefits */}
          <div className="order-1 lg:order-2 space-y-6">
            <div className="bg-card/80 backdrop-blur-sm rounded-lg border border-border p-6 shadow-sm">
              <h3 className="text-xl font-semibold text-foreground mb-4 flex items-center">
                <Star className="h-5 w-5 text-yellow-500 mr-2" />
                What's Included
              </h3>
              <ul className="space-y-3">
                <li className="flex items-start space-x-3">
                  <Check className="h-5 w-5 text-green-500 mt-0.5 flex-shrink-0" />
                  <span className="text-muted-foreground">14-day free trial - no credit card required</span>
                </li>
                <li className="flex items-start space-x-3">
                  <Check className="h-5 w-5 text-green-500 mt-0.5 flex-shrink-0" />
                  <span className="text-muted-foreground">Complete sales pipeline management</span>
                </li>
                <li className="flex items-start space-x-3">
                  <Check className="h-5 w-5 text-green-500 mt-0.5 flex-shrink-0" />
                  <span className="text-muted-foreground">Team collaboration tools</span>
                </li>
                <li className="flex items-start space-x-3">
                  <Check className="h-5 w-5 text-green-500 mt-0.5 flex-shrink-0" />
                  <span className="text-muted-foreground">Analytics and reporting</span>
                </li>
                <li className="flex items-start space-x-3">
                  <Check className="h-5 w-5 text-green-500 mt-0.5 flex-shrink-0" />
                  <span className="text-muted-foreground">Email support</span>
                </li>
              </ul>
            </div>

            <div className="bg-card/80 backdrop-blur-sm rounded-lg border border-border p-6 shadow-sm">
              <h3 className="text-lg font-semibold text-foreground mb-3">Quick Setup</h3>
              <div className="space-y-2 text-sm text-muted-foreground">
                <div className="flex items-center space-x-2">
                  <div className="w-6 h-6 bg-blue-100 dark:bg-blue-900/50 rounded-full flex items-center justify-center">
                    <span className="text-xs font-semibold text-blue-600 dark:text-blue-400">1</span>
                  </div>
                  <span>Create your account</span>
                </div>
                <div className="flex items-center space-x-2">
                  <div className="w-6 h-6 bg-blue-100 dark:bg-blue-900/50 rounded-full flex items-center justify-center">
                    <span className="text-xs font-semibold text-blue-600 dark:text-blue-400">2</span>
                  </div>
                  <span>Set up your organization</span>
                </div>
                <div className="flex items-center space-x-2">
                  <div className="w-6 h-6 bg-blue-100 dark:bg-blue-900/50 rounded-full flex items-center justify-center">
                    <span className="text-xs font-semibold text-blue-600 dark:text-blue-400">3</span>
                  </div>
                  <span>Start optimizing sales</span>
                </div>
              </div>
            </div>

            <p className="text-sm text-muted-foreground text-center">
              Already have an account?{" "}
              <Link 
                href="/login" 
                className="text-primary hover:text-primary/80 font-medium hover:underline transition-colors"
              >
                Sign in here
              </Link>
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}
