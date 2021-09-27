import cv2
import logging
import time
import os
import numpy as np

import threading

import boto3

try:
    from vision.DominantColor import DominantColor
    from vision.CameraHelper import CameraHelper
    from vision.helpers import get_script_directory
except:
    from DominantColor import DominantColor
    from CameraHelper import CameraHelper
    from helpers import get_script_directory


class PokeVision(CameraHelper):
    def __init__(self, poke_to_match=None, base_path='/home/pi/Projects/poke-bot',dom_color_file='dominant_color.csv', z_thresh=2.0, log_name='PokeVision', asset_folder='assets', image_size=[720, 1280]):
        self._base_path = base_path
        self._logger = logging.getLogger(log_name)

        self._script_dir = get_script_directory()
        self._asset_folder = asset_folder
        self._color_file = dom_color_file

        self._tmp_filename = f'{self._base_path}/static/image_to_check.jpg'
        self._backup_check_dir = f'{self._base_path}/static/checks/'
        self._color_file_fullpath = self._get_dom_color_filename(poke_to_match)

        # y, x image height and width
        self._img_size = image_size

        self._dc = DominantColor(self._color_file_fullpath, z_thresh, log_name=log_name)
    
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        return self

    def _get_dom_color_filename(self, poke_to_match=None):
        return f'{self._base_path}/{self._asset_folder}/shiny_hunt/{self._color_file}' if poke_to_match==None else f'{self._script_dir}/{self._asset_folder}/shiny_hunt/{poke_to_match}/{self._color_file}'

    def check_shiny(self, shiny_focus={'x':[583,797], 'y':[240,470]}):
        filename = self._tmp_filename

        time.sleep(6)
        self._take_still_image(filename)
        img = self._read_pixel_image(filename)

        clean_img = self._clean_image(img, shiny_focus)

        dominant_color = self._dc._get_dominant_color(clean_img, k=3)
        self._save_bkp_img(clean_img, shiny_focus, w_overlay=True, color_overlay=dominant_color)

        return self._dc._check_results(dominant_color)

    def _focus(self, img, focus):
        return self._crop_img(img, focus)

    def threaded_template_match(self, img_rgb, template_name_list, template_folder):
        threads = [None] * len(template_name_list)
        results = [None] * len(template_name_list)
        for i in range(len(threads)):
            template_path = f'{self._base_path}/{self._asset_folder}/state_templates/{template_folder}/{template_name_list[i]}.jpg'
            th = threading.Thread(target=self.template_match, args=(img_rgb,template_path,results,i,))
            th.start()
            threads[i] = th

        for i in range(len(threads)):
            threads[i].join()

        return results

    def template_match(self, img_rgb, template_path, results=[], i=0):
        # Convert it to grayscale
        img_gray = cv2.cvtColor(img_rgb, cv2.COLOR_RGB2GRAY)

        # Read the template
        template_rgb = cv2.imread(template_path)
        #template = cv2.cvtColor(template_rgb, cv2.COLOR_RGB2GRAY)
        
        template = cv2.cvtColor(template_rgb, cv2.COLOR_BGR2GRAY)

        # Store width and height of template in w and h
        w, h = template.shape[::-1]

        # Perform match operations.
        res = cv2.matchTemplate(img_gray,template,cv2.TM_CCOEFF_NORMED)

        # Specify a threshold
        threshold = 0.7

        # Store the coordinates of matched area in a numpy array
        loc = np.where( res >= threshold)

        if len(results) > 0:
            results[i] = True if len(list(zip(*loc[::-1]))) > 0 else False

        if True==False:
            pts = list(zip(*loc[::-1]))
            for p in matched_pts:
                img_rgb = self._draw_rec(img_rgb, pts[0][0], pts[0][1], pts[0][0]+w, pts[0][1] + h)
            cv2.imwrite(f'{self._base_path}/test_2.jpg',img_rgb)

        return list(zip(*loc[::-1])), w, h

    def _draw_rec(self, img_rgb, x_1, y_1, x_2, y_2):
        return cv2.rectangle(img_rgb, (x_1,y_1), (x_2,y_2), (0,255,255), 1)

    def detect_text(self):
        """Calls an API on AWS to detect text in an image. $1 per 1,000 requests"""
        ui_words = ['']
        image = cv2.imread('test.jpg')
        is_success, im_buf_arr = cv2.imencode(".jpg", image)
        byte_im = im_buf_arr.tobytes()

        client=boto3.client('rekognition', region_name='us-east-2')

        response=client.detect_text(Image={'Bytes':byte_im})
        textDetections=response['TextDetections']
        text_map = {}
        print ('Detected text\n----------')
        for t in textDetections:
            if float(t['Confidence']) > 85.0:
                pid = t.get('ParentId','')
                if pid != '':
                    id = t['Id']
                    text = t['DetectedText']
                    if text not in ui_words:
                        if text_map.get(pid, '') == '':
                            text_map[pid] = { id: text }
                        else:
                            text_map[pid][id] = text
        
        print(text_map)
        return text_map

    def _test_templates(self, img_path):
        focus_list = []
        #focus_list.append({'name':'fight','x':[2100,2500],'y':[420,800]})
        #focus_list.append({'name':'pokemon','x':[2000,2300],'y':[1600,2000]})
        #focus_list.append({'name':'bag','x':[2400,2700],'y':[1600,2000]})
        #focus_list.append({'name':'run','x':[2700,2870],'y':[1000,1400]})
        #focus_list.append({'name':'drifloon','x':[180,250],'y':[670,900]})
        focus_list.append({'name':'gastly','x':[127,184],'y':[750,928]})
        # Read the main image
        img_rgb = cv2.imread(f'{self._base_path}/{img_path}')
        for focus in focus_list:
            img_rgb = self._draw_rec(img_rgb, focus['x'][0], focus['y'][0], focus['x'][1], focus['y'][1])
        cv2.imwrite(f'{self._base_path}/test_out_temp.jpg',img_rgb)

    def set_templates(self, img_path):
        focus_list = []
        #focus_list.append({'name':'fight','x':[2100,2500],'y':[420,800]})
        #focus_list.append({'name':'pokemon','x':[2000,2300],'y':[1600,2000]})
        #focus_list.append({'name':'bag','x':[2400,2700],'y':[1600,2000]})
        #focus_list.append({'name':'run','x':[2700,2870],'y':[1000,1400]})
        #focus_list.append({'name':'drifloon','x':[180,250],'y':[670,900]})
        focus_list.append({'name':'gastly','x':[127,184],'y':[750,928]})
        # Read the main image
        img_rgb = cv2.imread(f'{self._base_path}/{img_path}')
        for focus in focus_list:
            img_rgb = self._focus(img_rgb, focus)
            cv2.imwrite(f'{self._base_path}/{self._asset_folder}/state_templates/pname/{focus["name"]}.jpg',img_rgb)

    def is_battle_screen(self, img_path):
        temps_to_check = ['fight','bag','run','pokemon']

        img_rgb = cv2.imread(f'{self._base_path}/{img_path}')

        results = self.threaded_template_match(img_rgb, temps_to_check, 'battle')
        
        if False not in results:
            return True
        
        return False

    def check_battle_mon(self, img_path, pname_list):
        img_rgb = cv2.imread(f'{self._base_path}/{img_path}')
        results = self.threaded_template_match(img_rgb, pname_list, 'pname')

        for i in range(len(pname_list)):
            if results[i] == True:
                return pname_list[i]
        return ''

    def get_base_path(self):
        return self._base_path

if __name__=="__main__":
    cm = PokeVision(asset_folder='ultrasun_assets')
    s = time.time()
    #os.popen(f'{cm.get_base_path()}/take_picture.sh test.jpg')
    #print(cm.is_battle_screen('test.jpg'))
    #pname_list = ['drifloon','gastly']
    #print(cm.check_battle_mon('test.jpg', pname_list))
    print(f'time took {time.time() - s}')
    #cm.set_templates('/home/pi/Projects/poke-bot/test.jpg')
    