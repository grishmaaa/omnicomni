"use client";

import Link from "next/link";
import { useState } from "react";

const tiers = [
    {
        id: "starter",
        name: "Starter",
        price: 500,
        popular: false,
        features: [
            "35 video generations per month",
            "30 standard quality videos",
            "5 HD quality videos",
            "Email support"
        ]
    },
    {
        id: "pro",
        name: "Professional",
        price: 700,
        popular: true,
        features: [
            "70 video generations per month",
            "45 standard quality videos",
            "25 HD quality videos",
            "Priority support"
        ]
    },
    {
        id: "elite",
        name: "Elite",
        price: 1100,
        popular: false,
        features: [
            "100 video generations per month",
            "All HD quality",
            "Anytime support",
            "Premium features"
        ]
    }
];

const faqs = [
    {
        question: "Can I change my plan later?",
        answer: "Yes! You can upgrade or downgrade your plan at any time. Changes take effect immediately."
    },
    {
        question: "What happens if I exceed my limit?",
        answer: "You'll be prompted to upgrade to continue generating videos. Your existing videos remain accessible."
    },
    {
        question: "Do you offer refunds?",
        answer: "NO REFUNDS - All sales are final. Payment is required before use. Please review plans carefully before subscribing."
    },
    {
        question: "Can I cancel anytime?",
        answer: "Yes, you can cancel your subscription at any time. You'll retain access until the end of your billing period."
    },
    {
        question: "What payment methods do you accept?",
        answer: "We accept all major credit cards, debit cards, UPI, and Net Banking through Razorpay."
    },
    {
        question: "Is there a free trial for paid plans?",
        answer: "Start with the Free plan to test the platform. Upgrade when you're ready for more features."
    }
];

export default function PricingPage() {
    const [openFaq, setOpenFaq] = useState<number | null>(null);

    return (
        <div className="min-h-screen">
            {/* Navigation */}
            <nav className="fixed top-0 left-0 right-0 z-50 glass">
                <div className="container mx-auto px-6 py-4">
                    <div className="flex items-center justify-between">
                        <Link href="/" className="text-2xl font-bold text-gradient">
                            🎬 AI Video Generator
                        </Link>
                        <div className="flex gap-4">
                            <Link href="/" className="text-white hover:text-purple-400 transition-colors">
                                Home
                            </Link>
                            <Link href="/login" className="text-white hover:text-purple-400 transition-colors">
                                Login
                            </Link>
                            <Link href="/signup" className="btn-primary">
                                Get Started
                            </Link>
                        </div>
                    </div>
                </div>
            </nav>

            {/* Header */}
            <section className="pt-32 pb-12 px-6">
                <div className="container mx-auto text-center">
                    <h1 className="text-6xl font-bold mb-6">
                        <span className="text-gradient">Choose Your Plan</span>
                    </h1>
                    <p className="text-xl text-gray-300 max-w-2xl mx-auto">
                        Start free, upgrade when you need more
                    </p>
                </div>
            </section>

            {/* Pricing Cards */}
            <section className="py-12 px-6">
                <div className="container mx-auto">
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-8 max-w-6xl mx-auto">
                        {tiers.map((tier) => (
                            <div
                                key={tier.id}
                                className={`glass rounded-3xl p-8 card-hover relative ${tier.popular ? 'ring-2 ring-purple-500 scale-105' : ''
                                    }`}
                            >
                                {tier.popular && (
                                    <div className="absolute -top-4 left-1/2 transform -translate-x-1/2">
                                        <span className="bg-gradient-to-r from-purple-500 to-pink-600 text-white px-6 py-2 rounded-full text-sm font-bold">
                                            MOST POPULAR
                                        </span>
                                    </div>
                                )}

                                <div className="text-center mb-8">
                                    <h3 className="text-3xl font-bold text-white mb-4">
                                        {tier.name}
                                    </h3>
                                    <div className="text-5xl font-bold text-gradient mb-2">
                                        ${tier.price}
                                    </div>
                                    <div className="text-gray-400">per month</div>
                                </div>

                                <ul className="space-y-4 mb-8">
                                    {tier.features.map((feature, index) => (
                                        <li key={index} className="flex items-start gap-3">
                                            <span className="text-green-400 text-xl">✓</span>
                                            <span className="text-gray-300">{feature}</span>
                                        </li>
                                    ))}
                                </ul>

                                <Link
                                    href={`/signup?plan=${tier.id}`}
                                    className={`block text-center py-4 rounded-full font-semibold transition-all duration-300 ${tier.popular
                                            ? 'btn-primary'
                                            : 'glass glass-hover text-white'
                                        }`}
                                >
                                    Subscribe to {tier.name}
                                </Link>
                            </div>
                        ))}
                    </div>
                </div>
            </section>

            {/* FAQ Section */}
            <section className="py-20 px-6">
                <div className="container mx-auto max-w-4xl">
                    <h2 className="text-5xl font-bold text-center mb-16">
                        <span className="text-gradient">Frequently Asked Questions</span>
                    </h2>

                    <div className="space-y-4">
                        {faqs.map((faq, index) => (
                            <div key={index} className="glass rounded-2xl overflow-hidden">
                                <button
                                    onClick={() => setOpenFaq(openFaq === index ? null : index)}
                                    className="w-full px-8 py-6 text-left flex items-center justify-between hover:bg-white/5 transition-colors"
                                >
                                    <span className="text-xl font-semibold text-white">
                                        ❓ {faq.question}
                                    </span>
                                    <span className={`text-2xl transition-transform ${openFaq === index ? 'rotate-180' : ''
                                        }`}>
                                        ↓
                                    </span>
                                </button>
                                {openFaq === index && (
                                    <div className="px-8 pb-6 text-gray-300">
                                        {faq.answer}
                                    </div>
                                )}
                            </div>
                        ))}
                    </div>
                </div>
            </section>

            {/* Back Button */}
            <section className="py-12 px-6">
                <div className="container mx-auto text-center">
                    <Link href="/" className="btn-secondary inline-block">
                        ← Back to Home
                    </Link>
                </div>
            </section>

            {/* Footer */}
            <footer className="py-12 px-6 border-t border-white/10">
                <div className="container mx-auto">
                    <div className="grid grid-cols-2 md:grid-cols-5 gap-8 mb-8">
                        <Link href="/pricing" className="text-gray-400 hover:text-white transition-colors">
                            Pricing
                        </Link>
                        <Link href="/about" className="text-gray-400 hover:text-white transition-colors">
                            About
                        </Link>
                        <Link href="/terms" className="text-gray-400 hover:text-white transition-colors">
                            Terms
                        </Link>
                        <Link href="/privacy" className="text-gray-400 hover:text-white transition-colors">
                            Privacy
                        </Link>
                        <Link href="/contact" className="text-gray-400 hover:text-white transition-colors">
                            Contact
                        </Link>
                    </div>
                    <div className="text-center text-gray-500">
                        © 2025 AI Video Generator. All rights reserved.
                    </div>
                </div>
            </footer>
        </div>
    );
}
