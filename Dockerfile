FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY . .

ENV PORT=8080

EXPOSE ${PORT}

CMD ["python", "-m", "app.main"]
