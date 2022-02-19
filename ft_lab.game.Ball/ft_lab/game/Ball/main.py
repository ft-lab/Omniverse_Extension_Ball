from pxr import Usd, UsdGeom, UsdSkel, UsdPhysics, UsdShade, UsdSkel, Sdf, Gf, Tf
import omni.ext
import omni.kit
import carb.events
import omni.usd

import omni.kit.commands
import omni.kit.menu.utils
from omni.kit.menu.utils import MenuItemDescription

import asyncio

from .scripts.GameWorkflow import GameWorkflow

# ----------------------------------------------------.
class WallTennisExtension(omni.ext.IExt):
    _gameWorkflow = None

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
    # Start from menu.
    # ------------------------------------------.
    def _menu_start (self):
        if self._gameWorkflow != None:
            self._gameWorkflow.GameExit()
            self._gameWorkflow = None

        self._gameWorkflow = GameWorkflow()
        self._gameWorkflow.GameStart()

    # ------------------------------------------.
    # Edit from menu.
    # ------------------------------------------.
    def _menu_exit (self):
        if self._gameWorkflow == None:
            return
        self._gameWorkflow.GameExit()

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




