from AnagramDrawer import *
from AnagramGenerator import *
from FacebookPage import *
from Log import *
import time
import random
import json

class AnagramBot0009:
    def __init__(self,wait_post_time = 0):
        self.post_interval = 45 * 60 #post every 45 minutes
        self.last_post_time = time.time() + wait_post_time - self.post_interval - 1
        self.last_comment_time = 0
        self.last_person_pull_time = 0
        self.fb = FacebookPage()
        self.comment_db = {} 
        self.anagram_db = {}
        self.anagram_drawer = AnagramDrawer()
        self.anagram_generator = AnagramGenerator()
        self.log = Logger("logs/anagrambot0009.txt")
        
        try:
            self.anagram_db = json.load(open("anagram_database.json","r"))
        except:
            self.log.put("no anagram database")

        try:
            self.comment_db = json.load(open("comment_database.json","r"))
        except:
            self.log.put("no comment database")
        
    def main_loop(self):
        self.fb.get_most_recent_posts()
        while(True): 
            time.sleep(10)
            self.anagram_generator_job(min_person_pull_interval_seconds = 120)
            time.sleep(10)
            self.feed_post_job()
            time.sleep(10)
            #self.comment_post_job(min_comment_pause_seconds = 5)
    
    def feed_post_job(self):
        self.log.put("feed post job")
        now = time.time()
        if((now - self.last_post_time) >= self.post_interval):
            original,anagram = self.pop_random_anagram(max_search_time_seconds = 5)
            self.anagram_drawer.draw_image(original,anagram,"out.png")
            self.fb.post_image("out.png","HERE IS YOUR ANAGRAM")    
            self.last_post_time = now
            self.fb.get_most_recent_posts()
            
    #be careful not to post too often
    #only posting every 10 seconds
    def comment_post_job(self,min_comment_pause_seconds,max_time_seconds = 360):
        self.log.put("comment post job")
        all_comments = []
        start_time = time.time()
        for post in self.fb.recent_posts:
            all_comments = all_comments + post.get_comments(60) #every 60 seconds get new ones,else pass the ones you already recieved.
        random.shuffle(all_comments) #make equal chances
        for cmt in all_comments:
            if(time.time() - start_time) >= max_time_seconds:
                return
            if(not cmt.id in self.comment_db):
                user_name = cmt.user_name
                if(not user_name in self.anagram_db):
                    self.anagram_db[user_name] = [] #make empty entry that gets filled by anagram_generator_job
                else:
                    anagrams = self.anagram_db[user_name]
                    if(len(anagrams) > 0):
                        now = time.time()
                        if((now-self.last_comment_time) >= min_comment_pause_seconds):
                            anagram = anagrams[0]
                            self.anagram_db[user_name] = self.anagram_db[user_name][1:]
                            self.anagram_drawer.draw_image(user_name,anagram,"out.png")
                            cmt.comment_image("out.png","HERE IS YOUR ANAGRAM")
                            self.comment_db[cmt.id] = {"time" : now , "comment text" : cmt.text, "user_name" : user_name, "anagram" : anagram}
                            self.save_db(self.comment_db,"comment_database.json")
                            self.save_db(self.anagram_db,"anagram_database.json")
                                   #self.last_comment_time = now
                            time.sleep(5)
                            
    def anagram_generator_job(self,min_person_pull_interval_seconds = 120,max_time_seconds = 60):
        self.log.put("anagram_generator_job")
        now = time.time()
        if((now - self.last_person_pull_time) >= min_person_pull_interval_seconds):
            new_people = self.fb.get_people_from_likes()
            for person in new_people:
                if(not person in self.anagram_db):
                    self.anagram_db[person] = []
                    new_people_count += 1
        for person in self.anagram_db:
            if(len(self.anagram_db[person]) <= 0):
                self.log.put("next one")
                for i in range(0,2):
                    self.anagram_generator.shuffle_dict()
                    self.anagram_db[person] += self.anagram_generator.run(person)
                self.remove_duplicates(person)
                if(len(self.anagram_db[person]) == 0):
                    self.anagram_db[person] = ["Sorry, i cant find any Anagrams for you","Empty","Blyat, no anagrams!"]#
                self.save_db(self.anagram_db,"anagram_database.json")
                if(time.time() - now) > max_time_seconds:
                    return
        self.save_db(self.anagram_db,"anagram_database.json")
        #todo: add code that deletes entries from database that are empty now.
    
    def remove_duplicates(self,person):
        anagrams = []
        for anagram in self.anagram_db[person]:
            a_arr = anagram.split(" ")
            a_arr.sort()
            sorted_anagram = " ".join(a_arr)
            if not (sorted_anagram in anagrams):
                anagrams.append(sorted_anagram)
        for i in range(len(anagrams)):
            a_arr = anagrams[i].split(" ")
            random.shuffle(a_arr)
            anagrams[i] = " ".join(a_arr)
        self.anagram_db[person] = anagrams
    
    def save_db(self,db,filename):
        json_data = json.dumps(db)
        f = open(filename,"w")
        f.write(json_data)
        f.close()
    
    def pop_random_anagram(self,max_search_time_seconds = 5):
        start_time = time.time()
        if(len(self.anagram_db) <= 0):
            return "no persons in database","in database no persons"
        while(True):
            now = time.time()
            person = random.choice(list(self.anagram_db.keys()))
            anagrams = self.anagram_db[person]
            if(len(anagrams) > 0):
                anagram = anagrams[0]
                self.anagram_db[person] = self.anagram_db[person][1:]
                self.save_db(self.anagram_db,"anagram_database.json")
                return person,anagram
            else:
                if((now - start_time) > max_search_time_seconds):
                    return "i took too long to select an anagram","to select an anagram i took too long"
     
     
         
#print(fb.get_people_from_likes())

