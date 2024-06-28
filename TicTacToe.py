from tkinter import *
import tkinter.ttk as ttk
import os
from PIL import ImageTk, Image
import time 
import numpy as np
import json

class Game:
    
    def __init__(self, p1, p2, N):
        """ Constructor.
    
        Parameters
        ----------
        p1 : `Player`
            First player

        p2 : `Player`
            Second player

        N : `int`
            Dimension of board game NxN
        """
        # 2 is empty spot, 0 is player 1's symbol, 1 is player 2's symbol
        self.board = [2 for i in range(N*N)] 
        self.p1 = p1
        self.p2 = p2
        self.N = N
        self.gameStillGoing = True
        self.winner = None
        # initialize to who plays first
        self.currentPlayer = 0 

        
    def show_board(self):
        """ Display board at it's current state. "_" is an empty position, "o" is player 1, "x" is player 2"""
        for i in range(self.N):
            line = " "
            for j in range(self.N):
                if self.board[i*self.N+j] == 0:
                    line = line+" o "
                if self.board[i*self.N+j] == 1:
                    line = line+" x "
                if self.board[i*self.N+j] == 2:
                    line = line+" _ "
                if j < self.N-1:
                    line = line+"|"
            print(line)
        print("")
        
        
    def update_board(self, position):
        """ Handles a turn using the current player's symbol and the chosen position to update the board and then flip player.

        Parameters
        ----------
        position : `int`
            Selected position in the hashed board as an integer between 0 and N*N.
        """
        self.board[position] = self.currentPlayer
        if self.currentPlayer == 0:
            self.currentPlayer = 1
        elif self.currentPlayer == 1:
            self.currentPlayer = 0
    
    
    def available_positions(self):
        """Searches for position currently available so that the next player can choose next action.

        Returns
        -------
        positions : `list`
            It contains current empty position on the board game.

        """
        positions = []
        for i in range(self.N):
            for j in range(self.N):
                if self.board[i*self.N+j] == 2:
                    # adds empty position to the list
                    positions.append(i*self.N+j)
        return positions
    
    
    def check_if_game_over(self):
        """Checks if game ends with a winner or a tie."""
        self.check_for_winner()
        self.check_if_tie()
        
        
    def check_for_winner(self):
        """Checks whether one player wins the game. If so, the variable self.winner is assigned with the symbol of the player who wins. """
        # check rows
        row_winner = self.check_rows()
        # check columns
        column_winner = self.check_columns()
        # check diagonals
        diagonal_winner = self.check_diagonals()
    
    
        if row_winner == 0 or row_winner == 1:
            self.winner = row_winner
        elif column_winner == 0 or column_winner == 1:
            self.winner = column_winner
        elif diagonal_winner == 0 or diagonal_winner == 1:
            self.winner = diagonal_winner
        else:
            self.winner = None
        return

    
    def check_rows(self):
        """Searches for a full horizontal row. If one is found, the flag self.gameStillGoing flips to False.

        Returns
        -------
        winning_player : `int`
            Symbol of the winner if there is one.
        """
        winning_player = 2
        for row in range(self.N):
            win = True
            for col in range(1,self.N):
                if self.board[row*self.N+col-1] != self.board[row*self.N+col] or self.board[row*self.N+col] == 2:
                    win = False
                    break
            if win:
                winning_player = self.board[row*self.N]
                self.gameStillGoing = False
                break        
        if winning_player != 2:
            return winning_player
        return

    
    def check_columns(self):
        """Searches for a full vertical row. If one is found, the flag self.gameStillGoing flips to False.

        Returns
        -------
        winning_player : `int`
            Symbol of the winner if there is one.
        """
        winning_player = 2
        for col in range(self.N):
            win = True
            for row in range(1,self.N):
                if self.board[(row-1)*self.N+col] != self.board[row*self.N+col] or self.board[row*self.N+col] == 2:
                    win = False
                    break
            if win:
                winning_player = self.board[col]
                self.gameStillGoing = False
                break        
        if winning_player != 2:
            return winning_player
        return

    
    def check_diagonals(self):
        """Searches for a full diagonal row. If one is found, the flag self.gameStillGoing flips to False.

        Returns
        -------
        winning_player : `int`
            Symbol of the winner if there is one.
        """
        diag1, diag2 = True, True
        token1, token2 = self.board[0], self.board[self.N-1]
        for row in range(1,self.N):
            if token1 != self.board[row*self.N+row]:
                diag1 = False
            if token2 != self.board[row*self.N+(self.N-row-1)]:
                diag2 = False
            if not diag1 and not diag2:
                break
        if diag1 and token1 != 2:
            self.gameStillGoing = False
            return token1
        elif diag2 and token2 != 2:
            self.gameStillGoing = False
            return token2
        return
    
    
    def check_if_tie(self):
        """Checks whether there is a tie, which means the board is completely full but no one wins. If so, the flag self.gameStillGoing flips to False. """
        if 2 not in self.board:
            self.gameStillGoing = False
        return
    
        
    def give_reward(self):
        """Gives rewards at the end of a game."""
        result = self.winner
        if result == 0:
            self.p1.update_policy(1)
            self.p2.update_policy(0)
        elif result == 1:
            self.p1.update_policy(0)
            self.p2.update_policy(1)
        else:
            self.p1.update_policy(0.5)                             
            self.p2.update_policy(0.5)

            
    def reset(self):
        """Resets the game to the beginning."""
        self.board = [2 for i in range(self.N*self.N)] 
        self.gameStillGoing = True
        self.winner = None
        self.currentPlayer = 0
        
    
    def training(self, rounds=100):
        """ Handles training of player 1 and player 2 to update their policies.

        Parameters
        ----------
        rounds : `int`
            Number of games in the training.
        """
        def bar(amount): 
            progress["value"]=amount
            
        training_label = Label(main_frame, text="Training ...", font=("Helvetica", 20), bg='#FFF3DB', fg="black")
        training_label.grid()
        style_progress = ttk.Style()
        style_progress.theme_use('clam')
        style_progress.configure("red.Horizontal.TProgressbar", troughcolor= 'white', darkcolor= 'white', lightcolor= 'white' , bordercolor='#FFF3DB', foreground='#FFCC66', background='#FFCC66')

        progress = ttk.Progressbar(main_frame, style="red.Horizontal.TProgressbar", orient = HORIZONTAL,length = 400, mode = 'determinate')
        progress.grid()
        
        num_rounds = 0
        progress["value"]= num_rounds
        progress["maximum"]=rounds
        
        for i in range(rounds):
            num_rounds+=1
            progress.after(0, bar(num_rounds))
            progress.update()
            while self.gameStillGoing:
                # Player 1 plays
                positions = self.available_positions()
                p1_pick = self.p1.choose_action(positions, self.board, self.currentPlayer) 
                self.update_board(p1_pick)
                self.p1.add_state(self.board)
                # Check whether the game ends here
                self.check_if_game_over()
                if not self.gameStillGoing:
                    self.give_reward()
                    self.p1.reset()
                    self.p2.reset()
                    self.reset()
                    break
                else:
                    # Player 2 plays
                    positions = self.available_positions()
                    p2_pick = self.p2.choose_action(positions, self.board, self.currentPlayer)
                    self.update_board(p2_pick)
                    self.p2.add_state(self.board)
                    # Check whether the game ends here
                    self.check_if_game_over()
                    if not self.gameStillGoing:
                        self.give_reward()
                        self.p1.reset()
                        self.p2.reset()
                        self.reset()
                        break
        training_label.grid_forget()
        progress.grid_forget()
        
                       
    def computer_move(self):
        """ Generates an action from p1 (computer) based on its policy.
        
        Returns
        -------
        p1_pick : `int`
            Chosen position.
        """
        positions = self.available_positions()
        p1_pick = self.p1.choose_action(positions, self.board, self.currentPlayer)
        self.p1.add_state(self.board)
        self.update_board(p1_pick)
        return p1_pick
        
                     
                    
class GUI:
    
    def __init__(self, Game):
        """ Constructor.
    
        Parameters
        ----------
        Game : `Game`
            Game to play with using the the GUI.
        """
        self.game = Game
        self.symbol = 0
        self.b0 = Button(main_frame, width=10, height=5, relief=GROOVE, command=lambda: self.choose(0))
        self.b1 = Button(main_frame, width=10, height=5, relief=GROOVE, command=lambda: self.choose(1))
        self.b2 = Button(main_frame, width=10, height=5, relief=GROOVE, command=lambda: self.choose(2))
        self.b3 = Button(main_frame, width=10, height=5, relief=GROOVE, command=lambda: self.choose(3))
        self.b4 = Button(main_frame, width=10, height=5, relief=GROOVE, command=lambda: self.choose(4))
        self.b5 = Button(main_frame, width=10, height=5, relief=GROOVE, command=lambda: self.choose(5))
        self.b6 = Button(main_frame, width=10, height=5, relief=GROOVE, command=lambda: self.choose(6))
        self.b7 = Button(main_frame, width=10, height=5, relief=GROOVE, command=lambda: self.choose(7))
        self.b8 = Button(main_frame, width=10, height=5, relief=GROOVE, command=lambda: self.choose(8))
        self.player_count = Label(window, text=username_entry.get()+" : 0", font=("Helvetica", 15), bg='#FFF3DB', fg="black")
        self.computer_count = Label(window, text="Computer : 0", font=("Helvetica", 15), bg='#FFF3DB', fg="black")
        self.win_text = ""
        self.winner_label = Label(title_frame, text=self.win_text, font=("Helvetica", 20), bg='#FFF3DB', fg="Red" )
        self.again_button = Button(title_frame, text="RESTART", command= lambda: self.restart(), font=("Helvetica", 15), bg="White", fg="Black", bd=0, relief=GROOVE, highlightbackground='#FFF3DB', activebackground='#FFF3DB', activeforeground="Black")
        
    def show(self):
        """Displays game board as a grid of buttons."""
        self.b0.grid(row=0, column=0)
        self.b1.grid(row=0, column=1)
        self.b2.grid(row=0, column=2)
        self.b3.grid(row=1, column=0)
        self.b4.grid(row=1, column=1)            
        self.b5.grid(row=1, column=2)
        self.b6.grid(row=2, column=0)
        self.b7.grid(row=2, column=1)
        self.b8.grid(row=2, column=2)
        self.player_count.grid(row=1, column=2)
        self.computer_count.grid(row=1, column=5)
        
    def run(self):
        """Starts a game by letting the computer pick its first move and then displays the board."""
        # Computer's first move
        p1_pick = self.game.computer_move()
        self.choose(p1_pick)
        self.symbol = self.game.currentPlayer
        self.show()
        
        
    def choose(self, position):
        """ Updates the interactive game board by changing the symbols and give the hand to the computer-player.
    
        Parameters
        ----------
        position : `int`
            Chosen position by current player.
        """
        if self.symbol == 0:
            img = PhotoImage(file="O.png")
            self.symbol = 1
        else:
            self.game.update_board(position)
            img = PhotoImage(file="X.png")
            self.symbol = 0
        img = img.subsample(10, 10) 
        exec("self.b"+str(position)+".config(width=90, height=80, image=img)")
        exec("self.b"+str(position)+".image = img")
        exec("self.b"+str(position)+"['state'] = DISABLED")
        
        self.game.check_if_game_over()
        if self.game.gameStillGoing and self.symbol == 0:
            p1_pick = self.game.computer_move()
            self.choose(p1_pick)
        elif not self.game.gameStillGoing:
            self.end_game()
            
        
    def end_game(self):
        """ Ends game by disabling all buttons and announcing the winner."""
        for i in range(9):
            exec("self.b"+str(i)+"['state'] = DISABLED")
        
        if self.game.winner is None:
            self.win_text = "It's a tie !" 
        elif self.game.winner ==0:
            original = self.computer_count.cget("text")
            count = int(original[11:])
            count += 1
            new = "Computer : "+str(count)
            self.computer_count['text'] = new
            self.win_text = "Computer wins !" 
        else:
            original = self.player_count.cget("text")
            count = int(original[len(self.game.p2.name)+3:])
            count += 1
            new = self.game.p2.name+" : "+str(count)
            self.player_count['text'] = new
            self.win_text = self.game.p2.name+" wins !"
        self.winner_label['text'] = self.win_text
        self.winner_label.grid(row=1, columnspan=3)
        self.again_button.grid(row=2, columnspan=3)
        self.game.give_reward()
        
    def restart(self):
        """ Handles the 'PLAY AGAIN' button."""
        self.reset()
        self.winner_label.grid_forget()
        self.run()
            
    def reset(self):
        """ Resets GUI object."""
        self.game.p1.reset()
        self.game.p2.reset()
        self.game.reset()
        self.symbol = 0
        self.b0 = Button(main_frame, width=10, height=5, relief=GROOVE, command=lambda: self.choose(0))
        self.b1 = Button(main_frame, width=10, height=5, relief=GROOVE, command=lambda: self.choose(1))
        self.b2 = Button(main_frame, width=10, height=5, relief=GROOVE, command=lambda: self.choose(2))
        self.b3 = Button(main_frame, width=10, height=5, relief=GROOVE, command=lambda: self.choose(3))
        self.b4 = Button(main_frame, width=10, height=5, relief=GROOVE, command=lambda: self.choose(4))
        self.b5 = Button(main_frame, width=10, height=5, relief=GROOVE, command=lambda: self.choose(5))
        self.b6 = Button(main_frame, width=10, height=5, relief=GROOVE, command=lambda: self.choose(6))
        self.b7 = Button(main_frame, width=10, height=5, relief=GROOVE, command=lambda: self.choose(7))
        self.b8 = Button(main_frame, width=10, height=5, relief=GROOVE, command=lambda: self.choose(8))
        
            
class Human:
    
    def __init__(self, name):
        """ Constructor.
    
        Parameters
        ----------
        name : `str`
            Name of human player.
        """
        self.name = name

    def choose_action(self, positions):
        """Chooses an action depending on the available positions.
    
        Parameters
        ----------
        positions : `list`
            List of available positions the human play can pick from.
            
        Returns
        -------
        pick : `int`
            Chosen position.
        """
        while True:
            pick = input("Choisir une position (1-9) : ")
            pick = int(pick) - 1
            if pick in positions:
                return pick
                break
            else:
                print("Position occupée !")

                
    def add_state(self, state):
        pass

    def update_policy(self, reward):
        pass

    def reset(self):
        pass
    
class Computer:
    
    def __init__(self, name, alpha=0.2, gamma=0.9, epsilon=0.3):
        """ Constructor.
    
        Parameters
        ----------
        name : `str`
            Name of computer player.
        epsilon : `float`
            Greedy rate for exploration-exploitation. 0.3 means 30% of random actions
        """
                                                                                     
        self.name = name
        self.states = []  # record all positions taken during the game
        self.alpha = alpha
        self.epsilon = epsilon
        self.gamma = gamma
        self.states_value = {}
        

    def choose_action(self, positions, current_board, symbol):
        """Chooses an action depending on the available positions.
    
        Parameters
        ----------
        positions : `list`
            List of available positions the agent can pick from.
            
        current_board : `list`
            List representing the current board
            
        symbol : `int`
            Symbol of current player.
            
        Returns
        -------
        pick : `int`
            Chosen position.
        """
        if np.random.uniform(0, 1) <= self.epsilon:  # random action
            idx = np.random.choice(len(positions))
            action = positions[idx]
        else: # greedy action
            value_max = -999
            for p in positions:
                # Evaluate the value function for each possible outcome
                # and keep in storage the higher probability throughout the process.
                next_board = current_board.copy() 
                next_board[p] = symbol
                next_board = str(next_board)
                value = 0 if self.states_value.get(next_board) is None else self.states_value.get(next_board)
                if value >= value_max:
                    value_max = value
                    action = p
        return action

   
    
    def add_state(self, state):
        """Adds a state/board to storage for this game.
    
        Parameters
        ----------
        state : `list`
            List representing the board to memory.
        """
        self.states.append(str(state))
        
                                                                
    def update_policy(self, reward):
        """Based on reward received by the player (1 if wins, 0 if loses or else), 
        updates the state-value function/policy for all visited states during the game.
    
        Parameters
        ----------
        reward : `float`
            Reward received by the player.
        """
        for st in reversed(self.states):
            state = string_to_list(st)
            optimization = {st}
            optimization.add(str(transpose(state)))
            for i in range(3):
                state = rotate(state)
                optimization.add(str(state))
                optimization.add(str(transpose(state)))
            if self.states_value.get(st) is None:
                for inv in optimization:
                    self.states_value[inv] = 0
            for inv in optimization:
                self.states_value[inv] += self.alpha * (self.gamma * reward - self.states_value[inv])
            reward = self.states_value[st]

            
    def reset(self):
        """Clear storage for latest game."""
        self.states = []
        
        
    def save_policy(self):
        """Save policy dictionary to json file."""
        with open('policy_' + str(self.name)+'.json', 'w') as fp:
            json.dump(self.states_value, fp)
            fp.close()

        
    def load_policy(self, file):
        """Load policy as json file to dictonary."""
        with open(file, 'r') as fp:
            self.states_value = json.load(fp)
            fp.close()
            

def rotate(board):
    """Performs rotation of a board matrix.
        
        Parameters
        ----------
        board : `list`
            List representing the board.
        Returns
        -------
        new : `list`
            Rotation matrix.
        """
    N = int(np.sqrt(len(board)))
    table = [[board[i*N+j] for j in range(N)] for i in range(N)]
    output = list(list(x)[::-1] for x in zip(*table))
    new = []
    for i in range(N):
        new += output[i]
    return new

def transpose(board):
    """Performs transpose of a board matrix.
        
        Parameters
        ----------
        board : `list`
            List representing the board.
        Returns
        -------
        new : `list`
            Transpose matrix.
        """
    N = int(np.sqrt(len(board)))
    m = [[board[i*N+j] for j in range(N)] for i in range(N)]
    output = [[m[j][i] for j in range(len(m))] for i in range(len(m[0]))] 
    new = []
    for i in range(N):
        new += output[i]
    return new

def string_to_list(st):
    """Converts a hashed board to list.
        
        Parameters
        ----------
        st : `string`
            List representing a board as a string.
        Returns
        -------
        res : `list`
            List representing the board.
        """
    res = [int(s) for s in st[1:-1].split(", ")]
    return res
            
def start_gui():
    """Starts training and testing. Change parameters in this section if needed."""
    global warning, warning_message
        
    if username_entry.get():
        if warning :
            warning_message.grid_forget()
            warning = False
        
        username_label.grid_forget()
        username_entry.grid_forget()
        username_button.grid_forget()
        
        hello_label = Label(main_frame, text="Hello "+username_entry.get()+ "!", font=("Helvetica", 30), bg='#FFF3DB', fg="black", pady=20, borderwidth=30)
        hello_label.grid()

        p1 = Computer("p1", epsilon=0.3)
        p2 = Computer("p2")
        train = Game(p1, p2, 3)

        train.training(10000)
        p1.save_policy()
        
        hello_label.grid_forget()
        
        p1 = Computer("Computer", epsilon=0)
        p1.load_policy("policy_p1.json")
        p2 = Human(username_entry.get())
        
        game = Game(p1, p2, 3)
        gui = GUI(game)
        gui.run()

    else: 
        if not warning:
            warning_message.grid()
            warning = True

if __name__ == "__main__":
    
    window = Tk()
    window.title("Tic Tac Toe")
    window.geometry("600x600")
    window.minsize(600,600)
    window.config(background='#FFF3DB')
    
    for x in range(8):
        Grid.columnconfigure(window, x, weight=1)
    for y in range(8):
        Grid.rowconfigure(window, y, weight=1)
    
    # Title
    title_frame = Frame(window, bg='#FFF3DB', width=600, height=50, pady=3)
    title_frame.grid(row=0, column=1, columnspan=6, sticky="n", pady=7)
    title_label = Label(title_frame, text="Tic Tac Toe", font=("Helvetica", 40), bg='#FFF3DB', fg="black")
    title_label.grid(row=0, columnspan=3)
    
    # Signature
    signature_label = Label(window, text="Tic Tac Toe par Céline Nguyen-Tu",  font=("Helvetica", 10), fg="Grey", bg='#FFF3DB')
    signature_label.place(relx=1.0, rely=1.0, anchor='se')
    
    # Main
    main_frame = Frame(window, bg='#FFF3DB', height=450, width=450, padx=10, pady=20)
    main_frame.grid(row=1, column=1, rowspan=6, columnspan=6, padx=10, pady=20)
    username_label = Label(main_frame, text="Username", font=("Helvetica", 15), fg="black", bg='#FFF3DB', padx=30)
    username_label.grid()
    username_entry = Entry(main_frame, bd=1, fg="black", bg="white", highlightbackground='#FFF3DB', justify=CENTER)
    username_entry.grid()
    warning = False
    warning_message = Label(main_frame, text="Enter username to start playing.", font=("Helvetica", 10), fg="Red", bg='#FFF3DB')
    username_button = Button(main_frame, text="PLAY", command= start_gui, font=("Helvetica", 15), bg="White", fg="Black", bd=0, relief=GROOVE, highlightbackground='#FFF3DB', activebackground='#FFF3DB', activeforeground="Black")
    username_button.grid()

    # Display
    window.mainloop()
