# Fixbot v2 - AI-Powered System Support Bot

An intelligent terminal-based system support bot powered by Google's Generative AI. Fixbot helps diagnose system issues, provide recommendations, and manage system tasks.

## Features

- 🤖 **AI-Powered Assistance** - Leverages Google's Generative AI for intelligent responses
- 💻 **System Diagnostics** - Analyzes CPU, memory, processes, and network status
- 🔍 **Intelligent Search** - Finds and manages files and applications
- 📝 **Report Generation** - Creates detailed system analysis reports
- 🛡️ **Permission Management** - Safe execution with permission gates
- 💾 **Conversation Memory** - Maintains context across sessions
- 🚀 **Vercel Ready** - Deploy as serverless API on Vercel

## Quick Start

### Local Development

1. **Clone the repository**

   ```bash
   git clone <repository-url>
   cd fixbot-v2-main
   ```

2. **Create virtual environment**

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

4. **Set environment variables**

   ```bash
   export GOOGLE_API_KEY="your-google-api-key"
   ```

   Get your API key from https://ai.google.dev

5. **Run the bot (CLI)**
   ```bash
   python -m sysdoc
   ```

### Vercel Deployment

See [VERCEL_DEPLOYMENT.md](VERCEL_DEPLOYMENT.md) for detailed deployment instructions.

**Quick deploy:**

1. Push code to GitHub
2. Import repository in Vercel dashboard
3. Add `GOOGLE_API_KEY` environment variable
4. Deploy!

## Project Structure

```
fixbot-v2-main/
├── sysdoc/                    # Main bot package
│   ├── core/                  # Core modules
│   │   ├── gemini_client.py   # AI integration
│   │   ├── executor.py        # System command execution
│   │   ├── intent_engine.py   # Intent detection
│   │   ├── permission_gate.py # Permission management
│   │   └── report_generator.py # Report creation
│   ├── display/               # UI components
│   ├── modules/               # Feature modules
│   ├── tickets/               # Ticket management
│   └── main.py                # CLI entry point
├── api/                       # Vercel API endpoints
│   ├── health.py              # Health check
│   ├── chat.py                # Chat endpoint
│   └── system-info.py         # System info endpoint
├── memory/                    # Conversation history
├── reports/                   # Generated reports
├── pyproject.toml             # Project metadata
├── requirements.txt           # Python dependencies
├── vercel.json                # Vercel configuration
└── VERCEL_DEPLOYMENT.md       # Deployment guide
```

## API Endpoints (Vercel)

### Health Check

```bash
GET /api/health
```

Returns service status and version.

### Chat

```bash
POST /api/chat
Content-Type: application/json

{
  "message": "Your question here"
}
```

Returns bot response based on user message.

### System Info

```bash
GET /api/system-info?type=all
```

Query parameters:

- `type`: `all`, `cpu`, `memory`, `processes`

Returns system information in JSON format.

## Usage Examples

### CLI Usage

```bash
# Start interactive session
python -m sysdoc

# Dry run (preview actions without executing)
python -m sysdoc --dry-run
```

### API Usage

```bash
# Using curl
curl -X POST https://your-project.vercel.app/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "What is my CPU usage?"}'

# Using Python
import requests

response = requests.post(
  'https://your-project.vercel.app/api/chat',
  json={'message': 'Analyze my system'}
)
print(response.json())
```

## Configuration

### Environment Variables

- `GOOGLE_API_KEY` - **Required** for AI features
- `DRY_RUN` - Set to enable dry-run mode (preview without execution)

### Vercel Configuration

Edit `vercel.json` to customize:

- Max function duration (default: 60 seconds)
- Memory allocation (default: 3008 MB)
- Build command
- Environment variables

## Requirements

- Python 3.9+
- Google Generative AI API key
- For local Windows development: psutil, wmi, pywin32
- For Vercel: streamlined dependencies (Linux-compatible)

## Commands (CLI)

- `help` - Show available commands
- `analyze` - Analyze system health
- `report` - Generate detailed report
- `find` - Search for files
- `install` - Get application installation help
- `exit`/`quit` - Exit the bot

## Development

### Running Tests

```bash
pip install pytest
pytest
```

### Building

```bash
python -m build
```

### Local API Testing

```bash
pip install -r requirements.txt
python -m sysdoc  # Use API endpoints
```

## Troubleshooting

### "GOOGLE_API_KEY not found"

- Ensure environment variable is set: `export GOOGLE_API_KEY="your-key"`
- Check your API key at https://ai.google.dev

### Module Import Errors

- Verify Python path: `python -c "import sysdoc"`
- Reinstall dependencies: `pip install -r requirements.txt`

### Vercel Deployment Fails

- Check logs: Vercel Dashboard > Deployments > [Your Deployment] > Logs
- Ensure all required environment variables are set
- Verify `vercel.json` is valid JSON

## Performance

- **API Response Time**: < 5 seconds average (depends on AI model)
- **System Analysis**: < 10 seconds for complete scan
- **Report Generation**: < 30 seconds for detailed reports

## Limitations

- Vercel runs on Linux (some Windows-specific features unavailable)
- Function timeout: 60 seconds (Vercel Pro) / 10 seconds (free)
- Memory limit: 3008 MB per function
- No persistent storage across invocations

## Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/your-feature`)
3. Commit changes (`git commit -am 'Add feature'`)
4. Push to branch (`git push origin feature/your-feature`)
5. Create Pull Request

## License

MIT License - See LICENSE file for details

## Support

For issues, questions, or suggestions:

1. Check existing [issues](https://github.com/yourusername/fixbot/issues)
2. Create a new issue with detailed description
3. Include system information from `analyze` command output

## Changelog

### v1.0.0 (2026-05-23)

- Initial release
- Added Vercel deployment support
- Implemented core chat API
- Added system information endpoints
- Full CLI interface

---

**Made with ❤️ for better system support**
