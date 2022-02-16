# -----------------------------------------------------.
# Change post processing.
# -----------------------------------------------------.
import omni.kit

class ChangePostProcessing:
    def __init__(self):
        pass

    def Change (self):
        omni.kit.commands.execute("ChangeSetting", path="rtx/post/lensFlares/enabled", value=True)
        omni.kit.commands.execute("ChangeSetting", path="rtx/post/lensFlares/flareScale", value=0.1)
        omni.kit.commands.execute("ChangeSetting", path="rtx/post/tvNoise/enabled", value=True)
        omni.kit.commands.execute("ChangeSetting", path="rtx/post/tvNoise/enableFilmGrain", value=False)
        omni.kit.commands.execute("ChangeSetting", path="rtx/post/tvNoise/enableVignetting", value=True)
        omni.kit.commands.execute("ChangeSetting", path="rtx/post/tvNoise/vignettingSize", value=20.0)
        omni.kit.commands.execute("ChangeSetting", path="rtx/post/tvNoise/vignettingStrength", value=0.1)

