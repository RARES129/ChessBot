import re
import chess
import chess.pgn
import chess.engine
import math
import os


class ExplainChess:
    def __init__(self):
        self.regex = r"\b([RNBQK]?[a-h]?[1-8]?x?[a-h][1-8](=[RNBQ])?[\+#]?|O-O-O|O-O)\b"
        self.pieces = {
            "R": "Rook",
            "N": "Knight",
            "B": "Bishop",
            "Q": "Queen",
            "K": "King"}
        self.special_moves = {
            "O-O": "Kingside castling",
            "O-O-O": "Queenside castling"
        }
        self.stockfish_path = os.getenv('STOCKFISH_PATH')
        self.scale_factor = 0.004

    def is_valid_chess_notation(self, text):
        return bool(re.search(self.regex, text))

    def find_chess_moves(self, text):
        return [move for move in text.split() if self.is_valid_chess_notation(move)]

    def explain_chess_move(self, move):
        if move in self.special_moves:
            return self.special_moves[move]

        explanation = ""
        promoted_piece = None

        if '=' in move:
            move, promoted_piece = move.split('=')
            promoted_piece = self.pieces.get(promoted_piece, promoted_piece)

        if move[0] in self.pieces:
            piece = self.pieces[move[0]]
            move = move[1:]
        else:
            piece = "Pawn"

        if 'x' in move:
            explanation += piece + " captures on "
            move = move.replace('x', '')

            if len(move) == 2 and piece == "Pawn":  # Potential en passant
                explanation += move + " via en passant"
            else:
                explanation += move[1:] if piece == 'Pawn' else move
        else:
            explanation += piece + " moves to " + move

        if promoted_piece:
            explanation += " and promotes to " + promoted_piece

        if '+' in move:
            explanation = explanation.replace('+', '') + " delivering check"
        elif '#' in move:
            explanation = explanation.replace('#', '') + " delivering checkmate"

        return explanation

    def score_to_probability(self, score):
        return 1 / (1 + math.exp(-self.scale_factor * score))

    def best_moves(self, moves):
        # Creating the board and first part of the answer
        answer = 'Explaining th current game: \n'
        for idx, move in enumerate(moves):
            if idx % 2 == 0:
                answer += f'\t{idx + 1}.{move} - {self.explain_chess_move(move)} (white move)\n'
            else:
                answer += f'\t{idx + 1}.{move} - {self.explain_chess_move(move)} (black move)\n'
        board = chess.Board()
        engine = chess.engine.SimpleEngine.popen_uci(self.stockfish_path)

        # Adding moves to the table
        try:
            for move in moves:
                board.push_san(move)
        except chess.IllegalMoveError as e:
            print(e)
            return f'Illegal move/moves detected, the game can not be analyzed.\n' \
                   f'Make sure that the move/moves are in correct notation or the game sequence of moves ' \
                   f'are in correct order.'

        # Computing move
        result = engine.play(board, chess.engine.Limit(time=0.1))

        # Final details
        answer += f'\nBest possible move: {board.san(result.move)} - ' \
                  f'{self.explain_chess_move(board.san(result.move))}\n\n'
        if moves[-1].__contains__('+'):
            answer += f'Check status: The above move is mandatory since the king is in check.\n\n'
        try:
            answer += f'Best opponent move: {board.san(result.ponder)} - ' \
                    f'{self.explain_chess_move(board.san(result.ponder))}\n\n'
        except AttributeError as e:
            print(e)
            answer += 'No best move for the opponent.\n\n'

        # Calculating probability
        board.push(result.move)
        info = engine.analyse(board, chess.engine.Limit(time=0.1))
        score_white = info['score'].white().score(mate_score=10_000)
        score_black = info['score'].black().score(mate_score=10_000)
        probability_white = self.score_to_probability(score_white)
        probability_black = self.score_to_probability(score_black)
        answer += f'The winning probability for the player controlling the white pieces based on the above move is ' \
                  f'{int(probability_white * 100)}%.\n\n'
        answer += f'The winning probability for the player controlling the black pieces based on the above move is ' \
                  f'{int(probability_black * 100)}%.\n\n'

        engine.quit()

        return answer
