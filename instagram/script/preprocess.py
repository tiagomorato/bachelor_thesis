import time
import os
import re
from typing import List
import pandas as pd
import numpy as np
import spacy
from tqdm import tqdm
from stopwords import get_stopwords, get_normalized_words

INSTAGRAM_DATA_DIR = f"/home/{os.getlogin()}/Desktop/bachelor_thesis" \
                      "/instagram/data"
STOPWORDS = get_stopwords()

def remove_hashtag(text): return re.sub('#\w+', '', text).strip()
def remove_mention(text): return re.sub("@\w+", '', text).strip()
def remove_laughter(text): return re.sub(r'(ha)+|(k)+', '', text).strip()

def is_valid_token(token: str) -> bool:
    return (
        not token.is_stop
        and not token.is_space
        and not token.is_punct
        and not token.is_digit
        and not token.is_oov
        and not token.like_url
        and not token.like_num
        and token.is_alpha
        and token.text not in STOPWORDS
        and len(token.lemma_) >= 3
    ) 

def spacy_preprocessing(df: pd.DataFrame, docs: List[str]) -> pd.DataFrame:
    for idx, doc in enumerate(tqdm(docs, desc="spacy_preprocessing")):
        processed_text = [token.lemma_ for token in doc if is_valid_token(token)]
        df.iat[idx, 3] = " ".join(processed_text) if processed_text else ""
        
    return df

def main():
    """If <n_process> is activated, gpu must not be used in paralell as it'll
    lead to conflict"""

    df = pd.read_pickle(f"{INSTAGRAM_DATA_DIR}/data_filtered.pkl")

    df['comment'] = df['comment'].apply(str.lower) 
    df['comment'] = df['comment'].apply(remove_hashtag)
    df['comment'] = df['comment'].apply(remove_mention)
    df['comment'] = df['comment'].apply(remove_laughter)
    normalized_words = get_normalized_words()
    df.replace(normalized_words, regex=True, inplace=True)

    nlp = spacy.load("pt_core_news_lg", 
                     exclude=["tagger", "ner", "morphologizer"])     
    docs = nlp.pipe(df["comment"], n_process=6) 
    df = spacy_preprocessing(df, docs)

    normalized_words = get_normalized_words()
    df['comment'] = df['comment'].replace(normalized_words, regex=True)
    df['comment'] = df['comment'].apply(lambda x: re.sub(r'\s+', ' ', x).strip())
    df['comment'] = df['comment'].replace('', np.nan)
    df.dropna(subset=['comment'], inplace=True)
    df.drop_duplicates(subset="comment", keep="first", inplace=True)
    df['comment'] = df['comment'].apply(str.lower)
    df["token_count"] = df["comment"].apply(lambda x: len(x.split()))

    df = pd.read_pickle(f"{INSTAGRAM_DATA_DIR}/data_preprocessed.pkl")

if __name__ == "__main__":
    main()