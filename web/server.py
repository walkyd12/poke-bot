from flask import Flask, render_template, request
import pandas as pd
import numpy as np
import os

import cv2
from shiny_calc import calculate_chance
from viz import viz

import PokeVision as pv

app = Flask(__name__)

class PokeWeb():
	def is_running():
		stream = os.popen('./is_running.sh')
		out = stream.read()
		print(out)
		if out is not None and out != "":
			return ["Running...", out.split(' ')[3]]
		return ["Not running!", "00:00:00"]

	@app.route('/')
	def index():
		csv_filename = 'dominant_color.csv'
		plot_filename = 'viz.png'
		df = pd.read_csv(f'{app.static_folder}/{csv_filename}')
		num_checks = int(df.count()[0])

		output_obj = calculate_chance(1, 4096, num_checks)
		is_run = is_running()
		output_obj['is_running'] = is_run[0]
		output_obj['cur_runtime'] = is_run[1]
		output_obj['is_running_col'] = "lightgreen" if "Running" in is_run[0] else "crimson"
		viz(app.static_folder, csv_filename, plot_filename)

		return render_template('index.html', value=output_obj)

	@app.route("/upload-complete", methods=["POST"])
	def handle_upload_response():
		"""This will be called after every upload, but we can ignore it"""
		return "Success"

	@app.route("/upload/<path_to_upload>", methods=["POST"])
	def upload(path_to_upload):
		io_file = request.files["media"]
		contents = io_file.read()
		if contents == b'':
			return { 'statusCode': 405 }
		jpg_as_np = np.frombuffer(contents, dtype=np.uint8)
		img = cv2.imdecode(jpg_as_np, flags=1)
		cv2.imwrite(f'{app.static_folder}/{path_to_upload}', img)

		return { 'statusCode': 200 }

	@app.route("/screen-check/<path_to_check>", methods=["GET"])
	def screen_check_w_path(path_to_check):
		cm = pv.PokeVision(base_path='/home/waklky/poke-bot',asset_folder='ultrasun_assets')

		res = cm.is_battle_screen(f'{app.static_folder}/{path_to_check}')

		return { 'statusCode': 200, 'response': res }

	# No caching at all for API endpoints.
	@app.after_request
	def add_header(response):
	    response.cache_control.no_store = True
	    if 'Cache-Control' not in response.headers:
	        response.headers['Cache-Control'] = 'no-store'
	    return response

if __name__ == '__main__':
	app.config.from_object('config')
	
	# config file has STATIC_FOLDER='/core/static'
	app.static_url_path=app.config.get('STATIC_FOLDER')
	print(f"Current static folder: {app.static_url_path}")
	print(f"Current static url path: {app.root_path}/..{app.static_url_path}")
	app.static_folder=app.root_path + "/.." + app.static_url_path

	app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
	app.run(host='0.0.0.0', debug=True)