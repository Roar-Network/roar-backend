FROM python:3.8.10-alpine

ADD . ./home
ADD ./requirements.txt ./home

RUN --mount=type=cache,target=/root/.cache \
    pip install -r ./home/requirements.txt

EXPOSE 8001

RUN cd ./home/src/objects
CMD ["sh"]

