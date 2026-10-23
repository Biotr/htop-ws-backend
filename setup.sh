#!/bin/bash

CERT_DIR="./certificates"
KEY_FILE="$CERT_DIR/key.pem"
CERT_FILE="$CERT_DIR/cert.pem"

mkdir -p "$CERT_DIR"

rm -f "$KEY_FILE" "$CERT_FILE"

echo "Creating certificates..."
openssl req -x509 -newkey rsa:4096 -nodes \
    -keyout "$KEY_FILE" \
    -out "$CERT_FILE" \
    -sha256 \
    -days 3650 \
    -subj "/C=PL/ST=Dolnoslaskie/L=Wroclaw/O=Dev/CN=localhost" \
    -addext "subjectAltName=DNS:localhost,IP:127.0.0.1"

if [ ! $? -eq 0 ]; then
    echo "Something went wrong. Try create certificates manually."
else
    echo "Certificates were successfully created."
fi

chmod  600 "$KEY_FILE"
chmod  600 "$CERT_FILE"