from flask_restful import Resource, Api
from flask import request
from app import api
from app import db
from app import views
from app import models
from flask_login import login_user, logout_user, current_user, login_required
import json

def new_score(username, question, score):
        user = models.User.query.filter_by(username=username).first()
        previousScore = models.UserScore.query.filter_by(user_username=username, question_id=question.id).first()
        if isinstance(previousScore, type(None)):
                    userscore = models.UserScore(user, question, score)
                    db.session.add(userscore)
                    db.session.commit()
        else:
            if score > previousScore.score:
                previousScore.score = score
                db.session.commit()


class RError(Resource):
    def get(self):
        return {"error": "Not Accesible"}

    def put(self):
        return {"error": "Not Accesible"}


class RUser(Resource):
    def get(self, username):
        user = models.User.query.filter_by(username=username).first()
        if views.is_empty(user):
            return {
                "result": False,
                "status": "error",
                "error": "Username doesn't exit"
            }
        else:
            return {
                "result": True,
                "user": user.username,
                "status": "Successful, User is on DB"
            }

    def post(self, username):
        if "update" == request.form["method"]:
            return {"result": True}
        elif "create" == request.form["method"]:
            if self.get(username)["result"]:
                return {"error": "Username already exist"}
            else:
                user = models.User(username, request.form["email"], request.form["password"])
                db.session.add(user)
                db.session.commit()
                return {"status": "Successful, User Created"}
        else:
            return {"error": "What are you trying to do?"}


class RTopic(Resource):
    def get(self, topic_name):
        topic = models.Topic.query.filter_by(name=topic_name).first()
        if views.is_empty(topic):
            return {
                "result": False,
                "status": "error",
                "error": "Topic doesn't exit"
            }
        else:
            return {
                "result": True,
                "topic": topic.name,
                "status": "Successful, Topic is on DB",
                "id": topic.id
            }

    def post(self, topic_name=None):
        if isinstance(topic_name,type(None)):
            if "create" == request.form["method"]:
                if views.is_empty(request.form["name"]):
                    return {"status":"error",
                            "error":"Name Empty"}
                if self.get(request.form["name"])["result"]:
                    return {"status":"error",
                            "error":"Topic already exist"}
                else:
                    if "icon" in request.form:
                        topic = models.Topic(request.form["name"], request.form["description"], request.form["icon"])
                    else:
                        topic = models.Topic(request.form["name"], request.form["description"])
                    db.session.add(topic)
                    db.session.commit()
                    return {"status": "Successful, Topic Created"}
        if "update" == request.form["method"]:
            if isinstance(topic_name,type(None)):
                return {"status":"Error! You can't update a topic without a name",
                        "error":"Not name found"}
            if views.is_empty(request.form["name"]):
                return {"status":"Error! Name empty",
                        "error":"Give a fucking valid name"}
            if self.get(topic_name)["result"]:
                try:
                    course = models.Topic.query.filter_by(name=topic_name).first()
                    course.name = request.form["name"]
                    course.icon = request.form["icon"]
                    course.description = request.form["description"]
                    db.session.commit()
                    return {"status": "Successful, Topic Update"}
                except:
                    return {"status": "error1","error":"O.o"}
            else:
                return {"error": "Topic doesn't exist","status":"error2"}
        elif "delete" == request.form["method"]:
            if isinstance(topic_name,type(None)):
                return {"status":"Error! You can't delete a topic without a name",
                        "error":"Not name found"}
            if self.get(topic_name)["result"]:
                try:
                    db.session.delete(models.Topic.query.filter_by(name=topic_name).first())
                    db.session.commit()
                    return {"status": "Successful, Topic Deleted"}
                except:
                    return {"status": "error","error":"O.o"}
            else:
                return {"error": "Topic doesn't exist","status":"error1"}
        else:
            return {"error": "What are you trying to do?","status":"error2"}


class RQuestion(Resource):
    def get(self, question_id=None):
        if question_id is None:
            questions = models.Question.query.all()
            return {
                "questions": [x.id for x in questions]
            }
        else:
            question = models.Question.query.filter_by(id=question_id).first()
            if views.is_empty(question):
                return {
                    "result": False,
                    "status": "error",
                    "error": "question not found"
                }
            else:
                return {
                    "result": True,
                    "type": question.type,
                    "topic": question.topic.name,
                    "status": "Successfull"
                }

    def post(self, question_id=None):
        if isinstance(question_id, type(None)):
            if "create" == request.form["method"]:
                if views.is_empty(request.form["title"]):
                    return {"status":"error2",
                            "error":"Not Valid Title"}
                max_score = views.set_default(int(request.form["max_score"]), 10)
                type_specified = request.form["type"]
                def_image = "https://cdn2.iconfinder.com/data/icons/color-svg-vector-icons-2/512/help_support_question_mark-128.png"
                if type_specified == "msu":  # for multiple selection unique response questions
                    try:
                        question = models.MSUQuestion(request.form["title"], request.form["statement"],
                                                  request.form["topic"], max_score)
                        question.image = views.set_default(request.form["image"],def_image)
                        db.session.add(question)
                        db.session.commit()
                        return {"status":"Question Created"}
                    except Exception, e:
                        return {"status":str(e)}
                elif type_specified == "msm":  # multiple selection multiple response
                    try:
                        question = models.MSMQuestion(request.form["title"], request.form["statement"],
                                                  request.form["topic"], max_score)
                        question.image = views.set_default(request.form["image"],def_image)
                        db.session.add(question)
                        db.session.commit()
                        return {"status":"Question Created"}
                    except Exception, e:
                        return {"status":str(e)}
                elif type_specified == "completation":
                    try:
                        question = models.CompletationQuestion(request.form["title"], request.form["statement"],
                                                           request.form["topic"], max_score)
                        question.image = views.set_default(request.form["image"],def_image)
                        db.session.add(question)
                        db.session.commit()
                        return {"status":"Question Created"}
                    except Exception, e:
                        return {"status":str(e)}
                elif type_specified == "clasification":
                    try:
                        question = models.ClasificationQuestion(request.form["title"], request.form["statement"],
                                                            request.form["topic"], max_score)
                        question.image = views.set_default(request.form["image"],def_image)
                        db.session.add(question)
                        db.session.commit()
                        return {"status":"Question Created"}
                    except Exception, e:
                        return {"status":str(e)}
                elif type_specified == "pairing":
                    try:
                        question = models.PairingQuestion(request.form["title"], request.form["statement"],
                                                      request.form["topic"], max_score)
                        question.image = views.set_default(request.form["image"],def_image)
                        db.session.add(question)
                        db.session.commit()
                        return {"status":"Question Created"}
                    except Exception, e:
                        return {"status":str(e)}
                else:
                    return {
                        "status": "error1",
                        "error": "type specified is not supported"
                    }
            else:
                return {
                    "status": "error2",
                    "error": "method specified is not supported"
                }
        else: #Specific Question Methods
            question = models.Question.query.get(question_id)
            if isinstance(question,type(None)):
                return {"status":"errorA",
                        "error":"Question Not Found"}
            if "update" == request.form["method"]:
                if isinstance(question_id,type(None)):
                    return {"status":"Error! You can't update a question without a name",
                            "error":"Not name found"}
                if views.is_empty(request.form["title"]):
                    return {"status":"Error! title empty",
                            "error":"Give a fucking valid title"}
                if not isinstance(question,type(None)):
                    try:
                        question.title = request.form["title"]
                        question.image = request.form["image"]
                        question.description = request.form["statement"]
                        question.max_score = request.form["score"]
                        db.session.commit()
                        return {"status": "Successful, Topic Update"}
                    except:
                        return {"status": "error1","error":"O.o"}
                else:
                    return {"status":"error",
                            "error":"Question Not Found"}
            elif "delete" == request.form["method"]:
                try:
                    db.session.delete(question)
                    db.session.commit()
                except Exception, e:
                    return {"status":"error",
                            "error":str(e)}
                return {"status":"Question Deleted"}
            else:
                return{"status":"errorB",
                       "error":"Not Valid Method"}


class RAnswer(Resource):
    def get(self, question_id, answer_id=None):
        if question_id and answer_id:
            try:
                answer = models.Answer.query.filter_by(id=answer_id, question_id=question_id).first()
                return {
                    "result": True,
                    "answer": "{}",
                    "id": answer.id,
                    "belongs to question": answer.question_id,
                    "state": answer.state,
                    "text": answer.text
                }
            except Exception:
                return {
                    "status": False,
                    "error": Exception.message
                }
        elif question_id:
            try:
                answers = models.Answer.query.filter_by(question_id=question_id).all()
                question = models.Question.query.filter_by(id=question_id).first()
                return {
                    "status": True,
                    "question": question_id,
                    "statement": question.statement,
                    "answers": [ans.id for ans in answers],
                    "results": views.json_results(question)
                }
            except Exception:
                return {
                    "status": False,
                    "error": Exception.message
                }
        else:
            return {
                "status": False,
                "message": "question id or answer id not specified"
            }

    def post(self, question_id=None, answer_id=None):
        if question_id is not None or answer_id is not None:
            return {
                "status": False,
                "error": "This doesn't make sense..."
            }
        else:
            if "create" in request.form["method"]:
                if "text" in request.form and "state" in request.form and "question" in request.form:
                    if "image" in request.form:
                        answer = models.Answer(request.form["state"], request.form["text"], request.form["question"],
                                               request.form["image"])
                    else:
                        answer = models.Answer(request.form["state"], request.form["text"], request.form["question"])
                    db.session.add(answer)
                    db.commit()
                    return {
                        "status": True,
                        "message": "Answer created",
                        "question": "And it belongs to" + answer.question_id + "question"
                    }
                else:
                    return {
                        "status": False,
                        "message": "Missing information"
                    }
            else:
                return {
                    "status": False,
                    "message": "method specified is not supported"
                }


class REvaluate(Resource):
    def post(self, question_id=None):
        if question_id is None:
            return {"error": "Not accessible",
                    "result": False
                    }
        else:
            question = models.Question.query.filter_by(id=question_id).first()
            if current_user.is_authenticated():
                user = models.User.query.filter_by(username=current_user.username).first()
            if isinstance(question,type(None)):
                return {"error": "Question not found",
                        "result": False
                        }
            else:
                if "type" in request.form and "selected" in request.form:
                    if request.form["type"] == "msu":
                        trueOne = [x.id for x in question.answers if x.state]
                        selected = json.loads(request.form["selected"])
                        result = question.validate_answer(selected[0], trueOne[0])
                        result["points"] = result["score"]*question.max_score
                        if current_user.is_authenticated():
                            new_score(current_user.username, question, result["points"])
                            if result["score"] == 0.0:
                                user.remove_life()
                                db.session.commit()
                            if result["score"] == 1.0:
                                user.give_life()
                                db.session.commit()
                        return result
                    if request.form["type"] == "msm":
                        trueOne = [x.id for x in question.answers if x.state]
                        selected = json.loads(request.form["selected"])
                        selected_objects = [models.Answer.query.filter_by(id=x).first() for x in selected]
                        result = question.validate_answer(len(trueOne), selected_objects)
                        result["points"] = int(result["score"]*question.max_score)
                        if current_user.is_authenticated():
                            new_score(current_user.username, question, result["points"])
                            if result["score"] == 0.0:
                                user.remove_life()
                                db.session.commit()
                            if result["score"] == 1.0:
                                user.give_life()
                                db.session.commit()
                        return result
                    if request.form["type"] == "completation":
                        selected = json.loads(request.form["selected"])
                        result = question.validate_answer(selected[0])
                        result["points"] = result["score"]*question.max_score
                        if current_user.is_authenticated():
                            new_score(current_user.username, question, result["points"])
                            if result["score"] == 0.0:
                                user.remove_life()
                                db.session.commit()
                            if result["score"] == 1.0:
                                user.give_life()
                                db.session.commit()
                        return result
                    if request.form["type"] == "pairing":
                        correct = views.json_results(question)
                        result = question.validate_answer(request.form["selected"], correct)
                        result["points"] = result["score"]*question.max_score
                        if current_user.is_authenticated():
                            new_score(current_user.username, question, result["points"])
                            if result["score"] == 0.0:
                                user.remove_life()
                                db.session.commit()
                            if result["score"] == 1.0:
                                user.give_life()
                                db.session.commit()
                        return result
                    if request.form["type"] == "clasification":
                        correct = views.json_results(question)
                        result = question.validate_answer(request.form["selected"], correct)
                        result["points"] = int(result["score"]*question.max_score)
                        if current_user.is_authenticated():
                            new_score(current_user.username, question, result["points"])
                            if result["score"] == 0.0:
                                user.remove_life()
                                db.session.commit()
                            if result["score"] == 1.0:
                                user.give_life()
                                db.session.commit()
                        return result
                    else:
                        return {
                            "error": "Type Invalid",
                            "result": False
                        }


class RRegister(Resource):
    def post(self):
        if "user" in request.form and "topic_id" in request.form:
            cur_user = models.User.query.filter_by(username=request.form["user"]).first()
            topic = models.Topic.query.filter_by(id=int(request.form["topic_id"])).first()
            if cur_user is None and topic is None:
                return{
                    "status": False,
                    "message": "User and Topic don't exist"
                }
            elif cur_user is None:
                return {
                    "status": False,
                    "message": "User not found"
                }
            elif topic is None:
                return {
                    "status": False,
                    "message": "Topic not found"
                }
            cur_user.set_topic(request.form["topic_id"])
            db.session.commit()
            return {
                "status": True,
                "message": "User registered successfully"
            }
        else:
            return {
                "status": False,
                "message": "Operation un-supported"
            }

    def get(self, username):
        user = models.User.query.filter_by(username=username).first()
        if views.is_empty(user):
            return {
                "result": False,
                "status": "error",
                "error": "Username doesn't exit"
            }
        else:
            topic = models.Topic.query.filter_by(id=user.cur_topic_id).first()
            if views.is_empty(topic):
                return{
                    "result": False,
                    "message": "User is not inscribed in any topic"
                }
            else:
                return {
                    "result": True,
                    "topic": topic.name,
                    "status": "User has a Topic"
                }


class RNextQuestion(Resource):
    def get(self, topic_id, question_id):
        topic = models.Topic.query.get(topic_id)
        questions = [x.id for x in topic.questions]
        if question_id in questions:
            pass
        else:
            return {
                "error": "Question Not Found",
                "return": False
            }
        questions.sort()
        try:
            next = questions[questions.index(question_id)+1]
            return {
                "url": views.url_for("questions", course=topic.name, num=next),
                "return": True
            }
        except IndexError:
            topics = models.Topic.query.all()
            topic_ids = [x.id for x in topics]
            topic_ids.sort()
            try:
                next = topic_ids[topic_ids.index(topic_id)+1]
            except IndexError:
                return {
                    "url": views.url_for("home")
                }
            topic = models.Topic.query.get(next)
            return {
                "url": views.url_for("course", course=topic.name)
            }

class RVideo(Resource):
    def get(self, question_id):
        videos = models.HelpVideos.query.filter_by(question_id=question_id)
        list = []
        for video in videos:
            print video.video_url
            if video.video_url:
                list.append(video.video_url)
        question = models.Question.query.filter_by(id=question_id).first()
        return dict(status=True, videos=list, topic=question.topic)

    def post(self):
        if "video" in request.form and "question_id" in request.form and "action" in request.form:
            question = models.Question.query.filter_by(id=request.form["question_id"])
            if views.is_empty(question):
                return{
                    "status": False,
                    "error": "Question not found, verify again"
                }
            if request.form["action"] == "insert":
                q = models.Question.query.filter_by(id=request.form["question_id"]).first()
                vh = models.HelpVideos(request.form["video"], q)
                db.session.add(vh)
            elif request.form["action"] == "delete":
                v = models.HelpVideos.query.filter_by(video_url=request.form["video"]).first()
                if v:
                    db.session.delete(v)
                else:
                    return{
                        "status": False,
                        "message": "This video was not found"
                    }
            else:
                return{
                    "status": False,
                    "message": "You must say only 'insert' or 'delete'"
                }
            db.session.commit()
            return{
                "status": True,
                "message": "Video inserted successfully"
            }
        else:
            return{
                "status": False,
                "message": "The information provided is not correct, must have 'video', 'question_id', and 'action'"
            }

class RHelpReport(Resource):
    def get(self):
        if "question_id" in request.form and "user_username" in request.form and "report_id" in request.form:
            return {
                "status": False,
                "message": "Too much information!"
            }
        elif "question_id" in request.form and "user_username" in request.form:
            qs = models.Question.query.filter_by(id=request.form["question_id"])
            q = None
            if len(qs)>0:
                q = qs.first()
            else:
                return{
                    "status": False,
                    "message": "Question not found"
                }
            us = models.User.query.filter_by(username=request.form["user_username"])
            u = None
            if len(us)>0:
                u = us.first()
            else:
                return{
                    "status": False,
                    "message": "User not found"
                }
            reports = models.HelpReport.query.filter_by(user_username=request.form["user_username"])
            if len(reports)>0:
                list = []
                for report in reports:
                    if report.question == q:
                        list.append(report)

                return{
                    "status": True,
                    "reports": list
                }
            else:
                return{
                    "status": False,
                    "message": "No reports found"
                }
        elif "report_id" in request.form:
            r = models.HelpReport.query.filter_by(id=request.form["report_id"]).first()
            if r:
                return{
                    "status": True,
                    "report": r.report,
                    "for_question": r.question.id,
                    "by": r.user.username
                }
            else:
                return {
                    "status": False,
                    "message": "Report not found"
                }
        elif "question_id" in request.form:
            q = models.Question.query.filter_by(question_id=request.form["question_id"]).first()
            if q:
                reports = models.HelpReport.query.filter_by(question_id=request.form["question_id"])
                if len(reports)>0:
                    return{
                        "status": True,
                        "reports": reports
                    }
                else:
                    return{
                        "status": False,
                        "message": "This question doesn't have reports"
                    }
            else:
                return{
                    "status": False,
                    "message": "Question not found"
                }
        elif "user_username" in request.form:
            u = models.User.query.filter_by(username=request.form["user_username"])
            if u:
                reports = models.HelpReport.query.filter_by(user_username=request.form["user_username"])
                if len(reports)>0:
                    return{
                        "status": True,
                        "reports": reports
                    }
                else:
                    return {
                        "status": False,
                        "message": "This user hasn't made any reports!"
                    }
            else:
                return{
                    "status": False,
                    "message": "User not found!"
                }

    def post(self):
        if "username" in request.form and "question_id" in request.form and "report" in request.form:
            u = models.User.query.get(request.form['username'][1:len(request.form['username'])-1])
            if u:
                print "primer filtro pasado"
                print request.form["question_id"][1:len(request.form['question_id'])-1]
                q = models.Question.query.filter_by(id=request.form["question_id"][1:len(request.form['question_id'])-1]).first()
                if q:
                    print "Entre en q"
                    r = models.HelpReport(request.form["report"], q, u)
                    db.session.add(r)
                    db.session.commit()
                    return{
                        "status": True,
                        "message": "Report generated correctly!"
                    }
                else:
                    return {
                        "status": False,
                        "message": "Question not found"
                    }
            else:
                return{
                    "status": False,
                    "message": "User not found"
                }
        else:
            return{
                "status": False,
                "message": "'username', 'question_id' and 'report' must be given"
            }

api.add_resource(RError, '/api', "/api/")
api.add_resource(RUser, "/api/users/<username>")
api.add_resource(RTopic, "/api/topics/<topic_name>", "/api/topics/")
api.add_resource(RQuestion, "/api/question/<int:question_id>", "/api/question/")
api.add_resource(RAnswer, "/api/answer/<int:question_id>", "/api/answer/",
                 "/api/answer/<int:question_id>/<int:answer_id>")
api.add_resource(REvaluate, "/api/evaluate/", "/api/evaluate/<question_id>")
api.add_resource(RRegister, "/api/register/", "/api/register/<username>")
api.add_resource(RNextQuestion, "/api/next/<int:topic_id>/<int:question_id>")
api.add_resource(RVideo, "/api/video/<int:question_id>", "/api/video/")
api.add_resource(RHelpReport, "/api/report/")
