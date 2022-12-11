# basic code concept taken from https://github.com/fayrose/Scrabble

class Board:    
    def get_board():

        # board =	{
        #     "intialLine": "   |  " + "  |  ".join(str(item) for item in range(10)) + "  | " + "  | ".join(str(item) for item in range(10, 15)) + " | \n",
        #     "initialLine1": "   _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ \n"
        # }


        board = [["   " for i in range(15)] for j in range(32)]
        board[16][7] = " * "

        board = list(board)
        board[0] = "   |  " + "  |  ".join(str(item) for item in range(10)) + "  | " + "  | ".join(str(item) for item in range(10, 15)) + " | \n"
        board[1] = "   _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ \n"
        rowCounter = 0
        for i in range(2, 32):
            if i == 2:
                board[i] = str(rowCounter) + "  | " + " | ".join(str(item) for item in board[i]) + " |"
                rowCounter = rowCounter +1
            else:
                if (i % 2) != 0:
                    board[i] = "   |_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _| \n"
                else:
                    if i < 21:
                        board[i] = str(rowCounter) + "  | " + " | ".join(str(item) for item in board[i]) + " | \n"
                        rowCounter = rowCounter +1
                    if i >= 21:
                        board[i] = str(rowCounter) + " | " + " | ".join(str(item) for item in board[i]) + " | \n"
                        rowCounter = rowCounter +1
        board[31] = "   _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ \n"

        for i in range(len(board)):
            print(board[i])

        return board

    def place_word(board, word, row, col, direction):

        # print('')
        # print('')
        # print('')
        # for b in board:
        #     print(b)
        # print('')
        # print('')
        # print('')


        for i in range(1,32):
            if str(row) in board[i]:
                # print(board[i])
                rowFound = board[i].split('|')
                # print(rowFound)
                colFound = rowFound[int(col)+1]
                # print(colFound)
                # board[i]
                rowFound[int(col)+1] = "  " + word[0] + "  "
                rowFound = ('|').join(rowFound)
                board[i] = rowFound
        return board




        # print(board[int(row)])
        print('')
        print('')
        print('')
        print('')
        print('')

        #Allows you to play words, assuming that they have already been confirmed as valid.
        # direction = direction.lower()
        # word = word.upper()

        # #Places the word going rightwards
        # if direction.lower() == "right":
        #     for i in range(len(word)):
        #         # if board[location[0]][location[1]+i] != "   ":
        #         #     premium_spots.append((word[i], board[location[0]][location[1]+i]))
        #         board[row][col] = " " + word[i] + " "

        # #Places the word going downwards
        # elif direction.lower() == "down":
        #     for i in range(len(word)):
        #         # if board[location[0]][location[1]+i] != "   ":
        #         #     premium_spots.append((word[i], board[location[0]][location[1]+i]))
        #         board[col][row] = " " + word[i] + " "


