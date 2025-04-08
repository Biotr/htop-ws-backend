#!/bin/bash
if [ ! -d ./certificates ]; then
    mkdir ./certificates
fi
echo "Creating certificates..."
openssl req -x509 -newkey rsa:4096 -keyout ./certificates/key.pem -out ./certificates/cert.pem -sha256 -days 3650 -nodes -subj "/C=XX/ST=StateName/L=CityName/O=CompanyName/OU=CompanySectionName/CN=biotr.github.io" -text 2>/dev/null
if [ ! $? -eq 0 ]; then
    echo "Something went wrong. Try create certificates manually."
else
    echo "Certificates were successfully created."
fi