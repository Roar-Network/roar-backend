FROM python:3.8.10-alpine

ADD . ./home
ADD ./requirements.txt ./home

RUN pip install -r ./home/requirements.txt 

EXPOSE 8002

CMD ["sh"]

