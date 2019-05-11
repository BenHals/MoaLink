FROM ubuntu:18.04

RUN apt-get update && apt-get install -y \
	python3-pip \
	default-jdk
	
RUN pip3 install numpy

COPY . MoaLink/

ENTRYPOINT ["python3", "MoaLink/gen_moa_baselines.py", "-l"]
CMD ["-d", "datastreams", "-m", "MoaLink/moa/lib/"]