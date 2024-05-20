import stopwordsiso as stopwords_iso
from spacy.lang.pt.stop_words import STOP_WORDS as stopwords_spacy
from nltk.corpus import stopwords as stopwords_nltk
from typing import Dict, Set

def get_stopwords() -> Set[str]:
    return set(
        stopwords_nltk.words('portuguese')
        + stopwords_nltk.words('english')
        + list(stopwords_iso.stopwords("pt"))
        + list(stopwords_spacy)
        + ['...', 'agr', 'aham', 'blá', 'canal', 'de aqui', 'eai', 
           'em ele', 'em o', 'etc', 'fica', 'hehe', 'href', 'href', 'hum', 
           'krlh', 'link', 'lol', 'mds', 'mim', 'msm', 'nda', 'olá', 'oque', 
           'parabens', 'parabéns', 'peido', 'pqp', 'pra', 'pra', 'qdo', 'qts', 
           'quot', 'quot', 'rsrs', 'sobe', 'sônia', 'tbm', 'tds', 'tmb', 'ueh', 
           'uff', 'uhuu', 'vcs', 'vcs', 'vezs', 'vixi', 'vzs',
          ]
    )

def get_normalized_words() -> Dict[str, str]:
    return {
        'agua': 'água',
        'alcool': 'álcool',
        'bacteria': 'bactéria',
        'bilionario': 'bilionário',
        'cabeca': 'cabeça',
        'celula': 'célula',
        'chines': 'chinês',
        'cidadao': 'cidadão',
        'ciencia': 'ciência',
        'cientifico': 'científico',
        'conteudo': 'conteúdo',
        'coronavirus': 'coronavírus',
        'covid-19': 'covid',
        'covid19': 'covid',
        'doenca': 'doença',
        'escandalo': 'escândalo',
        'familia': 'família',
        'fiquar': 'ficar',
        'genetico': 'genético',
        'historia': 'história',
        'imunologico': 'imunológico',
        'informacao': 'informação',
        'mae': 'mãe',
        'mao': 'mão',
        'mascara': 'máscara',
        'mascaras': 'máscara',
        'medico': 'médico',
        'midia': 'mídia',
        'máscaras': 'máscara',
        'obito': 'óbito',
        'onibus': 'ônibus',
        'operacao': 'operação',
        'oxigenio': 'oxigênio',
        'oxigénio': 'oxigênio',
        'politica': 'política',
        'politico': 'político',
        'proteina': 'proteína',
        'pulmao': 'pulmão',
        'saude': 'saúde',
        'vacinacao': 'vacinação',
        'vacinas': 'vacina',
        'vacino': 'vacinar',
        'video': 'vídeo',
        'virus': 'vírus',
    }