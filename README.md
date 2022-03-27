# Getting started

In collaborative scenarios, sharing and reproducing results is often necessary. 
When multiple versions of an application are containerized, it is often necessary to perform multiversion replay 

**CHEX** provides the ability to perform efficient multiversion replay. 

The following shows how **CHEX** works. 

![**CHEX Overview**](/img/CHEX-2.png)


Alice uses **CHEX** in audit mode to execute each version. **CHEX** audits details of her executions. It then represents the details of her executions in the form of a data structure called the *Execution Tree*. The execution tree contains information about the computation cost and average checkpoint size of each cell in each version of Alice's multiversion program. It also contains information about which cells can be identified with each other across versions. This information is encapsulated as a tree structure.

Bob uses **CHEX** in replay mode. **CHEX** first determines an efficient *replay sequence* or replay order for him, i.e., a plan for execution that includes checkpoint caching decisions. To do so **CHEX** asks Bob to provide a cache size bound, B, and then executes a heuristic algorithm on the execution tree received from Alice to determine the most cost efficient replay sequence for that cache size. We describe some efficient heuristics for this purpose. Finally, once the replay sequence is computed, **CHEX** uses this replay sequence to *compute, checkpoint, restore-switch* REPL program cells or *evict* stored checkpoints from cache.

The **Chex** paper: 
Naga Nithin Manne, Shilvi Satpati, Tanu Malik, Amitabha Bagchi, Ashish
Gehani, and Amitabh Chaudhary. CHEX: Multiversion Replay with
Ordered Checkpoints. PVLDB, 15(6): 1297-1310, 2022
doi:10.14778/3514061.3514075

This repository  has three directories: data, src, and dockerfiles.

* Sample execution trees of all notebooks used in the paper are found under `data`. 
* CHEX src code for Alice and Bob reside under `src`.
* Sample Alice/Bob scenarios can be constructed using provided dockerfiles under `docker`.
    

# INSTALL requirements

* OS
   - Ubuntu 20.04
   
* Python
    - Python (Version >= 3.8)
    - ```pip install -r requirements.txt```

* CRIU. 
    - Install from https://criu.org/Installation

* Optimal algorithm uses Couenne.
    - Download and install from: https://projects.coin-or.org/Couenne
    - Update: Not needed for set of results reported in PVLDB paper. 
   
* Clone this repo.
    - ```git clone https://github.com/depaul-dice/CHEX```
   
---
# Evaluating this artifact

## Repeating the results reported in the paper

1. Run ```python src\replay\plot.py```

## Reproducing new results with same notebooks 

1. Install Docker from https://docs.docker.com/get-docker/ 

There are _5_ notebooks provided. For each notebook do steps 2-5. 

2. Build a notebook Dockerfile as:
   ```docker build -t <tagname> .```
     This dockerfile should consist of notebooks, their dependecies, and Sciunit.

3. _Some instructions to enter the Docker container_ 
    
4. Run Sciunit to audit and replay with the provided notebooks.  
    
* Create a Sciunit Project
    - ```sciunit create <Project Name>```
    - For ML1 run as:
     ```sciunit create ML1```

* Convert Notebooks to Python Files
    - ```sciunit convert <file.ipynb>```
    - For ML1, v1 this is same as
    ```sciunit convert ML11.ipynb```

* Execute Each Python file **one-by-one**. 
    - ```sciunit exec python <file.py>```
    Each time, Sciunit creates a new execution `e<i>`
    - For ML1, v1 this is same as
    ```sciunit exec python ML11.py```

The above step refers to CHEX Audit in the figure and regenerates the execution trees. 

* List all executions as 
    ```sciunit list```

5. To regenerate the figures, export the execution tree as: 
    
    - _Give a command to export the tree and place the tree under the data directory._
    - Run ```python src\replay\plot.py```

6. To perform multiversion replay use the mve sub-command. This is CHEX Replay in the above figure. 
   - ```sciunit mve e<i>-<j> <Cache Size>```
   - Cache size is a parameter that specifies the size of the cache. Possible options are _1GB_
    

# OLD DOCUMENTATION
    

## The complete CHEX system is now also available as part of [Sciunit framework](https://sciunit.run/)

# Installation

* Dependencies
    - Python (Version >= 3.8)
    - CMake
    - CRIU (https://criu.org/Installation)

* Install from experimental `chex` branch in [Sciunit](https://bitbucket.org/geotrust/sciunit2/src/chex/)
    - Create a new virtual environment
    - ```pip install git+https://bitbucket.org/geotrust/sciunit2@chex```

# Usage

* Create a Sciunit Project
    - ```sciunit create <Project Name>```

* Convert Notebooks to Python Files
    - ```sciunit convert <.ipynb>```

* Execute Each Python file one-by-one - CHEX Audit
    - ```sciunit exec python <.py>```
    - Each time, Sciunit creates a new execution `e<i>`

* Multi version replay the required executions - CHEX Replay
    - ```sciunit mve e<i>-<j> <Cache Size>```

# Old README

## How to repeat our results? 

### A. Sample Alice/Bob scenarios 

Two sample notebook examples are provided under the directory docker. 
For these notebooks, we have created corresponding dockerfiles. 
The dockerfile for Alice downloads the specific GitHub repository, creates notebook versions, and generates execution trees using the code from this repository.

The dockerfile for Bob recreates the same notebook environment and allows the user to replay the notebooks using algorithms provided from this repo. 

To install and run these dockerfiles

1. Install Docker from https://docs.docker.com/get-docker/
2. Clone this repo.
3. Build Dockerfile as:
   ```docker build -t <tagname> .```
4. To run as Alice:
   ```docker run -v <Output Folder>:/output --privileged --cap-add all -it <tagname>```
5. To run as Bob:
  ```docker run --privileged --cap-add all -it <tagname>```

`/output` in container has the output tree

### B. Regenerate the figures in the paper:

1. Follow install instructions under INSTALL
2. Run ```python src\replay\plot.py```


## How to reproduce CHEX using your own notebooks?

### A. Generate Execution trees:
 
 1. Run ```python run_notebooks.py <Notebooks Path> <Output Tree>```

This command should be run from the same folder in which the notebook versions are present and were executed. 
Note, the command currently does not produce a container-based execution tree. Code for that is still under works over here: 
https://bitbucket.org/depauldbgroup/provenance-to-use/src/notebook

### B. Generate the replay sequence

 1. Run ```python replay-order.py pc|prpv1|prpv2|lfu <cache_size> <input tree.bin> <output replay-order.bin>```

sample.bin must be under data directory. 
output of this command is replay-order.bin

### C. For replaying 

 1. Run ```python replay.py replay-order.bin```

---
This material is based upon work supported by the National Science Foundation under Grants CNS-1846418, ICER-1639759, ICER-1661918, and a DoE BSSw Fellowship. Any opinions, findings, and conclusions or recommendations expressed in this material are those of the author(s) and do not necessarily reflect the views of the National Science Foundation.
