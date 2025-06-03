"use client"

import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { 
  ArrowRight, BarChart3, Users, Zap, Shield, TrendingUp, CheckCircle, Star, 
  Brain, MessageSquare, Globe, Smartphone, Database, Lock, Mail, Phone, 
  MapPin, Clock, UserCheck, Target, PieChart, FileSpreadsheet, Bell,
  Workflow, Calendar, CreditCard, Check, X
} from "lucide-react"
import Link from "next/link"
import { LandingHeader } from "@/components/landing/landing-header"
import { LandingFooter } from "@/components/landing/landing-footer"
import { useState } from "react"

export function LandingPage() {
  const [activeFeatureTab, setActiveFeatureTab] = useState('core')
  const [billingPeriod, setBillingPeriod] = useState<'monthly' | 'annual'>('monthly')

  const coreFeatures = [
    {
      icon: <BarChart3 className="h-8 w-8 text-blue-600" />,
      title: "Advanced Analytics",
      description: "Real-time insights with customizable dashboards, performance tracking, and predictive analytics for data-driven decisions."
    },
    {
      icon: <Users className="h-8 w-8 text-green-600" />,
      title: "Multi-Tenant Team Management",
      description: "Role-based access control with Org Admin, Team Manager, and Sales Rep permissions for complete team oversight."
    },
    {
      icon: <Target className="h-8 w-8 text-red-600" />,
      title: "Opportunity Management",
      description: "Visual pipeline with drag-and-drop stage management, success probability tracking, and automated follow-ups."
    },
    {
      icon: <CheckCircle className="h-8 w-8 text-indigo-600" />,
      title: "Advanced Task Management",
      description: "Collaborative tasks, private assignments, priority levels, dependencies, and automated reminders with team coordination."
    },
    {
      icon: <Shield className="h-8 w-8 text-purple-600" />,
      title: "Enterprise Security",
      description: "Bank-level security with tenant isolation, data encryption, audit logs, and compliance standards (SOC 2, GDPR)."
    },
    {
      icon: <Bell className="h-8 w-8 text-orange-600" />,
      title: "Real-Time Notifications",
      description: "Push notifications, email alerts, WebSocket updates, and customizable notification preferences for instant updates."
    }
  ]

  const aiFeatures = [
    {
      icon: <Brain className="h-8 w-8 text-purple-600" />,
      title: "AI Success Probability",
      description: "Machine learning algorithms analyze historical patterns, deal characteristics, and interaction data to predict opportunity success rates."
    },
    {
      icon: <TrendingUp className="h-8 w-8 text-green-600" />,
      title: "Predictive Lead Scoring",
      description: "Intelligent lead qualification using natural language processing and behavioral analysis to prioritize high-value prospects."
    },
    {
      icon: <PieChart className="h-8 w-8 text-blue-600" />,
      title: "Smart Recommendations",
      description: "AI-powered next best actions, optimal contact timing, deal prioritization, and resource allocation optimization."
    },
    {
      icon: <Workflow className="h-8 w-8 text-red-600" />,
      title: "Workflow Automation",
      description: "Trigger-based actions, custom workflow builder, automatic task creation, and intelligent reminder scheduling."
    }
  ]

  const integrationFeatures = [
    {
      icon: <Database className="h-8 w-8 text-blue-600" />,
      title: "Data Import/Export",
      description: "CSV import with validation, bulk data operations, CRM integrations (Salesforce, HubSpot), and automated data sync."
    },
    {
      icon: <Mail className="h-8 w-8 text-green-600" />,
      title: "Email Integration",
      description: "Gmail/Outlook sync, automated email notifications, template management, and email tracking with customer records."
    },
    {
      icon: <Calendar className="h-8 w-8 text-purple-600" />,
      title: "Calendar Sync",
      description: "Google Calendar and Outlook integration, meeting scheduling, automatic follow-up creation, and availability management."
    },
    {
      icon: <MessageSquare className="h-8 w-8 text-orange-600" />,
      title: "Communication Tools",
      description: "Slack/Teams integration, in-app messaging, activity feeds, and collaborative editing with real-time updates."
    }
  ]

  const mobileFeatures = [
    {
      icon: <Smartphone className="h-8 w-8 text-blue-600" />,
      title: "Progressive Web App",
      description: "Mobile-optimized PWA with offline capabilities, push notifications, and native app-like experience across all devices."
    },
    {
      icon: <Globe className="h-8 w-8 text-green-600" />,
      title: "Offline Functionality",
      description: "IndexedDB storage, background sync, conflict resolution, optimistic UI updates with automatic data synchronization."
    },
    {
      icon: <Lock className="h-8 w-8 text-red-600" />,
      title: "Secure Mobile Access",
      description: "Biometric authentication, secure data caching, encrypted communications, and device-specific security policies."
    }
  ]

  const featureTabs = [
    { id: 'core', label: 'Core Features', features: coreFeatures },
    { id: 'ai', label: 'AI & Analytics', features: aiFeatures },
    { id: 'integration', label: 'Integrations', features: integrationFeatures },
    { id: 'mobile', label: 'Mobile & PWA', features: mobileFeatures }
  ]

  const pricingPlans = [
    {
      name: "Starter",
      description: "Perfect for small sales teams getting started",
      price: { monthly: 29, annual: 290 },
      features: [
        "Up to 5 users",
        "Basic opportunity management",
        "Task management",
        "Email integration",
        "Mobile app access",
        "Standard support",
        "Basic analytics",
        "CSV import/export"
      ],
      limitations: [
        "No AI predictions",
        "Limited integrations",
        "No custom workflows"
      ],
      recommended: false,
      buttonText: "Start Free Trial"
    },
    {
      name: "Professional",
      description: "Advanced features for growing sales teams",
      price: { monthly: 79, annual: 790 },
      features: [
        "Up to 25 users",
        "Advanced analytics & reporting",
        "AI success probability",
        "Workflow automation",
        "Calendar integration",
        "Priority support",
        "Custom fields",
        "API access",
        "Advanced task management",
        "Real-time notifications"
      ],
      limitations: [
        "Limited AI features",
        "Standard integrations only"
      ],
      recommended: true,
      buttonText: "Start Free Trial"
    },
    {
      name: "Enterprise",
      description: "Full-featured solution for large organizations",
      price: { monthly: 149, annual: 1490 },
      features: [
        "Unlimited users",
        "Full AI & ML capabilities",
        "Advanced integrations (Salesforce, HubSpot)",
        "Custom workflow builder",
        "SSO & advanced security",
        "Dedicated support manager",
        "Custom onboarding",
        "Advanced audit logs",
        "White-label options",
        "SLA guarantee",
        "Data backup & recovery",
        "Compliance tools (SOC 2, GDPR)"
      ],
      limitations: [],
      recommended: false,
      buttonText: "Contact Sales"
    }
  ]

  const testimonials = [
    {
      name: "Sarah Johnson",
      role: "Sales Director",
      company: "TechStart Inc.",
      content: "SalesOptimizer's AI predictions helped us identify our highest-value opportunities. We saw a 40% increase in conversions within the first quarter.",
      rating: 5,
      image: "/api/placeholder/64/64"
    },
    {
      name: "Michael Chen",
      role: "VP of Sales",
      company: "Growth Corp",
      content: "The task management and team collaboration features transformed how we work. Our team productivity increased by 60% in just 3 months.",
      rating: 5,
      image: "/api/placeholder/64/64"
    },
    {
      name: "Emily Rodriguez",
      role: "Sales Manager",
      company: "Scale Solutions",
      content: "Best CRM we've ever used. The mobile app and offline capabilities mean our field sales team never misses an opportunity.",
      rating: 5,
      image: "/api/placeholder/64/64"
    },
    {
      name: "David Kim",
      role: "CEO",
      company: "InnovateCorp",
      content: "The predictive analytics and automation features gave us insights we never had before. Revenue forecasting is now 95% accurate.",
      rating: 5,
      image: "/api/placeholder/64/64"
    }
  ]

  const stats = [
    { value: "500+", label: "Active Organizations" },
    { value: "50K+", label: "Users Worldwide" },
    { value: "99.9%", label: "Uptime SLA" },
    { value: "24/7", label: "Support Available" }
  ]

  const companyValues = [
    {
      icon: <Users className="h-8 w-8 text-blue-600" />,
      title: "Customer-Centric",
      description: "Every feature is built based on real customer feedback and needs"
    },
    {
      icon: <Shield className="h-8 w-8 text-green-600" />,
      title: "Security First",
      description: "Enterprise-grade security and compliance built into every aspect"
    },
    {
      icon: <Brain className="h-8 w-8 text-purple-600" />,
      title: "Innovation Driven",
      description: "Continuously pushing the boundaries with AI and machine learning"
    },
    {
      icon: <Globe className="h-8 w-8 text-orange-600" />,
      title: "Global Scale",
      description: "Built to serve teams worldwide with multi-tenant architecture"
    }
  ]

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50">
      <LandingHeader />
      
      {/* Hero Section */}
      <section className="relative py-20 px-4 sm:px-6 lg:px-8">
        <div className="max-w-7xl mx-auto text-center">
          <Badge variant="secondary" className="mb-4 bg-blue-100 text-blue-800 hover:bg-blue-200">
            🚀 Now with AI-Powered Insights
          </Badge>
          
          <h1 className="text-4xl sm:text-6xl font-bold text-gray-900 mb-6 leading-tight">
            Supercharge Your
            <span className="text-transparent bg-clip-text bg-gradient-to-r from-blue-600 to-purple-600"> Sales Performance</span>
          </h1>
          
          <p className="text-xl text-gray-600 mb-8 max-w-3xl mx-auto leading-relaxed">
            Transform your sales process with intelligent automation, real-time analytics, and powerful team management tools. 
            Built for modern sales teams who demand results.
          </p>
          
          <div className="flex flex-col sm:flex-row gap-4 justify-center items-center mb-12">
            <Link href="/login">
              <Button size="lg" className="bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-white px-8 py-3 text-lg font-semibold shadow-lg hover:shadow-xl transition-all duration-200">
                Get Started Free
                <ArrowRight className="ml-2 h-5 w-5" />
              </Button>
            </Link>
            
            <Button variant="outline" size="lg" className="px-8 py-3 text-lg font-semibold border-2 hover:bg-gray-50">
              Watch Demo
            </Button>
          </div>
          
          {/* Stats */}
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-8 max-w-4xl mx-auto">
            {stats.map((stat, index) => (
              <div key={index} className="text-center">
                <div className="text-3xl font-bold text-gray-900 mb-1">{stat.value}</div>
                <div className="text-sm text-gray-600">{stat.label}</div>
              </div>
            ))}
          </div>
        </div>
        
        {/* Background decoration */}
        <div className="absolute top-0 left-0 w-full h-full overflow-hidden pointer-events-none">
          <div className="absolute top-20 left-10 w-72 h-72 bg-blue-200 rounded-full mix-blend-multiply filter blur-xl opacity-20 animate-blob"></div>
          <div className="absolute top-40 right-10 w-72 h-72 bg-purple-200 rounded-full mix-blend-multiply filter blur-xl opacity-20 animate-blob animation-delay-2000"></div>
          <div className="absolute -bottom-8 left-20 w-72 h-72 bg-pink-200 rounded-full mix-blend-multiply filter blur-xl opacity-20 animate-blob animation-delay-4000"></div>
        </div>
      </section>

      {/* Features Section */}
      <section id="features" className="py-20 px-4 sm:px-6 lg:px-8 bg-white">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-3xl sm:text-4xl font-bold text-gray-900 mb-4">
              Complete Sales Optimization Platform
            </h2>
            <p className="text-xl text-gray-600 max-w-3xl mx-auto">
              From AI-powered predictions to enterprise-grade security, everything you need to transform your sales process
            </p>
          </div>

          {/* Feature Tabs */}
          <div className="flex flex-wrap justify-center mb-12 gap-2">
            {featureTabs.map((tab) => (
              <Button
                key={tab.id}
                variant={activeFeatureTab === tab.id ? "default" : "outline"}
                onClick={() => setActiveFeatureTab(tab.id)}
                className="mb-2"
              >
                {tab.label}
              </Button>
            ))}
          </div>
          
          {/* Feature Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            {featureTabs.find(tab => tab.id === activeFeatureTab)?.features.map((feature, index) => (
              <Card key={index} className="border-0 shadow-lg hover:shadow-xl transition-shadow duration-300 group">
                <CardHeader>
                  <div className="mb-4 group-hover:scale-110 transition-transform duration-200">
                    {feature.icon}
                  </div>
                  <CardTitle className="text-xl font-semibold text-gray-900">
                    {feature.title}
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <CardDescription className="text-gray-600 text-base leading-relaxed">
                    {feature.description}
                  </CardDescription>
                </CardContent>
              </Card>
            ))}
          </div>

          {/* Role-Based Access Section */}
          <div className="mt-20">
            <div className="text-center mb-12">
              <h3 className="text-2xl sm:text-3xl font-bold text-gray-900 mb-4">
                Built for Every Role in Your Sales Organization
              </h3>
              <p className="text-lg text-gray-600 max-w-2xl mx-auto">
                Tailored permissions and features for each team member
              </p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              <Card className="text-center border-2 border-blue-200 hover:border-blue-300 transition-colors">
                <CardHeader>
                  <div className="w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-4">
                    <UserCheck className="h-8 w-8 text-blue-600" />
                  </div>
                  <CardTitle className="text-blue-600">Org Admin</CardTitle>
                </CardHeader>
                <CardContent>
                  <ul className="text-sm text-gray-600 space-y-2">
                    <li>• User management</li>
                    <li>• Data governance</li>
                    <li>• Audit & compliance</li>
                    <li>• Organization settings</li>
                  </ul>
                </CardContent>
              </Card>

              <Card className="text-center border-2 border-green-200 hover:border-green-300 transition-colors">
                <CardHeader>
                  <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
                    <Users className="h-8 w-8 text-green-600" />
                  </div>
                  <CardTitle className="text-green-600">Team Manager</CardTitle>
                </CardHeader>
                <CardContent>
                  <ul className="text-sm text-gray-600 space-y-2">
                    <li>• Team leadership</li>
                    <li>• Performance tracking</li>
                    <li>• Task assignment</li>
                    <li>• Goal management</li>
                  </ul>
                </CardContent>
              </Card>

              <Card className="text-center border-2 border-orange-200 hover:border-orange-300 transition-colors">
                <CardHeader>
                  <div className="w-16 h-16 bg-orange-100 rounded-full flex items-center justify-center mx-auto mb-4">
                    <Target className="h-8 w-8 text-orange-600" />
                  </div>
                  <CardTitle className="text-orange-600">Sales Rep</CardTitle>
                </CardHeader>
                <CardContent>
                  <ul className="text-sm text-gray-600 space-y-2">
                    <li>• Opportunity management</li>
                    <li>• Customer relationships</li>
                    <li>• Activity tracking</li>
                    <li>• Personal analytics</li>
                  </ul>
                </CardContent>
              </Card>
            </div>
          </div>
        </div>
      </section>

      {/* Pricing Section */}
      <section id="pricing" className="py-20 px-4 sm:px-6 lg:px-8 bg-gradient-to-br from-gray-50 to-blue-50">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-3xl sm:text-4xl font-bold text-gray-900 mb-4">
              Simple, Transparent Pricing
            </h2>
            <p className="text-xl text-gray-600 max-w-2xl mx-auto mb-8">
              Choose the plan that fits your team size and needs. All plans include a 14-day free trial.
            </p>

            {/* Billing Toggle */}
            <div className="flex items-center justify-center space-x-4 mb-12">
              <span className={`text-sm font-medium ${billingPeriod === 'monthly' ? 'text-gray-900' : 'text-gray-500'}`}>
                Monthly
              </span>
              <button
                onClick={() => setBillingPeriod(billingPeriod === 'monthly' ? 'annual' : 'monthly')}
                className="relative inline-flex h-6 w-11 items-center rounded-full bg-gray-200 transition-colors focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
              >
                <span
                  className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                    billingPeriod === 'annual' ? 'translate-x-6' : 'translate-x-1'
                  }`}
                />
              </button>
              <span className={`text-sm font-medium ${billingPeriod === 'annual' ? 'text-gray-900' : 'text-gray-500'}`}>
                Annual
              </span>
              {billingPeriod === 'annual' && (
                <Badge variant="secondary" className="bg-green-100 text-green-800">
                  Save 20%
                </Badge>
              )}
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            {pricingPlans.map((plan, index) => (
              <Card 
                key={index} 
                className={`relative border-2 ${plan.recommended ? 'border-blue-500 shadow-xl' : 'border-gray-200'} hover:shadow-lg transition-shadow duration-300`}
              >
                {plan.recommended && (
                  <div className="absolute -top-4 left-1/2 transform -translate-x-1/2">
                    <Badge className="bg-blue-500 text-white px-4 py-1">
                      Most Popular
                    </Badge>
                  </div>
                )}
                
                <CardHeader className="text-center pb-8">
                  <CardTitle className="text-2xl font-bold text-gray-900 mb-2">
                    {plan.name}
                  </CardTitle>
                  <CardDescription className="text-gray-600 mb-6">
                    {plan.description}
                  </CardDescription>
                  <div className="flex items-baseline justify-center">
                    <span className="text-4xl font-bold text-gray-900">
                      ${plan.price[billingPeriod]}
                    </span>
                    <span className="text-gray-500 ml-1">
                      /{billingPeriod === 'monthly' ? 'month' : 'year'}
                    </span>
                  </div>
                  {billingPeriod === 'annual' && (
                    <p className="text-sm text-green-600 mt-2">
                      ${Math.round(plan.price.annual / 12)}/month billed annually
                    </p>
                  )}
                </CardHeader>

                <CardContent className="space-y-6">
                  <div className="space-y-3">
                    {plan.features.map((feature, featureIndex) => (
                      <div key={featureIndex} className="flex items-center space-x-3">
                        <Check className="h-5 w-5 text-green-500 flex-shrink-0" />
                        <span className="text-gray-700">{feature}</span>
                      </div>
                    ))}
                    {plan.limitations.map((limitation, limitIndex) => (
                      <div key={limitIndex} className="flex items-center space-x-3">
                        <X className="h-5 w-5 text-gray-400 flex-shrink-0" />
                        <span className="text-gray-500">{limitation}</span>
                      </div>
                    ))}
                  </div>

                  <Button 
                    className={`w-full ${plan.recommended ? 'bg-blue-600 hover:bg-blue-700' : ''}`}
                    variant={plan.recommended ? "default" : "outline"}
                    size="lg"
                  >
                    {plan.buttonText}
                  </Button>
                </CardContent>
              </Card>
            ))}
          </div>

          <div className="text-center mt-12">
            <p className="text-gray-600 mb-4">
              Need a custom solution? <Link href="#contact" className="text-blue-600 hover:text-blue-800 font-medium">Contact our sales team</Link>
            </p>
            <div className="flex flex-wrap justify-center gap-6 text-sm text-gray-500">
              <div className="flex items-center">
                <Check className="h-4 w-4 text-green-500 mr-1" />
                14-day free trial
              </div>
              <div className="flex items-center">
                <Check className="h-4 w-4 text-green-500 mr-1" />
                No setup fees
              </div>
              <div className="flex items-center">
                <Check className="h-4 w-4 text-green-500 mr-1" />
                Cancel anytime
              </div>
              <div className="flex items-center">
                <Check className="h-4 w-4 text-green-500 mr-1" />
                24/7 support
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Testimonials Section */}
      <section className="py-20 px-4 sm:px-6 lg:px-8 bg-white">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-3xl sm:text-4xl font-bold text-gray-900 mb-4">
              Trusted by Sales Leaders Worldwide
            </h2>
            <p className="text-xl text-gray-600 max-w-2xl mx-auto">
              See how teams are transforming their sales performance with SalesOptimizer
            </p>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
            {testimonials.map((testimonial, index) => (
              <Card key={index} className="border-0 shadow-lg bg-gradient-to-br from-white to-gray-50">
                <CardHeader>
                  <div className="flex items-center mb-4">
                    {[...Array(testimonial.rating)].map((_, i) => (
                      <Star key={i} className="h-5 w-5 text-yellow-400 fill-current" />
                    ))}
                  </div>
                  <CardDescription className="text-gray-700 text-base italic leading-relaxed line-clamp-4">
                    "{testimonial.content}"
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="border-t pt-4">
                    <p className="font-semibold text-gray-900">{testimonial.name}</p>
                    <p className="text-sm text-gray-600">{testimonial.role}</p>
                    <p className="text-sm text-blue-600 font-medium">{testimonial.company}</p>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      </section>

      {/* About Section */}
      <section id="about" className="py-20 px-4 sm:px-6 lg:px-8 bg-gradient-to-br from-blue-50 to-purple-50">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-3xl sm:text-4xl font-bold text-gray-900 mb-6">
              Built for the Future of Sales
            </h2>
            <p className="text-xl text-gray-600 max-w-3xl mx-auto leading-relaxed">
              SalesOptimizer was founded with a simple mission: to empower sales teams with intelligent technology 
              that drives real results. We combine cutting-edge AI with intuitive design to create the most powerful 
              sales optimization platform available.
            </p>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 items-center mb-16">
            <div>
              <h3 className="text-2xl font-bold text-gray-900 mb-6">Our Story</h3>
              <div className="space-y-4 text-gray-600">
                <p>
                  Founded in 2023, SalesOptimizer emerged from the frustration of sales teams struggling with 
                  outdated tools and manual processes. Our founders, experienced sales leaders and technology 
                  experts, recognized the need for a platform that truly understands modern sales workflows.
                </p>
                <p>
                  Today, we serve over 500 organizations worldwide, from fast-growing startups to Fortune 500 
                  companies. Our platform has helped teams increase their conversion rates by an average of 40% 
                  and reduce sales cycle times by 30%.
                </p>
                <p>
                  We're committed to continuous innovation, regularly releasing new features based on customer 
                  feedback and emerging industry trends. Our roadmap includes advanced AI capabilities, enhanced 
                  mobile experiences, and deeper integration possibilities.
                </p>
              </div>
            </div>

            <div className="grid grid-cols-2 gap-6">
              <div className="text-center">
                <div className="text-4xl font-bold text-blue-600 mb-2">500+</div>
                <div className="text-gray-600">Organizations</div>
              </div>
              <div className="text-center">
                <div className="text-4xl font-bold text-green-600 mb-2">50K+</div>
                <div className="text-gray-600">Active Users</div>
              </div>
              <div className="text-center">
                <div className="text-4xl font-bold text-purple-600 mb-2">40%</div>
                <div className="text-gray-600">Avg. Conversion Increase</div>
              </div>
              <div className="text-center">
                <div className="text-4xl font-bold text-orange-600 mb-2">99.9%</div>
                <div className="text-gray-600">Uptime SLA</div>
              </div>
            </div>
          </div>

          {/* Company Values */}
          <div>
            <h3 className="text-2xl font-bold text-gray-900 text-center mb-12">Our Values</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
              {companyValues.map((value, index) => (
                <Card key={index} className="text-center border-0 shadow-lg bg-white">
                  <CardHeader>
                    <div className="mx-auto mb-4">
                      {value.icon}
                    </div>
                    <CardTitle className="text-lg font-semibold text-gray-900">
                      {value.title}
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <p className="text-gray-600 text-sm">
                      {value.description}
                    </p>
                  </CardContent>
                </Card>
              ))}
            </div>
          </div>
        </div>
      </section>

      {/* Contact Section */}
      <section id="contact" className="py-20 px-4 sm:px-6 lg:px-8 bg-white">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-3xl sm:text-4xl font-bold text-gray-900 mb-4">
              Get in Touch
            </h2>
            <p className="text-xl text-gray-600 max-w-2xl mx-auto">
              Ready to transform your sales process? Our team is here to help you get started.
            </p>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-12">
            {/* Contact Information */}
            <div>
              <h3 className="text-2xl font-bold text-gray-900 mb-8">Contact Information</h3>
              
              <div className="space-y-6">
                <div className="flex items-start space-x-4">
                  <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center flex-shrink-0">
                    <Mail className="h-6 w-6 text-blue-600" />
                  </div>
                  <div>
                    <h4 className="text-lg font-semibold text-gray-900 mb-1">Email</h4>
                    <p className="text-gray-600">sales@salesoptimizer.com</p>
                    <p className="text-gray-600">support@salesoptimizer.com</p>
                  </div>
                </div>

                <div className="flex items-start space-x-4">
                  <div className="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center flex-shrink-0">
                    <Phone className="h-6 w-6 text-green-600" />
                  </div>
                  <div>
                    <h4 className="text-lg font-semibold text-gray-900 mb-1">Phone</h4>
                    <p className="text-gray-600">+1 (555) 123-4567</p>
                    <p className="text-gray-600">+1 (555) 987-6543 (Support)</p>
                  </div>
                </div>

                <div className="flex items-start space-x-4">
                  <div className="w-12 h-12 bg-purple-100 rounded-lg flex items-center justify-center flex-shrink-0">
                    <MapPin className="h-6 w-6 text-purple-600" />
                  </div>
                  <div>
                    <h4 className="text-lg font-semibold text-gray-900 mb-1">Office</h4>
                    <p className="text-gray-600">123 Innovation Drive</p>
                    <p className="text-gray-600">San Francisco, CA 94105</p>
                  </div>
                </div>

                <div className="flex items-start space-x-4">
                  <div className="w-12 h-12 bg-orange-100 rounded-lg flex items-center justify-center flex-shrink-0">
                    <Clock className="h-6 w-6 text-orange-600" />
                  </div>
                  <div>
                    <h4 className="text-lg font-semibold text-gray-900 mb-1">Support Hours</h4>
                    <p className="text-gray-600">24/7 Chat & Email Support</p>
                    <p className="text-gray-600">Phone: Mon-Fri 9AM-6PM PST</p>
                  </div>
                </div>
              </div>

              <div className="mt-8 p-6 bg-gradient-to-r from-blue-50 to-purple-50 rounded-lg">
                <h4 className="text-lg font-semibold text-gray-900 mb-2">Enterprise Sales</h4>
                <p className="text-gray-600 mb-4">
                  Need a custom solution for your organization? Our enterprise team can help you with:
                </p>
                <ul className="text-gray-600 space-y-1">
                  <li>• Custom integrations and workflows</li>
                  <li>• Volume pricing and licensing</li>
                  <li>• Dedicated support and training</li>
                  <li>• Security and compliance review</li>
                </ul>
              </div>
            </div>

            {/* Contact Form */}
            <Card className="border-0 shadow-lg">
              <CardHeader>
                <CardTitle className="text-2xl font-bold text-gray-900">
                  Send us a Message
                </CardTitle>
                <CardDescription className="text-gray-600">
                  Fill out the form below and we'll get back to you within 24 hours.
                </CardDescription>
              </CardHeader>
              <CardContent>
                <form className="space-y-6">
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                    <div>
                      <label htmlFor="firstName" className="block text-sm font-medium text-gray-700 mb-1">
                        First Name
                      </label>
                      <input
                        type="text"
                        id="firstName"
                        name="firstName"
                        className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                        required
                      />
                    </div>
                    <div>
                      <label htmlFor="lastName" className="block text-sm font-medium text-gray-700 mb-1">
                        Last Name
                      </label>
                      <input
                        type="text"
                        id="lastName"
                        name="lastName"
                        className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                        required
                      />
                    </div>
                  </div>

                  <div>
                    <label htmlFor="email" className="block text-sm font-medium text-gray-700 mb-1">
                      Email Address
                    </label>
                    <input
                      type="email"
                      id="email"
                      name="email"
                      className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                      required
                    />
                  </div>

                  <div>
                    <label htmlFor="company" className="block text-sm font-medium text-gray-700 mb-1">
                      Company
                    </label>
                    <input
                      type="text"
                      id="company"
                      name="company"
                      className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                    />
                  </div>

                  <div>
                    <label htmlFor="subject" className="block text-sm font-medium text-gray-700 mb-1">
                      Subject
                    </label>
                    <select
                      id="subject"
                      name="subject"
                      className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                      required
                    >
                      <option value="">Select a subject</option>
                      <option value="sales">Sales Inquiry</option>
                      <option value="support">Technical Support</option>
                      <option value="partnership">Partnership</option>
                      <option value="general">General Question</option>
                    </select>
                  </div>

                  <div>
                    <label htmlFor="message" className="block text-sm font-medium text-gray-700 mb-1">
                      Message
                    </label>
                    <textarea
                      id="message"
                      name="message"
                      rows={4}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                      placeholder="Tell us about your needs..."
                      required
                    ></textarea>
                  </div>

                  <Button type="submit" className="w-full bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700">
                    Send Message
                    <ArrowRight className="ml-2 h-4 w-4" />
                  </Button>
                </form>
              </CardContent>
            </Card>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 px-4 sm:px-6 lg:px-8 bg-gradient-to-r from-blue-600 to-purple-600">
        <div className="max-w-4xl mx-auto text-center">
          <h2 className="text-3xl sm:text-4xl font-bold text-white mb-6">
            Ready to Transform Your Sales?
          </h2>
          <p className="text-xl text-blue-100 mb-8 leading-relaxed">
            Join thousands of sales teams who have already boosted their performance with SalesOptimizer.
            Start your free trial today - no credit card required.
          </p>
          
          <div className="flex flex-col sm:flex-row gap-4 justify-center items-center">
            <Link href="/login">
              <Button size="lg" variant="secondary" className="bg-white text-blue-600 hover:bg-gray-100 px-8 py-3 text-lg font-semibold shadow-lg hover:shadow-xl transition-all duration-200">
                Start Free Trial
                <ArrowRight className="ml-2 h-5 w-5" />
              </Button>
            </Link>
            
            <Button variant="outline" size="lg" className="border-white text-blue-600 hover:bg-white hover:text-blue-600 px-8 py-3 text-lg font-semibold transition-all duration-200">
              Contact Sales
            </Button>
          </div>
          
          <p className="text-blue-100 text-sm mt-6">
            Free 14-day trial • No credit card required • Cancel anytime
          </p>
        </div>
      </section>

      <LandingFooter />
    </div>
  )
}