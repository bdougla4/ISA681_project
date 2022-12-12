from board.bag import *
class Rack:
    """
    Creates each player's 'dock', or 'hand'. Allows players to add, remove and replenish the number of tiles in their hand.
    """
    def __init__(self, bag):
        #Initializes the player's rack/hand. Takes the bag from which the racks tiles will come as an argument.
        self.rack = []
        self.bag = bag
        self.initialize()

    def add_to_rack(self):
        #Takes a tile from the bag and adds it to the player's rack.
        self.rack.append(self.bag.take_from_bag())

    def initialize(self):
        #Adds the initial 7 tiles to the player's hand.
        for i in range(7):
            self.add_to_rack()

    def get_rack_str(self):
        #Displays the user's rack in string form.
        return ", ".join(str(item.get_letter()) for item in self.rack)

    def get_rack_arr(self):
        #Returns the rack as an array of tile instances
        return self.rack

    def remove_from_rack(self, tile):
        #Removes a tile from the rack (for example, when a tile is being played).
        self.rack.remove(tile)

    def get_rack_length(self):
        #Returns the number of tiles left in the rack.
        return len(self.rack)



# code above taken from https://github.com/fayrose/Scrabble


# TO-DO: add logging statements
    def convert_string_rack_to_array(self, rackString):
        self.rack = [word.strip().upper() for word in rackString.split(',')]
        return self.rack
    
    def convert_array_to_string(self):
        #Displays the user's rack in string form.
        return ", ".join(str(item) for item in self.rack)

    def remove_multiple_from_rack(self, tiles):
        for tile in tiles:
            self.rack.remove(tile.upper())
            #         try:
            # for tile in tiles:
            #     self.rack.remove(tile.upper())
            #                         logging.warning("User's word: %s does not use the letters in the rack", word)
            #         raise LettersNotInRackException("User's word: %s does not use the letters in the rack", word)
            

    def replenish_rack(self, bag):
        #Adds tiles to the rack after a turn such that the rack will have 7 tiles (assuming a proper number of tiles in the bag).
        while self.get_rack_length(self) < 7 and len(bag) > 0:
            self.add_letter_to_rack(self, bag)
        return bag


    def add_letter_to_rack(self, bag):
        letter = bag.pop()
        self.rack.append(letter)

