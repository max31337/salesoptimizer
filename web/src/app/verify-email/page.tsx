"use client";

import React, { useEffect } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { Loader2, CheckCircle, XCircle } from "lucide-react";

export default function VerifyEmailPage() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const [status, setStatus] = React.useState<"pending" | "success" | "fail" | "already_verified" | "expired">("pending");

  useEffect(() => {
    const token = searchParams.get("token");
    const statusParam = searchParams.get("status");
    const username = searchParams.get("username");

    async function performVerification(verificationToken: string) {
      try {
        // When this is called, it will redirect the browser to the backend,
        // which in turn redirects back to this page with status and username params.
        const url = `/organizations/verify-email?token=${encodeURIComponent(verificationToken)}`;
        const fullUrl = `${process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000"}/api/v1${url}`;
        window.location.href = fullUrl;
      } catch (error) {
        console.error("Verification request failed:", error);
        setStatus("fail");
      }
    }

    if (statusParam) {
      // This branch handles the page load after being redirected from the backend.
      if (statusParam === "success") {
        setStatus("success");
      } else if (statusParam === "already_verified") {
        setStatus("already_verified");
      } else if (statusParam === "expired") {
        setStatus("expired");
      } else {
        setStatus("fail");
      }

      // After showing the status for 2 seconds, redirect to the login page.
      setTimeout(() => {
        const redirectUrl =
          statusParam === "fail"
            ? "/login?verified=fail"
            : `/login?verified=${statusParam}&username=${encodeURIComponent(username || "")}`;
        router.push(redirectUrl);
      }, 2000);
    } else if (token) {
      // This branch handles the initial page load from the user's email link.
      performVerification(token);
    } else {
      // If there's no token and no status, it's an invalid state.
      setStatus("fail");
    }
  }, [searchParams, router]);

  return (
    <div className="min-h-screen flex flex-col items-center justify-center bg-background px-4">
      {status === "pending" && (
        <div className="flex flex-col items-center gap-4">
          <Loader2 className="h-10 w-10 animate-spin text-blue-600" />
          <p className="text-lg font-semibold text-muted-foreground">Verifying your email...</p>
        </div>
      )}
      {status === "success" && (
        <div className="flex flex-col items-center gap-4">
          <CheckCircle className="h-10 w-10 text-green-600" />
          <p className="text-lg font-semibold text-green-700">Email verified!</p>
          <p className="text-muted-foreground">Redirecting to login...</p>
        </div>
      )}
      {status === "already_verified" && (
        <div className="flex flex-col items-center gap-4">
          <CheckCircle className="h-10 w-10 text-blue-600" />
          <p className="text-lg font-semibold text-blue-700">Email already verified</p>
          <p className="text-muted-foreground">Redirecting to login...</p>
        </div>
      )}
      {status === "expired" && (
        <div className="flex flex-col items-center gap-4">
          <XCircle className="h-10 w-10 text-orange-600" />
          <p className="text-lg font-semibold text-orange-700">Verification link expired</p>
          <p className="text-muted-foreground text-center">
            Your verification link has expired. Please request a new verification email.
          </p>
          <p className="text-muted-foreground">Redirecting to login...</p>
        </div>
      )}
      {status === "fail" && (
        <div className="flex flex-col items-center gap-4">
          <XCircle className="h-10 w-10 text-red-600" />
          <p className="text-lg font-semibold text-red-700">Verification failed</p>
          <p className="text-muted-foreground text-center">
            The verification link is invalid or has been used already.
          </p>
          <p className="text-muted-foreground">Redirecting to login...</p>
        </div>
      )}
    </div>
  );
}