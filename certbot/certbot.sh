#!/bin/sh

trap exit TERM
while :; do 
    certbot renew -w /var/www/certbot --quiet
    sleep 7d &
    wait $!
done