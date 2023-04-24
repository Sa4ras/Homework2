# RL with MinAtar

## Install
Install either Anaconda or Miniconda using instructions below

https://docs.conda.io/projects/continuumio-conda/en/latest/user-guide/install/index.html

After installing Conda, follow the following instructions on a terminal:
```bash
cd <assignment_dir>
Create a conda environment using the following:

conda env create -f cs234-torch-10.1.yml
conda activate cs234-torch

pip install -r requirements.txt
git clone https://github.com/kenjyoung/MinAtar.git
cd MinAtar
pip install .
cd ../
```

## Results
### q4_linear_torch graph
![Alt text](/results/q4_linear_torch_results.png)

### q5_nature_torch graph
![Alt text](/results/q5_nature_torch_results.png)

### q6_train_atari_linear graph
![Alt text](/results/q6_train_atari_linear_results.png)
