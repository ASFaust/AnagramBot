from Log import *
import requests
import json
import unicodedata
import time

class FacebookComment:
    def __init__(self,data,log):
        self.data = data
        self.log = log
        self.id = self.data['id']
        self.user_name = str(unicodedata.normalize('NFKD', self.data['from']['name']).encode('ascii','ignore'))[2:-1]
        self.text = str(unicodedata.normalize('NFKD', self.data['message']).encode('ascii','ignore'))[2:-1]
        self.token = open("token","r").read()
        #self.log.put("init comment. user_name: " + self.user_name)
       
    def comment_image(self,path,text = ""):
        params = (
        ('message', text),
        ('access_token', self.token),
        )
        files = {'source':(path.split("/")[-1],open(path,"rb"),'image/png',{'Expires': '0'})}
        try:
            response = requests.post('https://graph.facebook.com/v3.2/'+self.id+ '/comments', params=params,files = files)
            self.log.put("posted nested image comment")
            return response
        except:
            return 0

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
            cmts = json.loads(requests.get('https://graph.facebook.com/v3.2/'+self.id+'/comments', params=params).text)
            for t2 in cmts['data']:
                ret.append(FacebookComment(t2,self.log))
            self.comments = ret
            return ret
           
    def comment_image(self,path,text = ""):
        params = (
        ('message', text),
        ('access_token', self.token),
        )
        files = {'source':(path.split("/")[-1],open(path,"rb"),'image/png',{'Expires': '0'})}
        response = requests.post('https://graph.facebook.com/v3.2/'+self.id+ '/comments', params=params,files = files)
        return response

class FacebookPage:
    def __init__(self):
        self.log = Logger("logs/facebook_log.txt")
        self.recent_posts_json = {}     
        self.recent_posts = []
        self.token = open("token","r").read()
   
    def get_most_recent_posts(self):
        ret = []
        params = (('access_token', self.token),)
        try:
            response = requests.get('https://graph.facebook.com/v3.2/me/feed', params=params)
        except:
            return ret
        self.recent_posts_json = json.loads(response.text)['data']
        ret = []
        for t1 in self.recent_posts_json:
            ret.append(FacebookPost(t1,self.log))
        self.recent_posts = ret
        #self.log.put("got recent posts")
        return ret 
            
    def get_people_from_likes(self):
        ret = []
        params = (('access_token', self.token),)
        for t1 in self.recent_posts_json:
            likes = 0
            try:
                likes = requests.get('https://graph.facebook.com/v3.2/'+t1['id']+'/likes', params=params)
            except:
                return
            t2 = json.loads(likes.text)['data']
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
        except:
            return 0
        self.log.put(response.text)
        return response
      
