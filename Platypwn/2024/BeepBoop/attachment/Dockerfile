# Golang 1.23.3
FROM golang@sha256:e5ca1999e21764b1fd40cf6564ebfb7022e7a55b8c72886a9bcb697a5feac8d6 AS builder

WORKDIR /src
COPY src/ .

RUN make

FROM debian:latest

RUN apt update && apt install -y socat lighttpd

# Copy files to serve them via lighttpd for download.
# We don't use static files here because we want to deliver the same binary that's
# running in the container.
WORKDIR /app
COPY Dockerfile entrypoint.sh lighttpd.conf .
COPY --from=builder /src ./src

COPY lighttpd.conf /etc/lighttpd/lighttpd.conf

COPY entrypoint.sh /

ENTRYPOINT ["/entrypoint.sh"]
CMD ["socat", "TCP-LISTEN:1337,fork,reuseaddr", "EXEC:'/app/src/beepboop'"]
