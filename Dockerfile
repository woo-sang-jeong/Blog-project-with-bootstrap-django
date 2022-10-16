# pull official base image
# 도커는 파이썬이 설치된 이미지를 기본으로 제공한다. 아래의 코드는 파이썬을 불러오는 코드다.
FROM python:3.8.0-alpine

# set work directory
# 프로젝트 폴더를 지정하는 코드다.
WORKDIR /usr/src/app

# set environment variables
# 파이썬은 컴파일하면 .pyc라는 확장자가 붙은 파일을 생성한다. 도커에서는 쓰이지 않으므로 .pyc 파일을 생성하지 않도록 한다.
# 파이썬 로그가 버퍼렁 없이 바로 출력하도록 한다.
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# requirements.txt에 적혀있는 라이브러리를 설치하기 위한 gcc,musl-dev를 미리 설치하는 코드다.
RUN apk update
RUN apk add postgresql-dev gcc python3-dev musl-dev zlib-dev jpeg-dev

# docker compose build시 cffi 설치 오류가 뜨는 경우 해결 코드
RUN apk add libffi-dev

# Dockerfile이 있는 위치에 있는 파일을 모두 작업 폴더인 WORKDIR로 복사한다. 이는 도커 이미지를 담기 위함이다.
# 중간의 . 은 현재 폴더를 의미한다.
COPY . /usr/src/app

# install dependencies
# requirements.txt에 기술된 라이브러리를 설치한다.
RUN pip install --upgrade pip
RUN pip install -r requirements.txt


