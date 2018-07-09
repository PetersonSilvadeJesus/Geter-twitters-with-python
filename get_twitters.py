from twython import Twython
import psycopg2
import json
import sys
import datetime
import unicodedata
import re
import time

def removerAcentosECaracteresEspeciais(palavra):

    # Unicode normalize transforma um caracter em seu equivalente em latin.
    nfkd = unicodedata.normalize('NFKD', palavra)
    palavraSemAcento = u"".join([c for c in nfkd if not unicodedata.combining(c)])

    # Usa expressão regular para retornar a palavra apenas com números, letras e espaço
    return re.sub('[^a-zA-Z0-9 \\\]', '', palavraSemAcento)



def clear(words):
    # percorre a lista retirando o indices que possui '@' e 'http' no conteúdo
    newList = []
    for element in words:
        flag = True
        #
        # Ideia pra tirar todos os hastags
        #
        if '#' in element:
            flag = False
        elif '@' in element:
            flag = False
            #words.remove(element)
        elif 'http' in element:
            flag = False

    # remove o indice que possui RT no conteúdo
        if 'RT' == element:
            flag = False

        if flag:
            newList.append(element)

    text = ' '.join(newList)                              # Junta novamente o texto com espaços
    text = removerAcentosECaracteresEspeciais(text)     # Remove Acentos e caracters especiais

    return text



def redefinirWords(text, chave):
    # Pega as Stop Words e coloca em 'stopWords'
    f = open("stopwords.txt", 'r')
    stopWords = f.read().splitlines()
    f.close()

    # Retira as stop Words do texto
    text = text.split()

    newList = []

    for esta in text:
        flag = True
        # Retira as stop Words do texto
        for element2 in stopWords:
            if(esta == element2):
                flag = False
                break

        if len(esta) < 4:
            flag = False

        # Remove a palavra se possuir número no meio
        for numbers in range(0, 10):
            if str(numbers) in esta:
                flag = False
                break

        # Tirar da lista de palavras encontradas, a(s) palavra(s) que faz(em) parte da pesquisa
        for este in chave.split():
            if (este in esta):
                flag = False
                break
		
       	if flag:
        	newList.append(esta)

    return newList


def save(twitter, data_param, con, cur):
    all_tweets = []
    data = twitter.search(q=data_param, lang='en', count=100)
    all_tweets = data['statuses']

    insercao = []
    cur.execute('SELECT word FROM keyword WHERE word = %s', (data_param,))
    if cur.fetchone() is None:
        cur.execute('insert into keyword (word, status) values (%s, %s) ', (data_param, True))
    cur.execute('UPDATE keyword set status = %s WHERE word = %s ', (True, data_param))

    for tweets in all_tweets:
        # VARs
        id = tweets['id']
        text = tweets['text']
        source = tweets['source']
        created_at = tweets['created_at']
        retweet_count = tweets['retweet_count']
        # print(text)
        # USER
        id_user = tweets['user']['id']
        created_at_user = tweets['user']['created_at']
        statuses_count = tweets['user']['statuses_count']
        followers_count = tweets['user']['followers_count']
        profile_image_url = tweets['user']['profile_image_url']
        screen_name = tweets['user']['screen_name']
        description = tweets['user']['description']
        friends_count = tweets['user']['friends_count']
        location = tweets['user']['location']
        name = tweets['user']['name']
        listed_count = tweets['user']['listed_count']

        # HASHTAG
        text_hashtag = []
        for hashtags in tweets['entities']['hashtags']:
            text_hashtag.append(hashtags['text'])

        # Busca todos os USERs que possuem o mesmo 'id'
        cur.execute('select id from user_twitter WHERE id = %s', (id_user,))
        if cur.fetchone() is None:
            # Inseri os USERs no banco
            cur.execute('insert into user_twitter (id, name, created_at, statuses_count, followers_count, profile_image_url, screen_name, description, friends_count, location, listed_count) '
                        'values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) ', (id_user, name, created_at_user, statuses_count, followers_count, profile_image_url, screen_name, description, friends_count, location, listed_count))

        # Verifica se não possui outro Tweet igual
        cur.execute('SELECT id FROM tweet WHERE id = %s', (id,))
        if cur.fetchone() is None:
            cur.execute('insert into tweet (id, source, text, created_at, retweet_count, user_id) values (%s, %s, %s, %s, %s, %s)',(id, source, text, created_at, retweet_count, id_user))

            for hash in text_hashtag:
                cur.execute('insert into hashtag (text, tweet_id) values (%s, %s)', (hash, id))

        words = list(map(lambda x: x.lower(), text.split()))
        words = redefinirWords(clear(words), data_param)

        for element in words:
            insercao.append(element)

        con.commit()
        print("Key: " + data_param + " - Twitters successfully saved!!! \n  New Words: " + str(len(words)))

    return insercao



def twittar():
    app_key = ""
    app_secret = ""
    token_key = ""
    token_secret = ""

    twitter = Twython(app_key, app_secret, token_key, token_secret)

    lista = []

    try:
        con = psycopg2.connect("host='localhost' dbname='' user='' password=''")
        cur = con.cursor()
        twite = list()

        # Ler do banco as palavras com statusigual a 0
        cur.execute('select * from keyword WHERE status = FALSE')

        count = cur.fetchall()

        if(len(count) == 0):
            print("No words found in the database!")
            newWord = input("Enter a word as a parameter:")
            if(newWord == ""):
                print("No words were entered. Try again!")
                return 0
            else:
                twite.append(newWord)

        con.commit()

        for element in count:
            twite.append(element[0])

        for twi in twite:
            lista = save(twitter, twi, con, cur)

            for ele in lista:
                twite.append(ele)
                cur.execute('select * from keyword WHERE word = %s', (ele,))
                if cur.fetchone() is None:
                    cur.execute('insert into keyword (word, status) values (%s, %s) ', (ele, False))

                con.commit()

        con.close()


    except Exception as e:
        # Verificar se a mensagem de erro é a mesma de limite de requisições
        # twittar()
        if("Rate limit exceeded" in str(e)):
            print("Wait a moment...")
            time.sleep(300)                             # Espera 5 minutos
            twittar()                                   # Twitta novamente
        else:
            print(e)
            print("Please, contact the support to solve your problem. Thanks!!!")

    return 0


################## MAIN ##################
twittar()
