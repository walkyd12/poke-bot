from gamesystem.GameSystem import GameSystem

class ThreeDsComm(GameSystem):
    TDS_COMMANDS = {
        'a':'PRESS_A',
        'b':'PRESS_B',
        'x':'PRESS_X',
        'y':'PRESS_Y',
        'select':'PRESS_SEL',
        'start':'PRESS_STA',
        'r':'PRESS_R',
        'l':'PRESS_L',
        's_up':'STICK_UP',
        's_down':'STICK_DOWN',
        's_left':'STICK_LEFT',
        's_right':'STICK_RIGHT',
        'd_up':'PRESS_D_UP',
        'd_down':'PRESS_D_DOWN',
        'd_left':'PRESS_D_LEFT',
        'd_right':'PRESS_D_RIGHT',
        'sr':'SOFT_RESET',
        'sel':'PRESS_SEL'
    }

    def _send_three_ds_command(self, cmd, resp_timeout=1.0):
        return self._send_game_system_command(cmd, resp_timeout)

    def __enter__(self):
        self.COMMANDS.update(self.TDS_COMMANDS)
        return self