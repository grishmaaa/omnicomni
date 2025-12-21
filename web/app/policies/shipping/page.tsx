export default function ShippingPolicy() {
    return (
        <div className="prose prose-invert max-w-none">
            <h1 className="text-3xl font-bold mb-6 text-gradient">Shipping & Delivery Policy</h1>

            <div className="bg-blue-500/10 border border-blue-500/20 p-4 rounded-lg mb-8 not-prose">
                <p className="text-blue-200">
                    <strong>NOTICE:</strong> This is a digital-only service. No physical products will be shipped to you.
                </p>
            </div>

            <h3>1. Digital Delivery Only</h3>
            <p>
                Technov.ai products are 100% digital. We do not sell or ship physical goods (such as DVDs, hard drives, or merchandise).
                Therefore, there are no shipping fees, shipping addresses, or delivery tracking numbers associated with your purchase.
            </p>

            <h3>2. Immediate Fulfillment</h3>
            <p>
                Upon successful payment:
            </p>
            <ul>
                <li><strong>Subscriptions:</strong> Your account is automatically and instantly upgraded to the paid tier. You gain immediate access to premium features.</li>
                <li><strong>Asset Delivery:</strong> All AI-generated videos and images are delivered digitally via your account dashboard ("My Videos" section).</li>
            </ul>

            <h3>3. Download & Access</h3>
            <p>
                You are responsible for downloading your generated content. While we store your content on our servers for a limited time (as per your plan limits), we recommend downloading your videos immediately after generation.
                We are not responsible for content lost due to failure to download before retention expiration.
            </p>

            <h3>4. No Physical Address Required</h3>
            <p>
                We do not require a shipping address for purchase. Billing addresses are collected solely for payment verification and tax compliance purpose.
            </p>
        </div>
    );
}
