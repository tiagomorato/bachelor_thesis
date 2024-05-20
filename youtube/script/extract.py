import os
import re
import sys
import json
from typing import Dict, List
from tqdm import tqdm
from dotenv import load_dotenv, find_dotenv
from urllib.request import urlopen
from urllib.error import HTTPError
from googleapiclient.discovery import build
_ = load_dotenv(find_dotenv())

YOUTUBE_DATA_DIR = f"/home/{os.getlogin()}/Desktop/bachelor_thesis/youtube/data"

def get_youtube_comments(video_url: str,
                         api_key: str,
                         max_number_of_comments: int=50000) -> Dict[str, str]:
    
    """Return a dict with the information of the given video

    :video_url: YouTube video URL
    :api_key: YouTube API v3 key
    :number_comments: upper boundary of how many comments to retrieve
    :return: a dict with all comments, where each comment is a separate string
    """

    video_id = get_video_id_from_video_url(video_url)

    youtube = build('youtube', 'v3', developerKey=api_key)
    url = 'https://www.googleapis.com/youtube/v3/commentThreads?key=' \
            + api_key + '&textFormat=plainText&part=snippet&videoId=' \
            + video_id + '&maxResults=100'
    raw_url = url
    last_nextPageToken = '-'
    comment_id = 0

    video_info = {
        'video_url': video_url,
        # 'video_channel_id': '',
        'video_channel_title': '',
        'video_published_at': '',
        'video_title': '',
        'video_comment': [],
    }

    while comment_id < max_number_of_comments:
        try:
            response = urlopen(url)
            json_data = json.loads(response.read())

            if not video_info['video_published_at']:
                video_request = youtube.videos().list(
                    part="snippet",
                    id=video_id
                )
                video_response = video_request.execute()

                for item in video_response['items']:

                    video_published_at = item['snippet']['publishedAt']
                    video_title = item['snippet']['title']
                    # video_channel_id = item['snippet']['channelId']
                    # video_description = item['snippet']['description']
                    video_channel_title = item['snippet']['channelTitle']

                # video_info["video_channel_id"] = video_channel_id
                video_info["video_published_at"] = video_published_at
                video_info["video_title"] = video_title
                video_info["video_channel_title"] = video_channel_title

            for item in tqdm(json_data['items']):
                # comment_video_id = item['snippet']['videoId']
                comment_text_display = item['snippet']['topLevelComment'] \
                                           ['snippet']['textDisplay']
                comment_text_display = re.sub('[\s]+', ' ', comment_text_display)
                comment_published_at = item['snippet']['topLevelComment']['snippet']['publishedAt']
                comment_reply_count = item['snippet']['totalReplyCount']

                comment_info = {
                    # 'comment_video_id': comment_video_id,
                    'comment_text_display': comment_text_display,
                    'comment_published_at': comment_published_at,
                    # 'comment_reply_count': comment_reply_count,
                    'comment_reply':  []
                }

                if comment_reply_count > 0:
                    parent_id = item['id']

                    request_replies = youtube.comments().list(
                        part='snippet',
                        parentId=parent_id,
                        maxResults=100
                    )
                    response_replies = request_replies.execute()

                    for reply in response_replies['items']:
                        reply_text_display = reply['snippet']['textDisplay']
                        reply_published_at = reply['snippet']['publishedAt']
                        reply_info = {
                            'reply_published_at': reply_published_at,
                            'reply_text_display': reply_text_display,
                        }
                        comment_info['comment_reply'].append(reply_info)
                        comment_id += 1

                video_info['video_comment'].append(comment_info)
                
                if comment_id > 50 and comment_id % 500 == 0:
                    print(comment_id)
                comment_id += 1

            if 'nextPageToken' in json_data:
                nextPageToken = json_data['nextPageToken']
                url = raw_url + '&pageToken='+nextPageToken

            if nextPageToken == last_nextPageToken:
                print(f"Successfully retrieved [{comment_id}] comments.")
                print("Can't go to the next page. Ending...")
                break

            last_nextPageToken = nextPageToken

        except HTTPError as e:
            if e.code == 403:
                print("HTTP ERROR 403 => the API reached the \
                      maximum allowed requests.")
                return 403

        except Exception as e:
            print("Something went wrong:", e)
            print(f"Successfully retrieved [{comment_id}] comments.")
            break

    return video_info

def get_api_key() -> List[str]:
    api_key = open(f"{YOUTUBE_DATA_DIR}/youtube_api_key.txt").readlines()
    return [x.split(";")[0] for x in api_key]

def get_next_free_api_key() -> str | None:
    for key in get_api_key(): 
        if not key.startswith("#"):
            return key
    return None

def set_api_key_as_visited(visited_api_key: str, 
                           filename: str=f"{YOUTUBE_DATA_DIR}/youtube_api_key.txt") -> None:
    """Set a given api key as visited."""
    print("Set the api key as visited... ", end="")
    with open(filename, 'r') as file:
        lines = file.readlines()

    for idx, line in enumerate(lines):
        current_api_key = line.split(";")[0].strip()
        if current_api_key == visited_api_key:
            lines[idx] = f'#{lines[idx]}'
            break

    with open(filename, 'w') as file:
        file.writelines(lines)
    print("OK")

def set_all_api_key_as_unvisited(filename: str=f'{YOUTUBE_DATA_DIR}/youtube_api_key.txt') -> None:
    """Set all api keys as unvisited."""
    with open(filename, 'r') as file:
        lines = file.readlines()

    for idx, line in enumerate(lines):
        if line.startswith("#"):
            lines[idx] = line.replace("#", "")
    
    with open(filename, 'w') as file:
        file.writelines(lines)

def get_unvisited_videos(filename: str=f'{YOUTUBE_DATA_DIR}/youtube_video.txt') -> List[str]:
    with open(filename, 'r') as file: 
        lines = file.readlines()
    return [line.strip() for line in lines if not line.startswith('#')]

def get_video_id_from_video_url(video_url: str) -> str: 
    return video_url.strip().split('=')[-1]

def set_video_as_visited(video_url: str, 
                         filename: str=f'{YOUTUBE_DATA_DIR}/youtube_video.txt') -> None:
    """Set a video as visited."""
    print("Set video URL as visited... ", end="")

    with open(filename, 'r') as file:
        lines = file.readlines()

    for idx, line in enumerate(lines):
        if line.strip() == video_url:
            lines[idx] = f'#{lines[idx]}'
            break
    
    with open(filename, 'w') as file:
        file.writelines(lines)
    print("OK")

def save_comments_to_json(new_data: dict, 
                          filename: str=f'{YOUTUBE_DATA_DIR}/data.json') -> None:
    """Save extracted comments in a json file."""
    print("Saving comments to json... ", end="")
    if not os.path.exists(filename):
        with open(filename, 'w') as f:
            json.dump([], f)

    with open(filename, 'r+') as file:
        file_data = json.load(file)
        file_data.append(new_data)
        file.seek(0)
        json.dump(file_data, file, indent=4)
        print("OK")

def delete_duplicate_youtube_url():
    """Search for duplicate URLs in the youtube_videos.txt file and keep first 
    occurrence. Reasoning: while adding new URLs manually, it might occur that
    the same link is visited in the future and added again accidentally to the
    txt file.
    """
    # 1. load youtube_videos.txt 
    # 2. 
    pass

def main():
    while True:
        api_key = get_next_free_api_key()
        unvisited_videos = get_unvisited_videos()   

        if not api_key: 
            print("There is no api key available.")
            sys.exit()
        elif not unvisited_videos: 
            print("There is no unvisited videos.")
            sys.exit()

        for video_url in unvisited_videos:
            print("\nURL", video_url)
            new_data = get_youtube_comments(video_url, api_key=api_key)
        
            # BUG: handle videos with comment section deactivated
            # BUG: handle videos that are private

            if new_data == 403:
                print(f"Skipping to next iteration... new_data=[{new_data}]")
                set_api_key_as_visited(api_key)
                break

            save_comments_to_json(new_data)
            set_video_as_visited(video_url)

if __name__ == "__main__":
    # set_api_key_as_unvisited()
    main()