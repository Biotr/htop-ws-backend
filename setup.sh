#!/bin/bash

mkdir -p "$(dirname $WEBSOCKET_CERT_PATH)"
mkdir -p "$(dirname $WEBSOCKET_KEY_PATH)"

rm -f "$WEBSOCKET_KEY_PATH" "$WEBSOCKET_CERT_PATH"

echo "Creating certificates..."
openssl req -x509 -newkey rsa:4096 -nodes \
    -keyout "$WEBSOCKET_KEY_PATH" \
    -out "$WEBSOCKET_CERT_PATH" \
    -sha256 \
    -days 3650 \
    -subj "/C=PL/ST=Dolnoslaskie/L=Wroclaw/O=Dev/CN=localhost" \
    -addext "subjectAltName=DNS:localhost,IP:127.0.0.1"

if [ ! $? -eq 0 ]; then
    echo "Something went wrong. Try create certificates manually."
else
    echo "Certificates were successfully created."
fi

chmod  600 "$WEBSOCKET_KEY_PATH"
chmod  600 "$WEBSOCKET_CERT_PATH"