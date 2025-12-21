import { NextRequest, NextResponse } from 'next/server';

export async function POST(request: NextRequest) {
    try {
        const body = await request.json();
        const { email, password } = body;

        // Validate input
        if (!email || !password) {
            return NextResponse.json(
                { error: 'Email and password are required' },
                { status: 400 }
            );
        }

        // Call your Python backend for authentication
        const pythonBackendUrl = process.env.PYTHON_BACKEND_URL || 'http://localhost:8000';

        const response = await fetch(`${pythonBackendUrl}/api/auth/login`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ email, password }),
        });

        if (!response.ok) {
            const error = await response.json();
            return NextResponse.json(
                { error: error.detail || error.message || 'Authentication failed' },
                { status: response.status }
            );
        }

        const data = await response.json();

        // Set session cookie
        const res = NextResponse.json({
            success: true,
            user: data.user,
            subscription: data.subscription,
        });

        res.cookies.set('session', data.session_token, {
            httpOnly: true,
            secure: process.env.NODE_ENV === 'production',
            sameSite: 'lax',
            maxAge: 60 * 60 * 24 * 7, // 7 days
        });

        return res;

    } catch (error) {
        console.error('Login error:', error);
        return NextResponse.json(
            { error: 'Authentication failed' },
            { status: 500 }
        );
    }
}
