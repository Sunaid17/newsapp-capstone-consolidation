FROM python:3.12-slim

WORKDIR /app

RUN pip install --no-cache-dir --break-system-packages pip==24.0

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]