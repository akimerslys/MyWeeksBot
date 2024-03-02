FROM python3.11.8-alpine3.19
ENV PYTHONWRITEBYCODE=1
ENV PYTHONUNBUFFERED=1
WORKDIR /app
COPY . .
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt