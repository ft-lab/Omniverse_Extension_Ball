# -----------------------------------------------------.
# Move Racket.
# -----------------------------------------------------.
from pxr import Usd, UsdGeom, UsdShade, Sdf, Gf, Tf
import omni.ext
import omni.usd

class MoveRacket:
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

    def __init__(self):
        pass

    def startup (self):
        self._racketPrim = self._getRacketPrim()

    def shutdown (self):
        pass

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

            minX = -5.0 * 200.0
            maxX = minX + 9.0 * 200.0

            minX += 100.0 + 10.0
            maxX -= 100.0 + 10.0

            xPos += moveX
            if xPos < minX:
                xPos = minX

            if xPos > maxX:
                xPos = maxX
            
            # Update translate.
            pos[0] = xPos
            tV.Set(pos)
        
