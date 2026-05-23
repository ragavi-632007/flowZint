"""
Example API Client for Fixbot Vercel Deployment

Usage:
    python example_client.py
"""

import requests
import json

# Replace with your Vercel deployment URL
BASE_URL = "https://your-project.vercel.app"

def check_health():
    """Check API health status"""
    response = requests.get(f"{BASE_URL}/api/health")
    print("Health Check:")
    print(json.dumps(response.json(), indent=2))
    return response.json()

def send_message(message):
    """Send a message to the fixbot API"""
    payload = {"message": message}
    response = requests.post(
        f"{BASE_URL}/api/chat",
        json=payload,
        headers={"Content-Type": "application/json"}
    )
    print(f"\nMessage: {message}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    return response.json()

def get_system_info(info_type="all"):
    """Get system information"""
    response = requests.get(
        f"{BASE_URL}/api/system-info",
        params={"type": info_type}
    )
    print(f"\nSystem Info ({info_type}):")
    print(json.dumps(response.json(), indent=2))
    return response.json()

if __name__ == "__main__":
    # Test endpoints
    check_health()
    send_message("What can you help me with?")
    get_system_info("all")
