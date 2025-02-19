# wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh
# bash Miniconda3-latest-Linux-x86_64.sh
# source ~/.bashrc
# source miniconda3/etc/profile.d/conda.sh
# conda init zsh
# source ~/.zshrc
# conda config --set auto_activate_base true

pip install poetry
poetry config virtualenvs.path .venv
poetry config virtualenvs.in-project true
poetry install
