FROM alpine:3.16

ENV USER root
ENV HOME /root

ARG NGROK_AUTHTOKEN
ENV NGROK_AUTHTOKEN $NGROK_AUTHTOKEN

RUN set -ex \
  && apk add --update libintl \
  && apk add --no-cache --virtual .build-deps wget gettext \
  && apk add --no-cache ca-certificates \
  && cp /usr/bin/envsubst /usr/local/bin/envsubst \
  \
  && cd /tmp \
  && wget https://bin.equinox.io/c/4VmDzA7iaHb/ngrok-stable-linux-amd64.zip --no-check-certificate \
  && unzip ngrok-stable-linux-amd64.zip \
  && install -v -D ngrok /bin/ngrok \
  && rm -f ngrok-stable-linux-amd64.zip ngrok \
  \
  && apk del .build-deps

ADD ngrok.template $HOME/ngrok.template
RUN envsubst < $HOME/ngrok.template > $HOME/ngrok.yml
RUN rm $HOME/ngrok.template


EXPOSE 4040

#ENTRYPOINT ["/bin/ngrok_discover"]
CMD ["bash"]
