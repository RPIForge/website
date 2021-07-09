FROM python:3.8
ENV PYTHONUNBUFFERED=1


COPY start.sh /code/start.sh
RUN chmod +x /code/start.sh


WORKDIR /code
COPY requirements.txt /code/
RUN pip install -r requirements.txt
RUN pip install gunicorn

COPY . /code/

RUN python3 manage.py collectstatic --no-input
EXPOSE 8000
CMD ["/bin/bash", "/code/start.sh"]
