FROM python:3.12-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV ZABEDSEC_ALLOWED_HOSTS=localhost,127.0.0.1

EXPOSE 8000
CMD ["uvicorn", "zabedsec.api:app", "--host", "0.0.0.0", "--port", "8000"]
