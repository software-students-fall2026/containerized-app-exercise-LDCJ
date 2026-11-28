# Python version matches the Pipfile ("3.12")
FROM python:3.12-slim

WORKDIR /app

# install dependencies first so Docker can cache this layer
COPY requirements.txt ./
RUN pip3 install -r requirements.txt

# then copy the rest of the ML client code
ADD . .

# ML client port the web app calls
EXPOSE 8000

CMD [ "python3", "-m", "ml_client.app" ]
