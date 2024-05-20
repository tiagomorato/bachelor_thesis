import os
import sys
import pandas as pd
import matplotlib.pyplot as plt
from langdetect import detect
from tqdm import tqdm

YOUTUBE_DATA_DIR = f"/home/{os.getlogin()}/Desktop/bachelor_thesis/youtube/data"

def create_language_distribution(token: int, df: pd.DataFrame):
    file_path = f"/home/{os.getlogin()}/Desktop/bachelor_thesis" \
                 "/youtube/result/language"
    if not os.path.exists(file_path):
        os.makedirs(file_path)

    language_counts = df["lang"].value_counts().head(5)
    total_count = language_counts.sum()
    language_percentages = (language_counts / total_count) * 100

    plt.figure(figsize=(7, 4))
    bars = language_counts.plot(kind="bar", color="skyblue")
    plt.xlabel("ISO-639-Sprachcode")
    plt.ylabel("Anzahl")
    plt.title(f"Top 5 erkannte Sprachen [Tokens>={token}, n={len(df)}]", 
              fontsize=15)

    for bar, percentage in zip(bars.patches, language_percentages):
        plt.text(bar.get_x() + bar.get_width() / 2, 
                 bar.get_height() + 0.02 * max(language_counts), 
                f'{int(bar.get_height())}\n({percentage:.1f}%)', 
                ha='center', 
                fontsize=10, 
                color='black')

    plt.xticks(rotation=0)
    plt.ylim(0, 1.2 * max(language_counts))

    plt.savefig(file_path + f"/language_distribution_{token}_tokens.svg", 
                format="svg", bbox_inches="tight")
    # plt.show()

def main():
    file_path = f"{YOUTUBE_DATA_DIR}/data_preprocessed_1_tokens.pkl"
    df = pd.read_pickle(file_path)

    if "lang" in df.columns.tolist():
        print("Column [lang] already exists. Closing...")
        sys.exit()

    tqdm.pandas(desc="Detecting language [tokens=%s]..." % file_path.split("_")[3])
    df["lang"] = df["comment"].progress_apply(detect)

    for token_count in [100, 75, 50, 25, 10, 1]:
        save_path = f"{YOUTUBE_DATA_DIR}/data_preprocessed_{token_count}_tokens.pkl"
            
        df_filtered = df[df["token_count"] >= token_count]
        # df_filtered = df_filtered.drop(columns=["token_count"])      
        df_filtered.to_pickle(save_path)

        create_language_distribution(token=token_count, df=df_filtered)

if __name__ == "__main__":
    # execution takes around [2h23min]
    main()