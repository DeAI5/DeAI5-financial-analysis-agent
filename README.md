# Financial Analysis Agent

A powerful financial assistant that provides comprehensive analysis for stocks and cryptocurrencies using multiple data sources including Yahoo Finance, TradingView, and CoinMarketCap.

## Features

- Interactive chat interface with Next.js and React
- Python backend with LlamaIndex RAG agent
- Comprehensive stock analysis with fundamental and technical indicators
- Multi-source cryptocurrency analysis (Yahoo Finance, TradingView, CoinMarketCap)
- Asset comparison tool for comparing multiple stocks or cryptocurrencies
- Technical indicators and market trends analysis
- Investment recommendations with risk assessment

## Project Structure

```
├── backend/                # Flask backend server
├── frontend/               # Next.js frontend application
├── agentic-rag.py          # Main LlamaIndex RAG agent implementation
├── coinmarketcap_api.py    # CoinMarketCap API integration
├── financial_tools.py      # Financial analysis tools and utilities
├── load_env.py             # Environment variables loader
├── tradingview_api.py      # TradingView API integration
└── requirements.txt        # Python dependencies
```

## Setup

### Prerequisites

- Python 3.9+
- Node.js 14+
- API keys for:
  - OpenAI
  - CoinMarketCap (optional, but recommended)
  - Llama Cloud (optional, enhances RAG capabilities)
  - Alpha Vantage (required for detailed stock analysis)
  - Finnhub (required for real-time stock data)

### Backend Setup

1. Create a virtual environment and activate it:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

2. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Set up your API keys:
   Create a `.env` file in the root directory with the following content:
   ```
   OPENAI_API_KEY=your_openai_api_key
   COINMARKETCAP_API_KEY=your_coinmarketcap_api_key
   LLAMA_CLOUD_API_KEY=your_llama_cloud_api_key  # For enhanced RAG capabilities
   ALPHA_VANTAGE_API_KEY=your_alpha_vantage_key  # For detailed stock analysis
   FINNHUB_API_KEY=your_finnhub_key              # For real-time stock data
   ```

4. Start the Flask backend:
   ```bash
   cd backend
   python app.py
   ```
   The backend server will run on http://localhost:5000

### Frontend Setup

1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Start the development server:
   ```bash
   npm run dev
   ```

4. Open [http://localhost:3000](http://localhost:3000) in your browser.

## Usage

### Available Features

- **Stock Analysis**: Get comprehensive analysis of stocks with technical indicators, fundamentals, and price trends
- **Cryptocurrency Analysis**: Analyze cryptocurrencies using data from multiple sources (Yahoo Finance, TradingView, CoinMarketCap)
- **Investment Recommendations**: Receive buy/sell recommendations with confidence scores based on your risk tolerance
- **Asset Comparisons**: Compare multiple stocks or cryptocurrencies with correlation analysis, performance metrics, and more
- **Market Overview**: Get market indices data, sector performance, and cryptocurrency market trends

### Example Queries

- Stock analysis: "Analyze AAPL stock with moderate risk tolerance"
- Cryptocurrency analysis: "What's your comprehensive analysis of Bitcoin?"
- Investment advice: "Should I buy Ethereum right now?"
- Comparisons: "Compare MSFT, AAPL, and GOOGL performance"
- Crypto comparisons: "Compare BTC, ETH, and SOL with correlation analysis"
- Technical analysis: "What do the technical indicators show for Tesla stock?"
- Market overview: "What's the current crypto market overview?"

## Disclaimer

This financial analysis tool is for informational purposes only and should not be considered financial advice. Always conduct your own research and consider consulting with a financial advisor before making investment decisions. Cryptocurrency investments are especially high-risk and speculative.

## License

MIT 