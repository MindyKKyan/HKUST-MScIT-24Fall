# -*- coding: utf-8 -*-
import numpy as np

def np_conv2d(x, ker):
    """
    calculate the 2d convolution of x and y.
    
    Args:
        x (2d numpy array): the input.
        ker (2d numpy array): the kernel.

    Return:
        out (2d numpy array): the valid convolution result.
    """
    sliding_windows = np.lib.stride_tricks.sliding_window_view(x, ker.shape)
    out = sliding_windows.reshape(*sliding_windows.shape[:2], -1).dot(
        ker.flatten()
    )
    return out

class TicTacToeBoard:
    __doc__ = r"""
    A game board for tic-tac-toe.
    * :attr:`board` a two dimensional numpy array of type int.
      It contains only 1 (for first player), -1 (for second player), 0 (empty cell).

    * :attr:`counter` a int records how many steps have been taken in total.

    * :attr:`on_move` indicates who should make move now. 
      Value of "on_move" can either be 1 indicating the first player should make move next
      or -1 indicating it's the second player's turn.

    * :attr:`terminated` indicates whether the game ends in "terminate".

    * :attr:`win_len` indicates the number of markers the corresponding player required to place in a line to win
    
    Args:
        size (tuple of (int, int), optional): The size of the game board, default to be (3, 3)

        length (int, optional): The number of markers the corresponding player required to place in a line to win,
                default to be `min(size)`
    """
    def __init__(self, size=(3, 3), length=None):
        self.board = np.zeros(size, dtype=int)
        self.win_len = length if length else min(size)
        self.counter = 0
        self.on_move = 1
        self.terminated = False

    def _check_board(self):
        """
        Check the status of the board to find if any player places 
        the corresponding marker in a line of length specified.

        Returns:
            winner (int): can be 1 indicating the first player won,
                -1 indicating the second player won,
                or 0, means no winner, possibly tie.

            terminate (bool): tells if the game has end.

            coordinates (ndarray or None): a array of coordinates of the same markers forming a line.
                The value is None when there is no winner.
        """
        length = self.win_len
        # check if board only contains -1, 0, 1
        assert all(
            map(lambda x: x in [-1, 0, 1], np.unique(self.board))
        ), "Something impossible happened!"

        # check consecutive 1 or -1 using 2d convolution
        ker_horizontal, ker_diagonal = np.ones((1, length)), np.eye(length) #kernel for checking horizonally and diagonally
        ker_vertical, ker_antidiagonal = np.rot90(ker_horizontal), np.rot90(ker_diagonal) #kernel for checking vertically and antidiagonally
        kernels = [ker_horizontal, ker_vertical, ker_diagonal, ker_antidiagonal]
        kernels_bases = []
        for ker in kernels:
            #coordinates of 1s in the kernel
            kernels_bases.append(np.stack(np.where(ker == 1), -1))

        checks = [np_conv2d(self.board, ker) for ker in kernels]
        p1_coordinates = []
        #Find coordinates of marker 1 forming lines
        for check, bases in zip(checks, kernels_bases):
            offsets = np.stack(np.where(check == length), -1)
            coords = offsets[:, None] + bases
            coords = coords.reshape(-1, coords.shape[-1])
            p1_coordinates.append(coords)
        p1_coordinates = np.concatenate(p1_coordinates)
        p1_win = len(p1_coordinates) > 0

        #Find coordinates of marker -1 forming lines
        p2_coordinates = []
        for check, bases in zip(checks, kernels_bases):
            offsets = np.stack(np.where(check == -length), -1)
            coords = offsets[:, None] + bases
            coords = coords.reshape(-1, coords.shape[-1])
            p2_coordinates.append(coords)
        p2_coordinates = np.concatenate(p2_coordinates)
        p2_win = len(p2_coordinates) > 0

        assert p1_win != p2_win or p1_win == 0, "Something impossible happened!"
        terminated = p1_win or p2_win or np.all(self.board != 0)
        if p1_win:
            return 1, terminated, p1_coordinates
        if p2_win:
            winner = -1
            coordinates = p2_coordinates
        else:
            winner = 0
            coordinates = None
        return winner, terminated, coordinates


    def reset(self):
        """
        Reset the game board.

        Returns:
            state (ndarray): the game board, represented in 2d numpy array of type int.
                It contains only 1 (for first player), -1 (for second player), 0 (empty cell).

            info (dict): a dict keeps who should make move now as "on_move", and the connected markers' coordinates as "coordinates" 
                Value of "on_move" can either be 1 indicating the first player should make move next
                or -1 indicating it's the second player's turn.

                Coordinates can be a ndarray as markers' coordinates connected in a line.
                The value is None when there is no winner.
        """
        self.counter = 0
        self.board[:] = 0
        self.on_move = 1
        self.terminated = False
        info = {"on_move": self.on_move, "coordinates": None}
        return np.copy(self.board), info

    def step(self, player, position):
        """
        Apply action to the game board.

        Args:
            player (int): can either be 1 indicating the first player or -1 indicating the second.

            position (tuple of (int, int)): the coordinates of the position to place the marker.
                Starting from 0.

        Returns:
            state (ndarray): the game board, represented in 2d numpy array of type int.
                It contains only 1 (for first player), -1 (for second player), 0 (empty cell).

            reward (tuple of (float, float)): the rewards for the first player and the second player,
                respectively.
            
            terminated (boolean): whether the game has ended.

            info (dict): a dict keeps who should make move now as "on_move", and the connected marker coordinates as "coordinates" 
                Value of "on_move" can either be 1 indicating the first player should make move next
                or -1 indicating it's the second player's turn.

                Coordinates can be a ndarray as markers' coordinates connected in a line.
                The value is None when there is no winner.
        """
        assert player == self.on_move, "Not this player's turn!"
        assert self.board[position] == 0, "Position already occupied!"
        #set the marker
        self.board[position] = player

        #update counter
        self.counter += 1
        #get reward of 1 if win or -1 if lose and 0 if tie
        p1_reward, terminated, coordinates = self._check_board()
        p2_reward = -p1_reward
        reward = (p1_reward, p2_reward)

        #switch player
        self.on_move = -1 if player == 1 else 1
        self.terminated = terminated

        info = {"on_move": self.on_move, "coordinates": coordinates}
        return np.copy(self.board), reward, terminated, info


