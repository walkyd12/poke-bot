import time

from gamesystem.ThreeDsComm import ThreeDsComm
from vision.PokeVision import PokeVision

class Pokemon():
    def __init__(self, name, level, is_enemy=False, moveset=None):
        self._name = name
        self._level = level
        blank_move = self._init_move()
        self._moveset = {1:blank_move,2:blank_move,3:blank_move,4:blank_move} if moveset==None else moveset

    def _init_move(self):
        return {'name':'','type':'','pp_curr':'','pp_max':''}

class UltraSunComm(ThreeDsComm):
    asset_folder = 'ultrasun_assets'

    def game_start(self, options={}):
        self._opening_sequence_a()
        shiny_found = False
        self._logger.info('Begin starter shiny hunt')
        shiny_found = self._starter_shiny_hunt(options=options)
        if shiny_found == False:
            self._logger.warning('Not a shiny...soft restarting')
            self._send_three_ds_command('sr', resp_timeout=5.0)
            time.sleep(15)
            self._com.flush()
            self._send_three_ds_command('flush')
            self.game_start(options=options)

    def wild_shiny_hunt_loop(self, options={}):
        shiny_found = False
        self._logger.info('Hunting a shiny in the wild')
        shiny_found = self._wild_shiny_hunt(options=options)
        if shiny_found == False:
            self._logger.warning('Not a shiny...trying again')
            self.wild_shiny_hunt_loop(options=options)

    def _opening_sequence_a(self):
        self._logger.info('Skipping intro and selecting save')
        for _ in range(0,6):
            a_succ = self._send_three_ds_command('a')
            time.sleep(1)
        time.sleep(1)

    def _starter_shiny_hunt(self, options={}):
        # Reading macro in early so we can just kick things off
        cmd_list = self._get_macro('opening_sequence_macro')
        self._logger.info('Kicking off cutscene')

        s_up_succ = False
        while(s_up_succ != True):
            s_up_succ = self._send_three_ds_command('s_up', resp_timeout=5.0)
            time.sleep(1)

        if self._execute_macro(cmd_list)==True:
            return self._check_shiny(options.get('z_thresh', 0))
        return False

    def _wild_shiny_hunt(self, options={}):
        # loop until screen change (?): s_up, s_down, check screen
        # assume: battle screen, tap a, read text, check if correct mon to catch
        # if is mon, format Pokemon obj for cur mon using screen text
        # Execute move # (?)
        # wait
        # go to bag and catch
        return True
    
    def _check_shiny(self, z_thresh):
        _shiny_checker = PokeVision(dom_color_file='dominant_color.csv', z_thresh=z_thresh, log_name=self._logger_name)
        is_shiny = _shiny_checker.check_shiny()
        if is_shiny==False:
            self._logger.info("Not shiny...trying again")
            return False
        self._logger.critical("Pokémon flagged as shiny!")
        return True