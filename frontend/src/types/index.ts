// Define the message types for chat
export interface Message {
  id?: string;
  role: 'user' | 'assistant' | 'system';
  content: string;
  timestamp?: Date;
}

export interface Conversation {
  id: string;
  title: string;
  messages: Message[];
  createdAt: Date;
  updatedAt: Date;
}

// Define cryptocurrency types
export interface CryptoCurrency {
  symbol: string;
  name: string;
  price: number;
  change24h: number;
  marketCap: number;
  volume24h: number;
  supply: number;
  recommendation?: string;
  technicalAnalysis?: {
    recommendation: string;
    buy: number;
    sell: number;
    neutral: number;
  };
}

export interface CryptoPrice {
  symbol: string;
  price: number;
  change_24h: number;
  market_cap: number;
  volume_24h: number;
}

export interface CryptoRecommendation {
  symbol: string;
  name?: string;
  recommendation: string;
  confidence_score: number;
  technical_score?: number;
  risk_level: string;
  risk_tolerance: string;
  current_price: {
    price: number;
    currency: string;
  };
  market_metrics?: {
    market_cap: number;
    volume_24h: number;
    volume_to_mcap_ratio: number;
    market_dominance?: number;
  };
  percent_changes?: {
    '1h'?: number;
    '24h'?: number;
    '7d'?: number;
    '30d'?: number;
    '60d'?: number | null;
    '90d'?: number | null;
  };
  potential_upside?: number;
  potential_downside?: number;
  investment_thesis: string;
  risks: string;
  timestamp?: string;
  disclaimer?: string;
}

// Define API response types
export interface ApiResponse<T> {
  success: boolean;
  data?: T;
  error?: string;
}

export interface ChatResponse {
  response: string;
  conversationHistory: Message[];
}

export interface CryptoResponse {
  data: CryptoPrice;
  error?: string;
}

export interface RecommendationResponse {
  data: CryptoRecommendation;
  error?: string;
} 