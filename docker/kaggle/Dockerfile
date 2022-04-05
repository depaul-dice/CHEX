FROM ubuntu:focal
WORKDIR /chex
RUN apt-get update && DEBIAN_FRONTEND=noninteractive apt-get install -y software-properties-common gpg wget git sudo python3-pip python3-venv python3-dev python3-wheel build-essential cmake &&\
    add-apt-repository ppa:criu/ppa && apt-get update && apt-get -y install criu &&\
    python3 -m venv venv && . venv/bin/activate && pip install wheel && pip install git+https://github.com/depaul-dice/sciunit@chex &&\
    git clone https://github.com/depaul-dice/CHEX chex &&\
    pip install -r chex/requirements.txt &&\
    mkdir repo &&\
    pip install numpy torch torchvision torchaudio Pillow sklearn &&\
    cd repo/ && python /chex/chex/src/replay/nbmaker.py /chex/chex/data/kaggle.bin notebooks && ln -s /chex/chex notebooks/chex &&\
    wget -q https://dice.cs.depaul.edu/chex/datasets/kaggle/fashionmnist_train.npy && wget -q https://dice.cs.depaul.edu/chex/datasets/kaggle/fashionmnist_test.npy
CMD . venv/bin/activate && cd repo/notebooks && exec bash
