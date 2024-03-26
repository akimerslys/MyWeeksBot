FROM ngrok/ngrok:latest
COPY ngrok.yml ngrok.yml
CMD ["start", "--all", "--config=/ngrok.yml"]
