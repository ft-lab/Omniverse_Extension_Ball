# -----------------------------------------------------.
# Game Workflow.
# All game manage the flow here.
# -----------------------------------------------------.
from pxr import Usd, UsdGeom, UsdShade, Sdf, Gf, Tf
import omni.ext
import omni.usd
import omni.kit
import carb.settings

import asyncio
import time

from .StageInfo import StageInfo
from .StateData import StateData, StateType, GameMessageType
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
   
    # -----------------------------------------------.
    # Change Path-Traced.
    # -----------------------------------------------.
    async def _setPathTraced (self):
        await omni.kit.app.get_app().next_update_async()
        settings = carb.settings.get_settings()
        settings.set('/rtx/rendermode', 'PathTracing')

    # -----------------------------------------------.
    # Change resolution (1280 x 720).
    # -----------------------------------------------.
    async def _setResolution_1280x720 (self):
        await omni.kit.app.get_app().next_update_async()
        settings = carb.settings.get_settings()

        width  = settings.get('/app/renderer/resolution/width')
        height = settings.get('/app/renderer/resolution/height')
        if width != 1280 or height != 720:
            settings.set('/app/renderer/resolution/width', 1280)
            settings.set('/app/renderer/resolution/height', 720)

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
                        self._audioControl.play(1)  # Play sound.
                elif self._stateData.selectTitleMenu == 1:
                    if menuV[0]:
                        self._stateData.selectTitleMenu = 0
                        self._audioControl.play(1)  # Play sound.

            # Push [Enter].
            if menuV[2]:
                # Game start.
                if self._stateData.selectTitleMenu == 0:
                    self._stateData.state = StateType.GAME
                    self._stateData.gameMessageType = GameMessageType.GAME_START

                    self._stateData.waitSec    = time.time()
                    self._stateData.waitEndSec = self._stateData.waitSec + self._stateData.gameStartWaitSec

                    self._audioControl.play(0)  # Play sound.

                # Exit.
                if self._stateData.selectTitleMenu == 1:
                    self.GameExit()

    # ------------------------------------------.
    # Update event (Game).
    # ------------------------------------------.
    def _pre_update_game (self):
        # Display a message and wait for a certain amount of time.
        if self._stateData.waitSec < self._stateData.waitEndSec:
            self._stateData.waitSec = time.time()
            return

        # Change the position of the ball.
        if self._stateData.gameMessageType == GameMessageType.GAME_FAILURE:
            if self._ballList != None:
                for ball in self._ballList:
                    ball.resetBallPosition()

            if self._stageInfo.playerLife > 0:
                self._stageInfo.playerLife -= 1

        self._stateData.gameMessageType = GameMessageType.NONE

        # Get Gamepad/keyboard input.
        moveX = self._inputControl.GetMoveRacketX()

        # Move racket.
        if self._moveRacket != None:
            self._moveRacket.MoveRacket(moveX)

        # Update balls.
        outOfRange = False
        if self._ballList != None:
            for ball in self._ballList:
                ball.updateBall()
                if ball.checkOutOfRange():
                    outOfRange = True

        # The ball went out of range ==> Failure!.
        if outOfRange:
            self._stateData.gameMessageType = GameMessageType.GAME_FAILURE
            self._stateData.waitSec    = time.time()
            self._stateData.waitEndSec = self._stateData.waitSec + self._stateData.gameFailureWaitSec

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

        # Set "RTX Path-traced"
        asyncio.ensure_future(self._setPathTraced())

        # Set Resolution(1280 x 720).
        #asyncio.ensure_future(self._setResolution_1280x720())

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

