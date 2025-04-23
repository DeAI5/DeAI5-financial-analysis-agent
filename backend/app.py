import logging
import signal
from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import sys
import json
from werkzeug.exceptions import BadRequest
import uuid

# Import the new image generator function
from image_generator import generate_image_with_openai

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

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

# --- Globals for Image Task Data ---
# Store data needed to generate the image later {task_id: {prompt_data}}
image_tasks = {} 
# --- End Globals ---

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
            
            # Extract Response Text for Logging/Prompting
            response_text = ""
            if hasattr(response, 'response') and isinstance(response.response, str):
                response_text = response.response
            elif isinstance(response, dict) and 'response' in response and isinstance(response['response'], str):
                response_text = response['response']
            elif isinstance(response, str):
                 response_text = response
            else:
                 response_text = str(response) # Fallback
            logging.info(f"Response from financial agent: {response_text}")

            # --- Prepare for Separate Image Generation Request ---
            image_task_id = None
            if response_text: # Only create task if there is text
                image_task_id = str(uuid.uuid4())
                # Store necessary data for the prompt, keyed by task ID
                image_tasks[image_task_id] = {
                    "user_query": user_message, 
                    "agent_response": response_text
                }
                logging.info(f"Created image task {image_task_id[:6]} for later generation.")
            # --- End Prepare ---

            # Return the text response and task ID immediately
            response_data = {"response": response_text, "image_task_id": image_task_id}
            logging.info(f"<<< Returning initial response: {response_data}")
            return jsonify(response_data) # Return text and ID

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

# --- New Endpoint for Generating Image ---
@app.route('/api/generate_image/<task_id>', methods=['POST']) # Use POST as it triggers an action
def generate_image_endpoint(task_id):
    logging.info(f"Received request to generate image for task {task_id[:6]}")
    prompt_data = None
    prompt_data = image_tasks.pop(task_id, None) # Get data and remove task

    if prompt_data is None:
        logging.warning(f"Image task {task_id[:6]} not found or already processed.")
        return jsonify({"error": "Task not found or already processed"}), 404
    
    try:
        # Construct the new prompt
        prompt = f"Create a minimalist visualization of the key concept from this financial interaction. Do not include any text, numbers, or labels in the image.\n\nUser Query: {prompt_data['user_query']}\n\nAgent Response: {prompt_data['agent_response'][:500]}"
        logging.info(f"Generating image for task {task_id[:6]} with prompt: {prompt[:100]}...")

        # Call the OpenAI API (this will take time)
        image_url = generate_image_with_openai(prompt)

        if image_url:
            logging.info(f"Successfully generated image for task {task_id[:6]}")
            return jsonify({"image_url": image_url})
        else:
            logging.error(f"Image generation failed for task {task_id[:6]}")
            return jsonify({"error": "Image generation failed"}), 500

    except Exception as e:
        logging.error(f"Error during image generation for task {task_id[:6]}: {e}")
        return jsonify({"error": f"Image generation error: {e}"}), 500
# --- End New Endpoint ---

if __name__ == '__main__':
    logging.info("Starting Financial Agent API server on http://localhost:5000")
    app.run(host='0.0.0.0', port=5000, debug=True)