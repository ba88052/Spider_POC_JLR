#!/bin/bash
set -e
sudo apt-get update -y

# 下載Google-chrome
wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
sudo dpkg -i google-chrome-stable_current_amd64.deb || true

# 安裝依賴
sudo apt-get install -f -y

sudo apt-get update -y
sudo apt-get install -y libglib2.0-0 libgconf-2-4 libfontconfig1 libasound2 libnspr4 libnss3 libx11-xcb1 libxkbcommon0 libxss1 libxtst6 xdg-utils libxss1 libappindicator1 libindicator7 google-chrome-stable

# 下載對應的chromedriver
CHROME_VERSION=$(google-chrome-stable --version | awk '{ print $3 }' | cut -d '.' -f 1)
DRIVER_VERSION=$(curl -s "https://chromedriver.storage.googleapis.com/LATEST_RELEASE_${CHROME_VERSION}")
wget "https://chromedriver.storage.googleapis.com/${DRIVER_VERSION}/chromedriver_linux64.zip"
unzip chromedriver_linux64.zip
sudo mv chromedriver /usr/bin/chromedriver
sudo chown root:root /usr/bin/chromedriver
sudo chmod +x /usr/bin/chromedriver
rm chromedriver_linux64.zip

# 添加Google軟體源
wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | sudo apt-key add -
echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" | sudo tee /etc/apt/sources.list.d/google-chrome.list

# 確認版本：
google-chrome --version
chromedriver --version

#刪除下載檔案
rm google-chrome-stable_current_amd64.deb
rm LICENSE.chromedriver
