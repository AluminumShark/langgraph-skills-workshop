# 把作業小助教（程式 ＋ skills/ ＋ scripts/）裝進同一個容器
# 在 review-bot/ 資料夾裡：
#   docker build -t review-bot .
#   docker run -p 8080:8080 -e GOOGLE_API_KEY=你的key -e HOMEWORK_MCP_URL=https://遠端MCP網址/mcp review-bot
# 金鑰不要寫進這個檔案：部署時由雲端的 Secret Manager 變成環境變數注入
# 沒設 HOMEWORK_MCP_URL 的話，作業倉庫 MCP 會在同一個容器裡用 stdio 開起來（示範用）
FROM python:3.12-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 程式、手冊、腳本一起進映像：手冊和程式永遠是同一個版本
COPY . .

ENV WORKSHOP_PROVIDER=gemini \
    PORT=8080
CMD ["sh", "-c", "uvicorn deploy.server:app --host 0.0.0.0 --port ${PORT}"]
