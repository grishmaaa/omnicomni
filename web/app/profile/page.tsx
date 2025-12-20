"use client";

import Link from "next/link";
import { useState, useEffect } from "react";

export default function ProfilePage() {
    const [user, setUser] = useState<any>(null);
    const [subscription, setSubscription] = useState<any>(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        // Load user data from localStorage
        const userData = localStorage.getItem("user");
        const subData = localStorage.getItem("subscription");

        if (userData) setUser(JSON.parse(userData));
        if (subData) setSubscription(JSON.parse(subData));

        setLoading(false);
    }, []);

    if (loading) {
        return (
            <div className="min-h-screen flex items-center justify-center">
                <div className="animate-spin rounded-full h-12 w-12 border-4 border-purple-500 border-t-transparent"></div>
            </div>
        );
    }

    return (
        <div className="min-h-screen">
            {/* Navigation */}
            <nav className="fixed top-0 left-0 right-0 z-50 glass">
                <div className="container mx-auto px-6 py-4">
                    <div className="flex items-center justify-between">
                        <Link href="/" className="text-2xl font-bold text-gradient">
                            🎬 AI Video Generator
                        </Link>
                        <div className="flex gap-4 items-center">
                            <Link href="/dashboard" className="text-white hover:text-purple-400 transition-colors">
                                Dashboard
                            </Link>
                            <Link href="/videos" className="text-white hover:text-purple-400 transition-colors">
                                My Videos
                            </Link>
                            <Link href="/profile" className="text-purple-400 font-semibold">
                                Profile
                            </Link>
                            <button className="text-white hover:text-purple-400 transition-colors">
                                Logout
                            </button>
                        </div>
                    </div>
                </div>
            </nav>

            <div className="pt-24 px-6 pb-12">
                <div className="container mx-auto max-w-4xl">
                    {/* Header */}
                    <div className="mb-12">
                        <h1 className="text-5xl font-bold mb-4">
                            <span className="text-gradient">Profile Settings</span>
                        </h1>
                        <p className="text-xl text-gray-300">
                            Manage your account and subscription
                        </p>
                    </div>

                    <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
                        {/* Profile Info */}
                        <div className="lg:col-span-2 space-y-6">
                            {/* Account Details */}
                            <div className="glass rounded-2xl p-8">
                                <h2 className="text-2xl font-bold text-white mb-6">
                                    Account Details
                                </h2>

                                <div className="space-y-4">
                                    <div>
                                        <label className="block text-gray-400 mb-2">Full Name</label>
                                        <input
                                            type="text"
                                            value={user?.name || ""}
                                            className="w-full bg-white/5 border border-white/10 rounded-xl px-4 py-3 text-white"
                                        />
                                    </div>

                                    <div>
                                        <label className="block text-gray-400 mb-2">Email</label>
                                        <input
                                            type="email"
                                            value={user?.email || ""}
                                            disabled
                                            className="w-full bg-white/5 border border-white/10 rounded-xl px-4 py-3 text-gray-500"
                                        />
                                    </div>

                                    <button className="btn-primary">
                                        Save Changes
                                    </button>
                                </div>
                            </div>

                            {/* Change Password */}
                            <div className="glass rounded-2xl p-8">
                                <h2 className="text-2xl font-bold text-white mb-6">
                                    Change Password
                                </h2>

                                <div className="space-y-4">
                                    <div>
                                        <label className="block text-gray-400 mb-2">Current Password</label>
                                        <input
                                            type="password"
                                            className="w-full bg-white/5 border border-white/10 rounded-xl px-4 py-3 text-white"
                                        />
                                    </div>

                                    <div>
                                        <label className="block text-gray-400 mb-2">New Password</label>
                                        <input
                                            type="password"
                                            className="w-full bg-white/5 border border-white/10 rounded-xl px-4 py-3 text-white"
                                        />
                                    </div>

                                    <div>
                                        <label className="block text-gray-400 mb-2">Confirm New Password</label>
                                        <input
                                            type="password"
                                            className="w-full bg-white/5 border border-white/10 rounded-xl px-4 py-3 text-white"
                                        />
                                    </div>

                                    <button className="btn-secondary">
                                        Update Password
                                    </button>
                                </div>
                            </div>
                        </div>

                        {/* Sidebar */}
                        <div className="space-y-6">
                            {/* Subscription Card */}
                            <div className="glass rounded-2xl p-6">
                                <h3 className="text-xl font-bold text-white mb-4">
                                    Current Plan
                                </h3>

                                <div className="mb-4">
                                    <div className="text-3xl font-bold text-gradient mb-2">
                                        {subscription?.tier?.charAt(0).toUpperCase() + subscription?.tier?.slice(1) || "Free"}
                                    </div>
                                    <div className="text-gray-400 text-sm">
                                        {subscription?.status || "Active"}
                                    </div>
                                </div>

                                <Link href="/pricing" className="btn-primary block text-center">
                                    Upgrade Plan
                                </Link>
                            </div>

                            {/* Usage Stats */}
                            <div className="glass rounded-2xl p-6">
                                <h3 className="text-xl font-bold text-white mb-4">
                                    This Month
                                </h3>

                                <div className="space-y-4">
                                    <div>
                                        <div className="flex justify-between text-sm text-gray-400 mb-2">
                                            <span>Videos</span>
                                            <span>45 / 70</span>
                                        </div>
                                        <div className="w-full bg-white/10 rounded-full h-2">
                                            <div className="h-full bg-gradient-to-r from-purple-500 to-pink-600 rounded-full" style={{ width: '64%' }} />
                                        </div>
                                    </div>

                                    <div>
                                        <div className="flex justify-between text-sm text-gray-400 mb-2">
                                            <span>Storage</span>
                                            <span>2.4 GB / 10 GB</span>
                                        </div>
                                        <div className="w-full bg-white/10 rounded-full h-2">
                                            <div className="h-full bg-gradient-to-r from-blue-500 to-cyan-600 rounded-full" style={{ width: '24%' }} />
                                        </div>
                                    </div>
                                </div>
                            </div>

                            {/* Danger Zone */}
                            <div className="glass rounded-2xl p-6 border-2 border-red-500/20">
                                <h3 className="text-xl font-bold text-red-400 mb-4">
                                    Danger Zone
                                </h3>

                                <button className="w-full bg-red-500/10 hover:bg-red-500/20 border border-red-500/50 text-red-400 py-3 rounded-xl font-medium transition-all">
                                    Delete Account
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}
