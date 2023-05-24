# nginx for https reverse proxy
FROM nginx:1.24.0-alpine
RUN apk add --no-cache inotify-tools
COPY ./default.conf /etc/nginx/conf.d/default.conf
COPY ./watch-certificate.sh /watch-certificate.sh
RUN chmod +x /watch-certificate.sh
CMD ["/bin/sh", "-c", "/watch-certificate.sh & nginx -g 'daemon off;'"]