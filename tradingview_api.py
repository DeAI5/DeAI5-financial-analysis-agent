import os
import requests
import json
import time
from datetime import datetime
import pandas as pd
from typing import Dict, List, Optional, Union, Any

# TradingView API base URL
TRADINGVIEW_API_BASE_URL = "https://pine-facade.tradingview.com/symbol-search"
TRADINGVIEW_CHARTS_URL = "https://scanner.tradingview.com/crypto/scan"

class TradingViewAPI:
    """
    Client for interacting with TradingView's REST API
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the TradingView API client
        
        Parameters:
        - api_key: Optional API key for authenticated requests (not required for basic endpoints)
        """
        self.api_key = api_key or os.environ.get("TRADINGVIEW_API_KEY")
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Content-Type": "application/json"
        })
        
        # Add API key authentication if available
        if self.api_key:
            self.session.headers.update({
                "Authorization": f"Bearer {self.api_key}"
            })
    
    def search_symbols(self, query: str, limit: int = 10) -> List[Dict]:
        """
        Search for cryptocurrency symbols on TradingView
        
        Parameters:
        - query: Search query (e.g., "BTC", "ETH")
        - limit: Maximum number of results to return
        
        Returns:
        - List of matching symbols with metadata
        """
        params = {
            "text": query,
            "type": "crypto",
            "exchange": "",
            "limit": limit
        }
        
        try:
            response = self.session.get(TRADINGVIEW_API_BASE_URL, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {"error": f"Error searching symbols: {str(e)}"}
    
    def get_crypto_screener(self, columns: List[str] = None) -> Dict:
        """
        Get cryptocurrency screener data from TradingView
        
        Parameters:
        - columns: List of specific columns to include in the response
        
        Returns:
        - Dictionary containing cryptocurrency screener data
        """
        if columns is None:
            # Default set of useful data columns
            columns = [
                "name",
                "description",
                "exchange",
                "close",
                "change",
                "change_abs",
                "high",
                "low",
                "volume",
                "Recommend.All",
                "Recommend.MA",
                "Recommend.Other",
                "RSI",
                "RSI[1]",
                "Stoch.K",
                "Stoch.D",
                "Stoch.K[1]",
                "Stoch.D[1]",
                "MACD.macd",
                "MACD.signal",
                "ADX",
                "ADX+DI",
                "ADX-DI",
                "ADX+DI[1]",
                "ADX-DI[1]",
                "AO",
                "AO[1]",
                "CCI20",
                "CCI20[1]"
            ]
        
        # Build the TradingView scanner request
        request_data = {
            "symbols": {
                "tickers": ["CRYPTOCAP:TOTAL"],
                "query": {
                    "types": ["crypto"]
                }
            },
            "columns": columns
        }
        
        try:
            response = self.session.post(TRADINGVIEW_CHARTS_URL, json=request_data)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {"error": f"Error fetching crypto screener data: {str(e)}"}
    
    def get_crypto_technical_analysis(self, symbol: str, interval: str = "1d") -> Dict:
        """
        Get technical analysis indicators for a specific cryptocurrency
        
        Parameters:
        - symbol: Cryptocurrency symbol (e.g., "BINANCE:BTCUSDT")
        - interval: Time interval (e.g., "1d", "4h", "1h", "15m")
        
        Returns:
        - Dictionary containing technical analysis indicators and signals
        """
        # Ensure the symbol is in the correct format for TradingView
        if ":" not in symbol:
            # Default to BINANCE exchange if not specified
            symbol = f"BINANCE:{symbol}USDT"
        
        # Technical indicators to retrieve
        indicators = [
            "Recommend.All",
            "Recommend.MA",
            "Recommend.Other",
            "RSI",
            "RSI[1]",
            "Stoch.K",
            "Stoch.D",
            "Stoch.K[1]",
            "Stoch.D[1]",
            "MACD.macd",
            "MACD.signal",
            "SMA20",
            "SMA50",
            "SMA200",
            "EMA20",
            "EMA50",
            "EMA200",
            "BB.lower",
            "BB.upper",
            "BB.basis",
            "volume",
            "change",
            "close",
            "high",
            "low"
        ]
        
        # Build the request data
        request_data = {
            "symbols": {
                "tickers": [symbol],
                "query": {
                    "types": []
                }
            },
            "columns": indicators
        }
        
        try:
            response = self.session.post(
                f"https://scanner.tradingview.com/{interval}/scan",
                json=request_data
            )
            response.raise_for_status()
            data = response.json()
            
            # Process and interpret the technical indicators
            if "data" in data and len(data["data"]) > 0:
                raw_data = data["data"][0]["d"]
                
                # Map raw data to the requested indicators
                result = {}
                for i, indicator in enumerate(indicators):
                    if i < len(raw_data):
                        result[indicator] = raw_data[i]
                
                # Add interpretation of technical analysis signals
                signals = self._interpret_technical_signals(result)
                result["signals"] = signals
                
                # Calculate overall sentiment
                bullish_count = sum(1 for signal in signals if signal["signal"] == "bullish")
                bearish_count = sum(1 for signal in signals if signal["signal"] == "bearish")
                neutral_count = sum(1 for signal in signals if signal["signal"] == "neutral")
                
                if bullish_count > bearish_count + neutral_count:
                    sentiment = "Strong Buy"
                elif bullish_count > bearish_count:
                    sentiment = "Buy"
                elif bearish_count > bullish_count + neutral_count:
                    sentiment = "Strong Sell"
                elif bearish_count > bullish_count:
                    sentiment = "Sell"
                else:
                    sentiment = "Neutral"
                
                result["overall_sentiment"] = sentiment
                result["interval"] = interval
                result["timestamp"] = datetime.now().isoformat()
                
                return result
            else:
                return {"error": "No data returned for the specified symbol"}
        except requests.exceptions.RequestException as e:
            return {"error": f"Error fetching technical analysis: {str(e)}"}
    
    def get_crypto_market_summary(self) -> Dict:
        """
        Get an overall summary of the cryptocurrency market
        
        Returns:
        - Dictionary containing market summary data
        """
        try:
            # Get data for key cryptocurrencies
            major_cryptos = ["BTCUSDT", "ETHUSDT", "BNBUSDT", "SOLUSDT", "ADAUSDT", "XRPUSDT"]
            
            results = {}
            for crypto in major_cryptos:
                symbol = f"BINANCE:{crypto}"
                analysis = self.get_crypto_technical_analysis(symbol)
                
                if "error" not in analysis:
                    results[crypto.replace("USDT", "")] = {
                        "price": analysis.get("close"),
                        "change_24h": analysis.get("change"),
                        "sentiment": analysis.get("overall_sentiment"),
                        "volume": analysis.get("volume")
                    }
            
            # Get overall crypto market cap
            market_data = self.get_crypto_screener()
            
            return {
                "timestamp": datetime.now().isoformat(),
                "major_cryptocurrencies": results,
                "market_data": market_data
            }
        except Exception as e:
            return {"error": f"Error generating market summary: {str(e)}"}
    
    def _interpret_technical_signals(self, indicators: Dict) -> List[Dict]:
        """
        Interpret technical indicators into actionable signals
        
        Parameters:
        - indicators: Dictionary of technical indicators
        
        Returns:
        - List of interpreted signals with indicator name, signal type and description
        """
        signals = []
        
        # Interpret TradingView's recommendation
        tv_recommend = indicators.get("Recommend.All")
        if tv_recommend is not None:
            signal = "neutral"
            if tv_recommend > 0.5:
                signal = "bullish"
            elif tv_recommend < -0.5:
                signal = "bearish"
                
            signals.append({
                "indicator": "TradingView Recommendation",
                "signal": signal,
                "value": tv_recommend,
                "description": f"TradingView's aggregate recommendation is {signal.upper()}"
            })
        
        # Interpret RSI (Relative Strength Index)
        rsi = indicators.get("RSI")
        if rsi is not None:
            signal = "neutral"
            if rsi > 70:
                signal = "bearish"
            elif rsi < 30:
                signal = "bullish"
                
            signals.append({
                "indicator": "RSI",
                "signal": signal,
                "value": rsi,
                "description": f"RSI at {rsi:.2f} is {signal.upper()}"
            })
        
        # Interpret MACD (Moving Average Convergence Divergence)
        macd = indicators.get("MACD.macd")
        macd_signal = indicators.get("MACD.signal")
        if macd is not None and macd_signal is not None:
            signal = "neutral"
            description = "MACD and Signal lines are close"
            
            if macd > macd_signal:
                signal = "bullish"
                description = "MACD is above Signal line"
            elif macd < macd_signal:
                signal = "bearish"
                description = "MACD is below Signal line"
                
            signals.append({
                "indicator": "MACD",
                "signal": signal,
                "value": {"macd": macd, "signal": macd_signal},
                "description": description
            })
        
        # Interpret Moving Averages
        price = indicators.get("close")
        sma20 = indicators.get("SMA20")
        sma50 = indicators.get("SMA50")
        sma200 = indicators.get("SMA200")
        
        if price is not None and sma20 is not None:
            signal = "neutral"
            if price > sma20:
                signal = "bullish"
            elif price < sma20:
                signal = "bearish"
                
            signals.append({
                "indicator": "SMA20",
                "signal": signal,
                "value": {"price": price, "sma20": sma20},
                "description": f"Price is {'above' if signal == 'bullish' else 'below'} the 20-day SMA"
            })
            
        if price is not None and sma50 is not None:
            signal = "neutral"
            if price > sma50:
                signal = "bullish"
            elif price < sma50:
                signal = "bearish"
                
            signals.append({
                "indicator": "SMA50",
                "signal": signal,
                "value": {"price": price, "sma50": sma50},
                "description": f"Price is {'above' if signal == 'bullish' else 'below'} the 50-day SMA"
            })
            
        if price is not None and sma200 is not None:
            signal = "neutral"
            if price > sma200:
                signal = "bullish"
            elif price < sma200:
                signal = "bearish"
                
            signals.append({
                "indicator": "SMA200",
                "signal": signal,
                "value": {"price": price, "sma200": sma200},
                "description": f"Price is {'above' if signal == 'bullish' else 'below'} the 200-day SMA"
            })
        
        # Interpret Bollinger Bands
        bb_upper = indicators.get("BB.upper")
        bb_lower = indicators.get("BB.lower")
        if price is not None and bb_upper is not None and bb_lower is not None:
            signal = "neutral"
            description = "Price is within Bollinger Bands"
            
            if price > bb_upper:
                signal = "bearish"
                description = "Price is above the upper Bollinger Band (overbought)"
            elif price < bb_lower:
                signal = "bullish"
                description = "Price is below the lower Bollinger Band (oversold)"
                
            signals.append({
                "indicator": "Bollinger Bands",
                "signal": signal,
                "value": {"price": price, "upper": bb_upper, "lower": bb_lower},
                "description": description
            })
        
        # Interpret Stochastic Oscillator
        stoch_k = indicators.get("Stoch.K")
        stoch_d = indicators.get("Stoch.D")
        stoch_k_prev = indicators.get("Stoch.K[1]")
        stoch_d_prev = indicators.get("Stoch.D[1]")
        
        if stoch_k is not None and stoch_d is not None and stoch_k_prev is not None and stoch_d_prev is not None:
            signal = "neutral"
            description = "Stochastic is in neutral zone"
            
            # Overbought/Oversold
            if stoch_k > 80 and stoch_d > 80:
                signal = "bearish"
                description = "Stochastic is in overbought territory"
            elif stoch_k < 20 and stoch_d < 20:
                signal = "bullish"
                description = "Stochastic is in oversold territory"
            
            # Crossover
            if stoch_k_prev < stoch_d_prev and stoch_k > stoch_d:
                signal = "bullish"
                description = "Stochastic K crossed above D (bullish crossover)"
            elif stoch_k_prev > stoch_d_prev and stoch_k < stoch_d:
                signal = "bearish"
                description = "Stochastic K crossed below D (bearish crossover)"
                
            signals.append({
                "indicator": "Stochastic",
                "signal": signal,
                "value": {"k": stoch_k, "d": stoch_d},
                "description": description
            })
        
        return signals

# Helper functions to use the TradingView API for cryptocurrency analysis

def get_tradingview_crypto_analysis(symbol: str, interval: str = "1d") -> Dict:
    """
    Get comprehensive technical analysis for a cryptocurrency from TradingView
    
    Parameters:
    - symbol: Cryptocurrency symbol (e.g., "BTC", "ETH", "BTCUSDT")
    - interval: Time interval (e.g., "1d", "4h", "1h", "15m")
    
    Returns:
    - Dictionary containing technical analysis indicators and interpreted signals
    """
    api = TradingViewAPI()
    
    # Clean up the symbol format
    symbol = symbol.upper().replace("-USD", "").replace("USD", "")
    
    # First try the standard format
    tv_symbol = f"BINANCE:{symbol}USDT"
    result = api.get_crypto_technical_analysis(tv_symbol, interval)
    
    # If it fails, try another exchange or format
    if "error" in result:
        # Try Coinbase exchange
        tv_symbol = f"COINBASE:{symbol}USD"
        result = api.get_crypto_technical_analysis(tv_symbol, interval)
        
        # If still failing, try with BTC pairing
        if "error" in result and symbol != "BTC":
            tv_symbol = f"BINANCE:{symbol}BTC"
            result = api.get_crypto_technical_analysis(tv_symbol, interval)
    
    # Add analyzed time intervals
    if "error" not in result:
        result["symbol"] = symbol
        result["tv_symbol"] = tv_symbol
        
        # Get multiple timeframes for a more comprehensive analysis
        timeframes = {}
        if interval != "1d":
            timeframes["1d"] = api.get_crypto_technical_analysis(tv_symbol, "1d")
        if interval != "4h":
            timeframes["4h"] = api.get_crypto_technical_analysis(tv_symbol, "4h")
        if interval != "1h":
            timeframes["1h"] = api.get_crypto_technical_analysis(tv_symbol, "1h")
            
        result["additional_timeframes"] = timeframes
    
    return result

def get_tradingview_crypto_market() -> Dict:
    """
    Get cryptocurrency market overview from TradingView
    
    Returns:
    - Dictionary containing market overview data
    """
    api = TradingViewAPI()
    return api.get_crypto_market_summary()

def get_tradingview_multi_timeframe_analysis(symbol: str) -> Dict:
    """
    Perform multi-timeframe analysis for a cryptocurrency
    
    Parameters:
    - symbol: Cryptocurrency symbol (e.g., "BTC", "ETH")
    
    Returns:
    - Dictionary containing multi-timeframe analysis
    """
    api = TradingViewAPI()
    
    # Clean up symbol format
    symbol = symbol.upper().replace("-USD", "").replace("USD", "")
    tv_symbol = f"BINANCE:{symbol}USDT"
    
    # Analyze different timeframes
    timeframes = {
        "1d": api.get_crypto_technical_analysis(tv_symbol, "1d"),
        "4h": api.get_crypto_technical_analysis(tv_symbol, "4h"),
        "1h": api.get_crypto_technical_analysis(tv_symbol, "1h"),
        "15m": api.get_crypto_technical_analysis(tv_symbol, "15m")
    }
    
    # Count bullish/bearish signals across timeframes
    signal_counts = {"bullish": 0, "bearish": 0, "neutral": 0}
    
    for tf, analysis in timeframes.items():
        if "error" not in analysis and "signals" in analysis:
            for signal in analysis["signals"]:
                signal_type = signal.get("signal", "neutral")
                signal_counts[signal_type] = signal_counts.get(signal_type, 0) + 1
    
    # Determine overall sentiment across timeframes
    if signal_counts["bullish"] > signal_counts["bearish"] * 2:
        overall_sentiment = "Strong Buy"
    elif signal_counts["bullish"] > signal_counts["bearish"]:
        overall_sentiment = "Buy"
    elif signal_counts["bearish"] > signal_counts["bullish"] * 2:
        overall_sentiment = "Strong Sell"
    elif signal_counts["bearish"] > signal_counts["bullish"]:
        overall_sentiment = "Sell"
    else:
        overall_sentiment = "Neutral"
    
    # Compile the final multi-timeframe analysis
    result = {
        "symbol": symbol,
        "tv_symbol": tv_symbol,
        "timestamp": datetime.now().isoformat(),
        "timeframes": timeframes,
        "signal_counts": signal_counts,
        "overall_sentiment": overall_sentiment
    }
    
    return result

if __name__ == "__main__":
    # Test the TradingView API functionality
    symbol = "BTC"
    print(f"Testing TradingView API with {symbol}")
    
    api = TradingViewAPI()
    
    # Test symbol search
    print("\nSearching for symbols:")
    symbols = api.search_symbols(symbol)
    print(json.dumps(symbols[:3], indent=2))
    
    # Test technical analysis
    print("\nGetting technical analysis:")
    analysis = get_tradingview_crypto_analysis(symbol)
    print(json.dumps({
        "symbol": analysis.get("symbol"),
        "overall_sentiment": analysis.get("overall_sentiment"),
        "signals_count": len(analysis.get("signals", []))
    }, indent=2))
    
    # Test market summary
    print("\nGetting market summary:")
    market = get_tradingview_crypto_market()
    print(json.dumps({
        "timestamp": market.get("timestamp"),
        "cryptocurrencies": list(market.get("major_cryptocurrencies", {}).keys())
    }, indent=2)) 