# !pip install leia-br
# Source: https://pypi.org/project/leia-br/
import os
import sys
from typing import Dict, Tuple
import pandas as pd
import matplotlib.pyplot as plt
from tqdm import tqdm
from LeIA import SentimentIntensityAnalyzer

YOUTUBE_DATA_DIR = f"/home/{os.getlogin()}/Desktop/bachelor_thesis/youtube/data"
SIA = SentimentIntensityAnalyzer()

def detect_sentiment(text: str) -> Dict[str, float]: 
    """Return a dict containing the sentiment values [neg, neu, pos, compound]
    example: 
    {
        'neg': 0.17, 
        'neu': 0.718, 
        'pos': 0.111, 
        'compound': -0.9062
    }
    """
    return SIA.polarity_scores(text)

def process_sentiment(file_path: str, df: pd.DataFrame) -> None:
    """
    Calculate the sentiment, append it to the original DataFrame and save it
    in the same original file, overwritting/replacing it.

    file_path: full path of the .pkl file
    """
    tqdm.pandas(desc="Detecting sentiment [tokens=%s]..." % file_path.split("_")[3])
    df_sentiment = df['comment'].progress_apply(detect_sentiment)

    sentiment_df = pd.DataFrame(df_sentiment.tolist())

    df_sent = df.reset_index(drop=True, inplace=True)
    df_sent = pd.concat([df, sentiment_df], axis=1)
    # df_sent.to_pickle(file_path)

    return df_sent

def calculate_sentiment_counts(df: pd.DataFrame) -> Tuple[int, int, int]:
    sent_pos = df[df['compound'] >= 0.05]
    sent_neg = df[df['compound'] <= -0.05]
    sent_neu = df[(df['compound'] > -0.05) & (df['compound'] < 0.05)]

    return len(sent_pos), len(sent_neg), len(sent_neu)

def create_sentiment_visualization(token_count: int, df: pd.DataFrame) -> None:
    file_path = f"/home/{os.getlogin()}/Desktop/bachelor_thesis" \
                 "/youtube/result/sentiment"
    if not os.path.exists(file_path):
        os.makedirs(file_path)

    pos_count, neg_count, neu_count = calculate_sentiment_counts(df)

    labels = [f'Positiv\n({pos_count})', 
              f'Negativ\n({neg_count})', 
              f'Neutral\n({neu_count})']
    sizes = [pos_count, neg_count, neu_count]
    colors = ["green", "darkred", "gray"] # colors: https://matplotlib.org/stable/gallery/color/named_colors.html

    plt.figure(figsize=(8, 7))
    plt.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', startangle=140)
    plt.title('Stimmungsverteilung [Tokens>=%s, n=%s]' % (token_count, sum(sizes)), 
              fontsize=15)
    plt.axis('equal') 
    plt.savefig(file_path + f"/sentiment_distribution_{token_count}_tokens.svg", 
                bbox_inches='tight')  
    plt.close()
    # plt.show()

def main():
    file_path = f"{YOUTUBE_DATA_DIR}/data_preprocessed_1_tokens.pkl"
    df = pd.read_pickle(file_path)

    if "neg" and "neu" and "pos" and "compound" in df.columns.tolist():
        print("Columns [neg, neu, pos, compound] already exist. Closing...")
        sys.exit()

    df_sent = process_sentiment(file_path, df)
    
    for token_count in [100, 75, 50, 25, 10, 1]:
        df_filtered = df_sent[df_sent["token_count"] >= token_count]
        # df_filtered = df_filtered.drop(columns=["token_count"])      
        df_filtered.to_pickle(f"{YOUTUBE_DATA_DIR}/data_preprocessed_{token_count}_tokens.pkl")
        df_filtered = df_filtered[df_filtered["lang"] == "pt"]
        create_sentiment_visualization(token_count=token_count, df=df_filtered)

if __name__ == "__main__":
    # execution takes around 3 minutes [2:48]
    main()