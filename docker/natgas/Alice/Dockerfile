FROM ubuntu:focal
WORKDIR /natgas
RUN apt-get update && DEBIAN_FRONTEND=noninteractive apt-get install -y software-properties-common gpg wget git sudo python3-pip python3-venv python3-dev python3-wheel &&\
    add-apt-repository ppa:criu/ppa && apt-get update && apt-get -y install criu && mkdir -p /output &&\
    python3 -m venv venv && . venv/bin/activate && pip install wheel &&\
    pip install numpy==1.19.2 pandas==0.25.3 matplotlib xlrd==1.2.0 openpyxl &&\
    git clone https://bitbucket.org/depauldbgroup/storagevscompute -b optimal chex &&\
    pip install -r chex/requirements.txt &&\
    git clone https://github.com/bahuisman/NatGasModel natgas &&\
    cd natgas/ && python /natgas/chex/src/nbmaker.py /natgas/chex/data/natgas.bin generate_notebooks &&\
    cp *.xlsx generate_notebooks
CMD . venv/bin/activate && cd natgas/ && exec python /natgas/chex/src/run_notebooks.py generate_notebooks /output/tree.bin
