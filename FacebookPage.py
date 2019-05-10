from Log import *
import requests
import json
import unicodedata
import time

class FacebookComment:
    def __init__(self,data,log):
        self.valid = True        
        self.data = data
        self.log = log
        try:
            self.id = self.data['id']
            self.user_name = str(unicodedata.normalize('NFKD', self.data['from']['name']).encode('ascii','ignore'))[2:-1]
            self.text = str(unicodedata.normalize('NFKD', self.data['message']).encode('ascii','ignore'))[2:-1]
            self.token = open("token","r").read()
        except:
            self.valid = False
        #self.log.put("init comment. user_name: " + self.user_name)
       
    def comment_image(self,path,text = ""):
        params = (
        ('message', text),
        ('access_token', self.token),
        )
        files = {'source':(path.split("/")[-1],open(path,"rb"),'image/png',{'Expires': '0'})}
        try:
            response = requests.post('https://graph.facebook.com/v3.2/'+self.id+ '/comments', params=params,files = files)
            time.sleep(5)
            if(str(response) != "<Response [200]>"):
                self.log.put(str(response) + ": " + response.text)
                return False
            self.log.put("posted nested image comment")
            return True
        except:
            return False
            
    def is_valid(self):
        return self.valid

class FacebookPost:
    def __init__(self,data,log):
        self.data = data 
        self.log = log
        self.id = self.data['id']
        self.comments = []
        self.last_request_time = 0
        self.token = open("token","r").read()
    
    #restrict the request frequency with min_request_pause_seconds
    def get_comments(self,min_request_pause_seconds = 0):
        now = time.time()
        if((now - self.last_request_time) < min_request_pause_seconds):
            return self.comments
        else:
            self.last_request_time = now
            ret = []
            self.log.put("getting comments to post " + self.id)
            params = (('access_token', self.token),)
            cmts = {}
            response_text = ""
            response = None
            try:
                response = requests.get('https://graph.facebook.com/v3.2/'+self.id+'/comments', params=params)
                time.sleep(5)
                response_text = response.text
                cmts = json.loads(response_text)
            except:
                self.log.put("couldn't get comments: response: " + str(response) + ", response_text: " + response_text)
                time.sleep(10)
                return ret
            for t2 in cmts['data']:
                fb_cmt = FacebookComment(t2,self.log)
                if(fb_cmt.is_valid()):
                    ret.append(fb_cmt)
            self.comments = ret
            return ret
           
    def comment_image(self,path,text = ""):
        params = (
        ('message', text),
        ('access_token', self.token),
        )
        files = {'source':(path.split("/")[-1],open(path,"rb"),'image/png',{'Expires': '0'})}
        try:
            response = requests.post('https://graph.facebook.com/v3.2/'+self.id+ '/comments', params=params,files = files)
            if(str(response) != "<Response [200]>"):
                self.log.put(str(response) + ": " + response.text)
                time.sleep(10)
                return False
            else:
                return True
        except:
            return False

class FacebookPage:
    def __init__(self):
        self.log = Logger("logs/Facebook.log")
        self.recent_posts_json = {}     
        self.recent_posts = []
        self.token = open("token","r").read()
   
    def get_most_recent_posts(self):
        self.log.put("start")
        ret = []
        params = (('access_token', self.token),)
        response = None
        try:
            response = requests.get('https://graph.facebook.com/v3.2/me/feed', params=params)
            time.sleep(5)
            if(str(response) != "<Response [200]>"):
                self.log.put(str(response) + ": " + response.text)
                return ret
        except:
            self.log.put("error at request get.")
            try:
                self.log.put(response.text)
            except:
                self.log.put("response is none")
            return ret
        self.recent_posts_json = json.loads(response.text)['data']
        ret = []
        for t1 in self.recent_posts_json:
            ret.append(FacebookPost(t1,self.log))
        self.recent_posts = ret
        #self.log.put("got recent posts")
        self.log.put("end")
        return ret 
            
    def get_people_from_likes(self):
        ret = []
        params = (('access_token', self.token),)
        self.log.put("this will take approximately " + str(1*len(self.recent_posts_json)) + " seconds")
        for t1 in self.recent_posts_json:
            response = 0
            try:
                response = requests.get('https://graph.facebook.com/v3.2/'+t1['id']+'/likes', params=params)
                time.sleep(1)
                if(str(response) != "<Response [200]>"):
                    self.log.put(str(response) + ": " + response.text)
                    time.sleep(10)
                    #return ret
            except:
                self.log.put("response is None")
                time.sleep(10)
                return ret
            t2 = []
            if(str(response) == "<Response [200]>"):
                t2 = json.loads(response.text)['data']
            for t3 in t2:
                try:
                    s1 = str(unicodedata.normalize('NFKD', t3['name']).encode('ascii','ignore'))[2:-1]
                    if(len(s1) > 0):
                        ret.append(s1)
                except:
                    continue
        return ret
            
    def post_image(self,path,text):
        params = (
            ('message', text),
            ('access_token', self.token),
            )
        files = {'source':(path.split("/")[-1],open(path,"rb"),'image/png',{'Expires': '0'})}
        try:
            response = requests.post('https://graph.facebook.com/v3.2/me/photos', params = params,files = files)
            time.sleep(10)
            if(str(response) != "<Response [200]>"):
                self.log.put(str(response) + ": " + response.text)
                return False
        except:
            return False
        return True
      
