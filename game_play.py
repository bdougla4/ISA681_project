from Exceptions.LettersNotInRackException import LettersNotInRackException
from Exceptions.UndefinedWordException import UndefinedWordException
from Exceptions.UserForfeitedException import UserForfeitedException
from PyDictionary import PyDictionary
from board.bag import LETTER_VALUES
from database.users import *
from database.moves import *
from database.games import *
from board.rack import *
from board.bag import *
import re


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
        logging.debug('calulating score for word: %s', word)
        word_score = 0
        for letter in word:
            word_score += LETTER_VALUES[letter.upper()]
        logging.info('final word score: %s', word_score)
        return word_score

    def handle_users_input(self, dbCur, gameId, currentUserId, word, position, col, row, rack):
        logging.debug("user's position: %s", position)
        logging.debug("user's word: %s", word)
        logging.debug("user's col: %s", col)
        logging.debug("user's row: %s", row)
        isWord = False
        wordScore = 0
        if ((re.match(r'(###)', word)) or (re.match(r'([A-Za-z]{2,7}|###)', word) and re.match(r'([rR][iI][gG][hH][tT])|([dD][oO][wW][nN])', position)
            and re.match(r'(1[0-5]|[1-9])', col) and re.match(r'(1[0-5]|[1-9])', row))):
            logging.info('position, word, col, ad row were formatted properly')
            logging.debug("checking if user word uses rack letters")
            if(word == '###'):
                logging.info("user skipped turn")
                return self.add_moves_and_update_game(dbCur, gameId, currentUserId, word, 
                wordScore, True, None, None, None, None, None)
            for letter in word:
                if letter.upper() not in rack:
                # TO-DO: uncomment when rack is in session
                # if letter.upper() not in rack.get_rack_str():
                    logging.warning("User's word: %s does not use the letters in the rack", word)
                    raise LettersNotInRackException("User's word: %s does not use the letters in the rack", word)
            if(word != "###"):
                isWord = self.is_word_in_dictionary(word)
                if isWord:
                    logging.info("user's word is a real word")
                    wordScore = self.calculate_word_score(word)
                    rackBag = self.replenish_rack(dbCur, rack, word, gameId)
                    rack = rackBag['rack']
                    bag = rackBag['bag']
                    return self.add_moves_and_update_game(dbCur, gameId, currentUserId, word, 
                    wordScore, False, col, row, position, rack, bag)
                else: 
                    logging.warning('position and / or word was not formatted properly')
                    raise UndefinedWordException("User's word: %s is undefined", word)

        # TO-DO:  DETERMINE IF WORD IS IN VALID POSITION

# TO-DO: add logging statements 
    def replenish_rack(dbCur, rack, word, gameId):
        bag = Games.get_active_game_by_id(dbCur, gameId)['bag']
        if bag == None: 
            raise UserForfeitedException("Other user forfeited during game play")
        bag = Bag.convert_string_bag_to_array(Bag, bag)
        rack = Rack.convert_string_rack_to_array(Rack, rack)
        Rack.remove_multiple_from_rack(Rack, word)
        bag = Rack.replenish_rack(Rack, bag)
        return {'rack': Rack.convert_array_to_string(Rack), 'bag':Bag.convert_array_to_string(bag)}

    def add_moves_and_update_game(dbCur, gameId, userId, word, wordScore, turnSkipped, col, row, position, rack, bag):
        # checking in case other user forfeited game in the meantime
        logging.debug("checking if game is still active")
        isGameStillActive = Games.get_active_game_by_id(dbCur, gameId)
        if isGameStillActive != None:
            logging.debug("game is still active. adding move and updating game")
            Moves.add_move(dbCur, gameId, userId, word, wordScore, turnSkipped, col, row, position)
            return Games.update_game_score(Games, dbCur, gameId, userId, wordScore, rack, bag)
        else: 
            raise UserForfeitedException("Other user forfeited during game play")

    def generate_continue_game_stats(dbCur, currentGame):
        # TO-DO: save these values globally per game to avoid calling it duing every turn
        currentUserNameTurn = Users.get_user_by_user_id(Users, dbCur, (currentGame['current_users_turn']))
        currentUserNameTurn = currentUserNameTurn['username']

        playerOne = Users.get_user_by_user_id(Users, dbCur, currentGame['user_id_one'])
        playerOneUserName = playerOne['username']
        playerOneScore = currentGame['user_id_one_score']

        playerTwo = Users.get_user_by_user_id(Users, dbCur, currentGame['user_id_two'])
        playerTwoUsername = playerTwo['username']
        playerTwoScore = currentGame['user_id_two_score']

        return {'currentUserNameTurn':currentUserNameTurn, 'playerOne':playerOneUserName, 'playerTwo':playerTwoUsername, 'playerOneScore':playerOneScore, 'playerTwoScore':playerTwoScore}

    # No longer needed due to session storage
    # def generate_new_game_stats(dbCur, newGame):
    #     currentUsersTurn = Users.get_user_by_user_id(Users, dbCur, (newGame['current_users_turn']))
    #     currentUsersTurn = currentUsersTurn['username']

    #     playerOne = Users.get_user_by_user_id(Users, dbCur, newGame['user_id_one'])
    #     playerOneUserName = playerOne['username']

    #     playerTwo = Users.get_user_by_user_id(Users, dbCur, newGame['user_id_two'])
    #     playerTwoUsername = playerTwo['username']
    #     return {'currentUsersTurn':currentUsersTurn, 'playerOne':playerOneUserName, 'playerTwo':playerTwoUsername, 'playerOneScore':0, 'playerTwoScore':0}

        
