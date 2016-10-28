FROM frolvlad/alpine-python3
MAINTAINER Nolan Essigmann
LABEL version="0.1"

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY app.py app.py
COPY urlshortener.py urlshortener.py
COPY ratelimiter.py ratelimiter.py
ADD index.html /
COPY public/ /public/

# RUN python3 

ENTRYPOINT ["python3", "app.py"]
