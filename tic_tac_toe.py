import tkinter as tk
from tkinter import messagebox
import random

BG = '#111827'
PANEL = '#1f2937'
CELL = '#374151'
TEXT = '#f9fafb'
X_COLOR = '#38bdf8'
O_COLOR = '#fb7185'
WIN = '#166534'

class TicTacToe:
    def __init__(self, root):
        self.root = root
        root.title('Tic-Tac-Toe | Python Edition')
        root.geometry('570x690')
        root.minsize(510, 650)
        root.configure(bg=BG)
        self.mode = tk.StringVar(value='Computer')
        self.difficulty = tk.StringVar(value='Hard')
        self.names = ['Player X', 'Player O']
        self.scores = {'X': 0, 'O': 0, 'Draw': 0}
        self.board = [''] * 9
        self.turn = 'X'
        self.paused = False
        self.finished = False
        self.pending = None
        self.build_ui()
        self.refresh()

    def button(self, parent, text, command, color=PANEL, width=11):
        return tk.Button(parent, text=text, command=command, bg=color, fg=TEXT,
                         activebackground='#4b5563', activeforeground=TEXT,
                         font=('Arial', 11, 'bold'), bd=0, padx=10, pady=9,
                         cursor='hand2', width=width)

    def build_ui(self):
        tk.Label(self.root, text='TIC-TAC-TOE', bg=BG, fg=TEXT,
                 font=('Arial', 27, 'bold')).pack(pady=(20, 5))
        tk.Label(self.root, text='Python Edition', bg=BG, fg='#9ca3af',
                 font=('Arial', 11)).pack()

        options = tk.Frame(self.root, bg=BG)
        options.pack(pady=12)
        tk.Label(options, text='Mode', bg=BG, fg=TEXT).grid(row=0, column=0, padx=7)
        tk.OptionMenu(options, self.mode, 'Computer', 'Two Players', command=lambda _: self.new_game()).grid(row=0, column=1, padx=7)
        tk.Label(options, text='AI Difficulty', bg=BG, fg=TEXT).grid(row=0, column=2, padx=7)
        tk.OptionMenu(options, self.difficulty, 'Easy', 'Medium', 'Hard', command=lambda _: self.new_game()).grid(row=0, column=3, padx=7)

        self.score_label = tk.Label(self.root, bg=BG, fg=TEXT, font=('Arial', 13, 'bold'))
        self.score_label.pack(pady=6)
        self.status = tk.Label(self.root, bg=BG, fg='#fbbf24', font=('Arial', 13, 'bold'))
        self.status.pack(pady=(3, 12))

        grid = tk.Frame(self.root, bg=BG)
        grid.pack()
        self.cells = []
        for i in range(9):
            b = tk.Button(grid, text='', font=('Arial', 34, 'bold'), bg=CELL, fg=TEXT,
                          activebackground='#4b5563', bd=0, width=4, height=2,
                          cursor='hand2', command=lambda idx=i: self.play(idx))
            b.grid(row=i // 3, column=i % 3, padx=5, pady=5)
            self.cells.append(b)

        controls = tk.Frame(self.root, bg=BG)
        controls.pack(pady=17)
        self.button(controls, 'Reset Round', self.reset_round).grid(row=0, column=0, padx=4)
        self.button(controls, 'New Game', self.new_game).grid(row=0, column=1, padx=4)
        self.pause_button = self.button(controls, 'Pause', self.toggle_pause)
        self.pause_button.grid(row=0, column=2, padx=4)
        self.button(self.root, 'Exit', self.exit_game, color='#991b1b', width=15).pack()
        tk.Label(self.root, text='X goes first  •  New Game resets scores', bg=BG,
                 fg='#9ca3af', font=('Arial', 9)).pack(pady=12)

    def lines(self):
        return [(0, 1, 2), (3, 4, 5), (6, 7, 8),
                (0, 3, 6), (1, 4, 7), (2, 5, 8),
                (0, 4, 8), (2, 4, 6)]

    def result(self, board):
        for line in self.lines():
            a, b, c = line
            if board[a] and board[a] == board[b] == board[c]:
                return board[a], line
        if all(board):
            return 'Draw', None
        return None, None

    def play(self, index):
        if self.paused or self.finished or self.board[index]:
            return
        if self.mode.get() == 'Computer' and self.turn == 'O':
            return
        self.place(index)

    def place(self, index):
        self.board[index] = self.turn
        winner, line = self.result(self.board)
        if winner:
            self.finished = True
            self.scores[winner] += 1
            self.refresh(line)
            return
        self.turn = 'O' if self.turn == 'X' else 'X'
        self.refresh()
        if self.mode.get() == 'Computer' and self.turn == 'O' and not self.paused:
            self.pending = self.root.after(350, self.computer_move)

    def computer_move(self):
        self.pending = None
        if self.paused or self.finished or self.turn != 'O':
            return
        moves = [i for i, value in enumerate(self.board) if not value]
        if not moves:
            return
        level = self.difficulty.get()
        if level == 'Easy':
            index = random.choice(moves)
        elif level == 'Medium':
            index = self.tactical_move() if random.random() < 0.75 else random.choice(moves)
        else:
            index = self.best_move()
        self.place(index)

    def tactical_move(self):
        for mark in ('O', 'X'):
            for i in range(9):
                if not self.board[i]:
                    trial = self.board.copy()
                    trial[i] = mark
                    if self.result(trial)[0] == mark:
                        return i
        return random.choice([i for i, x in enumerate(self.board) if not x])

    def minimax(self, board, maximizing, depth):
        winner, _ = self.result(board)
        if winner == 'O':
            return 10 - depth
        if winner == 'X':
            return depth - 10
        if winner == 'Draw':
            return 0
        scores = []
        for i, mark in enumerate(board):
            if not mark:
                board[i] = 'O' if maximizing else 'X'
                scores.append(self.minimax(board, not maximizing, depth + 1))
                board[i] = ''
        return max(scores) if maximizing else min(scores)

    def best_move(self):
        best = -float('inf')
        choices = []
        for i, mark in enumerate(self.board):
            if not mark:
                self.board[i] = 'O'
                score = self.minimax(self.board, False, 0)
                self.board[i] = ''
                if score > best:
                    best, choices = score, [i]
                elif score == best:
                    choices.append(i)
        return random.choice(choices)

    def refresh(self, winning_line=None):
        for i, cell in enumerate(self.cells):
            mark = self.board[i]
            cell.config(text=mark if not self.paused else '•',
                        fg=X_COLOR if mark == 'X' else O_COLOR,
                        bg=WIN if winning_line and i in winning_line else CELL,
                        state='disabled' if self.paused or self.finished or mark else 'normal')
        self.score_label.config(text=f"X: {self.scores['X']}     O: {self.scores['O']}     Draws: {self.scores['Draw']}")
        winner, _ = self.result(self.board)
        if self.paused:
            message = 'PAUSED'
        elif winner == 'Draw':
            message = "It's a draw!"
        elif winner:
            message = f'{winner} wins!'
        else:
            message = f"{self.turn}'s turn" + (' (Computer)' if self.mode.get() == 'Computer' and self.turn == 'O' else '')
        self.status.config(text=message)
        self.pause_button.config(text='Resume' if self.paused else 'Pause')

    def cancel_pending(self):
        if self.pending is not None:
            self.root.after_cancel(self.pending)
            self.pending = None

    def reset_round(self):
        self.cancel_pending()
        self.board = [''] * 9
        self.turn = 'X'
        self.paused = False
        self.finished = False
        self.refresh()

    def new_game(self):
        self.scores = {'X': 0, 'O': 0, 'Draw': 0}
        self.reset_round()

    def toggle_pause(self):
        if self.finished:
            return
        self.paused = not self.paused
        if self.paused:
            self.cancel_pending()
        self.refresh()
        if not self.paused and self.mode.get() == 'Computer' and self.turn == 'O':
            self.pending = self.root.after(350, self.computer_move)

    def exit_game(self):
        if messagebox.askyesno('Exit Game', 'Are you sure you want to exit?'):
            self.cancel_pending()
            self.root.destroy()

if __name__ == '__main__':
    root = tk.Tk()
    game = TicTacToe(root)
    root.protocol('WM_DELETE_WINDOW', game.exit_game)
    root.mainloop()
