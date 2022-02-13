# -----------------------------------------------------.
# Ball control.
# -----------------------------------------------------.
from pxr import Usd, UsdGeom, UsdShade, Sdf, Gf, Tf
import omni.ext
import omni.usd
import asyncio
import random
import math

from .StageInfo import StageInfo
from .MoveRacket import MoveRacket
from .AudioControl import AudioControl

class BallControl:
    _index = 0     # index.
    _stageInfo  = None
    _moveRacket = None
    _audioControl = None

    _ballPrim = None

    _speed       = 1.0    # Moving Speed.
    _movingScale = 40.0  # Moving scale.
    _dirAngle    = -90.0  # Direction angle (0.0 ==> Gf.Vec3f(1, 0, 0)).

    def __init__(self, stageInfo : StageInfo, moveRacket : MoveRacket, audioControl : AudioControl, index : int):
        self._stageInfo    = stageInfo
        self._moveRacket   = moveRacket
        self._audioControl = audioControl
        self._index     = index
        self._initFirstDirection()

    def _initFirstDirection (self):
        # (-50.0 - +50.0) + 270.0
        self._dirAngle = ((random.random() - 0.5) * 2.0) * 50.0 + 270.0

    def _angleToDirection (self, angle : float):
        v = angle * math.pi / 180.0
        dx =  math.cos(v)
        dz = -math.sin(v)
        return Gf.Vec3f(dx, 0.0, dz)

    def _directionToAngle (self, dirV : Gf.Vec3f):
        v = 0.0
        if dirV[0] >= 0.0:
            rot = Gf.Rotation().SetRotateInto(Gf.Vec3d(1, 0, 0), Gf.Vec3d(dirV))
            rV = rot.Decompose(Gf.Vec3d(1, 0, 0), Gf.Vec3d(0, 1, 0), Gf.Vec3d(0, 0, 1))
            v = rV[1]
        else:
            rot = Gf.Rotation().SetRotateInto(Gf.Vec3d(-1, 0, 0), Gf.Vec3d(dirV))
            rV = rot.Decompose(Gf.Vec3d(1, 0, 0), Gf.Vec3d(0, 1, 0), Gf.Vec3d(0, 0, 1))
            v = rV[1] + 180.0

        if v < 0.0:
            v += 360.0
        return v

    # -----------------------------------------------------.
    # Create ball.
    # -----------------------------------------------------.
    def _createBall (self):
        stage = omni.usd.get_context().get_stage()

        path = self._stageInfo.workPath + '/balls'
        UsdGeom.Xform.Define(stage, path)

        ballPath = path + '/sphere_' + str(self._index)
        sphereGeom = UsdGeom.Sphere.Define(stage, ballPath)
        self._ballPrim = stage.GetPrimAtPath(ballPath)

        # Set radius.
        sphereGeom.CreateRadiusAttr(self._stageInfo.ballRadius)

        # Get Material (OmniPBR).
        material = UsdShade.Material(stage.GetPrimAtPath(self._stageInfo.ballMaterialPath))

        # Bind material.
        UsdShade.MaterialBindingAPI(self._ballPrim).Bind(material)

        # Set position.
        px = ((random.random() - 0.5) * 2.0) * 500.0
        pz = ((random.random() - 0.5) * 2.0) * 300.0
        UsdGeom.XformCommonAPI(sphereGeom).SetTranslate((px, self._stageInfo.ballYPos, pz))

    # -----------------------------------------------------.
    # Clip in moving range.
    # -----------------------------------------------------.
    def _clipPos (self, pos1 : Gf.Vec3f, pos2 : Gf.Vec3f):
        minX = self._stageInfo.rangeMinX + 100.0 + 50.0
        maxX = self._stageInfo.rangeMaxX - 100.0 - 50.0
        minY = self._stageInfo.rangeMinY + 100.0 + 50.0
        maxY = self._stageInfo.rangeMaxY

        dirV = (pos2 - pos1).GetNormalized()
        newP = pos2

        if pos2[0] < minX:
            t = (minX - pos1[0]) / dirV[0]
            newP = dirV * t + pos1
        if pos2[0] > maxX:
            t = (maxX - pos1[0]) / dirV[0]
            newP = dirV * t + pos1
        if pos2[2] < minY:
            t = (minY - pos1[2]) / dirV[2]
            newP = dirV * t + pos1
        if pos2[2] > maxY:
            t = (maxY - pos1[2]) / dirV[2]
            newP = dirV * t + pos1

        racketPos  = self._moveRacket.GetRacketPosition()
        racketSize = self._moveRacket.GetRacketSize()
        rMinX = racketPos[0] - racketSize[0] * 0.5 - 25.0
        rMaxX = racketPos[0] + racketSize[0] * 0.5 + 25.0
        rMinY = racketPos[2] - racketSize[2] * 0.5 - 25.0
        rMaxY = racketPos[2] + racketSize[2] * 0.5 + 25.0
        if pos2[0] >= rMinX and pos2[0] <= rMaxX and pos2[2] >= rMinY and pos2[2] <= rMaxY:
            if pos2[2] > rMinY:
                t = (rMinY - pos1[2]) / dirV[2]
                newP = dirV * t + pos1
            elif pos2[2] < rMaxY:
                t = (rMaxY - pos1[2]) / dirV[2]
                newP = dirV * t + pos1
            elif pos2[0] > rMinX:
                t = (rMinX - pos1[0]) / dirV[0]
                newP = dirV * t + pos1
            elif pos2[0] < rMaxX:
                t = (rMaxX - pos1[0]) / dirV[0]
                newP = dirV * t + pos1
        return newP

    # -----------------------------------------------------.
    # Update ball.
    # -----------------------------------------------------.
    def updateBall (self):
        dirV = self._angleToDirection(self._dirAngle)

        # Amount of movement.
        dV = dirV * self._speed * self._movingScale

        tV = self._ballPrim.GetAttribute("xformOp:translate")
        if tV.IsValid():
            pos = Gf.Vec3f(tV.Get())
            pos2 = pos + dV

            # Collision with blocks.
            minX = self._stageInfo.rangeMinX + 100.0 + 50.0
            maxX = self._stageInfo.rangeMaxX - 100.0 - 50.0
            minY = self._stageInfo.rangeMinY + 100.0 + 50.0
            maxY = self._stageInfo.rangeMaxY

            dirV2 = dirV
            chkF = False
            if pos2[0] < minX:
                chkF = True
                dirV2 = Gf.Vec3f(-dirV[0], 0.0, dirV[2])

            if pos2[0] > maxX:
                chkF = True
                dirV2 = Gf.Vec3f(-dirV[0], 0.0, dirV[2])

            if pos2[2] < minY:
                chkF = True
                dirV2 = Gf.Vec3f(dirV[0], 0.0, -dirV[2])

            if pos2[2] > maxY:
                chkF = True
                dirV2 = Gf.Vec3f(dirV[0], 0.0, -dirV[2])

            # Play sound (Hit wall).
            if chkF:
                self._audioControl.play(1)

            # Collision with racket.
            if chkF == False and self._moveRacket != None:
                racketPos  = self._moveRacket.GetRacketPosition()
                racketSize = self._moveRacket.GetRacketSize()
                rMinX = racketPos[0] - racketSize[0] * 0.5 - 25.0
                rMaxX = racketPos[0] + racketSize[0] * 0.5 + 25.0
                rMinY = racketPos[2] - racketSize[2] * 0.5 - 25.0
                rMaxY = racketPos[2] + racketSize[2] * 0.5 + 25.0
                if pos2[0] >= rMinX and pos2[0] <= rMaxX and pos2[2] >= rMinY and pos2[2] <= rMaxY:
                    if pos2[2] > rMinY:
                        chkF = True
                        dirV2 = Gf.Vec3f(dirV[0], 0.0, -dirV[2])
                    elif pos2[0] > rMinX:
                        chkF = True
                        dirV2 = Gf.Vec3f(-dirV[0], 0.0, dirV[2])
                    elif pos2[0] < rMaxX:
                        chkF = True
                        dirV2 = Gf.Vec3f(-dirV[0], 0.0, dirV[2])

                if chkF:
                    # Play sound (Hit racket).
                    if chkF:
                        self._audioControl.play(0)

            # Clip in moving range.
            newPos = self._clipPos(pos, pos2)

            tV.Set(newPos)

            # Change direction.
            if chkF:
                self._dirAngle = self._directionToAngle(dirV2)

                self._dirAngle += ((random.random() - 0.5) * 2.0) * 5.0

                for i in range(5):
                    if abs(self._dirAngle - 0.0) < 10.0:
                        self._dirAngle += ((random.random() - 0.5) * 2.0) * 5.0
                    elif abs(self._dirAngle - 90.0) < 10.0:
                        self._dirAngle += ((random.random() - 0.5) * 2.0) * 5.0
                    elif abs(self._dirAngle - 180.0) < 10.0:
                        self._dirAngle += ((random.random() - 0.5) * 2.0) * 5.0
                    elif abs(self._dirAngle - 270.0) < 10.0:
                        self._dirAngle += ((random.random() - 0.5) * 2.0) * 5.0
                    else:
                        break

    # -----------------------------------------------------.
    def startup (self):
        self._createBall()
        self._speed = 0.8 + random.random() * 0.5

    def shutdown (self):
        pass

