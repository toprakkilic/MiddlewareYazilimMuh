FROM python:3.11-slim

WORKDIR /app

ENV PYTHONUNBUFFERED=1

# Middleware katmanında hem ana kodumuzu hem de dinamik KVKK ayar dosyasını kopyalıyoruz
COPY main.py .
COPY mask_config.json .

# Çıktı log dosyalarının yazılacağı klasörü container içinde oluşturuyoruz
RUN mkdir -p /app/output_logs

CMD ["python", "main.py"]
