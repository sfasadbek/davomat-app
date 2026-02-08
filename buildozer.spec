name: Build APK

on:
  push:
    branches: [ main ]
  workflow_dispatch:

jobs:
  build:
    # Eng muhim joyi: ubuntu-latest tezkor serverni bildiradi
    runs-on: ubuntu-latest

    steps:
      - name: Checkout code
        uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'

      - name: Install dependencies
        run: |
          sudo apt-get update
          sudo apt-get install -y build-essential libffi-dev git zip unzip
          pip install --upgrade pip
          pip install buildozer cython==0.29.33 kivy requests

      - name: Build with Buildozer
        # yes | buyrug'i litsenziyalarni avtomatik tasdiqlaydi
        run: yes | buildozer -v android debug

      - name: Upload APK
        uses: actions/upload-artifact@v3
        with:
          name: STATS-MB-APK
          path: bin/*.apk
          
