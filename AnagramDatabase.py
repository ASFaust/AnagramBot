
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
        self.nonzero_person_count = 0
        dict_db = []
        try:
            dict_db = json.load(open(filename,"r"))
        except:
            self.log.put("no database to load")
        for name in dict_db:
            anagrams = []
            if(len(dict_db[name]) > 0):
                self.nonzero_person_count += 1
            for dict_anagram in dict_db[name]:
                anagram = Anagram()
                anagram.set_from_dict(dict_anagram)
                anagrams.append(anagram)
            self.db[name] = anagrams
        
    
    def pop_random(self):
        non_empty_db = self.get_nonzero_entries()
        if(len(self.db) > 0):
            name = random.choice(list(non_empty_db.keys()))
            if(random.randint(1, 400) == 1):
                return name,"h"
            anagram_idx = random.randint(0,len(non_empty_db[name]) - 1)
            anagram = self.db[name].pop(anagram_idx).get_text()
            non_empty_db[name] = []
            self.nonzero_person_count -= 1
            return name,anagram
        else:
            return "lmao i don't have any","anagrams in my database"
    
    def get_nonzero_entries(self):
        ret = {}
        for name in self.db:
            if(len(self.db[name]) > 0):
                ret[name] = self.db[name]
        return ret

    def purge_empty_entries(self):
        self.db = self.get_nonzero_entries()

    def register_name(self,name):
        if not (name in self.db) and (len(name) < 100):
            self.db[name] = []
    
    def generate_anagrams(self,anagram_generator,max_time_seconds):
        start_time = time.time()
        if(self.nonzero_person_count < 50):
            self.log.put("generating anagrams. can only select from " + str(self.nonzero_person_count) + " persons rn")
            for name in self.db:
                if(len(self.db[name]) > 0):
                    continue
                try:
                    self.generate_anagrams_for_name(name,anagram_generator)
                except:
                    self.log.put("error at gen anagrams for name")
                if (time.time() - start_time) > max_time_seconds:
                    break
        else:
            self.log.put("enough anagrams, sleepy time")
            time.sleep(max_time_seconds)
                
    def generate_anagrams_for_name(self,name,anagram_generator):
        anagram_generator.shuffle_dictionary()
        new_anagrams = anagram_generator.run(name)
        hq_anagrams = self.get_high_quality_anagrams(new_anagrams)
        if(len(hq_anagrams) <= 0):
            self.log.put("didnt find any anagrams")
        else:
            self.db[name] = hq_anagrams
            self.nonzero_person_count += 1
            
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
        max_quality = 2 #just scrap anagrams consisting of short words completely
        for anagram in anagram_list:
            quality = anagram.get_quality()
            if(quality > max_quality):
                max_quality = quality
        for anagram in anagram_list:
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

