#!/bin/sh

while inotifywait -e modify /etc/letsencrypt/live/genieslack.kusshi.dev/; do
    nginx -s reload
done
