FROM python:3.9
WORKDIR /app
COPY requirements.txt .
COPY main.py .
COPY config.json .
RUN pip install --no-cache-dir -r requirements.txt
CMD ["python", "main.py"]