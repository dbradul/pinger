FROM python:3.8

RUN apt update

RUN mkdir /srv/project
WORKDIR /srv/project

COPY ./src ./src
COPY ./Pipfile ./Pipfile
COPY ./Pipfile.lock ./Pipfile.lock

RUN python -m pip install --upgrade pip
RUN python -m pip install pipenv
RUN pipenv install --system --deploy --ignore-pipfile

CMD ["bash"]