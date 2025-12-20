import { NextRequest, NextResponse } from 'next/server';

export async function GET(request: NextRequest) {
    try {
        // Get user from session (you'll need to implement session management)
        // For now, we'll use a mock user ID
        const userId = 1; // TODO: Get from session

        // Call Python backend
        const pythonBackendUrl = process.env.PYTHON_BACKEND_URL || 'http://localhost:8000';

        const response = await fetch(`${pythonBackendUrl}/api/videos?userId=${userId}`);

        if (!response.ok) {
            throw new Error('Failed to fetch videos');
        }

        const data = await response.json();

        return NextResponse.json(data);

    } catch (error) {
        console.error('Error fetching videos:', error);
        return NextResponse.json(
            { error: 'Failed to fetch videos' },
            { status: 500 }
        );
    }
}

export async function DELETE(request: NextRequest) {
    try {
        const { videoId } = await request.json();

        if (!videoId) {
            return NextResponse.json(
                { error: 'Video ID is required' },
                { status: 400 }
            );
        }

        // Call Python backend to delete video
        const pythonBackendUrl = process.env.PYTHON_BACKEND_URL || 'http://localhost:8000';

        const response = await fetch(`${pythonBackendUrl}/api/videos/${videoId}`, {
            method: 'DELETE',
        });

        if (!response.ok) {
            throw new Error('Failed to delete video');
        }

        return NextResponse.json({ success: true });

    } catch (error) {
        console.error('Error deleting video:', error);
        return NextResponse.json(
            { error: 'Failed to delete video' },
            { status: 500 }
        );
    }
}
