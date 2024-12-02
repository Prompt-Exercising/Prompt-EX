FROM ubuntu:latest
LABEL authors="baggiung"

ENTRYPOINT ["top", "-b"]