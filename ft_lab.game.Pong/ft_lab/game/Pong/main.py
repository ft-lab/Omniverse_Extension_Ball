from pxr import Usd, UsdGeom, UsdSkel, UsdPhysics, UsdShade, UsdSkel, Sdf, Gf, Tf
import omni.ext
import omni.kit
import carb.events
import omni.usd
import asyncio

from .scripts.CreateStage import CreateStage
from .scripts.InputControl import InputControl
from .scripts.MoveRacket import MoveRacket
from .scripts.StageInfo import StageInfo
from .scripts.BallControl import BallControl
from .scripts.AudioControl import AudioControl
from .scripts.OverlayControl import OverlayControl

# ----------------------------------------------------.
class PongExtension(omni.ext.IExt):
    _inputControl = None
    _createStage  = None
    _moveRacket   = None
    _stageInfo    = None
    _ballList     = None
    _audioControl = None
    _overlayControl = None

    _app = None
    _pre_update_sub = None

    # ------------------------------------------.
    # Update event.
    # ------------------------------------------.
    def _on_pre_update (self, event):
        if self._moveRacket == None:
            return

        # Get Gamepad input.
        moveX = self._inputControl.GetMoveRacketX()

        # Move racket.
        self._moveRacket.MoveRacket(moveX)

        # Update balls.
        for ball in self._ballList:
            ball.updateBall()

    # initialization.
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

    # ------------------------------------------.
    # Extension startup.
    # ------------------------------------------.
    def on_startup (self, ext_id):
        print("[ft_lab.game.Pong] startup")

        self._stageInfo = StageInfo()
        self._createStage = CreateStage(self._stageInfo)
        self._createStage.startup()

        self._inputControl = InputControl()
        self._inputControl.startup()

        self._overlayControl = OverlayControl(self._stageInfo)
        self._overlayControl.startup()

        asyncio.ensure_future(self._initStageData())

        # pre update event.
        self._app = omni.kit.app.get_app()
        self._pre_update_sub = self._app.get_pre_update_event_stream().create_subscription_to_pop(self._on_pre_update)

    # ------------------------------------------.
    # Extension shutdown.
    # ------------------------------------------.
    def on_shutdown(self):
        print("[ft_lab.game.Pong] shutdown")

        self._inputControl.shutdown()
        self._createStage.shutdown()
        self._audioControl.shutdown()
        self._overlayControl.shutdown()

        self._pre_update_sub = None
        self._app  = None



