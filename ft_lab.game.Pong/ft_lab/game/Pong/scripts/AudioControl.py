# -----------------------------------------------------.
# Play audio.
# -----------------------------------------------------.
from pxr import Usd, UsdGeom, UsdShade, Sdf, Gf, Tf
import omni.audioplayer   # need "omni.audioplayer" extension.
import time
import asyncio
from pathlib import Path

# ----------------------------------------------.
# AudioPlayer.
# ----------------------------------------------.
class AudioPlayer:
    _player = None
    _filePath = None
    _loadSuccess = False
    _loadBusy = False

    def __init__(self):
        pass

    def startup (self):
        self._player = omni.audioplayer.create_audio_player()

    def shutdown (self):
        self.stop()
        self._player = None

    def _file_loaded (self, success : bool):
        self._loadSuccess = success
        self._loadBusy    = False

    # Load sound from file.
    def loadFromFile (self, filePath : str):
        self._loadSuccess = False
        if self._player == None:
            return
        self._filePath = filePath
        self._loadBusy = True
        self._player.load_sound(filePath, self._file_loaded)

    # Wait for it to finish loading.
    def isLoad (self):
        while self._loadBusy:
            time.sleep(0.1)
        return self._loadSuccess

    # Called when playback is finished.
    def _play_finished (self):
        pass

    # Play sound.
    def play (self):
        if self._player == None:
            return False

        self._player.play_sound(self._filePath, None, self._play_finished, 0.0)

    # Stop sound.
    def stop (self):
        if self._player != None:
            self._player.stop_sound()

# ----------------------------------------------.
class AudioControl:
    _audioList = []
    def __init__(self):
        pass

    def startup (self):
        resourcePath = Path(__file__).parent.parent.joinpath("resources").joinpath("audio")

        # Load sound files.
        fileNameList = ["HitRacket.ogg", "HitWall.ogg"]
        for fileName in fileNameList:
            filePath = f"{resourcePath}/{fileName}"

            audioD = AudioPlayer()
            audioD.startup()
            audioD.loadFromFile(filePath)
            self._audioList.append(audioD)

    def shutdown (self):
        for audioD in self._audioList:
            audioD.shutdown()
        self._audioList = None

    def play (self, index : int):
        if index < 0 or index >= len(self._audioList):
            return
        audioD = self._audioList[index]
        audioD.play()

