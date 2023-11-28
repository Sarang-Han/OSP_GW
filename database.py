import pyrebase
import json

class DBhandler:
    def __init__(self ):
        with open('./authentication/firebase_auth.json') as f:
            config=json.load(f )
        firebase = pyrebase.initialize_app(config)
        self.db = firebase.database()
    
    def insert_item(self, name, data, img_path):
        item_info ={
            "seller": data['seller'],
            "addr": data['addr'],
            "email": data['email'],
            "category": data['category'],
            "card": data['card'],
            "status": data['status'],
            "phone": data['phone'],
            "img_path": img_path
}
        self.db.child("item").child(name).set(item_info)
        print(data, img_path)
        return True
    
    def insert_user(self, data, pw):
        if 'nickname' in data:
            user_info = {
                "id": data['id'],
                "pw": pw,
                "nickname": data['nickname']
            }
            if self.user_duplicate_check(str(data['id'])):
                self.db.child("user").push(user_info)
                print(data)
                return True
            else:
                return False
        else:
            print("Nickname is missing in user data.")
            return False


    def user_duplicate_check(self, id_string):
        users = self.db.child("user").get()
        
        print("users###",users.val())
        if str(users.val()) == "None": # first registration
            return True
        else:
            for res in users.each():
                value = res.val()
                if value['id'] == id_string:
                    return False
            return True
        
    def find_user(self, id_, pw_):
        users = self.db.child("user").get()
        target_value=[]
        for res in users.each():
            value = res.val()
            
            if value['id'] == id_ and value['pw'] == pw_:
                return True
        return False
    
    def get_items(self ):
        items = self.db.child("item").get().val()
        return items
    
    def get_item_byname(self, name):
        items = self.db.child("item").get()
        target_value=""
        print("###########",name)
        for res in items.each():
            key_value = res.key()
            
            if key_value == name:
                target_value=res.val()
        return target_value
    
    def reg_review(self, name, data, img_path):
        review_info ={
            "rate": data['reviewStar'],
            "review": data['reviewContents'],
            "title": data['title'],
            "img_path": img_path
        }
        self.db.child("review").child(data['name']).set(review_info)
        return True
    
    def get_reviews(self):
        reviews = self.db.child("review").get().val() 
        return reviews
    
    def get_review_byname(self, name):
        reviews = self.db.child("review").get()
        target_value=""
        print("###########",name)
        for res in reviews.each():
            key_value = res.key()
            
            if key_value == name:
                target_value=res.val()
        return target_value
    
    def get_heart_byname(self, uid, name):
        hearts = self.db.child("heart").child(uid).get() 
        target_value=""
        if hearts.val() == None:
            return target_value
        for res in hearts.each(): key_value = res.key()
        if key_value == name: target_value=res.val()
        return target_value
    
    def update_heart(self, uid, isHeart, item): 
        heart_info ={
            "interested": isHeart
        }
        self.db.child("heart").child(uid).child(item).set(heart_info)
        return True
    
    # 여기에 db에 채팅 전송하는 함수 작성
    # 여기에 db에서 채팅 불러와 화면에 띄우는 함수 작성
    def insert_chat_message(self, name, message, timestamp):
        chat_info = {
            "name": name,
            "message": message,
            "timestamp": timestamp
        }
        self.db.child("chat").push(chat_info)
        return True

    # 채팅 메시지 불러오기
    def get_chat_messages(self):
        chat_messages = self.db.child("chat").get().val()
        return chat_messages