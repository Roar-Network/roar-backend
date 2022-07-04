FROM roar/server

# COPY ./nltk_data ../root/nltk_data
WORKDIR /roar-backend

ADD . ./


EXPOSE 32020
EXPOSE 8002

CMD ["bash"]

