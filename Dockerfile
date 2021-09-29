
# pull official base image
FROM ubuntu:18.04

# This is not as skinny as it should be
RUN apt-get update && apt-get install -y \
        vim \
        build-essential \
        libpng-dev \
        libssl-dev \
		curl \
        git-core \
        python3-dev \
        python3-pip \
        bzip2 \
        libbz2-dev \
        liblzma-dev \
        libmysqlclient-dev \
        libasound2 libatk1.0-0 libc6 libcairo2 libcups2 libdbus-1-3 \
        libexpat1 libfontconfig1 libgcc1 libgconf-2-4 libgdk-pixbuf2.0-0 libglib2.0-0 libgtk-3-0 libnspr4 \
        libpango-1.0-0 libpangocairo-1.0-0 libstdc++6 libx11-6 libx11-xcb1 libxcb1 \
        libxcursor1 libxdamage1 libxext6 libxfixes3 libxi6 libxrandr2 libxrender1 libxss1 libxtst6 \
        libnss3

RUN curl -sL https://deb.nodesource.com/setup_12.x | bash \
    && apt-get install -y nodejs

RUN ln -s /usr/bin/python3 /usr/local/bin/python \
    && pip3 install --upgrade pip

# set work directory
WORKDIR /usr/src/seqview
USER root

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# install dependencies
RUN pip install --upgrade pip
COPY ./src/genome-browser /usr/src/seqview/
COPY ./src/genome-browser-client /usr/src/seqview/frontend/src/
COPY ./src/igv-webapp-embeddable /usr/src/seqview/frontend/src/src/igv-webapp-embeddable/
RUN pip install -r requirements.txt

WORKDIR /usr/src/seqview/frontend/src/
# Change this to git clone at some point
RUN npm install && npm run build

WORKDIR /usr/src/seqview/frontend/src/src/igv-webapp-embeddable/
RUN npm install && npm run build

WORKDIR /usr/src/seqview/
RUN python manage.py collectstatic --noinput
RUN cp /usr/src/seqview/frontend/src/src/igv-webapp-embeddable/dist/app_bundle-1.4.4.js /usr/src/seqview/static/frontend/app_bundle.js
RUN cp /usr/src/seqview/frontend/src/src/igv-webapp-embeddable/css/app.css /usr/src/seqview/static/frontend/
RUN cp /usr/src/seqview/frontend/src/src/igv-webapp-embeddable/css/fontawesome/all.css /usr/src/seqview/static/frontend/
RUN cp /usr/src/seqview/frontend/src/dist/main.js /usr/src/seqview/static/frontend/
RUN cp /usr/src/seqview/frontend/src/seqviewConfig.js /usr/src/seqview/static/frontend/
COPY ./igvwebConfig.js static/frontend/
COPY ./SeqViewLogoBanner.png static/frontend/

RUN cp -r /usr/src/seqview/static/ /tmp/
WORKDIR /usr/src/seqview

