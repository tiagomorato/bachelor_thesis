import os
from typing import Dict, List
import pandas as pd
import matplotlib.pyplot as plt
from tqdm import tqdm
from collections import defaultdict
from bertopic import BERTopic

def get_group() -> Dict[str, List[str]]:
    return {
        "brazilian_scientist" : [
            "Olá, Ciência!", "Julio Pereira - Neurocirurgião", "Atila Iamarino", 
            "Canal do Pirulla", "Drauzio Varella", "Paulo Jubilut", 
            "Nunca vi 1 cientista", "Dr. Frederico Porto", "Canal Butantan", 
            "Gustavo Lenci Marques", "Hospital Israelita Albert Einstein", 
            "Dr. Jamal Azzam", "PodPeople - Ana Beatriz Barbosa"
        ],
        "brazilian_youtuber" : [
            "Canal Nostalgia", "Nerdologia", "Meteoro Brasil", 
            "Manual do Mundo", "SpaceToday", "TecMundo", "Brasil Escola"
        ],
        "brazilian_media" : [
            "UOL", "vejapontocom", "Band Jornalismo", "SBT News", "Jornal O Globo", 
            "Domingo Espetacular", "Record News", "Jornalismo TV Cultura", 
            "CanalGov", "RedeTV", "Câmera Record", "Folha de S.Paulo", "Estadão", 
            "g1"
        ],
        "foreign_media" : ["BBC News Brasil", "CNN Brasil", "DW Brasil"],
    }

def get_channel_representativeness(token_count: int, 
                                   df: pd.DataFrame, 
                                   docs: List[str], 
                                   topic_model: BERTopic):
    channel_and_every_key = defaultdict(list)
    channel_and_comment = defaultdict(list)

    for index, row in tqdm(df.iterrows(), total=len(df), 
                           desc="Processing Data..."):
        channel_and_every_key[row["channel"]].append(index)
        channel_and_comment[row["channel"]].append(row["comment"])

    res_doc = topic_model.get_document_info(docs).Document
    res_topic = topic_model.get_document_info(docs).Topic
    document_and_topic = list(zip(res_doc, res_topic))

    channel_and_topic_representation = defaultdict(lambda: defaultdict(int))

    for doc, topic in tqdm(document_and_topic, desc="Document and Topic..."):
        for channel, comments in channel_and_comment.items():
            if doc in comments:
                channel_and_topic_representation[channel][topic] += 1

    # PLOT #
    save_path = f"/home/{os.getlogin()}/Desktop/bachelor_thesis/youtube" \
                f"/result/compare_group/tokens_{token_count}/"
    if not os.path.exists(save_path): 
        os.makedirs(save_path)

    all_keys = sorted(list(res_topic.unique()))

    for topic_number_of_interest in tqdm(all_keys[:14], 
                                         desc="topic_number_of_interest..."):
        participations = {
            channel_name: topics.get(topic_number_of_interest, 0) 
            for channel_name, topics in channel_and_topic_representation.items()
        }

        channel_names = list(participations.keys())
        topic_counts = list(participations.values())

        group_mapping = get_group()
        color_mapping = {
            "brazilian_scientist": "blue", 
            "brazilian_youtuber": "green",
            "brazilian_media": "yellow",
            "foreign_media": "orange"
        }  

        colors = [color_mapping[next(key for key, value in group_mapping.items() 
                                     if channel_name in value)] for channel_name 
                                     in channel_names]
        fig = plt.figure(figsize=(9, 7))
        bars = plt.barh(channel_names, topic_counts, color=colors)

        plt.title(f"Wie stark sind die YouTube-Kanäle im Topic " \
                  f"[{topic_number_of_interest}] vertreten?")
        plt.xlabel("Anzahl Kommentare")
        plt.ylabel("YouTube-Kanal")

        legend_labels = list(color_mapping.keys())
        legend_handles = [plt.Rectangle((0,0),1,1, color=color_mapping[label]) 
                          for label in legend_labels]
        plt.legend(legend_handles, legend_labels)

        plt.tight_layout()
        plt.savefig(f"{save_path}topic_{topic_number_of_interest}.svg")
        plt.close()