# Python version matches the Pipfile ("3.12")
FROM python:3.12-slim

WORKDIR /app

# system libraries that OpenCV and mediapipe need (not included in the slim image)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgl1 libegl1 libgles2 libglib2.0-0t64 libsm6 libice6 \
    libx11-6 libxext6 libxcb1 \
    && rm -rf /var/lib/apt/lists/*

# install dependencies first so Docker can cache this layer
COPY requirements.txt ./
RUN pip3 install -r requirements.txt

# then copy the rest of the ML client code
ADD . .

# ML client port the web app calls
EXPOSE 8000

CMD [ "python3", "-m", "ml_client.app" ]