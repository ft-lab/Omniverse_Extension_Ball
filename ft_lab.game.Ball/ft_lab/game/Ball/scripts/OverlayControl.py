# -----------------------------------------------------.
# Overlay control (Title screen, score display, game over screen).
# -----------------------------------------------------.
from pxr import Usd, UsdGeom, UsdShade, Sdf, Gf, Tf
import omni.ui
import omni.kit.app
import carb.events
import time
import asyncio
from pathlib import Path

from .StageInfo import StageInfo
from .StateData import StateData, StateType
from .LoadImageRGBA import LoadImageRGBA

class OverlayControl:
    _stageInfo = None
    _stateData = None
    _subs = None
    _window = None
    _showUI = True

    _titleImagePath = ""
    _titleImage = None

    def __init__(self, stageInfo : StageInfo, stateData : StateData):
        self._stageInfo = stageInfo
        self._stateData = stateData

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
        margin = 4          # frame size.

        # Get Viewport window (UI).
        uiViewportWindow = omni.ui.Workspace.get_window("Viewport")

        # Calculate the origin of the viewport as UI.
        mX = (uiViewportWindow.width - margin * 2.0  - viewportSize[0]) * 0.5
        mY = (uiViewportWindow.height - margin * 2.0 - captionHeight - viewportSize[1]) * 0.5

        # if full screen.
        if mX < 0 or mY < 0:
            mX = 0.0
            mY = 0.0

        return (mX, mY, viewportSize[0], viewportSize[1])

    # ----------------------------------------------------------.
    # State : Title
    # ----------------------------------------------------------.
    def _showStateTitle (self, e: carb.events.IEvent, posD):
        marginX = posD[0]
        marginY = posD[1]
        viewportWidth  = posD[2]
        viewportHeight = posD[3]

        aspectV = 800.0 / 309.0
        tWid = viewportWidth * 0.7
        tHei = tWid / aspectV
        tX = (viewportWidth - tWid) * 0.5 + marginX
        tY = marginY

        fontHeight = viewportHeight * 0.08

        with self._window.frame:
            with omni.ui.ZStack():
                # Darken the viewport.
                with omni.ui.VStack(height=0):
                    with omni.ui.Placer(offset_x=marginX, offset_y=marginY):
                        if self._showUI:
                            omni.ui.Rectangle(style={"background_color": 0x80000000}, width=viewportWidth, height=viewportHeight)

                # Draw title image.
                with omni.ui.VStack(height=0):
                    with omni.ui.Placer(offset_x=tX, offset_y=tY):
                        # "omni.ui.Image" cannot be used with "get_update_event_stream().create_subscription_to_pop".
                        # Use "omni.ui.ImageWithProvider" instead.
                        if self._titleImage != None:
                            byte_provider = self._titleImage.GetByteProvider()
                            img = omni.ui.ImageWithProvider(byte_provider, width=tWid, height=tHei)
                            img.visible = self._showUI

                # Menu (GAME / EXIT).
                px = (viewportWidth - fontHeight * 4) * 0.5 + marginX
                py = (viewportHeight - fontHeight) * 0.7 + marginY
                with omni.ui.VStack(height=0):
                    with omni.ui.Placer(offset_x=px, offset_y=py):
                        # Set label.
                        f = omni.ui.Label("GAME")
                        f.visible = self._showUI
                        f.set_style({"color": 0xff00ffff, "font_size": fontHeight})

                with omni.ui.VStack(height=0):
                    with omni.ui.Placer(offset_x=px, offset_y=py + fontHeight * 1.2):
                        f2 = omni.ui.Label("EXIT")
                        f2.visible = self._showUI
                        f2.set_style({"color": 0xff00ffff, "font_size": fontHeight})

                # Menu Cursor.
                cursor_x = px - fontHeight * 1.0
                cursor_y = py
                if self._stateData.selectTitleMenu == 1:
                    cursor_y += fontHeight * 1.2

                with omni.ui.VStack(height=0):
                    with omni.ui.Placer(offset_x=cursor_x, offset_y=cursor_y):
                        # Set label.
                        f = omni.ui.Label(">")
                        f.visible = self._showUI
                        f.set_style({"color": 0xff00ffff, "font_size": fontHeight})

    # ----------------------------------------------------------.
    # State : Game
    # ----------------------------------------------------------.
    def _showStateGame (self, e: carb.events.IEvent, posD):
        marginX = posD[0]
        marginY = posD[1]
        viewportWidth  = posD[2]
        viewportHeight = posD[3]

        fontHeight = viewportHeight * 0.08
        scoreWidth = fontHeight * 8.5
        fontHeightSpace = fontHeight * 0.5

        with self._window.frame:
            with omni.ui.ZStack():
                with omni.ui.VStack(height=0):
                    with omni.ui.Placer(draggable=True, offset_x=marginX + (viewportWidth - scoreWidth) - 4, offset_y=marginY + fontHeightSpace):
                        # Set label.
                        f = omni.ui.Label("SCORE : " + format(self._stageInfo.playerScore, '#010'))
                        f.visible = self._showUI
                        f.set_style({"color": 0xff00ffff, "font_size": fontHeight})

                with omni.ui.VStack(height=0):
                    with omni.ui.Placer(draggable=True, offset_x=marginX + fontHeight * 0.5, offset_y=marginY + fontHeightSpace):
                        # Set label.
                        f = omni.ui.Label("LIFE : " + str(self._stageInfo.playerLife))
                        f.visible = self._showUI
                        f.set_style({"color": 0xff00ffff, "font_size": fontHeight})

    # ----------------------------------------------------------.
    # Update event.
    # ----------------------------------------------------------.
    def on_update (self, e: carb.events.IEvent):
        # Get Viewport position, size.
        posD = self._getViewportUIOriginPos()

        if self._stateData.state == StateType.TITLE:
            self._showStateTitle(e, posD)
        elif self._stateData.state == StateType.GAME:
            self._showStateGame(e, posD)

    def startup (self):
        imgPath = Path(__file__).parent.parent.joinpath("resources").joinpath("images")
        imgPath = f"{imgPath}/title.png"

        # Load title image.
        self._titleImage = LoadImageRGBA()
        if not self._titleImage.Open(imgPath):
            self._titleImage = None

        # Get main window viewport.
        self._window = omni.ui.Window('Viewport') 
        self._showUI = True
        self._subs = omni.kit.app.get_app().get_update_event_stream().create_subscription_to_pop(self.on_update)

    def shutdown (self):
        async def _wait_update ():
            self._showUI = False
            await omni.kit.app.get_app().next_update_async()
            self._subs = None

        asyncio.ensure_future(_wait_update())


