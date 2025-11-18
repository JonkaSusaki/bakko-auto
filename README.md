# Bakko Auto

An automated Instagram scraping and content classification system that extracts post data from Instagram profiles and uses AI to classify posts as events or promotional content.

## Overview

Bakko Auto is a Python-based service that:
- Scrapes Instagram profile data using Selenium WebDriver
- Exposes a REST API (FastAPI) to fetch Instagram posts
- Integrates with n8n workflow automation
- Uses Google Gemini AI to analyze and classify Instagram posts as "Evento" (Event) or "Post de Aquecimento" (Warm-up Post)

## Features

- **Instagram Scraping**: Automated login and data extraction from Instagram profiles
- **GraphQL API Integration**: Fetches post data directly from Instagram's GraphQL endpoint
- **REST API**: FastAPI endpoint to retrieve Instagram profile data
- **AI Classification**: Uses Google Gemini to analyze posts and classify them
- **Workflow Automation**: n8n integration for automated processing pipelines
- **Docker Support**: Containerized deployment for both API and n8n services

## Project Structure

```
bakko-auto/
├── src/
│   ├── main.py                 # FastAPI application
│   ├── instagram_service.py    # Instagram scraping logic
│   ├── driver_chrome.py        # Selenium Chrome driver setup
│   ├── requirements.txt        # Python dependencies
│   └── Dockerfile.api          # FastAPI service Dockerfile
├── config.py                   # Configuration and credentials
├── docker-compose.yml          # n8n service configuration
├── Dockerfile                  # n8n Dockerfile
└── bakko_workflow.json         # n8n workflow definition
```

## Prerequisites

- Python 3.12+
- Docker and Docker Compose
- Chrome/Chromium browser (for local development)
- ChromeDriver (automatically installed in Docker)
- Google Gemini API credentials (for AI classification)
- Google Sheets API credentials (for n8n workflow)

## Installation

### Local Development

1. Clone the repository:
```bash
git clone <repository-url>
cd bakko-auto
```

2. Install Python dependencies:
```bash
cd src
pip install -r requirements.txt
```

3. Set up environment variables:
```bash
export INSTAGRAM_USER="your_instagram_username"
export INSTAGRAM_PASS="your_instagram_password"
```

Or edit `config.py` directly (not recommended for production).

4. Run the FastAPI service:
```bash
cd src
uvicorn main:app --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`

### Docker Deployment

1. Build and run the FastAPI service:
```bash
cd src
docker build -f Dockerfile.api -t bakko-api .
docker run -p 8000:8000 \
  -e INSTAGRAM_USER="your_username" \
  -e INSTAGRAM_PASS="your_password" \
  bakko-api
```

2. Start n8n workflow service:
```bash
docker-compose up -d
```

n8n will be available at `http://localhost:5678`

## Configuration

### Environment Variables

- `INSTAGRAM_USER`: Instagram username for login
- `INSTAGRAM_PASS`: Instagram password for login

### Config File

Edit `config.py` to customize:
- Login URL
- GraphQL endpoint settings
- Selenium selectors
- Query parameters

## API Usage

### Endpoints

#### `GET /`
Health check endpoint.

**Response:**
```json
{"Hello": "World"}
```

#### `GET /fetch/{username}`
Fetches Instagram profile data for a given username.

**Parameters:**
- `username` (path): Instagram username to fetch

**Response:**
```json
{
  "content": [
    {
      "caption": "Post caption text",
      "image": {
        "url": "https://...",
        "width": 1080,
        "height": 1080
      },
      "date": "2024-01-01T00:00:00"
    }
  ]
}
```

**Example:**
```bash
curl http://localhost:8000/fetch/aproveiteacidade
```

## n8n Workflow

The included `bakko_workflow.json` defines an n8n workflow that:
1. Reads organizer data from Google Sheets
2. Fetches Instagram posts via the API
3. Downloads and analyzes post images using Google Gemini
4. Classifies posts as "Evento" or "Post de Aquecimento"
5. Filters events based on confidence threshold

### Importing the Workflow

1. Access n8n at `http://localhost:5678`
2. Go to Workflows → Import from File
3. Select `bakko_workflow.json`
4. Configure credentials:
   - Google Sheets OAuth2
   - Google Gemini API

## How It Works

1. **Login**: The service logs into Instagram using Selenium
2. **Navigation**: Opens a new tab and navigates to the Instagram GraphQL endpoint
3. **Data Extraction**: Parses the HTML response to extract JSON data
4. **Post Processing**: Extracts captions, images, and dates from posts
5. **AI Analysis**: (via n8n) Uses Gemini to analyze images and classify content

## Dependencies

- **FastAPI**: Web framework for the REST API
- **Selenium**: Browser automation
- **BeautifulSoup4**: HTML parsing
- **uvicorn**: ASGI server

## Security Notes

⚠️ **Important**: 
- Never commit credentials to version control
- Use environment variables for sensitive data
- The current `config.py` contains hardcoded credentials - this should be changed for production
- Instagram may detect automated access - use responsibly

## Troubleshooting

### ChromeDriver Issues
If you encounter ChromeDriver version mismatches:
- Ensure Chrome and ChromeDriver versions match
- In Docker, ChromeDriver is automatically installed

### Login Failures
- Check Instagram credentials
- Instagram may require 2FA or challenge verification
- Add delays if needed in `instagram_service.py`

### API Timeouts
- Increase timeout values in `instagram_service.py`
- Check network connectivity
- Verify Instagram is accessible

## License

[Specify your license here]

## Contributing

[Add contribution guidelines if applicable]

## Support

[Add support/contact information if applicable]

