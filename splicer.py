#!/usr/bin/python

import subprocess
import os
from decimal import *
import csv

# Args
data_csv='data.csv'
segments_dir='segments' + os.path.sep
tmp_dir='tmp' + os.path.sep
ffmpeg = 'ffmpeg'

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

def cut_video (i, o, start, duration):
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
        self.name, self.character, self.comment, self.runner, self.start, self.end, self.duration, self.video = data

data = []
ts_list = []

try: os.stat(tmp_dir)
except: os.mkdir(tmp_dir)

# Parse csv and fill data
with open('data.csv', 'rb') as csvfile:
    for row in csv.reader(csvfile, delimiter=',', quotechar='"'):
        data.append(segment_data(row[:8]))

# Cut videos and convert to ts
for segment in data:
    cut_video(segments_dir + segment.name + '.mp4', tmp_dir + segment.name + '.mp4', segment.start, segment.duration)
    convert_ts(tmp_dir + segment.name + '.mp4', tmp_dir + segment.name + '.ts')
    if os.path.isfile(tmp_dir + segment.name + '.ts'):
        ts_list.append(tmp_dir + segment.name + '.ts')

if len(ts_list):
    concat_videos(ts_list, 'out.mp4')
