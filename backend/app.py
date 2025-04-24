import logging
import signal
import platform
import threading
from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import sys
import json
from werkzeug.exceptions import BadRequest

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

# Add the parent directory to sys.path to import the agent
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Use importlib to import the module with a hyphen in the filename
import importlib.util

# Get the absolute path to the agentic-rag.py file
module_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "agentic-rag.py")
logging.info(f"Attempting to load module from: {module_path}")

spec = importlib.util.spec_from_file_location("agentic_rag", module_path)
agentic_rag = importlib.util.module_from_spec(spec)
sys.modules["agentic_rag"] = agentic_rag
spec.loader.exec_module(agentic_rag)

# Import required functions for direct access
from coinmarketcap_api import get_cmc_crypto_data, get_cmc_crypto_market_overview

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "http://localhost:3000"}})

# Initialize the financial agent
logging.info("Initializing financial agent... (this may take a minute)")
financial_agent = agentic_rag.agent
logging.info("Financial agent initialized and ready!")

# Custom JSON encoder to handle non-serializable objects
class CustomJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        try:
            if hasattr(obj, 'to_dict'):
                return obj.to_dict()
            elif hasattr(obj, '__dict__'):
                return obj.__dict__
            elif hasattr(obj, 'response'):
                return str(obj.response)
            return str(obj)
        except Exception as e:
            logging.error(f"Error serializing object: {e}")
            return f"Unserializable object: {str(obj)}"

app.json_encoder = CustomJSONEncoder

# Timeout handler
class TimeoutException(Exception):
    pass

# Check if we're on Windows
is_windows = platform.system() == 'Windows'

# Set up the timeout handler only on Unix systems
if not is_windows:
    def timeout_handler(signum, frame):
        raise TimeoutException("Operation timed out")
    signal.signal(signal.SIGALRM, timeout_handler)

# Cross-platform function to run with timeout
def run_with_timeout(func, args=(), kwargs={}, timeout_duration=45):
    """Run a function with a timeout"""
    result = {"value": None, "exception": None}
    
    def worker():
        try:
            result["value"] = func(*args, **kwargs)
        except Exception as e:
            result["exception"] = e
    
    if is_windows:
        # Use threading based timeout for Windows
        thread = threading.Thread(target=worker)
        thread.daemon = True
        thread.start()
        thread.join(timeout_duration)
        if thread.is_alive():
            raise TimeoutException("Operation timed out")
        if result["exception"]:
            raise result["exception"]
        return result["value"]
    else:
        # Use signal based timeout for Unix systems
        signal.alarm(timeout_duration)
        try:
            result = func(*args, **kwargs)
            signal.alarm(0)  # Disable the alarm
            return result
        finally:
            signal.alarm(0)  # Ensure the alarm is disabled

@app.route('/api/chat', methods=['POST'])
def chat():
    try:
        try:
            data = request.json
        except BadRequest:
            logging.warning("Invalid JSON payload received")
            return jsonify({"error": "Invalid JSON payload"}), 400

        if not data or 'messages' not in data:
            logging.warning("Invalid request: 'messages' is required")
            return jsonify({"error": "Invalid request. 'messages' is required"}), 400
            
        messages = data['messages']
        user_message = next((m['content'] for m in reversed(messages) if m['role'] == 'user'), None)
        
        if not user_message:
            logging.warning("No user message found in the request")
            return jsonify({"error": "No user message found"}), 400
            
        logging.info(f"Received query: {user_message}")
        
        # Extract conversation history excluding system messages
        conversation_history = [
            {"role": m['role'], "content": m['content']} 
            for m in messages 
            if m['role'] != 'system'
        ]
        
        try:
            # Use the platform-independent timeout function with a longer timeout
            def get_agent_response():
                try:
                    # Check for common requests that might need special handling
                    lower_message = user_message.lower()
                    
                    # Set default response
                    if any(keyword in lower_message for keyword in ['bitcoin', 'btc', 'eth', 'ethereum', 'crypto', 'sui', 'sol', 'solana', 'compare']):
                        logging.info("Detected cryptocurrency request, using specialized function")
                        
                        # Check for general comparison requests
                        if ('compare' in lower_message or 'comparison' in lower_message or 'vs' in lower_message or 'versus' in lower_message):
                            # Check for Bitcoin vs Ethereum comparison
                            if (('bitcoin' in lower_message or 'btc' in lower_message) and 
                                ('ethereum' in lower_message or 'eth' in lower_message)):
                                # Bitcoin vs Ethereum comparison handler
                                logging.info("Detected Bitcoin vs Ethereum comparison request")
                                return handle_btc_eth_comparison()
                            # Check for other cryptocurrency comparisons
                            elif 'sui' in lower_message and ('sol' in lower_message or 'solana' in lower_message):
                                logging.info("Detected Sui vs Solana comparison request - using default agent")
                                # For other cryptocurrency pairs, use the default agent
                                return financial_agent.chat(user_message)
                            else:
                                # For other cryptocurrency comparisons, use the default agent
                                logging.info("Detected general cryptocurrency comparison - using default agent")
                                return financial_agent.chat(user_message)
                        
                    # Default behavior: use the agent
                    return financial_agent.chat(user_message)
                except Exception as e:
                    logging.error(f"Error in agent processing: {str(e)}")
                    return f"I encountered an issue while processing your request: {str(e)}. Please try a different query or check if the required API services are available."
            
            # Use a longer timeout for more complex queries
            response = run_with_timeout(get_agent_response, timeout_duration=90)
            
            if hasattr(response, 'response'):
                response_text = response.response
            elif isinstance(response, dict) and 'response' in response:
                response_text = response['response']
            else:
                response_text = str(response)
                
            logging.info(f"Response from financial agent: {response_text}")
            return jsonify({"message": response_text})
        except TimeoutException:
            logging.error("Financial agent took too long to respond")
            return jsonify({"error": "The financial agent took too long to respond"}), 504
        except Exception as agent_error:
            logging.error(f"Agent error: {str(agent_error)}")
            return jsonify({"message": f"I encountered an error processing your request: {str(agent_error)}"}), 500
    
    except Exception as e:
        logging.error(f"Unhandled error in chat endpoint: {str(e)}")
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500

@app.route('/api/test', methods=['GET'])
def test():
    logging.info("Test endpoint hit")
    return jsonify({"message": "Backend is working"})

@app.route('/health')
def health_check():
    return "Server is running", 200

@app.errorhandler(Exception)
def handle_exception(e):
    logging.error(f"Unhandled exception: {str(e)}")
    return jsonify({"error": "An internal error occurred"}), 500

# Handle Bitcoin vs Ethereum comparison
def handle_btc_eth_comparison():
    """Creates a detailed comparison between Bitcoin and Ethereum"""
    logging.info("Creating Bitcoin vs Ethereum comparison")
    custom_response = "I'll provide a comparison analysis of Bitcoin and Ethereum for you:\n\n"
    
    try:
        # Get data for both cryptocurrencies
        btc_data = get_cmc_crypto_data('BTC')
        eth_data = get_cmc_crypto_data('ETH')
        
        # Format comparison response
        custom_response += "## Bitcoin vs Ethereum Comparison\n\n"
        
        # Extract key metrics for comparison
        if isinstance(btc_data, dict) and isinstance(eth_data, dict):
            btc_quotes = btc_data.get('quotes', {})
            eth_quotes = eth_data.get('quotes', {})
            
            # Price comparison
            custom_response += "### Current Price\n"
            if 'quote' in btc_quotes and 'USD' in btc_quotes['quote'] and \
               'quote' in eth_quotes and 'USD' in eth_quotes['quote']:
                btc_price = btc_quotes['quote']['USD'].get('price', 0)
                eth_price = eth_quotes['quote']['USD'].get('price', 0)
                price_ratio = btc_price / eth_price if eth_price else 0
                
                custom_response += f"- Bitcoin: ${btc_price:,.2f}\n"
                custom_response += f"- Ethereum: ${eth_price:,.2f}\n"
                custom_response += f"- BTC is {price_ratio:.1f}x more expensive than ETH\n\n"
            
            # Market Cap comparison
            custom_response += "### Market Capitalization\n"
            if 'quote' in btc_quotes and 'USD' in btc_quotes['quote'] and \
               'quote' in eth_quotes and 'USD' in eth_quotes['quote']:
                btc_mcap = btc_quotes['quote']['USD'].get('market_cap', 0)
                eth_mcap = eth_quotes['quote']['USD'].get('market_cap', 0)
                mcap_ratio = btc_mcap / eth_mcap if eth_mcap else 0
                
                custom_response += f"- Bitcoin: ${btc_mcap:,.2f}\n"
                custom_response += f"- Ethereum: ${eth_mcap:,.2f}\n"
                custom_response += f"- BTC market cap is {mcap_ratio:.1f}x larger than ETH\n\n"
            
            # Performance comparison
            custom_response += "### Performance Comparison\n"
            if 'quote' in btc_quotes and 'USD' in btc_quotes['quote'] and \
               'quote' in eth_quotes and 'USD' in eth_quotes['quote']:
                # 24h change
                btc_24h = btc_quotes['quote']['USD'].get('percent_change_24h', 0)
                eth_24h = eth_quotes['quote']['USD'].get('percent_change_24h', 0)
                
                # 7d change
                btc_7d = btc_quotes['quote']['USD'].get('percent_change_7d', 0)
                eth_7d = eth_quotes['quote']['USD'].get('percent_change_7d', 0)
                
                # 30d change
                btc_30d = btc_quotes['quote']['USD'].get('percent_change_30d', 0)
                eth_30d = eth_quotes['quote']['USD'].get('percent_change_30d', 0)
                
                custom_response += "#### 24 Hour Performance\n"
                custom_response += f"- Bitcoin: {btc_24h:.2f}%\n"
                custom_response += f"- Ethereum: {eth_24h:.2f}%\n"
                if btc_24h > eth_24h:
                    custom_response += f"- Bitcoin is outperforming Ethereum by {btc_24h - eth_24h:.2f}% in the last 24 hours\n\n"
                else:
                    custom_response += f"- Ethereum is outperforming Bitcoin by {eth_24h - btc_24h:.2f}% in the last 24 hours\n\n"
                    
                custom_response += "#### 7 Day Performance\n"
                custom_response += f"- Bitcoin: {btc_7d:.2f}%\n"
                custom_response += f"- Ethereum: {eth_7d:.2f}%\n"
                if btc_7d > eth_7d:
                    custom_response += f"- Bitcoin is outperforming Ethereum by {btc_7d - eth_7d:.2f}% over the last week\n\n"
                else:
                    custom_response += f"- Ethereum is outperforming Bitcoin by {eth_7d - btc_7d:.2f}% over the last week\n\n"
                    
                custom_response += "#### 30 Day Performance\n"
                custom_response += f"- Bitcoin: {btc_30d:.2f}%\n"
                custom_response += f"- Ethereum: {eth_30d:.2f}%\n"
                if btc_30d > eth_30d:
                    custom_response += f"- Bitcoin is outperforming Ethereum by {btc_30d - eth_30d:.2f}% over the last month\n\n"
                else:
                    custom_response += f"- Ethereum is outperforming Bitcoin by {eth_30d - btc_30d:.2f}% over the last month\n\n"
            
            # Supply comparison
            custom_response += "### Supply Information\n"
            btc_supply = btc_quotes.get('circulating_supply', 0)
            eth_supply = eth_quotes.get('circulating_supply', 0)
            btc_max = btc_quotes.get('max_supply', 0)
            
            custom_response += f"- Bitcoin Circulating Supply: {btc_supply:,.0f} BTC\n"
            custom_response += f"- Bitcoin Max Supply: {btc_max:,.0f} BTC\n"
            custom_response += f"- Ethereum Circulating Supply: {eth_supply:,.0f} ETH\n"
            custom_response += f"- Unlike Bitcoin, Ethereum does not have a fixed maximum supply cap\n\n"
            
            # Trading volume comparison
            custom_response += "### Trading Volume (24h)\n"
            if 'quote' in btc_quotes and 'USD' in btc_quotes['quote'] and \
               'quote' in eth_quotes and 'USD' in eth_quotes['quote']:
                btc_vol = btc_quotes['quote']['USD'].get('volume_24h', 0)
                eth_vol = eth_quotes['quote']['USD'].get('volume_24h', 0)
                vol_ratio = btc_vol / eth_vol if eth_vol else 0
                
                custom_response += f"- Bitcoin: ${btc_vol:,.2f}\n"
                custom_response += f"- Ethereum: ${eth_vol:,.2f}\n"
                custom_response += f"- BTC trading volume is {vol_ratio:.1f}x larger than ETH\n\n"
            
            # Market dominance comparison
            custom_response += "### Market Dominance\n"
            if 'quote' in btc_quotes and 'USD' in btc_quotes['quote'] and \
               'quote' in eth_quotes and 'USD' in eth_quotes['quote']:
                btc_dom = btc_quotes['quote']['USD'].get('market_cap_dominance', 0)
                eth_dom = eth_quotes['quote']['USD'].get('market_cap_dominance', 0)
                
                custom_response += f"- Bitcoin: {btc_dom:.2f}%\n"
                custom_response += f"- Ethereum: {eth_dom:.2f}%\n\n"
            
            # Summary and analysis
            custom_response += "### Summary\n"
            custom_response += "Bitcoin remains the dominant cryptocurrency in terms of market capitalization and price, acting primarily as a store of value and digital gold. "
            custom_response += "Ethereum, on the other hand, offers smart contract functionality and serves as the foundation for decentralized applications, DeFi, and NFTs.\n\n"
            
            # Investment perspectives
            custom_response += "### Investment Perspective\n"
            if btc_7d > 0 and eth_7d > 0:
                custom_response += "Both assets are showing positive momentum in the current market. "
                if btc_7d > eth_7d:
                    custom_response += "Bitcoin is currently outperforming Ethereum, which might suggest a market preference for the more established cryptocurrency in the current environment."
                else:
                    custom_response += "Ethereum is currently outperforming Bitcoin, which might indicate growing interest in smart contract platforms and the broader Ethereum ecosystem."
            elif btc_7d > 0 and eth_7d <= 0:
                custom_response += "Bitcoin is showing positive momentum while Ethereum is declining, which could indicate a flight to the more established cryptocurrency in uncertain market conditions."
            elif btc_7d <= 0 and eth_7d > 0:
                custom_response += "Ethereum is showing positive momentum while Bitcoin is declining, which might signal growing interest in smart contract platforms over pure store-of-value cryptocurrencies."
            else:
                custom_response += "Both assets are currently in a downtrend, reflecting broader market uncertainty. During such periods, cryptocurrency markets often experience increased volatility."
        else:
            custom_response += "I couldn't retrieve detailed data for both cryptocurrencies to make a proper comparison.\n\n"
    except Exception as e:
        logging.error(f"Error creating comparison analysis: {str(e)}")
        custom_response += "I encountered an error while creating the comparison analysis. Here's what I know:\n\n"
        custom_response += "Bitcoin (BTC) is the first and largest cryptocurrency by market capitalization, often compared to digital gold and primarily used as a store of value. It has a fixed supply cap of 21 million coins.\n\n"
        custom_response += "Ethereum (ETH) is the second-largest cryptocurrency and offers smart contract functionality, serving as the foundation for thousands of decentralized applications, DeFi protocols, and NFTs. Unlike Bitcoin, Ethereum does not have a fixed maximum supply.\n\n"
        custom_response += "Both have different use cases and investment characteristics, with Bitcoin generally considered more of a store of value while Ethereum aims to be a decentralized computing platform."
    
    return custom_response

if __name__ == '__main__':
    logging.info("Starting Financial Agent API server on http://localhost:5000")
    app.run(host='0.0.0.0', port=5000, debug=True)