import random
import time


def display_board(board):
    """
    Displays the board as a grid
    """

    # Prints the initial column headings first
    print ("\n     1   2   3   4   5   6   7")
    print ("   -----------------------------")

    # Prints each row, one at a time
    for row in range(0,6):
        print ("   ", end = "")

        # For each row, prints the relevant column    
        for col in range(0,7):
            print ("| %s " % (board[row][col]), end="")

        print ("|\n   -----------------------------")

    return None


def copy_array(array):
    """
    Copies the contents of a two-dimensional array
    """
    return [array[x][:] for x in range(0,len(array))]


def alt_player(player):
    """
    Alternates the player
    """
    return "X" if player == "O" else "O"


def set_move(board, column, player):
    """
    Makes a move given a board, column and player
    """
    
    # Searches for a valid position in the given column, top down
    for row in range (5,-1,-1):
        if board[row][column] == " ":
            board[row][column] = player
            break

    return board


def player_move(board, player):
    """
    Takes input from a player and returns the relevant column
    (whereby the first column is 0, last is 6)
    """
    
    # Generates a set of free columns as strings (saves converting player input
    # into integer
    moveset = [str(x+1) for x in range(0,7) if board[0][x] == " "]
    column = "None"

    # Repeatedly asks for a move until a valid one is given
    while column not in moveset:
        column = input("Move: ")

    return int(column)-1


def npc_move(player, board, depth, debug=False):
    """
    Uses a minimax algorithm with alpha-beta pruning to determine a relatively
    optimal move, given the current board state and a depth to test to.
    debug set to True prints additional information about the search and scores
    """
    
    def alphabeta(player, board, depth, count, a, b, prune=0, node=0):
        """
        Alpha-beta search of game tree
        prune and node are variables used to count how many nodes are explored,
        and roughly how many nodes are pruned; only used for debugging
        """

        # Generates a set of valid moves in the board
        move_set = [x for x in range(0,7) if board[0][x] == " "]
        move_count = len(move_set)

        # v is the best score for the given branch of a tree
        v = -1e99 if count%2 == 0 else 1e99

        # the leaf score is calculated, as if there is a winning move, no
        # sub-trees are scored;
        node_score = score_board(board, player) * (depth+1)

        # Determines if a current node is a leaf or not
        if abs(node_score) > 1e9 or depth == 0 or move_count == 0:
            return node_score, prune, node+1
        else:
            # If not a leaf, recursively searches the rest of the tree
            for n in range (0,move_count):
                
                # Sets a move, and evaluates the new board
                test_board = set_move(copy_array(board), move_set[n], player if (count%2 == 0) else alt_player(player))

                # Recursively searches the game tree
                child, prune, node = alphabeta(player, test_board, depth-1, count+1, a, b, prune, node)

                # If count is an even number, then the minimax is maximising
                if (count%2 == 0):  
                    v = max(v, child)

                    # a represents a lower bound on the move that the maximising player can make
                    a = max(a, v)
                    
                else:
                    # in the other case, the minimax is minimising
                    v = min(v, child)
                    b = min(b, v)

                if a >= b:
                    # number of nodes pruned ~= number of moves left * number of valid moves^depth
                    # this is an upper bound, as lower depths may have less moves that are valid
                    prune += (move_count-(n+1))*(move_count**(depth-1))
                    break
                
            return v, prune, node
    # end of alphabeta

    # in this version, as the alpha-beta returns a score but no relevant move,
    # some work still needs to be done on the upper-most level to retain the move
    # that led to the score; an improvement in the Java implementation has the
    # alpha-beta method also return the move that led to the best score

    # generates the move set
    surface_move_set = [x for x in range(0,7) if board[0][x] == " "]
    surface_move_scores = [0 for x in surface_move_set]
    surface_move_count = len(surface_move_set)

    # initialises some variables for the search
    prune = 0
    node = 0
    v = -1e99
    a = -1e99
    b =  1e99

    # as no moves have been explored, defaults to best move of 0
    best_move = 0

    # this value is for debugging purposes only                    
    npc_timer = time.time()
    
    # This generates the final move scores, and sets them to 0 if no depths are looked at.
    if depth > 0:
        for n in range(0,surface_move_count):
            # searches for the optimal score using the alpha-beta from above;
            # score is a tuple of (best score, approx number of nodes pruned, number of nodes explored)
            score = alphabeta(player, set_move(copy_array(board), surface_move_set[n], player), depth-1, 1, a, b, prune, node)

            surface_move_scores[n] = score[0]
            if surface_move_scores[n] > v:
                best_move = surface_move_set[n]
            v = max(v, surface_move_scores[n])
            a = max(a, v)
            prune += score[1]
            node += score[2]
    else:
        # if depth = 0, then randomly selects a move from the list of valid ones
        best_move = surface_move_set[random.randint(0,surface_move_count-1)]
        
    # Debugging information
    if debug is True:
        print ("Possible moves: %s" % (surface_move_set))
        print ("Move scores: %s" % (surface_move_scores))
        #print ("Considered moves: %s" % (best_move_set))
        print ("Leaves pruned: %s" % (prune))
        print ("Leaves considered: %s" % (node))
        print ("Time Elapsed: %.3f" % (time.time()-npc_timer))

    return best_move


def score_board(board, player):
    """
    A scoring heuristic to value a given board, with the following system:
    10^0 for 1 piece + 3 spaces;
    10^2 for 2 pieces + 2 spaces;
    10^4 for 3 pieces + 1 space;
    10^10 for 4 pieces in a row (win).
    The points are deducted if the other player holds any of these positions
    """
    score = 0
    POINTS = [0,1,100,10000,1e10]
    chain = []

    # clearly, there is some serious code repetition here - would be better if that was made into a function
    # instead (again, the Java implementation handles this in a neater way)
    
    # Checks for horizontal chains first.
    for row in range(0,6):
        for col in range(0,4):
            chain = board[row][col:col+4]
            if not ("X" in chain and "O" in chain):
                score = score+POINTS[chain.count(player)] if player in chain else score-POINTS[chain.count(alt_player(player))]

    # Checks for vertical chains.
    for row in range(0,3):
        for col in range(0,7):
            chain = [board[row+x][col] for x in range(0,4)]
            if not ("X" in chain and "O" in chain):
                score = score+POINTS[chain.count(player)] if player in chain else score-POINTS[chain.count(alt_player(player))]

    # Checks for diaganols from top left to bottom right.
    for row in range(0,3):
        for col in range(0,4):
            chain = [board[row+x][col+x] for x in range(0,4)]
            if not ("X" in chain and "O" in chain):
                score = score+POINTS[chain.count(player)] if player in chain else score-POINTS[chain.count(alt_player(player))]

    # Checks for diaganols from top right to bottom left.
    for row in range(0,3):
        for col in range(3,7):
            chain = [board[row+x][col-x] for x in range(0,4)]
            if not ("X" in chain and "O" in chain):
                score = score+POINTS[chain.count(player)] if player in chain else score-POINTS[chain.count(alt_player(player))]

    return score


def get_option(title, contents, start_number=1):
    """
    Takes inputs as a title and a list of options, and obtains a user input.
    Always returns an integer.
    start_number represents what value to start the menu options at
    """
    print ("\n= - = - = %s = - = - =\n" % (title))

    # This displays the entries, each with their own row and number.
    for entry in range(0,len(contents)):
        print (" - %s: %s" % (entry+start_number, contents[entry]))

    # This set lists the possible numbers for the user to choose from.
    menu_set = [str(x+start_number) for x in range (0,len(contents))]
    user_option = "None"

    while user_option not in menu_set:
        user_option = input("Number: ")

    return int(user_option)


# The main menu will greet the player upon opening the program.
MAIN_MENU_TITLE = "Connect Four Main Menu"
MAIN_MENU_CONTENTS = [
    "Two Player: Play against another human player.",
    "One Player: Play against the computer, choosing your difficulty setting.",
    "Zero Player: Watch the computer play against itself, choosing both difficulty settings."
    ]

# The AI_MENU_TITLE has an open ending so that it can be changed easily.
AI_MENU_TITLE = "Connect Four Difficulty Menu for player "
AI_NAMES = ["Random","Very Easy","Easy","Regular","Better than Regular","Hard","Harder","Hardest"]
AI_MENU_CONTENTS = [
    "%s" % (AI_NAMES[0]),
    "%s" % (AI_NAMES[1]),
    "%s" % (AI_NAMES[2]),
    "%s" % (AI_NAMES[3]),
    "%s" % (AI_NAMES[4]),
    "%s" % (AI_NAMES[5]),
    "%s" % (AI_NAMES[6]),
    "%s" % (AI_NAMES[7])
    ]

if __name__ == "__main__":

    print ("\n\n========================| Connect Four v3 by Jolyon Shah |========================\n\n")

    replay = True
    reset = True

    while replay is True:

        # Initialises some starting variables that reset for every game.
        board = [[" " for y in range(0,7)] for x in range(0,6)]
        player = "O" if random.randint(0,1) == 0 else "X"
        winner = 0

        # Resets the options if requested, or if the first time.
        if reset is True:
            player_scores = [0,0]
            player_one = "Human Player One"
            player_two = "Human Player Two"
            game_mode = get_option(MAIN_MENU_TITLE, MAIN_MENU_CONTENTS, 1)

            # This sets up the names to be displayed, as well as the difficulties for the computer players.
            if game_mode == 1:
                player_one = input("Please enter Player One's (X) name: ") + " (X)"
                player_two = input("Please enter Player Two's (O) name: ") + " (O)"

            elif game_mode == 2:
                player_one = input("Please enter Player One's (X) name: ") + " (X)"
                computer_two = get_option(AI_MENU_TITLE+"two", AI_MENU_CONTENTS, 0)
                player_two = AI_NAMES[computer_two] + " (O)"

            elif game_mode == 3:
                computer_one = get_option(AI_MENU_TITLE+"one", AI_MENU_CONTENTS, 0)
                player_one = AI_NAMES[computer_one] + " (X)"
                computer_two = get_option(AI_MENU_TITLE+"two", AI_MENU_CONTENTS, 0)
                player_two = AI_NAMES[computer_two] + " (O)"

            # A few extra options.
            sleep = input("Would you like an added delay of one second between the computer's moves? Y/N ").lower().startswith("y")
            debug = input("Would you like to enable debug mode? Y/N ").lower().startswith("y")

        # Displays the board for the first time.
        print ("\n======================================")
        display_board(board)
        print ("\n======================================")

        timer = time.time()
        while winner < 1e9:
            
            # Alternates the player and displays the current player's turn.
            player = alt_player(player)
            print ("%s's turn!" % (player_one if player == "X" else player_two))

            # Performs a move for the current player. Gamemodes 1 and 2 have a human as Xs, and gamemode 1 has a human as Os.
            if player == "X":
                if game_mode in [1,2]:
                    move = player_move(board, player)
                    board = set_move(board, move, player)
                else:
                    if sleep is True:
                        time.sleep(1)
                    move = npc_move(player, board, computer_one, debug)
                    board = set_move(board, move, player)

            else:
                if game_mode == 1:
                    move = player_move(board, player)
                    board = set_move(board, move, player)
                else:
                    if sleep is True:
                        time.sleep(1)
                    move = npc_move(player, board, computer_two, debug)
                    board = set_move(board, move, player)

            # Outputs the move that was just made.
            print ("======================================\n")
            print ("%s moved to column %s." % (player_one if player == "X" else player_two, move+1))
            display_board(board)
            print ("\n======================================")

            winner = score_board(board, player)

            # This checks for draws.
            if len([x for x in range(0,6) if " " not in board[x]]) == 6:
                print ("Stalemate! Nobody wins!")
                break

        # This next section handles the winner.
        if winner > 1e9:
            if player == "X":
                player_scores[0] += 1
                print ("%s wins! Well done!" % (player_one))
                print ("Better luck next time, %s" % (player_two))
            else:
                player_scores[1] += 1
                print ("%s wins! Well done!" % (player_two))
                print ("Better luck next time, %s" % (player_one))

        print ("\nScores:")
        print ("%s: %s wins" % (player_one, player_scores[0]))
        print ("%s: %s wins" % (player_two, player_scores[1]))

        print ("Time elapsed: %.3f" % (time.time()-timer))

        replay = input("Would you like to play again? Y/N ").lower().startswith("y")

        if replay is True:
            reset = input("Would you like to reset scores and settings? Y/N ").lower().startswith("y")


    print ("\n\n=-=-=-=-=-=-=-=-=-=-=-= Thank you for playing! =-=-=-=-=-=-=-=-=-=-=-=\n\n")
