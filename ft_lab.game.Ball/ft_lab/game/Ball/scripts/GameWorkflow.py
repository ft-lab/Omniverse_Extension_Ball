# -----------------------------------------------------.
# Game Workflow.
# All game manage the flow here.
# -----------------------------------------------------.
from pxr import Usd, UsdGeom, UsdShade, Sdf, Gf, Tf
import omni.ext
import omni.usd

import asyncio

from .StageInfo import StageInfo
from .StateData import StateData, StateType
from .InputControl import InputControl
from .CreateStage import CreateStage
from .MoveRacket import MoveRacket
from .AudioControl import AudioControl
from .OverlayControl import OverlayControl
from .BallControl import BallControl
from .ChangePostProcessing import ChangePostProcessing

class GameWorkflow:
    _stageInfo = None
    _stateData = None
    _inputControl = None
    _createStage  = None
    _moveRacket   = None
    _ballList     = None
    _audioControl = None
    _overlayControl = None

    _app = None
    _pre_update_sub = None

    def __init__(self):
        pass
    
    # ------------------------------------------.
    # Update event (Title).
    # ------------------------------------------.
    def _pre_update_title (self):
        # Get Gamepad/keyboard input.
        menuV = self._inputControl.GetUpDown_TitleMenu()
        if menuV != None:
            # Push [UP][DOWN].
            if menuV[0] or menuV[1]:
                if self._stateData.selectTitleMenu == 0:
                    if menuV[1]:
                        self._stateData.selectTitleMenu = 1
                elif self._stateData.selectTitleMenu == 1:
                    if menuV[0]:
                        self._stateData.selectTitleMenu = 0
            # Push [Enter].
            if menuV[2]:
                # Game start.
                if self._stateData.selectTitleMenu == 0:
                    self._stateData.state = StateType.GAME

                # Exit.
                if self._stateData.selectTitleMenu == 1:
                    self.GameExit()

    # ------------------------------------------.
    # Update event (Game).
    # ------------------------------------------.
    def _pre_update_game (self):
        # Get Gamepad/keyboard input.
        moveX = self._inputControl.GetMoveRacketX()

        # Move racket.
        if self._moveRacket != None:
            self._moveRacket.MoveRacket(moveX)

        # Update balls.
        if self._ballList != None:
            for ball in self._ballList:
                ball.updateBall()

    # ------------------------------------------.
    # Update event.
    # ------------------------------------------.
    def _on_pre_update (self, event):
        if self._moveRacket == None or self._inputControl == None or self._stateData == None:
            return

        # if title,
        if self._stateData.state == StateType.TITLE:
            self._pre_update_title()

        # if game.
        elif self._stateData.state == StateType.GAME:
            self._pre_update_game()

    # ------------------------------------------.
    # initialization.
    # ------------------------------------------.
    async def _initStageData (self):
        await omni.kit.app.get_app().next_update_async()
        self._moveRacket = MoveRacket(self._stageInfo)
        self._moveRacket.startup()

        self._audioControl = AudioControl()
        self._audioControl.startup()

        self._ballList = []
        for i in range(1):
            self._ballList.append(BallControl(self._stageInfo, self._moveRacket, self._audioControl, i))
            self._ballList[i].startup()

        self._overlayControl = OverlayControl(self._stageInfo, self._stateData)
        self._overlayControl.startup()

    # ------------------------------------------.
    # Game Start.
    # ------------------------------------------.
    def GameStart (self):
        if self._app != None:
            self.GameExit()

        self._stateData = StateData()
        self._stateData.state = StateType.TITLE

        self._stageInfo = StageInfo()
        self._createStage = CreateStage(self._stageInfo)
        self._createStage.startup()

        self._inputControl = InputControl()
        self._inputControl.startup()

        asyncio.ensure_future(self._initStageData())

        # pre update event.
        self._app = omni.kit.app.get_app()
        self._pre_update_sub = self._app.get_pre_update_event_stream().create_subscription_to_pop(self._on_pre_update)

        # Change post processing parameters.
        async def _change_post_processing ():
            await omni.kit.app.get_app().next_update_async()
            postProcessing = ChangePostProcessing()
            postProcessing.Change()
        asyncio.ensure_future(_change_post_processing())

    # ------------------------------------------.
    # Game Exit.
    # ------------------------------------------.
    def GameExit (self):
        if self._app == None:
            return

        self._inputControl.shutdown()
        self._createStage.shutdown()
        self._audioControl.shutdown()
        self._overlayControl.shutdown()

        self._ballList = []
        self._pre_update_sub = None
        self._app  = None

