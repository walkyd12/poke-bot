import os
import csv
import time

from gamesystem.SerialManager import SerialManager

class GameSystem(SerialManager):
    asset_folder = 'assets'

    def __command_lookup(self, short_cmd):
        return self.COMMANDS.get(short_cmd, '')
    
    def __get_all_commands(self):
        return self.COMMANDS

    def _send_game_system_command(self, cmd, resp_timeout=1.0):
        msg = ''
        if cmd in self.__get_all_commands():
            msg = self.__command_lookup(cmd)
        if msg != '':
            return self._send_serial_message(msg, resp_timeout)
        else:
            self._logger.warning('Invalid 3DS Command!')
        return False

    def _get_macro(self, macro_name):
        lines = []
        col_names = []
        fname = f"{os.getcwd()}/{self.asset_folder}/macros/{macro_name}.csv"
        with open(fname) as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=',')
            line_count = 0
            for row in csv_reader:
                if line_count == 0:
                    col_names = row
                    if set(col_names) != set(['press_num','cmd','sec_from_last_press','desc']):
                        self._logger.info('Macro CSV file has invalid header...')
                        return None
                    line_count += 1
                else:
                    lines.append({col_names[1]:row[1],col_names[2]:row[2],col_names[3]:row[3]})
                    line_count += 1
            csv_file.close()
            self._logger.info(f'Read in {fname}')
            return lines
        return None

    def _execute_macro(self, cmd_list):
        if cmd_list == None:
            return False

        for cmd_set in cmd_list:
            start_time = time.time()
            time_to_elapse = cmd_set['sec_from_last_press']

            if cmd_set['desc'] != "":
                self._logger.info(f'Macro info: {cmd_set["desc"]}')

            time.sleep(float(time_to_elapse))
            a_succ = False
            while a_succ == False:
                a_succ = self._send_game_system_command(cmd_set['cmd'])

        return True

    def _run_macro(self, macro_name):
        return self._execute_macro(self._get_macro(macro_name))

    def command_mode(self):
        inp = ''
        while inp!='q' or inp!='quit':
            cmd = input('Button to Press:\n')
            to = 1.0

            if cmd in ['q','quit']:
                self._logger.info('Exiting...')
                break    
            elif cmd == 'flush':
                self._com.flush()
            elif cmd == 'sr':
                to = 5.0
            elif cmd=='':
                cmd = 'a'
            time.sleep(2)
            msg_succ = self._send_game_system_command(cmd, to)