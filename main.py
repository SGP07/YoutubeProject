import praw
import requests
import subprocess
import os
from datetime import date
import json

today = date.today()
today = str(today.strftime("%d_%m_%Y"))

path = "C:\\Users\\pc\\Documents\\Files\\Dev\\The Ytb Project"
os.chdir(path)

reddit = praw.Reddit(client_id="",client_secret ="",username="",password="", user_agent ="")

def content(sub,t,h):
    subreddit = reddit.subreddit(sub)
    top_posts, hot_posts = [], []
    top = subreddit.top(limit=t)
    hot = subreddit.top("day",limit=h)
    for submission in top:
        if not submission.over_18:
            top_posts.append(submission)
    for submission in hot:
        if not submission.over_18:
            hot_posts.append(submission)
    
    print(f"{sub} DONE ")
    return top_posts, hot_posts

#create day folder 
dirname = f"videos_{today}" 
if not os.path.exists(dirname):
    os.makedirs(dirname)

def save(video_url,audio_url, title):
    with open(f'{title}_video.mp4','wb') as file:
        print('Downloading Video...',end='',flush = True)
        response = requests.get(video_url,headers=headers)
        if(response.status_code == 200):
            file.write(response.content)
            print('\rVideo Downloaded...!')
        else:
            print('\rVideo Download Failed..!')
 
    with open(f'{title}_audio.mp3','wb') as file:
        print('Downloading Audio...',end = '',flush = True)
        response = requests.get(audio_url,headers=headers)
        if(response.status_code == 200):
            file.write(response.content)
            print('\rAudio Downloaded...!')
        else:
            print('\rAudio Download Failed..!')

headers = {'User-Agent':'Mozilla/5.0'}
subs = ["funnyvideos", "Unexpected","WatchPeopleDieInside", "yesyesno", "therewasanattempt", "instant_regret", "instantkarma","maybemaybemaybe","ContagiousLaughter"]

data = {}

for sub in subs:
    top, hot= content(sub,0,3)
    concat = top + hot
    for submission in concat:
        if submission.is_video:
            
            #get submission link
            r = requests.get(submission.url, headers=headers)
            link = r.url
            print(link)

            #get submission title
            title = str(submission.title).replace(" ",'')
            title = title.replace('.','')
            title = title[:15]
            title = ''.join(e for e in title if e.isalnum())

            #get json url
            json_url = link[:len(link)-1]+'.json'
            print(json_url)
            #send request
            response = requests.get(json_url, headers=headers)

            index = 0
            for file in os.listdir(dirname):
                if str(file).lower().startswith(title.lower()):
                    title = f'{title}_{index}'
                    index+=1

            infos = [f"u/{submission.author.name}", f"r/{submission.subreddit.display_name}"]
            data[title]=infos
            if response.ok:
                #get video url  
                video_url = response.json()[0]['data']['children'][0]['data']['secure_media']['reddit_video']['fallback_url']
                #get audio url
                audio_url = video_url.replace(video_url[video_url.find("DASH_")+5:video_url.find(".mp4")], "audio")

                save(video_url, audio_url, f'{dirname}/{title}')                             
                    
                #merge audio and video
                subprocess.call(['ffmpeg','-i',f'{dirname}/{title}_video.mp4','-i',f'{dirname}/{title}_audio.mp3','-map','0:v','-map','1:a','-c:v','copy',f'{dirname}/{title}.mp4'])
                print("merging done")
                    
                #deleting the files
                os.remove(f"{dirname}/{title}_video.mp4")
                os.remove(f'{dirname}/{title}_audio.mp3')
                print('files deleted')
            else :
                print("not a video")
        print("submission done")

with open('data.json','w') as f:
    json.dump(data,f)

subprocess.call(["python video.py"], shell=True)
