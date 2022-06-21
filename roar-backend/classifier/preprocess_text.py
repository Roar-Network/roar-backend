from string import punctuation
from contraction import fix
import nltk as text



class PreproccessText:
    def __init__(self):
        self.stop_words = set(text.corpus.stopwords.words(
            "english") + list(punctuation))
        self.lemm = text.stem.WordNetLemmatizer().lemmatize

    def fit(self, corpus):
        # ? normalization of str to lower case
        corpus = corpus.lower()
        # ? expand contraction like can't -> cannot
        corpus = fix(corpus)

        # ? tokenize
        word_tokens = text.tokenize.word_tokenize(corpus)
        # ? lemmatize
        word_tokens = [self.lemm(w) for w in word_tokens]
        # ? remove stopwords & punct &
        filtered_sentence = [
            self.lemm(w) for w in word_tokens if w.isalpha and not w in self.stop_words]

        return " ".join(filtered_sentence)
