import logging
import time

import serial

"""A class to connect to Arduino via serial connection. 

The class implements a COMMAND -> RESPONSE pattern and relies on 
the Arduino application code to follow the same pattern.
The class is purposefully single threaded and blocking upon write/read. 
This is to prevent I/O errors caused by simultaneous writes/reads.

Example event timeline:
    SerialArduino sends command 'HI'
    Arduino recieves 'HI'
    Arduino does some process
    Arduino sends command 'HI_SUCC'
    SerialArduino recieves 'HI_SUCC', indicating the Arduino processed the message properly
"""
class SerialManager():
    def __init__(self, logger_name='SerialManager', valid_ports=['/dev/ttyACM0', '/dev/ttyACM1'], baud=31250):
        """
        Params: 
        logger_name - name of logger to write to, 'SerialArduino' if none is passed
        valid_ports - list of ports to attempt to connect to. Used in handling reinit failures
        baud - rate at which bytes are sent on serial line. Must match on the Arduino
        """
        # Attach to a logger
        self._logger_name=logger_name
        self._logger = logging.getLogger(logger_name)

        # Set baud and port list for serial connection
        self.__baud_rate = baud
        self.__valid_ports = valid_ports

        # All SerialArduino objects should have a command to tell Arduino to flush the line
        self.COMMANDS = {'flush':'FLUSH_SER'}

        print("Initializing serial communication...")
        self._com = self.__init_serial_communication()
        time.sleep(2)
        # Tell arduino to flush it's serial line a couple of times. This prevents dropped first messages
        for _ in range(0,2):
            succ = self._send_serial_message(self.COMMANDS['flush'], 1)
            if succ:
                break

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        """Close port on application exit"""
        self.__close_port()

    def __close_port(self):
        """Safely close the serial port"""
        try:
            self._com.close()
        except serial.SerialException  as e:
            self._logger.critical(f"Failed to close serial port.\nException-\n{e}")
        self._logger.info("Serial port closed")

    def __init_serial_communication(self):
        """Connect to serial port using parameters passed at object initialization
        Returns:
            serial_com - successfully connected to serial device
            exit() - abort process and exit application
        """
        for _ in range(0,2):
            exceptions = []
            for port in self.__valid_ports:
                try:
                    # Connect to serial port
                    serial_com = serial.Serial(port, self.__baud_rate, timeout=1, rtscts=1)
                except serial.SerialException  as e:
                    self._logger.error(f'Failed to connect to serial port {port}...')
                    exceptions.append(e)
                    time.sleep(1.5)
                else:
                    self._logger.info(f'Connected to {port} successfully')
                    # Flush line and return serial connection
                    serial_com.flush()
                    return serial_com
            
        self._logger.critical(f'Failed to connect to all ports in {self.__valid_ports}...aborting.\nException(s)-\n{exceptions}')
        exit()

    def _send_serial_message(self, command, resp_timeout):
        """Write serial message and wait for a success response message
        Params:
            command - command to send to Arduino
            resp_timeout - time to wait for response before failing
        Returns:
            True - successfully sent and recieved expected response
            False - serial write failed/serial read failed/invalid response message
        """
        self._logger.info(f'Sending command: {command}')
        # Append newline char to command. Arduino looks for end of message as \n
        full_command = f'{command}\n'
        try:
            # Flush before starting COMMAND -> RESPONSE pattern
            self._com.flush()
            self._com.write(full_command.encode('utf-8'))
        except Exception as e:
            # Failed while trying to write serial message, close port and reinitialize
            self._logger.warning('Failed to write command...reinitializing serial communication.')
            self.__close_port()
            self._com = self.__init_serial_communication()
            self._logger.error(f'Serial write error:\nException-{e}')
            return False

        # Wait for response from Arduino
        resp = self._wait_for_serial_response(resp_timeout)

        # Check if this is our expected message. If no message, return False. If matches, return True
        if resp == f'{command}_SUCC':
            self._logger.info(f'Got success message: {command}_SUCC')
            return True
        elif resp is None:
            return False
        
        # Message didn't match, return True
        self._logger.error(f'Invalid return message! Expecting {command}_SUCC. Got {resp}')
        return False

    def _wait_for_serial_response(self, resp_timeout):
        """Wait for a message on the serial line, or time out
        Params:
            resp_timeout - time to wait before exiting function
        Returns:
            line - return message recieved via serial line
            None - nothing received/timeout/failed to read from serial line
        """
        try:
            # Only wait for 5 seconds to recieve a response
            start_time = time.time()
            while (time.time() - start_time) < resp_timeout:
                # Check if there is a waiting serial message
                if self._com.in_waiting > 0:
                    # Read message in waiting
                    line = self._com.readline().decode('utf-8').rstrip()
                    # Flush line after we recieve a message
                    self._com.flush()
                    self._logger.debug(f'Recieved message: {line}')
                    return line
            # Timed out
            self._logger.warning(f'Response timeout. Waited {str(resp_timeout)} seconds.')
            return None
        except Exception as e:
            # Failed read, close port and reinit
            self._logger.error(f'Failed to read serial response...\nException-\n{e}')
            self.__close_port()
            time.sleep(2)
            self._com = self.__init_serial_communication()
            return None