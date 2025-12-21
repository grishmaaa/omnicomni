export default function PrivacyPolicy() {
    return (
        <div className="prose prose-invert max-w-none">
            <h1 className="text-3xl font-bold mb-6 text-gradient">Privacy Policy</h1>

            <h3>1. Information We Collect</h3>
            <p>
                We collect info you provide directly (email, name) and info about your usage of the service (prompts, generation logs).
                We do not store payment card details; these are handled by our secure payment processors.
            </p>

            <h3>2. How We Use Your Information</h3>
            <ul>
                <li>To provide and maintain the Service.</li>
                <li>To process your transactions.</li>
                <li>To communicate with you about updates and support.</li>
                <li>To improve our AI models and user experience.</li>
            </ul>

            <h3>3. Data Security</h3>
            <p>
                We implement industry-standard security measures to protect your personal information.
                However, no method of transmission over the Internet is 100% secure.
            </p>

            <h3>4. Third-Party Services</h3>
            <p>
                We use third-party vendors (e.g., OpenAI, Fal.ai, Vercel, Railway) to provide infrastructure and AI services.
                Data shared with them is limited to what is necessary for the service to function.
            </p>

            <h3>5. Cookies</h3>
            <p>
                We use cookies to maintain your session and preference settings. You can control cookie usage through your browser settings.
            </p>
        </div>
    );
}
