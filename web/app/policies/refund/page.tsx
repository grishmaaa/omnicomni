export default function RefundPolicy() {
    return (
        <div className="prose prose-invert max-w-none">
            <h1 className="text-3xl font-bold mb-6 text-gradient">Cancellation & Refund Policy</h1>

            <h3>1. Subscription Cancellation</h3>
            <p>
                You may cancel your Technov.ai subscription at any time from your account dashboard.
                Upon cancellation, your subscription will remain active until the end of the current billing period.
                You will not be charged for the next billing cycle.
            </p>

            <h3>2. Refunds</h3>
            <p>
                <strong>Monthly Subscriptions:</strong> Due to the high cost of GPU computing resources used to generate AI videos,
                we generally do not offer refunds for partial months or unused credits once a subscription cycle has started.
            </p>
            <p>
                <strong>Exceptions:</strong> If you experienced a technical failure where the service did not deliver the generated content
                as promised (e.g., system errors, failed generation), please contact support within 7 days of the incident for a full or partial refund.
            </p>

            <h3>3. Annual Plans</h3>
            <p>
                For annual subscriptions, you may request a refund within 7 days of the initial purchase if you haven't used more than
                5 generation credits. After this period, cancellations will only stop the auto-renewal for the next year.
            </p>

            <h3>4. Processing Time</h3>
            <p>
                Approved refunds are processed within 5-7 business days and will be returned to the original payment method used.
            </p>
        </div>
    );
}
