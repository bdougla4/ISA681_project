    
class Board:    
    def get_board():
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