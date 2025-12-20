import { NextRequest, NextResponse } from 'next/server';

export async function POST(request: NextRequest) {
    try {
        const body = await request.json();
        const { topic, style, aspectRatio, numScenes } = body;

        // Validate input
        if (!topic || !topic.trim()) {
            return NextResponse.json(
                { error: 'Topic is required' },
                { status: 400 }
            );
        }

        // Call your Python backend
        // For now, we'll return a mock response
        // Replace this with actual API call to your Python service
        const pythonBackendUrl = process.env.PYTHON_BACKEND_URL || 'http://localhost:8000';

        const response = await fetch(`${pythonBackendUrl}/api/generate`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                topic,
                style: style || 'cinematic',
                aspect_ratio: aspectRatio || '16:9',
                num_scenes: numScenes || 5,
            }),
        });

        if (!response.ok) {
            throw new Error('Failed to generate video');
        }

        const data = await response.json();

        return NextResponse.json({
            success: true,
            jobId: data.job_id,
            message: 'Video generation started',
        });

    } catch (error) {
        console.error('Error generating video:', error);
        return NextResponse.json(
            { error: 'Failed to generate video' },
            { status: 500 }
        );
    }
}

export async function GET(request: NextRequest) {
    try {
        const searchParams = request.nextUrl.searchParams;
        const jobId = searchParams.get('jobId');

        if (!jobId) {
            return NextResponse.json(
                { error: 'Job ID is required' },
                { status: 400 }
            );
        }

        // Check job status from Python backend
        const pythonBackendUrl = process.env.PYTHON_BACKEND_URL || 'http://localhost:8000';

        const response = await fetch(`${pythonBackendUrl}/api/status/${jobId}`);

        if (!response.ok) {
            throw new Error('Failed to get job status');
        }

        const data = await response.json();

        return NextResponse.json(data);

    } catch (error) {
        console.error('Error checking status:', error);
        return NextResponse.json(
            { error: 'Failed to check status' },
            { status: 500 }
        );
    }
}
