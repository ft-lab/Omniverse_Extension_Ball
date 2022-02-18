# -----------------------------------------------------.
# Overlay control (Title screen, score display, game over screen).
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

    # ----------------------------------------------------------.
    # Calculates the reference position in the viewport UI coordinates.
    # return : (posX, posY, Viewport Width, Viewport Height)
    # ----------------------------------------------------------.
    def _getViewportUIOriginPos (self):
        # Get main window viewport.
        viewportI = omni.kit.viewport.acquire_viewport_interface()
        vWindow = viewportI.get_viewport_window(None)

        # Get viewport rect.
        viewportRect = vWindow.get_viewport_rect()
        viewportSize = (viewportRect[2] - viewportRect[0], viewportRect[3] - viewportRect[1])

        captionHeight = 24  # Height of the caption in the Viewport window.
        margin = 2          # frame size.

        # Get Viewport window (UI).
        uiViewportWindow = omni.ui.Workspace.get_window("Viewport")

        # Calculate the origin of the viewport as UI.
        mX = (uiViewportWindow.width - margin * 2.0  - viewportSize[0]) * 0.5
        mY = (uiViewportWindow.height - margin * 2.0 - captionHeight - viewportSize[1]) * 0.5

        return (mX, mY, viewportSize[0], viewportSize[1])

    # ----------------------------------------------------------.
    # Update event.
    # ----------------------------------------------------------.
    def on_update (self, e: carb.events.IEvent):
        # Get Viewport position, size.
        posD = self._getViewportUIOriginPos()
        marginX = posD[0]
        marginY = posD[1]
        viewportWidth  = posD[2]
        viewportHeight = posD[3]

        scoreWidth = 250
        with self._window.frame:
            with omni.ui.ZStack():            
                with omni.ui.VStack(height=0):
                    with omni.ui.Placer(offset_x=marginX + (viewportWidth - scoreWidth) - 4, offset_y=marginY + 4):
                        # Set label.
                        f = omni.ui.Label("SCORE : " + format(self._stageInfo.playerScore, '#010'))
                        f.visible = self._showUI
                        f.set_style({"color": 0xff00ffff, "font_size": 28})

                with omni.ui.VStack(height=0):
                    with omni.ui.Placer(offset_x=marginX + 8, offset_y=marginY + 4):
                        # Set label.
                        f = omni.ui.Label("LIFE : " + str(self._stageInfo.playerLife))
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


