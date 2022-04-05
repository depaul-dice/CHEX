FROM ubuntu:focal
WORKDIR /chex
RUN apt-get update && DEBIAN_FRONTEND=noninteractive apt-get install -y software-properties-common gpg wget git sudo python3-pip python3-venv python3-dev python3-wheel build-essential cmake &&\
    add-apt-repository ppa:criu/ppa && apt-get update && apt-get -y install criu &&\
    python3 -m venv venv && . venv/bin/activate && pip install wheel && pip install git+https://github.com/depaul-dice/sciunit@chex &&\
    git clone https://github.com/depaul-dice/CHEX chex &&\
    pip install -r chex/requirements.txt &&\
    git clone https://github.com/JEddy92/TimeSeries_Seq2Seq repo &&\
    pip install tensorflow scipy numpy seaborn pandas matplotlib keras &&\
    cd repo/notebooks/ && python /chex/chex/src/replay/nbmaker.py /chex/chex/data/timeseries.bin notebooks && ln -s /chex/chex notebooks/chex &&\
    ln -s ../data data && cd .. && mkdir data && cd data && wget -q https://dice.cs.depaul.edu/chex/datasets/timeseries/train_1.csv
CMD . venv/bin/activate && cd repo/notebooks/notebooks && exec bash
