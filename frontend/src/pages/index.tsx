import { useState, useRef, useEffect } from 'react';
import Head from 'next/head';
import ReactMarkdown from 'react-markdown';
import { FiSend, FiRefreshCw } from 'react-icons/fi';

interface Message {
  role: 'user' | 'assistant' | 'system';
  content: string;
  image_task_id?: string | null; // ID to trigger image generation fetch
  image_url?: string | null; 
  image_status?: 'idle' | 'fetching' | 'ready' | 'error'; // Status for image loading
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

  // --- Effect to Fetch Generated Image --- 
  useEffect(() => {
    // Function to fetch the image for a specific message
    const fetchGeneratedImage = async (messageIndex: number, taskId: string) => {
      console.log(`[Task ${taskId.substring(0,6)}]: Fetching generated image via direct URL...`);
      try {
        // Fetch DIRECTLY from the backend image generation endpoint
        const response = await fetch(`http://127.0.0.1:5000/api/generate_image/${taskId}`, { method: 'POST' }); 
        
        if (!response.ok) {
          const errorData = await response.json().catch(() => ({})); 
          console.error(`Image fetch failed for task ${taskId}: ${response.status}`, errorData);
          setMessages(prev => prev.map((msg, index) => 
            index === messageIndex ? { ...msg, image_status: 'error' } : msg
          ));
          return;
        }

        const data = await response.json();

        if (data.image_url) {
          console.log(`[Task ${taskId.substring(0,6)}]: Image received successfully.`);
          setMessages(prev => prev.map((msg, index) => 
            index === messageIndex ? { ...msg, image_status: 'ready', image_url: data.image_url } : msg
          ));
        } else {
          console.error(`Image fetch for task ${taskId} succeeded but no image_url found.`);
          setMessages(prev => prev.map((msg, index) => 
            index === messageIndex ? { ...msg, image_status: 'error' } : msg
          ));
        }
      } catch (error) {
        console.error("Error fetching generated image:", error);
        setMessages(prev => prev.map((msg, index) => 
          index === messageIndex ? { ...msg, image_status: 'error' } : msg
        ));
      }
    };

    // Find the latest assistant message that needs its image fetched
    const messageToFetch = messages.findLast((msg) => 
        msg.role === 'assistant' && msg.image_task_id && msg.image_status === 'fetching'
    );

    if (messageToFetch) {
       const messageIndex = messages.lastIndexOf(messageToFetch); 
       // Add a small delay before fetching image to ensure state update is processed
       const timer = setTimeout(() => {
            fetchGeneratedImage(messageIndex, messageToFetch.image_task_id!);
       }, 50); // 50ms delay
       return () => clearTimeout(timer); // Cleanup timeout if component/messages change before fetch
    }

  }, [messages]); 
  // --- End Image Fetching Effect ---

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
      // Fetch directly from backend, bypassing the Next.js proxy
      const response = await fetch('http://127.0.0.1:5000/api/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          messages: [...messages, userMessage],
        }),
      });

      if (!response.ok) {
        console.error(`Direct fetch failed with status: ${response.status}`);
        throw new Error('Failed to get response from direct backend fetch');
      }

      const data = await response.json();
      console.log("<<< Received direct data from API:", data);

      // Extract text response and image task ID
      let responseContent = data.response;
      let imageTaskId = data.image_task_id;
      responseContent = ensureString(responseContent); // Make sure text is string
      
      const assistantMessage: Message = { 
        role: 'assistant', 
        content: responseContent,
        image_task_id: imageTaskId, // Store the task ID
        image_status: imageTaskId ? 'fetching' : 'idle', // Set status to fetching if ID exists
        image_url: null // Reset image URL
      }; 
      
      console.log(">>> Adding assistant message (direct fetch):", assistantMessage); 

      setMessages((prev) => [...prev, assistantMessage]);
    } catch (error) {
      console.error('Error during direct fetch:', error);
      setMessages((prev) => [
        ...prev,
        // Keep error message simple
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
                  message.role === 'user' ? 'bg-blue-100 ml-auto max-w-[80%] dark:bg-blue-950' : 'bg-white border border-gray-200 mr-auto max-w-[80%] dark:bg-gray-800 dark:border-gray-600 dark:text-white'
                }`}
              >
                <div className="prose dark:prose-invert max-w-none">
                  {typeof message.content === 'string' ? (
                    <ReactMarkdown>
                      {message.content}
                    </ReactMarkdown>
                  ) : (
                    <pre>{JSON.stringify(message.content, null, 2)}</pre>
                  )}
                </div>
                 {/* Add image rendering logic */} 
                 {/* Show image if ready */}
                 {message.role === 'assistant' && message.image_status === 'ready' && message.image_url && (
                   <div className="mt-2">
                     <img
                       src={message.image_url}
                       alt="Generated visualization"
                       className="max-w-full h-auto rounded-lg border border-gray-300 dark:border-gray-600"
                       onError={(e) => {
                         const target = e.target as HTMLImageElement;
                         target.onerror = null; 
                         target.style.display = 'none'; 
                         const errorMsg = document.createElement('p');
                         errorMsg.textContent = 'Error loading image.';
                         errorMsg.className = 'text-red-500 text-sm';
                         target.parentNode?.insertBefore(errorMsg, target.nextSibling);
                       }}
                     />
                   </div>
                 )}
                 {/* Show loading indicator while fetching */}
                 {message.role === 'assistant' && message.image_status === 'fetching' && (
                    <div className="mt-2 text-sm text-gray-500 dark:text-gray-400 flex items-center">
                      <svg className="animate-spin -ml-1 mr-2 h-4 w-4 text-gray-400" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                        <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                        <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                      </svg>
                      Generating image...
                    </div>
                 )}
                  {/* Show error indicator */}
                  {message.role === 'assistant' && message.image_status === 'error' && (
                    <div className="mt-2 text-sm text-red-500">
                      Failed to load image.
                    </div>
                  )}
                 {/* End of image rendering logic */}
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