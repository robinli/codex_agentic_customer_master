FROM python:3.12-slim

WORKDIR /app/backend

COPY backend/requirements.txt /app/backend/requirements.txt
RUN pip install --no-cache-dir -r /app/backend/requirements.txt

COPY backend /app/backend

RUN chmod +x /app/backend/start.sh

EXPOSE 8000

CMD ["/app/backend/start.sh"]
