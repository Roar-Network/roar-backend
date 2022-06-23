FROM python:3.10

ADD . ./home
ADD ./requirements.txt ./home

RUN python -m pip install --upgrade pip
RUN pip install -r ./home/requirements.txt

EXPOSE 32020
EXPOSE 8002

CMD ["sh"]

