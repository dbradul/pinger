FROM python:3.9

RUN apt update
RUN apt install iputils-ping -y

RUN mkdir /app
WORKDIR /app

COPY ./src ./src
COPY ./Pipfile ./Pipfile
COPY ./Pipfile.lock ./Pipfile.lock

RUN python -m pip install --upgrade pip
RUN python -m pip install pipenv
RUN pipenv install --system --deploy --ignore-pipfile

CMD ["bash"]