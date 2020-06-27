import control_panel
import numpy as np

if __name__ == '__main__':
    temp = control_panel.ControlPanel("hello")
    temp.start()
    while not temp.is_ready:
        pass
    reversi_board = np.zeros(8 * 8, dtype=np.int).reshape(8, 8)
    reversi_board[3][3] = 1
    reversi_board[3][4] = -1
    reversi_board[4][3] = -1
    reversi_board[4][4] = 1
    print(reversi_board)
    temp.update_board(reversi_board)