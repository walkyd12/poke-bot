try:
    from gamesystem.GameSystem import GameSystem
except:
    from GameSystem import GameSystem

class ThreeDsComm(GameSystem):
    def __init__(self, logger_name='ThreeDsComm'):
        GameSystem.__init__(self, logger_name=logger_name)
        self.TDS_COMMANDS = {
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
            's_up_s':'STICK_UP_SMALL',
            's_down_s':'STICK_DOWN_SMALL',
            's_left':'STICK_LEFT',
            's_right':'STICK_RIGHT',
            'd_up':'PRESS_D_UP',
            'd_down':'PRESS_D_DOWN',
            'd_left':'PRESS_D_LEFT',
            'd_right':'PRESS_D_RIGHT',
            'sr':'SOFT_RESET',
            'sel':'PRESS_SEL'
        }
        self.COMMANDS.update(self.TDS_COMMANDS)

    def _send_three_ds_command(self, cmd, resp_timeout=1.0):
        return self._send_game_system_command(cmd, resp_timeout)
