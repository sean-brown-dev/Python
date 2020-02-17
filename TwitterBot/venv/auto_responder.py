import nltk
from nltk.corpus import stopwords, twitter_samples, webtext
import numpy
import random
import string
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import re
from pathlib import Path
from datetime import datetime

GREETING_INPUTS = [
"hello", "hi", "greetings", "sup", "what's up", "hey", "yo", "oi", "wuddup", "ello", "sup dude", "hey man", "hey there",
"hello there", "hi there", "how you doing"]
GREETING_RESPONSES = ["hi", "hey", "*nods*", "hi there", "hello", "I am glad you are talking to me", "yo", "oi",
                      "wuddup", "ello", "sup dude", "hey thar", "*tips cap*", "aloha"]
NOT_SURE_RESPONSES = ["I don't know what to say to that.", "No idea.", "What?", "What're you talkin' 'bout Willis?",
                      "I don't understand the words coming out of your mouth.", "Try rephrasing that.",
                      "Sorry, I am but a simple bot.", "I got no clue what you just said to me.",
                      "Ask @realDonaldTrump."]
NO_POLITICS_RESPONSE = ["I don't like to talk about politics.", "I like to stick to sports.", "You are MAGA'n me mad with all this political talk."]


def get_greeting(sentence):
    for word in sentence.split():
        if word.lower() in GREETING_INPUTS:
            return random.choice(GREETING_RESPONSES)


def clean_text(regex_pattern, dirty_text):
    return re.sub(regex_pattern, '', dirty_text)


def clean_coca_text(dirty_text):
    pattern = re.compile(r"(##\d+ ABSTRACT \.) |(##\d+ Section : )|(##\d+ )|((<p>)|( @){10})")
    return clean_text(pattern, dirty_text)


def clean_citation_numbers(dirty_text):
    pattern = re.compile(r"\[\d+\]")
    return clean_text(pattern, dirty_text)


def clean_tweet(dirty_text):
    pattern = re.compile(r"(?<=^|(?<=[^a-zA-Z0-9-_\.]))@([A-Za-z]+[A-Za-z0-9-_]+)")
    cleaned_text = clean_text(pattern, dirty_text)

    pattern = re.compile(r"(?<=^|(?<=[^a-zA-Z0-9-_\.]))#([A-Za-z]+[A-Za-z0-9-_]+)")
    cleaned_text = clean_text(pattern, cleaned_text).casefold().strip()

    return cleaned_text


def get_hockey_string():
    with open('./corpus/ovechkin_greatest_scorer.txt',
              'r') as hockey_corpus:
        casefolded_hockey_text = clean_citation_numbers(hockey_corpus.read().casefold())

    return casefolded_hockey_text


def get_corpus_string():
    for path in Path('./corpus/COCA').glob("*.txt"):
        with open(str(path), 'r') as coca_file:
            raw_casefolded_text = clean_coca_text(coca_file.read().casefold())

    return raw_casefolded_text


def get_tweet_data():
    tweet_docs = ([(clean_tweet(t), "pos") for t in twitter_samples.strings("positive_tweets.json")] +
                 [(clean_tweet(t), "neg") for t in twitter_samples.strings("negative_tweets.json")])

    tweets_as_text = ''.join([tweet[0] for tweet in tweet_docs]).casefold()
    return tweets_as_text


def get_webtext_data():
    return ''.join([webtext.raw(file_id) for file_id in webtext.fileids()]).casefold()


class ResponseGenerator:
    def __init__(self):
        nltk.download('punkt')
        nltk.download('wordnet')
        nltk.download('stopwords')
        nltk.download('twitter_samples')
        nltk.download('webtext')

        # Initialized in learn_corpus()
        self.sent_tokens = None
        self.word_tokens = None
        self.lemmer = None
        self.remove_punct_dict = None
        self.learn_corpus()

    def learn_corpus(self):
        raw_casefolded_text = get_corpus_string()
        self.sent_tokens = nltk.sent_tokenize(raw_casefolded_text)
        self.word_tokens = nltk.word_tokenize(raw_casefolded_text)

        hockey_casefolded_text = get_hockey_string()
        self.sent_tokens.extend(nltk.sent_tokenize(hockey_casefolded_text))
        self.word_tokens.extend(nltk.word_tokenize(hockey_casefolded_text))

        tweet_casefolded_text = get_tweet_data()
        self.sent_tokens.extend(nltk.sent_tokenize(tweet_casefolded_text))
        self.word_tokens.extend(nltk.word_tokenize(tweet_casefolded_text))

        webtext_casefolded = get_webtext_data()
        self.sent_tokens.extend(nltk.sent_tokenize(webtext_casefolded))
        self.word_tokens.extend(nltk.word_tokenize(webtext_casefolded))

        self.lemmer = nltk.stem.WordNetLemmatizer()
        self.remove_punct_dict = dict((ord(punct), None) for punct in string.punctuation)

    def get_lem_tokens(self, tokens):
        return [self.lemmer.lemmatize(token) for token in tokens if token not in stopwords.words('english')]

    def get_normalized_tokens(self, text):
        return self.get_lem_tokens(nltk.word_tokenize(text.casefold().translate(self.remove_punct_dict)))

    def get_bot_response(self, user_input):
        print(f"[{datetime.now()}] >> Getting bot response for: '{user_input}'")

        user_input = clean_tweet(user_input)

        if user_input in GREETING_INPUTS:
            robo_response = random.choice(GREETING_RESPONSES)
        elif "trump" in user_input.casefold():
            robo_response = random.choice(NO_POLITICS_RESPONSE)
        else:
            self.sent_tokens.extend(nltk.sent_tokenize(user_input))
            self.word_tokens.extend(nltk.word_tokenize(user_input))

            tf_id_vector = TfidfVectorizer(tokenizer=self.get_normalized_tokens, stop_words='english')
            doc_matrix = tf_id_vector.fit_transform(self.sent_tokens)

            similarities = cosine_similarity(doc_matrix[-1], doc_matrix)
            idx = similarities.argsort()[0][-2]

            flat = similarities.flatten()
            flat.sort()
            req_tfidf = flat[-2]


            if req_tfidf != 0:
                robo_response = self.sent_tokens[idx]
            else:
                robo_response = random.choice(NOT_SURE_RESPONSES)

        print(f"[{datetime.now()}] >> Got response: '{robo_response}'")
        return robo_response
