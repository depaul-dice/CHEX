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

* Clone this repo.
    - ```git clone https://github.com/depaul-dice/CHEX```

* Optimal algorithm uses Couenne.
    - Download and install from: https://projects.coin-or.org/Couenne
    - Update: Not needed for set of results reported in PVLDB paper. You can ignore Couenne for now. 
      
---
# Evaluating this artifact

## Repeating the results reported in the paper

1. Run ```python src\replay\plot.py <plot>```
* Plots Available
  * real - Fig 8
  * synthetic
  * storage - Fig 10(b)
  * cr - Fig 10(c)
  * versions - Fig 9(a)
  * algotime - Fig 10(a)
  * timevstorage
  * sciunit - Fig 8 - Only available after running notebooks with Sciunit as explained after this
  * overhead - Fig 9(b) - Only available after running notebooks with Sciunit as explained after this

## Reproducing new results with same notebooks 

1. Install Docker from https://docs.docker.com/get-docker/ 

Using Dockerfiles we will create Alice's environment in which we will audit the notebooks and create new execution trees. 
There are _5_ notebook dockerfiles. For each notebook do steps 2-5. 

2. Build a notebook Dockerfile as:
   ```docker build -t <tagname> .```
     This dockerfile consists of notebooks, their dependencies, and Sciunit.

3. Run the container as:
   ```docker run -it <tagname>```.
   The current folder has all the notebooks that we used, and `python` has all the dependencies installed.
    
4. Run Sciunit to audit and replay with the provided notebooks.  
    
* Create a Sciunit Project
    - ```sciunit create <Project Name>```
    - For ML1 run as:
     ```sciunit create ML1```

* Convert Notebooks to Python Files
    - ```sciunit convert <file.ipynb>```
    - Use `ls` to see notebooks present in the folder
    - Creates a Python file as `<file.ipynb>.py`

* Execute Each Python file **one-by-one**. 
    - ```sciunit exec python <file.py>```
    Each time, Sciunit creates a new execution `e<i>`.
    It's not required to run all notebooks to generate results.

The above step refers to CHEX Audit in the figure and regenerates the execution trees. 

* List all executions as 
    ```sciunit list```

5. To regenerate the figures plot.py reads the updated execution tree from Sciunit: 
    
    - Run ```python chex/src/replay/plot.py sciunit```. The CHEX repo is present in the `chex` folder in the current directory.
This will regenerate the figure 8 of the paper with new execution trees.
    
---
This material is based upon work supported by the National Science Foundation under Grants CNS-1846418, ICER-1639759, ICER-1661918, and a DoE BSSw Fellowship. Any opinions, findings, and conclusions or recommendations expressed in this material are those of the author(s) and do not necessarily reflect the views of the National Science Foundation.
