"use client";

import Link from "next/link";
import { useState } from "react";

export default function DashboardPage() {
    const [topic, setTopic] = useState("");
    const [style, setStyle] = useState("cinematic");
    const [aspectRatio, setAspectRatio] = useState("16:9");
    const [numScenes, setNumScenes] = useState(5);
    const [generating, setGenerating] = useState(false);
    const [progress, setProgress] = useState(0);
    const [currentStage, setCurrentStage] = useState("");
    const [currentMessage, setCurrentMessage] = useState("");
    const [lastVideoUrl, setLastVideoUrl] = useState<string | null>(null);

    const styles = [
        { id: "cinematic", name: "Cinematic", emoji: "🎬" },
        { id: "anime", name: "Anime", emoji: "🎨" },
        { id: "photorealistic", name: "Photorealistic", emoji: "📸" },
        { id: "cartoon", name: "Cartoon", emoji: "🎪" }
    ];

    const handleGenerate = async () => {
        if (!topic.trim()) {
            alert("Please enter a topic!");
            return;
        }

        setGenerating(true);
        setProgress(0);

        try {
            // Call backend API
            const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'https://web-production-f1795.up.railway.app'}/api/generate`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    topic,
                    style,
                    aspect_ratio: aspectRatio,
                    num_scenes: numScenes
                }),
            });

            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.detail || 'Generation failed');
            }

            const data = await response.json();
            const jobId = data.job_id;

            // Poll for status
            while (true) {
                const statusRes = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'https://web-production-f1795.up.railway.app'}/api/status/${jobId}`);

                if (!statusRes.ok) {
                    // If we get 404, the job might be lost (server restart)
                    if (statusRes.status === 404) {
                        throw new Error("Connection lost. Please try again.");
                    }
                    throw new Error("Failed to get status update");
                }

                const status = await statusRes.json();

                setProgress(status.progress);
                setCurrentStage(status.stage.replace(/_/g, ' ')); // formatting: generating_story -> generating story
                if (status.message) setCurrentMessage(status.message);

                if (status.status === 'completed') {
                    setGenerating(false);
                    setCurrentStage("Complete! 🎉");
                    setLastVideoUrl(status.video_url); // Save URL to state
                    break;
                } else if (status.status === 'failed') {
                    throw new Error(status.error || 'Generation failed');
                }

                // Wait 2 seconds before next poll
                await new Promise(resolve => setTimeout(resolve, 2000));
            }

        } catch (error: any) {
            console.error('Generation error:', error);
            alert(error.message || "Something went wrong sending the request");
            setGenerating(false);
        }
    };

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
                            <div className="glass px-4 py-2 rounded-full">
                                <span className="text-purple-400">Pro Plan</span>
                            </div>
                            <button className="text-white hover:text-purple-400 transition-colors">
                                Logout
                            </button>
                        </div>
                    </div>
                </div>
            </nav>

            <div className="pt-24 px-6 pb-12">
                <div className="container mx-auto max-w-6xl">
                    {/* Header */}
                    <div className="text-center mb-12">
                        <h1 className="text-5xl font-bold mb-4">
                            <span className="text-gradient">Create Your Video</span>
                        </h1>
                        <p className="text-xl text-gray-300">
                            Enter your topic and let AI do the magic ✨
                        </p>
                    </div>

                    <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
                        {/* Main Generation Panel */}
                        <div className="lg:col-span-2 space-y-6">
                            {/* Topic Input */}
                            <div className="glass rounded-2xl p-8">
                                <label className="block text-white font-semibold mb-3 text-lg">
                                    Video Topic
                                </label>
                                <input
                                    type="text"
                                    value={topic}
                                    onChange={(e) => setTopic(e.target.value)}
                                    placeholder="e.g., 'Cyberpunk Tokyo at night' or 'Morning coffee routine'"
                                    className="w-full bg-white/5 border border-white/10 rounded-xl px-6 py-4 text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-purple-500 transition-all"
                                />
                            </div>

                            {/* Style Selection */}
                            <div className="glass rounded-2xl p-8">
                                <label className="block text-white font-semibold mb-4 text-lg">
                                    Visual Style
                                </label>
                                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                                    {styles.map((s) => (
                                        <button
                                            key={s.id}
                                            onClick={() => setStyle(s.id)}
                                            className={`p-4 rounded-xl transition-all ${style === s.id
                                                ? 'bg-gradient-to-r from-purple-500 to-pink-600 scale-105'
                                                : 'bg-white/5 hover:bg-white/10'
                                                }`}
                                        >
                                            <div className="text-3xl mb-2">{s.emoji}</div>
                                            <div className="text-white font-medium">{s.name}</div>
                                        </button>
                                    ))}
                                </div>
                            </div>

                            {/* Settings */}
                            <div className="glass rounded-2xl p-8">
                                <h3 className="text-white font-semibold mb-4 text-lg">
                                    Settings
                                </h3>

                                <div className="space-y-6">
                                    {/* Aspect Ratio */}
                                    <div>
                                        <label className="block text-gray-300 mb-2">
                                            Aspect Ratio
                                        </label>
                                        <select
                                            value={aspectRatio}
                                            onChange={(e) => setAspectRatio(e.target.value)}
                                            className="w-full bg-white/5 border border-white/10 rounded-xl px-4 py-3 text-white focus:outline-none focus:ring-2 focus:ring-purple-500"
                                        >
                                            <option value="16:9">16:9 (YouTube)</option>
                                            <option value="9:16">9:16 (TikTok)</option>
                                            <option value="1:1">1:1 (Instagram)</option>
                                        </select>
                                    </div>

                                    {/* Number of Scenes */}
                                    <div>
                                        <label className="block text-gray-300 mb-2">
                                            Number of Scenes: {numScenes}
                                        </label>
                                        <input
                                            type="range"
                                            min="3"
                                            max="10"
                                            value={numScenes}
                                            onChange={(e) => setNumScenes(parseInt(e.target.value))}
                                            className="w-full accent-purple-500"
                                        />
                                        <div className="flex justify-between text-sm text-gray-500 mt-1">
                                            <span>3</span>
                                            <span>10</span>
                                        </div>
                                    </div>
                                </div>
                            </div>

                            {/* Generate Button */}
                            <button
                                onClick={handleGenerate}
                                disabled={generating}
                                className={`w-full py-6 rounded-2xl font-bold text-xl transition-all ${generating
                                    ? 'bg-gray-600 cursor-not-allowed'
                                    : 'btn-primary'
                                    }`}
                            >
                                {generating ? '⏳ Generating...' : '🚀 Generate Video'}
                            </button>

                            {/* Progress */}
                            {generating && (
                                <div className="glass rounded-2xl p-8">
                                    <div className="mb-4">
                                        <div className="flex justify-between text-white mb-2">
                                            <span>{currentStage}</span>
                                            <span>{Math.round(progress)}%</span>
                                        </div>
                                        <div className="w-full bg-white/10 rounded-full h-3 overflow-hidden">
                                            <div
                                                className="h-full bg-gradient-to-r from-purple-500 to-pink-600 transition-all duration-500 animate-glow"
                                                style={{ width: `${progress}%` }}
                                            />
                                        </div>
                                    </div>
                                    <p className="text-gray-400 text-sm animate-pulse">
                                        👉 {currentMessage || "Contacting AI servers..."}
                                    </p>
                                </div>
                            )}

                            {/* Result Video Player */}
                            {lastVideoUrl && !generating && (
                                <div className="glass rounded-2xl p-8 animate-in fade-in slide-in-from-bottom-4 duration-700">
                                    <h3 className="text-white font-bold text-2xl mb-6 flex items-center gap-3">
                                        🎉 Your Video is Ready!
                                    </h3>

                                    <div className="relative rounded-xl overflow-hidden shadow-2xl border border-white/10 bg-black aspect-video mb-6">
                                        <video
                                            controls
                                            autoPlay
                                            className="w-full h-full object-contain"
                                            src={`${process.env.NEXT_PUBLIC_API_URL || 'https://web-production-f1795.up.railway.app'}${lastVideoUrl}`}
                                        />
                                    </div>

                                    <div className="flex gap-4">
                                        <a
                                            href={`${process.env.NEXT_PUBLIC_API_URL || 'https://web-production-f1795.up.railway.app'}${lastVideoUrl}`}
                                            download={`technov_video_${Date.now()}.mp4`}
                                            className="flex-1 btn-primary py-4 rounded-xl font-bold text-center flex items-center justify-center gap-2 hover:scale-[1.02] transition-transform"
                                            target="_blank"
                                            rel="noopener noreferrer"
                                        >
                                            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
                                            </svg>
                                            Download Video
                                        </a>
                                        <button
                                            onClick={() => {
                                                setLastVideoUrl(null);
                                                setTopic("");
                                            }}
                                            className="px-6 py-4 rounded-xl font-semibold bg-white/5 hover:bg-white/10 text-white transition-colors border border-white/10"
                                        >
                                            Create Another
                                        </button>
                                    </div>
                                </div>
                            )}
                        </div>

                        {/* Sidebar */}
                        <div className="space-y-6">
                            {/* Usage Stats */}
                            <div className="glass rounded-2xl p-6">
                                <h3 className="text-white font-semibold mb-4 text-lg">
                                    📊 Usage This Month
                                </h3>
                                <div className="space-y-4">
                                    <div>
                                        <div className="flex justify-between text-sm text-gray-400 mb-1">
                                            <span>Videos Generated</span>
                                            <span>45 / 70</span>
                                        </div>
                                        <div className="w-full bg-white/10 rounded-full h-2">
                                            <div className="h-full bg-gradient-to-r from-purple-500 to-pink-600 rounded-full" style={{ width: '64%' }} />
                                        </div>
                                    </div>
                                    <div>
                                        <div className="flex justify-between text-sm text-gray-400 mb-1">
                                            <span>HD Quality</span>
                                            <span>12 / 25</span>
                                        </div>
                                        <div className="w-full bg-white/10 rounded-full h-2">
                                            <div className="h-full bg-gradient-to-r from-blue-500 to-cyan-600 rounded-full" style={{ width: '48%' }} />
                                        </div>
                                    </div>
                                </div>
                            </div>

                            {/* Legal & Support */}
                            <div className="glass rounded-2xl p-6">
                                <h3 className="text-white font-semibold mb-4 text-lg">
                                    ⚖️ Legal & Support
                                </h3>
                                <div className="space-y-3 text-sm">
                                    <Link href="/policies/terms" className="block text-gray-400 hover:text-white transition-colors">
                                        📄 Terms & Conditions
                                    </Link>
                                    <Link href="/policies/privacy" className="block text-gray-400 hover:text-white transition-colors">
                                        🔒 Privacy Policy
                                    </Link>
                                    <Link href="/policies/refund" className="block text-gray-400 hover:text-white transition-colors">
                                        💸 Refund Policy
                                    </Link>
                                    <Link href="/policies/shipping" className="block text-gray-400 hover:text-white transition-colors">
                                        📦 Delivery Policy
                                    </Link>
                                    <Link href="/policies/contact" className="block text-gray-400 hover:text-white transition-colors">
                                        📧 Contact Support
                                    </Link>
                                </div>
                            </div>

                            {/* Cost Estimate */}
                            <div className="glass rounded-2xl p-6">
                                <h3 className="text-white font-semibold mb-4 text-lg">
                                    💰 Estimated Cost
                                </h3>
                                <div className="text-4xl font-bold text-gradient mb-2">
                                    $2.50
                                </div>
                                <p className="text-gray-400 text-sm">
                                    Based on {numScenes} scenes with {style} style
                                </p>
                            </div>

                            {/* Quick Tips */}
                            <div className="glass rounded-2xl p-6">
                                <h3 className="text-white font-semibold mb-4 text-lg">
                                    💡 Quick Tips
                                </h3>
                                <ul className="space-y-2 text-sm text-gray-300">
                                    <li>• Be specific with your topic</li>
                                    <li>• Choose the right aspect ratio for your platform</li>
                                    <li>• More scenes = longer video</li>
                                    <li>• HD quality uses more quota</li>
                                </ul>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}
