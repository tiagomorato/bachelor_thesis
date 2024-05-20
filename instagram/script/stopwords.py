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
        + ['...','<','=','>','aff','agr','ah','aham','ai','atila','blá','br','canal',
           'cm','conhecer literarse','de aqui','dr','drauzio','drauziocomliterarse',
           'dráuzio','eai','em ele','em o','etc','fica','hehe','hj','href','hum','ja',
           'krlh','link','literarse','lol','mds','mim','msm','n','nd','nda','né',
           'oatila','oi','olá','oque','parabens','parabéns','peido','pq','pqp','pra',
           'q','qdo','qts','quot','rs','rsrs','sobe','sônia','tb','tbm','td','tds',
           'tmb','tá','tô','ueh','uff','uhuu','vc','vcs','vezs','vixi','vzs','átila',
           'ñ','“','”'
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