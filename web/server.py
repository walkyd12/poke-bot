from flask import Flask, render_template
import pandas as pd
import os

from shiny_calc import calculate_chance
from viz import viz

app = Flask(__name__)

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

@app.route('/my-link/')
def my_link():
	print ('I got clicked!')

	return 'Click.'

# No caching at all for API endpoints.
@app.after_request
def add_header(response):
    # response.cache_control.no_store = True
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