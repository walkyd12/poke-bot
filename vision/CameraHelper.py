from datetime import datetime
import cv2
from picamera import PiCamera

class CameraHelper():
    _backup_check_dir = '/'

    def _take_still_image(self, out_filename):
        camera = PiCamera()     
        camera.capture(out_filename)
        camera.close()

    def _read_pixel_image(self, filename):
        return cv2.imread(filename, 1)

    def _crop_img(self, pixel_array, image_focus):
        return pixel_array[image_focus['y'][0]:image_focus['y'][1], image_focus['x'][0]:image_focus['x'][1]]

    def _flip_img(self, pixel_array):
        return cv2.flip(pixel_array, 0)

    def _clean_image(self, pixel_array, image_focus):
        # 720x1280
        crop = self._crop_img(pixel_array, image_focus)

        crop = self._flip_img(pixel_array)

        return crop

    def _save_bkp_img(self, img, image_focus, w_overlay=False, color_overlay=[0,0,0]):
        now = datetime.now() # current date and time
        date_time = now.strftime("%Y-%m-%dT%H-%M-%S")

        x_end = image_focus['y'][1] - image_focus['y'][0]
        x_middle = int(x_end / 2)

        y_end = image_focus['y'][1] - image_focus['y'][0]
        y_middle = int(x_end / 2)

        if w_overlay == True:
            img[0:y_middle, 0:x_middle] = color_overlay
            img[y_middle:y_end, x_middle:x_end] = color_overlay

        cv2.imwrite(self._backup_check_dir + date_time + '_pixel_check.png', img)
