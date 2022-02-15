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

        workPath = rootPath + '/work'
        racketPath = workPath + '/racket'

        # Duplicate Prim from specified path.
        omni.kit.commands.execute("CopyPrim", path_from=racketOrgPath)

        # Stores the path of the newly duplicated Prim.
        copyPrimPath = ""
        selection = omni.usd.get_context().get_selection()
        paths = selection.get_selected_prim_paths()
        if len(paths) >= 1:
            copyPrimPath = paths[0]

        prim = None
        if copyPrimPath != "":
            # Change Prim's path.
            # path_from : Path of the original Prim.
            # path_to   : Path to move to.
            omni.kit.commands.execute("MovePrim", path_from=copyPrimPath, path_to=racketPath)

            # Change position.
            prim = stage.GetPrimAtPath(racketPath)
            tV = prim.GetAttribute("xformOp:translate")
            if tV.IsValid():
                tV.Set(Gf.Vec3f(0, 10, 1140))

            # Change rotation.
            tV = prim.GetAttribute("xformOp:rotateXYZ")
            if tV.IsValid():
                tV.Set(Gf.Vec3f(-90, 0, 0))

        # Deselect all.
        omni.kit.commands.execute("SelectNone")

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
        
