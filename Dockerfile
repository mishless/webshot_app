FROM --platform=linux/amd64 python:3.12

ENV DEBIAN_FRONTEND noninteractive
ENV CHROME_VERSION=118.0.5993.70

# install google chrome
RUN apt-get update && apt-get install -y unzip sqlite3 libnss3 libatk1.0-0 libatk-bridge2.0-0 libcups2 \
        libdrm2 libxkbcommon0 libxcomposite1 libxdamage1 libxfixes3 libxrandr2 libasound2 libgbm1
RUN wget -q -O /tmp/chrome.zip https://edgedl.me.gvt1.com/edgedl/chrome/chrome-for-testing/$CHROME_VERSION/linux64/chrome-linux64.zip
RUN unzip /tmp/chrome.zip -d /opt
ENV PATH="${PATH}:/opt/chrome-linux64"

# install chrome driver
RUN wget -q -O /tmp/chromedriver.zip https://edgedl.me.gvt1.com/edgedl/chrome/chrome-for-testing/$CHROME_VERSION/linux64/chromedriver-linux64.zip
RUN unzip /tmp/chromedriver.zip -d /usr/local/bin/

# set display port to avoid crash
ENV DISPLAY=:99

WORKDIR /webshot_app
COPY ./pyproject.toml /webshot_app/pyproject.toml
COPY ./app /webshot_app/app
COPY ./db /webshot_app/db
COPY ./main.py /webshot_app/main.py
COPY ./root.py /webshot_app/root.py

RUN python -m pip install poetry
RUN poetry install


CMD ["poetry", "run", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80"]

