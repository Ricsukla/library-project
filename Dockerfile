FROM python:3.10

WORKDIR /app
COPY . /app
RUN pip install -r requirements.txt

# 👇 CHANGE THIS LINE
CMD gunicorn --bind 0.0.0.0:$PORT app:app
