FROM python:3.8.5-alpine3.12
WORKDIR /usr/app
ENV FLASK_APP=app.py
COPY requirements.txt ./
RUN pip install -r requirements.txt
COPY . .
EXPOSE 5000
CMD ["flask", "run", "--host=0.0.0.0"]