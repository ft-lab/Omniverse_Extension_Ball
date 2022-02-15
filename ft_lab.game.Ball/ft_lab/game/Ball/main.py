from pxr import Usd, UsdGeom, UsdSkel, UsdPhysics, UsdShade, UsdSkel, Sdf, Gf, Tf
import omni.ext
import omni.kit
import carb.events
import omni.usd

import omni.kit.commands
import omni.kit.menu.utils
from omni.kit.menu.utils import MenuItemDescription

import asyncio

from .scripts.CreateStage import CreateStage
from .scripts.InputControl import InputControl
from .scripts.MoveRacket import MoveRacket
from .scripts.StageInfo import StageInfo
from .scripts.BallControl import BallControl
from .scripts.AudioControl import AudioControl
from .scripts.OverlayControl import OverlayControl

# ----------------------------------------------------.
class WallTennisExtension(omni.ext.IExt):
    _game_start = False
    _inputControl = None
    _createStage  = None
    _moveRacket   = None
    _stageInfo    = None
    _ballList     = None
    _audioControl = None
    _overlayControl = None

    _app = None
    _pre_update_sub = None

    # Menu list.
    _menu_list = None
    _sub_menu_list = None

    # Menu name.
    _menu_name = "Game"

    # ------------------------------------------.
    # Initialize menu.
    # ------------------------------------------.
    def _init_menu (self):
        async def _rebuild_menus ():
            await omni.kit.app.get_app().next_update_async()
            omni.kit.menu.utils.rebuild_menus()

        def menu_select (mode):
            if mode == 1:
                self._menu_start()

            if mode == 2:
                self._menu_exit()

        self._sub_menu_list = [
            MenuItemDescription(name="Start/Reset", onclick_fn=lambda: menu_select(1)),
            MenuItemDescription(name="Exit", onclick_fn=lambda: menu_select(2)),
        ]

        self._menu_list = [
            MenuItemDescription(name="Ball", sub_menu=self._sub_menu_list),
        ]

        # Rebuild with additional menu items.
        omni.kit.menu.utils.add_menu_items(self._menu_list, self._menu_name)
        asyncio.ensure_future(_rebuild_menus())

    # ------------------------------------------.
    # Term menu.
    # It seems that the additional items in the top menu will not be removed.
    # ------------------------------------------.
    def _term_menu (self):
        async def _rebuild_menus ():
            await omni.kit.app.get_app().next_update_async()
            omni.kit.menu.utils.rebuild_menus()
        
        # Remove and rebuild the added menu items.
        omni.kit.menu.utils.remove_menu_items(self._menu_list, self._menu_name)
        asyncio.ensure_future(_rebuild_menus())

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
    # Start from menu.
    # ------------------------------------------.
    def _menu_start (self):
        if self._app != None:
            self._menu_exit()

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
    # Edit from menu.
    # ------------------------------------------.
    def _menu_exit (self):
        if self._app == None:
            return

        self._inputControl.shutdown()
        self._createStage.shutdown()
        self._audioControl.shutdown()
        self._overlayControl.shutdown()

        self._pre_update_sub = None
        self._app  = None

    # ------------------------------------------.
    # Extension startup.
    # ------------------------------------------.
    def on_startup (self, ext_id):
        print("[ft_lab.game.Ball] startup")

        # Initialize menu.
        self._init_menu()

    # ------------------------------------------.
    # Extension shutdown.
    # ------------------------------------------.
    def on_shutdown(self):
        print("[ft_lab.game.Ball] shutdown")

        # Term menu.
        self._term_menu()

        self._menu_exit()




