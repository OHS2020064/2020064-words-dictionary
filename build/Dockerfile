# 基础镜像
FROM python:3.7.0 AS builder

# 添加依赖
ADD 2020064-scrapy-spider/requirements.txt opt/requirements.txt

# 设置工作目录
WORKDIR opt

# 安装支持
#-i https://pypi.tuna.tsinghua.edu.cn/simple
RUN pip install -i https://pypi.tuna.tsinghua.edu.cn/simple -r requirements.txt

RUN apt-get update
RUN apt-get -y install vim

# 代码添加到镜像
ADD 2020064-scrapy-spider 2020064-scrapy-spider

# 设置工作目录
WORKDIR 2020064-scrapy-spider

# 打包
RUN pyinstaller main.spec

# 镜像
RUN cp /opt/2020064-scrapy-spider/dist/main /opt

# 基础镜像
FROM ubuntu AS executable

# 添加defaultconfigs
ADD 2020064-scrapy-spider/scrapy_idx/configs opt/2020064-scrapy-spider/scrapy_idx/configs
ADD 2020064-scrapy-spider/scrapy_idx/text_analysis opt/2020064-scrapy-spider/scrapy_idx/text_analysis

COPY --from=builder /opt/main /opt/2020064-scrapy-spider/main

ENV SCRAPY_SETTINGS_MODULE=scrapy_idx.configs.scrapy_configs

# 设置工作目录
WORKDIR opt/2020064-scrapy-spider

# 执行
#RUN ./main