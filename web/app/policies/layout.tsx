export default function PoliciesLayout({
    children,
}: {
    children: React.ReactNode;
}) {
    return (
        <div className="min-h-screen gradient-mesh text-white selection:bg-purple-500/30">
            <nav className="fixed top-0 left-0 right-0 z-50 glass border-b border-white/5">
                <div className="container mx-auto px-6 py-4">
                    <div className="flex items-center justify-between">
                        <a href="/" className="text-xl font-bold text-gradient">
                            🎬 Technov.ai
                        </a>
                        <a href="/" className="text-sm text-gray-400 hover:text-white transition-colors">
                            ← Back to Home
                        </a>
                    </div>
                </div>
            </nav>

            <main className="pt-24 pb-12 px-6">
                <div className="container mx-auto max-w-4xl">
                    <div className="glass rounded-2xl p-8 md:p-12">
                        {children}
                    </div>
                </div>
            </main>
        </div>
    );
}
