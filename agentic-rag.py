import os
from llama_index.core import VectorStoreIndex, Settings, SimpleDirectoryReader
from llama_index.core.tools import QueryEngineTool, FunctionTool
from llama_index.core.agent import ReActAgent
from llama_parse import LlamaParse
from llama_index.llms.openai import OpenAI
import yfinance as yf
import pandas as pd
from datetime import datetime
from load_env import load_environment
from financial_tools import (
    extract_financial_insights,
    get_company_financials,
    sector_performance,
    get_analyst_recommendations,
    generate_investment_advice,
    # Cryptocurrency functions
    get_crypto_data,
    get_crypto_market_data,
    analyze_crypto,
    generate_crypto_investment_advice,
    compare_cryptos,
    get_crypto_dominance
)

# Import TradingView API tools
from tradingview_api import (
    get_tradingview_crypto_analysis,
    get_tradingview_crypto_market,
    get_tradingview_multi_timeframe_analysis
)

# Import CoinMarketCap API tools
from coinmarketcap_api import (
    get_cmc_crypto_data,
    get_cmc_crypto_market_overview,
    get_cmc_crypto_analysis,
    compare_cmc_cryptocurrencies,
    get_cmc_investment_recommendation
)

# Load environment variables
if not load_environment():
    print("Failed to load required environment variables. Exiting.")
    exit(1)

# Configure LLM
Settings.llm = OpenAI(model="gpt-4o", temperature=0.1)

# Financial data tools
def get_stock_data(ticker, period="1y", interval="1d"):
    """Get historical stock price data for analysis"""
    try:
        data = yf.Ticker(ticker).history(period=period, interval=interval)
        return f"Retrieved {len(data)} data points for {ticker}. Latest close price: {data['Close'].iloc[-1]:.2f}"
    except Exception as e:
        return f"Error retrieving data for {ticker}: {str(e)}"

def analyze_stock(ticker, period="6mo"):
    """Comprehensive stock analysis with technical and fundamental indicators"""
    try:
        analysis = extract_financial_insights(ticker, period)
        return analysis
    except Exception as e:
        return f"Error analyzing {ticker}: {str(e)}"

def get_investment_recommendation(ticker, period="6mo", risk_tolerance="moderate"):
    """Generate comprehensive investment recommendation and financial advice"""
    try:
        advice = generate_investment_advice(ticker, period, risk_tolerance)
        return advice
    except Exception as e:
        return f"Error generating investment advice for {ticker}: {str(e)}"

def get_market_indices():
    """Get major market indices performance"""
    indices = {
        "S&P 500": "^GSPC",
        "Dow Jones": "^DJI",
        "NASDAQ": "^IXIC",
        "Russell 2000": "^RUT"
    }
    
    results = {}
    for name, ticker in indices.items():
        try:
            data = yf.Ticker(ticker).history(period="5d")
            latest = data['Close'].iloc[-1]
            previous = data['Close'].iloc[-2]
            daily_change = ((latest - previous) / previous) * 100
            
            # Get YTD performance
            ytd_data = yf.Ticker(ticker).history(period="ytd")
            ytd_change = ((ytd_data['Close'].iloc[-1] - ytd_data['Close'].iloc[0]) / ytd_data['Close'].iloc[0]) * 100
            
            results[name] = {
                "current": latest,
                "daily_change_pct": daily_change,
                "ytd_change_pct": ytd_change
            }
        except Exception as e:
            results[name] = f"Error: {str(e)}"
    
    return results

def compare_stocks(tickers, period="1y"):
    """Compare performance of multiple stocks over a period"""
    if not isinstance(tickers, list):
        tickers = tickers.split(',')
    
    tickers = [t.strip() for t in tickers]
    results = {}
    
    for ticker in tickers:
        try:
            data = yf.Ticker(ticker).history(period=period)
            start_price = data['Close'].iloc[0]
            current_price = data['Close'].iloc[-1]
            percent_change = ((current_price - start_price) / start_price) * 100
            
            results[ticker] = {
                "start_price": start_price,
                "current_price": current_price,
                "percent_change": percent_change
            }
        except Exception as e:
            results[ticker] = f"Error: {str(e)}"
    
    return results

def get_economic_indicators():
    """Get key economic indicators using Yahoo Finance data for related ETFs/indices"""
    indicators = {
        "10Y Treasury Yield": "^TNX",
        "VIX Volatility Index": "^VIX",
        "US Dollar Index": "DX-Y.NYB",
        "Gold": "GC=F",
        "Crude Oil": "CL=F"
    }
    
    results = {}
    for name, ticker in indicators.items():
        try:
            data = yf.Ticker(ticker).history(period="5d")
            latest = data['Close'].iloc[-1]
            previous = data['Close'].iloc[-2]
            daily_change = ((latest - previous) / previous) * 100
            
            results[name] = {
                "current_value": latest,
                "daily_change_pct": daily_change
            }
        except Exception as e:
            results[name] = f"Error: {str(e)}"
    
    return results

def get_sector_analysis():
    """Analyze performance across market sectors"""
    try:
        return sector_performance()
    except Exception as e:
        return f"Error analyzing sectors: {str(e)}"

# Cryptocurrency wrapper functions
def get_crypto_analysis(symbol, period="6mo"):
    """Comprehensive cryptocurrency analysis with technical indicators"""
    try:
        # Ensure proper suffix for crypto symbols
        if not '-' in symbol:
            symbol = f"{symbol}-USD"
        return analyze_crypto(symbol, period)
    except Exception as e:
        return f"Error analyzing cryptocurrency {symbol}: {str(e)}"

def get_crypto_investment_advice(symbol, period="6mo", risk_tolerance="moderate"):
    """Generate cryptocurrency investment recommendation and financial advice"""
    try:
        # Ensure proper suffix for crypto symbols
        if not '-' in symbol:
            symbol = f"{symbol}-USD"
        return generate_crypto_investment_advice(symbol, period, risk_tolerance)
    except Exception as e:
        return f"Error generating crypto investment advice for {symbol}: {str(e)}"

def get_crypto_market_overview():
    """Get overview of the cryptocurrency market including major coins"""
    try:
        market_data = get_crypto_market_data()
        dominance_data = get_crypto_dominance()
        
        # Combine the data
        result = {
            "market_data": market_data,
            "dominance_data": dominance_data,
            "analysis_date": datetime.now().strftime("%Y-%m-%d")
        }
        
        return result
    except Exception as e:
        return f"Error retrieving crypto market overview: {str(e)}"

def compare_cryptocurrencies(symbols, period="1y"):
    """Compare performance of multiple cryptocurrencies over a period"""
    try:
        return compare_cryptos(symbols, period)
    except Exception as e:
        return f"Error comparing cryptocurrencies: {str(e)}"

# TradingView API wrapper functions
def get_tradingview_crypto_technical_analysis(symbol, interval="1d"):
    """Get detailed technical analysis from TradingView for a cryptocurrency"""
    try:
        return get_tradingview_crypto_analysis(symbol, interval)
    except Exception as e:
        return f"Error retrieving TradingView analysis for {symbol}: {str(e)}"

def get_tradingview_crypto_market_overview():
    """Get cryptocurrency market overview using TradingView data"""
    try:
        return get_tradingview_crypto_market()
    except Exception as e:
        return f"Error retrieving TradingView market overview: {str(e)}"

def get_tradingview_multi_timeframe_crypto_analysis(symbol):
    """Get multi-timeframe technical analysis for a cryptocurrency using TradingView"""
    try:
        return get_tradingview_multi_timeframe_analysis(symbol)
    except Exception as e:
        return f"Error retrieving multi-timeframe analysis for {symbol}: {str(e)}"

# CoinMarketCap API wrapper functions
def get_coinmarketcap_crypto_data(symbol):
    """Get comprehensive data for a cryptocurrency from CoinMarketCap"""
    try:
        return get_cmc_crypto_data(symbol)
    except Exception as e:
        return f"Error retrieving CoinMarketCap data for {symbol}: {str(e)}"

def get_coinmarketcap_crypto_market_overview():
    """Get cryptocurrency market overview using CoinMarketCap data"""
    try:
        return get_cmc_crypto_market_overview()
    except Exception as e:
        return f"Error retrieving CoinMarketCap market overview: {str(e)}"

def get_coinmarketcap_crypto_analysis(symbol):
    """Analyze a cryptocurrency with data from CoinMarketCap"""
    try:
        return get_cmc_crypto_analysis(symbol)
    except Exception as e:
        return f"Error analyzing cryptocurrency with CoinMarketCap: {str(e)}"

def compare_coinmarketcap_cryptocurrencies(symbols):
    """Compare multiple cryptocurrencies using CoinMarketCap data"""
    if not isinstance(symbols, list):
        symbols = symbols.split(',')
    
    symbols = [s.strip() for s in symbols]
    
    try:
        return compare_cmc_cryptocurrencies(symbols)
    except Exception as e:
        return f"Error comparing cryptocurrencies with CoinMarketCap: {str(e)}"

def get_coinmarketcap_investment_recommendation(symbol, risk_tolerance="moderate"):
    """Generate detailed investment recommendation for a cryptocurrency based on CoinMarketCap data"""
    try:
        return get_cmc_investment_recommendation(symbol, risk_tolerance)
    except Exception as e:
        return f"Error generating investment recommendation for {symbol}: {str(e)}"

def get_buy_sell_recommendation(symbol, risk_tolerance="moderate"):
    """
    Generate a comprehensive buy/sell recommendation for a cryptocurrency by combining the best data from all sources
    
    Parameters:
    - symbol: Cryptocurrency symbol (e.g., "BTC", "ETH")
    - risk_tolerance: User's risk tolerance level (low, moderate, high)
    
    Returns:
    - Dictionary containing detailed buy/sell recommendation with supporting data
    """
    try:
        # Clean up symbol format
        clean_symbol = symbol.upper().replace("-USD", "").replace("USD", "")
        
        # Get recommendations from all sources, prioritizing CoinMarketCap
        cmc_recommendation = get_coinmarketcap_investment_recommendation(clean_symbol, risk_tolerance)
        
        # If CoinMarketCap recommendation is successful, use it as our base
        if isinstance(cmc_recommendation, dict) and "error" not in cmc_recommendation:
            # Try to supplement with data from other sources
            try:
                # Get TradingView analysis
                tv_analysis = get_tradingview_multi_timeframe_crypto_analysis(clean_symbol)
                
                # Get Yahoo Finance analysis (use period based on risk tolerance)
                period = "3mo" if risk_tolerance == "low" else "6mo" if risk_tolerance == "moderate" else "1y"
                yf_analysis = get_crypto_investment_advice(clean_symbol, period, risk_tolerance)
                
                # Enhance the recommendation with additional insights if available
                if isinstance(tv_analysis, dict) and "error" not in tv_analysis:
                    cmc_recommendation["tradingview_analysis"] = {
                        "recommendation": tv_analysis.get("overall_sentiment"),
                        "timeframes": {k: v.get("overall_sentiment", "Unknown") for k, v in tv_analysis.get("timeframes", {}).items() if "error" not in v}
                    }
                
                if isinstance(yf_analysis, dict):
                    cmc_recommendation["yahoo_finance_analysis"] = {
                        "recommendation": yf_analysis.get("recommendation"),
                        "confidence_score": yf_analysis.get("confidence_score"),
                        "technical_signals": yf_analysis.get("technical_signals", [])[:3]  # Top 3 signals
                    }
                
                # Add a consensus field if we have multiple sources
                sources_available = 1  # We already have CoinMarketCap
                recommendations = [cmc_recommendation.get("recommendation", "Neutral")]
                
                if isinstance(tv_analysis, dict) and "error" not in tv_analysis:
                    sources_available += 1
                    recommendations.append(tv_analysis.get("overall_sentiment", "Neutral"))
                
                if isinstance(yf_analysis, dict):
                    sources_available += 1
                    recommendations.append(yf_analysis.get("recommendation", "Neutral"))
                
                if sources_available > 1:
                    # Determine if recommendations align
                    buy_count = sum(1 for r in recommendations if "Buy" in r)
                    sell_count = sum(1 for r in recommendations if "Sell" in r)
                    
                    # Only override with consensus if there's strong agreement
                    if buy_count >= 2 and buy_count > sell_count:
                        consensus = "Strong consensus to Buy" if buy_count == sources_available else "Moderate consensus to Buy"
                    elif sell_count >= 2 and sell_count > buy_count:
                        consensus = "Strong consensus to Sell" if sell_count == sources_available else "Moderate consensus to Sell"
                    else:
                        consensus = "Mixed signals across sources"
                    
                    cmc_recommendation["consensus"] = {
                        "recommendation": consensus,
                        "sources": sources_available,
                        "agreement_level": "High" if buy_count == sources_available or sell_count == sources_available else "Moderate" if buy_count > sell_count or sell_count > buy_count else "Low"
                    }
            
            except Exception as e:
                # If enhancement fails, still return the CoinMarketCap recommendation
                pass
            
            return cmc_recommendation
        
        # If CoinMarketCap fails, try TradingView next
        tv_analysis = get_tradingview_multi_timeframe_crypto_analysis(clean_symbol)
        if isinstance(tv_analysis, dict) and "error" not in tv_analysis:
            # Format in a similar structure to CoinMarketCap recommendation
            result = {
                "symbol": clean_symbol,
                "recommendation": tv_analysis.get("overall_sentiment", "Neutral"),
                "confidence_score": 65,  # Lower confidence since it's not as detailed
                "risk_tolerance": risk_tolerance,
                "technical_signals": [],
                "investment_thesis": f"Based on TradingView technical analysis across multiple timeframes, the overall sentiment for {clean_symbol} is {tv_analysis.get('overall_sentiment', 'Neutral')}.",
                "risks": "TradingView analysis is primarily based on technical indicators and may not reflect fundamental factors or market news.",
                "timestamp": datetime.now().isoformat(),
                "disclaimer": "This analysis is for informational purposes only and should not be considered financial advice. Always conduct your own research and consider consulting with a financial advisor before making investment decisions. Cryptocurrency investments are especially high-risk and speculative."
            }
            
            # Extract signals from TradingView analysis
            for tf, data in tv_analysis.get("timeframes", {}).items():
                if "signals" in data:
                    for signal in data.get("signals", []):
                        result["technical_signals"].append({
                            "timeframe": tf,
                            "indicator": signal.get("indicator"),
                            "signal": signal.get("signal"),
                            "description": signal.get("description")
                        })
            
            return result
            
        # If both fail, try Yahoo Finance
        period = "3mo" if risk_tolerance == "low" else "6mo" if risk_tolerance == "moderate" else "1y"
        yf_analysis = get_crypto_investment_advice(clean_symbol, period, risk_tolerance)
        
        if isinstance(yf_analysis, dict):
            return yf_analysis
        
        # If all sources fail
        return {"error": f"Unable to generate buy/sell recommendation for {symbol} from any source"}
        
    except Exception as e:
        return {"error": f"Error generating buy/sell recommendation for {symbol}: {str(e)}"}

def combine_all_crypto_analysis_sources(symbol, period="6mo", risk_tolerance="moderate"):
    """Combine analysis from Yahoo Finance, TradingView, and CoinMarketCap for comprehensive cryptocurrency insights"""
    try:
        # Get analysis from all three sources
        yf_analysis = get_crypto_investment_advice(symbol, period, risk_tolerance)
        tv_analysis = get_tradingview_multi_timeframe_crypto_analysis(symbol)
        cmc_analysis = get_coinmarketcap_crypto_analysis(symbol)
        
        # Extract key insights from all sources
        if isinstance(yf_analysis, dict) and isinstance(tv_analysis, dict) and isinstance(cmc_analysis, dict) and "error" not in cmc_analysis:
            # Create combined recommendation
            yf_recommendation = yf_analysis.get("recommendation", "Neutral")
            tv_recommendation = tv_analysis.get("overall_sentiment", "Neutral")
            cmc_recommendation = cmc_analysis.get("overall_sentiment", "Neutral")
            
            # Determine consensus recommendation
            recommendations = [yf_recommendation, tv_recommendation, cmc_recommendation]
            buy_count = sum(1 for r in recommendations if r in ["Strong Buy", "Buy"])
            sell_count = sum(1 for r in recommendations if r in ["Strong Sell", "Sell"])
            neutral_count = sum(1 for r in recommendations if r in ["Hold", "Neutral"])
            
            if buy_count >= 2:
                consensus = "Buy"
            elif sell_count >= 2:
                consensus = "Sell"
            else:
                consensus = "Neutral/Hold"
            
            # Extract price data
            yf_price = yf_analysis.get("current_price", {}).get("price", 0)
            tv_price = tv_analysis.get("timeframes", {}).get("1d", {}).get("close", 0)
            cmc_price = cmc_analysis.get("price_usd", 0)
            
            # Use CoinMarketCap price if available (usually most accurate)
            price = cmc_price or tv_price or yf_price
            
            # Extract market data from CoinMarketCap
            market_cap = cmc_analysis.get("market_cap_usd", 0)
            volume_24h = cmc_analysis.get("volume_24h_usd", 0)
            volume_to_mcap_ratio = cmc_analysis.get("volume_to_mcap_ratio", 0)
            
            # Extract signals from TradingView analysis
            tv_signals = []
            for tf, data in tv_analysis.get("timeframes", {}).items():
                if "signals" in data:
                    for signal in data.get("signals", []):
                        tv_signals.append({
                            "timeframe": tf,
                            "indicator": signal.get("indicator"),
                            "signal": signal.get("signal"),
                            "description": signal.get("description")
                        })
            
            # Extract momentum signals from CoinMarketCap
            cmc_signals = cmc_analysis.get("momentum_signals", [])
            
            # Combine the analysis
            combined_analysis = {
                "symbol": symbol,
                "analysis_date": datetime.now().strftime("%Y-%m-%d"),
                "price_usd": price,
                "market_cap_usd": market_cap,
                "volume_24h_usd": volume_24h,
                "volume_to_mcap_ratio": volume_to_mcap_ratio,
                "source_recommendations": {
                    "yahoo_finance": yf_recommendation,
                    "tradingview": tv_recommendation,
                    "coinmarketcap": cmc_recommendation
                },
                "consensus_recommendation": consensus,
                "confidence_level": "High" if len(set(recommendations)) == 1 else "Moderate" if len(set(recommendations)) == 2 else "Low",
                "yahoo_finance_analysis": {
                    "recommendation": yf_analysis.get("recommendation"),
                    "confidence_score": yf_analysis.get("confidence_score"),
                    "potential_upside": yf_analysis.get("potential_upside"),
                    "potential_downside": yf_analysis.get("potential_downside"),
                    "signals": yf_analysis.get("technical_signals")
                },
                "tradingview_analysis": {
                    "recommendation": tv_analysis.get("overall_sentiment"),
                    "signal_counts": tv_analysis.get("signal_counts"),
                    "notable_signals": [s for s in tv_signals if s["signal"] != "neutral"][:3]  # Top 3 non-neutral signals
                },
                "coinmarketcap_analysis": {
                    "recommendation": cmc_analysis.get("overall_sentiment"),
                    "price_change_24h": cmc_analysis.get("percent_changes", {}).get("24h", 0),
                    "price_change_7d": cmc_analysis.get("percent_changes", {}).get("7d", 0),
                    "momentum_signals": cmc_signals[:3]  # Top 3 momentum signals
                },
                "investment_thesis": yf_analysis.get("investment_thesis"),
                "risks": yf_analysis.get("risks")
            }
            
            return combined_analysis
        else:
            # Fall back to available sources if some fail
            available_sources = []
            if isinstance(yf_analysis, dict):
                available_sources.append("Yahoo Finance")
            if isinstance(tv_analysis, dict) and "error" not in tv_analysis:
                available_sources.append("TradingView")
            if isinstance(cmc_analysis, dict) and "error" not in cmc_analysis:
                available_sources.append("CoinMarketCap")
                
            if len(available_sources) > 0:
                # Return the most detailed source
                if isinstance(cmc_analysis, dict) and "error" not in cmc_analysis:
                    return cmc_analysis
                elif isinstance(tv_analysis, dict) and "error" not in tv_analysis:
                    return tv_analysis
                else:
                    return yf_analysis
            else:
                return f"Error: No valid analysis available for {symbol} from any source"
    except Exception as e:
        return f"Error combining analysis for {symbol}: {str(e)}"

def combine_crypto_analysis_sources(symbol, period="6mo", risk_tolerance="moderate"):
    """Combine analysis from both Yahoo Finance and TradingView for comprehensive cryptocurrency insights"""
    try:
        # Get analysis from both sources
        yf_analysis = get_crypto_investment_advice(symbol, period, risk_tolerance)
        tv_analysis = get_tradingview_multi_timeframe_crypto_analysis(symbol)
        
        # Extract key insights from both sources
        if isinstance(yf_analysis, dict) and isinstance(tv_analysis, dict) and "error" not in tv_analysis:
            # Create combined recommendation
            yf_recommendation = yf_analysis.get("recommendation", "Neutral")
            tv_recommendation = tv_analysis.get("overall_sentiment", "Neutral")
            
            # Determine if recommendations align
            recommendations_align = (
                (yf_recommendation in ["Strong Buy", "Buy"] and tv_recommendation in ["Strong Buy", "Buy"]) or
                (yf_recommendation in ["Strong Sell", "Sell"] and tv_recommendation in ["Strong Sell", "Sell"]) or
                (yf_recommendation in ["Hold", "Mild Buy"] and tv_recommendation in ["Neutral"])
            )
            
            # Extract signals from TradingView analysis
            tv_signals = []
            for tf, data in tv_analysis.get("timeframes", {}).items():
                if "signals" in data:
                    for signal in data.get("signals", []):
                        tv_signals.append({
                            "timeframe": tf,
                            "indicator": signal.get("indicator"),
                            "signal": signal.get("signal"),
                            "description": signal.get("description")
                        })
            
            # Combine the analysis
            combined_analysis = {
                "symbol": symbol,
                "analysis_date": datetime.now().strftime("%Y-%m-%d"),
                "yahoo_finance": {
                    "recommendation": yf_analysis.get("recommendation"),
                    "confidence_score": yf_analysis.get("confidence_score"),
                    "potential_upside": yf_analysis.get("potential_upside"),
                    "potential_downside": yf_analysis.get("potential_downside"),
                    "price_data": yf_analysis.get("current_price"),
                    "signals": yf_analysis.get("technical_signals")
                },
                "tradingview": {
                    "recommendation": tv_analysis.get("overall_sentiment"),
                    "signal_counts": tv_analysis.get("signal_counts"),
                    "notable_signals": [s for s in tv_signals if s["signal"] != "neutral"][:5]  # Top 5 non-neutral signals
                },
                "combined_analysis": {
                    "recommendations_align": recommendations_align,
                    "combined_recommendation": tv_recommendation if recommendations_align else "Mixed Signals",
                    "confidence_level": "High" if recommendations_align else "Moderate",
                    "investment_thesis": yf_analysis.get("investment_thesis"),
                    "risks": yf_analysis.get("risks")
                }
            }
            
            return combined_analysis
        else:
            # Fall back to just one analysis if the other fails
            if isinstance(yf_analysis, dict):
                return yf_analysis
            elif isinstance(tv_analysis, dict) and "error" not in tv_analysis:
                return tv_analysis
            else:
                return f"Error combining analysis sources for {symbol}"
    except Exception as e:
        return f"Error combining analysis for {symbol}: {str(e)}"

def comprehensive_ticker_comparison(tickers, asset_type="auto", period="1y", metrics=None):
    """
    Comprehensive comparison of multiple tickers (stocks or cryptocurrencies) with detailed metrics
    
    Parameters:
    - tickers: List or comma-separated string of ticker symbols to compare
    - asset_type: "stocks", "crypto", or "auto" to auto-detect based on symbols
    - period: Time period for comparison (e.g., "1m", "3m", "6m", "1y", "2y", "5y")
    - metrics: List of specific metrics to include (None for all available metrics)
    
    Returns:
    - Dictionary containing comparative analysis and visualizable data
    """
    if isinstance(tickers, str):
        tickers = [t.strip() for t in tickers.split(',')]
    
    if not tickers:
        return {"error": "No tickers provided for comparison"}
    
    # Auto-detect asset type if not specified
    if asset_type == "auto":
        crypto_prefixes = ["BTC", "ETH", "XRP", "LTC", "BCH", "ADA", "DOT", "LINK", "XLM", "DOGE", "UNI", "SOL"]
        # Check if any ticker matches common crypto symbols
        if any(ticker.upper().startswith(tuple(crypto_prefixes)) for ticker in tickers) or \
           any("-USD" in ticker for ticker in tickers):
            asset_type = "crypto"
        else:
            asset_type = "stocks"
    
    # Use appropriate comparison function based on asset type
    try:
        results = {}
        correlation_matrix = {}
        key_metrics = {}
        
        if asset_type == "stocks":
            # Get basic comparison data
            comparison_data = compare_stocks(tickers, period)
            
            # Add additional metrics for stocks
            for ticker in tickers:
                try:
                    # Get company fundamentals
                    stock_info = yf.Ticker(ticker)
                    info = stock_info.info
                    
                    key_metrics[ticker] = {
                        "market_cap": info.get("marketCap"),
                        "pe_ratio": info.get("trailingPE"),
                        "eps": info.get("trailingEps"),
                        "dividend_yield": info.get("dividendYield", 0) * 100 if info.get("dividendYield") else 0,
                        "52w_high": info.get("fiftyTwoWeekHigh"),
                        "52w_low": info.get("fiftyTwoWeekLow"),
                        "avg_volume": info.get("averageVolume"),
                        "sector": info.get("sector"),
                        "industry": info.get("industry")
                    }
                    
                    # Get analyst recommendations
                    try:
                        recommendations = stock_info.recommendations
                        if not recommendations.empty:
                            recent_rec = recommendations.iloc[-1]
                            key_metrics[ticker]["analyst_recommendation"] = recent_rec["To Grade"] if "To Grade" in recent_rec else "N/A"
                    except:
                        key_metrics[ticker]["analyst_recommendation"] = "N/A"
                    
                except Exception as e:
                    key_metrics[ticker] = {"error": f"Could not retrieve detailed metrics: {str(e)}"}
            
            # Calculate correlation matrix
            try:
                price_data = {}
                for ticker in tickers:
                    data = yf.Ticker(ticker).history(period=period)["Close"]
                    price_data[ticker] = data
                
                if price_data:
                    df = pd.DataFrame(price_data)
                    corr_matrix = df.corr().round(2)
                    
                    # Convert correlation matrix to dictionary for JSON serialization
                    correlation_matrix = corr_matrix.to_dict()
            except Exception as e:
                correlation_matrix = {"error": f"Error calculating correlation: {str(e)}"}
                
            # Add sector/industry analysis
            sectors = {}
            for ticker, metrics in key_metrics.items():
                sector = metrics.get("sector", "Unknown")
                if sector not in sectors:
                    sectors[sector] = []
                sectors[sector].append(ticker)
            
            # Compile final results
            results = {
                "comparison_type": "stocks",
                "period": period,
                "tickers": tickers,
                "basic_comparison": comparison_data,
                "key_metrics": key_metrics,
                "correlation_matrix": correlation_matrix,
                "sector_grouping": sectors,
                "analysis_date": datetime.now().strftime("%Y-%m-%d")
            }
            
        else:  # Crypto comparison
            # Try to get best data from multiple sources
            
            # 1. First try CoinMarketCap (most comprehensive crypto data)
            try:
                cmc_data = compare_cmc_cryptocurrencies(tickers)
                if "error" not in cmc_data:
                    comparison_data = cmc_data
                    data_source = "CoinMarketCap"
                else:
                    # 2. If CMC fails, try TradingView
                    try:
                        tv_data = {}
                        for ticker in tickers:
                            clean_ticker = ticker.upper().replace("-USD", "").replace("USD", "")
                            tv_analysis = get_tradingview_crypto_analysis(clean_ticker)
                            if "error" not in tv_analysis:
                                tv_data[clean_ticker] = tv_analysis
                        
                        if tv_data:
                            comparison_data = {"tradingview_data": tv_data}
                            data_source = "TradingView"
                        else:
                            # 3. If all else fails, use Yahoo Finance
                            comparison_data = compare_cryptocurrencies(tickers, period)
                            data_source = "Yahoo Finance"
                    except:
                        # Final fallback
                        comparison_data = compare_cryptocurrencies(tickers, period)
                        data_source = "Yahoo Finance"
            except:
                # Fallback to Yahoo Finance if CoinMarketCap API fails
                comparison_data = compare_cryptocurrencies(tickers, period)
                data_source = "Yahoo Finance"
            
            # Add correlation data for cryptocurrencies
            try:
                price_data = {}
                for ticker in tickers:
                    # Ensure proper format for crypto symbols
                    if not "-USD" in ticker and not ticker.endswith("USD"):
                        ticker = f"{ticker}-USD"
                    data = yf.Ticker(ticker).history(period=period)["Close"]
                    price_data[ticker] = data
                
                if price_data:
                    df = pd.DataFrame(price_data)
                    corr_matrix = df.corr().round(2)
                    correlation_matrix = corr_matrix.to_dict()
            except Exception as e:
                correlation_matrix = {"error": f"Error calculating correlation: {str(e)}"}
            
            # Add volatility and risk metrics
            volatility_metrics = {}
            for ticker in tickers:
                try:
                    # Ensure proper format for crypto symbols
                    if not "-USD" in ticker and not ticker.endswith("USD"):
                        ticker = f"{ticker}-USD"
                        
                    # Calculate volatility
                    data = yf.Ticker(ticker).history(period=period)["Close"]
                    returns = data.pct_change().dropna()
                    
                    volatility_metrics[ticker] = {
                        "daily_volatility": returns.std() * 100,  # Daily volatility in percentage
                        "annualized_volatility": returns.std() * (252 ** 0.5) * 100,  # Annualized volatility
                        "max_drawdown": ((data / data.cummax()) - 1).min() * 100,  # Maximum drawdown in percentage
                        "sharpe_ratio": (returns.mean() / returns.std()) * (252 ** 0.5) if returns.std() > 0 else 0
                    }
                except Exception as e:
                    volatility_metrics[ticker] = {"error": f"Error calculating volatility metrics: {str(e)}"}
            
            # Compile final results
            results = {
                "comparison_type": "cryptocurrencies",
                "period": period,
                "tickers": tickers,
                "data_source": data_source,
                "basic_comparison": comparison_data,
                "correlation_matrix": correlation_matrix,
                "volatility_metrics": volatility_metrics,
                "analysis_date": datetime.now().strftime("%Y-%m-%d")
            }
            
            # Add Bitcoin correlation if BTC is not already in the comparison
            if not any(ticker.upper().startswith("BTC") for ticker in tickers):
                try:
                    # Get Bitcoin price data for the same period
                    btc_data = yf.Ticker("BTC-USD").history(period=period)["Close"]
                    
                    # Calculate correlation with Bitcoin for each ticker
                    btc_correlation = {}
                    for ticker in tickers:
                        if not "-USD" in ticker and not ticker.endswith("USD"):
                            ticker = f"{ticker}-USD"
                        
                        try:
                            ticker_data = price_data.get(ticker)
                            if ticker_data is not None:
                                # Create DataFrame with both series
                                combined = pd.DataFrame({"ticker": ticker_data, "btc": btc_data})
                                # Calculate correlation
                                correlation = combined.corr().loc["ticker", "btc"]
                                btc_correlation[ticker] = round(correlation, 2)
                        except Exception as e:
                            btc_correlation[ticker] = None
                    
                    results["bitcoin_correlation"] = btc_correlation
                except Exception as e:
                    results["bitcoin_correlation"] = {"error": f"Error calculating Bitcoin correlation: {str(e)}"}
        
        # Generate summary insights
        summary = []
        
        # Identify best and worst performers
        if asset_type == "stocks":
            performers = [(ticker, metrics.get("percent_change", 0)) 
                         for ticker, metrics in comparison_data.items() 
                         if isinstance(metrics, dict) and "percent_change" in metrics]
        else:
            # Handle different data sources for crypto
            if data_source == "CoinMarketCap":
                performers = [(ticker, data.get("percent_change_7d", 0)) 
                             for ticker, data in comparison_data.get("cryptocurrencies", {}).items()]
            elif data_source == "Yahoo Finance":
                performers = [(ticker, metrics.get("percent_change", 0)) 
                             for ticker, metrics in comparison_data.items() 
                             if isinstance(metrics, dict) and "percent_change" in metrics]
            else:
                performers = []
        
        if performers:
            performers.sort(key=lambda x: x[1], reverse=True)
            best_performer = performers[0]
            worst_performer = performers[-1]
            
            summary.append(f"Best performer: {best_performer[0]} with {best_performer[1]:.2f}% return")
            summary.append(f"Worst performer: {worst_performer[0]} with {worst_performer[1]:.2f}% return")
        
        # Add correlation insights
        try:
            if isinstance(correlation_matrix, dict) and len(correlation_matrix) > 0:
                # Find highest and lowest correlated pairs
                highest_corr = (-1, None, None)
                lowest_corr = (2, None, None)
                
                for ticker1 in correlation_matrix:
                    for ticker2 in correlation_matrix[ticker1]:
                        if ticker1 != ticker2:
                            corr_value = correlation_matrix[ticker1][ticker2]
                            if corr_value > highest_corr[0]:
                                highest_corr = (corr_value, ticker1, ticker2)
                            if corr_value < lowest_corr[0]:
                                lowest_corr = (corr_value, ticker1, ticker2)
                
                if highest_corr[1]:
                    summary.append(f"Highest correlation: {highest_corr[1]} and {highest_corr[2]} at {highest_corr[0]:.2f}")
                if lowest_corr[1]:
                    summary.append(f"Lowest correlation: {lowest_corr[1]} and {lowest_corr[2]} at {lowest_corr[0]:.2f}")
        except Exception as e:
            summary.append(f"Could not calculate correlation insights: {str(e)}")
        
        # Add volatility comparison for crypto
        if asset_type == "crypto" and volatility_metrics:
            try:
                # Find most and least volatile
                volatility_list = [(ticker, data.get("annualized_volatility", 0)) 
                                  for ticker, data in volatility_metrics.items() 
                                  if isinstance(data, dict) and "annualized_volatility" in data]
                
                if volatility_list:
                    volatility_list.sort(key=lambda x: x[1], reverse=True)
                    most_volatile = volatility_list[0]
                    least_volatile = volatility_list[-1]
                    
                    summary.append(f"Most volatile: {most_volatile[0]} with {most_volatile[1]:.2f}% annualized volatility")
                    summary.append(f"Least volatile: {least_volatile[0]} with {least_volatile[1]:.2f}% annualized volatility")
            except Exception as e:
                summary.append(f"Could not calculate volatility insights: {str(e)}")
        
        results["summary_insights"] = summary
        return results
        
    except Exception as e:
        return {"error": f"Error in comprehensive comparison: {str(e)}"}

# Create the comprehensive comparison tool
comprehensive_comparison_tool = FunctionTool.from_defaults(
    fn=comprehensive_ticker_comparison,
    name="comprehensive_ticker_comparison",
    description="Perform a comprehensive comparison of multiple tickers (stocks or cryptocurrencies) with detailed metrics and visualizable data. Parameters: tickers (required, comma-separated string or list), asset_type (optional: 'stocks', 'crypto', or 'auto' to auto-detect), period (optional, default '1y'), metrics (optional, specific metrics to include)"
)

# Create financial analysis tools
stock_data_tool = FunctionTool.from_defaults(
    fn=get_stock_data,
    name="get_stock_data",
    description="Get historical stock price data for a given ticker symbol. Parameters: ticker (required), period (optional, default '1y'), interval (optional, default '1d')"
)

stock_analysis_tool = FunctionTool.from_defaults(
    fn=analyze_stock,
    name="analyze_stock",
    description="Perform comprehensive technical and fundamental analysis on a stock. Returns price trends, technical indicators, company fundamentals, and analyst recommendations. Parameters: ticker (required), period (optional, default '6mo')"
)

investment_advice_tool = FunctionTool.from_defaults(
    fn=get_investment_recommendation,
    name="get_investment_recommendation",
    description="Generate investment recommendations and financial advice for a stock based on technical and fundamental analysis. Returns buy/sell recommendation, confidence score, risk assessment, and investment thesis. Parameters: ticker (required), period (optional, default '6mo'), risk_tolerance (optional: 'low', 'moderate', 'high', default 'moderate')"
)

market_indices_tool = FunctionTool.from_defaults(
    fn=get_market_indices,
    name="get_market_indices",
    description="Get the current values and recent performance of major market indices (S&P 500, Dow Jones, NASDAQ, Russell 2000)"
)

stock_comparison_tool = FunctionTool.from_defaults(
    fn=compare_stocks,
    name="compare_stocks",
    description="Compare the performance of multiple stocks over a given time period. Parameters: tickers (required, comma-separated string or list), period (optional, default '1y')"
)

economic_indicators_tool = FunctionTool.from_defaults(
    fn=get_economic_indicators,
    name="get_economic_indicators",
    description="Get current values of key economic indicators including Treasury yields, VIX volatility index, US Dollar index, gold and oil prices"
)

sector_analysis_tool = FunctionTool.from_defaults(
    fn=get_sector_analysis,
    name="get_sector_analysis",
    description="Get performance analysis of different market sectors (Technology, Healthcare, Financials, etc.) over various time periods"
)

company_financials_tool = FunctionTool.from_defaults(
    fn=get_company_financials,
    name="get_company_financials",
    description="Get detailed financial data for a company including key financial metrics, ratios, and growth figures. Parameter: ticker (required)"
)

analyst_recommendations_tool = FunctionTool.from_defaults(
    fn=get_analyst_recommendations,
    name="get_analyst_recommendations",
    description="Get recent analyst recommendations and ratings for a stock. Parameter: ticker (required)"
)

# Cryptocurrency analysis tools
crypto_analysis_tool = FunctionTool.from_defaults(
    fn=get_crypto_analysis,
    name="get_crypto_analysis",
    description="Perform comprehensive technical analysis on a cryptocurrency. Returns price trends, technical indicators, and market metrics. Parameters: symbol (required, e.g., 'BTC', 'ETH', or with suffix like 'BTC-USD'), period (optional, default '6mo')"
)

crypto_investment_advice_tool = FunctionTool.from_defaults(
    fn=get_crypto_investment_advice,
    name="get_crypto_investment_advice",
    description="Generate investment recommendations and financial advice for a cryptocurrency based on technical analysis. Returns buy/sell recommendation, confidence score, risk assessment, and investment thesis. Parameters: symbol (required), period (optional, default '6mo'), risk_tolerance (optional: 'low', 'moderate', 'high', default 'moderate')"
)

crypto_market_overview_tool = FunctionTool.from_defaults(
    fn=get_crypto_market_overview,
    name="get_crypto_market_overview",
    description="Get overview of the cryptocurrency market including performance data for major coins and Bitcoin dominance metrics"
)

crypto_comparison_tool = FunctionTool.from_defaults(
    fn=compare_cryptocurrencies,
    name="compare_cryptocurrencies",
    description="Compare the performance and technical indicators of multiple cryptocurrencies. Parameters: symbols (required, comma-separated string like 'BTC,ETH,ADA' or list), period (optional, default '1y')"
)

# TradingView API tools
tradingview_crypto_analysis_tool = FunctionTool.from_defaults(
    fn=get_tradingview_crypto_technical_analysis,
    name="get_tradingview_crypto_analysis",
    description="Get detailed technical analysis from TradingView for a cryptocurrency. Includes advanced indicators and signals. Parameters: symbol (required, e.g., 'BTC', 'ETH'), interval (optional, e.g., '1d', '4h', '1h', '15m', default '1d')"
)

tradingview_market_overview_tool = FunctionTool.from_defaults(
    fn=get_tradingview_crypto_market_overview,
    name="get_tradingview_market_overview",
    description="Get cryptocurrency market overview using TradingView data. Includes major coins with price, change, volume, and technical sentiment"
)

tradingview_multi_timeframe_tool = FunctionTool.from_defaults(
    fn=get_tradingview_multi_timeframe_crypto_analysis,
    name="get_tradingview_multi_timeframe_analysis",
    description="Get multi-timeframe (1d, 4h, 1h, 15m) technical analysis for a cryptocurrency using TradingView. Parameter: symbol (required, e.g., 'BTC', 'ETH')"
)

combined_crypto_analysis_tool = FunctionTool.from_defaults(
    fn=combine_crypto_analysis_sources,
    name="get_combined_crypto_analysis",
    description="Get comprehensive cryptocurrency analysis combining data from both Yahoo Finance and TradingView. Parameters: symbol (required), period (optional, default '6mo'), risk_tolerance (optional, default 'moderate')"
)

# CoinMarketCap API tools
coinmarketcap_data_tool = FunctionTool.from_defaults(
    fn=get_coinmarketcap_crypto_data,
    name="get_coinmarketcap_crypto_data",
    description="Get comprehensive data for a cryptocurrency from CoinMarketCap. Parameter: symbol (required)"
)

coinmarketcap_market_tool = FunctionTool.from_defaults(
    fn=get_coinmarketcap_crypto_market_overview,
    name="get_coinmarketcap_crypto_market_overview",
    description="Get cryptocurrency market overview using CoinMarketCap data"
)

coinmarketcap_analysis_tool = FunctionTool.from_defaults(
    fn=get_coinmarketcap_crypto_analysis,
    name="get_coinmarketcap_crypto_analysis",
    description="Analyze a cryptocurrency with data from CoinMarketCap. Parameter: symbol (required)"
)

coinmarketcap_comparison_tool = FunctionTool.from_defaults(
    fn=compare_coinmarketcap_cryptocurrencies,
    name="compare_coinmarketcap_cryptocurrencies",
    description="Compare multiple cryptocurrencies using CoinMarketCap data. Parameters: symbols (required, comma-separated string like 'BTC,ETH,ADA' or list)"
)

coinmarketcap_recommendation_tool = FunctionTool.from_defaults(
    fn=get_coinmarketcap_investment_recommendation,
    name="get_coinmarketcap_investment_recommendation",
    description="Generate detailed investment recommendation for a cryptocurrency based on CoinMarketCap data. Parameters: symbol (required), risk_tolerance (optional: 'low', 'moderate', 'high', default 'moderate')"
)

# Specialized buy/sell recommendation tool
buy_sell_recommendation_tool = FunctionTool.from_defaults(
    fn=get_buy_sell_recommendation,
    name="get_buy_sell_recommendation",
    description="Generate a comprehensive buy/sell recommendation for a cryptocurrency by combining the best data from all sources. Parameters: symbol (required), risk_tolerance (optional: 'low', 'moderate', 'high', default 'moderate')"
)

# Combined analysis from all sources
all_sources_crypto_analysis_tool = FunctionTool.from_defaults(
    fn=combine_all_crypto_analysis_sources,
    name="get_all_sources_crypto_analysis",
    description="Get comprehensive cryptocurrency analysis combining data from Yahoo Finance, TradingView, and CoinMarketCap. Parameters: symbol (required), period (optional, default '6mo'), risk_tolerance (optional, default 'moderate')"
)

# Create base tool list
base_tools = [
    # Stock market tools
    investment_advice_tool,
    stock_data_tool, 
    stock_analysis_tool, 
    market_indices_tool, 
    stock_comparison_tool,
    economic_indicators_tool,
    sector_analysis_tool,
    company_financials_tool,
    analyst_recommendations_tool,
    
    # Cryptocurrency tools - Yahoo Finance
    crypto_investment_advice_tool,
    crypto_analysis_tool,
    crypto_market_overview_tool,
    crypto_comparison_tool,
    
    # Cryptocurrency tools - TradingView
    tradingview_crypto_analysis_tool,
    tradingview_market_overview_tool,
    tradingview_multi_timeframe_tool,
    combined_crypto_analysis_tool,
    
    # Cryptocurrency tools - CoinMarketCap
    coinmarketcap_data_tool,
    coinmarketcap_market_tool,
    coinmarketcap_analysis_tool,
    coinmarketcap_comparison_tool,
    coinmarketcap_recommendation_tool,
    all_sources_crypto_analysis_tool,
    
    # Specialized crypto advice tools
    buy_sell_recommendation_tool,
    comprehensive_comparison_tool
]

# Load financial documents if available
documents = []
try:
    financial_docs_path = "./financial_docs"  # Create this directory and add relevant financial PDFs
    
    if os.path.exists(financial_docs_path):
        print(f"Loading documents from {financial_docs_path}...")
        # Load traditional documents
        documents.extend(SimpleDirectoryReader(financial_docs_path).load_data())
    
    # Add option to parse PDF reports using LlamaParse
    pdf_path = "./financial_reports.pdf"  # Update this path as needed
    if os.path.exists(pdf_path):
        print(f"Parsing PDF report: {pdf_path}...")
        parsed_docs = LlamaParse(result_type="markdown").load_data(pdf_path)
        documents.extend(parsed_docs)
except Exception as e:
    print(f"Error loading documents: {str(e)}")
    documents = []

# Create vector index and document tool if documents exist
if documents:
    try:
        print(f"Creating vector index from {len(documents)} documents...")
        index = VectorStoreIndex.from_documents(documents)
        query_engine = index.as_query_engine()

        # Create document query tool
        document_tool = QueryEngineTool.from_defaults(
            query_engine,
            name="financial_documents_tool",
            description="Search through financial documents, reports, and filings for information",
        )
        
        # Add document tool to tools list
        tools = base_tools + [document_tool]
    except Exception as e:
        print(f"Error creating index: {str(e)}")
        tools = base_tools
else:
    print("No documents found. Using only financial data tools.")
    tools = base_tools

# Create the financial analysis agent
system_prompt = """You are an expert financial analysis agent specialized in market analysis and investment recommendations for both traditional stocks and cryptocurrencies.

Your capabilities include:
1. Providing investment recommendations with confidence scores and risk assessments for stocks and cryptocurrencies
2. Analyzing stocks using technical indicators (moving averages, RSI, MACD, Bollinger Bands)
3. Evaluating company fundamentals (P/E ratio, revenue growth, profit margins)
4. Analyzing cryptocurrencies using technical indicators and market metrics from multiple sources (Yahoo Finance, TradingView, and CoinMarketCap)
5. Tracking major market indices, economic indicators, and crypto market trends
6. Comparing multiple stocks or cryptocurrencies with detailed metrics, correlations, and insights
7. Retrieving information from financial documents and reports

When providing stock analysis:
- Focus on both technical and fundamental factors
- Explain how earnings, growth, and financial health affect your recommendation
- Compare against sector and market performance

When providing cryptocurrency analysis:
- Use data from all three sources (Yahoo Finance, TradingView, and CoinMarketCap) for the most comprehensive analysis
- Analyze multiple timeframes (daily, 4-hour, 1-hour) for better insight
- Consider market dominance, volatility, trading volume, and on-chain metrics
- Explain how market trends and Bitcoin performance might affect altcoins
- Use advanced technical indicators to identify market trends
- Use CoinMarketCap for the most accurate market data, including price, market cap, and trading volume

When users ask to compare multiple assets:
- Always use the comprehensive_ticker_comparison tool for these requests
- The tool auto-detects whether the tickers are stocks or cryptocurrencies
- Provide insights on relative performance, correlation between assets, and volatility
- For stocks, include fundamental metrics comparison and sector analysis
- For cryptocurrencies, include Bitcoin correlation and risk metrics
- Present the comprehensive data in a way that highlights key differences and similarities

When users ask for investment advice or if they should buy/sell a cryptocurrency:
- IMPORTANT: Always use the specialized buy_sell_recommendation_tool for these questions
- Make sure to extract the cryptocurrency symbol from their question
- Assess the user's risk tolerance from context or default to "moderate"
- Provide a clear recommendation (Buy, Hold, or Sell) with a confidence score
- Explain your reasoning by citing specific metrics and trends
- Include the technical score and what it's based on
- Detail both potential upside and downside scenarios with percentage estimates
- Give a risk assessment appropriate to the user's risk tolerance
- Present an investment thesis explaining why this recommendation makes sense
- Highlight specific risks so the user can make an informed decision
- Always include the market cap, trading volume, and recent price performance in your answer
- Make sure to include the disclaimer about financial advice

Your combined cryptocurrency analysis provides:
- Multi-source verification (Yahoo Finance + TradingView + CoinMarketCap)
- Multi-timeframe perspective (long and short-term trends)
- Consensus recommendations with confidence level
- Risk-adjusted potential returns
- Detailed price momentum analysis across different timeframes

For all investment recommendations:
- Always explain the reasoning behind your conclusions
- Highlight both potential upside and risks
- Consider market conditions and trends
- Provide balanced perspectives with supporting data
- Tailor advice based on investor risk tolerance (low, moderate, high)
- Be especially cautious with high-risk assets like cryptocurrencies

Your goal is to provide data-driven financial insights that help with investment decisions.

IMPORTANT DISCLAIMER: Add this to all investment recommendations: "This analysis is for informational purposes only and should not be considered financial advice. Always conduct your own research and consider consulting with a financial advisor before making investment decisions. Cryptocurrency investments are especially high-risk and speculative."
"""

agent = ReActAgent.from_tools(
    tools, 
    llm=Settings.llm,
    verbose=True,
    system_prompt=system_prompt
)

# Example usage
if __name__ == "__main__":
    print("\n" + "="*50)
    print("Financial Analysis Agent initialized")
    print("="*50)
    print("Available tools:")
    
    # Display stock tools
    print("\nStock Market Analysis Tools:")
    stock_tools = [t for t in base_tools[:9]]
    for i, tool in enumerate(stock_tools, 1):
        print(f"{i}. {tool.metadata.name}: {tool.metadata.description.split('.')[0]}")
    
    # Display Yahoo Finance crypto tools
    print("\nCryptocurrency Analysis Tools (Yahoo Finance):")
    yf_crypto_tools = [t for t in base_tools[9:13]]
    for i, tool in enumerate(yf_crypto_tools, 1):
        print(f"{i}. {tool.metadata.name}: {tool.metadata.description.split('.')[0]}")
    
    # Display TradingView crypto tools
    print("\nCryptocurrency Analysis Tools (TradingView):")
    tv_crypto_tools = [t for t in base_tools[13:17]]
    for i, tool in enumerate(tv_crypto_tools, 1):
        print(f"{i}. {tool.metadata.name}: {tool.metadata.description.split('.')[0]}")
    
    # Display CoinMarketCap crypto tools
    print("\nCryptocurrency Analysis Tools (CoinMarketCap):")
    cmc_crypto_tools = [t for t in base_tools[17:]]
    for i, tool in enumerate(cmc_crypto_tools, 1):
        print(f"{i}. {tool.metadata.name}: {tool.metadata.description.split('.')[0]}")
    
    print("\n" + "="*50)
    print("Example queries:")
    print("\nFor Stocks:")
    print("- 'What's your investment recommendation for AAPL?'")
    print("- 'Analyze TSLA stock with a high risk tolerance'")
    print("- 'Compare the performance of MSFT, GOOGL, and AMZN'")
    
    print("\nFor Cryptocurrencies:")
    print("- 'What's your combined analysis for Bitcoin using all data sources?'")
    print("- 'Should I buy Ethereum right now?'")
    print("- 'Is it a good time to sell Solana given my moderate risk tolerance?'")
    print("- 'Give me a detailed investment recommendation for BNB'")
    print("- 'Compare BTC, ETH, and SOL performance using all data sources'")
    print("- 'What's the TradingView market sentiment for cryptocurrencies?'")
    print("- 'Get detailed CoinMarketCap data for Cardano (ADA)'")
    print("- 'What's the current crypto market overview from CoinMarketCap?'")
    print("- 'Give me a comprehensive price momentum analysis for Solana from CoinMarketCap'")
    
    print("\nGeneral Queries:")
    print("- 'What are the current market conditions?'")
    print("- 'How are tech stocks and cryptocurrencies correlated?'")
    
    print("\n" + "="*50)
    print("Type 'exit' to quit")
    print("="*50 + "\n")
    
    while True:
        user_input = input("\nEnter your financial query: ")
        if user_input.lower() in ["exit", "quit", "q"]:
            break
            
        print("\nProcessing your query...\n")
        try:
            response = agent.chat(user_input)
            print(f"\nAgent response: {response}")
        except Exception as e:
            print(f"Error processing query: {str(e)}")
            
    print("\nThank you for using the Financial Analysis Agent!")