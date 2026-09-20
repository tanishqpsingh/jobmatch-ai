"use client";

import React, { useState } from "react";
import { apiFetch } from "@/lib/api";

export interface UserProfile {
  id: number;
  email: string;
  created_at?: string;
}

interface AuthModalProps {
  isOpen: boolean;
  onClose: () => void;
  onAuthSuccess: (user: UserProfile) => void;
}

export default function AuthModal({ isOpen, onClose, onAuthSuccess }: AuthModalProps) {
  const [isLoginMode, setIsLoginMode] = useState<boolean>(true);
  const [email, setEmail] = useState<string>("");
  const [password, setPassword] = useState<string>("");
  const [confirmPassword, setConfirmPassword] = useState<string>("");
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  if (!isOpen) return null;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);

    if (!email.trim() || !password.trim()) {
      setError("Email and password are required.");
      return;
    }

    if (!isLoginMode && password !== confirmPassword) {
      setError("Passwords do not match.");
      return;
    }

    if (password.length < 8) {
      setError("Password must be at least 8 characters.");
      return;
    }

    setIsLoading(true);

    try {
      if (!isLoginMode) {
        // 1. Register
        const registerRes = await apiFetch("/api/v1/auth/register", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ email: email.trim(), password }),
        });

        if (!registerRes.ok) {
          const errData = await registerRes.json().catch(() => null);
          throw new Error(errData?.detail || `Registration failed (${registerRes.status})`);
        }
      }

      // 2. Login (sets HttpOnly cookies)
      const formBody = new URLSearchParams();
      formBody.append("username", email.trim());
      formBody.append("password", password);

      const loginRes = await apiFetch("/api/v1/auth/login", {
        method: "POST",
        headers: {
          "Content-Type": "application/x-www-form-urlencoded",
        },
        body: formBody.toString(),
      });

      if (!loginRes.ok) {
        const errData = await loginRes.json().catch(() => null);
        throw new Error(errData?.detail || `Login failed (${loginRes.status})`);
      }

      // 3. Fetch authenticated profile
      const meRes = await apiFetch("/api/v1/auth/me");

      if (meRes.ok) {
        const user: UserProfile = await meRes.json();
        onAuthSuccess(user);
        onClose();
      } else {
        throw new Error("Failed to retrieve profile after sign-in.");
      }
    } catch (err: any) {
      setError(err.message || "An authentication error occurred.");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/70 backdrop-blur-sm animate-in fade-in duration-200">
      <div className="bg-slate-900 border border-slate-800 rounded-2xl max-w-md w-full p-6 sm:p-8 shadow-2xl relative space-y-6">
        {/* Close Button */}
        <button
          onClick={onClose}
          className="absolute top-5 right-5 text-slate-400 hover:text-white text-xl transition"
          aria-label="Close"
        >
          ✕
        </button>

        {/* Modal Header */}
        <div className="text-center space-y-2">
          <div className="inline-flex w-10 h-10 rounded-xl bg-gradient-to-tr from-indigo-600 to-purple-600 items-center justify-center text-white font-bold shadow-md shadow-indigo-500/20 mb-1">
            JM
          </div>
          <h2 className="text-2xl font-bold tracking-tight text-white">
            {isLoginMode ? "Sign in to JobMatch AI" : "Create an Account"}
          </h2>
          <p className="text-xs text-slate-400">
            {isLoginMode
              ? "Access your isolated job application pipeline"
              : "Register a private account to track applications securely"}
          </p>
        </div>

        {/* Mode Toggle */}
        <div className="flex p-1 bg-slate-950 rounded-xl border border-slate-800 text-xs font-semibold">
          <button
            type="button"
            onClick={() => {
              setIsLoginMode(true);
              setError(null);
            }}
            className={`flex-1 py-2 rounded-lg transition ${
              isLoginMode
                ? "bg-indigo-600 text-white shadow-sm"
                : "text-slate-400 hover:text-white"
            }`}
          >
            Sign In
          </button>
          <button
            type="button"
            onClick={() => {
              setIsLoginMode(false);
              setError(null);
            }}
            className={`flex-1 py-2 rounded-lg transition ${
              !isLoginMode
                ? "bg-indigo-600 text-white shadow-sm"
                : "text-slate-400 hover:text-white"
            }`}
          >
            Register
          </button>
        </div>

        {/* Error Alert */}
        {error && (
          <div className="p-3.5 rounded-xl bg-rose-500/10 border border-rose-500/30 text-rose-300 text-xs flex items-center space-x-2">
            <span>⚠️</span>
            <span>{error}</span>
          </div>
        )}

        {/* Auth Form */}
        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="space-y-1.5">
            <label className="text-xs font-medium text-slate-300">Email Address</label>
            <input
              type="email"
              required
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="candidate@example.com"
              className="w-full px-3.5 py-2.5 rounded-xl bg-slate-950 border border-slate-800 text-slate-100 text-sm focus:outline-none focus:border-indigo-500 transition placeholder:text-slate-600"
            />
          </div>

          <div className="space-y-1.5">
            <label className="text-xs font-medium text-slate-300">Password</label>
            <input
              type="password"
              required
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="••••••••"
              className="w-full px-3.5 py-2.5 rounded-xl bg-slate-950 border border-slate-800 text-slate-100 text-sm focus:outline-none focus:border-indigo-500 transition placeholder:text-slate-600"
            />
          </div>

          {!isLoginMode && (
            <div className="space-y-1.5">
              <label className="text-xs font-medium text-slate-300">Confirm Password</label>
              <input
                type="password"
                required
                value={confirmPassword}
                onChange={(e) => setConfirmPassword(e.target.value)}
                placeholder="••••••••"
                className="w-full px-3.5 py-2.5 rounded-xl bg-slate-950 border border-slate-800 text-slate-100 text-sm focus:outline-none focus:border-indigo-500 transition placeholder:text-slate-600"
              />
            </div>
          )}

          <button
            type="submit"
            disabled={isLoading}
            className="w-full py-2.5 px-4 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white font-semibold text-sm shadow-lg shadow-indigo-600/30 transition disabled:opacity-50 flex items-center justify-center space-x-2"
          >
            {isLoading ? (
              <>
                <span className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                <span>{isLoginMode ? "Signing In..." : "Creating Account..."}</span>
              </>
            ) : (
              <span>{isLoginMode ? "Sign In" : "Create Account"}</span>
            )}
          </button>
        </form>

        <p className="text-center text-[11px] text-slate-500">
          Protected by Argon2 & HttpOnly token authentication.
        </p>
      </div>
    </div>
  );
}
