# Put the Homework Helper (code + skills/ + scripts/) into one container
# From inside the review-bot/ folder:
#   docker build -t review-bot .
#   docker run -p 8080:8080 -e GOOGLE_API_KEY=your-key -e HOMEWORK_MCP_URL=https://your-remote-mcp-url/mcp review-bot
# Don't write keys into this file: when deploying, the cloud's Secret Manager injects them as environment variables
# If HOMEWORK_MCP_URL is not set, the homework repo MCP is started inside the same container over stdio (for demos)
FROM python:3.12-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Code, handbooks and scripts all go into the image, so the handbooks and the code are always the same version
COPY . .

ENV WORKSHOP_PROVIDER=gemini \
    PORT=8080
CMD ["sh", "-c", "uvicorn deploy.server:app --host 0.0.0.0 --port ${PORT}"]
