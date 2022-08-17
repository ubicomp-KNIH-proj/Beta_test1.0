from logging import setLogRecordFactory
from sched import scheduler
from flask import *
from flask_pymongo import PyMongo
from pymongo import MongoClient
import datetime
from flask import flash
from flask import url_for
import gridfs
import time
import pytz
from apscheduler.schedulers.background import BackgroundScheduler
import requests
import json
from datetime import timedelta
from flask import session, app
from calIndexSearch import calIndexSearch

######### Config #########
app = Flask(__name__)
app.config['SECRET_KEY'] = "2019"
app.config["MONGO_URI"] = "mongodb://localhost:27017/survey"
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=5)
mongo = PyMongo(app)

client = MongoClient('localhost', 27017)
members = mongo.db.members
db = client['survey']
IoT_1 = "http://114.71.220.59:7579"
# Ubi_Lab, Dept. of Internet of Things, ML, SCH Univ.
######### Config #########


#홈화면
@app.route('/')
def home():
   return render_template('login.html')

#홈화면_영어
@app.route('/en')
def home_en():
   return render_template('login_en.html')

# 회원가입
@app.route('/register', methods=['GET','POST'])
def register():
    if request.method == 'GET':
        return render_template("register.html")
    else:
        id =  'S' + request.form.get("id", type=str)
        pwd = request.form.get("pwd", type=str)
        pwd2 = request.form.get("pwd2", type=str)
        
        now = datetime.datetime.now()
        today_y = now.year
        today_m = now.month
        today_d = now.day
        post = {
            "id": id,
            "pwd": pwd,
            "register_year": today_y,
            "register_month": today_m,
            "register_day": today_d,
            "gyro_count": 0,
            "acc_count": 0,
            "health_count": 0,
            "submit_count": 0,
            "weekly_count": 0,
            "attach_count": 0,
            "daily": 0,
            "CIN_count": 0,
            "cal_list": []
        }

        if id in mongo.db.list_collection_names() :
            flash("이미 가입한 계정이 있습니다.")
            return render_template("register.html", data=id)
        else :
            mongo.db.create_collection(id)  #회원가입시 컬렉션 생성
        
        if not (id and pwd and pwd2): # 아이디, 비밀번호 중 하나라도 미입력시
            return "모두 입력해주세요"
        elif pwd != pwd2: # 비밀번호가 틀렸을 시
            return "비밀번호를 확인해주세요."
        else: # 정상 로그인
            members.insert_one(post)
            return render_template("one_time.html", data=id)

# 회원가입_영어
@app.route('/register_en', methods=['GET','POST'])
def register_en():
    if request.method == 'GET':
        return render_template("register_en.html")
    else:
        id =  'S' + request.form.get("id", type=str)
        pwd = request.form.get("pwd", type=str)
        pwd2 = request.form.get("pwd2", type=str)
        
        now = datetime.datetime.now()
        today_y = now.year
        today_m = now.month
        today_d = now.day
        post = {
            "id": id,
            "pwd": pwd,
            "register_year": today_y,
            "register_month": today_m,
            "register_day": today_d,
            "gyro_count": 0,
            "acc_count": 0,
            "health_count": 0,
            "submit_count": 0,
            "weekly_count": 0,
            "attach_count": 0,
            "daily": 0,
            "CIN_count": 0,
            "cal_list": []
        }

        if id in mongo.db.list_collection_names() : # 회원가입 되어있는 Sid 접근시 
            flash("Already signed up for an account. Please check again!")
            return render_template("register_en.html", data=id)
        else :
            mongo.db.create_collection(id)  #회원가입시 컬렉션 생성
        
        if not (id and pwd and pwd2): # 아이디, 비밀번호 중 하나라도 미입력시
            return "모두 입력해주세요"
        elif pwd != pwd2: # 비밀번호가 틀렸을 시
            return "비밀번호를 확인해주세요."
        else: # 정상 로그인
            members.insert_one(post)
            return render_template("one_time_en.html", data=id)

# One-time survey 아이폰, 갤럭시 사용자 구분
@app.route('/ajax', methods=['GET', 'POST'])
def ajax():
    data = request.get_json()
    x_survey = list(data.values())[0]
    survey_result = mongo.db.get_collection(x_survey)
    del data['ID']
    survey_result.insert_one(data)
    data.pop('_id')
    daily = data['1_formData1']
    daily_f = list(m['value'] for m in daily)

    if daily_f[3] == '1':
        members.update_one({'id':x_survey}, {'$set':{'daily':1}})
    else:
        if daily_f[3] == '2':
            members.update_one({'id':x_survey}, {'$set':{'daily':2}})

    return jsonify(result = "success", result2= data, result3=daily)
    
#로그인
@app.route('/user/login', methods = ['POST'])
def login():
    id = 'S' + request.form['id']
    pwd = request.form['pwd']
    session['id'] = id
    user = members.find_one({'id':id}, {'pwd':pwd})

    if user is None: #members에 없음
        flash("접속하신 계정은 존재하지 않는 계정입니다.")
        return render_template('login.html')
    else: #members에 있음
        member_id = members.find_one({'id': id})
        if member_id['pwd'] == pwd: #비밀번호가 맞는지 확인
            reg_coll = mongo.db.get_collection(id) 
            reg_check = reg_coll.find_one({'check':1}) #해당 컬렉션에 onetime 결과가 있는지 확인

            if reg_check is None:
                flash("회원가입을 이어서 진행합니다.")
                return render_template('one_time.html', data=id)
            else:
                session['id'] = request.form['id'] 
                session.permanent = True

                daily_cal = member_id["daily"]
                cin_count = member_id["CIN_count"]
                cal_list = member_id["cal_list"]
                reg_y = member_id["register_year"]
                reg_m = member_id["register_month"]
                reg_d = member_id["register_day"]

                if daily_cal == 1 : #갤럭시 사용자
                    return render_template('cal_test.html', sid=id, cin=cin_count, cal=cal_list, reg_y=reg_y, reg_m=reg_m, reg_d=reg_d)
                else:
                    if daily_cal == 2: #아이폰 사용자
                        count = member_id['submit_count']
                        wcount = member_id['weekly_count']
                        hcount = member_id['health_count']
                        gcount = member_id['gyro_count']
                        acount = member_id['acc_count']
                        fcount = member_id['attach_count']

                        if member_id['weekly_count'] > 0:
                            return render_template('weekly.html', sid=id, cnt=count, fcnt=fcount, wcnt=wcount)
                        else:
                            if member_id['daily'] == 1:
                                return render_template('gal_daily.html', sid=id, cnt=count, fcnt=fcount, wcnt=wcount)
                            else:
                                if member_id['daily'] == 2:
                                    return render_template('daily.html', sid=id, cnt=count, wcnt=wcount, hcnt=hcount, gcnt=gcount, acnt=acount)     

        else: #비밀번호가 틀리면
            flash('비밀번호가 일치하지 않습니다.')
            return render_template('login.html')

#로그인_영어
@app.route('/user/login_en', methods = ['POST'])
def login_en():
    id = 'S' + request.form['id']
    pwd = request.form['pwd']
    session['id'] = id
    user = members.find_one({'id':id}, {'pwd':pwd})

    if user is None: #members에 없음
        flash("The account you accessed does not exist")
        return render_template('login_en.html')
    else: #members에 있음
        member_id = members.find_one({'id': id})
        if member_id['pwd'] == pwd: #비밀번호가 맞는지 확인
            reg_coll = mongo.db.get_collection(id) 
            reg_check = reg_coll.find_one({'check':1}) #해당 컬렉션에 onetime 결과가 있는지 확인

            if reg_check is None:
                flash("The survey for membership registration has not been completed.")
                return render_template('one_time_en.html', data=id)
            else:
                session['id'] = request.form['id'] 
                session.permanent = True

                daily_cal = member_id["daily"]
                cin_count = member_id["CIN_count"]
                cal_list = member_id["cal_list"]
                reg_y = member_id["register_year"]
                reg_m = member_id["register_month"]
                reg_d = member_id["register_day"]

                if daily_cal == 1 : #갤럭시 사용자
                    return render_template('cal_test_en.html', sid=id, cin=cin_count, cal=cal_list, reg_y=reg_y, reg_m=reg_m, reg_d=reg_d)
                else:
                    if daily_cal == 2: #아이폰 사용자
                        count = member_id['submit_count']
                        wcount = member_id['weekly_count']
                        hcount = member_id['health_count']
                        gcount = member_id['gyro_count']
                        acount = member_id['acc_count']
                        fcount = member_id['attach_count']

                        if member_id['weekly_count'] > 0:
                            return render_template('weekly_en.html', sid=id, cnt=count, fcnt=fcount, wcnt=wcount)
                        else:
                            if member_id['daily'] == 1:
                                return render_template('gal_daily_en.html', sid=id, cnt=count, fcnt=fcount, wcnt=wcount)
                            else:
                                if member_id['daily'] == 2:
                                    return render_template('daily_en.html', sid=id, cnt=count, wcnt=wcount, hcnt=hcount, gcnt=gcount, acnt=acount)     

        else: #비밀번호가 틀리면
            flash('The password you entered does not match.')
            return render_template('login_en.html')


#로그아웃
@app.route('/logout')
def logout():
    session.pop('id', None) # 세션 종료
    return render_template('login.html')

#Daily_아이폰 사용자
@app.route('/moody', methods=['POST'])
def moody():  
    data = request.files['data']
    st = data.read()
    l = st.decode()
    evl = eval(l)
    s_id = evl['sid']
    mood = evl['mood']
    date = evl['date']

    md = { "mood": mood , "date": date }
    survey_coll = mongo.db.get_collection(s_id)
    survey_coll.insert_one(md)

    if 'filed' in request.files:
        f = request.files['filed']
        print("file1 is", f)
        contents = f.read()
        fs = gridfs.GridFS(db, s_id)
        fname = f.filename
        members.update_one({'id': s_id}, {'$inc': {'gyro_count': 1}})
        fs.put(contents, filename=fname)
    if 'filed2' in request.files:
        f2 = request.files['filed2']
        print("file2 is", f2)
        contents = f2.read()
        fs2 = gridfs.GridFS(db, s_id)
        fname2 = f2.filename
        members.update_one({'id': s_id}, {'$inc': {'acc_count': 1}})
        fs2.put(contents, filename=fname2)
    if 'filed3' in request.files:
        f3 = request.files['filed3']
        print("file3 is", f3)
        contents = f3.read()
        fs3 = gridfs.GridFS(db, s_id)
        fname3 = f3.filename
        members.update_one({'id': s_id}, {'$inc': {'health_count': 1}})
        fs3.put(contents, filename=fname3)

    members.update_one({'id': s_id}, {'$inc': {'submit_count': 1}})
    return render_template('login.html')

#Daily_아이폰 사용자_영어
@app.route('/moody_en', methods=['POST'])
def moody_en():  
    data = request.files['data']
    st = data.read()
    l = st.decode()
    evl = eval(l)
    s_id = evl['sid']
    mood = evl['mood']
    date = evl['date']

    md = { "mood": mood , "date": date }
    survey_coll = mongo.db.get_collection(s_id)
    survey_coll.insert_one(md)
    
    if 'filed' in request.files:
        f = request.files['filed']
        print("file1 is", f)
        contents = f.read()
        fs = gridfs.GridFS(db, s_id)
        fname = f.filename
        members.update_one({'id': s_id}, {'$inc': {'gyro_count': 1}})
        fs.put(contents, filename=fname)
    if 'filed2' in request.files:
        f2 = request.files['filed2']
        print("file2 is", f2)
        contents = f2.read()
        fs2 = gridfs.GridFS(db, s_id)
        fname2 = f2.filename
        members.update_one({'id': s_id}, {'$inc': {'acc_count': 1}})
        fs2.put(contents, filename=fname2)
    if 'filed3' in request.files:
        f3 = request.files['filed3']
        print("file3 is", f3)
        contents = f3.read()
        fs3 = gridfs.GridFS(db, s_id)
        fname3 = f3.filename
        members.update_one({'id': s_id}, {'$inc': {'health_count': 1}})
        fs3.put(contents, filename=fname3)

    members.update_one({'id': s_id}, {'$inc': {'submit_count': 1}})
    return render_template('weekly.html')

#Daily_갤럭시 사용자
@app.route('/moody2', methods=['POST'])
def moody2():  
    data = request.files['data']
    st = data.read()
    l = st.decode()
    evl = eval(l)
    s_id = evl['sid']
    mood = evl['mood']
    date = evl['date']

    md = { "mood": mood , "date": date }
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

#Daily_갤럭시 사용자_영어
@app.route('/moody2_en', methods=['POST'])
def moody2_en():  
    data = request.files['data']
    st = data.read()
    l = st.decode()
    evl = eval(l)
    s_id = evl['sid']
    mood = evl['mood']
    date = evl['date']

    md = { "mood": mood , "date": date }
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
    return render_template('weekly_en.html')

#마지막 페이지
@app.route('/final', methods=['GET', 'POST'])
def final():
    session.pop('id', None)
    return render_template("final.html")

#마지막 페이지_영어
@app.route('/final_en', methods=['GET', 'POST'])
def final_en():
    session.pop('id', None)
    return render_template("final_en.html")

#Weekly
@app.route('/weekly', methods=['GET', 'POST'])
def weekly():
    data = request.get_json()
    x_survey = list(data.values())[0]
    survey_result = mongo.db.get_collection(x_survey)
    del data['ID']
    survey_result.insert_one(data)
    data.pop('_id')
    member_id = members.find_one({'id': x_survey})
    members.update_one({'id': x_survey}, {'$inc': {'weekly_count': -1}}) # Weekly survey 완료시-> count가 1씩 감소

    count = member_id['submit_count']
    wcount = member_id['weekly_count']
    hcount = member_id['health_count']
    gcount = member_id['gyro_count']
    acount = member_id['acc_count']
    fcount = member_id['attach_count']
    
    if member_id['daily'] == 1:
        return jsonify(render_template("gal_daily.html", sid=x_survey, cnt=count, fcnt=fcount))
    else:
        if member_id['daily'] == 2:
            return jsonify(render_template('daily.html', sid=id, cnt=count, wcnt=wcount, hcnt=hcount, gcnt=gcount, acnt=acount))

#Weekly_영어
@app.route('/weekly_en', methods=['GET', 'POST'])
def weekly_en():
    data = request.get_json()
    x_survey = list(data.values())[0]
    survey_result = mongo.db.get_collection(x_survey)
    del data['ID']
    survey_result.insert_one(data)
    data.pop('_id')
    member_id = members.find_one({'id': x_survey})
    members.update_one({'id': x_survey}, {'$inc': {'weekly_count': -1}}) # Weekly survey 완료시-> count가 1씩 감소

    count = member_id['submit_count']
    wcount = member_id['weekly_count']
    hcount = member_id['health_count']
    gcount = member_id['gyro_count']
    acount = member_id['acc_count']
    fcount = member_id['attach_count']
    
    if member_id['daily'] == 1:
        return jsonify(render_template("gal_daily_en.html", sid=x_survey, cnt=count, fcnt=fcount))
    else:
        if member_id['daily'] == 2:
            return jsonify(render_template('daily_en.html', sid=id, cnt=count, wcnt=wcount, hcnt=hcount, gcnt=gcount, acnt=acount))

#캘린더_갤럭시 사용자
@app.route('/ajax3', methods=['GET', 'POST'])
def ajax3():
    data = request.get_json()
    x_survey = list(data.values())[0]
    member_id = members.find_one({'id': x_survey})

    count = member_id['submit_count']
    wcount = member_id['weekly_count']
    hcount = member_id['health_count']
    gcount = member_id['gyro_count']
    acount = member_id['acc_count']
    fcount = member_id['attach_count']
    cin_count = member_id["CIN_count"]

    if member_id['weekly_count'] > 0:
        return jsonify(render_template('weekly.html', sid=x_survey, cnt=count, fcnt=fcount, wcnt=wcount))
    else:
        if member_id['daily'] == 1:
            return jsonify(render_template('gal_daily.html', sid=x_survey, cnt=count, fcnt=fcount, wcnt=wcount))
        else:
            if member_id['daily'] == 2:
                return jsonify(render_template('daily.html', sid=id, cnt=count, wcnt=wcount, hcnt=hcount, gcnt=gcount, acnt=acount))

#캘린더_갤럭시 사용자_영어
@app.route('/ajax3_en', methods=['GET', 'POST'])
def ajax3_en():
    data = request.get_json()
    x_survey = list(data.values())[0]
    member_id = members.find_one({'id': x_survey})

    count = member_id['submit_count']
    wcount = member_id['weekly_count']
    hcount = member_id['health_count']
    gcount = member_id['gyro_count']
    acount = member_id['acc_count']
    fcount = member_id['attach_count']
    cin_count = member_id["CIN_count"]

    if member_id['weekly_count'] > 0:
        return jsonify(render_template('weekly_en.html', sid=x_survey, cnt=count, fcnt=fcount, wcnt=wcount))
    else:
        if member_id['daily'] == 1:
            return jsonify(render_template('gal_daily_en.html', sid=x_survey, cnt=count, fcnt=fcount, wcnt=wcount))
        else:
            if member_id['daily'] == 2:
                return jsonify(render_template('daily.html', sid=id, cnt=count, wcnt=wcount, hcnt=hcount, gcnt=gcount, acnt=acount))

# 이전 파일 처리
@app.route('/justfile', methods=['POST'])
def justfile(): 
    data = request.files['data'] 
    st = data.read()
    l = st.decode()
    evl = eval(l)
    s_id = evl['sid']
    date = evl['dt']
    member_id = members.find_one({'id': s_id})

    reg_y = member_id["register_year"]
    reg_m = member_id["register_month"]
    reg_d = member_id["register_day"]
    cin_count = member_id["CIN_count"]
    cal_list = member_id["cal_list"]
    
    y, m, d = date.split('-')
    y = int(y); m = int(m); d = int(d)
    index = int(calIndexSearch(reg_m, reg_d, m, d))
    cal_list = member_id["cal_list"]

    if cal_list[index] == 0:

        if 'filed' in request.files:
            f = request.files['filed']
            print("file is", f)
            contents = f.read()
            fs = gridfs.GridFS(db, s_id)
            fname = f.filename
            members.update_one({'id': s_id}, {'$inc': {'attach_count': 1}})
            fs.put(contents, filename=fname, attachDate=date)

            # 파일이 있어야만 색깔이 바뀌도록
            cal_list[index] = 1
            members.update_one({'id': s_id}, { '$set': {'cal_list': cal_list}})
            md = { "date": date }
            survey_coll = mongo.db.get_collection(s_id)
            survey_coll.insert_one(md)
    else:
        flash("제출된 파일이 아니거나 제출이 가능한 날짜가 아닙니다.")
        
    return jsonify(render_template('cal_test.html', sid=s_id, cin=cin_count, cal=cal_list, reg_y=reg_y, reg_m=reg_m, reg_d=reg_d))

# 이전 파일 처리 eng
@app.route('/justfile_en', methods=['POST'])
def justfile_en(): 
    data = request.files['data'] 
    st = data.read()
    l = st.decode()
    evl = eval(l)
    s_id = evl['sid']
    date = evl['dt']
    member_id = members.find_one({'id': s_id})

    reg_y = member_id["register_year"]
    reg_m = member_id["register_month"]
    reg_d = member_id["register_day"]
    cin_count = member_id["CIN_count"]
    cal_list = member_id["cal_list"]
    
    y, m, d = date.split('-')
    y = int(y); m = int(m); d = int(d)
    index = int(calIndexSearch(reg_m, reg_d, m, d))
    cal_list = member_id["cal_list"]

    if cal_list[index] == 0:

        if 'filed' in request.files:
            f = request.files['filed']
            print("file is", f)
            contents = f.read()
            fs = gridfs.GridFS(db, s_id)
            fname = f.filename
            members.update_one({'id': s_id}, {'$inc': {'attach_count': 1}})
            fs.put(contents, filename=fname, attachDate=date)

            # 파일이 있어야만 색깔이 바뀌도록
            cal_list[index] = 1
            members.update_one({'id': s_id}, { '$set': {'cal_list': cal_list}})
            md = { "date": date }
            survey_coll = mongo.db.get_collection(s_id)
            survey_coll.insert_one(md)
    else:
        pass
        
    return jsonify(render_template('cal_test_en.html', sid=s_id, cin=cin_count, cal=cal_list, reg_y=reg_y, reg_m=reg_m, reg_d=reg_d))


#팝업창
@app.route('/pop.html', methods=['GET'])
def window_pop():
    return render_template("pop.html")

#팝업창_영어
@app.route('/pop_en.html', methods=['GET'])
def window_pop_en():
    return render_template("pop_en.html")

#세션 유지
@app.before_request
def make_session_permanent():
    session.permanent = True
    #10분 후 세션 만료
    app.permanent_session_lifetime = timedelta(minutes=1)

#백그라운드 실행
asia_seoul = datetime.datetime.fromtimestamp(time.time(), pytz.timezone('Asia/Seoul'))
today = asia_seoul.strftime("%Y%m%d")

def count(): # function for increasing weekly_count
    asia_seoul = datetime.datetime.fromtimestamp(time.time(), pytz.timezone('Asia/Seoul'))
    t = ['월요일', '화요일', '수요일', '목요일', '금요일', '토요일', '일요일']
    now = t[asia_seoul.today().weekday()]
    print(now)
    if now == '토요일':
        members.update_many({}, {'$inc': {'weekly_count': 1}}) #collection에 있는 모든 id에서 count가 1씩 증가

def countCIN(name, aeName, today): #모비우스 cnt 개수 가져오기
    cra = datetime.datetime.strptime(today, "%Y%m%d")
    cra = cra - timedelta(1)
    cra = '&cra=' + cra.strftime("%Y%m%d") + 'T150000'
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
        return None

def getCountDict(today): # Count number of container in Mobius Server
    dict_CIN = {}

    for i in range(0, 1000):
        aeName = str(i)

        if len(aeName) == 1:
            aeName = '00' + aeName
        elif len(aeName) == 2:
            aeName = '0' + aeName
        
        aeName = 'S' + aeName
        cnt = countCIN('IoT_1', aeName, today)

        if cnt == None:
            continue
        else:
            dict_CIN[aeName] = cnt
            
    for k,v in dict_CIN.items():
        k=str(k)
        v=int(v)
        member_id = members.find_one({'id': k})
        members.update_one({'id':k}, {'$set':{'CIN_count':v}})
        if member_id != None :
            cin_count = member_id["CIN_count"]
            print(cin_count)
            if cin_count < 143:
                members.update_one({'id': k}, {'$push': {'cal_list':0}})
                continue
            else:
                if cin_count >= 143:
                    members.update_one({'id': k}, {'$push': {'cal_list':1}})
                    continue
    return dict_CIN
    
if __name__ == '__main__':
    
    sched = BackgroundScheduler(daemon=True)
    asia_seoul = datetime.datetime.fromtimestamp(time.time(), pytz.timezone('Asia/Seoul'))
    today = asia_seoul.strftime("%Y%m%d")

    sched.add_job(count, 'cron', hour="00", minute="01", id="test_1") #토요일마다
    sched.add_job(getCountDict, 'cron', hour="00", minute="05", id="test_2", args=[today]) # 매일, 사용자에 대한 데이터 수 GET
    sched.start()

    app.run(host='0.0.0.0', port=2017)
