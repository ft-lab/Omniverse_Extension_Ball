# -----------------------------------------------------.
# State data.
# -----------------------------------------------------.
from enum import Enum
import time

# ---------------------------------------.
# State type.
# ---------------------------------------.
class StateType(Enum):
    NONE  = 0
    TITLE = 1
    GAME = 2
    GAMEOVER = 3

# ---------------------------------------.
# Game message.
# ---------------------------------------.
class GameMessageType(Enum):
    NONE = 0
    GAME_START = 1
    GAME_FAILURE = 2
    GAME_OVER = 3

# ---------------------------------------.
# State data.
# ---------------------------------------.
class StateData:
    state = StateType.NONE
    waitSec = 0.0               # Count the number of seconds to display a message.
    waitEndSec = 0.0

    gameStartWaitSec = 2
    gameFailureWaitSec = 1
    gameoverWaitSec = 3

    gameMessageType = GameMessageType.NONE       

    # Menu selection on the title screen.
    # 0 : GAME, 1 : EXIT
    selectTitleMenu = 0

    def __init__(self):
        self.clear()

    def clear (self):
        self.state = StateType.NONE
        self.gameMessageType = GameMessageType.NONE       
        self.waitSec = 0.0
        self.waitEndSec = 0.0
        self.selectTitleMenu = 0

