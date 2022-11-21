from PyDictionary import PyDictionary

dictionary=PyDictionary()

def isWordInDictionary(word):
    try:
        print('Getting definition for word: ' + word)
        definition = dictionary.meaning(word, disable_errors=True)
        print(definition)

        if(definition == None):
            print('definition was not found')
            return False
        print('definition was found')
        return True
    except Exception as ex:
        print(f"Something went wrong when accessing dictionary: '{ex}'")
