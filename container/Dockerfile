FROM ubuntu:20.04

ENV TZ=Asia/Kolkata \
    DEBIAN_FRONTEND=noninteractive

WORKDIR /app

# Install dependencies
RUN apt-get update
RUN apt-get -y install -y python3
RUN apt-get -y install net-tools
RUN apt-get -y install sudo
RUN apt-get install -y python3-pip
RUN sudo apt-get install -y can-utils
RUN sudo apt-get install -y iproute2
COPY requirements.txt /app/

RUN pip install -r requirements.txt

COPY . /app/

RUN chmod +x /app/startup.sh

CMD ["/app/startup.sh"]