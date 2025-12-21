export default function RefundPolicy() {
    return (
        <div className="prose prose-invert max-w-none">
            <h1 className="text-3xl font-bold mb-6 text-gradient">Cancellation & Refund Policy</h1>

            <div className="bg-black border border-red-500/50 p-6 rounded-xl mb-8 not-prose shadow-lg shadow-red-900/20">
                <p className="text-red-400 font-bold text-lg">
                    All purchases are final. We do not offer refunds.
                </p>
            </div>

            <h3>1. Strict No Refund Policy</h3>
            <p>
                Technov.ai operates on a <strong>Strict No Refund Policy</strong>. Due to the high computational costs and immediate costs incurred by us for GPU usage upon content generation,
                we cannot offer refunds for any payments made, including subscription fees, credit packs, or annual plans.
            </p>
            <p>
                By purchasing a subscription or credits, you acknowledge and agree that:
            </p>
            <ul>
                <li>All sales are final.</li>
                <li>You will not receive a refund for partially used billing cycles.</li>
                <li>You will not receive a refund for unused credits.</li>
                <li>Unused credits do not roll over to the next month (unless specified in your plan).</li>
            </ul>

            <h3>2. Subscription Cancellation</h3>
            <p>
                You have the freedom to cancel your subscription at any time.
            </p>
            <ul>
                <li><strong>How to Cancel:</strong> Go to your Dashboard {'>'} Subscription Settings {'>'} Cancel Subscription.</li>
                <li><strong>Effect of Cancellation:</strong> Your subscription will remain active until the end of your current paid billing period. You will not be charged for the next cycle.</li>
                <li><strong>Data Retention:</strong> After cancellation, your account will downgrade to the Free tier. Your generated video storage may be limited according to Free tier policies.</li>
            </ul>

            <h3>3. Exceptional Circumstances</h3>
            <p>
                The only exception to this policy is if a billing error has occurred on our end (e.g., double charge for the same invoice).
                In such cases, please contact <a href="mailto:support@technov.ai">support@technov.ai</a> within 72 hours of the transaction with proof of the duplicate charge.
            </p>

            <h3>4. Dispute Resolution</h3>
            <p>
                By using our service, you agree not to file a chargeback or dispute with your bank or credit card provider for reasons covered by this policy (e.g., "forgot to cancel", "didn't use the service").
                Attempting to file a fraudulent chargeback will result in immediate and permanent termination of your account and ban from our platform.
            </p>
        </div>
    );
}
