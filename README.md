# Getting started

In collaborative scenarios, sharing and reproducig results is often necessary. 
When multiple versions of an application are containerized, it is often necessary to perform multiversion replay 

**CHEX** provides the ability to perform efficient multiversion replay. 

The following shows how **CHEX** works. 

![**CHEX Overview**](/img/CHEX-2.png)


Alice uses **CHEX** in audit mode to execute each version. **CHEX** audits details of her executions. It then represents the details of her executions in the form of a data structure called the *Execution Tree*. The execution tree contains information about the computation cost and average checkpoint size of each cell in each version of Alice's multiversion program. It also contains information about which cells can be identified with each other across versions. This information is encapsulated as a tree structure.

Bob uses **CHEX** in replay mode. **CHEX** first determines an efficient *replay sequence* or replay order for him, i.e., a plan for execution that includes checkpoint caching decisions. To do so **CHEX** asks Bob to provide a cache size bound, B, and then executes a heuristic algorithm on the execution tree received from Alice to determine the most cost efficient replay sequence for that cache size. We describe some efficient heuristics for this purpose. Finally, once the replay sequence is computed, **CHEX** uses this replay sequence to *compute, checkpoint, restore-switch* REPL program cells or *evict* stored checkpoints from cache.


This repository  has three directories: data, src, and dockerfiles.

* Sample execution trees of all notebooks used in the paper are found under `data`. 
* CHEX src code for Alice and Bob reside under `src`.
* Sample Alice/Bob scenarios can be constructed using provided dockerfiles under `dockerfile`.
    

# INSTALL requirements

* Python and OS
    - Python (Version >= 3.8)
    - pip install -r requirements.txt
    - **CHEX** was developed on Ubuntu 20.04

* The repository uses CRIU. 
    - Install from https://criu.org/Installation

* Optimal algorithm uses Couenne.
    - Download and install from: https://projects.coin-or.org/Couenne

---
# Evaluating this artifact

## How to repeat our results? 

### A. Sample Alice/Bob scenarios 

Two sample notebook examples are provided under the directory dockerfiles. 
For these notebooks, we have created corresponding dockerfiles. 
The dockerfile for Alice downloads the specific GitHub repository, creates notebook versions, and generates execution trees using the code from this repository.

The dockerfile for Bob recreates the same notebook environment and allows the user to replay the notebooks using algorithms provided from this repo. 

To install and run these dockerfiles

1. Install Docker from http://docker.com
2. Clone this repo:
3. Build dockerfile as:
4. To run as Alice: 
5. To run as Bob:

### B. Regenerate the figures in the paper:

1. Follow install instructions under INSTALL
2. Run ```python plot.py```


## How to reproduce CHEX using your own notebooks?

### A. Generate Execution trees:
 
 1. Run ```python run_notebooks.py```

This command should be run from the same folder in which the notebook versions are present and were executed. 
Note, the command currently does not produce a container-based execution tree. Code for that is still under works over here: 
https://bitbucket.org/depauldbgroup/provenance-to-use/src/notebook

### B. Generate the replay sequence

 1. Run ```python replay-order.py --algo pc|prp-v1|prp-v2 --size <B> --tree <sample.bin>```

sample.bin must be under data directory. 
output of this command is replay-order.bin

### C. For replaying 

 1. Run ```python replay.py --RO replay-order.bin```

---
This material is based upon work supported by the National Science Foundation under Grants CNS-1846418, ICER-1639759, ICER-1661918, and a DoE BSSw Fellowship. Any opinions, findings, and conclusions or recommendations expressed in this material are those of the author(s) and do not necessarily reflect the views of the National Science Foundation.
