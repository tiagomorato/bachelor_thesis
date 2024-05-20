import os
import json
from tqdm import tqdm
from googleapiclient.discovery import build
from extract import get_next_free_api_key
from extract import get_video_id_from_video_url

YOUTUBE_DATA_PATH = f"/home/{os.getlogin()}/Desktop/bachelor_thesis/youtube/data/data.json"

def get_youtube_data(file_path: str=YOUTUBE_DATA_PATH):
    """Open the file containing youtube data."""     
    with open(file_path, 'r') as file: return json.load(file) 

def set_youtube_data(docs: json, 
                     file_path: str=YOUTUBE_DATA_PATH):
    """Save new data into the file containing youtube data."""
    with open(file_path, 'w') as file: json.dump(docs, file, indent=4)

def get_links_from_playlist(playlist_url: str) -> None:
    """Save the URL of all videos in a playlist into a text file.

    The the playlist ID will be extracted from the URL, which is after the
    element "list=", as long as it is right after the video ID. If it does not
    work try checking the variable <playlist_id>.
    
    Args:
        playlist_list (str): the full playlist url
    """

    playlist_id = playlist_url.split("=")[2].split("&")[0]
    links_list = list()
    next_page_token = None

    while True:
        request = youtube.playlistItems().list(
            playlistId=playlist_id,
            part='contentDetails',
            maxResults=50,
            pageToken=next_page_token
        )
        response = request.execute()

        for item in tqdm(response['items']):
            video_id = item['contentDetails']['videoId']
            video_url = f'https://www.youtube.com/watch?v={video_id}'
            links_list.append(video_url + "\n")
        
        next_page_token = response.get('nextPageToken')

        if not next_page_token:
            break

    with open("links_from_playlist.txt", 'w+') as file:
        file.writelines(links_list)

def get_video_channel_and_title(video_url: str) -> dict:
    """Get the publisher channel and video title of a youtube video.
    
    Args:
        video_url (str): the full video URL.
        
    Returns:
        dict: a dictionary containing the keys "channel_name" and "video_title". 
    """

    video_id = get_video_id_from_video_url(video_url)

    request = youtube.videos().list(
        part='snippet',
        id=video_id
    )
    response = request.execute()

    if 'items' in response and response['items']:
        channel_name = response['items'][0]['snippet']['channelTitle']
        video_title = response['items'][0]['snippet']['title']
        return {"channel": channel_name, "video": video_title}
    else:
        return None
    
def delete_json_entry_by_index(indexes: list, 
                               file_path: str=YOUTUBE_DATA_PATH) -> None:
    """Delete a specific entry in the JSON file based on its index.
    
    Args:
        indexes (list): a list containing the indexes of the entries to be deleted.
    """

    data = get_youtube_data(file_path=file_path)

    invalid_indexes = [i for i in indexes if i < 0 or i >= len(data)]
    if not invalid_indexes:
        for index in sorted(indexes, reverse=True):
            del data[index]

        set_youtube_data(data)

        print(f"Entry at indexes {indexes} deleted successfully.")
    else:
        print(f"Invalid indexes: {invalid_indexes}. Please provide a valid index.")

def comment_count_of_video_url(video_url: str):
    """Print the number of comments of a specific URL."""

    docs = get_youtube_data()

    for doc in docs:
        if doc["video_url"] == video_url:
            print(len(doc["video_comment"]))

def get_duplicate_entry_in_youtube_data_file():
    docs = get_youtube_data()

    # Check for duplicates
    # it creates a dictionary with the video url and a list associated to it
    # the first element of the list is always how often the repeated element occurs
    # from the second element on it's the indexes of these repeated elements
    # the index can be used to then manually remove repetead elements with the least comments

    vid = dict()

    for index, i in enumerate(docs):
        if i["video_url"] not in vid:
            vid[i["video_url"]] = [1, index]
        else: 
            vid[i["video_url"]][0] += 1
            vid[i["video_url"]].append(index)

    print("Following are the duplicates")
    for x, y in vid.items():
        if y[0] > 1:
            print(x, y)

            comment_count_of_video_url(x)

if __name__ == "__main__":
    api_key = get_next_free_api_key()
    youtube = build('youtube', 'v3', developerKey=api_key)
    # get_links_from_playlist("")
