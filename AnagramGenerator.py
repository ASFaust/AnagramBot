import time
import numpy as np
import random
import hashlib
import json

class Word:
    word_init_counter = 0  
    def __init__(self):
        self.repr = 0
        self.arr = 0
        self.hash_value = 0

    def init_from_dict(self,data):
        self.repr = data["repr"]
        self.arr = np.array(data["arr"],dtype = np.int16)
        self.hash_value = data["hash"]
        Word.word_init_counter = max(int(data["hash"]) + 1,Word.word_init_counter)

    def get_dict(self):
        ret = {}
        ret["repr"] = self.repr
        ret["arr"] = self.arr.tolist()
        ret["hash"] = self.hash_value
        return ret

    def init_gen(self,txt,quality):
        self.repr = [{"text" : txt,"quality" : quality}]
        self.arr = np.zeros(26,dtype = np.int16)
        offset = ord('a')
        for c in self.only_text(txt):
            self.arr[ord(c) - offset] += 1
        self.hash_value = "{:05d}".format(Word.word_init_counter)
        Word.word_init_counter += 1

    def only_text(self,text):
        ret = ""
        allowed = range(ord('a'),ord('z')+1)
        for x in text.lower():
            if ord(x) in allowed:
                ret = ret + x
        return ret  

    def same_as(self,other):
        if(self.arr == other.arr).all():
            other.repr = other.repr + self.repr
            return True
        return False
    
    def get_repr(self):
        max_q = -10000;
        ret = ""
        random.shuffle(self.repr)
        for t in self.repr:
            if(t["quality"] > max_q):
                max_q = t["quality"]
                ret = t["text"]
        return ret
        
    def get_quality(self):
        max_q = -10000;
        for t in self.repr:
            if(t["quality"] > max_q):
                max_q = t["quality"]
        return max_q
        
    def is_subword(self,of):
        return (self.arr <= of.arr).all()
        
class Dictionary:
    def __init__(self):
        self.words = []
        self.fav_words = []
        self.normal_words = []
        
    def load_normal_words_from_json(self,filename):
        db = json.load(open(filename,"r"))
        for word_name in db:
            word = Word()
            word.init_from_dict(db[word_name])
            self.normal_words.append(word)
        self.shuffle_words()
        
    def load_fav_words_from_text(self,filename):
        #"dict/favorites.txt"
        fav = open(filename,"r").read().split("\n")
        for f in fav:
            if(len(f)) < 2:
                continue
            word = Word()
            word.init_gen(f,10)
            self.fav_words.append(word)
        self.shuffle_words()
                    
    def shuffle_words(self):
        random.shuffle(self.fav_words)
        random.shuffle(self.normal_words)
        self.words = self.fav_words + self.normal_words
    
    def gen_normal_from_text_files(self,filename):
        self.words = []
        print("loading normal")
        normal = open("dict/dict.txt","r").read().split("\n")
        for f in normal:
            if(len(f)) < 2:
                continue
            w = Word()
            w.init_gen(f,5)
            self.append_normal_word(w)
            print(f)
        print("loading short")
        short = open("dict/smallwords.txt","r").read().split("\n")
        for f in short:
            if(len(f)) < 2:
                continue
            w = Word()
            w.init_gen(f,1)
            self.fav_words.append(word)
        db = {}
        for word in self.normal_words:
            db[word.hash_value] = {"repr" : word.repr, "arr" : word.arr.tolist(), "hash" : word.hash_value}
        json_data = json.dumps(db)
        f = open(filename,"w")
        f.write(json_data)
        f.close()
        
    def append_normal_word(self,word):
        for w in self.normal_words:
            if(word.same_as(w)):
                return
        self.normal_words.append(word)
        
class Anagram:
    def __init__(self):
        self.new_word = None
        self.arr = None
        self.path = None
        self.words = None
        
    def get_dict(self):
        #only needs self.words and self.path saved
        ret = {}
        ret["path"] = self.path
        word_dict_arr = []
        for word in self.words:
            word_dict_arr.append(word.get_dict())
        ret["words"] = word_dict_arr
        return ret
        
    def set_from_dict(self,anagram_dict):
        self.path = anagram_dict["path"]
        for word_dict in anagram_dict["words"]:
            word = Word()
            word.init_from_dict(word_dict)
            self.words.append(word)
        
    def create(self,new_word,old_anagram):
        self.new_word = new_word
        if(old_anagram is None):
            self.words = [new_word]
            self.arr = new_word.arr
        else:
            self.words = old_anagram.words + [new_word]
            self.arr = old_anagram.arr + new_word.arr
        path_arr = []
        for word in self.words:
            path_arr.append(word.hash_value)
        path_arr.sort()
        self.path = "".join(path_arr)
        
    def get_quality(self):
        ret = 0
        for word in self.words:
            word_quality = word.get_quality()
            if(word_quality > ret):
                ret = word_quality
        return ret

    def get_text(self):
        ret = " "
        random.shuffle(self.words)
        for word in self.words:
            text = word.get_repr()
            text = text[0].upper() + text[1:]
            if(ret == " "):
                ret = text
            else:
                ret = ret + " " + text
        return ret

    def same_as(self,other):
        return (self.path == other.path)

class AnagramGenerator:
    def __init__(self):
        self.dict = Dictionary()
        self.dict.load_normal_words_from_json("dict.json")
        self.dict.load_fav_words_from_text("dict/favorites.txt")
        self.paths = []
        self.ret = []
        self.max_time = 10
        self.start_time = 0
        self.max_results = 200
        self.breaking = False
        
    def run(self,text):
        self.paths = []
        self.ret = []
        self.breaking = False
        whole_word = Word()
        whole_word.init_gen(text,100)
        self.start_time = time.time()
        self.get_anagram(self.dict.words,whole_word,None)
        return self.ret
        
    def shuffle_dictionary(self):
        self.dict.shuffle_words()
    
    def get_anagram(self,current_dict,remaining_word,anagram):
        if((time.time() - self.start_time) >= self.max_time) or self.breaking:
            return

        new_dict = []
        remaining_words = []
        for word in current_dict:
            if(word.is_subword(remaining_word)):
                new_dict.append(word)
                new_anagram = Anagram()
                new_anagram.create(word,anagram)
                if not (new_anagram.path in self.paths):                    
                    self.paths.append(new_anagram.path)
                    new_remainig_word = Word()
                    new_remainig_word.arr = remaining_word.arr - word.arr
                    if(not new_remainig_word.arr.any()):
                        self.ret.append(new_anagram)
                        if(len(self.ret) >= self.max_results):
                            self.breaking = True
                            return
                    else:
                        self.get_anagram(new_dict,new_remainig_word,new_anagram)

