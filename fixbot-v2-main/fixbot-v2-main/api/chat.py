"""Chat API endpoint for fixbot"""

import json
import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sysdoc.core.gemini_client import GeminiClient
from sysdoc.core.conversation_memory import ConversationMemory


def handler(request):
    """
    Chat endpoint that accepts a message and returns bot response
    
    Expected POST body:
    {
        "message": "user message here"
    }
    """
    
    if request.method != "POST":
        return {
            "error": "Method not allowed. Use POST.",
            "allowed_methods": ["POST"]
        }, 405
    
    try:
        # Parse request body
        body = request.get_json()
        user_message = body.get("message", "").strip()
        
        if not user_message:
            return {
                "error": "Message field is required and cannot be empty"
            }, 400
        
        # Initialize Gemini client
        api_key = os.environ.get("GOOGLE_API_KEY")
        if not api_key:
            return {
                "error": "GOOGLE_API_KEY environment variable not set"
            }, 500
        
        client = GeminiClient(api_key)
        
        # Get bot response
        response = client.generate_response(user_message)
        
        return {
            "success": True,
            "message": user_message,
            "response": response
        }, 200
        
    except json.JSONDecodeError:
        return {
            "error": "Invalid JSON in request body"
        }, 400
    except Exception as e:
        return {
            "error": f"Internal server error: {str(e)}"
        }, 500
