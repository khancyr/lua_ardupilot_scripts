FROM python:3.12-slim

WORKDIR /app

# Install dependencies
COPY website/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the full repo so the app can read scripts from disk
COPY . /repo

# Copy the website app
COPY website/app ./app

ENV PYTHONPATH=/app
ENV REPO_ROOT=/repo

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/api/v1/health')"

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
