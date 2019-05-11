FROM ubuntu:18.04

RUN apt-get update

COPY . MoaLink/

RUN apt install python3-pip
RUN pip3 install numpy
RUN apt-get install default-jdk

CMD ["python3", "MoaLink/gen_moa_baselines.py", "-d", "datastreams", "-m", "MoaLink/moa/lib/"]