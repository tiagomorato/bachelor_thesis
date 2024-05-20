import os
from typing import List, Tuple
import pandas as pd
from numpy import ndarray
from sklearn.feature_extraction.text import CountVectorizer
from sentence_transformers import SentenceTransformer
from umap import UMAP
from hdbscan import HDBSCAN
from bertopic import BERTopic

INSTAGRAM_DIR = f"/home/{os.getlogin()}/Desktop/bachelor_thesis/instagram"

def get_umap(n_neighbors=20, n_components=5, min_dist=0.0, metric="cosine", 
             random_state=42) -> UMAP:
    return UMAP(n_neighbors=n_neighbors,
                n_components=n_components,
                min_dist=min_dist,
                metric=metric,
                random_state=random_state)

def get_hdbscan(min_cluster_size=10) -> HDBSCAN:
    return HDBSCAN(min_cluster_size=min_cluster_size, prediction_data=True)

def get_embedding_model(docs: List[str]) -> Tuple[SentenceTransformer, ndarray]:
    embedding_model = SentenceTransformer(
        model_name_or_path="paraphrase-multilingual-MiniLM-L12-v2", 
        device="cuda")
    
    embeddings = embedding_model.encode(docs, 
                                        show_progress_bar=True, 
                                        batch_size=32)
    return embedding_model, embeddings

def topic_modeling(docs: List[str]) -> BERTopic:
    embedding_model, embeddings = get_embedding_model(docs)
    umap_model, hdbscan_model = get_umap(), get_hdbscan()
    vectorizer_model = CountVectorizer(ngram_range=(1,1))
    top_n_words = 10
    nr_topics = 50
    topic_model = BERTopic(
        language="multilingual",
        embedding_model=embedding_model,
        umap_model=umap_model,
        hdbscan_model=hdbscan_model,
        vectorizer_model=vectorizer_model,
        top_n_words=top_n_words,
        nr_topics=nr_topics,
        verbose=True
    )

    topic_model.fit_transform(docs, embeddings)

    return topic_model

def save_topic_model(topic_model: BERTopic) -> None:    
    save_path = f"{INSTAGRAM_DIR}/result/model_dir"

    if not os.path.exists(save_path): 
        os.makedirs(save_path)

    topic_model.save(
        save_path,
        serialization="safetensors",
        save_ctfidf=True,
        save_embedding_model="sentence-transformers/all-MiniLM-L6-v2"
    )

def get_topic_info(topic_model: BERTopic) -> None: 
    topic_model.get_topic_info().to_pickle(
        path=f"{INSTAGRAM_DIR}/result/model_dir/get_topic_info.pkl"
    )

def get_topic_word_scores(topic_model: BERTopic) -> None: 
    topic_model.visualize_barchart(
        top_n_topics=12,
        title="<b>Topic Word Scores</b>"
    ).write_image(f"{INSTAGRAM_DIR}" + "/result/topic_word_scores.svg", 
                  engine="orca")

def get_topics_over_time(topic_model: BERTopic, 
                         docs: List[str], 
                         timestamps: List[str]) -> None:
    topics_over_time = topic_model.topics_over_time(
        docs, timestamps, datetime_format="%Y-%m-%d"
    )
    
    topic_model.visualize_topics_over_time(
        topics_over_time, 
        top_n_topics=5
    ).write_image(f"{INSTAGRAM_DIR}/result/topics_over_time.svg", 
                  engine="orca")

def main():
    save_path = f"{INSTAGRAM_DIR}/result/"
    if not os.path.exists(save_path): 
        os.makedirs(save_path)

    df = pd.read_pickle(f"{INSTAGRAM_DIR}/data/data_preprocessed.pkl")

    df["token_count"] = df["comment"].apply(lambda x: len(x.split()))

    df = df[(df["token_count"] >= 10) & (df["lang"] == "pt")]

    docs = df["comment"].astype(str).tolist()
    timestamps = df["date"].astype(str).tolist()

    topic_model = topic_modeling(docs)

    save_topic_model(topic_model)
    get_topic_info(topic_model)
    get_topic_word_scores(topic_model)
    get_topics_over_time(topic_model, docs, timestamps)

if __name__ == "__main__":
    os.environ["TOKENIZERS_PARALLELISM"] = "false"
    main()