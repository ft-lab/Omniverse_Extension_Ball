
# -----------------------------------------------------------.
# Create stage.
# -----------------------------------------------------------.
from pxr import Usd, UsdGeom, UsdShade, Sdf, Gf, Tf
import omni.ext
import omni.usd
import omni.kit
import carb.settings
from pathlib import Path
import asyncio

from .StageInfo import StageInfo

class CreateStage:
    _stageInfo  = None

    def __init__(self, stageInfo : StageInfo):
        self._stageInfo = stageInfo

    # -----------------------------------------------.
    # Change Path-Traced.
    # -----------------------------------------------.
    async def _setPathTraced (self):
        await omni.kit.app.get_app().next_update_async()
        settings = carb.settings.get_settings()
        settings.set('/rtx/rendermode', 'PathTracing')

    # -----------------------------------------------.
    # Set block.
    # -----------------------------------------------.
    def _setBlock (self, stage, orgPrimPath, path, pos, rot90):
        UsdGeom.Xform.Define(stage, path)
        prim = stage.GetPrimAtPath(path)

        prim.CreateAttribute("xformOp:translate", Sdf.ValueTypeNames.Float3, False).Set(Gf.Vec3f(pos[0], pos[1], pos[2]))
        prim.CreateAttribute("xformOp:scale", Sdf.ValueTypeNames.Float3, False).Set(Gf.Vec3f(100, 100, 100))

        if rot90 == True:
            prim.CreateAttribute("xformOp:rotateXYZ", Sdf.ValueTypeNames.Float3, False).Set(Gf.Vec3f(90, 0, -180))
        else:
            prim.CreateAttribute("xformOp:rotateXYZ", Sdf.ValueTypeNames.Float3, False).Set(Gf.Vec3f(0, -90, -90))
        transformOrder = prim.CreateAttribute("xformOpOrder", Sdf.ValueTypeNames.String, False)
        transformOrder.Set(["xformOp:translate", "xformOp:rotateXYZ", "xformOp:scale"])

        prim.GetReferences().ClearReferences()
        prim.GetReferences().AddInternalReference(orgPrimPath)

    # -----------------------------------------------.
    # Set camera.
    # -----------------------------------------------.
    def _setCamera (self, stage):
        # Create camera.
        pathName = self._stageInfo.workPath + '/camera'
        cameraGeom = UsdGeom.Camera.Define(stage, pathName)

        cameraGeom.CreateFocalLengthAttr(19.0)
        cameraGeom.CreateFocusDistanceAttr(400.0)
        cameraGeom.CreateFStopAttr(0.0)
        cameraGeom.CreateProjectionAttr('perspective')

        # Set position.
        UsdGeom.XformCommonAPI(cameraGeom).SetTranslate((-150.0, 3178.0, 2281.0))

        # Set rotation.
        UsdGeom.XformCommonAPI(cameraGeom).SetRotate((-55.62, 0.0, 0.0), UsdGeom.XformCommonAPI.RotationOrderXYZ)

        # Set scale.
        UsdGeom.XformCommonAPI(cameraGeom).SetScale((1, 1, 1))

        # Change active camera.
        viewport = omni.kit.viewport.get_viewport_interface()
        viewport.get_viewport_window().set_active_camera(pathName)

    # -----------------------------------------------.
    # Initialize the stage.
    # -----------------------------------------------.
    def _initStage (self):
        # New stage.
        omni.usd.get_context().new_stage()
        stage = omni.usd.get_context().get_stage()

        # Set "RTX Path-traced"
        asyncio.ensure_future(self._setPathTraced())

        # Create root(DefaultPrim).
        UsdGeom.Xform.Define(stage, self._stageInfo.rootPath)
        prim = stage.GetPrimAtPath(self._stageInfo.rootPath)
        stage.SetDefaultPrim(prim)

        # Set Camera.
        self._setCamera(stage)

        # Get USD file.
        pathUSD = Path(__file__).parent.parent.joinpath("resources").joinpath("usd")
        usdStageTemplatePath = f"{pathUSD}/stageTemplate.usd"

        # Reference.
        try:
            path = self._stageInfo.stageTemplatePath
            UsdGeom.Xform.Define(stage, path)
            prim = stage.GetPrimAtPath(path)
            prim.GetReferences().AddReference(usdStageTemplatePath)
        except Exception as e:
            print("error : " + str(e))

        # asset path.
        orgAssetsPath     = self._stageInfo.stageAssetsPath
        orgFloorBlockPath = orgAssetsPath + "/floorBlock_2x2"
        orgBlockPath      = orgAssetsPath + "/block_2x1"

        # Hide Assets.
        prim = stage.GetPrimAtPath(orgAssetsPath)
        primImageable = UsdGeom.Imageable(prim)
        primImageable.GetVisibilityAttr().Set('invisible')

        UsdGeom.Xform.Define(stage, self._stageInfo.workPath)
        floorBlocksPath = self._stageInfo.workPath + '/floorBlocks'
        UsdGeom.Xform.Define(stage, floorBlocksPath)
        blocksPath = self._stageInfo.workPath + '/blocks'
        UsdGeom.Xform.Define(stage, blocksPath)
        
        # ----------------------------------------------------.
        # Set floor blocks.
        index = 0
        zV = -7.0 * 200.0
        for z in range(14):
            xV = -5.0 * 200.0
            for x in range(10):
                path = floorBlocksPath + '/block_' + str(index)
                self._setBlock(stage, orgFloorBlockPath, path, [xV, 0.0, zV], False)
                index += 1
                xV += 200.0
            zV += 200.0

        # Set wall blocks.
        index = 0
        zV = 6.0 * 200.0
        for x in range(14):
            path = blocksPath + '/block_' + str(index)
            self._setBlock(stage, orgBlockPath, path, [-5.0 * 200.0 - 50.0, 5.0, zV], True)
            index += 1
            zV -= 200.0

        zV = 6.0 * 200.0
        for x in range(14):
            path = blocksPath + '/block_' + str(index)
            self._setBlock(stage, orgBlockPath, path, [4.0 * 200.0 + 50.0, 5.0, zV], True)
            index += 1
            zV -= 200.0

        xV = -5.0 * 200.0
        for x in range(10):
            path = blocksPath + '/block_' + str(index)
            self._setBlock(stage, orgBlockPath, path, [xV, 5.0, -7.0 * 200.0 - 50.0], False)
            index += 1
            xV += 200.0

    # -----------------------------------------------.
    # Startup.
    # -----------------------------------------------.
    def startup (self):
        self._initStage()

    def shutdown (self):
        pass
    

