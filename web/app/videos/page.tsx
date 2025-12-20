"use client";

import Link from "next/link";
import { useState, useEffect } from "react";

interface Video {
    id: string;
    topic: string;
    thumbnail: string;
    duration: number;
    created_at: string;
    file_path: string;
}

export default function VideosPage() {
    const [videos, setVideos] = useState<Video[]>([]);
    const [loading, setLoading] = useState(true);
    const [filter, setFilter] = useState("all");

    useEffect(() => {
        // Fetch user's videos
        fetchVideos();
    }, []);

    const fetchVideos = async () => {
        try {
            const response = await fetch("/api/videos");
            const data = await response.json();
            setVideos(data.videos || []);
        } catch (error) {
            console.error("Failed to fetch videos:", error);
        } finally {
            setLoading(false);
        }
    };

    const formatDate = (dateString: string) => {
        const date = new Date(dateString);
        return date.toLocaleDateString("en-US", {
            month: "short",
            day: "numeric",
            year: "numeric",
        });
    };

    const formatDuration = (seconds: number) => {
        const mins = Math.floor(seconds / 60);
        const secs = seconds % 60;
        return `${mins}:${secs.toString().padStart(2, "0")}`;
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
                            <Link href="/videos" className="text-purple-400 font-semibold">
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
                <div className="container mx-auto max-w-7xl">
                    {/* Header */}
                    <div className="mb-12">
                        <h1 className="text-5xl font-bold mb-4">
                            <span className="text-gradient">My Videos</span>
                        </h1>
                        <p className="text-xl text-gray-300">
                            All your AI-generated videos in one place
                        </p>
                    </div>

                    {/* Filters */}
                    <div className="flex gap-4 mb-8">
                        <button
                            onClick={() => setFilter("all")}
                            className={`px-6 py-3 rounded-xl font-medium transition-all ${filter === "all"
                                    ? "bg-gradient-to-r from-purple-500 to-pink-600 text-white"
                                    : "glass glass-hover text-gray-300"
                                }`}
                        >
                            All Videos
                        </button>
                        <button
                            onClick={() => setFilter("recent")}
                            className={`px-6 py-3 rounded-xl font-medium transition-all ${filter === "recent"
                                    ? "bg-gradient-to-r from-purple-500 to-pink-600 text-white"
                                    : "glass glass-hover text-gray-300"
                                }`}
                        >
                            Recent
                        </button>
                        <button
                            onClick={() => setFilter("favorites")}
                            className={`px-6 py-3 rounded-xl font-medium transition-all ${filter === "favorites"
                                    ? "bg-gradient-to-r from-purple-500 to-pink-600 text-white"
                                    : "glass glass-hover text-gray-300"
                                }`}
                        >
                            Favorites
                        </button>
                    </div>

                    {/* Videos Grid */}
                    {loading ? (
                        <div className="text-center py-20">
                            <div className="inline-block animate-spin rounded-full h-12 w-12 border-4 border-purple-500 border-t-transparent"></div>
                            <p className="text-gray-400 mt-4">Loading your videos...</p>
                        </div>
                    ) : videos.length === 0 ? (
                        <div className="text-center py-20">
                            <div className="glass rounded-3xl p-12 max-w-2xl mx-auto">
                                <div className="text-6xl mb-4">🎬</div>
                                <h3 className="text-2xl font-bold text-white mb-4">
                                    No videos yet
                                </h3>
                                <p className="text-gray-400 mb-8">
                                    Create your first AI-generated video to get started!
                                </p>
                                <Link href="/dashboard" className="btn-primary inline-block">
                                    Create Your First Video
                                </Link>
                            </div>
                        </div>
                    ) : (
                        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                            {videos.map((video) => (
                                <div key={video.id} className="glass rounded-2xl overflow-hidden card-hover group">
                                    {/* Thumbnail */}
                                    <div className="relative aspect-video bg-gradient-to-br from-purple-500/20 to-pink-500/20">
                                        {video.thumbnail ? (
                                            <img
                                                src={video.thumbnail}
                                                alt={video.topic}
                                                className="w-full h-full object-cover"
                                            />
                                        ) : (
                                            <div className="w-full h-full flex items-center justify-center">
                                                <span className="text-6xl">🎬</span>
                                            </div>
                                        )}

                                        {/* Play Button Overlay */}
                                        <div className="absolute inset-0 bg-black/50 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center">
                                            <button className="w-16 h-16 bg-white rounded-full flex items-center justify-center transform group-hover:scale-110 transition-transform">
                                                <svg className="w-8 h-8 text-purple-600 ml-1" fill="currentColor" viewBox="0 0 24 24">
                                                    <path d="M8 5v14l11-7z" />
                                                </svg>
                                            </button>
                                        </div>

                                        {/* Duration Badge */}
                                        <div className="absolute bottom-2 right-2 bg-black/80 px-2 py-1 rounded text-white text-sm">
                                            {formatDuration(video.duration)}
                                        </div>
                                    </div>

                                    {/* Video Info */}
                                    <div className="p-4">
                                        <h3 className="text-white font-semibold mb-2 line-clamp-2">
                                            {video.topic}
                                        </h3>
                                        <p className="text-gray-400 text-sm mb-4">
                                            {formatDate(video.created_at)}
                                        </p>

                                        {/* Actions */}
                                        <div className="flex gap-2">
                                            <button className="flex-1 glass glass-hover py-2 rounded-lg text-white text-sm font-medium">
                                                Download
                                            </button>
                                            <button className="flex-1 glass glass-hover py-2 rounded-lg text-white text-sm font-medium">
                                                Share
                                            </button>
                                            <button className="glass glass-hover p-2 rounded-lg text-white">
                                                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 12h.01M12 12h.01M19 12h.01M6 12a1 1 0 11-2 0 1 1 0 012 0zm7 0a1 1 0 11-2 0 1 1 0 012 0zm7 0a1 1 0 11-2 0 1 1 0 012 0z" />
                                                </svg>
                                            </button>
                                        </div>
                                    </div>
                                </div>
                            ))}
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
}
