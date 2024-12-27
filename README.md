# Simplify Chinese

This tool is intended to take Chinese Wikipedia pages or text, and rewrite them in a simpler manner for reading practice for language learning. 

# How to use this

## Installation

First, install `ollama` on your platform of choice [here](https://ollama.com/download/). 

Then, run `setup.sh` to download GLM-4, and `pip install -r requirements.txt` to get the requisite packages. 

## Running the app locally

This is a Streamlit-based app. Hence, simply run `streamlit run app.py` and a window in your browser will open (usually `localhost:8501`).

## Limitations

This is not a translation tool. LLM-generated text is *not* guaranteed to be coherent or grounded in the target text (though it often is). As a heritage speaker I have some intuition to lean on, but as such, this tool is not a replacement for another structured language learning tool.