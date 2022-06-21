import fasttext.FastText as ftt
from .preprocess_text import PreproccessText


class TextClassifier:
    def __init__(self, model: ftt._FastText = None, threshold: float = 0.61, preprocess: PreproccessText = None):
        self.model: ftt._FastText = model if model is not None else ftt.load_model(
            "./model.bin")
        self.threshold: float = threshold
        self.preprocess: PreproccessText = PreproccessText(
        ).fit if preprocess is None or not isinstance(preprocess, PreproccessText) else preprocess.fit

    def predict(self, corpus: str) -> int:
        corpus = self.preprocess(corpus)
        result = self.model.predict(corpus)
        if result[1][0] >= self.threshold:
            return int(result[0][0].split("__")[-1])
        return -1
