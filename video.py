from moviepy.editor import VideoFileClip, ColorClip, CompositeVideoClip, concatenate_videoclips, TextClip
import os
from datetime import date
import json
import subprocess


today = date.today()
today = str(today.strftime("%d_%m_%Y"))
dirname = f'videos_{today}'

with open('data.json') as json_file:
    data = json.load(json_file) 


files = os.listdir(dirname)
clips = []
intro = VideoFileClip("intro.mp4")
d = 0
for file in files:
    clip = VideoFileClip(f'{dirname}/{file}',has_mask=True)
    if clip.duration <35 :
        main = ColorClip(size=(1920,1080),color=[0,0,0], duration=clip.duration)
        
        temp_width = clip.w
        temp_height = clip.h

        if clip.w/16 > clip.h/9:
            clip = clip.resize(width=1920, height=1920/temp_width*temp_height)
        else:
            clip = clip.resize(width=1080/temp_height*temp_width, height=1080)
        
        author, sub= data[file[:-4]][0], data[file[:-4]][1]
        # Generate a text clips 
        author_clip = TextClip(author, fontsize = 25, color = 'white')
        sub_clip = TextClip(sub, fontsize = 25, color = 'white')
    
        # setting position and duration of the text 
        author_clip = author_clip.set_position(('right','bottom')).set_duration(clip.duration)  
        sub_clip = sub_clip.set_position(('left','bottom')).set_duration(clip.duration)  

        add = CompositeVideoClip([main, clip.set_position("center"), author_clip, sub_clip],size=(1920,1080))
        clips.append(add)
        if d/60 > 8: break
        d+= clip.duration
 

video = concatenate_videoclips([intro]+clips,method="compose")


print(f"duration {video.duration/60}min\n", f"size : {video.size}")

video.write_videofile(f"final_{today}.mp4", threads=8, fps=24)


subprocess.call(["python upload_video.py"], shell=True)
