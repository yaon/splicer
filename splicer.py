#!/usr/bin/python

import subprocess
import os
from decimal import *

segments=sorted(os.listdir('segments'))
segments_dir='segments'
tmp_dir='tmp'

def call (cmd):
    print(cmd)
    proc = subprocess.Popen(cmd, shell=True)
    proc.wait()
    if (proc.returncode):
        raise "Error " + proc.returncode

def convert_ts (i, o):
    call('ffmpeg -i '+ i +' -c copy -bsf:v h264_mp4toannexb -f mpegts ' + o)

def cut_video (i, o, start, duration):
    i = i.replace(' ', '\\ ');
    call('ffmpeg -i '+i+' -ss '+start+' -t '+duration+' -c:v libx264 -c:a aac -strict experimental -b:a 128k '+o)

def concat_videos (videos, o):
    print(videos)
    cll('ffmpeg -i "concat:'+('|'.join(videos))+'" -c copy -bsf:a aac_adtstoasc '+o)


ts_list = []
try:
    os.stat(tmp_dir)
except:
    os.mkdir(tmp_dir)

for segment in segments:
    number, name, start, stop = os.path.splitext(segment)[0].split()
    duration = Decimal(stop)-Decimal(start)
    cut_video(segments_dir+'/'+segment, tmp_dir+'/'+number+'.mp4', start, str(duration))
    convert_ts(tmp_dir+'/'+number+'.mp4', tmp_dir+'/'+number+'.ts')
    ts_list.append(tmp_dir+'/'+number+'.ts')

concat_videos(ts_list, 'out.mp4')
