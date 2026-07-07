FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
# Copy semua isi folder backend ke /app
COPY . . 
CMD ["python3", "app/main.py"]
