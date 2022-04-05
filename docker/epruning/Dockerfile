FROM ubuntu:focal
WORKDIR /chex
RUN apt-get update && DEBIAN_FRONTEND=noninteractive apt-get install -y software-properties-common gpg wget git sudo python3-pip python3-venv python3-dev python3-wheel build-essential cmake unzip &&\
    add-apt-repository ppa:criu/ppa && apt-get update && apt-get -y install criu &&\
    python3 -m venv venv && . venv/bin/activate && pip install wheel && pip install git+https://github.com/depaul-dice/sciunit@chex &&\
    git clone https://github.com/depaul-dice/CHEX chex &&\
    pip install -r chex/requirements.txt &&\
    wget -q https://dice.cs.depaul.edu/chex/datasets/epruning.zip && unzip epruning.zip -d repo/ &&\
    pip install numpy scipy torch torchvision torchaudio torchsummary tensorflow &&\
    cd repo/epruning/epruning && python /chex/chex/src/replay/nbmaker.py /chex/chex/data/epruning.bin notebooks && ln -s /chex/chex notebooks/chex
CMD . venv/bin/activate && cd repo/epruning/epruning/notebooks && exec bash
