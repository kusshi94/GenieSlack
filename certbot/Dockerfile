FROM certbot/certbot:v2.6.0

COPY ./certbot.sh /certbot.sh
RUN chmod +x /certbot.sh

ENTRYPOINT ["/certbot.sh"]
