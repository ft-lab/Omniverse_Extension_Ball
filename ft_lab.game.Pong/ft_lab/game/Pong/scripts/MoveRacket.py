# -----------------------------------------------------.
# Move Racket.
# -----------------------------------------------------.
from pxr import Usd, UsdGeom, UsdShade, Sdf, Gf, Tf
import omni.ext
import omni.usd

from .StageInfo import StageInfo

class MoveRacket:
    _stageInfo  = None
    _racketPrim = None

    # -------------------------------------------.
    # Create Racket Prim.
    # -------------------------------------------.
    def _getRacketPrim (self):
        stage = omni.usd.get_context().get_stage()

        rootPath = '/World'
        orgAssetsPath = rootPath + '/StageTemplate/Resources/Assets'
        racketOrgPath = orgAssetsPath + '/racket'

        # Create Racket.
        workPath = rootPath + '/work'
        racketPath = workPath + '/racket'
        UsdGeom.Xform.Define(stage, racketPath)

        prim = stage.GetPrimAtPath(racketPath)
        prim.CreateAttribute("xformOp:translate", Sdf.ValueTypeNames.Float3, False).Set(Gf.Vec3f(0, 10, 1140))
        prim.CreateAttribute("xformOp:scale", Sdf.ValueTypeNames.Float3, False).Set(Gf.Vec3f(100, 100, 100))
        prim.CreateAttribute("xformOp:rotateXYZ", Sdf.ValueTypeNames.Float3, False).Set(Gf.Vec3f(-90, 0, 0))
        transformOrder = prim.CreateAttribute("xformOpOrder", Sdf.ValueTypeNames.String, False)
        transformOrder.Set(["xformOp:translate", "xformOp:rotateXYZ", "xformOp:scale"])

        prim.GetReferences().ClearReferences()
        prim.GetReferences().AddInternalReference(racketOrgPath)

        return prim

    def __init__(self, stageInfo : StageInfo):
        self._stageInfo = stageInfo

    def startup (self):
        self._racketPrim = self._getRacketPrim()

    def shutdown (self):
        pass

    # -------------------------------------------.
    # Get racket position.
    # -------------------------------------------.
    def GetRacketPosition (self):
        pos = Gf.Vec3f(0.0, 0.0, 0.0) 
        if self._racketPrim == None:
            return pos

        tV = self._racketPrim.GetAttribute("xformOp:translate")
        if tV.IsValid():
            pos = Gf.Vec3f(tV.Get())
        return pos

    # -------------------------------------------.
    # Get racket size.
    # -------------------------------------------.
    def GetRacketSize (self):
        return Gf.Vec3f(200.0, 100.0, 100.0) 

    # -------------------------------------------.
    # Move the racket.
    # -------------------------------------------.
    def MoveRacket (self, moveX : float):
        if self._racketPrim == None:
            return

        if abs(moveX) < 1e-5:
            return
        
        # Get translate.
        tV = self._racketPrim.GetAttribute("xformOp:translate")
        if tV.IsValid():
            pos = Gf.Vec3f(tV.Get())
            xPos = pos[0]

            minX = self._stageInfo.racketMinX
            maxX = self._stageInfo.racketMaxX

            xPos += moveX
            if xPos < minX:
                xPos = minX

            if xPos > maxX:
                xPos = maxX
            
            # Update translate.
            pos[0] = xPos
            tV.Set(pos)
        
