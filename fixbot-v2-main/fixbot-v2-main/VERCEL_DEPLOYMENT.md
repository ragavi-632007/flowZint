# Deployment Instructions for Vercel

## Setup

1. **Push to GitHub**

   ```bash
   git init
   git add .
   git commit -m "Initial commit with Vercel configuration"
   git remote add origin https://github.com/yourusername/fixbot.git
   git branch -M main
   git push -u origin main
   ```

2. **Deploy to Vercel**
   - Visit https://vercel.com/import
   - Import your GitHub repository
   - Add environment variables:
     - `GOOGLE_API_KEY`: Your Google Gemini API key
   - Deploy!

## API Endpoints

### Health Check

- **GET** `/api/health`
- Returns: Service status and version

### Chat

- **POST** `/api/chat`
- Body: `{"message": "Your question here"}`
- Returns: Bot response with conversation context

### System Info

- **GET** `/api/system-info?type=all`
- Query params: `type` (all, cpu, memory, processes)
- Returns: System information based on type

## Environment Variables

Required for production:

- `GOOGLE_API_KEY`: Google Generative AI API key (get from https://ai.google.dev)

## Testing Locally

```bash
# Install dependencies
pip install -r requirements.txt

# Test API endpoints using curl or Postman
curl -X POST http://localhost:3000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello"}'
```

## Notes

- Windows-specific modules (wmi, pywin32, winshell) are excluded for Vercel compatibility
- API endpoints run in serverless environment with 60-second timeout
- Memory allocated: 3008 MB per function
- For system info operations, note that Vercel runs on Linux, not Windows

## Monitoring

After deployment, monitor your API at:

- `https://your-project.vercel.app/api/health`
- Logs available in Vercel dashboard
