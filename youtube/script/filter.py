import os
import pandas as pd
from extract import get_video_id_from_video_url
from functions import get_youtube_data

def main():
    docs = get_youtube_data()
    all_comments = list()
    year = ("2020", "2021", "2022")

    for doc in docs:
        video_url = doc["video_url"]
        video_url = get_video_id_from_video_url(video_url)
        video_date = doc["video_published_at"][:10]
        video_channel = doc["video_channel_title"]
        # video_title = doc["video_title"]

        if video_date.startswith(year) and len(doc["video_comment"]) >= 20:
            for comment in doc["video_comment"]:
                comment_text = comment["comment_text_display"]
                comment_date = comment["comment_published_at"][:10]

                if comment_date.startswith(year):
                    all_comments.append(
                        (video_url, video_channel, comment_date, comment_text)
                    )
                    
                    if comment["comment_reply"]:
                        for reply in comment["comment_reply"]:
                            reply_text = reply["reply_text_display"]
                            reply_date = reply["reply_published_at"][:10]

                            if reply_date.startswith(year):
                                all_comments.append(
                                    (video_url, 
                                     video_channel, 
                                     reply_date, 
                                     reply_text)
                                )
    
    df = pd.DataFrame(all_comments, 
                      columns=["url", "channel", "date", "comment"])
    df.to_pickle(f"/home/{os.getlogin()}/Desktop/bachelor_thesis/" \
                  "youtube/data/data_filtered.pkl")
       
if __name__ == "__main__":
    print("Filtering comments... ", end="")
    main()
    print("OK")
