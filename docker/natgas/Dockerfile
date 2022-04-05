FROM ubuntu:focal
WORKDIR /chex
RUN apt-get update && DEBIAN_FRONTEND=noninteractive apt-get install -y software-properties-common gpg wget git sudo python3-pip python3-venv python3-dev python3-wheel build-essential cmake &&\
    add-apt-repository ppa:criu/ppa && apt-get update && apt-get -y install criu &&\
    python3 -m venv venv && . venv/bin/activate && pip install wheel && pip install git+https://github.com/depaul-dice/sciunit@chex &&\
    git clone https://github.com/depaul-dice/CHEX chex &&\
    pip install -r chex/requirements.txt &&\
    git clone https://github.com/bahuisman/NatGasModel repo &&\
    pip install numpy==1.19.2 pandas==0.25.3 matplotlib xlrd==1.2.0 openpyxl &&\
    cd repo/ && python /chex/chex/src/replay/nbmaker.py /chex/chex/data/natgas.bin notebooks && ln -s /chex/chex notebooks/chex &&\
    cp *.xlsx notebooks
CMD . venv/bin/activate && cd repo/notebooks && exec bash
