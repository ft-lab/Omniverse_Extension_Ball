# -----------------------------------------------------.
# Input control (Gamepad / Keyboard).
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
    _keyboard = None
    _keyboard_subs = None

    _push_key_left  = False
    _push_key_right = False
    _push_key_up    = False
    _push_key_down  = False
    _push_key_enter = False

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
    # Racket movement event.
    # ------------------------------------------------------.
    def GetMoveRacketX (self):
        moveX  = 0.0
        scaleV = 30.0
        minV   = 0.3

        if self._gamepads != None:
            gamepad_descD = None
            for gamepad_desc in self._gamepads:
                gamepad_descD = gamepad_desc
                for gamepad_input in self._gamepad_inputs:
                    # Store value.
                    val = self._input.get_gamepad_value(gamepad_desc.gamepad_device, gamepad_input)
                    gamepad_descD.input_val[gamepad_input] = float(val)

            if gamepad_descD != None:
                if gamepad_descD.input_val[carb.input.GamepadInput.LEFT_STICK_LEFT] > minV:
                    moveX -= scaleV * gamepad_descD.input_val[carb.input.GamepadInput.LEFT_STICK_LEFT]
                if gamepad_descD.input_val[carb.input.GamepadInput.LEFT_STICK_RIGHT] > minV:
                    moveX += scaleV * gamepad_descD.input_val[carb.input.GamepadInput.LEFT_STICK_RIGHT]

        if self._push_key_left:
            moveX -= scaleV
        if self._push_key_right:
            moveX += scaleV

        return moveX

    # ------------------------------------------------------.
    # Selecting(UP/DOWN/Enter) the title menu.
    # ------------------------------------------------------.
    def GetUpDown_TitleMenu (self):
        buttonV = [False, False, False]     # Up/Down/Enter

        if self._gamepads != None:
            gamepad_descD = None
            for gamepad_desc in self._gamepads:
                gamepad_descD = gamepad_desc
                for gamepad_input in self._gamepad_inputs:
                    # Store value.
                    val = self._input.get_gamepad_value(gamepad_desc.gamepad_device, gamepad_input)
                    gamepad_descD.input_val[gamepad_input] = float(val)

            if gamepad_descD != None:
                minV = 0.3
                if gamepad_descD.input_val[carb.input.GamepadInput.LEFT_STICK_UP] > minV:
                    buttonV[0] = True
                if gamepad_descD.input_val[carb.input.GamepadInput.LEFT_STICK_DOWN] > minV:
                    buttonV[1] = True
                if gamepad_descD.input_val[carb.input.GamepadInput.DPAD_UP] > minV:
                    buttonV[0] = True
                if gamepad_descD.input_val[carb.input.GamepadInput.DPAD_DOWN] > minV:
                    buttonV[1] = True
                if gamepad_descD.input_val[carb.input.GamepadInput.A] > minV:
                    buttonV[2] = True

        if self._push_key_up:
            buttonV[0] = True
        if self._push_key_down:
            buttonV[1] = True
        if self._push_key_enter:
            buttonV[2] = True

        return buttonV

    # ------------------------------------------------------.
    # Keyboard event.
    # ------------------------------------------------------.
    def _keyboard_event (self, event : carb.input.KeyboardEvent):
        if event.type == carb.input.KeyboardEventType.KEY_PRESS:
            if event.input == carb.input.KeyboardInput.LEFT:
                self._push_key_left  = True
            if event.input == carb.input.KeyboardInput.RIGHT:
                self._push_key_right = True
            if event.input == carb.input.KeyboardInput.UP:
                self._push_key_up  = True
            if event.input == carb.input.KeyboardInput.DOWN:
                self._push_key_down  = True
            if event.input == carb.input.KeyboardInput.ENTER:
                self._push_key_enter  = True

        elif event.type == carb.input.KeyboardEventType.KEY_RELEASE:
            if event.input == carb.input.KeyboardInput.LEFT:
                self._push_key_left  = False
            if event.input == carb.input.KeyboardInput.RIGHT:
                self._push_key_right = False
            if event.input == carb.input.KeyboardInput.UP:
                self._push_key_up  = False
            if event.input == carb.input.KeyboardInput.DOWN:
                self._push_key_down  = False
            if event.input == carb.input.KeyboardInput.ENTER:
                self._push_key_enter  = False

        return True

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

        # Assign keyboard event.
        appwindow = omni.appwindow.get_default_app_window()
        self._keyboard = appwindow.get_keyboard()
        self._keyboard_subs = self._input.subscribe_to_keyboard_events(self._keyboard, self._keyboard_event)

    def shutdown (self):
        if self._input != None:
            self._input.unsubscribe_to_gamepad_connection_events(self._gamepad_connection_subs)

        # Release keyboard event.
        if self._input != None:
            self._input.unsubscribe_to_keyboard_events(self._keyboard, self._keyboard_subs)

        self._gamepad_connection_subs = None
        self._gamepad_inputs = None
        self._gamepads = None

        self._keyboard_subs = None
        self._keyboard      = None

        self._input_provider = None
        self._input = None

