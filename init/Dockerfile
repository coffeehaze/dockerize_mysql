FROM python:3.9
WORKDIR /app
COPY requirements.txt .
COPY init.py .
RUN pip install --no-cache-dir -r requirements.txt
CMD ["python", "init.py"]