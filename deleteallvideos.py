from app import models, db
import requests

videos = models.HelpVideos.query.all()
for video in videos:
    print "deleting video...%s in question %s" % (video.video_url,video.question_id)
    db.session.delete(video)

db.session.commit()
