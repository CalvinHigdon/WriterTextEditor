class WordTools:
    def __init__(self):
        file = open("data/words_alpha.txt", "r")
        self.wordPruneArray = file.read().splitlines()
        # self.wordPruneArray = [word.rstrip() for word in self.wordPruneArray]

    def get_intersection(self, wordList):
        wordList.sort()
        pruned = []
        j = 0
        for word in wordList:
            if word.count(" ") > 0:
                continue
            while (word > self.wordPruneArray[j]):
                j += 1
                if j >= len(self.wordPruneArray):
                    break
            if (word == self.wordPruneArray[j]):
                pruned.append(word)
                continue
        return pruned