import os
from dotenv import load_dotenv

def load_environment():
    """Load environment variables from .env file"""
    # Load environment variables from .env file
    load_dotenv()
    
    # Check for required API keys
    required_keys = ["OPENAI_API_KEY"]
    missing_keys = [key for key in required_keys if not os.environ.get(key)]
    
    if missing_keys:
        print(f"ERROR: Missing required environment variables: {', '.join(missing_keys)}")
        print("Please set these variables in your .env file or environment.")
        return False
    
    # Check for optional but recommended keys
    recommended_keys = ["LLAMA_CLOUD_API_KEY"]
    missing_recommended = [key for key in recommended_keys if not os.environ.get(key)]
    
    if missing_recommended:
        print(f"WARNING: Missing recommended environment variables: {', '.join(missing_recommended)}")
        print("Some features may be limited without these keys.")
    
    return True

if __name__ == "__main__":
    # Test environment setup
    if load_environment():
        print("Environment successfully loaded with all required keys.")
    else:
        print("Environment setup incomplete. Please check your .env file.") 