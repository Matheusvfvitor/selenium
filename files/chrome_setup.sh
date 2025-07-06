#!/bin/bash
mkdir -p files
cd files

# Chrome headless
curl -SL https://github.com/adieuadieu/serverless-chrome/releases/download/v1.0.0-55/stable-headless-chromium-amazonlinux-2017-03.zip -o headless-chromium.zip
unzip headless-chromium.zip
chmod +x headless-chromium

# Chromedriver
curl -SL https://chromedriver.storage.googleapis.com/114.0.5735.90/chromedriver_linux64.zip -o chromedriver.zip
unzip chromedriver.zip
chmod +x chromedriver
