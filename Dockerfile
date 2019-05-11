FROM ubuntu:18.04

RUN apt-get update

COPY . MoaLink/

RUN apt-get install -y python3-pip
RUN pip3 install numpy
RUN apt-get install -y default-jdk

CMD ["python3", "MoaLink/gen_moa_baselines.py", "-d", "datastreams", "-m", "MoaLink/moa/lib/"]