# -----------------------------------------------------.
# Stage information.
# -----------------------------------------------------.
from pxr import Usd, UsdGeom, UsdShade, Sdf, Gf, Tf
import omni.ext

class StageInfo:
    stageArea   = None
    stageSize   = None

    def __init__(self):
        stageSize  = [10.0 * 200.0, 14.0 * 200.0]

        sx1 = -5.0 * 200.0
        sy1 = -7.0 * 200.0
        sx2 = sx1 + stageSize[0]
        sy2 = sy1 + stageSize[1]
        stageArea = [sx1, sy1, sx2, sy2]


