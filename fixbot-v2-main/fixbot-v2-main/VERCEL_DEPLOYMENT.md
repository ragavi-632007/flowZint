# Deployment Instructions for Vercel

Complete guide to deploy Fixbot v2 to Vercel as a serverless application.

## Prerequisites

- GitHub account with a repository
- Vercel account (free at https://vercel.com)
- Google Generative AI API key (free at https://ai.google.dev)
- Python 3.9+ (for local testing)
- Git installed

## Step-by-Step Setup

### 1. Prepare Your Repository

```bash
# Initialize git if not already done
git init

# Add all files
git add .

# Create initial commit
git commit -m "Initial commit: Fixbot v2 with Vercel configuration"

# Add remote repository
git remote add origin https://github.com/yourusername/fixbot.git

# Rename branch to main
git branch -M main

# Push to GitHub
git push -u origin main
```

### 2. Deploy to Vercel

**Option A: Using Vercel Dashboard (Recommended)**

1. Go to https://vercel.com/dashboard
2. Click "Add New..." → "Project"
3. Select "Import Git Repository"
4. Paste your GitHub repository URL
5. Click "Import"
6. Add environment variables:
   - `GOOGLE_API_KEY`: Your Google Gemini API key
7. Click "Deploy"

**Option B: Using Vercel CLI**

```bash
# Install Vercel CLI
npm install -g vercel

# Login to Vercel
vercel login

# Deploy from project root
vercel

# Follow prompts and add environment variables
```

### 3. Configure Environment Variables

In Vercel Dashboard:

1. Go to Settings → Environment Variables
2. Add `GOOGLE_API_KEY` with your Google API key
3. Select environments: Production, Preview, Development
4. Click "Save"

## API Endpoints Reference

### 1. Health Check

**Endpoint:** `GET /api/health`

**Description:** Check if the API is running and responsive

**Response:**

```json
{
  "status": "ok",
  "service": "fixbot-api",
  "version": "1.0.0"
}
```

### 2. Chat Endpoint

**Endpoint:** `POST /api/chat`

**Request Body:**

```json
{
  "message": "What is my system status?"
}
```

**Response:**

```json
{
  "success": true,
  "message": "Your question here",
  "response": "Bot's response here"
}
```

### 3. System Information Endpoint

**Endpoint:** `GET /api/system-info?type=all`

**Query Parameters:**

- `type`: `all` (default), `cpu`, `memory`, `processes`

**Response:**

```json
{
  "success": true,
  "type": "all",
  "data": {
    "cpu": {...},
    "memory": {...},
    "timestamp": "2026-05-23T12:34:56Z"
  }
}
```

## Environment Variables

### Required

- **`GOOGLE_API_KEY`** - Google Generative AI API key (get from https://ai.google.dev)

### Optional

- **`DEBUG`** - Enable debug mode (default: false)
- **`VERCEL_ENV`** - Environment name (production/preview/development)

## Testing Locally

```bash
# Install dependencies
pip install -r requirements.txt

# Test health endpoint
curl http://localhost:3000/api/health

# Test chat endpoint
curl -X POST http://localhost:3000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello"}'

# Test system info
curl http://localhost:3000/api/system-info?type=cpu
```

## Troubleshooting

**Issue: "GOOGLE_API_KEY not found"**

- Solution: Add environment variable in Vercel Settings

**Issue: 500 Error from API**

- Check Vercel logs for detailed error messages
- Verify API key is valid
- Test locally first

**Issue: Function timeout**

- Requests taking longer than 60 seconds
- Optimize queries or increase timeout in vercel.json

## Monitoring

View Vercel Dashboard:

1. Go to Vercel Dashboard
2. Select your project
3. Click "Deployments"
4. Select a deployment
5. Click "Logs" tab

Monitor your API health at:

- `https://your-project.vercel.app/api/health`

View analytics:

- Request count
- Response times
- Error rates
- Bandwidth usage
- CPU/Memory usage
