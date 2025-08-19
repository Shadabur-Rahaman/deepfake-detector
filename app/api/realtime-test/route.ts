import { NextRequest, NextResponse } from 'next/server';

export async function POST(request: NextRequest) {
  try {
    const formData = await request.formData();
    const file = formData.get('file') as File;
    
    if (!file) {
      return NextResponse.json({ error: 'No file provided' }, { status: 400 });
    }

    // Forward to your Python backend
    const backendFormData = new FormData();
    backendFormData.append('file', file);

    const response = await fetch('http://localhost:8000/detect-realtime-image', {
      method: 'POST',
      body: backendFormData,
    });

    const result = await response.json();
    return NextResponse.json(result);

  } catch (error: any) {
    return NextResponse.json(
      { error: 'Real-time detection failed', details: error.message },
      { status: 500 }
    );
  }
}
