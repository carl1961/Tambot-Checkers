import random


# represents a square in the board.
class Square:
    def __init__(self, is_black, piece, board, x, y):
        self.isBlack = is_black
        self.piece = piece  # 1 is p1, 2 is p2, 3 is p1king, 4 is p2king, 0 is empty
        self.board = board
        self.x = x
        self.y = y
        self.jump_simulated = False  # to prevent infinite recursion in chained jumps with kings

    def __repr__(self):
        return "(" + chr(self.x + 96).capitalize() + "," + str(self.y) + ")"

    def symbol(self):
        if self.piece != 0:
            return str(self.piece)
        else:
            if self.isBlack:
                return " "
            else:
                return " "

    def get_diagonals(self, player):
        squares = []
        relative_coordinates = []
        if player == 1 or player > 2:
            relative_coordinates.extend([(-1, -1), (1, -1)])
        if player >= 2:
            relative_coordinates.extend([(1, 1), (-1, 1)])

        for coordinate in relative_coordinates:
            x = self.x + coordinate[0]
            y = self.y + coordinate[1]
            diagonal = self.board.get(x, y)
            if diagonal is not None:
                squares.append(diagonal)
        return squares

    def get_next_one_over(self, over_square):
        return self.board.get(over_square.x + (over_square.x - self.x), over_square.y + (over_square.y - self.y))


class Board:
    def __init__(self):
        self.squares = []  # 8x8 list of Square objects
        self.move_history = []  # a list containing lists of moves that have been executed.
        self.moves_without_jump = 0
        self.winner = 0

		# add all squares into the board and initialize them to be like they should in the beginninf of the game
        for i in range(8):
            row = []
            for j in range(8):
                append_square = Square(True, 0, self, j+1, i+1)
                if i % 2 == 0:
                    if j % 2 == 0:
                        append_square.isBlack = False
                else:
                    if j % 2 != 0:
                        append_square.isBlack = False
                if append_square.isBlack:
                    if i < 3:
                        append_square.piece = 2
                    elif i > 4:
                        append_square.piece = 1
                row.append(append_square)
            self.squares.append(row)

    def get(self, x, y):
        if 1 <= x <= 8 and 1 <= y <= 8:
            return self.squares[y-1][x-1]
        else:
            return None

	# returns a string representing the board
    def board_str(self):
        append_str = ""
        for row in self.squares:
            append_str += str(row[0].y) + " "
            for square in row:
                append_str += square.symbol() + " "
            append_str += "\n"
        append_str += "  A B C D E F G H\n"
        return append_str

	# (used for robot) compares binary 8x8 list of integers to current internal board state 
    def is_up_to_date(self, board_data):
        for x in range(1, 9):
            for y in range(1, 9):
                square = self.get(x, y)
                if square.isBlack:
                    bit = board_data[y-1][x-1]
                    if (square.piece != 0 and bit == 0) or (square.piece == 0 and bit == 1):
                        return False
        return True

	# (used for robot) returns false, until a legal move is detected from input
    def process_input(self, board_data, player):
        if not self.is_up_to_date(board_data):
            return self.execute_difference_move(self.find_differences(board_data, player), player)
        else:
            return False

	# (used for robot)
    def find_differences(self, board_data, player):
        differences = []
        for x in range(1, 9):
            for y in range(1, 9):
                square = self.get(x, y)
                if square.isBlack:
                    piece = square.piece
                    bit = board_data[y - 1][x - 1]
                    if bit == 1 and piece == 0:
                        differences.append({'x': x, 'y': y, 'type': 3})  # player end square
                    elif bit == 0 and self.is_same_team(piece, player):
                        differences.append({'x': x, 'y': y, 'type': 1})  # player move start square
                    elif bit == 0 and piece != 0:
                        differences.append({'x': x, 'y': y, 'type': 2})  # eaten piece square
        return differences

	# (used for robot)
    def execute_difference_move(self, differences, player):
        starts = list(filter(lambda diff: diff['type'] == 1, differences))
        if len(starts) != 1:
            return False
        start = starts[0]
        player_piece = self.get(start['x'], start['y']).piece

        if not self.is_same_team(player_piece, player):
            return False
        possible_moves = self.possible_moves(start['x'], start['y'])
        for moves in possible_moves:
            found_legal_move = True
            self.execute_moves(moves)
            for difference in differences:
                square = self.get(difference['x'], difference['y'])
                if (difference['type'] == 2 and square.piece != 0) or \
                        (difference['type'] == 3 and not self.is_same_team(square.piece, player)):
                    found_legal_move = False
                    break
            if found_legal_move:
                return True
            else:
                self.undo_moves()
        return False

    @staticmethod
    def is_same_team(piece1, piece2):
        if piece1 == 0 or piece2 == 0:
            return False
        elif piece1 % 2 == piece2 % 2:
            return True
        else:
            return False

	# returns all possible moves for a piece in certain coordinates
    def possible_moves(self, x, y, is_chain=False, chain_piece=0):
        moves_list = []
        square = self.get(x, y)
        if is_chain:
            p = chain_piece
        else:
            p = square.piece

        if p != 0:
            for target_square in square.get_diagonals(p):
                if target_square.piece == 0 and not is_chain:
                    moves_list.append([Move(square, target_square, p)])
                elif target_square.piece != 0 and target_square.piece % 2 != p % 2:
                    # the target square has an enemy piece
                    jump_square = square.get_next_one_over(target_square)
                    if jump_square is not None and jump_square.piece == 0 and not jump_square.jump_simulated:
                        jump_square.jump_simulated = True
                        for move in self.possible_moves(jump_square.x, jump_square.y, True, p):
                            moves_list.append([Move(square, jump_square, p, True, target_square)] + move)
                        jump_square.jump_simulated = False
        if any(moves[0].jumps for moves in moves_list):
            moves_list = list(filter(lambda move: move[0].jumps, moves_list))
        if is_chain and not moves_list:
            moves_list.append([])
        return moves_list

    def get_all_squares(self):
        all_squares = []
        for row in self.squares:
            all_squares.extend(row)
        return all_squares
	
	# return all squares where a certain player is
    def get_player_squares(self, player):
        all_squares = self.get_all_squares()
        return list(filter(lambda square: square.piece % 2 == player % 2 and square.piece != 0, all_squares))

	# return all possible moves that a player currently has
    def all_possible_moves(self, player):
        player_squares = self.get_player_squares(player)
        moves = []
        for piece_square in player_squares:
            moves.extend(self.possible_moves(piece_square.x, piece_square.y))
        if any(move[0].jumps for move in moves):
            moves = list(filter(lambda move: move[0].jumps, moves))
        return moves

	# executes moves and saves them in move_history
    def execute_moves(self, moves):
        for move in moves:
            move.end.piece = move.start.piece
            move.start.piece = 0
            if move.jumps:
                move.between_square.piece = 0
            if move.kinged:
                move.end.piece += 2  # kings a piece if it reaches the end.
        self.move_history.append(moves)
        return moves

	# will change instance variable 'winner' once called if a certain win condition is met 
    def check_game_over(self):
        if not self.all_possible_moves(1):
            self.winner = 2
        if not self.all_possible_moves(2):
            self.winner = 1
        if self.moves_without_jump > 20:
            self.winner = 99  # tie

	# undoes most recent set of moves in the internal gameboard
    def undo_moves(self):
        moves = reversed(self.move_history.pop())
        for move in moves:
            if move.kinged:
                move.start.piece -= 2.
            if move.jumps:
                    move.between_square.piece = move.captured
            move.start.piece = move.moved_piece
            move.end.piece = 0
        return moves
	
	# used to evaluate current situation for a player (greater than 0 is leagin and less is losing)
    def evaluate(self, player):
        score = 0
        all_squares = self.get_all_squares()
        for square in all_squares:
            p = square.piece
            if p != 0:
                if p % 2 == player % 2:
                    score += 100
                    if p == player + 2:
                        score += 50
                else:
                    score -= 100
                    if p > 2:
                        score -= 50
        return score
	
	# returns best move according to the minimax algorithm
    def evaluate_best_move(self, player, depth):
        possible_moves = self.all_possible_moves(player)
        random.shuffle(possible_moves)
        return max(possible_moves, key=(lambda move: Simulation().minimax(depth, self, player)))

# Represents a move in the game. Contains necessary information for AI and controlling the robot.
class Move:
    def __init__(self, square_1, square_2, moved_piece, jumps=False, between_square=None):
        self.start = square_1
        self.end = square_2
        self.jumps = jumps
        self.between_square = between_square
        self.moved_piece = moved_piece
        if between_square is not None:
            self.captured = between_square.piece
        else:
            self.captured = None

        self.kinged = (self.moved_piece == 1 and self.end.y == 1) or (self.moved_piece == 2 and self.end.y == 8)

    def __repr__(self):
        return str(self.start) + "to" + str(self.end)


class Simulation:
    def __init__(self):
        pass

    def minimax(self, depth, board, player, is_maxing_player=True):
        if depth == 0:
            return board.evaluate(player)
        possible_moves = board.all_possible_moves(player)

        if player == 1:
            nextplayer = 2
        else:
            nextplayer = 1

        if is_maxing_player:
            best_move = -9999
            for move in possible_moves:
                board.execute_moves(move)
                best_move = max(best_move,
                                self.minimax(depth-1, board, nextplayer, not is_maxing_player))
                board.undo_moves()
            return best_move
        else:
            best_move = 9999
            for move in possible_moves:
                board.execute_moves(move)
                best_move = min(best_move,
                                self.minimax(depth-1, board, nextplayer, not is_maxing_player))
                board.undo_moves()
            return best_move


# AI vs. AI on console
def ai_vs_ai_game():
	pnum = 1
	turn = 1
	while test_board.winner == 0:
		print("\n" + str(turn) + "# Round, Player:" + str(pnum))
		print(test_board.print_board())
		best_moves = test_board.evaluate_best_move(pnum, 4)
		if best_moves[0].jumps:
			test_board.moves_without_jump = 0
		else:
			test_board.moves_without_jump += 1
		print(test_board.execute_moves(best_moves))
		print("evaluation for player " + str(pnum) + ": " + str(test_board.evaluate(pnum)))
		test_board.check_game_over()
		turn += 1
		if pnum == 1:
			pnum = 2
		else:
			pnum = 1

	print("\n" + str(turn) + "# Round, Player:" + str(pnum))
	print(test_board.print_board())

	print("The winner is " + str(test_board.winner) + "\n")
