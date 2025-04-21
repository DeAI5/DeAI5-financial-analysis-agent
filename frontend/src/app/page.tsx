'use client';

import { useState, useRef, useEffect } from 'react';
import { Message } from '../types';

export default function Home() {
  const [messages, setMessages] = useState<Message[]>([
    {
      role: 'system',
      content: 'You are a financial assistant specialized in stocks and cryptocurrencies analysis.'
    },
    {
      role: 'assistant',
      content: 'Hello! I\'m your financial assistant. I can help you with stock and cryptocurrency analysis, market trends, investment advice, and more. How can I assist you today?'
    }
  ]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [showComparisonTool, setShowComparisonTool] = useState(false);
  const [tickers, setTickers] = useState<string[]>(['', '']);
  const [assetType, setAssetType] = useState<'auto' | 'stocks' | 'crypto'>('auto');
  const [timePeriod, setTimePeriod] = useState<string>('1y');
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!input.trim()) return;
    
    // Add user message to the state
    const userMessage: Message = { role: 'user', content: input };
    setMessages((prev) => [...prev, userMessage]);
    setInput('');
    setLoading(true);

    try {
      const response = await fetch('/api/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ messages: [...messages, userMessage] }),
      });

      const data = await response.json();
      
      if (!response.ok) {
        throw new Error(data.error || 'Failed to get response');
      }

      // Add assistant response to the state
      setMessages((prev) => [
        ...prev,
        { role: 'assistant', content: data.message },
      ]);
    } catch (error) {
      console.error('Error sending message:', error);
      // Add error message
      setMessages((prev) => [
        ...prev,
        { 
          role: 'assistant', 
          content: 'Sorry, there was an error processing your request. Please try again.' 
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  const handleCompareSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    // Filter out empty tickers
    const validTickers = tickers.filter(ticker => ticker.trim() !== '');
    
    if (validTickers.length < 2) {
      alert('Please enter at least 2 tickers to compare');
      return;
    }
    
    const tickerList = validTickers.join(', ');
    const comparisonPrompt = `Compare the following tickers: ${tickerList} with asset type: ${assetType} for period: ${timePeriod}`;
    
    // Add user message to the state
    const userMessage: Message = { 
      role: 'user', 
      content: comparisonPrompt
    };
    
    setMessages((prev) => [...prev, userMessage]);
    setShowComparisonTool(false); // Hide the comparison tool after submitting
    setLoading(true);

    try {
      const response = await fetch('/api/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ messages: [...messages, userMessage] }),
      });

      const data = await response.json();
      
      if (!response.ok) {
        throw new Error(data.error || 'Failed to get response');
      }

      // Add assistant response to the state
      setMessages((prev) => [
        ...prev,
        { role: 'assistant', content: data.message },
      ]);
    } catch (error) {
      console.error('Error sending comparison request:', error);
      // Add error message
      setMessages((prev) => [
        ...prev,
        { 
          role: 'assistant', 
          content: 'Sorry, there was an error processing your comparison request. Please try again.' 
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  const addTickerField = () => {
    setTickers([...tickers, '']);
  };

  const handleTickerChange = (index: number, value: string) => {
    const newTickers = [...tickers];
    newTickers[index] = value;
    setTickers(newTickers);
  };

  const removeTickerField = (index: number) => {
    if (tickers.length <= 2) {
      return; // Keep at least 2 ticker fields
    }
    const newTickers = tickers.filter((_, i) => i !== index);
    setTickers(newTickers);
  };

  return (
    <main className="flex min-h-screen flex-col items-center p-4 md:p-24">
      <h1 className="text-3xl font-bold mb-8">Financial Assistant</h1>
      
      <div className="w-full max-w-4xl bg-white rounded-lg shadow-lg p-4 flex flex-col h-[70vh]">
        <div className="flex-1 overflow-y-auto mb-4 space-y-4">
          {messages
            .filter((message) => message.role !== 'system')
            .map((message, index) => (
              <div
                key={index}
                className={`p-4 rounded-lg ${
                  message.role === 'user'
                    ? 'bg-blue-100 ml-auto max-w-[80%]'
                    : 'bg-gray-100 mr-auto max-w-[80%]'
                }`}
              >
                <p className="whitespace-pre-wrap">{message.content}</p>
              </div>
            ))}
          {loading && (
            <div className="bg-gray-100 p-4 rounded-lg mr-auto max-w-[80%]">
              <p>Thinking...</p>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>
        
        {showComparisonTool ? (
          <div className="mb-4 p-4 border border-gray-200 rounded-lg bg-blue-50">
            <h3 className="font-bold mb-3">Compare Multiple Assets</h3>
            <form onSubmit={handleCompareSubmit} className="space-y-3">
              <div className="flex flex-col gap-2">
                {tickers.map((ticker, index) => (
                  <div key={index} className="flex gap-2 items-center">
                    <input
                      type="text"
                      value={ticker}
                      onChange={(e) => handleTickerChange(index, e.target.value)}
                      placeholder={`Ticker ${index + 1} (e.g., AAPL, BTC)`}
                      className="flex-1 p-2 border border-gray-300 rounded-lg"
                      required={index < 2} // First two fields are required
                    />
                    {index >= 2 && (
                      <button
                        type="button"
                        onClick={() => removeTickerField(index)}
                        className="bg-red-500 text-white p-2 rounded-lg"
                        title="Remove ticker"
                      >
                        ✕
                      </button>
                    )}
                  </div>
                ))}
                <button
                  type="button"
                  onClick={addTickerField}
                  className="bg-green-500 text-white p-2 rounded-lg self-start"
                >
                  + Add Another Ticker
                </button>
              </div>
              
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block mb-1 font-medium">Asset Type</label>
                  <select
                    value={assetType}
                    onChange={(e) => setAssetType(e.target.value as 'auto' | 'stocks' | 'crypto')}
                    className="w-full p-2 border border-gray-300 rounded-lg"
                  >
                    <option value="auto">Auto-detect</option>
                    <option value="stocks">Stocks</option>
                    <option value="crypto">Cryptocurrencies</option>
                  </select>
                </div>
                
                <div>
                  <label className="block mb-1 font-medium">Time Period</label>
                  <select
                    value={timePeriod}
                    onChange={(e) => setTimePeriod(e.target.value)}
                    className="w-full p-2 border border-gray-300 rounded-lg"
                  >
                    <option value="1m">1 Month</option>
                    <option value="3m">3 Months</option>
                    <option value="6m">6 Months</option>
                    <option value="1y">1 Year</option>
                    <option value="2y">2 Years</option>
                    <option value="5y">5 Years</option>
                  </select>
                </div>
              </div>
              
              <div className="flex gap-2">
                <button
                  type="submit"
                  className="bg-blue-500 text-white px-4 py-2 rounded-lg hover:bg-blue-600 transition-colors"
                >
                  Compare Assets
                </button>
                <button
                  type="button"
                  onClick={() => setShowComparisonTool(false)}
                  className="bg-gray-300 px-4 py-2 rounded-lg hover:bg-gray-400 transition-colors"
                >
                  Cancel
                </button>
              </div>
            </form>
          </div>
        ) : (
          <div className="flex justify-between mb-2">
            <button
              type="button"
              onClick={() => setShowComparisonTool(true)}
              className="text-blue-500 text-sm hover:underline"
            >
              Compare Multiple Assets
            </button>
          </div>
        )}
        
        <form onSubmit={handleSubmit} className="flex gap-2">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Ask about stocks, crypto, or investment advice..."
            className="flex-1 p-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            disabled={loading}
          />
          <button
            type="submit"
            className="bg-blue-500 text-white px-4 py-2 rounded-lg hover:bg-blue-600 transition-colors disabled:opacity-50"
            disabled={loading || !input.trim()}
          >
            Send
          </button>
        </form>
      </div>
    </main>
  );
} 