import chess
import chess.pgn
import chess.engine
import os

from dotenv import load_dotenv
from ExplainChess import *


class ChessPlayer:
    def __init__(self):
        load_dotenv()
        self.stockfish_path = os.getenv('STOCKFISH_PATH')
        self.name = "ChessBot"
        self.explain = ExplainChess()

    @staticmethod
    def get_games_from_file(file):
        with open(file, 'r') as f:
            games = f.read().split('\n')
        return games

    def get_last_winning_moves_for_game(self, moves: str):
        board = chess.Board()
        game = chess.pgn.Game()
        engine = chess.engine.SimpleEngine.popen_uci(self.stockfish_path)

        for move in moves.split():
            board.push_san(move)

        engine.configure({"Threads": 4})
        info = engine.analyse(board, chess.engine.Limit(time=0.1))

        result = 'draw' if board.is_stalemate() or board.is_insufficient_material()\
            else 'white' if board.turn else 'black'

        game.add_line(board.move_stack)
        pgn_list = str(game).split()[-8: -1]

        last_three_moves_pgn = []
        last_three_moves_uci = []
        if result != 'draw':
            skip = 1 if (board.turn != (result == 'white')) else -1
            while len(last_three_moves_uci) < 3:
                if skip > 0:
                    board.pop()
                    skip -= 1
                else:
                    last_three_moves_uci.append(board.pop().uci())
                    skip = 1

            idx = 0
            while len(last_three_moves_pgn) < 3:
                last_three_moves_pgn.append(pgn_list[idx])
                idx += 3

            last_three_moves_uci.reverse()

        engine.quit()

        last_three_moves_string = ''
        for move in last_three_moves_pgn:
            last_three_moves_string += f"{move} "

        return last_three_moves_string + '\n'

    def get_all_winning_moves_for(self, game_list: list):
        all_moves = {}
        result = " Moves and explanations\n\n"

        for game in game_list:
            moves = self.get_last_winning_moves_for_game(game)
            if moves in all_moves:
                all_moves[moves] += 1
            else:
                all_moves[moves] = 1

        for moves in all_moves.keys():
            if all_moves[moves] >= 2:
                result += f"{moves}"
                for idx, move in enumerate(moves.replace('\n', '').split(' ')):
                    if move != '':
                        result += f'\t{idx + 1}. {move} - {self.explain.explain_chess_move(move)}\n'
                result += '\n'

        return result
