import requests
import time

class PokeVisionApi():
    def __init__(self, domain='192.168.86.202', port=5000):
        self._base_url = f"http://{domain}:{str(port)}"

    def upload(self, in_filename, out_filename='upload.png'):
        files = { 'media': open(in_filename, 'rb') }
        return requests.post(f'{self._base_url}/upload/{out_filename}', files=files )

    def check_screen(self, path_to_check='upload.png'):
        r = requests.get(f'{self._base_url}/screen-check/{path_to_check}')
        return r.json()['response'].get('battle_screen', {})

if __name__=="__main__":
    s = time.time()
    api = PokeVisionApi()
    api.upload("/home/pi/Projects/poke-bot/test.jpg")
    print(api.check_screen())
    print(time.time() - s)