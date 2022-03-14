import collections
import csv
import json
import time

import requests as requests
from flask import Flask
from flask import send_from_directory

app = Flask(__name__)
leaders = {}
last_updated = 0


def update_leaders():
    ret = collections.defaultdict(lambda: 0)
    with open('repos.csv') as csvfile:
        reader = csv.reader(csvfile)
        reader.__next__()
        for user, repo in reader:
            # resp = requests.get(f"https://api.github.com/repos/{user}/{repo}/pulls?state=all&per_page=100").json()
            resp = []
            page = 1
            t_resp = requests.get(f"https://api.github.com/repos/{user}/{repo}/pulls?state=all&per_page=100&page={page}").json()
            while len(t_resp) > 0:
                resp.extend(t_resp)
                if len(t_resp) < 90:
                    break  # smol optimisation to reduce our number of calls
                page += 1
                t_resp = requests.get(
                    f"https://api.github.com/repos/{user}/{repo}/pulls?state=all&per_page=100&page={page}").json()
            try:
                x = resp
                for pull in resp:
                    if any('accepted-' in label['name'] for label in pull['labels']):
                        valid_pull = next(label['name'] for label in pull['labels'] if 'accepted-' in label['name'])
                        ret[pull['user']['login']] += int(valid_pull.split('-')[-1])
            except Exception:
                print(f"ERROR AT: {user}, {repo}")
                print(resp)
                return 'ded'
    global leaders
    print(ret)
    print('')
    leaders = {k: v for k, v in sorted(ret.items(), key=lambda item: -item[1])}


# @app.route('/')
# def hello_world():  # put application's code here
#     return send_from_directory('public', 'index.html')


@app.route('/leaderboard')
def leaderboard():
    curr_time = time.time()
    global last_updated
    if curr_time - last_updated > 3600:
        last_updated = curr_time
        update_leaders()
    return json.dumps(leaders)


# @app.route('/<path:path>')
# def send_report(path):
#     return send_from_directory('public', path)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)

