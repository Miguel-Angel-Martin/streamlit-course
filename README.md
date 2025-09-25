## Virtual enviroment with UV

How to install from pyproject.toml

uv venv --name str-dev --python 3.13

uv sync --active

## Activate virtual enviroment

En el directorio principal

source str-dev/bin/activate

## Streamlit

streamlit run text.py --server.port 5000      

## Uv to install packges
uv add streamlit-extras
uv pip install streamlit-aggrid
uv pip sync pyproject.toml                             


## para crear requirements.txt limpio y estatico

uv export --format requirements-txt > requirements.txt   

uv export --format requirements-txt --no-hashes > requirements.txt  

uv export --format requirements-txt --no-hashes | sed 's/==/>=/' > requirements.txt