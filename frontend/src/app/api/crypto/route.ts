import { NextRequest, NextResponse } from 'next/server';
import axios from 'axios';

// Set the backend URL from environment variable or fallback to localhost
const BACKEND_URL = process.env.BACKEND_URL || 'http://localhost:5000';

export async function GET(request: NextRequest) {
  try {
    const searchParams = request.nextUrl.searchParams;
    const symbol = searchParams.get('symbol');
    
    if (!symbol) {
      return NextResponse.json(
        { error: 'Cryptocurrency symbol is required' },
        { status: 400 }
      );
    }

    try {
      // Make request to the Python backend
      const response = await axios.get(`${BACKEND_URL}/api/crypto`, {
        params: { symbol }
      });

      return NextResponse.json(response.data);
    } catch (error) {
      console.error('Error calling backend:', error);
      
      // For development purposes, return mock data
      return NextResponse.json({
        symbol,
        price: 42000.00,
        change_24h: 2.5,
        market_cap: 800000000000,
        volume_24h: 30000000000,
        mock: true
      });
    }
  } catch (error) {
    console.error('API route error:', error);
    return NextResponse.json(
      { error: 'Failed to process request' },
      { status: 500 }
    );
  }
}

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const { symbol, action, risk_tolerance } = body;
    
    if (!symbol) {
      return NextResponse.json(
        { error: 'Cryptocurrency symbol is required' },
        { status: 400 }
      );
    }

    try {
      // Make request to the Python backend
      const response = await axios.post(`${BACKEND_URL}/api/crypto/recommendation`, {
        symbol,
        action: action || 'analyze',
        risk_tolerance: risk_tolerance || 'moderate'
      });

      return NextResponse.json(response.data);
    } catch (error) {
      console.error('Error calling backend:', error);
      
      // For development purposes, return mock recommendation
      return NextResponse.json({
        symbol,
        recommendation: 'Hold',
        confidence_score: 65,
        price: 42000.00,
        potential_upside: 15,
        potential_downside: 10,
        risk_level: 'Moderate',
        investment_thesis: `This is a mock investment thesis for ${symbol}.`,
        mock: true
      });
    }
  } catch (error) {
    console.error('API route error:', error);
    return NextResponse.json(
      { error: 'Failed to process request' },
      { status: 500 }
    );
  }
} 