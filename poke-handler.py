#!/usr/bin/env python3
import serial
import time
import argparse
import logging
import os

from gamesystem.ThreeDsComm import ThreeDsComm
from gamesystem.UltraSunComm import UltraSunComm

from vision.PokeVision import PokeVision

if __name__ == '__main__':
    # Initialize parser
    parser = argparse.ArgumentParser()

    # Set cli args
    parser.add_argument('-c', '--mode', choices=['command', 'vision','ultrasun_start','ultrasun_wild'], default='command', help = 'Change mode')
    parser.add_argument('-p', '--pokemon', choices=['rowlet'], default='rowlet', help = 'Change pokemon to hunt')
    parser.add_argument('-f', '--log_file_name', default='poke-handler.log', help = 'File to send log outputs')
    parser.add_argument('-l', '--log_level', choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'], default='INFO', help = 'Log severity level')
    parser.add_argument('-z', '--z_threshold', default=2.0, help = 'Threshold for dominant poke colors to flag for shinies')
    # Read arguments from command line
    args = parser.parse_args()

    logging.basicConfig(filename=f'{os.getcwd()}/{args.log_file_name}', filemode='a', format='%(asctime)s.%(msecs)03d: %(levelname)s - %(message)s',  datefmt='%Y%m%d %H:%M:%S', level=args.log_level)
    
    log_name = 'poke-handler'
    logging.info('Program starting')

    if args.mode=='ultrasun_start':
        logging.info('Running communication with 3DS: Pokémon: Ultra Sun. Mode: Starter Shiny Hunt')
        with UltraSunComm(log_name) as usc:
            usc.game_start(options={'z_thresh':float(args.z_threshold)})
    elif args.mode=='ultrasun_wild':
        logging.info('Running communication with 3DS: Pokémon: Ultra Sun. Mode: Wild Shiny Hunt')
        with UltraSunComm(log_name) as usc:
            usc.wild_shiny_hunt_loop(options={'z_thresh':float(args.z_threshold)})
    elif args.mode == 'vision':
        logging.info('Running vision check...')
        with PokeVision(log_name=log_name, asset_folder='ultrasun_assets') as pv:
            pv.template_match()
    else:
        logging.info('Entering command mode')
        with ThreeDsComm(log_name) as tds:
            tds.command_mode()