# Imports
import os
import sys
import math
import datetime
from pathlib import Path
import pandas as pd
import numpy as np
import locale
try:
    locale.setlocale(locale.LC_TIME, "pt_PT.utf8")
except locale.Error:
    locale.setlocale(locale.LC_TIME, "pt_PT")


link_repo = "https://github.com/dssg-pt/covid19pt-data"

# https://www.ine.pt/xportal/xmain?xpid=INE&xpgid=ine_indicadores&indOcorrCod=0008273&xlang=pt
# POP_PT = 10_298_252
# POP_PT_CONTINENTE = 9_802_128
# Açores 242_201 | Madeira 253_923

# Keeping these consistent with previous vaccination numbers
POP_PT = 10_347_892
POP_PT_CONTINENTE = 9_860_175
POP_VACINAVEL = 9_234_166
#POP_0_11 = 1_113_726

# POP_IDADE = {
#     '0_9':      433_332 + 461_299,  #  0-04 + 05-09
#     '10_19':    507_646 + 549_033,  # 10-14 + 15-19
#     '20_29':    544_575 + 547_505,  # 20-24 + 25-29
#     '30_39':    571_355 + 679_093,  # 30-34 + 35-39
#     '40_49':    792_670 + 782_555,  # 40-44 + 45-49
#     '50_59':    747_581 + 734_540,  # 50-54 + 55-59
#     '60_69':    672_758 + 620_543,  # 60-64 + 65-69
#     '65_69':          0 + 620_543,  #     0 + 65-69
#     '70_79':    544_016 + 429_107,  # 70-74 + 75-79
#     '80_plus':  352_218 + 316_442,  # 80-84 + 85 ou mais
# }
# https://www.pordata.pt/Portugal/População+residente++média+anual+total+e+por+grupo+etário-10
POP_IDADE = {
    'TOTAL':    10_297_081,
    '0_9':      436_118 + 450_275,  # 433_332 + 461_299,  #  0-04 + 05-09
    '10_19':    503_414	+ 540_882,  # 507_646 + 549_033,  # 10-14 + 15-19
    '20_29':    557_119	+ 547_637,  # 544_575 + 547_505,  # 20-24 + 25-29
    '30_39':    566_423	+ 661_324,  # 571_355 + 679_093,  # 30-34 + 35-39
    '40_49':    774_449	+ 796_276,  # 792_670 + 782_555,  # 40-44 + 45-49
    '50_59':    745_100	+ 741_435,  # 747_581 + 734_540,  # 50-54 + 55-59
    '60_69':    681_597	+ 625_377,  # 672_758 + 620_543,  # 60-64 + 65-69
    '65_69':          0 + 625_377,  #       0 + 620_543,  #     0 + 65-69
    '70_79':    552_932	+ 438_002,  # 544_016 + 429_107,  # 70-74 + 75-79
    '80_plus':  350_661	+ 328_066,  # 352_218 + 316_442,  # 80-84 + 85 ou mais
}

PROPORTION_CONTINENTE = POP_PT_CONTINENTE / POP_PT
POP_VACINAVEL_CONTINENTE = POP_VACINAVEL * PROPORTION_CONTINENTE

# Proportion is not constant per age group
#POP_IDADE = dict (
#    (k, v * PROPORTION_CONTINENTE) for (k, v) in POP_IDADE.items()
#)


# https://www.pordata.pt/DB/Municipios/Ambiente+de+Consulta/Tabela
PROPORTIONS = {
    'TOTAL':   9_857_593 / 10_344_802,
    '0_14':    1_264_897 /  1_331_396,
    '15_64':   6_257_752 /  6_589_284,
    '65_plus': 2_334_944 /  2_424_122,
}
POP_IDADE = {
    'TOTAL':    POP_IDADE['TOTAL'] * PROPORTIONS['TOTAL'],
    '0_9':      POP_IDADE['0_9'] * PROPORTIONS['0_14'],
    '10_19':    POP_IDADE['10_19'] * ( PROPORTIONS['0_14'] + PROPORTIONS['15_64'] ) / 2,
    '20_29':    POP_IDADE['20_29'] * PROPORTIONS['15_64'],
    '30_39':    POP_IDADE['30_39'] * PROPORTIONS['15_64'],
    '40_49':    POP_IDADE['40_49'] * PROPORTIONS['15_64'],
    '50_59':    POP_IDADE['50_59'] * PROPORTIONS['15_64'],
    '60_69':    POP_IDADE['60_69'] * ( PROPORTIONS['15_64'] + PROPORTIONS['65_plus'] ) / 2,
    '65_69':    POP_IDADE['65_69'] * PROPORTIONS['65_plus'],
    '70_79':    POP_IDADE['70_79'] * PROPORTIONS['65_plus'],
    '80_plus':  POP_IDADE['80_plus'] * PROPORTIONS['65_plus'],
}

POP_80 = POP_IDADE['80_plus']
POP_70 = POP_IDADE['70_79']
POP_65 = POP_IDADE['65_69']
#POP_REFORCO_65PLUS = POP_65 + POP_70 + POP_80
#POP_REFORCO_12_64 = POP_VACINAVEL - POP_REFORCO_65PLUS
POP_60 = POP_IDADE['60_69']
POP_50 = POP_IDADE['50_59']
POP_REFORCO_50PLUS = POP_80 + POP_70 + POP_60 + POP_50
POP_REFORCO_12_49 = POP_VACINAVEL_CONTINENTE - POP_REFORCO_50PLUS

POP_05_11 = POP_PT - POP_VACINAVEL_CONTINENTE - 436_118


TENDENCIA = ["⬈", "⬊", "⬌"]
GTE = '≥'
CASAS_DECIMAIS = 1

# Note: to debug the tweet content without publishing, use
# export TWITTER_CONSUMER_KEY_VAC=DEBUG
consumer_key = os.environ['TWITTER_CONSUMER_KEY_VAC']
if consumer_key != 'DEBUG':
    consumer_secret = os.environ['TWITTER_CONSUMER_SECRET_VAC']
    access_token = os.environ['TWITTER_ACCESS_TOKEN_VAC']
    access_token_secret = os.environ['TWITTER_ACCESS_SECRET_VAC']

# ---
# Helper methods
def autenticar_twitter():
    import tweepy
    # authentication of consumer key and secret
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    # authentication of access token and secret
    auth.set_access_token(access_token, access_token_secret)
    try:
        return tweepy.API(auth)
    except Exception as e:
        print("Erro ao autenticar", e)
        pass

def f(valor, plus=False):
    if valor is None:
        return "+?" if plus else ""
    valor = valor if type(valor) == int else round(float(valor), CASAS_DECIMAIS)
    r = format(valor, ",").replace(".","!").replace(",",".").replace("!",",")
    return f"+{r}" if plus and valor > 0 else r

def tweet_len(s):
    # quick hack to kind of count emojis as 2 chars. not 100% to spec
    return sum( (2 if ord(c)>0x2100 else 1) for c in s)

def t(valor):
    valor = valor if type(valor) == int else float(valor)
    return (
        TENDENCIA[0] if valor > 0
        else TENDENCIA[1] if valor < 0
        else TENDENCIA[2] if valor == 0 and len(TENDENCIA) > 2
        else ""
    )

def compose_tweets(DAYS_OFFSET=0):

    path = Path(__file__).resolve().parents[2]
    df = pd.read_csv(path / 'vacinas.csv',
        parse_dates=[0], index_col=[0], infer_datetime_format=True, skip_blank_lines=False, dayfirst=True
    )

    d = df.tail(DAYS_OFFSET + 1)[-1:]

    data = d.index.item().strftime("%d %b %Y")
    n_vacinados = int(d['pessoas_vacinadas_completamente'])
    n_vacinados_novas = int(d['pessoas_vacinadas_completamente_novas'])
    p_vacinados = 100.0 * n_vacinados / POP_PT
    p_vacinaveis = 100.0 * n_vacinados / POP_VACINAVEL

    n_inoculados = int(d['pessoas_inoculadas'])
    n_inoculados_novas = None # -int(d['pessoas_inoculadas_novas'])
    p_inoculados = 100.0 * n_inoculados / POP_PT
    n_inoculados_12mais = int(d['pessoas_inoculadas_12mais'])
    p_inoculaveis = 100.0 * n_inoculados_12mais / POP_VACINAVEL

    n_vacinados_c = int(d['pessoas_vacinadas_completamente_continente'])
    n_vacinados_c_novas = int(d['pessoas_vacinadas_completamente_continente_novas'])
    p_vacinados_c = 100.0 * n_vacinados_c / POP_PT_CONTINENTE

    n_iniciados_05_11 = int(d['vacinação_iniciada_05_11'])
    n_iniciados_05_11_novas = int(d['vacinação_iniciada_05_11_novas'])
    p_iniciados_05_11 = 100.0 * n_iniciados_05_11 / POP_05_11

    n_vacinas = int(d['vacinas'])
    n_vacinas_novas = int(d['vacinas_novas'])
    p_vacinas = 100.0 * n_vacinas / POP_PT

    n_reforco_80 = int(d['reforço_80mais'])
    n_reforco_80_novas = int(d['reforço_80mais_novas'])
    p_reforco_80 = 100.0 * n_reforco_80 / POP_80
    n_reforco_70 = int(d['reforço_70_79'])
    n_reforco_70_novas = int(d['reforço_70_79_novas'])
    p_reforco_70 = 100.0 * n_reforco_70 / POP_70
    #n_reforco_65 = int(d['reforço_65_69'])
    #n_reforco_65_novas = int(d['reforço_65_69_novas'])
    #p_reforco_65 = 100.0 * n_reforco_65 / POP_65
    has_60_novas = not math.isnan(d['reforço_60_69_novas'])
    n_reforco_60 = int(d['reforço_60_69'])
    n_reforco_60_novas = int(d['reforço_60_69_novas']) if has_60_novas else None
    p_reforco_60 = 100.0 * n_reforco_60 / POP_60
    n_reforco_50 = int(d['reforço_50_59'])
    n_reforco_50_novas = int(d['reforço_50_59_novas']) if has_60_novas else None
    p_reforco_50 = 100.0 * n_reforco_50 / POP_50

    n_reforco = int(d['pessoas_reforço'])
    n_reforco_novas = int(d['pessoas_reforço_novas'])
    p_reforco = 100.0 * n_reforco / POP_PT

    n_reforco_c = int(d['pessoas_reforço_continente'])
    n_reforco_c_novas = int(d['pessoas_reforço_continente_novas'])
    p_reforco_c = 100.0 * n_reforco_c / POP_PT_CONTINENTE

    n_reforco_c_resto = n_reforco_c - n_reforco_80 - n_reforco_70 - n_reforco_60 - n_reforco_50
    if has_60_novas:
        n_reforco_c_resto_novas = n_reforco_c_novas - n_reforco_80_novas - n_reforco_70_novas - n_reforco_60_novas - n_reforco_50_novas

        # relatorio 21-12-2021 não aumentou os valores por idade (mas adicionou percentagens) portanto a 22 o resto fica negativo
        if n_reforco_c_resto_novas < 0: n_reforco_c_resto_novas = None
    else:
        n_reforco_c_resto_novas = None
    
    p_reforco_c_resto = 100.0 * n_reforco_c_resto / POP_REFORCO_12_49

    n_gripe = int(d['pessoas_gripe'])
    n_gripe_novas = int(d['pessoas_gripe_novas'])
    p_gripe = 100.0 * n_gripe / POP_PT_CONTINENTE

    #n_vacinas_reforco = int(d['vacinas_reforço_e_gripe'])
    n_vacinas_reforco_novas = int(d['vacinas_reforço_e_gripe_novas'])
    #p_vacinas_reforco = int(n_vacinas_reforco / POP_REFORCO * 100_000)

    tweet_1 = (
        f"💉População 🇵🇹 nacional vacinada até {data}:"
        f"\n"
        f"\nInoculações: {GTE}{f(n_vacinas)} {f(n_vacinas_novas, True)} {GTE}{f(p_vacinas)}%"
        f"\nInoculados 5+: {GTE}{f(n_inoculados)} {f(n_inoculados_novas, True)} {GTE}{f(p_inoculados)}%"
        f"\nInoculados 12+: {GTE}{f(p_inoculaveis)}%"
        f"\nVacinados 5+: {GTE}{f(n_vacinados)} {f(n_vacinados_novas, True)} {GTE}{f(p_vacinados)}%"
        f"\nVacinados 12+: {GTE}{f(p_vacinaveis)}%"
        f"\nReforço: {GTE}{f(n_reforco)} {GTE}{f(n_reforco_novas, True)} {GTE}{f(p_reforco)}%"
        f"\n\n[1/3]"
    )
    tweet_2 = (
        f"💉População 🇵🇹 continente vacinada até {data}:"
        f"\n"
        f"\nIniciada 5-11: {f(n_iniciados_05_11)} {f(n_iniciados_05_11_novas, True)} {f(p_iniciados_05_11)}%"
        f"\nVacinados: {f(n_vacinados_c)} {f(n_vacinados_c_novas, True)} {f(p_vacinados_c)}%"
        f"\nReforço: {f(n_reforco_c)} {f(n_reforco_c_novas, True)} {f(p_reforco_c)}%"
        f"\n"
        f"\nGripe: {f(n_gripe)} {f(n_gripe_novas, True)} {f(p_gripe)}%"
        f"\n"
        f"\nInoculações diárias: {f(n_vacinas_reforco_novas, True)}"
        f"\n\n[2/3]"
    )
    tweet_3 = (
        f"💉População 🇵🇹 continente reforço por idade até {data}:"
        f"\n"
        f"\n80+: {f(n_reforco_80)} {f(n_reforco_80_novas, True)} {f(p_reforco_80)}%"
        f"\n70s: {f(n_reforco_70)} {f(n_reforco_70_novas, True)} {f(p_reforco_70)}%"
        f"\n60s: {f(n_reforco_60)} {f(n_reforco_60_novas, True)} {f(p_reforco_60)}%"
        f"\n50s: {f(n_reforco_50)} {f(n_reforco_50_novas, True)} {f(p_reforco_50)}%"
        f"\n12-49: {f(n_reforco_c_resto)} {f(n_reforco_c_resto_novas, True)} {f(p_reforco_c_resto)}%"
        f"\n\n[3/3]"
        f"\n\n➕Todos os dados em: {link_repo}"
    )
    return [tweet_1, tweet_2, tweet_3]


# ---
# Main
if __name__ == '__main__':

    DAYS_OFFSET = int(sys.argv[1]) if len(sys.argv) > 1 else 0

    tweets = compose_tweets(DAYS_OFFSET)
    if not tweets:
        print("No today data to tweet about")
        sys.exit()

    if consumer_key == 'DEBUG':
        for i, tweet in enumerate(tweets):
            print(f"Tweet {i+1} {tweet_len(tweet)} '''\n{tweet}\n'''")
        exit(0)

    api = autenticar_twitter()
    try:
        api.me()
    except Exception as ex:
        print(f"Erro na autenticação. Programa vai fechar: {ex}")
        exit(0)

    # Update status and create thread
    try:
        prev_tweet = None
        for i, tweet in enumerate(tweets):
            print(f"Tweet {i+1} {tweet_len(tweet)} '''\n{tweet}\n'''")
            prev_tweet = api.update_status(tweet, prev_tweet)
            prev_tweet = prev_tweet.id_str

    except Exception as e:
        print("Erro a enviar o tweet", e)
        pass

