# -*- coding: utf-8 -*-
__doc__ = r""" TicTacToe in TUI

This is a script for loading computer agent, and playing tic-tac-toe with human user.
After you have finished you QLearningPolicy, you can use `python main.py -a QLearningPolicy` to test your agent.
"""

import numpy as np
from tic_tac_toe import TicTacToeBoard
import os, sys, argparse
import policy

mark_map = {1: " X ", -1: " O ", 0: "   "}

def render(state):
    """
    render the game board.

    Args:
        state (ndarray): a 2D numpy array, filled with 1, -1, 0,
            indicating mark of first player, second player, and place not yet occupied.
    """
    clean()
    h, w = state.shape
    rows = map(lambda x: "|".join(map(lambda y: mark_map[y], x)), state)
    splitter = "+".join(["---"] * w)
    print(("\n" + splitter + "\n").join(rows))
    print()

def get_action():
    """
    get user's input and return the action.

    Returns:
        action (tuple of (int, int)): indicates the coordinates to place mark,
            starting from 0, i.e. (0, 0) is the top left corner.
    """
    x, y = map(
        int,
        input(
            'Please input the coordinates as "x y" to place, starting from 1: '
        ).split(),
    )
    return x - 1, y - 1

def set_winner():
    """
    Display winner information.
    """
    print("Congratulation, you win!")

def set_loser():
    """
    Display loser information.
    """
    print("Sorry, you lose!")

def set_tie():
    """
    Display tie information.
    """
    print("Tie!")

def clean():
    """
    clear screen.
    """
    if sys.platform == "win32":
        os.system("cls")
    else:
        os.system("clear")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="A Tic-TacToe game rendered in Terminal")
    parser.add_argument("-p", "--policy", choices=["RandomPolicy", "QLearningPolicy"], default="QLearningPolicy", help="The policy class of the agent")

    args = parser.parse_args()
    Agent = getattr(policy, args.policy)

    win_len = 3
    board_size = 3, 3 
    board = TicTacToeBoard(board_size, win_len)
    p1 = Agent(marker=1, board_size=board_size) #Computer as the first player (X).
    p2 = Agent(marker=-1, board_size=board_size) #Human as the first player (X)

    play = True
    while play:
        order = input("First player or second? [1/2]: ").strip()
        assert order in ["1", "2"], "Invalid selection!"
        opponent = p2 if order == "1" else p1
        marker = 1 if order == "1" else -1
        state, info = board.reset()        
        while not board.terminated:
            render(state)
            if board.on_move == opponent.marker:
                #agent's turn.
                state, (r1, r2), *_ = board.step(opponent.marker, opponent.decide(state))
            else:
                #your turn.
                action = get_action()
                state, (r1, r2), *_ = board.step(marker, action)
        if r1 == marker:
            set_winner()                
        elif r1 == opponent.marker:
            set_loser()
        else:
            set_tie()
        play = input("Play again:[Y/n]").lower() != "n"
