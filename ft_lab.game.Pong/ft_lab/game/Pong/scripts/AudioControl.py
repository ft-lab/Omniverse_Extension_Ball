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
    _loadSuccess = False
    _loadBusy = False

    _filePathList = []

    def __init__(self):
        pass

    def startup (self):
        self._player = omni.audioplayer.create_audio_player()
        _filePathList = []

    def shutdown (self):
        self.stop()
        self._player = None

    def _file_loaded (self, success : bool):
        self._loadSuccess = success
        self._loadBusy    = False

        if not success:
            index = len(self._filePathList)
            if index >= 1:
                self._filePathList.pop(index - 1)

    # Load sound from file.
    def loadFromFile (self, filePath : str):
        self._loadSuccess = False
        if self._player == None:
            return
        self._loadBusy = True
        self._player.load_sound(filePath, self._file_loaded)
        self._filePathList.append(filePath)

    # Wait for it to finish loading.
    def isLoad (self):
        while self._loadBusy:
            time.sleep(0.1)
        return self._loadSuccess

    # Called when playback is finished.
    def _play_finished (self):
        pass

    # Play sound.
    def play (self, index : int):
        if self._player == None:
            return
        if index < 0 or index >= len(self._filePathList):
            return

        self._player.play_sound(self._filePathList[index], None, self._play_finished, 0.0)

    # Stop sound.
    def stop (self):
        if self._player != None:
            self._player.stop_sound()

# ----------------------------------------------.
class AudioControl:
    _audioPlayer = None
    def __init__(self):
        pass

    def startup (self):
        resourcePath = Path(__file__).parent.parent.joinpath("resources").joinpath("audio")

        self._audioPlayer = AudioPlayer()
        self._audioPlayer.startup()

        # Load sound files.
        fileNameList = ["HitRacket.ogg", "HitWall.ogg"]
        for fileName in fileNameList:
            filePath = f"{resourcePath}/{fileName}"
            self._audioPlayer.loadFromFile(filePath)

    def shutdown (self):
        self._audioPlayer.shutdown()
        self._audioPlayer = None

    def play (self, index : int):
        self._audioPlayer.play(index)

