"use client";

import Link from "next/link";
import { useState } from "react";

export default function Home() {
  const [hoveredFeature, setHoveredFeature] = useState<number | null>(null);

  const features = [
    {
      icon: "🤖",
      title: "AI-Powered",
      description: "Advanced AI generates scripts, images, and narration automatically"
    },
    {
      icon: "⚡",
      title: "Lightning Fast",
      description: "Create professional videos in minutes, not hours"
    },
    {
      icon: "🎨",
      title: "Customizable",
      description: "Choose styles, themes, and customize every aspect"
    },
    {
      icon: "📚",
      title: "Video Library",
      description: "Access all your videos anytime, anywhere"
    },
    {
      icon: "🔒",
      title: "Secure & Private",
      description: "Your data is encrypted and never shared"
    },
    {
      icon: "💾",
      title: "Easy Download",
      description: "Download videos in high quality instantly"
    }
  ];

  const stats = [
    { number: "10K+", label: "Videos Created" },
    { number: "5K+", label: "Happy Users" },
    { number: "99%", label: "Satisfaction Rate" }
  ];

  const steps = [
    {
      number: "1",
      title: "Enter Your Topic",
      description: "Simply describe what you want your video to be about"
    },
    {
      number: "2",
      title: "AI Does the Magic",
      description: "Our AI generates script, images, videos, and narration"
    },
    {
      number: "3",
      title: "Download & Share",
      description: "Get your professional video ready to share anywhere"
    }
  ];

  return (
    <div className="min-h-screen">
      {/* Navigation */}
      <nav className="fixed top-0 left-0 right-0 z-50 glass">
        <div className="container mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="text-2xl font-bold text-gradient">
              🎬 AI Video Generator
            </div>
            <div className="flex gap-4">
              <Link href="/pricing" className="text-white hover:text-purple-400 transition-colors">
                Pricing
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

      {/* Hero Section */}
      <section className="pt-32 pb-20 px-6">
        <div className="container mx-auto text-center">
          <div className="animate-float">
            <h1 className="text-6xl md:text-8xl font-bold mb-6">
              <span className="text-gradient">Transform Ideas</span>
              <br />
              <span className="text-white">Into Stunning Videos</span>
            </h1>
          </div>

          <p className="text-xl md:text-2xl text-gray-300 mb-12 max-w-3xl mx-auto">
            Powered by cutting-edge AI technology. No video editing skills required.
            Create professional videos in minutes.
          </p>

          <div className="flex gap-4 justify-center flex-wrap">
            <Link href="/signup" className="btn-primary">
              🚀 Get Started Free
            </Link>
            <Link href="/pricing" className="btn-secondary">
              View Pricing
            </Link>
          </div>

          {/* Stats */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8 mt-20 max-w-4xl mx-auto">
            {stats.map((stat, index) => (
              <div key={index} className="glass rounded-2xl p-8 card-hover">
                <div className="text-5xl font-bold text-gradient mb-2">
                  {stat.number}
                </div>
                <div className="text-gray-400">
                  {stat.label}
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-20 px-6">
        <div className="container mx-auto">
          <h2 className="text-5xl font-bold text-center mb-16">
            <span className="text-gradient">Powerful Features</span>
          </h2>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            {features.map((feature, index) => (
              <div
                key={index}
                className="glass rounded-2xl p-8 card-hover cursor-pointer"
                onMouseEnter={() => setHoveredFeature(index)}
                onMouseLeave={() => setHoveredFeature(null)}
              >
                <div className={`text-6xl mb-4 transition-transform duration-300 ${hoveredFeature === index ? 'scale-125' : 'scale-100'
                  }`}>
                  {feature.icon}
                </div>
                <h3 className="text-2xl font-bold text-white mb-3">
                  {feature.title}
                </h3>
                <p className="text-gray-400">
                  {feature.description}
                </p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* How It Works */}
      <section className="py-20 px-6">
        <div className="container mx-auto max-w-4xl">
          <h2 className="text-5xl font-bold text-center mb-16">
            <span className="text-gradient">How It Works</span>
          </h2>

          <div className="space-y-8">
            {steps.map((step, index) => (
              <div key={index} className="glass rounded-2xl p-8 flex items-center gap-6 card-hover">
                <div className="text-6xl font-bold text-gradient min-w-[80px]">
                  {step.number}
                </div>
                <div>
                  <h3 className="text-2xl font-bold text-white mb-2">
                    {step.title}
                  </h3>
                  <p className="text-gray-400">
                    {step.description}
                  </p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 px-6">
        <div className="container mx-auto text-center">
          <div className="glass rounded-3xl p-16 max-w-4xl mx-auto">
            <h2 className="text-5xl font-bold mb-6">
              <span className="text-gradient">Ready to Create Amazing Videos?</span>
            </h2>
            <p className="text-xl text-gray-300 mb-8">
              Join thousands of creators already using AI Video Generator Pro
            </p>
            <Link href="/signup" className="btn-primary inline-block">
              🎬 Start Creating Now
            </Link>
          </div>
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
