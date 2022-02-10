# -----------------------------------------------------.
# Input control.
# -----------------------------------------------------.
from pxr import Usd, UsdGeom, UsdShade, Sdf, Gf, Tf
import omni.ext
import omni.usd
import carb
import carb.input

# ------------------------------------------.
# Gamepad discription.
# ------------------------------------------.
class GamepadDesc:
    def _cleanup(self):
        self.name = None
        self.guid = None
        self.gamepad_device = None
        self.input_device = None
        self.is_connected = False

        self.input_val = {}

    def __init__(self):
        self._cleanup()

    def __del__(self):
        self._cleanup()

# ------------------------------------------.
# InputControl.
# ------------------------------------------.
class InputControl:
    _gamepads = None
    _input = None
    _input_provider = None
    _gamepad_connection_subs = None
    _gamepad_inputs = None

    def __init__(self):
        pass

    def _update_gamepad_connection_state(self, gamepad_device, connection_state):
        for gamepad_desc in self._gamepads:
            if gamepad_desc.gamepad_device == gamepad_device:
                gamepad_desc.is_connected = connection_state

    # gamepad connection event.
    def _gamepad_connection_event(self, event):
        # Gamepad created.
        if event.type == carb.input.GamepadConnectionEventType.CREATED:
            gamepad_desc = GamepadDesc()
            gamepad_desc.name = self._input.get_gamepad_name(event.gamepad)
            gamepad_desc.guid = self._input.get_gamepad_guid(event.gamepad)
            gamepad_desc.gamepad_device = event.gamepad
            gamepad_desc.input_device = event.device
            self._gamepads.append(gamepad_desc)
            print("carb.input.GamepadConnectionEventType.CREATED")
            print("name : " + str(gamepad_desc.name))
            print("guid : " + str(gamepad_desc.guid))

        # Gamepad destroyed.
        elif event.type == carb.input.GamepadConnectionEventType.DESTROYED:
            for gamepad_desc in self._gamepads:
                if gamepad_desc.gamepad_device == event.gamepad:
                    self._gamepads.remove(gamepad_desc)
            print("carb.input.GamepadConnectionEventType.DESTROYED")

        # Gamepad connected.
        elif event.type == carb.input.GamepadConnectionEventType.CONNECTED:
            self._update_gamepad_connection_state(event.gamepad, True)
            print(" carb.input.GamepadConnectionEventType.CONNECTED")

        # Gamepad disconnected.
        elif event.type == carb.input.GamepadConnectionEventType.DISCONNECTED:
            self._update_gamepad_connection_state(event.gamepad, False)
            print(" carb.input.GamepadConnectionEventType.DISCONNECTED")

    # ------------------------------------------------------.
    # gamepad update event.
    # ------------------------------------------------------.
    def GetMoveRacketX (self):
        for gamepad_desc in self._gamepads:
            for gamepad_input in self._gamepad_inputs:
                # Store value.
                val = self._input.get_gamepad_value(gamepad_desc.gamepad_device, gamepad_input)
                gamepad_desc.input_val[gamepad_input] = float(val)

        moveX  = 0.0
        scaleV = 30.0
        minV   = 0.3
        if gamepad_desc.input_val[carb.input.GamepadInput.LEFT_STICK_LEFT] > minV:
            moveX -= scaleV * gamepad_desc.input_val[carb.input.GamepadInput.LEFT_STICK_LEFT]
        if gamepad_desc.input_val[carb.input.GamepadInput.LEFT_STICK_RIGHT] > minV:
            moveX += scaleV * gamepad_desc.input_val[carb.input.GamepadInput.LEFT_STICK_RIGHT]

        return moveX

    # ------------------------------------------------------.
    def startup (self):
        self._gamepads = []
        self._input = carb.input.acquire_input_interface()
        self._input_provider = carb.input.acquire_input_provider()
        self._gamepad_connection_subs = self._input.subscribe_to_gamepad_connection_events(self._gamepad_connection_event)
    
        # Creating a dict of processed GamepadInput enumeration for convenience
        def filter_gamepad_input_attribs(attr):
            return not callable(getattr(carb.input.GamepadInput, attr)) and not attr.startswith("__") and attr != "name" and attr != "COUNT"
        self._gamepad_inputs = dict((getattr(carb.input.GamepadInput, attr), attr) for attr in dir(carb.input.GamepadInput) if filter_gamepad_input_attribs(attr))

    def shutdown (self):
        self._input.unsubscribe_to_gamepad_connection_events(self._gamepad_connection_subs)

        self._gamepad_connection_subs = None
        self._gamepad_inputs = None
        self._gamepads = None

        self._input_provider = None
        self._input = None

