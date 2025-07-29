FROM python:3.13

WORKDIR /app

COPY ./.docker/fastapi/requirements.txt /app/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /app/requirements.txt

COPY ./fastapi /app

CMD ["fastapi", "run", "main.py", "--port", "8000"]
