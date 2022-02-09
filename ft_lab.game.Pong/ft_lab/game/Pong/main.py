from pxr import Usd, UsdGeom, UsdSkel, UsdPhysics, UsdShade, UsdSkel, Sdf, Gf, Tf
import omni.ext
import carb.events
import omni.usd

from .scripts.CreateStage import CreateStage

# ----------------------------------------------------.
class PongExtension(omni.ext.IExt):
    # ------------------------------------------.
    # Update event.
    # ------------------------------------------.
    def on_update (self, e: carb.events.IEvent):
        pass

    # ------------------------------------------.
    # Extension startup.
    # ------------------------------------------.
    def on_startup (self, ext_id):
        print("[ft_lab.game.Pong] startup")

        _createStage = CreateStage()
        _createStage.startup()

    # ------------------------------------------.
    # Extension shutdown.
    # ------------------------------------------.
    def on_shutdown(self):
        print("[ft_lab.game.Pong] shutdown")

