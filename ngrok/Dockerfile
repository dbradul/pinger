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
  && wget https://bin.equinox.io/c/bNyj1mQVY4c/ngrok-v3-stable-linux-amd64.tgz --no-check-certificate \
  && tar xvzf ngrok-v3-stable-linux-amd64.tgz -C /usr/local/bin \
  && tar xvzf ngrok-v3-stable-linux-amd64.tgz -C /bin \
  && rm -f ngrok-stable-linux-amd64.zip \
  \
  && apk del .build-deps

ADD ngrok.template $HOME/ngrok.template
RUN mkdir -p $HOME/.config/ngrok
RUN envsubst < $HOME/ngrok.template > $HOME/.config/ngrok/ngrok.yml
RUN rm $HOME/ngrok.template


EXPOSE 4040

#ENTRYPOINT ["/bin/ngrok_discover"]
CMD ["bash"]
