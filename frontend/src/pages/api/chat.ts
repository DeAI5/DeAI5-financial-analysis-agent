import { NextApiRequest, NextApiResponse } from 'next';
import axios, { AxiosError } from 'axios';

export default async function handler(
  req: NextApiRequest,
  res: NextApiResponse
) {
  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  try {
    const { messages } = req.body;

    if (!messages || !Array.isArray(messages)) {
      return res.status(400).json({ error: 'Messages array is required' });
    }

    // Find the last user message
    const userMessages = messages.filter(m => m.role === 'user');
    if (userMessages.length === 0) {
      return res.status(400).json({ error: 'No user messages found' });
    }

    // Use IPv4 explicitly (127.0.0.1 instead of localhost which might resolve to ::1)
    const flaskUrl = process.env.FLASK_API_URL || 'http://127.0.0.1:5000';
    
    console.log(`Attempting to connect to backend at: ${flaskUrl}/api/chat`);
    
    // Forward the messages directly to the Python backend
    try {
      const response = await axios.post(`${flaskUrl}/api/chat`, {
        messages,
      });

      if (response.data && response.data.message) {
        return res.status(200).json({ response: response.data.message });
      } else {
        return res.status(500).json({ 
          error: 'Invalid response from backend',
          details: response.data 
        });
      }
    } catch (error) {
      const axiosError = error as AxiosError;
      console.error("Backend connection error:", axiosError.message);
      // Provide a more helpful error message
      return res.status(503).json({
        error: 'Cannot connect to the backend server',
        message: 'Please make sure the Python backend is running at ' + flaskUrl,
        details: axiosError.message
      });
    }
  } catch (error: unknown) {
    console.error('Error in API route:', error);
    const errorMessage = error instanceof Error ? error.message : 'Unknown error';
    return res.status(500).json({ 
      error: 'An error occurred while processing your request',
      message: errorMessage
    });
  }
} 