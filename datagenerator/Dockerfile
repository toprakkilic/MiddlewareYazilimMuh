# 1. Temel imaj: Python 3.11'in hafif (slim) sürümünü kullanıyoruz
FROM python:3.11-slim

# 2. Container içindeki çalışma dizini /app olsun
WORKDIR /app

# 3. Python'un çıktıları buffer'a almadan anlık terminale basmasını sağlayan ayar
ENV PYTHONUNBUFFERED=1

# 4. Bilgisayarımızdaki generator.py kodunu container içine kopyala
COPY generator.py .

# 5. Container başladığında bu kodu çalıştır
CMD ["python", "generator.py"]
