from PyDictionary import PyDictionary
from board.bag import LETTER_VALUES

# TO-DO: ensure log injection can't happen 
class GamePlay:

    # checks if word is a real English word
    def is_word_in_dictionary(word):
        dictionary = PyDictionary()
        try:
            print('Getting definition for word: ' + word)
            definition = dictionary.meaning(word, disable_errors=True)
            
            if(definition == None):
                print('definition was not found')
                return False
            print('definition was found')
            return True
        except Exception as ex:
            print(f"Something went wrong when accessing dictionary: '{ex}'")


    # checks if the user's position is "right" or "down"
    def is_position_allowed(position): 
        print("checking is user's position is allowed: " + position)
        if ((position.upper() == "RIGHT" or position.upper() == "DOWN")) :
            print("user's position input is acceptable")
            return True
        else:
            print("user's position input is not acceptable")
            return False

    
    # calculate the word's score based on the LETTER_VALUE provided in the Bag class
    # TO-DO: add special values?
    def calculate_word_score(word):
        print("calulating score for word: " + word)
        word_score = 0
        for letter in word:
            word_score += LETTER_VALUES[letter.upper()]
        print("final word score: " + str(word_score))
        return word_score
        
