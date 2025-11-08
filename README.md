# News Summarizer – AWS Lambda + LangChain + Gemini

This project deploys a serverless Flask API on AWS Lambda that accepts a news article URL, fetches and cleans the article, and returns a concise Gemini-powered summary. It also includes a minimal HTML interface and testing instructions.

<img width="1778" height="761" alt="image" src="https://github.com/user-attachments/assets/a54ff11f-f81c-4efc-9cc4-848cc1ee150f" />

## Features

- `POST /summarize` endpoint (Flask → AWS API Gateway → Lambda)
- LangChain chain wrapping Google Gemini (free tier) via `langchain-google-genai`
- Article extraction with `readability-lxml` and `BeautifulSoup`
- Error-handling for malformed requests and upstream failures
- Static HTML UI (`static/index.html`) for quick manual testing
- SAM template for repeatable deployments, including SSM Parameter Store integration for API keys

## Prerequisites

- Python 3.12
- AWS CLI v2 configured with deployment credentials
- AWS SAM CLI (`sam --version`)
- Google AI Studio API key (Gemini free tier) stored locally as `GOOGLE_API_KEY`

## Local Development

```bash
python -m venv .venv
source .venv/bin/activate        # Windows PowerShell: .venv\Scripts\Activate.ps1
pip install -r requirements.txt

# Export environment variables for Flask
setx GOOGLE_API_KEY "<your-gemini-api-key>"    # PowerShell: $env:GOOGLE_API_KEY = "..."

flask --app app run --port 8000
```

Test locally:

```bash
curl --request POST http://127.0.0.1:8000/summarize \
     --header "Content-Type: application/json" \
     --data '{"url": "https://example.com/news"}'
```

Open `http://127.0.0.1:8000/static/index.html` in a browser for the UI.

## Deployment Steps (AWS SAM)

1. **Create Parameter Store entry for Gemini key**

   ```bash
   aws ssm put-parameter \
     --name /news-summarizer/google-api-key \
     --type SecureString \
     --value <your-gemini-api-key>
   ```

2. **Build and package**

   ```bash
   sam build --use-container
   sam deploy \
     --guided \
     --parameter-overrides StageName=prod \
     --stack-name news-summarizer \
     --capabilities CAPABILITY_IAM
   ```

3. **Record the API endpoint** shown after deployment.

4. **Smoke test**

   ```bash
   API_URL="https://<api-id>.execute-api.<region>.amazonaws.com/prod"
   curl --request POST "$API_URL/summarize" \
     --header "Content-Type: application/json" \
     --data '{"url": "https://example.com/news"}'
   ```

5. **Serve the UI** locally or host it (e.g., S3 static site). Update the fetch URL to the deployed endpoint if hosting separately.

## Environment Variables

- `GOOGLE_API_KEY` (required) – Gemini API key
- `GEMINI_MODEL` (optional) – override default `gemini-2.0-flash`
- `MAX_ARTICLE_CHARS` (optional) – limit article text passed to Gemini (default `8000`)

## Minimal HTML Tester

The `static/index.html` file uses a relative POST to `/summarize`. When hosting separately, swap the fetch URL:

```javascript
const response = await fetch("https://<api-id>.execute-api.<region>.amazonaws.com/prod/summarize", { ... })
```

## Context7 MCP Traceability

Documentation for the Gemini + LangChain integration was sourced automatically using Context7 MCP (`/langchain-ai/langchain-google` library ID) to ensure the latest usage patterns for `ChatGoogleGenerativeAI`.

## Troubleshooting

- `GOOGLE_API_KEY is required` → set the key locally or in Lambda environment variables.
- HTTP 502/504 from `/summarize` → target site may block scraping; try a different article URL.
- SAM deployment access denied → ensure IAM user/role has `cloudformation:*`, `iam:PassRole`, `ssm:GetParameter` permissions.

## License

MIT

