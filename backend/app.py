from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import sys
import json

# Add the parent directory to sys.path to import the agent
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Use importlib to import the module with a hyphen in the filename
import importlib.util

# Get the absolute path to the agentic-rag.py file
module_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "agentic-rag.py")
print(f"Attempting to load module from: {module_path}")

spec = importlib.util.spec_from_file_location("agentic_rag", module_path)
agentic_rag = importlib.util.module_from_spec(spec)
sys.modules["agentic_rag"] = agentic_rag
spec.loader.exec_module(agentic_rag)

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "http://localhost:3000"}})

# Initialize the financial agent
print("Initializing financial agent... (this may take a minute)")
# The agent is already created in the module, just access it directly
financial_agent = agentic_rag.agent
print("Financial agent initialized and ready!")

# Custom JSON encoder to handle non-serializable objects
class CustomJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        # Handle specific types that might come from LlamaIndex
        try:
            # Try to get a dictionary representation
            if hasattr(obj, 'to_dict'):
                return obj.to_dict()
            elif hasattr(obj, '__dict__'):
                return obj.__dict__
            # For objects from agent tools
            elif hasattr(obj, 'response'):
                return str(obj.response)
            # Try to convert to string as a fallback
            return str(obj)
        except:
            # Last resort, convert to string
            return f"Unserializable object: {str(obj)}"

# Use the custom encoder for Flask's jsonify
app.json_encoder = CustomJSONEncoder

@app.route('/api/chat', methods=['POST'])
def chat():
    try:
        data = request.json
        
        if not data or 'messages' not in data:
            return jsonify({"error": "Invalid request. 'messages' is required"}), 400
            
        messages = data['messages']
        
        # Get the last user message
        user_message = next((m['content'] for m in reversed(messages) if m['role'] == 'user'), None)
        
        if not user_message:
            return jsonify({"error": "No user message found"}), 400
            
        # Extract conversation history excluding system messages
        conversation_history = [
            {"role": m['role'], "content": m['content']} 
            for m in messages 
            if m['role'] != 'system'
        ]
        
        # Log the received query
        print(f"Received query: {user_message}")
        
        # Get response from the financial agent
        try:
            response = financial_agent.chat(user_message)
            
            # Extract the text response if the result is more complex
            if hasattr(response, 'response'):
                response_text = response.response
            elif isinstance(response, dict) and 'response' in response:
                response_text = response['response']
            else:
                response_text = str(response)
                
            print(f"Response: {response_text}")
            return jsonify({"message": response_text})
        except Exception as agent_error:
            print(f"Agent error: {str(agent_error)}")
            error_message = str(agent_error)
            return jsonify({"message": f"I encountered an error processing your request: {error_message}"}), 500
    
    except Exception as e:
        print(f"Error in chat endpoint: {str(e)}")
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500

if __name__ == '__main__':
    print("Starting Financial Agent API server on http://localhost:5000")
    app.run(host='0.0.0.0', port=5000, debug=True) 