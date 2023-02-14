FROM --platform=arm64 golang:alpine

COPY app/ /home/
WORKDIR /home/

CMD ["go", "run", "main.go"]