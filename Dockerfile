FROM python:3.11-slim

WORKDIR /opt/minipay

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app/ ./app/
COPY web/ ./web/

RUN useradd --create-home minipay
RUN chown -R minipay:minipay /opt/minipay
USER minipay

EXPOSE 8080

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]
