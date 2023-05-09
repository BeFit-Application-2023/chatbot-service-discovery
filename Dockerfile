# syntax=docker/dockerfile:1

#FROM pytorch/pytorch
FROM tiangolo/uwsgi-nginx-flask:python3.7

WORKDIR /service-discovery
COPY ./requirements.txt requirements.txt
RUN pip install -r requirements.txt
COPY . .

EXPOSE 9999

ENV FLASK_APP=main.py

CMD ["python","-u","main.py"]