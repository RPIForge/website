FROM python:3.8-alpine
WORKDIR /code

#set up env
ENV PYTHONUNBUFFERED=1

RUN apk update \
    && apk add postgresql-dev gcc python3-dev musl-dev libffi-dev


COPY requirements.txt /code/
RUN pip install -r requirements.txt

COPY . /code/

CMD ["gunicorn", "forge.wsgi:application","--bind","0.0.0.0:8000","--workers","3"]
