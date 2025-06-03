"use client"

import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle } from "@/components/ui/dialog"
import { Alert, AlertDescription } from "@/components/ui/alert"
import { Icons } from "@/components/ui/icons"
import { Check } from "lucide-react"
import { invitationService } from '@/features/admin/services/invitation-service'

interface SubscriptionTier {
  value: string
  label: string
}

const subscriptionTiers: SubscriptionTier[] = [
  { value: "basic", label: "Basic" },
  { value: "pro", label: "Pro" },
  { value: "enterprise", label: "Enterprise" }
]

interface InviteOrgAdminModalProps {
  open: boolean
  onOpenChange: (open: boolean) => void
}

export function InviteOrgAdminModal({ open, onOpenChange }: InviteOrgAdminModalProps) {
  const [formData, setFormData] = useState({
    email: "",
    organization_name: "",
    subscription_tier: "basic",
    slug: ""
  })
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState("")
  const [success, setSuccess] = useState(false)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setIsLoading(true)
    setError("")

    try {
      await invitationService.createOrgAdminInvitation(formData)
      setSuccess(true)
      // Reset form after success
      setTimeout(() => {
        setFormData({
          email: "",
          organization_name: "",
          subscription_tier: "basic",
          slug: ""
        })
        setSuccess(false)
        onOpenChange(false)
      }, 2000)
    } catch (err: any) {
      setError(err.message || "Failed to send invitation")
    } finally {
      setIsLoading(false)
    }
  }

  const handleInputChange = (field: string, value: string) => {
    setFormData(prev => ({ ...prev, [field]: value }))
    
    // Auto-generate slug from organization name
    if (field === "organization_name" && value && !formData.slug) {
      const autoSlug = value
        .toLowerCase()
        .replace(/[^a-z0-9\s-]/g, '')
        .replace(/\s+/g, '-')
        .replace(/-+/g, '-')
        .trim()
      setFormData(prev => ({ ...prev, slug: autoSlug }))
    }
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-[425px]">
        <DialogHeader>
          <DialogTitle>Invite Organization Administrator</DialogTitle>
          <DialogDescription>
            Create a new organization and invite an administrator to manage it.
          </DialogDescription>
        </DialogHeader>

        {success ? (
          <Alert className="border-green-200 bg-green-50">
            <Check className="h-4 w-4 text-green-600" />
            <AlertDescription className="text-green-800">
              Invitation sent successfully! The organization admin will receive an email with setup instructions.
            </AlertDescription>
          </Alert>
        ) : (
          <form onSubmit={handleSubmit} className="space-y-4">
            {error && (
              <Alert variant="destructive">
                <AlertDescription>{error}</AlertDescription>
              </Alert>
            )}

            <div className="space-y-2">
              <Label htmlFor="email">Admin Email *</Label>
              <Input
                id="email"
                type="email"
                placeholder="admin@company.com"
                value={formData.email}
                onChange={(e) => handleInputChange("email", e.target.value)}
                required
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="organization_name">Organization Name *</Label>
              <Input
                id="organization_name"
                placeholder="Acme Corporation"
                value={formData.organization_name}
                onChange={(e) => handleInputChange("organization_name", e.target.value)}
                required
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="slug">Organization Slug</Label>
              <Input
                id="slug"
                placeholder="acme-corporation"
                value={formData.slug}
                onChange={(e) => handleInputChange("slug", e.target.value)}
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="subscription_tier">Subscription Tier</Label>
              <Select value={formData.subscription_tier} onValueChange={(value: string) => handleInputChange("subscription_tier", value)}>
                <SelectTrigger>
                  <SelectValue placeholder="Select subscription tier" />
                </SelectTrigger>
                <SelectContent>
                  {subscriptionTiers.map((tier: SubscriptionTier) => (
                    <SelectItem key={tier.value} value={tier.value}>
                      {tier.label}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            <DialogFooter>
              <Button
                type="button"
                variant="outline"
                onClick={() => onOpenChange(false)}
                disabled={isLoading}
              >
                Cancel
              </Button>
              <Button type="submit" disabled={isLoading}>
                {isLoading && <Icons.spinner className="mr-2 h-4 w-4 animate-spin" />}
                Send Invitation
              </Button>
            </DialogFooter>
          </form>
        )}
      </DialogContent>
    </Dialog>
  )
}