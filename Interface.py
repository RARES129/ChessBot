from tkinter import *
from tkinter import filedialog

import customtkinter
import threading
from ChessBot import *
from Stockfish import *
from ExplainChess import *


class ChatApp:
    def __init__(self, root):
        self.chat_bot = ChessBot()
        self.chess_player = ChessPlayer()
        self.explain = ExplainChess()
        self.user_input = None
        self.chat_display = None
        self.root = root
        self.root.title("Chess AI")
        self.create_gui()

    def create_gui(self):
        self.chat_display = customtkinter.CTkTextbox(
            self.root,
            wrap=WORD,
            width=480,
            height=400,
            font=("Helvetica", 12),
            state='disabled'
        )
        self.chat_display.place(relx=0.5, rely=0.37, anchor=CENTER)

        self.user_input = customtkinter.CTkEntry(
            self.root,
            width=480,
            height=40,
            font=("Helvetica", 17),
            placeholder_text='Please enter your question here:'
        )
        self.user_input.place(relx=0.5, rely=0.8, anchor=CENTER)
        self.user_input.bind("<Return>", self.send_message)

        send_button = customtkinter.CTkButton(
            master=self.root,
            text="Send",
            command=self.send_message,
            width=150,
            height=35,
            font=("Helvetica", 17),
            hover=True,
            cursor="hand2",
        )
        send_button.place(relx=0.75, rely=0.9, anchor=CENTER)

        attach_button = customtkinter.CTkButton(
            self.root,
            text="Attach File",
            command=self.attach_file,
            width=150,
            height=35,
            font=("Helvetica", 17),
            hover=True,
            cursor="hand2",
        )
        attach_button.place(relx=0.25, rely=0.9, anchor=CENTER)

    def send_message(self, event=None):
        user_message = self.user_input.get()
        if user_message:
            self.display_message("User: " + user_message)
            self.user_input.delete(0, END)
            if self.explain.is_valid_chess_notation(user_message):
                moves = [move[:-1] if move[-1] == '?' else move
                         for move in self.explain.find_chess_moves(user_message)]
                if len(moves) == 1:
                    self.display_message('AI: ' + self.explain.explain_chess_move(moves[0]))
                else:
                    self.display_message('AI:\n' + self.explain.best_moves(moves))
            else:
                self.get_ai_response(user_message)

    def display_message(self, message):
        self.chat_display.configure(state='normal')
        self.chat_display.insert(END, message + "\n\n")
        self.chat_display.configure(state='disabled')
        self.chat_display.see(END)

    def get_ai_response(self, user_message):
        ai_response = self.chat_bot.answer_question(user_message)
        self.display_message("AI: " + ai_response)

    def attach_file(self):
        file_path = filedialog.askopenfilename()

        if file_path:
            self.display_message('System:')
            self.display_message("You attached a file: " + file_path)
            self.display_message('Waiting for file to be uploaded ...')
            thread = threading.Thread(target=self.process_file, args=(file_path,))
            thread.start()
        else:
            self.display_message("System: Im sorry. The file you provided is invalid!")

    def process_file(self, file_path):
        games = self.chess_player.get_games_from_file(file_path)
        self.display_message('File uploaded successfully')
        self.display_message('Waiting for result to be calculated (this may take some time depending on the '
                             'size of the file) ...')
        self.display_message("AI: " + self.chess_player.get_all_winning_moves_for(games))


if __name__ == "__main__":
    customtkinter.set_appearance_mode('dark')
    customtkinter.set_default_color_theme('green')
    root = customtkinter.CTk()
    root.geometry("500x600")
    root.resizable(False, False)
    app = ChatApp(root)
    root.mainloop()
