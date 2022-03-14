FROM python:3.8-slim-buster
RUN apt-get update -y
RUN apt-get install python3-pip -y

RUN mkdir /app
WORKDIR /app
#ADD requirements.txt /app
COPY requirements.txt requirements.txt
ADD app.py /app
RUN pip3 install -r requirements.txt

#COPY flaskapp /opt/

RUN pip3 install -r requirements.txt

COPY . .

CMD [ "python3", "-m" , "flask", "run", "--host=0.0.0.0"]