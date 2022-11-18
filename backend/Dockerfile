FROM python:3.10.6-alpine

ENV PYTHONBURRERED=1

WORKDIR /usr/src/app

COPY requirements.txt .

RUN apk add --no-cache build-base \
 && pip install --no-cache-dir --trusted-host pypi.python.org -r requirements.txt \
 && apk del build-base

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--reload", "--host", "0.0.0.0", "--port", "8000"]