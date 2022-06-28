FROM roar/system

WORKDIR /roar-backend

ADD . ./


EXPOSE 32020
EXPOSE 8002

CMD ["bash"]

