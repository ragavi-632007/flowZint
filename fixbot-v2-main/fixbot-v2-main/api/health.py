"""Health check endpoint for Vercel deployment"""

def handler(request):
    """Health check endpoint"""
    return {
        "status": "ok",
        "service": "fixbot-api",
        "version": "1.0.0"
    }
