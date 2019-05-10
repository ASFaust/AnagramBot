
from AnagramGenerator import *
from Log import *
import time
import random
import json

#the database holds a dictionary of anagrams for names. {"name" : ["dict_for_anagram_1","dict_for_anagram_2","etc.",],}
#while it's in the ram, instead of the dict_for_anagram_1 strings, actual anagram objects are instantiated.

class AnagramDatabase:
    def __init__(self,filename):
        self.filename = filename
        self.log = Logger("logs/AnagramDatabase.log")
        self.db = {}
        try:
            dict_db = json.load(open(filename,"r"))
            for name in dict_db:
                anagrams = []
                for dict_anagram in dict_db[name]:
                    anagram = Anagram()
                    anagram.set_from_dict(dict_anagram)
                    anagrams.append(anagram)
                self.db[name] = anagrams
        except:
            self.log.put("no database to load")
    
    def pop_random(self):
        name = random.choice(list(self.db.keys()))
        anagram = random.choice(self.db[name]).get_text()
        return name,anagram
    
    def purge_empty_entries(self):
        new_db = {}
        for name in self.db:
            if(len(self.db[name]) > 0):
                new_db[name] = self.db[name]
        self.db = new_db

    def register_name(self,name):
        if not (name in self.db) and (len(name) < 100):
            self.db[name] = []
    
    def generate_anagrams(self,anagram_generator,max_time_seconds):
        start_time = time.time()
        for name in self.db:
            
            if(len(self.db[name]) > 0):
                continue
            self.log.put("generating anagrams for " + name)
            self.generate_anagrams_for_name(name)
            if (time.time() - start_time) > max_time_seconds:
                break
                
    def generate_anagrams_for_name(self,name,anagram_generator):
        anagram_generator.shuffle_dictionary()
        new_anagrams = anagram_generator.run(name)
        self.db[name] = self.get_high_quality_anagrams(new_anagrams)
            
    def save(self,filename):
        save_db = {}
        for name in self.db:
            anagrams = []
            for anagram in self.db[name]:
                anagrams.append(anagram.get_dict())
            save_db[name] = anagrams
        json_data = json.dumps(save_db)
        f = open(filename,"w")
        f.write(json_data)
        f.close()
        
    def get_high_quality_anagrams(self,anagram_list):
        ok_anagrams = []
        max_quality = 0
        for anagram in new_anagrams:
            quality = anagram.get_quality()
            if(quality > max_quality):
                max_quality = quality
        for anagram in new_anagrams:
            anagram_ok_flag = True
            if(anagram.get_quality() < max_quality):
                anagram_ok_flag = False
            else:
                for ok_anagram in ok_anagrams:
                    if(ok_anagram.same_as(anagram)):
                        anagram_ok_flag = False
                        break
                if(anagram_ok_flag):
                    ok_anagrams.append(anagram)
        return ok_anagrams

