import time
import os


max_long = 3600     # seconds

while True:
    files = os.listdir('output')
    for file in files:
        t = int(file.split('.')[0])
        if time.time() - t > max_long:
            os.remove(path=f'output/{file}')
    time.sleep(max_long)
