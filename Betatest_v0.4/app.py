from logging import setLogRecordFactory
from sched import scheduler
import string
from flask import *
from flask_pymongo import PyMongo
from pymongo import MongoClient
import datetime
from flask import flash
from flask import url_for
import gridfs
import time
import pytz
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.schedulers.background import BackgroundScheduler
import requests
import json

app = Flask(__name__)
app.config['SECRET_KEY'] = "2019"
app.config["MONGO_URI"] = "mongodb://localhost:27017/survey"
mongo = PyMongo(app)

client = MongoClient('localhost', 27017)
members = mongo.db.members
db = client['survey']

#홈화면
@app.route('/')
def home():
   return render_template('login.html')

# 회원가입
@app.route('/register', methods=['GET','POST'])
def register():
    if request.method == 'GET':
        return render_template("register.html")
    else:
        id = request.form.get("id", type=str)
        pwd = request.form.get("pwd", type=str)
        pwd2 = request.form.get("pwd2", type=str)
        
        current_utc_time = round(datetime.datetime.utcnow().timestamp() * 1000)
        post = {
            "id": id,
            "pwd": pwd,
            "register_date": current_utc_time,
            "attach_count": 0,
            "submit_count": 0,
            "weekly_count": 0,
            "daily": 0,
            "CIN_count": 0
        }
        # print(mongo.db.list_collection_names())
        if id in mongo.db.list_collection_names() :
            flash("이미 가입한 계정이 있습니다.")
            return render_template("register.html", data=id)
        else :
            #회원가입시 컬렉션 생성
            mongo.db.create_collection(id)  
        
        if not (id and pwd and pwd2):
            return "모두 입력해주세요"
        elif pwd != pwd2:
            return "비밀번호를 확인해주세요."
        else:
            members.insert_one(post)
            return render_template("one_time.html", data=id)

# 회원가입
@app.route('/register_en', methods=['GET','POST'])
def register_en():
    if request.method == 'GET':
        return render_template("register_en.html")
    else:
        id = request.form.get("id", type=str)
        pwd = request.form.get("pwd", type=str)
        pwd2 = request.form.get("pwd2", type=str)
        
        current_utc_time = round(datetime.datetime.utcnow().timestamp() * 1000)
        post = {
            "id": id,
            "pwd": pwd,
            "register_date": current_utc_time,
            "attach_count": 0,
            "submit_count": 0,
            "weekly_count": 0,
            "daily": 0,
            "CIN_count": 0
        }
        if id in mongo.db.list_collection_names() :
            flash("이미 가입한 계정이 있습니다.")
            return render_template("register.html", data=id)
        else :
            #회원가입시 컬렉션 생성
            mongo.db.create_collection(id)  
        
        if not (id and pwd and pwd2):
            return "모두 입력해주세요"
        elif pwd != pwd2:
            return "비밀번호를 확인해주세요."
        else:
            members.insert_one(post)
            return render_template("one_time.html", data=id)


@app.route('/ajax', methods=['GET', 'POST'])
def ajax():
    data = request.get_json()
    #회원가입한 id와 같은 이름의 컬렉션 찾기
    #list()함수 이용해서 첫 번째 키 가져오기(id 값)
    x_survey = list(data.values())[0]
    survey_result = mongo.db.get_collection(x_survey)
    del data['ID']
    #해당 컬렉션에 data upload
    survey_result.insert_one(data)
    data.pop('_id')
    daily = data['1_formData1']
    daily_f = list(m['value'] for m in daily)
    # if daily_f[3] == '1' and daily_f[4] == '1':
    #     print("갤럭시와 갤럭시 워치 사용자입니다.")
    #     members.update_one({'id': x_survey}, {'$set': {'daily': 1}})
    # else:
    #     if daily_f[3] == '2' and daily_f[4] == '2':
    #         print("아이폰과 핏빗 사용자입니다.")
    #         members.update_one({'id': x_survey}, {'$set': {'daily': 2}})
    #     if (daily_f[3] == '1' and daily_f[4] == '2') or (daily_f[3] == '2' and daily_f[4] == '1'):
    #         print("2번과 3번 조합이 틀립니다.")
    if daily_f[3] == '1':
        # print('갤럭시 사용자입니다.')
        members.update_one({'id':x_survey}, {'$set':{'daily':1}})
    else:
        if daily_f[3] == '2':
            # print('아이폰 사용자입니다.')
            members.update_one({'id':x_survey}, {'$set':{'daily':2}})

    return jsonify(result = "success", result2= data, result3=daily)
    
#로그인
@app.route('/user/login', methods = ['POST'])
def login():
    id = request.form['id']
    pwd = request.form['pwd']
    #form에서 가져온 id를 세션에 저장
    session['id'] = id
    user = members.find_one({'id':id}, {'pwd':pwd})
    # print(wcount)
    if user is None:
        flash("접속하신 계정은 존재하지 않는 계정입니다.")
        return render_template('login.html')
    else:
        member_id = members.find_one({'id': id})
        if member_id['pwd'] == pwd: #비밀번호가 맞는지 확인
            daily_cal = member_id["daily"]
            cin_count = member_id["CIN_count"]
            print(daily_cal)
            if daily_cal == 1 : #갤럭시 사용자
                return render_template('cal_test.html', sid=id, cin=cin_count)
            else:
                if daily_cal == 2: #아이폰 사용자
                    count = member_id['submit_count']
                    fcount = member_id['attach_count']
                    wcount = member_id['weekly_count']
                    asia_seoul = datetime.datetime.fromtimestamp(time.time(), pytz.timezone('Asia/Seoul'))
                    t = ['월요일', '화요일', '수요일', '목요일', '금요일', '토요일', '일요일']
                    now = t[asia_seoul.today().weekday()]

                    if now == "토요일":
                        members.update_one({'id': id}, {'$inc': {'weekly_count': -1}}) #토요일 로그인 -> count가 1씩 감소
                        return render_template('weekly.html', sid=id, cnt=count, fcnt=fcount, wcnt=wcount)
                    else:
                        if member_id['weekly_count'] > 0:
                            return render_template('weekly.html', sid=id, cnt=count, fcnt=fcount, wcnt=wcount)
                        else:
                            if member_id['daily'] == 1:
                                return render_template('gal_daily.html', sid=id, cnt=count, fcnt=fcount, wcnt=wcount)
                            else:
                                if member_id['daily'] == 2:
                                    return render_template('daily.html', sid=id, cnt=count, fcnt=fcount, wcnt=wcount)                    
        else: #비밀번호가 틀리면
            flash('비밀번호가 일치하지 않습니다.')
            return render_template('login.html')

#갤럭시 사용자 - 캘린더 보여주기 
# @app.route('/cal', methods = ['POST'])
# def cal():
#     member_id = members.find_one({'id': id})
#     count = member_id['submit_count']
#     fcount = member_id['attach_count']
#     wcount = member_id['weekly_count']
#     asia_seoul = datetime.datetime.fromtimestamp(time.time(), pytz.timezone('Asia/Seoul'))
#     t = ['월요일', '화요일', '수요일', '목요일', '금요일', '토요일', '일요일']
#     now = t[asia_seoul.today().weekday()]

#     if now == "금요일":
#         members.update_one({'id': id}, {'$inc': {'weekly_count': -1}}) #토요일 로그인 -> count가 1씩 감소
#         return render_template('weekly.html', sid=id, cnt=count, fcnt=fcount, wcnt=wcount)
#     else:
#         if member_id['weekly_count'] > 0:
#             return render_template('weekly.html', sid=id, cnt=count, fcnt=fcount, wcnt=wcount)
#         else:
#             if member_id['daily'] == 1:
#                 return render_template('gal_daily.html', sid=id, cnt=count, fcnt=fcount, wcnt=wcount)
#             else:
#                 if member_id['daily'] == 2:
#                     return render_template('daily.html', sid=id, cnt=count, fcnt=fcount, wcnt=wcount)    


#로그아웃
@app.route('/logout')
def logout():
    #세션 pop
    session.pop('id', None)
    return render_template('login.html')

#daily survey-iphone user
@app.route('/moody', methods=['POST'])
def moody():  
    data = request.files['data']
    st = data.read()
    l = st.decode()
    evl = eval(l)
    s_id = evl['sid']
    mood = evl['mood']
    #print("mood is ", mood)
    md = { "mood": mood }
    survey_coll = mongo.db.get_collection(s_id)
    survey_coll.insert_one(md)
    
    if 'filed' in request.files:
        f = request.files['filed']
        print("file1 is", f)
        contents = f.read()
        fs = gridfs.GridFS(db, s_id)
        fname = f.filename
        members.update_one({'id': s_id}, {'$inc': {'attach_count': 1}})
        fs.put(contents, filename=fname)
    if 'filed2' in request.files:
        f2 = request.files['filed2']
        print("file2 is", f2)
        contents = f2.read()
        fs2 = gridfs.GridFS(db, s_id)
        fname2 = f2.filename
        members.update_one({'id': s_id}, {'$inc': {'attach_count': 1}})
        fs2.put(contents, filename=fname2)

    
    members.update_one({'id': s_id}, {'$inc': {'submit_count': 1}})
    return render_template('weekly.html')

#daily survey-galaxy user
@app.route('/moody2', methods=['POST'])
def moody2():  
    data = request.files['data']
    st = data.read()
    l = st.decode()
    evl = eval(l)
    s_id = evl['sid']
    mood = evl['mood']
    #print("mood is ", mood)
    md = { "mood": mood }
    survey_coll = mongo.db.get_collection(s_id)
    survey_coll.insert_one(md)
    
    if 'filed[]' in request.files:
        f = request.files.getlist('filed[]')
        for file in f:
          print("file is", file)
          contents = file.read()
          fs = gridfs.GridFS(db, s_id)
          fname = file.filename
          fs.put(contents, filename=fname)
        members.update_one({'id': s_id}, {'$inc': {'attach_count': 1}})
    
    members.update_one({'id': s_id}, {'$inc': {'submit_count': 1}})
    return render_template('weekly.html')

#마지막 페이지
@app.route('/final', methods=['GET', 'POST'])
def final():
    session.pop('id', None)
    return render_template("final.html")

#weekly survey
@app.route('/weekly', methods=['GET', 'POST'])
def weekly():
    data = request.get_json()
    x_survey = list(data.values())[0]
    survey_result = mongo.db.get_collection(x_survey)
    del data['ID']
    survey_result.insert_one(data)
    data.pop('_id')
    member_id = members.find_one({'id': x_survey})
    count = member_id['submit_count']
    fcount = member_id['attach_count']
    if member_id['daily'] == 1:
        return jsonify(render_template("gal_daily.html", sid=x_survey, cnt=count, fcnt=fcount))
    else:
        if member_id['daily'] == 2:
            return jsonify(render_template("daily.html", sid=x_survey, cnt=count, fcnt=fcount))

#팝업창
@app.route('/pop.html', methods=['GET'])
def window_pop():
    return render_template("pop.html")

#백그라운드 실행-토요일마다
asia_seoul = datetime.datetime.fromtimestamp(time.time(), pytz.timezone('Asia/Seoul'))
today = asia_seoul.strftime("%Y%m%d")

def count():
    asia_seoul = datetime.datetime.fromtimestamp(time.time(), pytz.timezone('Asia/Seoul'))
    # print(asia_seoul.today())
    t = ['월요일', '화요일', '수요일', '목요일', '금요일', '토요일', '일요일']
    now = t[asia_seoul.today().weekday()]
    if now == '금요일':
        members.update_many({}, {'$inc': {'weekly_count': 1}}) #collection에 있는 모든 id에서 count가 1씩 증가

#모비우스 cnt 개수 가져오기
IoT_1 = "http://114.71.220.59:7579"

def countCIN(serverName, aeName, today):
    # asia_seoul = datetime.datetime.fromtimestamp(time.time(), pytz.timezone('Asia/Seoul'))
    # today = asia_seoul.strftime("%Y%m%d")
    cra = '&cra=' + str(int(today) - 1) + 'T150000'
    crb = '&crb=' + today + 'T145959'
    
    url1 = IoT_1 + "/Mobius/" + aeName + "/mobile?fu=1&ty=4&rcn=4" + cra + crb
    url2 = IoT_1 + "/Mobius/" + aeName + "/watch?fu=1&ty=4&rcn=4"  + cra + crb
    payload={}
    headers = {
    'Accept': 'application/json',
    'X-M2M-RI': '12345',
    'X-M2M-Origin': 'ubicomp_super'
    }
    try:
        response1 = requests.request("GET", url1, headers=headers, data=payload)
        response2 = requests.request("GET", url2, headers=headers, data=payload)
        data1 = json.loads(response1.text)
        data2 = json.loads(response2.text)
        total = len(data1['m2m:uril'])
        total = total + len(data2['m2m:uril'])
        return total

    except:
        # print("mobile: ", response1)
        # print("watch: ", response2)
        return None

def getCountDict(today):
    dict_CIN = {}

    for i in range(600, 1000):
        aeName = 'S' + str(i)
        cnt = countCIN('IoT_1', aeName, today)
        if cnt == None:
            continue
        else:
            dict_CIN[aeName] = cnt
            
    for k,v in dict_CIN.items():
        k=str(k)
        print(v)
        # print("{}:{}".format(k,v))
        member_id = members.find_one({'id': k})
        # print(member_id)
        # members.update_one({'id':k}, {'$set':{'CIN_count':v}})
        members.update_one({'id':k}, {'$set':{'CIN_count':v}})
    return dict_CIN
    
if __name__ == '__main__':
    
    sched = BackgroundScheduler(daemon=True)
    asia_seoul = datetime.datetime.fromtimestamp(time.time(), pytz.timezone('Asia/Seoul'))
    today = asia_seoul.strftime("%Y%m%d")
    print(type(today))
    sched.add_job(count, 'cron', hour="00", minute="00", id="test_1")
    sched.add_job(getCountDict, 'cron', hour="23", minute="59", id="test_2", args=[today])
    sched.start()

    #from waitress import serve
    #serve(app, host="0.0.0.0", port=2017)
    app.run(host='0.0.0.0', port=2019)
