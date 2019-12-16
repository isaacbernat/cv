FROM python:3.6.3-alpine3.6

# set working directory
RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app

RUN apk update && \
   apk add --virtual build-deps gcc python3-dev musl-dev && \
   apk add postgresql-dev

# add requirements (to leverage Docker cache)
ADD ./requirements.txt /usr/src/app/requirements.txt

# install requirements
RUN pip install -r requirements.txt

# add app
ADD . /usr/src/app

# run server
CMD python manage.py runserver -h 0.0.0.0
