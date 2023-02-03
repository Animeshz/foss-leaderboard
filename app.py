import collections
import csv
import json
import time
import sys
import os
from threading import Thread

import requests as requests
from flask import Flask
from flask import send_from_directory
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

leaders = {}

remaining_hits = 5000
hits_reset = 0
hits_per_update = 1

headers = {
   "Authorization": "Bearer " + os.environ["GH_TOKEN"]
}

def update_leaders():
    ret = collections.defaultdict(lambda: 0)
    with open('repos.csv') as csvfile:
        reader = csv.reader(csvfile)
        reader.__next__()
        for user, repo in reader:
            resp = []
            page = 1
            f_resp = requests.get(f"https://api.github.com/repos/{user}/{repo}/pulls?state=all&per_page=100&page={page}", headers=headers)
            t_resp = f_resp.json()
            while len(t_resp) > 0:
                resp.extend(t_resp)
                if len(t_resp) < 90:
                    break  # smol optimisation to reduce our number of calls
                page += 1
                f_resp = requests.get(f"https://api.github.com/repos/{user}/{repo}/pulls?state=all&per_page=100&page={page}", headers=headers)
                t_resp = f_resp.json()
            try:
                x = resp
                for pull in resp:
                    if any('accepted-' in label['name'] for label in pull['labels']):
                        valid_pull = next(label['name'] for label in pull['labels'] if 'accepted-' in label['name'])
                        ret[pull['user']['login']] += int(valid_pull.split('-')[-1])
            except Exception:
                print(f"ERROR AT: {user}, {repo}")
                print(resp)
                print(user, repo)
                return 'ded'
    global leaders, remaining_hits, hits_reset, hits_per_update
    leaders = {k: v for k, v in sorted(ret.items(), key=lambda item: -item[1])}

    initial_remaining_hits = remaining_hits
    remaining_hits = int(f_resp.headers['X-RateLimit-Remaining'])
    hits_reset = int(f_resp.headers['X-RateLimit-Reset'])
    hits_per_update = initial_remaining_hits - remaining_hits

class UpdaterThread(Thread):
    def run(self):
        global last_updated, leaders, remaining_hits, hits_reset, hits_per_update

        while True:
            update_leaders()

            number_updates = remaining_hits/hits_per_update
            update_interval = (hits_reset - time.time()) / number_updates

            print(f"remaining_hits: {remaining_hits}")
            print(f"hits_per_update: {hits_per_update}")
            print(f"update_interval: {update_interval}")

            sys.stdout.flush()

            time.sleep(max(update_interval, 30))

@app.route('/leaderboard')
def leaderboard():
    return json.dumps(leaders)

@app.route('/<path:path>')
def send_files(path):
    return send_from_directory('.', path)

@app.route('/')
def root():
    return send_from_directory('.', 'index.html')


if __name__ == '__main__':
    UpdaterThread().start()
    app.run(host='0.0.0.0', port=5000, debug=False)

