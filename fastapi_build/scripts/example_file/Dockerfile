FROM python:3.9.5
MAINTAINER hello

ENV TZ=Asia/Shanghai
ENV LANG=en_US.UTF-8

RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ >/etc/timezone
# 更改源为阿里云镜像源并更新软件包列表
RUN sed -i 's|http://deb.debian.org/debian|http://mirrors.aliyun.com/debian|g' /etc/apt/sources.list && \
    sed -i 's|http://security.debian.org/debian-security|http://mirrors.aliyun.com/debian-security|g' /etc/apt/sources.list && \
    apt-get update


WORKDIR /project

ADD requirements.txt /project
COPY requirements.txt .
RUN pip install -r requirements.txt -i https://mirrors.aliyun.com/pypi/simple/ --trusted-host mirrors.aliyun.com

COPY ./src /project/

EXPOSE 9999

CMD ["bash"]



