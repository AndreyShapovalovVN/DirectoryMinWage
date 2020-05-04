FROM tiangolo/meinheld-gunicorn:python3.7-alpine3.8

RUN apk add --update git
RUN apk add --update libxml2-dev
RUN apk add --update libxslt-dev
RUN apk add --update build-base

RUN pip install --upgrade pip
RUN pip install gunicorn
RUN pip install Flask
RUN pip install lxml
RUN pip install git+https://github.com/arskom/spyne.git

COPY ./app /app

ENV userId="0123456789"
ENV token="bb96c2fc40d2d54617d6f276febe571f623a8dadf0b734855299b0e107fda32cf6b69f2da32b36445d73690b93cbd0f7bfc20e0f7f28553d2a4428f23b716e90"
