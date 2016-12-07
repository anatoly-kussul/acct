FROM python:3.5
ENV TZ=Europe/Kiev
RUN mkdir app
RUN adduser bob
#---------------------Postgres--------------
WORKDIR /
RUN apt-get update
RUN apt-get install -y postgresql
#-------------------- Python requirements----
WORKDIR /
ADD eblank/requirements.txt /requirements.txt
RUN pip install -r requirements.txt
RUN rm requirements.txt
WORKDIR app/