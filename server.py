from flask import Flask
from multiprocessing import Process, Value
import time
import os


class AutoRestart:
    def __init__(self):
        self.saved_time = time.time()
        self.api = None
        self.bot = None
        self.site = None
        self.bot_running = False

    # noinspection PyUnusedLocal
    def check_time(self, loop_on):
        while True:
            if not self.bot_running:
                self.start_bot()
            # time in seconds before restarting Irene
            check_difference = (int(time.time()-self.saved_time)) > 120
            if check_difference:
                self.saved_time = time.time()
                print(f"Bot Found Dead at {time.time()}")
                self.start_bot()

    def start_bot(self):
        os.system("python3 run.py")
        self.bot_running = True

    def start_api(self):
        os.system("node API/index.js")

    def start_site(self):
        os.system("node irenebot-com/index.js")

    def restart_api(self):
        if self.api:
            self.api.terminate()
            os.system("fuser -k 5454/tcp")
        while self.api.is_alive():
            time.sleep(1.5)
        self.api = Process(target=restart.start_api)
        self.api.start()
        self.api.join()


app = Flask(__name__)
restart = AutoRestart()


@app.route('/restartBot', methods=['GET'])
def auto_restart():
    restart.saved_time = time.time()
    print(restart.saved_time)
    return 'Received.'


@app.route('/restartAPI', methods=['GET'])
def restart_api():
    restart.restart_api()
    return 'Received.'


if __name__ == "__main__":
    recording_on = Value('b', True)
    restart.bot = Process(target=restart.check_time, args=(recording_on,))
    restart.api = Process(target=restart.start_api)
    restart.site = Process(target=restart.start_site)
    restart.api.start()
    restart.bot.start()
    restart.site.start()
    app.run(debug=True, use_reloader=False, port=5123)
    restart.api.join()
    restart.bot.join()
    restart.site.join()


