import logging
import signal
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

def timeout_handler(signum, frame):
    raise TimeoutException("Operation timed out")

signal.signal(signal.SIGALRM, timeout_handler)

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
            # Set a timeout for the financial agent's response
            signal.alarm(45)  # 45-second timeout
            response = financial_agent.chat(user_message)
            signal.alarm(0)  # Disable the alarm
            
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
        logging.error(f"Error in chat endpoint: {str(e)}")
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500

@app.route('/api/test', methods=['GET'])
def test():
    logging.info("Test endpoint hit")
    return jsonify({"message": "Backend is working"})

@app.errorhandler(Exception)
def handle_exception(e):
    logging.error(f"Unhandled exception: {str(e)}")
    return jsonify({"error": "An internal error occurred"}), 500

if __name__ == '__main__':
    logging.info("Starting Financial Agent API server on http://localhost:5000")
    app.run(host='0.0.0.0', port=5000, debug=True)