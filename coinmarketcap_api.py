import os
import requests
import json
from typing import Dict, List, Optional, Any
from datetime import datetime

# CoinMarketCap API base URL
CMC_API_BASE_URL = "https://pro-api.coinmarketcap.com/v1"

class CoinMarketCapAPI:
    """
    Client for interacting with CoinMarketCap's REST API
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the CoinMarketCap API client
        
        Parameters:
        - api_key: API key for authenticated requests (required)
        """
        self.api_key = api_key or os.environ.get("COINMARKETCAP_API_KEY")
        if not self.api_key:
            raise ValueError("CoinMarketCap API key is required")
            
        self.session = requests.Session()
        self.session.headers.update({
            "X-CMC_PRO_API_KEY": self.api_key,
            "Accept": "application/json"
        })
    
    def get_latest_listings(self, limit: int = 100, convert: str = "USD") -> Dict:
        """
        Get latest cryptocurrency listings with market data
        
        Parameters:
        - limit: Number of cryptocurrencies to return (default 100, max 5000)
        - convert: Currency to convert prices to (default USD)
        
        Returns:
        - Dictionary containing cryptocurrency listings with market data
        """
        url = f"{CMC_API_BASE_URL}/cryptocurrency/listings/latest"
        params = {
            "limit": limit,
            "convert": convert
        }
        
        try:
            response = self.session.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            
            if "data" in data:
                return {
                    "status": data.get("status", {}),
                    "data": data.get("data", []),
                    "timestamp": datetime.now().isoformat()
                }
            else:
                return {"error": "No data returned from CoinMarketCap API"}
        except requests.exceptions.RequestException as e:
            return {"error": f"Error fetching latest listings: {str(e)}"}
    
    def get_cryptocurrency_info(self, symbol: str) -> Dict:
        """
        Get metadata about a cryptocurrency
        
        Parameters:
        - symbol: Cryptocurrency symbol (e.g., "BTC", "ETH")
        
        Returns:
        - Dictionary containing cryptocurrency metadata
        """
        url = f"{CMC_API_BASE_URL}/cryptocurrency/info"
        params = {
            "symbol": symbol
        }
        
        try:
            response = self.session.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            
            if "data" in data and symbol in data["data"]:
                return {
                    "status": data.get("status", {}),
                    "data": data["data"][symbol],
                    "timestamp": datetime.now().isoformat()
                }
            else:
                return {"error": f"No metadata found for {symbol}"}
        except requests.exceptions.RequestException as e:
            return {"error": f"Error fetching cryptocurrency info: {str(e)}"}
    
    def get_cryptocurrency_quotes(self, symbol: str, convert: str = "USD") -> Dict:
        """
        Get latest market quotes for a cryptocurrency
        
        Parameters:
        - symbol: Cryptocurrency symbol (e.g., "BTC", "ETH")
        - convert: Currency to convert prices to (default USD)
        
        Returns:
        - Dictionary containing cryptocurrency quotes data
        """
        url = f"{CMC_API_BASE_URL}/cryptocurrency/quotes/latest"
        params = {
            "symbol": symbol,
            "convert": convert
        }
        
        try:
            response = self.session.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            
            if "data" in data and symbol in data["data"]:
                return {
                    "status": data.get("status", {}),
                    "data": data["data"][symbol],
                    "timestamp": datetime.now().isoformat()
                }
            else:
                return {"error": f"No quote data found for {symbol}"}
        except requests.exceptions.RequestException as e:
            return {"error": f"Error fetching cryptocurrency quotes: {str(e)}"}
    
    def get_global_metrics(self, convert: str = "USD") -> Dict:
        """
        Get global cryptocurrency market metrics
        
        Parameters:
        - convert: Currency to convert prices to (default USD)
        
        Returns:
        - Dictionary containing global market data
        """
        url = f"{CMC_API_BASE_URL}/global-metrics/quotes/latest"
        params = {
            "convert": convert
        }
        
        try:
            response = self.session.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            
            if "data" in data:
                return {
                    "status": data.get("status", {}),
                    "data": data.get("data", {}),
                    "timestamp": datetime.now().isoformat()
                }
            else:
                return {"error": "No global metrics data returned"}
        except requests.exceptions.RequestException as e:
            return {"error": f"Error fetching global metrics: {str(e)}"}
    
    def get_cryptocurrency_ohlcv(self, symbol: str, convert: str = "USD", time_period: str = "daily", count: int = 30) -> Dict:
        """
        Get OHLCV (Open, High, Low, Close, Volume) for a cryptocurrency
        
        Parameters:
        - symbol: Cryptocurrency symbol (e.g., "BTC", "ETH")
        - convert: Currency to convert prices to (default USD)
        - time_period: Time period for data (hourly, daily, weekly, monthly, yearly, etc.)
        - count: Number of data points to return
        
        Returns:
        - Dictionary containing OHLCV data
        """
        url = f"{CMC_API_BASE_URL}/cryptocurrency/ohlcv/latest"
        params = {
            "symbol": symbol,
            "convert": convert,
            "time_period": time_period,
            "count": count
        }
        
        try:
            response = self.session.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            
            if "data" in data and symbol in data["data"]:
                return {
                    "status": data.get("status", {}),
                    "data": data["data"][symbol],
                    "timestamp": datetime.now().isoformat()
                }
            else:
                return {"error": f"No OHLCV data found for {symbol}"}
        except requests.exceptions.RequestException as e:
            return {"error": f"Error fetching OHLCV data: {str(e)}"}
    
    def get_cryptocurrency_market_pairs(self, symbol: str, limit: int = 100) -> Dict:
        """
        Get market pairs for a cryptocurrency (exchanges, trading pairs, etc.)
        
        Parameters:
        - symbol: Cryptocurrency symbol (e.g., "BTC", "ETH")
        - limit: Number of market pairs to return
        
        Returns:
        - Dictionary containing market pairs data
        """
        url = f"{CMC_API_BASE_URL}/cryptocurrency/market-pairs/latest"
        params = {
            "symbol": symbol,
            "limit": limit
        }
        
        try:
            response = self.session.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            
            if "data" in data and symbol in data["data"]:
                return {
                    "status": data.get("status", {}),
                    "data": data["data"][symbol],
                    "timestamp": datetime.now().isoformat()
                }
            else:
                return {"error": f"No market pairs data found for {symbol}"}
        except requests.exceptions.RequestException as e:
            return {"error": f"Error fetching market pairs: {str(e)}"}

# Helper functions to use the CoinMarketCap API

def get_cmc_crypto_data(symbol: str) -> Dict:
    """
    Get comprehensive data for a cryptocurrency from CoinMarketCap
    
    Parameters:
    - symbol: Cryptocurrency symbol (e.g., "BTC", "ETH")
    
    Returns:
    - Dictionary containing comprehensive cryptocurrency data
    """
    api = CoinMarketCapAPI()
    
    # Clean up symbol format
    symbol = symbol.upper().replace("-USD", "").replace("USD", "")
    
    # Get metadata
    info = api.get_cryptocurrency_info(symbol)
    
    # Get latest quotes
    quotes = api.get_cryptocurrency_quotes(symbol)
    
    # Get market pairs data
    market_pairs = api.get_cryptocurrency_market_pairs(symbol)
    
    # Get historical OHLCV data
    ohlcv = api.get_cryptocurrency_ohlcv(symbol)
    
    # Compile all data
    result = {
        "symbol": symbol,
        "timestamp": datetime.now().isoformat(),
        "info": info.get("data", {}) if "error" not in info else {"error": info.get("error")},
        "quotes": quotes.get("data", {}) if "error" not in quotes else {"error": quotes.get("error")},
        "market_pairs": market_pairs.get("data", {}) if "error" not in market_pairs else {"error": market_pairs.get("error")},
        "ohlcv": ohlcv.get("data", {}) if "error" not in ohlcv else {"error": ohlcv.get("error")}
    }
    
    return result

def get_cmc_crypto_market_overview() -> Dict:
    """
    Get cryptocurrency market overview from CoinMarketCap
    
    Returns:
    - Dictionary containing market overview data
    """
    api = CoinMarketCapAPI()
    
    # Get global metrics
    global_metrics = api.get_global_metrics()
    
    # Get top 20 cryptocurrencies
    top_cryptos = api.get_latest_listings(limit=20)
    
    return {
        "timestamp": datetime.now().isoformat(),
        "global_metrics": global_metrics.get("data", {}) if "error" not in global_metrics else {"error": global_metrics.get("error")},
        "top_cryptocurrencies": top_cryptos.get("data", []) if "error" not in top_cryptos else {"error": top_cryptos.get("error")}
    }

def get_cmc_crypto_analysis(symbol: str) -> Dict:
    """
    Analyze a cryptocurrency with data from CoinMarketCap
    
    Parameters:
    - symbol: Cryptocurrency symbol (e.g., "BTC", "ETH")
    
    Returns:
    - Dictionary containing analyzed cryptocurrency data
    """
    api = CoinMarketCapAPI()
    
    # Clean up symbol format
    symbol = symbol.upper().replace("-USD", "").replace("USD", "")
    
    # Get cryptocurrency quotes data
    quotes = api.get_cryptocurrency_quotes(symbol)
    
    if "error" in quotes:
        return quotes
    
    # Extract quote data
    quote_data = quotes.get("data", {}).get("quote", {}).get("USD", {})
    
    # Calculate metrics and determine sentiment
    price = quote_data.get("price", 0)
    market_cap = quote_data.get("market_cap", 0)
    volume_24h = quote_data.get("volume_24h", 0)
    percent_change_1h = quote_data.get("percent_change_1h", 0)
    percent_change_24h = quote_data.get("percent_change_24h", 0)
    percent_change_7d = quote_data.get("percent_change_7d", 0)
    percent_change_30d = quote_data.get("percent_change_30d", 0)
    
    # Determine sentiment based on price changes
    if percent_change_24h > 10 and percent_change_7d > 20:
        sentiment = "Strong Buy"
    elif percent_change_24h > 5 and percent_change_7d > 10:
        sentiment = "Buy"
    elif percent_change_24h < -10 and percent_change_7d < -20:
        sentiment = "Strong Sell"
    elif percent_change_24h < -5 and percent_change_7d < -10:
        sentiment = "Sell"
    else:
        sentiment = "Hold"
    
    # Calculate volume to market cap ratio (liquidity indicator)
    volume_to_mcap_ratio = volume_24h / market_cap if market_cap > 0 else 0
    
    # Analyze price momentum across different timeframes
    momentum_signals = []
    
    if percent_change_1h > 0:
        momentum_signals.append({"timeframe": "1h", "signal": "positive", "value": percent_change_1h})
    else:
        momentum_signals.append({"timeframe": "1h", "signal": "negative", "value": percent_change_1h})
    
    if percent_change_24h > 0:
        momentum_signals.append({"timeframe": "24h", "signal": "positive", "value": percent_change_24h})
    else:
        momentum_signals.append({"timeframe": "24h", "signal": "negative", "value": percent_change_24h})
    
    if percent_change_7d > 0:
        momentum_signals.append({"timeframe": "7d", "signal": "positive", "value": percent_change_7d})
    else:
        momentum_signals.append({"timeframe": "7d", "signal": "negative", "value": percent_change_7d})
    
    if percent_change_30d > 0:
        momentum_signals.append({"timeframe": "30d", "signal": "positive", "value": percent_change_30d})
    else:
        momentum_signals.append({"timeframe": "30d", "signal": "negative", "value": percent_change_30d})
    
    # Compile analysis result
    result = {
        "symbol": symbol,
        "name": quotes.get("data", {}).get("name", "Unknown"),
        "timestamp": datetime.now().isoformat(),
        "price_usd": price,
        "market_cap_usd": market_cap,
        "volume_24h_usd": volume_24h,
        "volume_to_mcap_ratio": volume_to_mcap_ratio,
        "percent_changes": {
            "1h": percent_change_1h,
            "24h": percent_change_24h,
            "7d": percent_change_7d,
            "30d": percent_change_30d
        },
        "momentum_signals": momentum_signals,
        "overall_sentiment": sentiment
    }
    
    return result

def compare_cmc_cryptocurrencies(symbols: List[str]) -> Dict:
    """
    Compare multiple cryptocurrencies using CoinMarketCap data
    
    Parameters:
    - symbols: List of cryptocurrency symbols (e.g., ["BTC", "ETH", "XRP"])
    
    Returns:
    - Dictionary containing comparison data
    """
    api = CoinMarketCapAPI()
    
    # Clean up symbols
    symbols = [symbol.upper().replace("-USD", "").replace("USD", "") for symbol in symbols]
    
    # Get quotes for all symbols
    symbol_string = ",".join(symbols)
    url = f"{CMC_API_BASE_URL}/cryptocurrency/quotes/latest"
    params = {
        "symbol": symbol_string,
        "convert": "USD"
    }
    
    try:
        response = api.session.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        
        if "data" not in data:
            return {"error": "No data returned from CoinMarketCap API"}
        
        # Process each cryptocurrency's data
        comparison = {}
        for symbol in symbols:
            if symbol in data["data"]:
                crypto_data = data["data"][symbol]
                quote_data = crypto_data.get("quote", {}).get("USD", {})
                
                comparison[symbol] = {
                    "name": crypto_data.get("name", "Unknown"),
                    "price_usd": quote_data.get("price", 0),
                    "market_cap_usd": quote_data.get("market_cap", 0),
                    "volume_24h_usd": quote_data.get("volume_24h", 0),
                    "percent_change_24h": quote_data.get("percent_change_24h", 0),
                    "percent_change_7d": quote_data.get("percent_change_7d", 0)
                }
            else:
                comparison[symbol] = {"error": f"No data found for {symbol}"}
        
        return {
            "timestamp": datetime.now().isoformat(),
            "comparison_data": comparison
        }
        
    except requests.exceptions.RequestException as e:
        return {"error": f"Error comparing cryptocurrencies: {str(e)}"}

def get_cmc_investment_recommendation(symbol: str, risk_tolerance: str = "moderate") -> Dict:
    """
    Generate comprehensive investment recommendation for a cryptocurrency based on CoinMarketCap data
    
    Parameters:
    - symbol: Cryptocurrency symbol (e.g., "BTC", "ETH")
    - risk_tolerance: User's risk tolerance level (low, moderate, high)
    
    Returns:
    - Dictionary containing detailed investment recommendation
    """
    api = CoinMarketCapAPI()
    
    # Clean up symbol format
    symbol = symbol.upper().replace("-USD", "").replace("USD", "")
    
    # Get cryptocurrency quotes data
    quotes = api.get_cryptocurrency_quotes(symbol)
    
    if "error" in quotes:
        return quotes
    
    # Get cryptocurrency info for additional data
    info = api.get_cryptocurrency_info(symbol)
    
    # Extract quote data
    crypto_data = quotes.get("data", {})
    quote_data = crypto_data.get("quote", {}).get("USD", {})
    
    # Extract key metrics
    price = quote_data.get("price", 0)
    market_cap = quote_data.get("market_cap", 0)
    volume_24h = quote_data.get("volume_24h", 0)
    percent_change_1h = quote_data.get("percent_change_1h", 0)
    percent_change_24h = quote_data.get("percent_change_24h", 0)
    percent_change_7d = quote_data.get("percent_change_7d", 0)
    percent_change_30d = quote_data.get("percent_change_30d", 0)
    percent_change_60d = quote_data.get("percent_change_60d", 0) if "percent_change_60d" in quote_data else None
    percent_change_90d = quote_data.get("percent_change_90d", 0) if "percent_change_90d" in quote_data else None
    
    # Calculate volume to market cap ratio (liquidity indicator)
    volume_to_mcap_ratio = volume_24h / market_cap if market_cap > 0 else 0
    
    # Get crypto dominance if available
    market_dominance = quote_data.get("market_cap_dominance", 0)
    
    # Define risk profiles based on market cap
    risk_profiles = {
        "low": market_cap > 50000000000,  # $50B+ (e.g., BTC, ETH)
        "moderate": market_cap > 5000000000,  # $5B+
        "high": market_cap > 1000000000,  # $1B+
        "very_high": market_cap <= 1000000000  # under $1B
    }
    
    # Calculate technical scores
    technical_score = 0
    
    # Short-term momentum (1h, 24h)
    if percent_change_1h > 1:
        technical_score += 1
    elif percent_change_1h < -1:
        technical_score -= 1
        
    if percent_change_24h > 5:
        technical_score += 2
    elif percent_change_24h > 2:
        technical_score += 1
    elif percent_change_24h < -5:
        technical_score -= 2
    elif percent_change_24h < -2:
        technical_score -= 1
    
    # Medium-term momentum (7d, 30d)
    if percent_change_7d > 10:
        technical_score += 2
    elif percent_change_7d > 5:
        technical_score += 1
    elif percent_change_7d < -10:
        technical_score -= 2
    elif percent_change_7d < -5:
        technical_score -= 1
        
    if percent_change_30d > 20:
        technical_score += 2
    elif percent_change_30d > 10:
        technical_score += 1
    elif percent_change_30d < -20:
        technical_score -= 2
    elif percent_change_30d < -10:
        technical_score -= 1
    
    # Longer-term trends if available
    if percent_change_60d is not None:
        if percent_change_60d > 50:
            technical_score += 1
        elif percent_change_60d < -50:
            technical_score -= 1
            
    if percent_change_90d is not None:
        if percent_change_90d > 100:
            technical_score += 1
        elif percent_change_90d < -50:
            technical_score -= 1
    
    # Liquidity bonus for highly liquid assets
    if volume_to_mcap_ratio > 0.1:  # Over 10% of market cap traded daily
        technical_score += 1
    elif volume_to_mcap_ratio < 0.01:  # Less than 1% of market cap traded daily
        technical_score -= 1
    
    # Market dominance bonus for major cryptocurrencies
    if market_dominance > 40:  # BTC-like dominance
        technical_score += 2
    elif market_dominance > 15:  # ETH-like dominance
        technical_score += 1
    
    # Determine recommendation based on technical score and risk tolerance
    recommendation = ""
    confidence_score = 0
    
    if risk_tolerance == "low":
        if technical_score >= 6 and risk_profiles["low"]:
            recommendation = "Strong Buy"
            confidence_score = 90
        elif technical_score >= 4 and risk_profiles["low"]:
            recommendation = "Buy"
            confidence_score = 70
        elif technical_score <= -6:
            recommendation = "Strong Sell"
            confidence_score = 85
        elif technical_score <= -4:
            recommendation = "Sell"
            confidence_score = 65
        elif technical_score >= 2 and risk_profiles["moderate"]:
            recommendation = "Mild Buy"
            confidence_score = 55
        elif technical_score <= -2:
            recommendation = "Mild Sell"
            confidence_score = 55
        else:
            recommendation = "Hold"
            confidence_score = 60
            
    elif risk_tolerance == "moderate":
        if technical_score >= 5:
            recommendation = "Strong Buy"
            confidence_score = 85
        elif technical_score >= 3:
            recommendation = "Buy"
            confidence_score = 70
        elif technical_score <= -5:
            recommendation = "Strong Sell"
            confidence_score = 80
        elif technical_score <= -3:
            recommendation = "Sell"
            confidence_score = 65
        elif technical_score >= 1:
            recommendation = "Mild Buy"
            confidence_score = 55
        elif technical_score <= -1:
            recommendation = "Mild Sell"
            confidence_score = 55
        else:
            recommendation = "Hold"
            confidence_score = 60
            
    else:  # high risk tolerance
        if technical_score >= 4:
            recommendation = "Strong Buy"
            confidence_score = 80
        elif technical_score >= 2:
            recommendation = "Buy"
            confidence_score = 65
        elif technical_score <= -4:
            recommendation = "Strong Sell"
            confidence_score = 75
        elif technical_score <= -2:
            recommendation = "Sell"
            confidence_score = 60
        elif technical_score >= 1:
            recommendation = "Mild Buy"
            confidence_score = 55
        elif technical_score <= -1:
            recommendation = "Mild Sell"
            confidence_score = 55
        else:
            recommendation = "Hold"
            confidence_score = 60
    
    # Calculate risk level
    if risk_profiles["low"]:
        risk_level = "Low to Moderate"
    elif risk_profiles["moderate"]:
        risk_level = "Moderate"
    elif risk_profiles["high"]:
        risk_level = "High"
    else:
        risk_level = "Very High"
    
    # Calculate potential upside and downside based on volatility
    volatility_factor = abs(percent_change_30d) / 30  # Daily volatility approximation
    
    potential_upside = None
    potential_downside = None
    
    if volatility_factor > 0:
        # Higher potential returns for favorable technical scores
        if technical_score > 0:
            upside_multiplier = 1 + (technical_score * 0.5)  # Scaled based on technical strength
            potential_upside = round(volatility_factor * 30 * upside_multiplier, 2)  # 30-day projection
        else:
            # Even with negative technical score, some upside is possible
            potential_upside = round(volatility_factor * 15, 2)  # Reduced upside projection
            
        # Higher potential losses for unfavorable technical scores
        if technical_score < 0:
            downside_multiplier = 1 + (abs(technical_score) * 0.5)  # Scaled based on technical weakness
            potential_downside = round(volatility_factor * 30 * downside_multiplier, 2)  # 30-day projection
        else:
            # Even with positive technical score, some downside is possible
            potential_downside = round(volatility_factor * 15, 2)  # Reduced downside projection
    
    # Generate investment thesis based on recommendation
    investment_thesis = ""
    risks = ""
    
    if "Buy" in recommendation:
        investment_thesis = f"{crypto_data.get('name', symbol)} shows {percent_change_7d:.2f}% growth over the past week"
        
        if percent_change_24h > 0:
            investment_thesis += f" and {percent_change_24h:.2f}% in the last 24 hours"
            
        if percent_change_30d > 0:
            investment_thesis += f", with sustained momentum of {percent_change_30d:.2f}% over the past month"
        
        investment_thesis += ". "
        
        if volume_to_mcap_ratio > 0.05:
            investment_thesis += f"Strong trading volume at {volume_24h/1000000:.2f}M USD represents good liquidity. "
            
        if market_dominance and market_dominance > 1:
            investment_thesis += f"Market dominance of {market_dominance:.2f}% shows significant market presence. "
            
        # Add info from CoinMarketCap if available
        if "error" not in info:
            tags = info.get("data", {}).get("tags", [])
            if tags and len(tags) > 0:
                investment_thesis += f"Tagged as {', '.join(tags[:3])} on CoinMarketCap. "
    
    elif "Sell" in recommendation:
        investment_thesis = f"{crypto_data.get('name', symbol)} shows "
        
        if percent_change_7d < 0:
            investment_thesis += f"{percent_change_7d:.2f}% decline over the past week"
            
        if percent_change_24h < 0:
            if "decline" in investment_thesis:
                investment_thesis += f" and {percent_change_24h:.2f}% in the last 24 hours"
            else:
                investment_thesis += f"{percent_change_24h:.2f}% decline in the last 24 hours"
                
        if percent_change_30d < 0:
            investment_thesis += f", with a significant downtrend of {percent_change_30d:.2f}% over the past month"
        
        investment_thesis += ". "
        
        if volume_to_mcap_ratio < 0.01:
            investment_thesis += "Low trading volume relative to market cap may indicate reduced interest. "
    
    else:  # Hold
        investment_thesis = f"{crypto_data.get('name', symbol)} is showing mixed signals with "
        
        if percent_change_24h > 0:
            investment_thesis += f"{percent_change_24h:.2f}% growth in the last 24 hours"
        else:
            investment_thesis += f"{percent_change_24h:.2f}% change in the last 24 hours"
            
        if percent_change_7d > 0:
            investment_thesis += f" and {percent_change_7d:.2f}% over the past week"
        else:
            investment_thesis += f" and {percent_change_7d:.2f}% over the past week"
        
        investment_thesis += ". Current technical indicators don't show a strong directional bias. "
    
    # Generate risk assessment
    if risk_profiles["low"]:
        risks = f"As one of the larger cryptocurrencies with a market cap of ${market_cap/1000000000:.2f}B, {crypto_data.get('name', symbol)} has relatively lower risk compared to smaller altcoins. "
    elif risk_profiles["moderate"]:
        risks = f"With a market cap of ${market_cap/1000000000:.2f}B, {crypto_data.get('name', symbol)} has moderate volatility and risk exposure. "
    elif risk_profiles["high"]:
        risks = f"{crypto_data.get('name', symbol)} has a market cap of ${market_cap/1000000000:.2f}B, which exposes it to higher volatility and risk than larger cryptocurrencies. "
    else:
        risks = f"With a smaller market cap of ${market_cap/1000000:.2f}M, {crypto_data.get('name', symbol)} is subject to high volatility and significant risk. "
    
    risks += f"Daily trading volume of ${volume_24h/1000000:.2f}M "
    
    if volume_to_mcap_ratio > 0.1:
        risks += "indicates strong liquidity, which can help mitigate some execution risks. "
    elif volume_to_mcap_ratio > 0.05:
        risks += "indicates adequate liquidity for moderate position sizes. "
    else:
        risks += "indicates potential liquidity constraints, which could amplify volatility. "
    
    if percent_change_30d > 30 or percent_change_30d < -30:
        risks += f"Recent 30-day volatility of {abs(percent_change_30d):.2f}% suggests significant price swings may continue. "
    
    # Compile the final recommendation
    result = {
        "symbol": symbol,
        "name": crypto_data.get("name", "Unknown"),
        "recommendation": recommendation,
        "confidence_score": confidence_score,
        "technical_score": technical_score,
        "risk_level": risk_level,
        "risk_tolerance": risk_tolerance,
        "current_price": {
            "price": price,
            "currency": "USD"
        },
        "market_metrics": {
            "market_cap": market_cap,
            "volume_24h": volume_24h,
            "volume_to_mcap_ratio": volume_to_mcap_ratio,
            "market_dominance": market_dominance
        },
        "percent_changes": {
            "1h": percent_change_1h,
            "24h": percent_change_24h,
            "7d": percent_change_7d,
            "30d": percent_change_30d,
            "60d": percent_change_60d,
            "90d": percent_change_90d
        },
        "potential_upside": potential_upside,
        "potential_downside": potential_downside,
        "investment_thesis": investment_thesis,
        "risks": risks,
        "timestamp": datetime.now().isoformat(),
        "disclaimer": "This analysis is for informational purposes only and should not be considered financial advice. Always conduct your own research and consider consulting with a financial advisor before making investment decisions. Cryptocurrency investments are especially high-risk and speculative."
    }
    
    return result

if __name__ == "__main__":
    # Test the CoinMarketCap API functionality
    api_key = os.environ.get("COINMARKETCAP_API_KEY")
    if not api_key:
        print("Warning: COINMARKETCAP_API_KEY not found in environment variables")
        print("Please set the API key or provide it directly to the API client")
    else:
        api = CoinMarketCapAPI(api_key)
        
        # Test getting market data
        print("\nTesting CoinMarketCap API with BTC...")
        btc_data = get_cmc_crypto_data("BTC")
        
        if "error" not in btc_data:
            print(f"Successfully retrieved data for {btc_data.get('symbol')}")
            print(f"Current price: ${btc_data.get('quotes', {}).get('quote', {}).get('USD', {}).get('price', 0):.2f}")
        else:
            print(f"Error: {btc_data.get('error')}") 