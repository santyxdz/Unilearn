import app
from apiclient.discovery import build
from apiclient.errors import HttpError
from oauth2client.tools import argparser

DEVELOPER_KEY = "AIzaSyCoCW1zerva0xAumLCF9jMaRVMB600FKzc"
YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"

def youtube_search(name, limit):
  youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION,
    developerKey=DEVELOPER_KEY)

  search_response = youtube.search().list(
    q=name,
    part="id,snippet",
    maxResults=limit
  ).execute()

  videos = []

  for search_result in search_response.get("items", []):
    if search_result["id"]["kind"] == "youtube#video":
      videos.append("http://youtube.com/embed/%s" % (search_result["id"]["videoId"]))
      
  return videos

# with videos, lets insert the videos on DB using Unilearn API

import requests
import json 
api_url = 'http://localhost:5000/api/video/'


questions = app.models.Question.query.all()
for question in questions:
  try:
    videos = youtube_search(question.statement, 5)
    for video in videos:
        data_json = {"video": video, "question_id": question.id, "action": "insert"}
        print "Sending '%s'" % json.dumps(data_json)
        r = requests.post(api_url, data=data_json)
        if not json.loads(r.text)["status"]:
            print "Aborting, exception generated"
            print json.loads(r.text)["message"]
            exit()
        else:
          print "video inserted"
        
  except HttpError, e:
    print "Un error HTTP %d ocurrio:\n%s" % (e.resp.status, e.content)
