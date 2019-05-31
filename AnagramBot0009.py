from AnagramDrawer import *
from AnagramDatabase import *
from AnagramGenerator import *
from FacebookPage import *
from Log import *
import time
import random
import json

class AnagramBot0009:
    def __init__(self,wait_post_time = 0):
        self.log = Logger("logs/AnagramBot0009.log")
        self.log.put("start")
        self.post_interval = 30 * 60 #post every 45 minutes
        self.last_post_time = time.time() + wait_post_time - self.post_interval - 1
        self.last_person_pull_time = 0
        self.fb = FacebookPage()
        self.anagram_db = AnagramDatabase("anagram_database.json")
        self.anagram_drawer = AnagramDrawer()
        self.anagram_generator = AnagramGenerator()
        self.log.put("init finished")
        
    def main_loop(self):
        while(True):             
            self.anagram_generator_job()
            self.feed_post_job()

    def feed_post_job(self):
        self.log.put("feed post job")
        now = time.time()
        if((now - self.last_post_time) >= self.post_interval):
            try:
                original,anagram = self.anagram_db.pop_random()
            except:
                self.log.put("anagram db error")
            try:
                self.anagram_drawer.draw_image(original,anagram,"out.png")
            except:
                self.log.put("anagram drawer exception")
            try:
                self.fb.post_image("out.png","HERE IS YOUR ANAGRAM")    
            except:
                self.log.put("fb post image error")
            self.last_post_time = now
            self.log.put("posted: Original: " + original + " , Anagram: " + anagram)
            
    def anagram_generator_job(self,min_person_pull_interval_seconds = 300, max_time_seconds = 120):
        self.log.put("anagram generator job")
        now = time.time()
        if((now - self.last_person_pull_time) >= min_person_pull_interval_seconds):
            self.log.put("pulling persons from facebook")
            self.anagram_db.purge_empty_entries() #remove old unanagramized entries
            self.fb.get_most_recent_posts()
            new_people = self.fb.get_people_from_likes()
            for person_name in new_people:
                self.anagram_db.register_name(person_name)
            self.last_person_pull_time = now
        self.anagram_db.generate_anagrams(self.anagram_generator,max_time_seconds)
        self.anagram_db.save("anagram_database.json")                    

