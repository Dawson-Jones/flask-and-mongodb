FROM python:3.8
WORKDIR /usr/src/app
MAINTAINER Dobby <jeedq@qq.com>
COPY requirements.txt ./
RUN pip3 install -r requirements.txt -i https://mirrors.aliyun.com/pypi/simple
#EXPOSE 5000
#ENTRYPOINT ["python"]
#CMD gunicorn -w 4 -b 0.0.0.0:5000 -D --access-logfile ./log manager:app
