import emojis
import pickle
import navec
import pymorphy2 as pm
import numpy as np
import os


from tqdm import tqdm
from googletrans import Translator


alpha = set('йцукенгшщзхъфывапролджэячсмитьбюё')


def preprocess_tags(debug_ok=False, debug_fail=False, debug_process=True, debug_result=True) -> None:

    vector_path = 'navec_hudlit_v1_12B_500K_300d_100q.tar'
    emb = navec.Navec.load(vector_path)

    tags = emojis.db.get_emoji_aliases()

    def process_tag(tag):
        text = ' '.join(tag[1:-1].split('_'))

        translator = Translator()
        text = translator.translate(text, dest='ru').text.lower()

        common_vector = np.zeros((1, 300))
        size = 0
        words = []
        for word in text.split():
            word = ''.join([symb for symb in word if symb in alpha])
            if word in emb:
                words.append(word)
                common_vector += emb[word]
                size += 1
        text = ' '.join(words)
    
        emoji = emojis.db.get_emoji_by_alias(tag[1:-1]).emoji
        if size == 0:
            if debug_fail:
                print(f"{emoji}     {tag=},             {text=}             FAILED")
            return None

        if debug_ok:
            print(f"{emoji}     {tag=},             {text=}             OK")

        common_vector /= size
        return common_vector

    success = 0
    fail = 0

    tags_process = tags
    if debug_process:
        tags_process = tqdm(tags)

    log_vocab = dict()
    for tag in tags_process:
        res = process_tag(tag)
        if res is None:
            fail += 1
        else:
            success += 1
            log_vocab[tuple(list(res[0]))] = emojis.db.get_emoji_by_alias(tag[1:-1]).emoji

    if debug_result:
        print(f" {success = },\n {fail = }")

    with open('encoded_emojis.pickle', 'wb') as file:
        pickle.dump(log_vocab, file)



def text_to_emoji(text):

    text = ''.join([symb for symb in text.lower() if symb in alpha or symb == ' '])

    print(text)
    if not os.path.exists('encoded_emojis.pickle'):
        preprocess_tags()



    

print(text_to_emoji('Привет, дорогая, смеюсь с тебя, я дома, люблю всех ребят на свете'))