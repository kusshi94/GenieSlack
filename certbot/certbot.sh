#!/bin/sh

trap exit TERM
while :; do 
    certbot renew -w /var/www/certbot --post-hook "nginx -s reload" --quiet
    sleep 7d &
    wait $!
done