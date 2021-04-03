FROM python:3.8
ENV PYTHONUNBUFFERED=1


WORKDIR /code
COPY requirements.txt /code/
RUN pip install -r requirements.txt
RUN pip install gunicorn

COPY . /code/

RUN python3 manage.py collectstatic --no-input
EXPOSE 8000
CMD ["gunicorn", "forge.wsgi:application", "--bind", "0.0.0.0:8000", "--workers"," 3"]
