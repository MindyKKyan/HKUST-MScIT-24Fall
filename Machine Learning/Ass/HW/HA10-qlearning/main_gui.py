import sys
import numpy as np
from PyQt5 import QtCore, QtWidgets, uic
from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QHBoxLayout,
    QVBoxLayout,
    QGridLayout,
    QPushButton,
    QComboBox,
    QLabel,
    QMessageBox,
    QSizePolicy,
)
from PyQt5.QtCore import QRect, pyqtSignal
from PyQt5.QtGui import (
    QPainter,
    QColor,
    QPen,
    QPixmap,
    QPolygon,
)
from tic_tac_toe import TicTacToeBoard
from policy import RandomPolicy, QLearningPolicy

class TicTacToeGui(QMainWindow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        uic.loadUi("./assets_gui/tic_tac_toe.ui", self)
        self.setWindowTitle("TicTacToe!")
        self.board = None
        self.add_game_panel()
        self.add_side_panel()
        self.reset()

    """
    Game Panel, Container for the game board.
    """
    def add_game_panel(self):
        central = self.central
        game_panel = QWidget()
        game_panel.setProperty("style_class", "game_panel")
        board = QTicTacToeBoard()

        layout = QHBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)
        layout.addWidget(board)
        game_panel.setLayout(layout)
        central.layout().addWidget(game_panel)
        self.board = board

    """
    Supporting game agent.
    """
    def set_agent(self):
        if self.agent_selector.currentText() == "Q-Learning":
            Agent = QLearningPolicy
        else:
            Agent = RandomPolicy

        if self.role_selector.currentText() == "X: Player1":
            self.agent = Agent(-1)
        else:
            self.agent = Agent(1)
        self.board.step_finish.connect(self.agent_step)

    """
    Automatically step the agent.
    """
    def agent_step(self, state):
        marker = self.agent.marker
        if marker == self.board.on_move:
            self.board.step(marker, self.agent.decide(state))

    """
    Side Panel, Container for controller.
    """
    def add_side_panel(self):
        central = self.central
        side_panel = QWidget()
        side_panel.setProperty("style_class", "side_panel")
        side_panel.setMaximumWidth(200)
        side_panel_layout = QVBoxLayout()

        side_panel_layout.addWidget(QLabel("Please Select Your Role:"))
        role_selector = QComboBox()
        #role_selector.setView(QtWidgets.QListView())
        role_selector.addItems(["X: Player1", "O: Player2"])
        side_panel_layout.addWidget(role_selector)
        self.role_selector = role_selector

        role_selector.currentIndexChanged.connect(self.on_change_setting)

        side_panel_layout.addWidget(QLabel("Please Select Your Opponent:"))
        agent_selector = QComboBox()
        #agent_selector.setView(QtWidgets.QListView())
        agent_selector.addItems(["Random", "Q-Learning"])
        side_panel_layout.addWidget(agent_selector)
        self.agent_selector = agent_selector
        agent_selector.currentIndexChanged.connect(self.on_change_setting)

        side_panel_layout.addStretch()
        reset_button = QPushButton()
        reset_button.setText("restart")
        reset_button.setObjectName("restart")
        reset_button.clicked.connect(self.reset)
        side_panel_layout.addWidget(reset_button)

        side_panel.setLayout(side_panel_layout)
        central.layout().addWidget(side_panel)

    def on_change_setting(self):
        if self.board.board.counter == 0:
            #No action yet.
            self.reset()
        else:
            self.statusBar().showMessage("Config changed! Please click the restart to enable your setting!")

    """
    Reset
    """
    def reset(self):
        self.statusBar().clearMessage()
        self.set_agent()
        self.board.reset()


"""
A wrapped TicTacToeBoard, to give GUI.
"""
class QTicTacToeBoard(QWidget):

    """
    Signals when there is a move, to notify any existing agent.
    """
    step_finish = pyqtSignal(np.ndarray)

    def __init__(self, size=(3,3), *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setObjectName("board")
        self.setAttribute(QtCore.Qt.WA_StyledBackground, True)
        self.cells = []

        grid = QGridLayout()
        grid.setContentsMargins(0, 0, 0, 0)
        self.setLayout(grid)

        self.size = size
        self.board = TicTacToeBoard(size)
        #For drawing a line when game finished.
        self.check_cells = []
        self.reset()

    def step(self, Policy, position):
        i, j = position
        state, reward, terminated, info = self.board.step(Policy, position)
        self.sync_cells()
        if self.board.terminated == True:
            if info["coordinates"] is not None:
                for i, j in info["coordinates"]:
                    self.check_cells.append(self.cells[i][j])
            if reward[0] == 1:
                result_str = "X: Player 1 won!"
            elif reward[0] == -1:
                result_str = winner = "O: Player 2 won!"
            else:
                result_str = "Draw!"
            QMessageBox.information(self, "Game Finish", result_str)
        else:
            self.step_finish.emit(state)

    def reset(self):
        self.cells = []
        state, *_ = self.board.reset()
        self.make_cells()        
        self.check_cells = []
        self.step_finish.emit(state)

    @property
    def on_move(self):
        return self.board.on_move

    """
    Make M*N cells in grid, where M, N = size.
    """
    def make_cells(self):
        grid = self.layout()
        for i in reversed(range(grid.count())):
            grid.itemAt(i).widget().deleteLater()

        n_row, n_col = self.size
        for i in range(n_row):
            self.cells.append([])
            for j in range(n_col):
                cell = Cell(self, loc=(i, j))
                cell.clicked.connect(cell.click)
                grid.addWidget(cell, i+1, j+1)
                self.cells[i].append(cell)

    """
    Synchronize the cell buttons according to the state.
    """
    def sync_cells(self):
        for i, row in enumerate(self.board.board):
            for j, cell_val in enumerate(row):
                cell = self.cells[i][j]
                if self.board.terminated:
                    cell.setEnabled(False)
                if cell_val != 0:
                    if cell_val == 1:
                        cell.setStyleSheet("border-image: url(./assets_gui/cross.svg) 0 0 0 0 stretch stretch")
                    else:
                        cell.setStyleSheet("border-image: url(./assets_gui/circle.svg) 0 0 0 0 stretch stretch")
                    cell.setEnabled(False)
                    #cell.style().unpolish(cell)
                    cell.style().polish(cell)
    """
    Draw lines on cells connected.
    """
    def paintEvent(self, event):
        super().paintEvent(event)
        if len(self.check_cells) > 2:
            points = []
            for cell in self.check_cells:
                center = cell.rect().center()
                location = cell.mapToParent(center)
                points.append(location)
            start_offset = (points[0] - points[1])/4
            end_offset = (points[-1] - points[-2])/4
            points[0] += start_offset
            points[-1] += end_offset

            pen = QPen(QColor(150, 100, 100, 150))
            pen.setWidth(self.width()//27)
            painter = QPainter(self)
            painter.setPen(pen)
            polyline = QPolygon(points)
            painter.drawPolyline(polyline)
            painter.end()
            for row in self.cells:
                for cell in row:
                    pixmap = QPixmap(cell.size())
                    pixmap.fill(QColor(0,0,0,0))
                    painter = QPainter(pixmap)
                    painter.setPen(pen)
                    polyline = QPolygon([cell.mapFromParent(point) for point in points])
                    painter.drawPolyline(polyline)
                    painter.end()
                    cell.pixmap = pixmap

    """
    Maintain the aspect ratio.
    """
    def resizeEvent(self, event):
        super().resizeEvent(event)
        height, width = self.height(), self.width()

        center = self.parent().rect().center()
        length = min(height, width)
        self.layout().setSpacing(length // 40)
        rect = QRect(0, 0, length, length)
        rect.moveCenter(center)
        self.setGeometry(rect)

        
class Cell(QPushButton):
    def __init__(self, board, loc, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.board = board
        self.loc = loc
        self.setProperty("style_class", "board_cell")
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.pixmap = QPixmap()

    def click(self):
        res = self.board.step(self.board.on_move, self.loc)

    def paintEvent(self, event):
        super().paintEvent(event)
        painter = QPainter(self)
        painter.drawPixmap(0, 0, self.pixmap)

if __name__ == "__main__": 
    app = QApplication(sys.argv)
    window = TicTacToeGui()
    with open("./assets_gui/theme.qss", "r") as f:
        style_sheet = f.read()
    window.setStyleSheet(style_sheet)
    window.show()
    app.exec()
