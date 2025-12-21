export default function ContactPage() {
    return (
        <div className="prose prose-invert max-w-none">
            <h1 className="text-3xl font-bold mb-6 text-gradient">Contact Us</h1>

            <p className="text-lg mb-8">
                We are here to help! If you have any questions, issues, or feedback about Technov.ai, please reach out to us.
            </p>

            <div className="grid gap-8 md:grid-cols-2 not-prose mb-12">
                <div className="bg-white/5 p-6 rounded-xl border border-white/10">
                    <h3 className="text-xl font-semibold mb-2">📧 Email Support</h3>
                    <p className="text-gray-400 mb-4">For general inquiries and technical support</p>
                    <a href="mailto:support@technov.ai" className="text-purple-400 hover:text-purple-300 font-medium">
                        support@technov.ai
                    </a>
                </div>

                <div className="bg-white/5 p-6 rounded-xl border border-white/10">
                    <h3 className="text-xl font-semibold mb-2">🏢 Registered Office</h3>
                    <p className="text-gray-400">
                        Technov AI Solutions<br />
                        Sector 4, HSR Layout<br />
                        Bengaluru, Karnataka, 560102<br />
                        India
                    </p>
                </div>
            </div>

            <h3>Response Time</h3>
            <p>
                We aim to respond to all support tickets within 24 hours during business days (Mon-Fri).
                Priority support is available for Pro and Elite plan members.
            </p>
        </div>
    );
}
