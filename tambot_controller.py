import checkers_ai as ai
import stepper_controller as sc
import shift_reader as sr
import time
import threading

king_piece_locations = [(8,-1),(7,-1),(6,-1),(8,0),(7,0),(6,0)]


def print_input():
    for row in sr.read_with_shift():
        print(row)
    print("\n")

def complete_moves(moves):
    sc.move_to(moves[0].start.x, moves[0].start.y)
    sc.grabber_grab(moves[0].moved_piece > 2)
    for move in moves:
        sc.move_to(move.end.x, move.end.y)
    sc.grabber_drop(moves[0].moved_piece > 2)
    
    for move in moves:
        if move.jumps:
            sc.move_to(move.between_square.x, move.between_square.y)
            sc.grabber_grab(move.captured > 2)
            dispose_piece(pieces_amount(move.captured))
        if move.kinged:
            get_king()
            sc.move_to(move.end.x, move.end.y)
            sc.grabber_drop(True)
    sc.move_home()
    sc.grabber_elevate()
    sc.magnet_elevate()

def get_king():
    loc = king_piece_locations.pop()
    sc.move_to(loc[0], loc[1])
    sc.grabber_grab(True)
    
def pieces_amount(piece):
    if piece > 2:
        return 2
    else:
        return 1

disposal_locations = [(5,-1), (4,-1), (3,-1), (2,-1), (1,-1)]
disposal_amounts = [0,0,0,0,0]

def dispose_piece(pieces):
    index = 0
    for i in disposal_amounts:
        if (disposal_amounts[index] + pieces) <= 4:
            disposal_amounts[index] += pieces
            break
        else:
            index += 1
    loc = disposal_locations[index]
    sc.move_to(loc[0], loc[1])
    sc.grabber_lower_with_height(disposal_amounts[index])
    sc.magnet_elevate()
    sc.grabber_elevate()
        


def player_vs_ai():
    player_turn = True
    turn = 1
    while board.winner == 0:
        if player_turn:
            while not board.process_input(sr.read_with_shift(), 1):
                print_input()
                print(board.board_str())
                time.sleep(1)
        else:
            best_moves = board.evaluate_best_move(2, 4)
            complete_moves(board.execute_moves(best_moves))
            
        
        if board.move_history[len(board.move_history)-1][0].jumps:
            board.moves_without_jump = 0
        else:
            board.moves_without_jump += 1
        board.check_game_over()
        turn += 1
        player_turn = not player_turn
        print(board.board_str())

		
def ai_vs_ai():
    pnum = 1
    turn = 1
    while board.winner == 0:
        print("\n" + str(turn) + "# Round, Player:" + str(pnum))
        print(board.board_str())
        best_moves = board.evaluate_best_move(pnum, 2)
        if best_moves[0].jumps:
            board.moves_without_jump = 0
        else:
            board.moves_without_jump += 1
        print(board.execute_moves(best_moves))
        complete_moves(best_moves)
        print("evaluation for player " + str(pnum) + ": " + str(board.evaluate(pnum)))
        board.check_game_over()
        turn += 1
        if pnum == 1:
            pnum = 2
        else:
            pnum = 1

# infinite player vs ai
while True:
    board = ai.Board()
    player_vs_ai()