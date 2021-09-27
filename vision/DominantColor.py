import numpy as np
import cv2
import os
import logging
import time
from collections import Counter

from sklearn.cluster import KMeans
from scipy import stats

import pandas as pd

class DominantColor():
    def __init__(self, dominant_color_fullpath, z_threshold, log_name='DominantColor'):
        self._logger = logging.getLogger(log_name)
        self._z_threshold = z_threshold
        self._full_filepath = dominant_color_fullpath

        self._file_headers = ['b','g','r','b_z','g_z','r_z','z_thresh']
        self._file_header_str = self._set_file_header_str()

        if os.path.isfile(self._full_filepath) == False:
            f = open(self._full_filepath, "w")
            f.write(self._file_header_str)

    def _set_file_header_str(self):
        header_str = ''
        for h in self._file_headers:
            header_str += h if header_str == '' else f',{h}'
        header_str += '\n'
        return header_str
    
    def _make_record_str(self, record):
        record_str = ''
        for h in self._file_headers:
            if h in record.keys():
                record_str += record[h] if record_str == '' else f',{record[h]}'
            else:
                return ''
        return(record_str + '\n')

    def write_to_file(self, record):
        try:
            f = open(self._full_filepath, "a")
            f.write(self._make_record_str(record))
            f.close()
            self._logger.info("Wrote record to dominant color file!")
            return True
        except Exception as e:
            self._logger.error(f"Failed to write to dominant color file.\nException-\n{e}")
            return False

    def _get_dominant_color(self, image, k=4, image_processing_size = None):
        """
        takes an image as input
        returns the dominant color of the image as a list

        dominant color is found by running k means on the 
        pixels & returning the centroid of the largest cluster

        processing time is sped up by working with a smaller image; 
        this resizing can be done with the image_processing_size param 
        which takes a tuple of image dims as input

        >>> get_dominant_color(my_image, k=4, image_processing_size = (25, 25))
        [56.2423442, 34.0834233, 70.1234123]
        """
        #resize image if new dims provided
        if image_processing_size is not None:
            image = cv2.resize(image, image_processing_size, 
                                interpolation = cv2.INTER_AREA)

        #reshape the image to be a list of pixels
        image = image.reshape((image.shape[0] * image.shape[1], 3))

        #cluster and assign labels to the pixels 
        clt = KMeans(n_clusters = k)
        labels = clt.fit_predict(image)

        #count labels to find most popular
        label_counts = Counter(labels)

        #subset out most popular centroid
        dominant = list(clt.cluster_centers_[label_counts.most_common(1)[0][0]])

        return dominant

    def _check_results(self, dominant_color):
        z_thresh = self._z_threshold
        
        try:
            df = pd.read_csv(self._full_filepath)
        except pd.errors.EmptyDataError as e:
            df = pd.DataFrame({'b': [float(dominant_color[0])], 'g': [float(dominant_color[1])], 'r':[float(dominant_color[2])]},index=['b', 'g', 'r'])

        try:
            b_z = np.abs(stats.zscore(np.append(df['b'],dominant_color[0])))
            g_z = np.abs(stats.zscore(np.append(df['g'],dominant_color[1])))
            r_z = np.abs(stats.zscore(np.append(df['r'],dominant_color[2])))
        except Exception as e:
            self._logger.error(f'Failed z-score caclulation on dominant color file data.\nException-\n{e}')
            b_z = [100.0]
            g_z = [100.0]
            r_z = [100.0]

        self._logger.warning("Blue z score: " + str(b_z[len(b_z) - 1]) + "; Green z score: " + str(g_z[len(g_z) - 1]) + "; Red z score: " + str(r_z[len(r_z) - 1]))

        record = {
            'b':str(dominant_color[0]),
            'g':str(dominant_color[1]),
            'r':str(dominant_color[2]),
            'b_z':str(b_z[len(b_z) - 1]),
            'g_z':str(g_z[len(g_z) - 1]),
            'r_z':str(r_z[len(r_z) - 1]),
            'z_thresh':str(z_thresh)
        }
        self.write_to_file(record)

        if b_z[len(b_z) - 1] > z_thresh or g_z[len(g_z) - 1] > z_thresh or r_z[len(r_z) - 1] > z_thresh:
            return True
        return False