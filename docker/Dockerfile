#
# Docker Buildfile for the radio-streams container based on alpine linux - about 41.4MB
# put dockerfile and bootstrap.sh in same directory and build or enter
# docker build  https://github.com/bitstreamout/radio-streams
#
FROM alpine:latest AS build

#
# Upgrade alpine Linux, install python3 and dependencies for pillow - alpine does not use glibc
# pip install needed modules for radio-streams
# make /opt/radio-streams Directory, delete unneeded packages
# download radio-streams tar.gz and extract it in radio-streams Directory
# delete unneeded stuff
#

ENV PYCURL_SSL_LIBRARY=openssl

RUN apk --no-cache update && \
    apk --no-cache upgrade && \
    apk add --no-cache python3 && \
    apk add --no-cache py3-pip && \
    apk add --no-cache build-base && \
    apk add --no-cache curl-dev && \
    apk add --no-cache python3-dev && \
    pip3 install --no-cache-dir --break-system-packages pycurl && \
    pip3 install --no-cache-dir --break-system-packages wheel && \
    pip3 install --no-cache-dir --break-system-packages tornado && \
    mkdir /opt/radio-streams && \
    apk del --no-cache python3-dev && \
    apk del --no-cache build-base && \
    apk add --no-cache libcurl && \
    apk add --no-cache curl && \
    curl -L https://codeload.github.com/bitstreamout/radio-streams/tar.gz/master \
        | tar xvzC /opt/radio-streams && \
    apk del --no-cache curl && \
    apk del --no-cache curl-dev && \
    cd /opt/radio-streams/radio-streams-master && \
        python3 -mpip wheel --verbose --progress-bar off --disable-pip-version-check --no-build-isolation --no-deps --wheel-dir ./build . && \
        python3 -mpip install --verbose --progress-bar off --disable-pip-version-check --break-system-packages --no-compile --ignore-installed --no-deps --no-index --find-links ./build radiostreams && \
    cd && \
    pip3 uninstall --yes --break-system-packages wheel

#
# Copy bootstrap.sh to /opt
#
COPY bootstrap.sh /opt
COPY streams.json /opt/radio-streams/streams.json

#
# Start bootstrap on Container start
#
RUN chmod +x /opt/bootstrap.sh

#
# Second stage
#
FROM scratch

#
# Variables
# RS_VERSION version of radio-streams software
# RS_STREAMS path an name of the indiviudual streams.json e.g. /radio-streams/streams.json
# RS_DEBUG turn ON or OFF debug output of radio-streams proxy else only start /bin/sh
# RS_PORT port radio-stations server listens to, e.g. 8080
#
ENV RS_VERSION master
ENV RS_STREAMS /opt/radio-streams/streams.json
ENV RS_DEBUG OFF
ENV RS_PORT 8080

COPY --from=build / /

#
# Set Workdirectory on radio-streams folder
#
WORKDIR /opt/radio-stations/radio-streams-${RS_VERSION}

#
# Docker Container should be listening for AVR on port 8080
#
EXPOSE ${RS_PORT}/tcp

ENTRYPOINT ["/opt/bootstrap.sh"]
