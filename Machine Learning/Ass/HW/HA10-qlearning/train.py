# -*- coding: utf-8 -*-
__doc__ = """This is a script for training Q-Learning Agent"""

import numpy as np
from tic_tac_toe import TicTacToeBoard
from policy import QLearningPolicy, RandomPolicy
import matplotlib.pyplot as plt
import argparse

def run_test(board, policy1, policy2):
    """
    Run the game between policy1 and policy2 till someone win or tie.

    Args:
        board (TicTacToeBoard), the game board.

        policy1 (Policy): the policy for the first player, marker X.

        policy2 (Policy): the policy for the second player, marker O.

    Returns:
        winner (int): can be 1 indicating the first Policy won,
            -1 indicating the second Policy won,
            or 0, means tie.
    """
    p1_state, info = board.reset()
    while True:
        if info["on_move"] == 1:
            action = policy1.decide(p1_state)
            p2_state, (p1_reward, p2_reward), terminated, info = board.step(1, action)

        elif info["on_move"] == -1:
            action = policy2.decide(p2_state)
            p1_state, (p1_reward, p2_reward), terminated, info = board.step(-1, action)

        if terminated:
            break            

    winner = p1_reward
    return winner

def run_train(board, policy1, policy2):
    """
    train any instances of QLearningPolicy in policy1 and policy2 for one game.

    Args:
        board (TicTacToeBoard), the game board.

        policy1 (Policy): the policy for the first player, marker X.

        policy2 (Policy): the policy for the second player, marker O.

    Returns:
        winner (int): can be 1 indicating the first Policy won,
            -1 indicating the second Policy won,
            or 0, means tie.
    """
    p1_state, info = board.reset()
    train_p1 = isinstance(policy1, QLearningPolicy) and policy1.mode == "train"
    train_p2 = isinstance(policy2, QLearningPolicy) and policy2.mode == "train"

    if train_p1:
        transaction_p1 = {}
    if train_p2:
        transaction_p2 = {}
    while True:
        if info["on_move"] == 1:
            action = policy1.decide(p1_state)
            p2_state, (p1_reward, p2_reward), terminated, info = board.step(1, action)

            #train policy2 and there is a state before p2_state for policy2
            if train_p2 and "state" in transaction_p2:
                #add the reward for policy2 caused by policy1
                transaction_p2["reward"] += p2_reward

                #if policy1 makes it terminated, the p2_state is a terminal state for policy2
                if not terminated:
                    transaction_p2["next_state"] = p2_state
                policy2.update_q_table(**transaction_p2)
            if train_p1:
                transaction_p1 = {"state": p1_state, "action": action, "reward": p1_reward, "next_state": None}
                if terminated:
                    policy1.update_q_table(**transaction_p1)

        elif info["on_move"] == -1:
            action = policy2.decide(p2_state)
            p1_state, (p1_reward, p2_reward), terminated, info = board.step(-1, action)

            #train policy1 and there is a state before p1_state for policy1
            #actually redundant
            if train_p1 and "state" in transaction_p1:
                #add the reward for policy1 caused by policy2
                transaction_p1["reward"] += p1_reward

                #if policy2 makes it terminated, the p1_state is a terminal state for policy1
                if not terminated:
                    transaction_p1["next_state"] = p1_state
                policy1.update_q_table(**transaction_p1)
            if train_p2:
                transaction_p2 = {"state": p2_state, "action": action, "reward": p2_reward, "next_state": None}
                if terminated:
                    policy2.update_q_table(**transaction_p2)

        if terminated:
            break            

    winner = p1_reward
    return winner

if __name__ == "__main__":
    parser = argparse.ArgumentParser("Train Q-Learning agent")
    parser.add_argument("-n", "--num", type=int, required=True, help="The number of games for training")
    args = parser.parse_args()

    board_size = 3, 3
    win_len = 3

    board = TicTacToeBoard(board_size, win_len)
    p1 = QLearningPolicy(marker=1, board_size=board_size)
    p2 = QLearningPolicy(marker=-1, board_size=board_size)

    #define the tester
    test_p1 = RandomPolicy(marker=1, board_size=board_size)
    test_p2 = RandomPolicy(marker=-1, board_size=board_size)

    N = args.num
    hist_p1, hist_p2 = [], []
    for i in range(1, N+1):
        #training part
        p1.set_mode("train")
        p2.set_mode("train")
        run_train(board, p1, p2)
        if i % 1000 == 0:
            #test part
            p1.set_mode("eval")
            p2.set_mode("eval")
            print("game{:9}:".format(i))
            results = [run_test(board, p1, test_p2) for i in range(100)]

            win_rate = len([r for r in results if r == 1]) / len(results)
            lose_rate = len([r for r in results if r == -1]) / len(results)
            tie_rate = len([r for r in results if r == 0]) / len(results)
            hist_p1.append((win_rate, lose_rate, tie_rate))
            print("    QLearningPolicy vs RandomPolicy: p1_win: {:4.0%} p2_win: {:4.0%} tie: {:4.0%}".format(win_rate, lose_rate, tie_rate))

            results = [run_test(board, test_p1, p2) for i in range(100)]

            win_rate = len([r for r in results if r == 1]) / len(results)
            lose_rate = len([r for r in results if r == -1]) / len(results)
            tie_rate = len([r for r in results if r == 0]) / len(results)
            hist_p2.append((lose_rate, win_rate, tie_rate))
            print("    RandomPolicy vs QLearningPolicy: p1_win: {:4.0%} p2_win: {:4.0%} tie: {:4.0%}".format(win_rate, lose_rate, tie_rate))
            
            result = run_test(board, p1, p2)
            print("    Self play: {}".format("p1_win" if result == 1 else ("p2_win" if result == -1 else "tie")))
            print()
    p1.save()
    p2.save()
    
    # Plot part
    if len(hist_p1) > 100:
        def running_average(arr, length):
            ker = np.ones(length) / length
            return np.convolve(arr, ker, mode="valid")
        
        def running_max(arr, length):
            arr = [arr[i:i+length] for i in range(len(arr) - length + 1)]
            arr = np.asarray(arr)
            maxs = np.max(arr, -1)
            return maxs

        def running_min(arr, length):
            arr = [arr[i:i+length] for i in range(len(arr) - length + 1)]
            arr = np.asarray(arr)
            mins = np.min(arr, -1)
            return mins

        x = np.arange(len(hist_p1)) + 1
        p1_win_a, p1_lose_a, p1_tie_a = [running_average(x, 100) for x in zip(*hist_p1)]
        p1_win_max, p1_lose_max, p1_tie_max = [running_max(x, 100) for x in zip(*hist_p1)]
        p1_win_min, p1_lose_min, p1_tie_min = [running_min(x, 100) for x in zip(*hist_p1)]

        x = x[: len(p1_win_a)]

        #Plot for QLearningPolicy as the first player
        plt.figure()
        plt.title("P1 record")
        plt.plot(x, p1_win_a, label="p1_win")
        plt.fill_between(x, p1_win_min, p1_win_max, alpha = 0.5)

        plt.plot(x, p1_lose_a, label="p1_lose")
        plt.fill_between(x, p1_lose_min, p1_lose_max, alpha = 0.5)

        plt.plot(x, p1_tie_a, "--", label="p1_tie")
        plt.fill_between(x, p1_tie_min, p1_tie_max, alpha = 0.5)
        plt.xlim(left=0, right=x[-1])
        plt.ylim(top=1, bottom=0)
        plt.legend()

        p2_win_a, p2_lose_a, p2_tie_a = [running_average(x, 100) for x in zip(*hist_p2)]
        p2_win_max, p2_lose_max, p2_tie_max = [running_max(x, 100) for x in zip(*hist_p2)]
        p2_win_min, p2_lose_min, p2_tie_min = [running_min(x, 100) for x in zip(*hist_p2)]

        #Plot for QLearningPolicy as the second player
        plt.figure()
        plt.title("P2 record")
        plt.plot(x, p2_win_a, label="p2_win")
        plt.fill_between(x, p2_win_min, p2_win_max, alpha = 0.5)

        plt.plot(x, p2_lose_a, label="p2_lose")
        plt.fill_between(x, p2_lose_min, p2_lose_max, alpha = 0.5)

        plt.plot(x, p2_tie_a, "--", label="p2_tie")
        plt.fill_between(x, p2_tie_min, p2_tie_max, alpha = 0.5)
        plt.xlim(left=0, right=x[-1])
        plt.ylim(top=1, bottom=0)
        plt.legend()
        plt.show()
