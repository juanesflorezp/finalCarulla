#!/usr/bin/env bash

# Crear carpeta temporal para el binario de Chrome
mkdir -p .apt/usr/bin

# Descargar e instalar Google Chrome
wget -q -O - https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb > chrome.deb
dpkg -x chrome.deb .apt/
mv .apt/opt/google/chrome/google-chrome .apt/usr/bin/

# Descargar ChromeDriver compatible
CHROMEDRIVER_VERSION=`curl -sS chromedriver.storage.googleapis.com/LATEST_RELEASE`
wget -N https://chromedriver.storage.googleapis.com/$CHROMEDRIVER_VERSION/chromedriver_linux64.zip
unzip chromedriver_linux64.zip
mkdir -p .chromedriver/bin
mv chromedriver .chromedriver/bin/
chmod +x .chromedriver/bin/chromedriver
