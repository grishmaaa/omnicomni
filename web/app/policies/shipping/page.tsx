export default function ShippingPolicy() {
    return (
        <div className="prose prose-invert max-w-none">
            <h1 className="text-3xl font-bold mb-6 text-gradient">Shipping & Delivery Policy</h1>

            <div className="bg-blue-500/10 border border-blue-500/20 p-4 rounded-lg mb-8 not-prose">
                <p className="text-blue-200">
                    <strong>Note:</strong> Technov.ai provides purely digital products and services. No physical goods are shipped.
                </p>
            </div>

            <h3>1. Service Delivery</h3>
            <p>
                Upon successful payment for a subscription or credit pack:
            </p>
            <ul>
                <li><strong>Instant Access:</strong> Your account will be immediately upgraded, and generation credits will be available for use instantly.</li>
                <li><strong>Digital Content:</strong> All videos generated on the platform are delivered digitally. You can download them directly from your dashboard or "My Videos" page.</li>
            </ul>

            <h3>2. Timeline</h3>
            <p>
                Video generation times vary based on complexity, but typically range from 2 to 5 minutes per video.
                Once generated, the file is available for immediate download.
            </p>

            <h3>3. Global Availability</h3>
            <p>
                Our services are available globally to anyone with an internet connection, subject to local laws and regulations.
            </p>
        </div>
    );
}
