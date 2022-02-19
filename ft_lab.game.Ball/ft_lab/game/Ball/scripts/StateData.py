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
# State data.
# ---------------------------------------.
class StateData:
    state = StateType.NONE
    waitCount = 0

    # Menu selection on the title screen.
    # 0 : GAME, 1 : EXIT
    selectTitleMenu = 0

    def __init__(self):
        self.clear()

    def clear (self):
        self.state = StateType.NONE
        self.waitCount = 0
        self.selectTitleMenu = 0

