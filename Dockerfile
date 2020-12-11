FROM debian:stretch

RUN apt-get -y update && apt-get install -y \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

RUN useradd -ms /bin/bash app

USER app

WORKDIR /home/app

RUN pip3 install pysummarize pysummarization

RUN python3 -c 'import nltk; nltk.download(["stopwords", "punkt"])'

COPY src /home/app/src

CMD ["python3", "/home/app/src/serve.py"]