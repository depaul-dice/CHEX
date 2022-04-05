FROM ubuntu:focal
WORKDIR /chex
RUN apt-get update && DEBIAN_FRONTEND=noninteractive apt-get install -y software-properties-common gpg wget git sudo python3-pip python3-venv python3-dev python3-wheel build-essential cmake &&\
    add-apt-repository ppa:criu/ppa && apt-get update && apt-get -y install criu &&\
    python3 -m venv venv && . venv/bin/activate && pip install wheel && pip install git+https://github.com/depaul-dice/sciunit@chex &&\
    git clone https://github.com/depaul-dice/CHEX chex &&\
    pip install -r chex/requirements.txt &&\
    git clone https://github.com/AI4Finance-LLC/Financial-News-for-Stock-Prediction-using-DP-LSTM-NIPS-2019 repo &&\
    pip install tensorflow scipy pandas matplotlib scikit-learn statsmodels &&\
    cd repo/code/ && python /chex/chex/src/replay/nbmaker.py /chex/chex/data/financial_news.bin notebooks && ln -s /chex/chex notebooks/chex
CMD . venv/bin/activate && cd repo/code/notebooks && exec bash
