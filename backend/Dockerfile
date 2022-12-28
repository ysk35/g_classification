FROM python:3.9-slim-buster

ENV PYTHONBURRERED=1

WORKDIR /usr/src/app

COPY requirements.txt .

# RUN apk add --no-cache build-base \
#  && apk del build-base \
RUN apt-get update && apt-get upgrade -y
RUN apt-get install -y libgl1-mesa-dev
RUN apt-get install -y libopencv-dev
RUN apt-get install sqlite3
RUN pip install --upgrade pip \
 && pip install --no-cache-dir --trusted-host pypi.python.org -r requirements.txt \
 && pip install python-multipart

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--reload", "--host", "0.0.0.0", "--port", "8000"]