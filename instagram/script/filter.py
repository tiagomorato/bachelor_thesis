import os
import json
import pandas as pd
# from bachelorarbeit.youtube.script.functions import get_youtube_data

def main():
    with open(f"/home/{os.getlogin()}/Desktop/bachelor_thesis/instagram/data/data.json", 'r') as file: 
        docs = json.load(file) 
    all_comments = list()
    year = ("2020", "2021", "2022")

    for doc in docs:
        post_url = doc["post_url"].split("/")[-2]
        post_user = doc["post_user"]
        post_date = doc["post_date"]
        post_comments = doc["post_comments"]

        if post_date.startswith(year) and len(post_comments) >= 20:
            for comment in post_comments:
                comment_text = comment["comment"]
                comment_date = comment["comment_date"][:10]

                if comment_date.startswith(year):
                    all_comments.append(
                        (post_url, post_user, comment_date, comment_text)
                    )

    df = pd.DataFrame(all_comments, 
                      columns=["url", "channel", "date", "comment"])
    df.to_pickle(f"/home/{os.getlogin()}/Desktop/bachelor_thesis/instagram/data/data_filtered.pkl")


    df["date_year"] = df["date"].apply(lambda x: x.split("-")[0])
    print(df[["channel"]].value_counts())
    print(df[["date_year"]].value_counts())

if __name__ == "__main__":
    print("Filtering comments... ", end="")
    main()
    print("OK")