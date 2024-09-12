FROM golang:1.22.6
WORKDIR /src
ENV CGO_ENABLED=1
RUN go env -w GOCACHE=/go-cache
RUN go env -w GOMODCACHE=/gomod-cache
COPY lostpass-ee.go /src/lostpass-ee.go

RUN --mount=type=cache,target=/gomod-cache --mount=type=cache,target=/go-cache  go build -o /src/lostpass-ee ./lostpass-ee.go

FROM ubuntu:24.04

RUN apt update && apt install -y sass

RUN mkdir -p /app/lostpass-ee/data
RUN chmod 777 /app/lostpass-ee/data
RUN chmod +t /app/lostpass-ee/data
RUN ln -s /data-ro/government /app/lostpass-ee/data/government

COPY --from=0 /src/lostpass-ee /app/lostpass-ee/
ADD --chown=nobody ./ /app/lostpass-ee/
WORKDIR /app/lostpass-ee/
USER nobody
RUN ./build_assets.sh
CMD ["/app/lostpass-ee/lostpass-ee"]
