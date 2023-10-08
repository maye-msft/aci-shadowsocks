FROM python:3.7-alpine

RUN set -ex \
	&& apk add --no-cache unzip libsodium-dev openssl mbedtls \
	&& cd /tmp \
	&& wget -O shadowsocks.zip https://github.com/shadowsocks/shadowsocks/archive/master.zip \
	&& unzip shadowsocks.zip \
	&& cd shadowsocks-master \
	&& python setup.py install \
	&& cd /tmp \
	&& rm -fr shadowsocks.zip shadowsocks-master 

COPY ss_config.json /etc/shadowsocks-python/config.json
VOLUME /etc/shadowsocks-python

CMD [ "ssserver", "-c", "/etc/shadowsocks-python/config.json" ]