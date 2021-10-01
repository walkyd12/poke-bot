import time
import os

try:
    from gamesystem.ThreeDsComm import ThreeDsComm
except:
    from ThreeDsComm import ThreeDsComm
from PokeVision import PokeVision
from CameraHelper import CameraHelper
from PokeVisionApi import PokeVisionApi

class UiManager():
    def __init__(self):
        self.last_state = 'startup'
        self.last_press = 's_down'
        
    def wild_next_press(self):
        ret = 's_up' if self.last_press == 's_down' else 's_down'
        self.last_press = ret
        return ret

class UltraSunComm(ThreeDsComm):

    def __init__(self):
        ThreeDsComm.__init__(self)
        self._ui = UiManager()
        self.asset_folder = 'ultrasun_assets'
        self._pvision_api = PokeVisionApi(domain='192.168.86.202', port=5000)

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
        mon = ''
        os.popen(f'./take_picture.sh test.jpg')
        time.sleep(1)
        print(f"Upload of test.jpg: {self._pvision_api.upload('test.jpg', out_filename='upload.png')}")
        is_battle = False
        in_wild = True
        while is_battle == False:
            if in_wild:
                print("Walking through the grass...")
                # loop until screen change (?): s_up, s_down, check screen
                next_button = self._ui.wild_next_press()
                self._send_three_ds_command('s_down',5)
                next_button = self._ui.wild_next_press()
                self._send_three_ds_command('s_up',5)
            else:
                print("No longer in the wild, hold on")
                time.sleep(7)

            os.popen(f'./take_picture.sh test.jpg')
            time.sleep(1)
            print(f"Upload of test.jpg: {self._pvision_api.upload('test.jpg', out_filename='upload.png')}")
            batt_ret = self._pvision_api.check_screen(path_to_check='upload.png')

            is_battle = batt_ret['is_battle']
            in_wild = batt_ret['is_wild']
            mon = batt_ret['pname']
        
        last_state = 'battle'
        print(f"Ran into {mon} in the wild!")

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

if __name__=="__main__":
    usc = UltraSunComm()
    usc._wild_shiny_hunt()