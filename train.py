import re
import pandas as pd

emotion_words_path = r"C:\Users\Dell\OneDrive - University of Hertfordshire\Lexicon Based Approach\Bing.csv"
modifier_words_path = r"C:\Users\Dell\OneDrive - University of Hertfordshire\Lexicon Based Approach\Afinn.csv"

class SentimentAnalyzer:
    def __init__(self, emotion_words_path, modifier_words_path):
        self.lexicon = self.load_data(emotion_words_path)
        self.modifiers, self.negations = self.load_modifier_words(modifier_words_path)


    def load_data(self, path): #returns a dictionary with word and sentiment
        df=pd.read_csv(path, encoding='latin1')
        return dict(zip(df['word'], df['sentiment']))

# Loads the dataset with weights
    def load_modifier_words(self, path): #Modifiers and negations are separated and are given weights accordingly
        modifiers = {}
        negations =set()
        df = pd.read_csv(path, encoding='latin1')

        for _, row in df.iterrows():
            if row['weight'] > 0:
                modifiers[row['word']] = row['weight']
            else:
                negations.add(row['word'])
        return modifiers, negations


    def _preprocess(self, text): #Turns the given text into lowercase and tokenizes it
        text = text.lower()
        return re.findall(r"\w+(?:'\w+)?", text)

    def analyze(self, text):

        words = self._preprocess(text) #returns "neutral" when nothing is passed
        if not words:
            return 0.0, "neutral"

        pos, neg = 0, 0
        current_weight = 1


        for word in words:
            sentiment = self.lexicon.get(word) #checks for the word passed by player in lexicon

            if sentiment == "positive":
                pos += current_weight
                current_weight = 1  # Reset after applying
            elif sentiment == "negative":
                neg += current_weight
                current_weight = 1
            elif word in self.modifiers:
                current_weight *= self.modifiers[word] #gets the weight of modifiers from the dictionary
            elif word in self.negations:
                current_weight *= -1 #weight of negations is -1

        score = (pos - neg) / len(words) #
        sentiment = "positive" if score > 0.1 else "negative" if score < -0.1 else "neutral"
        return score, sentiment


if __name__ == "__main__":

    analyzer = SentimentAnalyzer(
        emotion_words_path=r"C:\Users\Dell\OneDrive - University of Hertfordshire\Lexicon Based Approach\Bing.csv",
        modifier_words_path=r"C:\Users\Dell\OneDrive - University of Hertfordshire\Lexicon Based Approach\Afinn.csv"
    )

    # Test analysis
    text = "I want to destroy the world"
    score, sentiment = analyzer.analyze(text)
    print(f"Text: '{text}'")
    print(f"Score: {score:.2f} | Sentiment: {sentiment}")



