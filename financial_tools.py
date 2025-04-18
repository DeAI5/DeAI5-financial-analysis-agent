import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json
import os
import requests

def calculate_moving_average(data, window):
    """Calculate moving average from price data"""
    return data.rolling(window=window).mean()

def calculate_rsi(data, window=14):
    """Calculate Relative Strength Index"""
    delta = data.diff()
    gain = delta.where(delta > 0, 0).rolling(window=window).mean()
    loss = -delta.where(delta < 0, 0).rolling(window=window).mean()
    
    rs = gain / loss
    return 100 - (100 / (1 + rs))

def calculate_macd(data, fast=12, slow=26, signal=9):
    """Calculate MACD (Moving Average Convergence Divergence)"""
    fast_ma = data.ewm(span=fast, adjust=False).mean()
    slow_ma = data.ewm(span=slow, adjust=False).mean()
    macd_line = fast_ma - slow_ma
    signal_line = macd_line.ewm(span=signal, adjust=False).mean()
    macd_histogram = macd_line - signal_line
    
    return {
        'macd_line': macd_line,
        'signal_line': signal_line,
        'histogram': macd_histogram
    }

def calculate_bollinger_bands(data, window=20, num_std=2):
    """Calculate Bollinger Bands"""
    rolling_mean = data.rolling(window=window).mean()
    rolling_std = data.rolling(window=window).std()
    
    upper_band = rolling_mean + (rolling_std * num_std)
    lower_band = rolling_mean - (rolling_std * num_std)
    
    return {
        'upper_band': upper_band,
        'middle_band': rolling_mean,
        'lower_band': lower_band
    }

def get_company_financials(ticker):
    """Get key financial statements and ratios for a company"""
    try:
        stock = yf.Ticker(ticker)
        
        # Get financial statements
        income_stmt = stock.income_stmt
        balance_sheet = stock.balance_sheet
        cash_flow = stock.cashflow
        
        # Get key financial metrics and ratios
        info = stock.info
        
        # Create a summary of key financial indicators
        financial_summary = {
            "company_name": info.get('longName', ticker),
            "sector": info.get('sector', 'Unknown'),
            "industry": info.get('industry', 'Unknown'),
            "market_cap": info.get('marketCap', None),
            "pe_ratio": info.get('trailingPE', None),
            "forward_pe": info.get('forwardPE', None),
            "dividend_yield": info.get('dividendYield', None),
            "eps": info.get('trailingEps', None),
            "beta": info.get('beta', None),
            "52w_high": info.get('fiftyTwoWeekHigh', None),
            "52w_low": info.get('fiftyTwoWeekLow', None),
            "profit_margins": info.get('profitMargins', None),
            "return_on_equity": info.get('returnOnEquity', None),
            "debt_to_equity": info.get('debtToEquity', None),
            "price_to_book": info.get('priceToBook', None),
        }
        
        # Get revenue and earnings growth if available
        if not income_stmt.empty and income_stmt.shape[1] >= 2:
            try:
                latest_revenue = income_stmt.loc['Total Revenue'][0]
                prev_revenue = income_stmt.loc['Total Revenue'][1]
                revenue_growth = ((latest_revenue - prev_revenue) / prev_revenue) * 100
                financial_summary["revenue_growth_pct"] = revenue_growth
                
                latest_net_income = income_stmt.loc['Net Income'][0]
                prev_net_income = income_stmt.loc['Net Income'][1]
                net_income_growth = ((latest_net_income - prev_net_income) / prev_net_income) * 100
                financial_summary["net_income_growth_pct"] = net_income_growth
            except (KeyError, IndexError, ZeroDivisionError):
                pass
        
        return financial_summary
        
    except Exception as e:
        return f"Error retrieving financial data for {ticker}: {str(e)}"

def sector_performance():
    """Get performance of different market sectors using sector ETFs"""
    # Major sector ETFs
    sectors = {
        "Technology": "XLK",
        "Healthcare": "XLV", 
        "Financials": "XLF",
        "Consumer Discretionary": "XLY",
        "Consumer Staples": "XLP",
        "Energy": "XLE",
        "Materials": "XLB",
        "Industrials": "XLI",
        "Utilities": "XLU",
        "Real Estate": "XLRE",
        "Communication Services": "XLC"
    }
    
    results = {}
    time_periods = {
        "1_month": "1mo",
        "3_month": "3mo",
        "ytd": "ytd",
        "1_year": "1y"
    }
    
    for sector_name, ticker in sectors.items():
        sector_data = {}
        try:
            # Get current data
            current_data = yf.Ticker(ticker).history(period="5d")
            latest_price = current_data['Close'].iloc[-1]
            previous_price = current_data['Close'].iloc[-2]
            daily_change = ((latest_price - previous_price) / previous_price) * 100
            sector_data["current_price"] = latest_price
            sector_data["daily_change_pct"] = daily_change
            
            # Get performance over different time periods
            for period_name, period_code in time_periods.items():
                period_data = yf.Ticker(ticker).history(period=period_code)
                if not period_data.empty:
                    start_price = period_data['Close'].iloc[0]
                    period_change = ((latest_price - start_price) / start_price) * 100
                    sector_data[f"{period_name}_change_pct"] = period_change
            
            results[sector_name] = sector_data
            
        except Exception as e:
            results[sector_name] = f"Error: {str(e)}"
    
    return results

def get_analyst_recommendations(ticker):
    """Get analyst recommendations for a stock"""
    try:
        stock = yf.Ticker(ticker)
        recommendations = stock.recommendations
        
        if recommendations is None or recommendations.empty:
            return f"No analyst recommendations available for {ticker}"
        
        # Get the most recent recommendations
        recent_recommendations = recommendations.tail(10)
        
        # Calculate recommendation distribution
        if 'To Grade' in recent_recommendations.columns:
            grades = recent_recommendations['To Grade'].value_counts().to_dict()
            return {
                "ticker": ticker,
                "recommendation_counts": grades,
                "recent_changes": recent_recommendations[['Date', 'Firm', 'From Grade', 'To Grade']].to_dict('records')
            }
        else:
            return f"Recommendation data format unexpected for {ticker}"
            
    except Exception as e:
        return f"Error retrieving analyst recommendations for {ticker}: {str(e)}"

def extract_financial_insights(ticker, period="1y"):
    """Comprehensive analysis combining technical, fundamental, and analyst data"""
    try:
        # Get stock data
        stock = yf.Ticker(ticker)
        data = stock.history(period=period)
        
        if data.empty:
            return f"No price data available for {ticker}"
        
        # Get company info
        info = stock.info
        company_name = info.get('longName', ticker)
        
        # Calculate technical indicators
        data['MA50'] = calculate_moving_average(data['Close'], 50)
        data['MA200'] = calculate_moving_average(data['Close'], 200)
        data['RSI'] = calculate_rsi(data['Close'])
        
        macd_data = calculate_macd(data['Close'])
        data['MACD'] = macd_data['macd_line']
        data['MACD_Signal'] = macd_data['signal_line']
        
        bb_data = calculate_bollinger_bands(data['Close'])
        data['BB_Upper'] = bb_data['upper_band']
        data['BB_Middle'] = bb_data['middle_band']
        data['BB_Lower'] = bb_data['lower_band']
        
        # Get fundamental data
        financials = get_company_financials(ticker)
        
        # Get analyst recommendations
        analyst_data = get_analyst_recommendations(ticker)
        
        # Current price data
        current_price = data['Close'].iloc[-1]
        price_change_1d = ((data['Close'].iloc[-1] - data['Close'].iloc[-2]) / data['Close'].iloc[-2]) * 100 if len(data) > 1 else None
        price_change_period = ((data['Close'].iloc[-1] - data['Close'].iloc[0]) / data['Close'].iloc[0]) * 100
        
        # Technical signals
        ma50_latest = data['MA50'].iloc[-1] if not pd.isna(data['MA50'].iloc[-1]) else None
        ma200_latest = data['MA200'].iloc[-1] if not pd.isna(data['MA200'].iloc[-1]) else None
        
        golden_cross = False
        death_cross = False
        
        if not pd.isna(data['MA50'].iloc[-1]) and not pd.isna(data['MA200'].iloc[-1]) and not pd.isna(data['MA50'].iloc[-2]) and not pd.isna(data['MA200'].iloc[-2]):
            golden_cross = data['MA50'].iloc[-2] <= data['MA200'].iloc[-2] and data['MA50'].iloc[-1] > data['MA200'].iloc[-1]
            death_cross = data['MA50'].iloc[-2] >= data['MA200'].iloc[-2] and data['MA50'].iloc[-1] < data['MA200'].iloc[-1]
        
        rsi_latest = data['RSI'].iloc[-1] if not pd.isna(data['RSI'].iloc[-1]) else None
        rsi_signal = ""
        if rsi_latest is not None:
            if rsi_latest < 30:
                rsi_signal = "Oversold"
            elif rsi_latest > 70:
                rsi_signal = "Overbought"
            else:
                rsi_signal = "Neutral"
        
        # MACD signal
        macd_signal = ""
        if not pd.isna(data['MACD'].iloc[-1]) and not pd.isna(data['MACD_Signal'].iloc[-1]) and not pd.isna(data['MACD'].iloc[-2]) and not pd.isna(data['MACD_Signal'].iloc[-2]):
            if data['MACD'].iloc[-2] <= data['MACD_Signal'].iloc[-2] and data['MACD'].iloc[-1] > data['MACD_Signal'].iloc[-1]:
                macd_signal = "Bullish Crossover"
            elif data['MACD'].iloc[-2] >= data['MACD_Signal'].iloc[-2] and data['MACD'].iloc[-1] < data['MACD_Signal'].iloc[-1]:
                macd_signal = "Bearish Crossover"
            elif data['MACD'].iloc[-1] > data['MACD_Signal'].iloc[-1]:
                macd_signal = "Bullish"
            else:
                macd_signal = "Bearish"
        
        # Bollinger Bands signal
        bb_signal = ""
        if not pd.isna(data['BB_Upper'].iloc[-1]) and not pd.isna(data['BB_Lower'].iloc[-1]):
            if data['Close'].iloc[-1] > data['BB_Upper'].iloc[-1]:
                bb_signal = "Overbought"
            elif data['Close'].iloc[-1] < data['BB_Lower'].iloc[-1]:
                bb_signal = "Oversold"
            else:
                bb_signal = "Within Bands"
        
        # Compile the analysis
        analysis = {
            "ticker": ticker,
            "company_name": company_name,
            "analysis_date": datetime.now().strftime("%Y-%m-%d"),
            "price_data": {
                "current_price": current_price,
                "daily_change_pct": price_change_1d,
                "period_change_pct": price_change_period,
                "period_analyzed": period
            },
            "technical_indicators": {
                "moving_averages": {
                    "ma50": ma50_latest,
                    "ma200": ma200_latest,
                    "golden_cross": golden_cross,
                    "death_cross": death_cross,
                    "price_vs_ma50": "Above" if current_price > ma50_latest else "Below" if ma50_latest is not None else "Unknown",
                    "price_vs_ma200": "Above" if current_price > ma200_latest else "Below" if ma200_latest is not None else "Unknown"
                },
                "rsi": {
                    "current": rsi_latest,
                    "signal": rsi_signal
                },
                "macd": {
                    "current": data['MACD'].iloc[-1] if not pd.isna(data['MACD'].iloc[-1]) else None,
                    "signal": macd_signal
                },
                "bollinger_bands": {
                    "upper": data['BB_Upper'].iloc[-1] if not pd.isna(data['BB_Upper'].iloc[-1]) else None,
                    "middle": data['BB_Middle'].iloc[-1] if not pd.isna(data['BB_Middle'].iloc[-1]) else None,
                    "lower": data['BB_Lower'].iloc[-1] if not pd.isna(data['BB_Lower'].iloc[-1]) else None,
                    "signal": bb_signal
                }
            },
            "fundamentals": financials,
            "analyst_recommendations": analyst_data
        }
        
        return analysis
        
    except Exception as e:
        return f"Error performing comprehensive analysis for {ticker}: {str(e)}"

def generate_investment_advice(ticker, period="6mo", risk_tolerance="moderate"):
    """
    Generate comprehensive investment advice and recommendations based on technical and fundamental analysis.
    
    Parameters:
    - ticker: Stock symbol to analyze
    - period: Time period for analysis (default: 6 months)
    - risk_tolerance: Investor's risk tolerance (low, moderate, high)
    
    Returns:
    - Dictionary containing investment recommendation, reasoning, risk assessment, and supporting data
    """
    try:
        # Get comprehensive analysis
        analysis = extract_financial_insights(ticker, period)
        
        if isinstance(analysis, str) and "Error" in analysis:
            return analysis
        
        # Get market context
        market_indices = {}
        try:
            indices = {
                "S&P 500": "^GSPC",
                "Nasdaq": "^IXIC"
            }
            
            for name, idx_ticker in indices.items():
                idx_data = yf.Ticker(idx_ticker).history(period=period)
                start_price = idx_data['Close'].iloc[0]
                current_price = idx_data['Close'].iloc[-1]
                percent_change = ((current_price - start_price) / start_price) * 100
                market_indices[name] = {
                    "change_pct": percent_change
                }
        except Exception as e:
            market_indices["error"] = str(e)
        
        # Get sector performance for context
        try:
            stock_info = analysis["fundamentals"]
            if isinstance(stock_info, dict) and "sector" in stock_info:
                sector = stock_info["sector"]
                all_sectors = sector_performance()
                if sector in all_sectors:
                    sector_perf = all_sectors[sector]
                else:
                    sector_perf = "Sector performance data unavailable"
            else:
                sector_perf = "Sector information unavailable"
        except Exception as e:
            sector_perf = f"Error retrieving sector data: {str(e)}"
        
        # Extract key metrics for analysis
        tech_signals = []
        fund_signals = []
        
        # Technical Analysis Signals
        try:
            # Moving Averages
            ma_data = analysis["technical_indicators"]["moving_averages"]
            if ma_data["golden_cross"]:
                tech_signals.append({"indicator": "Golden Cross", "signal": "Bullish", "weight": 3})
            if ma_data["death_cross"]:
                tech_signals.append({"indicator": "Death Cross", "signal": "Bearish", "weight": 3})
            
            price_vs_ma50 = ma_data["price_vs_ma50"]
            if price_vs_ma50 == "Above":
                tech_signals.append({"indicator": "Price vs MA50", "signal": "Bullish", "weight": 2})
            elif price_vs_ma50 == "Below":
                tech_signals.append({"indicator": "Price vs MA50", "signal": "Bearish", "weight": 2})
            
            price_vs_ma200 = ma_data["price_vs_ma200"]
            if price_vs_ma200 == "Above":
                tech_signals.append({"indicator": "Price vs MA200", "signal": "Bullish", "weight": 2})
            elif price_vs_ma200 == "Below":
                tech_signals.append({"indicator": "Price vs MA200", "signal": "Bearish", "weight": 2})
            
            # RSI
            rsi_signal = analysis["technical_indicators"]["rsi"]["signal"]
            if rsi_signal == "Oversold":
                tech_signals.append({"indicator": "RSI", "signal": "Bullish", "weight": 2})
            elif rsi_signal == "Overbought":
                tech_signals.append({"indicator": "RSI", "signal": "Bearish", "weight": 2})
            
            # MACD
            macd_signal = analysis["technical_indicators"]["macd"]["signal"]
            if "Bullish" in macd_signal:
                signal_weight = 3 if "Crossover" in macd_signal else 2
                tech_signals.append({"indicator": "MACD", "signal": "Bullish", "weight": signal_weight})
            elif "Bearish" in macd_signal:
                signal_weight = 3 if "Crossover" in macd_signal else 2
                tech_signals.append({"indicator": "MACD", "signal": "Bearish", "weight": signal_weight})
            
            # Bollinger Bands
            bb_signal = analysis["technical_indicators"]["bollinger_bands"]["signal"]
            if bb_signal == "Oversold":
                tech_signals.append({"indicator": "Bollinger Bands", "signal": "Bullish", "weight": 2})
            elif bb_signal == "Overbought":
                tech_signals.append({"indicator": "Bollinger Bands", "signal": "Bearish", "weight": 2})
        except Exception as e:
            tech_signals.append({"indicator": "Error", "signal": f"Error processing technical signals: {str(e)}", "weight": 0})
        
        # Fundamental Analysis Signals
        try:
            fundamentals = analysis["fundamentals"]
            if not isinstance(fundamentals, dict):
                fund_signals.append({"indicator": "Error", "signal": "Fundamental data unavailable", "weight": 0})
            else:
                # P/E Ratio analysis
                pe_ratio = fundamentals.get("pe_ratio")
                if pe_ratio is not None:
                    if pe_ratio < 15:
                        fund_signals.append({"indicator": "P/E Ratio", "signal": "Bullish", "weight": 2, "value": pe_ratio})
                    elif pe_ratio > 30:
                        fund_signals.append({"indicator": "P/E Ratio", "signal": "Bearish", "weight": 2, "value": pe_ratio})
                    else:
                        fund_signals.append({"indicator": "P/E Ratio", "signal": "Neutral", "weight": 1, "value": pe_ratio})
                
                # Revenue Growth
                revenue_growth = fundamentals.get("revenue_growth_pct")
                if revenue_growth is not None:
                    if revenue_growth > 20:
                        fund_signals.append({"indicator": "Revenue Growth", "signal": "Bullish", "weight": 3, "value": f"{revenue_growth:.2f}%"})
                    elif revenue_growth > 10:
                        fund_signals.append({"indicator": "Revenue Growth", "signal": "Bullish", "weight": 2, "value": f"{revenue_growth:.2f}%"})
                    elif revenue_growth < 0:
                        fund_signals.append({"indicator": "Revenue Growth", "signal": "Bearish", "weight": 2, "value": f"{revenue_growth:.2f}%"})
                    else:
                        fund_signals.append({"indicator": "Revenue Growth", "signal": "Neutral", "weight": 1, "value": f"{revenue_growth:.2f}%"})
                
                # Profit Margins
                margins = fundamentals.get("profit_margins")
                if margins is not None:
                    margins_pct = margins * 100 if margins < 1 else margins  # Convert to percentage if needed
                    if margins_pct > 20:
                        fund_signals.append({"indicator": "Profit Margins", "signal": "Bullish", "weight": 2, "value": f"{margins_pct:.2f}%"})
                    elif margins_pct < 5:
                        fund_signals.append({"indicator": "Profit Margins", "signal": "Bearish", "weight": 2, "value": f"{margins_pct:.2f}%"})
                    else:
                        fund_signals.append({"indicator": "Profit Margins", "signal": "Neutral", "weight": 1, "value": f"{margins_pct:.2f}%"})
                
                # Return on Equity
                roe = fundamentals.get("return_on_equity")
                if roe is not None:
                    roe_pct = roe * 100 if roe < 1 else roe  # Convert to percentage if needed
                    if roe_pct > 20:
                        fund_signals.append({"indicator": "Return on Equity", "signal": "Bullish", "weight": 2, "value": f"{roe_pct:.2f}%"})
                    elif roe_pct < 10:
                        fund_signals.append({"indicator": "Return on Equity", "signal": "Bearish", "weight": 1, "value": f"{roe_pct:.2f}%"})
                    else:
                        fund_signals.append({"indicator": "Return on Equity", "signal": "Neutral", "weight": 1, "value": f"{roe_pct:.2f}%"})
                
                # Debt to Equity
                debt_to_equity = fundamentals.get("debt_to_equity")
                if debt_to_equity is not None:
                    if debt_to_equity > 2:
                        fund_signals.append({"indicator": "Debt to Equity", "signal": "Bearish", "weight": 2, "value": debt_to_equity})
                    elif debt_to_equity < 0.5:
                        fund_signals.append({"indicator": "Debt to Equity", "signal": "Bullish", "weight": 1, "value": debt_to_equity})
                    else:
                        fund_signals.append({"indicator": "Debt to Equity", "signal": "Neutral", "weight": 1, "value": debt_to_equity})
        except Exception as e:
            fund_signals.append({"indicator": "Error", "signal": f"Error processing fundamental signals: {str(e)}", "weight": 0})
        
        # Analyst Recommendations
        analyst_signal = {"indicator": "Analyst Consensus", "signal": "Neutral", "weight": 2, "value": "N/A"}
        try:
            analyst_recs = analysis["analyst_recommendations"]
            if isinstance(analyst_recs, dict) and "recommendation_counts" in analyst_recs:
                # Create a weighted score based on analyst recommendations
                rec_counts = analyst_recs["recommendation_counts"]
                
                # Define weights for different recommendation types
                rec_weights = {
                    'Strong Buy': 2,
                    'Buy': 1,
                    'Outperform': 1,
                    'Overweight': 1,
                    'Hold': 0,
                    'Neutral': 0,
                    'Perform': 0,
                    'Market Perform': 0,
                    'Equal-Weight': 0,
                    'Underperform': -1,
                    'Underweight': -1,
                    'Sell': -1,
                    'Strong Sell': -2
                }
                
                # Calculate weighted score
                total_weights = 0
                total_recs = 0
                
                for rec, count in rec_counts.items():
                    if rec in rec_weights:
                        total_weights += rec_weights[rec] * count
                        total_recs += count
                
                if total_recs > 0:
                    score = total_weights / total_recs
                    if score > 0.5:
                        analyst_signal = {"indicator": "Analyst Consensus", "signal": "Bullish", "weight": 3, "value": f"Score: {score:.2f}"}
                    elif score < -0.5:
                        analyst_signal = {"indicator": "Analyst Consensus", "signal": "Bearish", "weight": 3, "value": f"Score: {score:.2f}"}
                    else:
                        analyst_signal = {"indicator": "Analyst Consensus", "signal": "Neutral", "weight": 2, "value": f"Score: {score:.2f}"}
        except Exception as e:
            analyst_signal = {"indicator": "Analyst Consensus", "signal": f"Error: {str(e)}", "weight": 0, "value": "Error"}
        
        # Add analyst consensus to signals
        fund_signals.append(analyst_signal)
        
        # Calculate overall technical and fundamental scores
        tech_score = 0
        tech_weight_sum = 0
        for signal in tech_signals:
            if signal["signal"] == "Bullish":
                tech_score += signal["weight"]
            elif signal["signal"] == "Bearish":
                tech_score -= signal["weight"]
            tech_weight_sum += signal["weight"]
        
        fund_score = 0
        fund_weight_sum = 0
        for signal in fund_signals:
            if signal["signal"] == "Bullish":
                fund_score += signal["weight"]
            elif signal["signal"] == "Bearish":
                fund_score -= signal["weight"]
            fund_weight_sum += signal["weight"]
        
        # Normalize scores to range from -10 to 10
        tech_normalized = 0 if tech_weight_sum == 0 else (tech_score / tech_weight_sum) * 10
        fund_normalized = 0 if fund_weight_sum == 0 else (fund_score / fund_weight_sum) * 10
        
        # Combine scores with appropriate weights based on risk tolerance
        if risk_tolerance.lower() == "low":
            tech_weight = 0.3
            fund_weight = 0.7
        elif risk_tolerance.lower() == "high":
            tech_weight = 0.7
            fund_weight = 0.3
        else:  # moderate
            tech_weight = 0.5
            fund_weight = 0.5
        
        combined_score = (tech_normalized * tech_weight) + (fund_normalized * fund_weight)
        
        # Determine recommendation
        recommendation = ""
        confidence = abs(combined_score) / 10  # 0 to 1 scale
        
        if combined_score > 6:
            recommendation = "Strong Buy"
        elif combined_score > 3:
            recommendation = "Buy"
        elif combined_score > 0:
            recommendation = "Mild Buy"
        elif combined_score > -3:
            recommendation = "Hold"
        elif combined_score > -6:
            recommendation = "Sell"
        else:
            recommendation = "Strong Sell"
        
        # Calculate potential return and risk
        price_data = analysis["price_data"]
        current_price = price_data["current_price"]
        
        # Estimate potential upside/downside based on signals and historical volatility
        potential_upside = 0
        potential_downside = 0
        
        try:
            # Use historical data to calculate volatility
            stock_data = yf.Ticker(ticker).history(period="1y")
            daily_returns = stock_data['Close'].pct_change().dropna()
            volatility = daily_returns.std() * np.sqrt(252)  # Annualize volatility
            
            # Base case scenario (assuming average market return)
            base_return = 0.10  # 10% annual return
            
            # Adjust based on combined score
            score_adjustment = combined_score / 10  # -1 to 1
            
            # Higher volatility means more extreme potential outcomes
            volatility_factor = min(max(volatility, 0.15), 0.50)  # Limit volatility impact
            
            # Calculate potential returns
            potential_upside = base_return + (score_adjustment * volatility_factor * 2)
            potential_downside = -(base_return - (score_adjustment * volatility_factor * 2))
            
            # Convert to percentages and ensure logical outcomes
            potential_upside = max(potential_upside * 100, 2)  # Minimum 2% upside
            potential_downside = min(max(potential_downside * 100, 2), 50)  # Between 2% and 50% downside
            
            # Adjust based on risk tolerance
            if risk_tolerance.lower() == "low":
                potential_upside *= 0.8
                potential_downside *= 1.2
            elif risk_tolerance.lower() == "high":
                potential_upside *= 1.2
                potential_downside *= 0.8
                
        except Exception as e:
            potential_upside = 10  # Default to 10% upside
            potential_downside = 10  # Default to 10% downside
        
        # Compile investment thesis and risks
        investment_thesis = []
        risks = []
        
        # Significant technical signals
        for signal in tech_signals:
            if signal["weight"] >= 2 and signal["signal"] == "Bullish":
                investment_thesis.append(f"{signal['indicator']} indicates bullish momentum")
            elif signal["weight"] >= 2 and signal["signal"] == "Bearish":
                risks.append(f"{signal['indicator']} shows bearish signals")
        
        # Significant fundamental factors
        for signal in fund_signals:
            if "value" in signal:
                value_str = f" ({signal['value']})"
            else:
                value_str = ""
                
            if signal["weight"] >= 2 and signal["signal"] == "Bullish":
                investment_thesis.append(f"Strong {signal['indicator']}{value_str}")
            elif signal["weight"] >= 2 and signal["signal"] == "Bearish":
                risks.append(f"Concerning {signal['indicator']}{value_str}")
        
        # Add market context
        if isinstance(market_indices, dict) and "S&P 500" in market_indices:
            sp500_change = market_indices["S&P 500"]["change_pct"]
            stock_change = price_data["period_change_pct"]
            
            if stock_change > sp500_change + 10:
                investment_thesis.append(f"Outperforming S&P 500 by {(stock_change - sp500_change):.2f}% over {period}")
            elif stock_change < sp500_change - 10:
                risks.append(f"Underperforming S&P 500 by {(sp500_change - stock_change):.2f}% over {period}")
        
        # Add sector context
        if isinstance(sector_perf, dict) and "ytd_change_pct" in sector_perf:
            sector_ytd = sector_perf["ytd_change_pct"]
            stock_change = price_data["period_change_pct"]
            
            if period == "ytd" and stock_change > sector_ytd + 10:
                investment_thesis.append(f"Outperforming sector average by {(stock_change - sector_ytd):.2f}% YTD")
            elif period == "ytd" and stock_change < sector_ytd - 10:
                risks.append(f"Underperforming sector average by {(sector_ytd - stock_change):.2f}% YTD")
        
        # Ensure we have at least some thesis and risks
        if not investment_thesis:
            if combined_score > 0:
                investment_thesis.append("Overall technical and fundamental indicators are positive")
            else:
                investment_thesis.append("Limited positive indicators found")
                
        if not risks:
            if combined_score < 0:
                risks.append("Overall technical and fundamental indicators are negative")
            else:
                risks.append("Market volatility and economic uncertainty")
                
        # Format advice        
        advice = {
            "ticker": ticker,
            "company_name": analysis["company_name"],
            "recommendation": recommendation,
            "confidence_score": round(confidence * 100),  # 0-100% confidence
            "potential_upside": round(potential_upside, 1),
            "potential_downside": round(potential_downside, 1),
            "risk_reward_ratio": round(potential_upside / potential_downside, 2) if potential_downside > 0 else "N/A",
            "investment_thesis": investment_thesis,
            "risks": risks,
            "technical_signals": tech_signals,
            "fundamental_signals": fund_signals,
            "technical_score": round(tech_normalized, 2),
            "fundamental_score": round(fund_normalized, 2),
            "combined_score": round(combined_score, 2),
            "current_price": current_price,
            "price_change": f"{price_data['period_change_pct']:.2f}% over {period}",
            "analysis_date": datetime.now().strftime("%Y-%m-%d"),
            "risk_tolerance": risk_tolerance.capitalize()
        }
        
        return advice
        
    except Exception as e:
        return f"Error generating investment advice for {ticker}: {str(e)}"

# Cryptocurrency analysis functions

def get_crypto_data(symbol, period="1y", interval="1d"):
    """
    Get historical cryptocurrency data
    
    Parameters:
    - symbol: Cryptocurrency symbol (e.g., BTC-USD, ETH-USD)
    - period: Time period for analysis
    - interval: Data interval
    
    Returns:
    - Historical price and volume data for the cryptocurrency
    """
    try:
        # Ensure proper suffix for crypto symbols
        if not '-' in symbol:
            symbol = f"{symbol}-USD"
        
        data = yf.Ticker(symbol).history(period=period, interval=interval)
        if data.empty:
            return f"No data found for {symbol}"
        
        return data
    except Exception as e:
        return f"Error retrieving data for {symbol}: {str(e)}"

def get_crypto_market_data():
    """
    Get data for major cryptocurrencies
    
    Returns:
    - Dictionary with data for major cryptocurrencies
    """
    crypto_symbols = {
        "Bitcoin": "BTC-USD",
        "Ethereum": "ETH-USD",
        "Binance Coin": "BNB-USD",
        "Cardano": "ADA-USD",
        "Solana": "SOL-USD",
        "XRP": "XRP-USD",
        "Dogecoin": "DOGE-USD",
        "Polkadot": "DOT-USD",
        "Polygon": "MATIC-USD",
        "Chainlink": "LINK-USD"
    }
    
    results = {}
    time_periods = {
        "1_day": "1d",
        "1_week": "1wk",
        "1_month": "1mo",
        "ytd": "ytd",
        "1_year": "1y"
    }
    
    for name, symbol in crypto_symbols.items():
        try:
            data = yf.Ticker(symbol).history(period="5d")
            
            if data.empty:
                results[name] = "No data available"
                continue
                
            current_price = data['Close'].iloc[-1]
            previous_price = data['Close'].iloc[-2]
            daily_change = ((current_price - previous_price) / previous_price) * 100
            
            crypto_result = {
                "current_price": current_price,
                "daily_change_pct": daily_change,
                "period_changes": {}
            }
            
            # Get performance over different time periods
            for period_name, period_code in time_periods.items():
                try:
                    period_data = yf.Ticker(symbol).history(period=period_code)
                    if not period_data.empty and len(period_data) > 1:
                        start_price = period_data['Close'].iloc[0]
                        period_change = ((current_price - start_price) / start_price) * 100
                        crypto_result["period_changes"][period_name] = period_change
                except Exception:
                    pass
            
            results[name] = crypto_result
            
        except Exception as e:
            results[name] = f"Error: {str(e)}"
    
    return results

def get_crypto_dominance():
    """
    Get Bitcoin dominance and market share of top cryptocurrencies
    
    Returns:
    - Dictionary with BTC dominance and top crypto market shares
    """
    try:
        # Get data for top cryptocurrencies to calculate market share
        top_cryptos = {
            "Bitcoin": "BTC-USD",
            "Ethereum": "ETH-USD",
            "Binance Coin": "BNB-USD",
            "XRP": "XRP-USD",
            "Cardano": "ADA-USD",
            "Solana": "SOL-USD",
            "Dogecoin": "DOGE-USD",
            "Polkadot": "DOT-USD",
            "Polygon": "MATIC-USD",
            "Chainlink": "LINK-USD"
        }
        
        market_caps = {}
        total_market_cap = 0
        
        for name, symbol in top_cryptos.items():
            try:
                data = yf.Ticker(symbol).info
                if 'marketCap' in data and data['marketCap'] is not None:
                    market_cap = data['marketCap']
                    market_caps[name] = market_cap
                    total_market_cap += market_cap
            except Exception:
                pass
        
        # Calculate dominance percentages
        dominance = {}
        if total_market_cap > 0:
            for name, market_cap in market_caps.items():
                dominance[name] = (market_cap / total_market_cap) * 100
        
        return {
            "market_caps": market_caps,
            "dominance_percentages": dominance,
            "total_analyzed_market_cap": total_market_cap
        }
        
    except Exception as e:
        return f"Error calculating crypto dominance: {str(e)}"

def analyze_crypto(symbol, period="1y"):
    """
    Comprehensive cryptocurrency analysis
    
    Parameters:
    - symbol: Cryptocurrency symbol (e.g., BTC-USD, ETH-USD)
    - period: Time period for analysis
    
    Returns:
    - Dictionary with comprehensive analysis
    """
    try:
        # Ensure proper suffix for crypto symbols
        if not '-' in symbol:
            symbol = f"{symbol}-USD"
        
        # Get historical data
        data = get_crypto_data(symbol, period)
        
        if isinstance(data, str):
            return f"Error: {data}"
        
        if data.empty:
            return f"No price data available for {symbol}"
        
        # Get basic info
        ticker_info = yf.Ticker(symbol).info
        name = ticker_info.get('name', symbol.split('-')[0])
        
        # Calculate technical indicators
        data['MA50'] = calculate_moving_average(data['Close'], 50)
        data['MA200'] = calculate_moving_average(data['Close'], 200)
        data['RSI'] = calculate_rsi(data['Close'])
        
        macd_data = calculate_macd(data['Close'])
        data['MACD'] = macd_data['macd_line']
        data['MACD_Signal'] = macd_data['signal_line']
        
        bb_data = calculate_bollinger_bands(data['Close'])
        data['BB_Upper'] = bb_data['upper_band']
        data['BB_Middle'] = bb_data['middle_band']
        data['BB_Lower'] = bb_data['lower_band']
        
        # Current price data
        current_price = data['Close'].iloc[-1]
        price_change_1d = ((data['Close'].iloc[-1] - data['Close'].iloc[-2]) / data['Close'].iloc[-2]) * 100 if len(data) > 1 else None
        price_change_period = ((data['Close'].iloc[-1] - data['Close'].iloc[0]) / data['Close'].iloc[0]) * 100
        
        # Technical signals
        ma50_latest = data['MA50'].iloc[-1] if not pd.isna(data['MA50'].iloc[-1]) else None
        ma200_latest = data['MA200'].iloc[-1] if not pd.isna(data['MA200'].iloc[-1]) else None
        
        golden_cross = False
        death_cross = False
        
        if not pd.isna(data['MA50'].iloc[-1]) and not pd.isna(data['MA200'].iloc[-1]) and not pd.isna(data['MA50'].iloc[-2]) and not pd.isna(data['MA200'].iloc[-2]):
            golden_cross = data['MA50'].iloc[-2] <= data['MA200'].iloc[-2] and data['MA50'].iloc[-1] > data['MA200'].iloc[-1]
            death_cross = data['MA50'].iloc[-2] >= data['MA200'].iloc[-2] and data['MA50'].iloc[-1] < data['MA200'].iloc[-1]
        
        rsi_latest = data['RSI'].iloc[-1] if not pd.isna(data['RSI'].iloc[-1]) else None
        rsi_signal = ""
        if rsi_latest is not None:
            if rsi_latest < 30:
                rsi_signal = "Oversold"
            elif rsi_latest > 70:
                rsi_signal = "Overbought"
            else:
                rsi_signal = "Neutral"
        
        # MACD signal
        macd_signal = ""
        if not pd.isna(data['MACD'].iloc[-1]) and not pd.isna(data['MACD_Signal'].iloc[-1]) and not pd.isna(data['MACD'].iloc[-2]) and not pd.isna(data['MACD_Signal'].iloc[-2]):
            if data['MACD'].iloc[-2] <= data['MACD_Signal'].iloc[-2] and data['MACD'].iloc[-1] > data['MACD_Signal'].iloc[-1]:
                macd_signal = "Bullish Crossover"
            elif data['MACD'].iloc[-2] >= data['MACD_Signal'].iloc[-2] and data['MACD'].iloc[-1] < data['MACD_Signal'].iloc[-1]:
                macd_signal = "Bearish Crossover"
            elif data['MACD'].iloc[-1] > data['MACD_Signal'].iloc[-1]:
                macd_signal = "Bullish"
            else:
                macd_signal = "Bearish"
        
        # Bollinger Bands signal
        bb_signal = ""
        if not pd.isna(data['BB_Upper'].iloc[-1]) and not pd.isna(data['BB_Lower'].iloc[-1]):
            if data['Close'].iloc[-1] > data['BB_Upper'].iloc[-1]:
                bb_signal = "Overbought"
            elif data['Close'].iloc[-1] < data['BB_Lower'].iloc[-1]:
                bb_signal = "Oversold"
            else:
                bb_signal = "Within Bands"
        
        # Volume analysis
        avg_volume = data['Volume'].mean()
        recent_volume = data['Volume'].iloc[-5:].mean()
        volume_change = ((recent_volume - avg_volume) / avg_volume) * 100 if avg_volume > 0 else 0
        
        # Get market cap if available
        market_cap = ticker_info.get('marketCap', None)
        
        # Volatility calculation
        daily_returns = data['Close'].pct_change().dropna()
        volatility = daily_returns.std() * np.sqrt(252)  # Annualized volatility
        
        # Compile the analysis
        analysis = {
            "symbol": symbol,
            "name": name,
            "analysis_date": datetime.now().strftime("%Y-%m-%d"),
            "price_data": {
                "current_price": current_price,
                "daily_change_pct": price_change_1d,
                "period_change_pct": price_change_period,
                "period_analyzed": period,
                "volatility_annual": volatility * 100  # Convert to percentage
            },
            "market_data": {
                "market_cap": market_cap,
                "avg_volume": avg_volume,
                "recent_volume": recent_volume,
                "volume_change_pct": volume_change
            },
            "technical_indicators": {
                "moving_averages": {
                    "ma50": ma50_latest,
                    "ma200": ma200_latest,
                    "golden_cross": golden_cross,
                    "death_cross": death_cross,
                    "price_vs_ma50": "Above" if current_price > ma50_latest else "Below" if ma50_latest is not None else "Unknown",
                    "price_vs_ma200": "Above" if current_price > ma200_latest else "Below" if ma200_latest is not None else "Unknown"
                },
                "rsi": {
                    "current": rsi_latest,
                    "signal": rsi_signal
                },
                "macd": {
                    "current": data['MACD'].iloc[-1] if not pd.isna(data['MACD'].iloc[-1]) else None,
                    "signal": macd_signal
                },
                "bollinger_bands": {
                    "upper": data['BB_Upper'].iloc[-1] if not pd.isna(data['BB_Upper'].iloc[-1]) else None,
                    "middle": data['BB_Middle'].iloc[-1] if not pd.isna(data['BB_Middle'].iloc[-1]) else None,
                    "lower": data['BB_Lower'].iloc[-1] if not pd.isna(data['BB_Lower'].iloc[-1]) else None,
                    "signal": bb_signal
                }
            }
        }
        
        # Try to get additional crypto-specific metrics
        try:
            # Compare to Bitcoin for non-BTC assets
            if not symbol.startswith('BTC'):
                btc_data = yf.Ticker('BTC-USD').history(period=period)
                btc_change = ((btc_data['Close'].iloc[-1] - btc_data['Close'].iloc[0]) / btc_data['Close'].iloc[0]) * 100
                analysis["btc_comparison"] = {
                    "btc_period_change_pct": btc_change,
                    "outperforming_btc": price_change_period > btc_change,
                    "performance_vs_btc": price_change_period - btc_change
                }
            
            # Get Bitcoin dominance for context
            dominance_data = get_crypto_dominance()
            if isinstance(dominance_data, dict) and "dominance_percentages" in dominance_data:
                crypto_name = name.split('-')[0]
                for key in dominance_data["dominance_percentages"]:
                    if crypto_name in key:
                        analysis["market_data"]["dominance_pct"] = dominance_data["dominance_percentages"].get(key, None)
                        break
            
        except Exception:
            pass
            
        return analysis
        
    except Exception as e:
        return f"Error performing comprehensive analysis for {symbol}: {str(e)}"

def generate_crypto_investment_advice(symbol, period="6mo", risk_tolerance="moderate"):
    """
    Generate investment advice for cryptocurrency
    
    Parameters:
    - symbol: Cryptocurrency symbol
    - period: Analysis time period
    - risk_tolerance: Investor's risk tolerance (low, moderate, high)
    
    Returns:
    - Investment advice for the cryptocurrency
    """
    try:
        # Ensure proper suffix for crypto symbols
        if not '-' in symbol:
            symbol = f"{symbol}-USD"
            
        # Get comprehensive analysis
        analysis = analyze_crypto(symbol, period)
        
        if isinstance(analysis, str) and "Error" in analysis:
            return analysis
        
        # Extract key metrics for analysis
        tech_signals = []
        
        # Technical Analysis Signals
        try:
            # Moving Averages
            ma_data = analysis["technical_indicators"]["moving_averages"]
            if ma_data["golden_cross"]:
                tech_signals.append({"indicator": "Golden Cross", "signal": "Bullish", "weight": 3})
            if ma_data["death_cross"]:
                tech_signals.append({"indicator": "Death Cross", "signal": "Bearish", "weight": 3})
            
            price_vs_ma50 = ma_data["price_vs_ma50"]
            if price_vs_ma50 == "Above":
                tech_signals.append({"indicator": "Price vs MA50", "signal": "Bullish", "weight": 2})
            elif price_vs_ma50 == "Below":
                tech_signals.append({"indicator": "Price vs MA50", "signal": "Bearish", "weight": 2})
            
            price_vs_ma200 = ma_data["price_vs_ma200"]
            if price_vs_ma200 == "Above":
                tech_signals.append({"indicator": "Price vs MA200", "signal": "Bullish", "weight": 2})
            elif price_vs_ma200 == "Below":
                tech_signals.append({"indicator": "Price vs MA200", "signal": "Bearish", "weight": 2})
            
            # RSI
            rsi_signal = analysis["technical_indicators"]["rsi"]["signal"]
            if rsi_signal == "Oversold":
                tech_signals.append({"indicator": "RSI", "signal": "Bullish", "weight": 2})
            elif rsi_signal == "Overbought":
                tech_signals.append({"indicator": "RSI", "signal": "Bearish", "weight": 2})
            
            # MACD
            macd_signal = analysis["technical_indicators"]["macd"]["signal"]
            if "Bullish" in macd_signal:
                signal_weight = 3 if "Crossover" in macd_signal else 2
                tech_signals.append({"indicator": "MACD", "signal": "Bullish", "weight": signal_weight})
            elif "Bearish" in macd_signal:
                signal_weight = 3 if "Crossover" in macd_signal else 2
                tech_signals.append({"indicator": "MACD", "signal": "Bearish", "weight": signal_weight})
            
            # Bollinger Bands
            bb_signal = analysis["technical_indicators"]["bollinger_bands"]["signal"]
            if bb_signal == "Oversold":
                tech_signals.append({"indicator": "Bollinger Bands", "signal": "Bullish", "weight": 2})
            elif bb_signal == "Overbought":
                tech_signals.append({"indicator": "Bollinger Bands", "signal": "Bearish", "weight": 2})
                
            # Volume analysis
            volume_change = analysis["market_data"]["volume_change_pct"]
            if volume_change > 30:
                tech_signals.append({"indicator": "Volume", "signal": "Bullish" if price_vs_ma50 == "Above" else "Bearish", "weight": 2})
                
        except Exception as e:
            tech_signals.append({"indicator": "Error", "signal": f"Error processing technical signals: {str(e)}", "weight": 0})
        
        # Calculate overall technical score
        tech_score = 0
        tech_weight_sum = 0
        for signal in tech_signals:
            if signal["signal"] == "Bullish":
                tech_score += signal["weight"]
            elif signal["signal"] == "Bearish":
                tech_score -= signal["weight"]
            tech_weight_sum += signal["weight"]
        
        # Normalize score to range from -10 to 10
        tech_normalized = 0 if tech_weight_sum == 0 else (tech_score / tech_weight_sum) * 10
        
        # For cryptocurrencies, we adjust the weight of technical analysis based on risk tolerance
        if risk_tolerance.lower() == "low":
            tech_weight = 0.4
        elif risk_tolerance.lower() == "high":
            tech_weight = 1.0  # Full weight for high risk tolerance
        else:  # moderate
            tech_weight = 0.7
        
        combined_score = tech_normalized * tech_weight
        
        # Market trend adjustment
        try:
            crypto_market = get_crypto_market_data()
            btc_trend = crypto_market.get("Bitcoin", {}).get("daily_change_pct", 0)
            market_adj = 0
            
            # If Bitcoin is strongly trending up or down, adjust the score
            if btc_trend > 5:  # Strong BTC uptrend
                market_adj = 2
            elif btc_trend > 2:  # Moderate BTC uptrend
                market_adj = 1
            elif btc_trend < -5:  # Strong BTC downtrend
                market_adj = -2
            elif btc_trend < -2:  # Moderate BTC downtrend
                market_adj = -1
                
            combined_score += market_adj
            
            # Add Bitcoin correlation/comparison data if available
            if "btc_comparison" in analysis:
                if analysis["btc_comparison"]["outperforming_btc"]:
                    tech_signals.append({"indicator": "BTC Comparison", "signal": "Bullish", "weight": 2})
                    combined_score += 1
                else:
                    tech_signals.append({"indicator": "BTC Comparison", "signal": "Bearish", "weight": 1})
                    combined_score -= 0.5
        except Exception:
            pass
        
        # Volatility adjustment
        try:
            volatility = analysis["price_data"]["volatility_annual"]
            
            # Higher volatility increases risk
            volatility_risk = "Very High" if volatility > 100 else "High" if volatility > 70 else "Moderate" if volatility > 40 else "Low"
            
            # For low risk tolerance, penalize high volatility
            if risk_tolerance.lower() == "low" and volatility > 70:
                combined_score -= 2
            # For high risk tolerance, slightly reward high volatility (potential opportunity)
            elif risk_tolerance.lower() == "high" and volatility > 70:
                combined_score += 1
                
            tech_signals.append({"indicator": "Volatility", "signal": "Neutral", "weight": 2, "value": f"{volatility:.2f}% ({volatility_risk})"})
        except Exception:
            pass
        
        # Determine recommendation
        recommendation = ""
        confidence = abs(combined_score) / 10  # 0 to 1 scale
        
        if combined_score > 6:
            recommendation = "Strong Buy"
        elif combined_score > 3:
            recommendation = "Buy"
        elif combined_score > 0:
            recommendation = "Mild Buy"
        elif combined_score > -3:
            recommendation = "Hold"
        elif combined_score > -6:
            recommendation = "Sell"
        else:
            recommendation = "Strong Sell"
        
        # Calculate potential return and risk
        price_data = analysis["price_data"]
        current_price = price_data["current_price"]
        
        # Estimate potential upside/downside based on signals and historical volatility
        potential_upside = 0
        potential_downside = 0
        
        try:
            # Use historical volatility to estimate potential returns
            volatility = price_data["volatility_annual"] / 100  # Convert from percentage
            
            # Cryptocurrencies can have higher potential returns/losses than stocks
            base_return = 0.15  # Higher base return for crypto
            
            # Adjust based on combined score
            score_adjustment = combined_score / 10  # -1 to 1
            
            # Higher volatility means more extreme potential outcomes
            volatility_factor = min(max(volatility, 0.3), 1.0)  # Limit volatility impact, but higher than stocks
            
            # Calculate potential returns - crypto has higher upside/downside
            potential_upside = base_return + (score_adjustment * volatility_factor * 3)
            potential_downside = -(base_return - (score_adjustment * volatility_factor * 3))
            
            # Convert to percentages and ensure logical outcomes - higher ranges for crypto
            potential_upside = max(potential_upside * 100, 5)  # Minimum 5% upside for crypto
            potential_downside = min(max(potential_downside * 100, 5), 90)  # Between 5% and 90% downside for crypto
            
            # Adjust based on risk tolerance
            if risk_tolerance.lower() == "low":
                potential_upside *= 0.7
                potential_downside *= 1.3
            elif risk_tolerance.lower() == "high":
                potential_upside *= 1.3
                potential_downside *= 0.7
                
        except Exception as e:
            potential_upside = 20  # Default to 20% upside for crypto
            potential_downside = 20  # Default to 20% downside for crypto
        
        # Compile investment thesis and risks
        investment_thesis = []
        risks = []
        
        # Significant technical signals
        for signal in tech_signals:
            if signal["weight"] >= 2 and signal["signal"] == "Bullish":
                investment_thesis.append(f"{signal['indicator']} indicates bullish momentum")
            elif signal["weight"] >= 2 and signal["signal"] == "Bearish":
                risks.append(f"{signal['indicator']} shows bearish signals")
        
        # Additional crypto-specific considerations
        investment_thesis.append(f"Historical volatility of {volatility:.2f}% suggests potential for higher returns")
        
        # Add bitcoin trend relationship if available
        try:
            if "btc_comparison" in analysis:
                performance_vs_btc = analysis["btc_comparison"]["performance_vs_btc"]
                if performance_vs_btc > 10:
                    investment_thesis.append(f"Outperforming Bitcoin by {performance_vs_btc:.2f}% over the analyzed period")
                elif performance_vs_btc < -10:
                    risks.append(f"Underperforming Bitcoin by {abs(performance_vs_btc):.2f}% over the analyzed period")
        except Exception:
            pass
        
        # Add market dominance context if available
        try:
            if "dominance_pct" in analysis["market_data"]:
                dominance = analysis["market_data"]["dominance_pct"]
                if dominance > 50:
                    investment_thesis.append(f"Market dominance of {dominance:.2f}% indicates strong market position")
                elif dominance > 10:
                    investment_thesis.append(f"Significant market share of {dominance:.2f}%")
        except Exception:
            pass
            
        # Volume analysis
        try:
            volume_change = analysis["market_data"]["volume_change_pct"]
            if volume_change > 50:
                investment_thesis.append(f"Notable volume increase of {volume_change:.2f}% indicates growing interest")
            elif volume_change < -30:
                risks.append(f"Decreasing volume of {abs(volume_change):.2f}% suggests declining interest")
        except Exception:
            pass
        
        # Ensure we have at least some thesis and risks
        if not investment_thesis:
            if combined_score > 0:
                investment_thesis.append("Overall technical indicators are positive")
            else:
                investment_thesis.append("Limited positive indicators found")
                
        if not risks:
            if combined_score < 0:
                risks.append("Overall technical indicators are negative")
            else:
                # Always include standard crypto risks
                risks.append("High market volatility and regulatory uncertainty")
                risks.append("Cryptocurrency markets are highly speculative and can experience extreme price swings")
                
        # Add standard crypto disclaimer based on risk tolerance
        if risk_tolerance.lower() == "low":
            risks.append("Cryptocurrencies are generally not suitable for low risk tolerance investors")
        
        # Format advice
        advice = {
            "symbol": symbol,
            "name": analysis["name"],
            "recommendation": recommendation,
            "confidence_score": round(confidence * 100),  # 0-100% confidence
            "potential_upside": round(potential_upside, 1),
            "potential_downside": round(potential_downside, 1),
            "risk_reward_ratio": round(potential_upside / potential_downside, 2) if potential_downside > 0 else "N/A",
            "investment_thesis": investment_thesis,
            "risks": risks,
            "technical_signals": tech_signals,
            "technical_score": round(tech_normalized, 2),
            "combined_score": round(combined_score, 2),
            "current_price": current_price,
            "price_change": f"{price_data['period_change_pct']:.2f}% over {period}",
            "volatility": f"{price_data['volatility_annual']:.2f}%",
            "analysis_date": datetime.now().strftime("%Y-%m-%d"),
            "risk_tolerance": risk_tolerance.capitalize()
        }
        
        return advice
        
    except Exception as e:
        return f"Error generating investment advice for {symbol}: {str(e)}"

def compare_cryptos(symbols, period="1y"):
    """
    Compare multiple cryptocurrencies
    
    Parameters:
    - symbols: List of cryptocurrency symbols or comma-separated string
    - period: Analysis time period
    
    Returns:
    - Comparative analysis of the cryptocurrencies
    """
    try:
        # Process input symbols
        if not isinstance(symbols, list):
            symbols = symbols.split(',')
        
        symbols = [s.strip() for s in symbols]
        
        # Ensure proper suffix for crypto symbols
        formatted_symbols = []
        for symbol in symbols:
            if not '-' in symbol:
                formatted_symbols.append(f"{symbol}-USD")
            else:
                formatted_symbols.append(symbol)
        
        results = {}
        performance_data = {}
        volatility_data = {}
        indicator_data = {}
        
        # Get Bitcoin data for reference
        btc_data = get_crypto_data("BTC-USD", period)
        if isinstance(btc_data, pd.DataFrame) and not btc_data.empty:
            btc_start_price = btc_data['Close'].iloc[0]
            btc_end_price = btc_data['Close'].iloc[-1]
            btc_change = ((btc_end_price - btc_start_price) / btc_start_price) * 100
        else:
            btc_change = 0
            
        # Analyze each cryptocurrency
        for symbol in formatted_symbols:
            try:
                analysis = analyze_crypto(symbol, period)
                
                if isinstance(analysis, str):
                    results[symbol] = analysis
                    continue
                
                # Extract key performance metrics
                current_price = analysis["price_data"]["current_price"]
                period_change = analysis["price_data"]["period_change_pct"]
                volatility = analysis["price_data"]["volatility_annual"]
                
                # Extract technical indicators
                rsi = analysis["technical_indicators"]["rsi"]["current"]
                ma50 = analysis["technical_indicators"]["moving_averages"]["ma50"]
                ma200 = analysis["technical_indicators"]["moving_averages"]["ma200"]
                price_vs_ma50 = analysis["technical_indicators"]["moving_averages"]["price_vs_ma50"]
                price_vs_ma200 = analysis["technical_indicators"]["moving_averages"]["price_vs_ma200"]
                
                # Store performance data
                performance_data[symbol] = {
                    "name": analysis["name"],
                    "current_price": current_price,
                    "period_change_pct": period_change,
                    "vs_btc_change": period_change - btc_change,
                    "outperforming_btc": period_change > btc_change
                }
                
                # Store volatility data
                volatility_data[symbol] = {
                    "name": analysis["name"],
                    "volatility_annual": volatility,
                    "risk_level": "Very High" if volatility > 100 else "High" if volatility > 70 else "Moderate" if volatility > 40 else "Low"
                }
                
                # Store indicator data
                indicator_data[symbol] = {
                    "name": analysis["name"],
                    "rsi": rsi,
                    "ma50": ma50,
                    "ma200": ma200,
                    "price_vs_ma50": price_vs_ma50,
                    "price_vs_ma200": price_vs_ma200,
                    "trend": "Bullish" if price_vs_ma50 == "Above" and price_vs_ma200 == "Above" else 
                             "Bearish" if price_vs_ma50 == "Below" and price_vs_ma200 == "Below" else
                             "Mixed"
                }
                
            except Exception as e:
                results[symbol] = f"Error analyzing {symbol}: {str(e)}"
                
        # Rank by performance
        performance_ranking = sorted(
            [symbol for symbol in performance_data], 
            key=lambda s: performance_data[s]["period_change_pct"], 
            reverse=True
        )
        
        # Rank by volatility (lower is better)
        volatility_ranking = sorted(
            [symbol for symbol in volatility_data], 
            key=lambda s: volatility_data[s]["volatility_annual"]
        )
        
        # Compile results
        results = {
            "period": period,
            "btc_performance": btc_change,
            "performance_data": performance_data,
            "volatility_data": volatility_data,
            "indicator_data": indicator_data,
            "performance_ranking": performance_ranking,
            "volatility_ranking": volatility_ranking
        }
        
        return results
        
    except Exception as e:
        return f"Error comparing cryptocurrencies: {str(e)}"

if __name__ == "__main__":
    # Test the functions
    ticker = "AAPL"
    print(f"Testing financial tools with {ticker}")
    
    # Test stock analysis
    result = extract_financial_insights(ticker)
    print(json.dumps(result, indent=2)) 
    
    # Test investment advice
    advice = generate_investment_advice(ticker, risk_tolerance="moderate")
    print("\nInvestment Advice:")
    print(json.dumps(advice, indent=2))
    
    # Test cryptocurrency analysis
    crypto_symbol = "BTC-USD"
    print(f"\nTesting crypto analysis with {crypto_symbol}")
    crypto_result = analyze_crypto(crypto_symbol)
    print(json.dumps(crypto_result, indent=2))
    
    # Test crypto investment advice
    crypto_advice = generate_crypto_investment_advice(crypto_symbol, risk_tolerance="moderate")
    print("\nCrypto Investment Advice:")
    print(json.dumps(crypto_advice, indent=2))
    
    # Test cryptocurrency comparison
    crypto_symbols = "BTC-USD,ETH-USD,ADA-USD"
    print(f"\nTesting crypto comparison with {crypto_symbols}")
    comparison_result = compare_cryptos(crypto_symbols)
    print(json.dumps(comparison_result, indent=2)) 