#!/usr/bin/python

import subprocess
import os
import csv
import urllib
import time
import decimal

# Args
data_csv='data.csv'
segments_dir='segments' + os.path.sep
tmp_dir='tmp' + os.path.sep
ffmpeg = 'ffmpeg'
data_path='https://docs.google.com/spreadsheets/d/1Te4rbNSbv0sW3mmqf735K-ryfsPEfnow00Iuvl7di6c/export?format=csv'

def seconds_to_timestamp(seconds): return time.strftime('%H:%M:%S', time.gmtime(seconds)) + str(seconds%1)[1:]

def call (cmd):
    proc = subprocess.Popen(cmd, shell=True)
    proc.wait()
    if (proc.returncode):
        raise 'Error ' + proc.returncode + ' ' + cmd

def check_io(i, o, debug):
    i_exists = os.path.isfile(i)
    o_exists = os.path.isfile(o)
    if not i_exists: print('No input file, skipping '+debug)
    elif o_exists: print('Output exists, skipping '+debug)
    return i_exists and not o_exists

def get_video(url, o):
    print('get_video '+str(o))
    if os.path.isfile(o) or url == "": return
    urllib.urlretrieve(url, o)

def cut_video (i, o, start, duration):
    duration = seconds_to_timestamp(decimal.Decimal(duration))
    debug = 'cut_video '+str(i)+' '+str(o)+' '+str(start)+' '+str(duration)
    if check_io (i, o, debug):
        call(ffmpeg+' -i '+i+' -ss '+start+' -t '+duration+' -c:v libx264 -c:a aac -strict experimental -b:a 128k '+o)

def convert_ts (i, o):
    debug = 'convert_ts '+str(i)+' '+str(o)
    if check_io (i, o, debug):
        call(ffmpeg + ' -i ' + i + ' -c copy -bsf:v h264_mp4toannexb -f mpegts ' + o)

def concat_videos (videos, o):
    # let ffmpeg ask for replacement in this case
    call(ffmpeg+' -i "concat:'+('|'.join(videos))+'" -c copy -bsf:a aac_adtstoasc '+o)

class segment_data:
    def __init__(self, data):
        self.name, self.character, self.comment, self.runner, self.start, self.end, self.duration, self.drive_id, self.drive_player, self.drive_video = data

data = []
ts_list = []

if __name__ == "__main__":
    try: os.stat(tmp_dir)
    except: os.mkdir(tmp_dir)
    try: os.stat(segments_dir)
    except: os.mkdir(segments_dir)

    # Parse csv and fill data

    urllib.urlretrieve(data_path, data_csv)
    with open('data.csv', 'rb') as csvfile:
        for row in csv.reader(csvfile, delimiter=',', quotechar='"'):
            data.append(segment_data(row[:10]))
    # Remove first info line
    data.pop(0)
    # Remove links line
    data.pop(0)

    # Cut videos and convert to ts
    for segment in data:
        get_video(segment.drive_video, segments_dir + segment.name + '.mp4')
        cut_video(segments_dir + segment.name + '.mp4', tmp_dir + segment.name + '.mp4', segment.start, segment.duration)
        convert_ts(tmp_dir + segment.name + '.mp4', tmp_dir + segment.name + '.ts')
        if os.path.isfile(tmp_dir + segment.name + '.ts'):
            ts_list.append(tmp_dir + segment.name + '.ts')

    if len(ts_list):
        concat_videos(ts_list, 'out.mp4')
