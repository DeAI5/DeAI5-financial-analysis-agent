'use client';

import React, { createContext, useContext, useState, ReactNode, useEffect } from 'react';
import { v4 as uuidv4 } from 'uuid';
import { Conversation, Message, CryptoRecommendation, CryptoPrice } from '@/types';

interface AppContextType {
  conversations: Conversation[];
  currentConversationId: string | null;
  isLoading: boolean;
  cryptoData: Map<string, CryptoPrice>;
  cryptoRecommendations: Map<string, CryptoRecommendation>;
  errorMessage: string | null;
  createNewConversation: () => string;
  selectConversation: (id: string) => void;
  addMessage: (content: string, role: 'user' | 'assistant' | 'system') => void;
  sendMessage: (message: string) => Promise<void>;
  fetchCryptoData: (symbol: string) => Promise<CryptoPrice | null>;
  getCryptoRecommendation: (symbol: string, riskTolerance: string) => Promise<CryptoRecommendation | null>;
  clearError: () => void;
}

const AppContext = createContext<AppContextType | undefined>(undefined);

export const AppProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [currentConversationId, setCurrentConversationId] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [cryptoData, setCryptoData] = useState<Map<string, CryptoPrice>>(new Map());
  const [cryptoRecommendations, setCryptoRecommendations] = useState<Map<string, CryptoRecommendation>>(new Map());
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  // Load conversations from local storage on initial render
  useEffect(() => {
    const savedConversations = localStorage.getItem('conversations');
    if (savedConversations) {
      try {
        const parsed = JSON.parse(savedConversations);
        // Convert date strings back to Date objects
        const conversationsWithDates = parsed.map((conv: any) => ({
          ...conv,
          createdAt: new Date(conv.createdAt),
          updatedAt: new Date(conv.updatedAt)
        }));
        setConversations(conversationsWithDates);
      } catch (error) {
        console.error('Failed to parse conversations from localStorage:', error);
      }
    }

    const savedCurrentId = localStorage.getItem('currentConversationId');
    if (savedCurrentId) {
      setCurrentConversationId(savedCurrentId);
    }
  }, []);

  // Save conversations to local storage whenever they change
  useEffect(() => {
    if (conversations.length > 0) {
      localStorage.setItem('conversations', JSON.stringify(conversations));
    }
    if (currentConversationId) {
      localStorage.setItem('currentConversationId', currentConversationId);
    }
  }, [conversations, currentConversationId]);

  const createNewConversation = () => {
    const id = uuidv4();
    const newConversation: Conversation = {
      id,
      title: 'New Conversation',
      messages: [],
      createdAt: new Date(),
      updatedAt: new Date(),
    };
    
    setConversations(prev => [...prev, newConversation]);
    setCurrentConversationId(id);
    return id;
  };

  const selectConversation = (id: string) => {
    setCurrentConversationId(id);
  };

  const addMessage = (content: string, role: 'user' | 'assistant' | 'system') => {
    if (!currentConversationId) return;
    
    const message: Message = { role, content };
    
    setConversations(prev => prev.map(conv => {
      if (conv.id === currentConversationId) {
        return {
          ...conv,
          messages: [...conv.messages, message],
          updatedAt: new Date(),
          title: role === 'user' && conv.messages.length === 0 ? content.substring(0, 30) + (content.length > 30 ? '...' : '') : conv.title
        };
      }
      return conv;
    }));
  };

  const sendMessage = async (message: string) => {
    if (!currentConversationId) {
      createNewConversation();
    }
    
    addMessage(message, 'user');
    setIsLoading(true);
    setErrorMessage(null);
    
    try {
      const currentConversation = conversations.find(c => c.id === currentConversationId);
      if (!currentConversation) throw new Error('Conversation not found');
      
      const response = await fetch('/api/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message,
          history: currentConversation.messages,
        }),
      });
      
      if (!response.ok) {
        throw new Error('Failed to get response from AI');
      }
      
      const data = await response.json();
      addMessage(data.response, 'assistant');
    } catch (error) {
      console.error('Error sending message:', error);
      setErrorMessage(error instanceof Error ? error.message : 'An unknown error occurred');
    } finally {
      setIsLoading(false);
    }
  };

  const fetchCryptoData = async (symbol: string): Promise<CryptoPrice | null> => {
    try {
      const response = await fetch(`/api/crypto?symbol=${symbol}`);
      if (!response.ok) {
        throw new Error('Failed to fetch crypto data');
      }
      
      const data = await response.json();
      if (data.error) {
        throw new Error(data.error);
      }
      
      setCryptoData(prev => new Map(prev).set(symbol.toUpperCase(), data.data));
      return data.data;
    } catch (error) {
      console.error('Error fetching crypto data:', error);
      setErrorMessage(error instanceof Error ? error.message : 'Failed to fetch cryptocurrency data');
      return null;
    }
  };

  const getCryptoRecommendation = async (symbol: string, riskTolerance: string): Promise<CryptoRecommendation | null> => {
    try {
      const response = await fetch('/api/crypto', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          symbol,
          action: 'recommend',
          risk_tolerance: riskTolerance,
        }),
      });
      
      if (!response.ok) {
        throw new Error('Failed to get recommendation');
      }
      
      const data = await response.json();
      if (data.error) {
        throw new Error(data.error);
      }
      
      setCryptoRecommendations(prev => new Map(prev).set(symbol.toUpperCase(), data.data));
      return data.data;
    } catch (error) {
      console.error('Error getting crypto recommendation:', error);
      setErrorMessage(error instanceof Error ? error.message : 'Failed to get recommendation');
      return null;
    }
  };

  const clearError = () => {
    setErrorMessage(null);
  };

  return (
    <AppContext.Provider
      value={{
        conversations,
        currentConversationId,
        isLoading,
        cryptoData,
        cryptoRecommendations,
        errorMessage,
        createNewConversation,
        selectConversation,
        addMessage,
        sendMessage,
        fetchCryptoData,
        getCryptoRecommendation,
        clearError,
      }}
    >
      {children}
    </AppContext.Provider>
  );
};

export const useAppContext = () => {
  const context = useContext(AppContext);
  if (context === undefined) {
    throw new Error('useAppContext must be used within an AppProvider');
  }
  return context;
}; 