FROM ubuntu:focal
WORKDIR /financial_news
RUN apt-get update && DEBIAN_FRONTEND=noninteractive apt-get install -y software-properties-common gpg wget git sudo python3-pip python3-venv python3-dev python3-wheel &&\
    add-apt-repository ppa:criu/ppa && apt-get update && apt-get -y install criu && mkdir -p /output &&\
    python3 -m venv venv && . venv/bin/activate && pip install wheel &&\
    pip install tensorflow scipy pandas matplotlib scikit-learn statsmodels &&\
    git clone https://bitbucket.org/depauldbgroup/storagevscompute -b optimal chex &&\
    pip install -r chex/requirements.txt &&\
    git clone https://github.com/AI4Finance-LLC/Financial-News-for-Stock-Prediction-using-DP-LSTM-NIPS-2019 financial_news &&\
    cd financial_news/code/ && python /financial_news/chex/src/nbmaker.py /financial_news/chex/data/financial_news.bin generate_notebooks
CMD . venv/bin/activate && cd financial_news/code/ && exec python /financial_news/chex/src/run_notebooks.py generate_notebooks /output/tree.bin
