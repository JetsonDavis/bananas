FROM python:3
LABEL maintainer "jd <jd@mac.com>"

WORKDIR /usr/src/app

COPY /requirements.txt ./

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5000

CMD ["python","./bananas.py"]