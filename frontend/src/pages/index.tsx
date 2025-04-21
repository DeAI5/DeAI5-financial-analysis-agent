import { useState, useRef, useEffect } from 'react';
import Head from 'next/head';
import ReactMarkdown from 'react-markdown';
import { FiSend, FiRefreshCw } from 'react-icons/fi';

interface Message {
  role: 'user' | 'assistant' | 'system';
  content: string;
}

// Define the response format from the LlamaIndex agent
interface AgentResponse {
  is_dummy_stream?: boolean;
  metadata?: Record<string, unknown>;
  response: string;
  source_nodes?: Array<Record<string, unknown>>;
  sources?: Array<Record<string, unknown>>;
}

export default function Home() {
  const [input, setInput] = useState('');
  const [messages, setMessages] = useState<Message[]>([
    {
      role: 'system',
      content: 'You are a financial assistant specializing in stocks and cryptocurrencies.'
    },
    {
      role: 'assistant',
      content: 'Hello! I\'m your financial assistant. I can help you with stock analysis, cryptocurrency insights, and investment advice. What would you like to know today?'
    }
  ]);
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  // Helper function to ensure content is always a string
  const ensureString = (content: unknown): string => {
    if (typeof content === 'string') {
      return content;
    } else if (content === null || content === undefined) {
      return '';
    } else if (typeof content === 'object') {
      try {
        // Check if this is an agent response object
        const obj = content as Record<string, unknown>;
        if (obj.response && typeof obj.response === 'string') {
          return obj.response;
        }
        return JSON.stringify(content, null, 2);
      } catch {
        return 'Error: Could not stringify response object';
      }
    }
    return String(content);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim()) return;

    const userMessage = { role: 'user', content: input } as Message;
    setMessages((prev) => [...prev, userMessage]);
    setInput('');
    setIsLoading(true);

    try {
      const response = await fetch('/api/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          messages: [...messages, userMessage],
        }),
      });

      if (!response.ok) {
        throw new Error('Failed to get response');
      }

      const data = await response.json();
      let responseContent = data.response;

      // Handle different response formats
      if (typeof responseContent === 'object' && responseContent !== null) {
        // Check if it's an agent response object
        const agentResponse = responseContent as AgentResponse;
        if (agentResponse.response) {
          responseContent = agentResponse.response;
        }
      }

      // If it's still not a string, ensure it becomes one
      responseContent = ensureString(responseContent);
      
      const assistantMessage = { 
        role: 'assistant', 
        content: responseContent
      } as Message;
      
      setMessages((prev) => [...prev, assistantMessage]);
    } catch (error) {
      console.error('Error:', error);
      setMessages((prev) => [
        ...prev,
        { role: 'assistant', content: 'Sorry, there was an error processing your request.' },
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  const clearChat = () => {
    setMessages([
      {
        role: 'system',
        content: 'You are a financial assistant specializing in stocks and cryptocurrencies.'
      },
      {
        role: 'assistant',
        content: 'Hello! I\'m your financial assistant. I can help you with stock analysis, cryptocurrency insights, and investment advice. What would you like to know today?'
      }
    ]);
  };

  return (
    <>
      <Head>
        <title>Financial AI Agent</title>
        <meta name="description" content="Chat with your financial AI assistant" />
        <link rel="icon" href="/favicon.ico" />
      </Head>

      <main className="min-h-screen bg-gray-50 text-gray-900 dark:bg-gray-900 dark:text-gray-100">
      {/* <main className="flex flex-col h-screen bg-gray-50"> */}
        <header className="bg-blue-600 p-4 text-white">
          <h1 className="text-2xl font-bold text-center">Financial AI Assistant</h1>
        </header>

        <div className="flex-1 overflow-auto p-4 space-y-4">
          {messages.length <= 2 ? (
            <div className="flex items-center justify-center h-full">
              <div className="text-center text-gray-500 max-w-md">
                <h2 className="text-xl font-semibold mb-2">Welcome to your Financial AI Assistant</h2>
                <p className="mb-4">Ask about stocks, cryptocurrencies, investment advice, or financial analysis.</p>
                <p className="text-sm text-gray-400">Example questions:</p>
                <ul className="text-sm text-gray-400 space-y-1">
                  <li>What&apos;s the current technical analysis for Bitcoin?</li>
                  <li>Give me investment advice on Tesla stock</li>
                  <li>What are the trending cryptocurrencies today?</li>
                </ul>
              </div>
            </div>
          ) : (
            messages.slice(1).map((message, index) => (
              <div
                key={index}
                className={`p-4 rounded-lg ${
                  message.role === 'user' ? 'bg-blue-100 ml-auto max-w-[80%] dark:bg-blue-200' : 'bg-white border border-gray-200 mr-auto max-w-[80%] dark:bg-gray-800 dark:border-gray-600 dark:text-white'
                }`}
              >
                <div className="prose">
                  {typeof message.content === 'string' ? (
                    <ReactMarkdown>
                      {message.content}
                    </ReactMarkdown>
                  ) : (
                    <pre>{JSON.stringify(message.content, null, 2)}</pre>
                  )}
                </div>
              </div>
            ))
          )}
          {isLoading && (
            <div className="p-4 rounded-lg bg-gray-100 mr-auto max-w-[80%]">
              <div className="flex space-x-2 items-center">
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.4s' }}></div>
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>

        <div className="p-4 border-t bg-white dark:bg-gray-800 border-gray-200 dark:border-gray-700">
          <form onSubmit={handleSubmit} className="flex space-x-2">
            <button
              type="button"
              onClick={clearChat}
              className="p-2 rounded-full hover:bg-gray-200 dark:hover:bg-gray-700 transition-colors text-black dark:text-white"
              title="Clear chat"
            >
              <FiRefreshCw />
            </button>
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Ask about stocks, crypto, or investment advice..."
              className="flex-1 p-2 border rounded-lg 
                 bg-white text-black placeholder-gray-500 
                 dark:bg-gray-900 dark:text-white dark:placeholder-gray-400 
                 border-gray-300 dark:border-gray-600 
                 focus:outline-none focus:ring-2 focus:ring-blue-500"
              disabled={isLoading}
            />
            <button
              type="submit"
              className="bg-blue-600 text-white p-2 rounded-lg 
                 hover:bg-blue-700 transition-colors 
                 disabled:bg-blue-300 dark:disabled:bg-blue-800"
              disabled={isLoading || !input.trim()}
            >
              <FiSend />
            </button>
          </form>
        </div>
      </main>
    </>
  );
} 