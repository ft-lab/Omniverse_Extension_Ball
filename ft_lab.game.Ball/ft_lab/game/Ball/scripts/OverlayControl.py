# -----------------------------------------------------.
# Overlay control.
# -----------------------------------------------------.
from pxr import Usd, UsdGeom, UsdShade, Sdf, Gf, Tf
import omni.ui
import omni.kit.app
import carb.events
import time
import asyncio

from .StageInfo import StageInfo

class OverlayControl:
    _stageInfo = None
    _subs = None
    _window = None
    _showUI = True

    def __init__(self, stageInfo : StageInfo):
        self._stageInfo = stageInfo

    def _getViewportRect (self):
        # Get main window viewport.
        viewportI = omni.kit.viewport.acquire_viewport_interface()
        vWindow = viewportI.get_viewport_window(None)

        # Get viewport rect.
        viewportRect = vWindow.get_viewport_rect()
        viewportSize = (viewportRect[2] - viewportRect[0], viewportRect[3] - viewportRect[1])
        return viewportSize

    def on_update (self, e: carb.events.IEvent):
        # Get viewport size.
        rec = self._getViewportRect()

        with self._window.frame:
            with omni.ui.VStack(height=0):
                with omni.ui.Placer(offset_x=rec[0] - 250, offset_y=50):
                    # Set label.
                    f = omni.ui.Label("SCORE : " + format(self._stageInfo.playerScore, '#010'))
                    f.visible = self._showUI
                    f.set_style({"color": 0xff00ffff, "font_size": 28})

    def startup (self):
        # Get main window viewport.
        self._window = omni.ui.Window('Viewport') 
        self._subs = omni.kit.app.get_app().get_update_event_stream().create_subscription_to_pop(self.on_update)
        self._showUI = True

    def shutdown (self):
        async def _wait_update ():
            self._showUI = False
            await omni.kit.app.get_app().next_update_async()
            self._subs = None

        asyncio.ensure_future(_wait_update())


