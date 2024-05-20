import os
from typing import List, Tuple
import pandas as pd
import matplotlib.pyplot as plt
from tqdm import tqdm
from wordcloud import WordCloud
from numpy import ndarray
from sklearn.feature_extraction.text import CountVectorizer
from sentence_transformers import SentenceTransformer
from umap import UMAP
from hdbscan import HDBSCAN
from bertopic import BERTopic
from channel_representativeness import get_channel_representativeness
# conda install -c plotly plotly-orca # https://github.com/plotly/orca

YOUTUBE_DIR = f"/home/{os.getlogin()}/Desktop/bachelor_thesis/youtube"

def get_umap(n_neighbors=5, n_components=5, min_dist=0.0, metric="cosine", 
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

def save_topic_model(topic_model: BERTopic, filename: str) -> None:    
    topic_model.save(f"{YOUTUBE_DIR}/result/{filename}/model_dir",
                     serialization="safetensors",
                     save_ctfidf=True,
                     save_embedding_model="sentence-transformers/" \
                                          "all-MiniLM-L6-v2")

def get_topic_info(save_path: str, topic_model: BERTopic) -> None: 
    topic_model.get_topic_info().to_pickle(
        path=save_path + "/get_topic_info.pkl"
    )

def get_topic_word_scores(token_count: int, topic_model: BERTopic) -> None: 
    save_path = f"{YOUTUBE_DIR}/result/topic_word_scores/"
    if not os.path.exists(save_path): 
        os.makedirs(save_path)

    topic_model.visualize_barchart(
        top_n_topics=12,
        title="<b>Topic Word Scores</b>"
    ).write_image(save_path + f"topic_word_scores_{token_count}_tokens.svg", 
                  engine="orca")

def get_intertopic_distance_map(save_path: str, topic_model: BERTopic) -> None: 
    topic_model.visualize_topics(
        top_n_topics=12
    ).write_html(save_path + "/intertopic_distance_map.html")

def get_similarity_matrix(save_path: str, topic_model: BERTopic) -> None: 
    topic_model.visualize_heatmap(
        top_n_topics=12
    ).write_html(save_path + "/similarity_matrix.html")
    
def get_topics_over_time(token_count: int, 
                         topic_model: BERTopic, 
                         docs: List[str], 
                         timestamps: List[str]) -> None:
    save_path = f"{YOUTUBE_DIR}/result/topics_over_time/"
    if not os.path.exists(save_path): 
        os.makedirs(save_path)

    topics_over_time = topic_model.topics_over_time(
        docs, timestamps, datetime_format="%Y-%m-%d"
    )
    
    topic_model.visualize_topics_over_time(
        topics_over_time, 
        top_n_topics=5
    ).write_image(save_path + f"topics_over_time_{token_count}_tokens.svg", 
                  engine="orca")

def get_wordcloud(token_count: int, topic_model: BERTopic, topic: int) -> None:
    save_path = f"{YOUTUBE_DIR}/result/wordcloud/"
    if not os.path.exists(save_path): 
        os.makedirs(save_path)

    text = {word: value for word, value in topic_model.get_topic(topic)}
    wc = WordCloud(background_color="white", max_words=1000)
    wc.generate_from_frequencies(text)
    plt.figure()
    plt.imshow(wc, interpolation="bilinear")
    plt.axis("off")
    plt.savefig(save_path + f"wordcloud_{token_count}_tokens.svg",
                format="svg", 
                bbox_inches="tight")

def main():
    for token_count in tqdm([
                    # 100, 
                    75, 
                    50, 
                    25, 
                    10,
                    1
                   ]
                  ):
        filename = f"data_preprocessed_{token_count}_tokens" 
        load_path = f"{YOUTUBE_DIR}/data/{filename}.pkl"
        result_filename = f"data_processed_{token_count}_tokens"
        save_path = f"{YOUTUBE_DIR}/result/{result_filename}/plot"
        if not os.path.exists(save_path): 
            os.makedirs(save_path)

        print(f"+++++{filename}+++++")

        df = pd.read_pickle(load_path)[["date", "channel", "comment", "lang"]]
        df = df[df["lang"] == "pt"] # filter by language

        docs = df["comment"].astype(str).tolist()
        timestamps = df["date"].astype(str).tolist()

        topic_model = topic_modeling(docs)

        save_topic_model(topic_model, result_filename)

        get_topic_info(save_path, topic_model)
        get_topic_word_scores(token_count, topic_model)
        get_topics_over_time(token_count, topic_model, docs, timestamps)
        # get_intertopic_distance_map(save_path, topic_model)
        # get_similarity_matrix(save_path, topic_model)
        # get_wordcloud(token_count, topic_model, 0)

        get_channel_representativeness(token_count=token_count, 
                                       df=df, 
                                       docs=docs, 
                                       topic_model=topic_model)
if __name__ == "__main__":
    os.environ["TOKENIZERS_PARALLELISM"] = "false"
    main()