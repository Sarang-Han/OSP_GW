from flask import Flask, render_template, request, flash, redirect, url_for, session, jsonify
from database import DBhandler
import sys
import hashlib

application = Flask(__name__, static_url_path='/static', static_folder='static')
DB = DBhandler()
application.config["SECRET_KEY"] = "Oisobaki"

#메인화면
@application.route("/")
def hello():
    #return render_template("index.html")
    return redirect(url_for('view_list'))

#상품 등록하기
@application.route("/reg_items")
def reg_item():
    return render_template("reg_items.html")


from flask import session

@application.route("/submit_item_post", methods=['POST'])
def reg_item_submit_post():
    image_file = request.files["file"]
    image_file.save("static/images/{}".format(image_file.filename))
    data = request.form

    # 세션이 있는 경우 seller id를 가져오고, 없을 경우 빈 문자열로 설정
    seller_id = session.get('id', '')

    # seller_id를 폼 데이터에 추가
    data['seller'] = seller_id

    DB.insert_item(data['name'], data, image_file.filename)
    return render_template("submit_item_result.html",
                           data=data,
                           img_path="static/images/{}".format(image_file.filename))


#전체 상품보기
@application.route("/list")
def view_list():
    page = request.args.get("page", 0, type=int)
    per_page=6 # item count to display per page
    per_row=3# item count to display per row
    row_count=int(per_page/per_row)
    start_idx=per_page*page
    end_idx=per_page*(page+1)
    data = DB.get_items() #read the table
    item_counts = len(data)
    data = dict(list(data.items())[start_idx:end_idx])
    tot_count = len(data)
    for i in range(row_count):#last row
        if (i == row_count-1) and (tot_count%per_row != 0):
            locals()['data_{}'.format(i)] = dict(list(data.items())[i*per_row:])
        else: 
            locals()['data_{}'.format(i)] = dict(list(data.items())[i*per_row:(i+1)*per_row])
    return render_template(
    "list.html",
    datas=data.items(),
    row1=locals()['data_0'].items(),
    row2=locals()['data_1'].items(),
    limit=per_page,
    page=page,
    page_count=int((item_counts/per_page)+1),
    total=item_counts)

#상세 상품보기
@application.route("/view_detail/<name>/")
def view_item_detail(name):
    print("###name:", name)
    data = DB.get_item_byname(str(name))
    print("####data:", data)
    return render_template("detail.html", name=name, data=data)


#리뷰 등록하기
@application.route("/reg_review", methods=['POST']) 
def reg_review():
    image_file=request.files["file"]
    image_file.save("static/images/{}".format(image_file.filename))
    data=request.form
    DB.reg_review(data['name'], data, image_file.filename)
    return redirect(url_for('view_review'))

@application.route("/reg_review_init/<name>/") 
def reg_review_init(name):
    return render_template("reg_reviews.html", name=name)

#전체 리뷰보기
@application.route("/review")
def view_review():
    page = request.args.get("page", 0, type=int) 
    per_page=6 # item count to display per page 
    per_row=3 # item count to display per row 
    row_count=int(per_page/per_row) 
    start_idx=per_page*page 
    end_idx=per_page*(page+1)
    data = DB.get_reviews() #read the table 
    item_counts = len(data)
    data = dict(list(data.items())[start_idx:end_idx]) 
    tot_count = len(data)
    for i in range(row_count): #last row
        if (i == row_count-1) and (tot_count%per_row != 0): 
            locals()['data_{}'.format(i)] = dict(list(data.items())[i*per_row:])
        else:
            locals()['data_{}'.format(i)] = dict(list(data.items())[i*per_row:(i+1)*per_row])
    return render_template( 
        "review.html", 
        datas=data.items(), 
        row1=locals()['data_0'].items(), 
        row2=locals()['data_1'].items(), 
        limit=per_page,
        page=page,
        page_count=int((item_counts/per_page)+1),
        total=item_counts)

#상세 리뷰보기
@application.route("/view_review_detail/<name>/")
def view_review_detail(name):
    print("###name:", name)
    data = DB.get_review_byname(str(name))
    print("####data:", data)
    return render_template("view_review_detail.html", name=name, data=data)


#로그인 로그아웃 회원가입
@application.route("/login")
def login():
    return render_template("login.html")

@application.route("/login_confirm", methods=['POST'])
def login_user():
    id_=request.form['id']
    pw=request.form['pw']
    pw_hash = hashlib.sha256(pw.encode('utf-8')).hexdigest()
    if DB.find_user(id_,pw_hash):
        session['id']=id_
        return redirect(url_for('view_list'))
    else:
        flash("Wrong ID or PW!")
        return render_template("login.html")
    
@application.route("/logout")
def logout_user():
    session.clear()
    return redirect(url_for('view_list'))

@application.route("/signup")
def signup():
    return render_template("signup.html")

@application.route("/signup_post", methods=['POST'])
def register_user():
    data=request.form
    pw=request.form['pw']
    pw_hash = hashlib.sha256(pw.encode('utf-8')).hexdigest()
    if DB.insert_user(data,pw_hash):
        return render_template("/login.html")
    else:
        flash("user id already exist!")
        return render_template("/signup.html")

#좋아요 기능
@application.route('/show_heart/<name>/', methods=['GET'])
def show_heart(name):
    my_heart = DB.get_heart_byname(session['id'],name) 
    return jsonify({'my_heart': my_heart})

@application.route('/like/<name>/', methods=['POST']) 
def like(name):
    my_heart = DB.update_heart(session['id'],'Y', name) 
    return jsonify({'msg': '좋아요 완료!'})

@application.route('/unlike/<name>/', methods=['POST'])
def unlike(name):
    my_heart = DB.update_heart(session['id'],'N', name) 
    return jsonify({'msg': '좋아요 취소!'})

if __name__ == "__main__":
 application.run(host='0.0.0.0', debug=True)
