"use client";

import Link from "next/link";
import { useState, Suspense } from "react";
import { useRouter, useSearchParams } from "next/navigation";

function SignupForm() {
    const router = useRouter();
    const searchParams = useSearchParams();
    const selectedPlan = searchParams.get("plan") || "free";

    const [name, setName] = useState("");
    const [email, setEmail] = useState("");
    const [password, setPassword] = useState("");
    const [confirmPassword, setConfirmPassword] = useState("");
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState("");
    const [agreedToTerms, setAgreedToTerms] = useState(false);

    const handleSignup = async (e: React.FormEvent) => {
        e.preventDefault();
        setError("");

        // Validation
        if (password !== confirmPassword) {
            setError("Passwords don't match");
            return;
        }

        if (password.length < 8) {
            setError("Password must be at least 8 characters");
            return;
        }

        if (!agreedToTerms) {
            setError("Please agree to the Terms of Service");
            return;
        }

        setLoading(true);

        try {
            const response = await fetch("/api/auth/signup", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ name, email, password, plan: selectedPlan }),
            });

            const data = await response.json();

            if (response.ok) {
                // Redirect to login or dashboard
                if (selectedPlan !== "free") {
                    // Redirect to payment
                    router.push(`/payment?plan=${selectedPlan}`);
                } else {
                    router.push("/login");
                }
            } else {
                setError(data.error || "Signup failed");
            }
        } catch (err) {
            setError("Network error. Please try again.");
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="min-h-screen flex items-center justify-center px-6 py-12">
            {/* Background */}
            <div className="absolute inset-0 gradient-mesh opacity-50" />

            {/* Signup Card */}
            <div className="relative z-10 w-full max-w-md">
                <div className="glass rounded-3xl p-8 md:p-12">
                    {/* Logo */}
                    <div className="text-center mb-8">
                        <Link href="/" className="text-3xl font-bold text-gradient">
                            🎬 AI Video Generator
                        </Link>
                        <h2 className="text-2xl font-bold text-white mt-6 mb-2">
                            Create Your Account
                        </h2>
                        <p className="text-gray-400">
                            Start creating amazing videos today
                        </p>
                    </div>

                    {/* Selected Plan Badge */}
                    {selectedPlan !== "free" && (
                        <div className="mb-6 p-4 bg-purple-500/10 border border-purple-500/50 rounded-xl text-center">
                            <p className="text-purple-400 font-semibold">
                                Selected Plan: {selectedPlan.charAt(0).toUpperCase() + selectedPlan.slice(1)}
                            </p>
                        </div>
                    )}

                    {/* Error Message */}
                    {error && (
                        <div className="mb-6 p-4 bg-red-500/10 border border-red-500/50 rounded-xl text-red-400 text-sm">
                            {error}
                        </div>
                    )}

                    {/* Signup Form */}
                    <form onSubmit={handleSignup} className="space-y-5">
                        <div>
                            <label className="block text-white font-medium mb-2">
                                Full Name
                            </label>
                            <input
                                type="text"
                                value={name}
                                onChange={(e) => setName(e.target.value)}
                                placeholder="John Doe"
                                required
                                className="w-full bg-white/5 border border-white/10 rounded-xl px-4 py-3 text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-purple-500 transition-all"
                            />
                        </div>

                        <div>
                            <label className="block text-white font-medium mb-2">
                                Email Address
                            </label>
                            <input
                                type="email"
                                value={email}
                                onChange={(e) => setEmail(e.target.value)}
                                placeholder="you@example.com"
                                required
                                className="w-full bg-white/5 border border-white/10 rounded-xl px-4 py-3 text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-purple-500 transition-all"
                            />
                        </div>

                        <div>
                            <label className="block text-white font-medium mb-2">
                                Password
                            </label>
                            <input
                                type="password"
                                value={password}
                                onChange={(e) => setPassword(e.target.value)}
                                placeholder="••••••••"
                                required
                                minLength={8}
                                className="w-full bg-white/5 border border-white/10 rounded-xl px-4 py-3 text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-purple-500 transition-all"
                            />
                            <p className="mt-1 text-xs text-gray-500">
                                Must be at least 8 characters
                            </p>
                        </div>

                        <div>
                            <label className="block text-white font-medium mb-2">
                                Confirm Password
                            </label>
                            <input
                                type="password"
                                value={confirmPassword}
                                onChange={(e) => setConfirmPassword(e.target.value)}
                                placeholder="••••••••"
                                required
                                className="w-full bg-white/5 border border-white/10 rounded-xl px-4 py-3 text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-purple-500 transition-all"
                            />
                        </div>

                        <div className="flex items-start">
                            <input
                                type="checkbox"
                                checked={agreedToTerms}
                                onChange={(e) => setAgreedToTerms(e.target.checked)}
                                className="mt-1 mr-3 accent-purple-500"
                            />
                            <label className="text-sm text-gray-400">
                                I agree to the{" "}
                                <Link href="/terms" className="text-purple-400 hover:text-purple-300">
                                    Terms of Service
                                </Link>{" "}
                                and{" "}
                                <Link href="/privacy" className="text-purple-400 hover:text-purple-300">
                                    Privacy Policy
                                </Link>
                            </label>
                        </div>

                        <button
                            type="submit"
                            disabled={loading}
                            className={`w-full py-4 rounded-xl font-semibold text-lg transition-all ${loading
                                ? "bg-gray-600 cursor-not-allowed"
                                : "btn-primary"
                                }`}
                        >
                            {loading ? "Creating account..." : "Create Account"}
                        </button>
                    </form>

                    {/* Divider */}
                    <div className="my-8 flex items-center">
                        <div className="flex-1 border-t border-white/10" />
                        <span className="px-4 text-gray-500 text-sm">OR</span>
                        <div className="flex-1 border-t border-white/10" />
                    </div>

                    {/* Social Signup */}
                    <div className="space-y-3">
                        <button className="w-full glass glass-hover py-3 rounded-xl font-medium text-white flex items-center justify-center gap-3">
                            <svg className="w-5 h-5" viewBox="0 0 24 24" fill="currentColor">
                                <path d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z" fill="#4285F4" />
                                <path d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" fill="#34A853" />
                                <path d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z" fill="#FBBC05" />
                                <path d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z" fill="#EA4335" />
                            </svg>
                            Continue with Google
                        </button>
                    </div>

                    {/* Login Link */}
                    <div className="mt-8 text-center text-gray-400">
                        Already have an account?{" "}
                        <Link href="/login" className="text-purple-400 hover:text-purple-300 font-semibold transition-colors">
                            Sign in
                        </Link>
                    </div>
                </div>

                {/* Back to Home */}
                <div className="mt-6 text-center">
                    <Link href="/" className="text-gray-400 hover:text-white transition-colors">
                        ← Back to Home
                    </Link>
                </div>
            </div>
        </div>
    );
}

export default function SignupPage() {
    return (
        <Suspense fallback={<div className="min-h-screen flex items-center justify-center"><div className="animate-spin rounded-full h-12 w-12 border-4 border-purple-500 border-t-transparent"></div></div>}>
            <SignupForm />
        </Suspense>
    );
}
