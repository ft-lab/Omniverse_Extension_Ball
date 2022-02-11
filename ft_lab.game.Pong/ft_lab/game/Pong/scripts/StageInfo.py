# -----------------------------------------------------.
# Stage information.
# -----------------------------------------------------.
from pxr import Usd, UsdGeom, UsdShade, Sdf, Gf, Tf

class StageInfo:
    # Range of movement of the racket in the X direction.
    racketMinX = 0.0
    racketMaxX = 0.0

    # Moving range.
    rangeMinX = 0.0
    rangeMaxX = 0.0
    rangeMinY = 0.0
    rangeMaxY = 0.0

    # Stage info.
    rootPath = '/World'
    stageTemplatePath = rootPath + '/StageTemplate'
    stageAssetsPath   = stageTemplatePath + '/Resources/Assets'
    workPath          = rootPath + '/work'
    ballMaterialPath  = stageTemplatePath + '/Looks/OmniPBR_metal'

    # ball position Y.
    ballYPos = 50.0

    # ball radius.
    ballRadius = 50.0

    def __init__(self):
        self.racketMinX = -5.0 * 200.0
        self.racketMaxX = self.racketMinX + 9.0 * 200.0
        self.racketMinX += 100.0 + 10.0
        self.racketMaxX -= 100.0 + 10.0

        self.rangeMinX = -5.0 * 200.0
        self.rangeMaxX = self.rangeMinX + 9.0 * 200.0
        self.rangeMinY = -7.0 * 200.0
        self.rangeMaxY = self.rangeMinY + 13.0 * 200.0

        self.rangeMinX -= 100.0
        self.rangeMaxX += 100.0
        self.rangeMinY -= 100.0
        self.rangeMaxY += 100.0


