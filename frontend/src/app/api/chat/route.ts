import { NextRequest, NextResponse } from 'next/server';

// Function to retry fetching with exponential backoff
async function fetchWithRetry(url: string, options: RequestInit, maxRetries = 3) {
  let retries = 0;
  
  while (retries < maxRetries) {
    try {
      console.log(`Attempting to connect to backend at: ${url}`);
      const response = await fetch(url, options);
      if (response.ok) return response;
      
      // If response is not ok, wait and retry
      const status = response.status;
      console.log(`Backend responded with status: ${status}, retrying (${retries + 1}/${maxRetries})...`);
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : String(error);
      console.log(`Backend connection failed: ${errorMessage}, retrying (${retries + 1}/${maxRetries})...`);
    }
    
    // Exponential backoff with some randomness
    const delay = Math.min(1000 * 2 ** retries, 10000) + Math.random() * 1000;
    await new Promise(resolve => setTimeout(resolve, delay));
    retries++;
  }
  
  throw new Error('Failed to connect to backend after several retries');
}

export async function POST(request: NextRequest) {
  try {
    const { messages } = await request.json();
    
    if (!messages || !Array.isArray(messages)) {
      return NextResponse.json(
        { error: 'Invalid request. Messages array is required.' },
        { status: 400 }
      );
    }

    // Extract the last user message
    const userMessage = messages.filter(m => m.role === 'user').pop();
    
    if (!userMessage) {
      return NextResponse.json(
        { error: 'No user message found.' },
        { status: 400 }
      );
    }

    // Filter out system messages and prepare conversation history
    const conversationHistory = messages
      .filter(m => m.role !== 'system')
      .map(m => ({ role: m.role, content: m.content }));

    try {
      // Make a request to the Python backend with retry logic
      const response = await fetchWithRetry('http://localhost:5000/api/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message: userMessage.content,
          history: conversationHistory,
        }),
      });

      const data = await response.json();

      return NextResponse.json({
        message: data.message || data.response,
      });
    } catch (backendError) {
      console.error('Error connecting to backend:', backendError);
      
      // Return a fallback response that the backend is not available
      return NextResponse.json({
        message: "I'm sorry, but the financial analysis backend is currently unavailable. Please make sure the backend server is running at http://localhost:5000 and try again later.",
      });
    }
  } catch (error) {
    console.error('Error processing chat request:', error);
    return NextResponse.json(
      { error: 'An error occurred while processing your request.' },
      { status: 500 }
    );
  }
} 