from PIL import Image, ImageDraw, ImageFont
import random
import json

aa_factor = 3
edge_padding = 30
y_space = 250      
        
class AnagramDrawer:
    def __init__(self,font_json_path = "font/font.json"):
        self.aa_factor = aa_factor
        self.edge_padding = edge_padding * aa_factor
        self.y_space = y_space * aa_factor
        self.arrow_y_padding = 0
        self.arrow_width = 0
        self.offset = (0,0)
        self.textSizeImage = Image.new('RGB',(1,1),(255,255,255))
        self.fonts = json.load(open(font_json_path,'r'))
        self.load_fonts()
        self.current_font = 0
        self.case = "camel"
        
    def load_fonts(self):
        for f in self.fonts:
            sc = self.fonts[f]["scale"] * self.aa_factor
            self.fonts[f]["font"] = ImageFont.truetype('font/' + f,sc)
    
    def textSize(self,txt):
        d = ImageDraw.Draw(self.textSizeImage)
        ret = d.textsize(txt,font=self.current_font)
        return ret
    
    def drawArrow(self,drawer,pos1,pos2):
        drawer.line([pos1, pos2], fill=(0,0,0), width=self.arrow_width)
    
    def draw_sorted(self,txt1,txt2,drawer):
        for t1 in txt1:
            if(t1[0] == " "): 
                continue
            min_dist = 1000000.0
            sel = 0
            for t2 in txt2:
                if((t1[0] == t2[0]) and (t2[2] == False)):
                    dist = t1[1][0] - t2[1][0]
                    if(dist < 0):
                        dist = -dist
                    if(dist < min_dist):
                        sel = t2
                        min_dist = dist
            try:
                self.drawArrow(drawer,t1[1],sel[1])
                sel[2] = True
            except:
                continue
                
    def draw_unsorted(self,txt1,txt2,drawer):
        for t1 in txt1:
            if(t1[0] == " "): 
                continue
            for t2 in txt2:
                if((t1[0] == t2[0]) and (t2[2] == False)):
                    self.drawArrow(drawer,t1[1],t2[1])
                    t2[2] = True
                    break

    def remove_all_but(self,text,ok_chars):
        ret = ""
        for c in text:
            if(c in ok_chars):
                ret += c
        return ret
                
    def set_font_from_keywords(self,str1,str2):
        sel_font = "mono_01.ttf"
        for f in self.fonts:
            compstr = str(str1 + " " + str2).lower()
            compstr = self.remove_all_but(compstr,"abcdefghijklmnopqrstuvwxyz ")
            if(not set(self.fonts[f]["keywords"]).isdisjoint(compstr.split(" "))):
                sel_font = f
                break
        self.case = self.fonts[sel_font]["case"]
        self.arrow_y_padding = self.fonts[sel_font]["arrow_y_padding"] * self.aa_factor
        self.arrow_width = self.fonts[sel_font]["arrow_width"] * self.aa_factor
        self.offset =  self.fonts[sel_font]["offset"]
        self.offset[0] *= self.aa_factor
        self.offset[1] *= self.aa_factor
        self.current_font = self.fonts[sel_font]["font"]

    def adjust_case(self,text):
        ret = "" 
        str_arr = text.split(" ")
        for word in str_arr:
            ret += " "
            if(self.case == "camel"):
                ret += word[0].upper() + word[1:]
            if(self.case == "upper"):
                ret += word.upper()
            if(self.case == "lower"):
                ret += word.lower()
        return ret[1:]

    #takes two strings and makes an anagram picture from them
    def draw_image(self,str1,str2,filename):
        self.set_font_from_keywords(str1,str2)
        str1 = self.adjust_case(str1)
        str2 = self.adjust_case(str2)
        ts1 = self.textSize(str1)
        ts2 = self.textSize(str2)
        imgSize = (max(ts1[0],ts2[0]) + self.edge_padding * 2,ts2[1] + self.y_space + self.edge_padding * 2)
        image = Image.new('RGB',imgSize,(255,255,255))
        drawer = ImageDraw.Draw(image)
        drawer.text((self.edge_padding + self.offset[0],self.edge_padding + self.offset[1]), str1, font=self.current_font, fill=(0,0,0))
        drawer.text((self.edge_padding + self.offset[0],self.edge_padding + self.offset[1] + self.y_space), str2, font=self.current_font, fill=(0,0,0))
        
        #generating start and end points of the arrows alongside a flag and their chars
        txt1 = []
        for i in range(len(str1)):
            c = str1[i]
            s1 = self.textSize(str1[:i])
            s2 = self.textSize(str1[:i+1])
            x_position = self.edge_padding + s1[0] + (s2[0] - s1[0]) / 2 
            y_position = s2[1] + self.arrow_y_padding + self.edge_padding
            txt1.append([c.lower(),(x_position,y_position)])
        
        txt2 = []
        for i in range(len(str2)):
            c = str2[i]
            s1 = self.textSize(str2[:i])
            s2 = self.textSize(str2[:i+1])
            x_position = self.edge_padding + s1[0] + (s2[0] - s1[0]) / 2 
            y_position = self.edge_padding + self.y_space - self.arrow_y_padding
            txt2.append([c.lower(),(x_position,y_position),False])
    
        #decide wether to untangle or not
        
        if("".join(sorted(str1.split(" "))) == "".join(sorted(str2.split(" ")))):
            #add nice randomness
            random.shuffle(txt2)
            #searching for matching chars and drawing the arrows
            self.draw_unsorted(txt1,txt2,drawer)
        else:
            self.draw_sorted(txt1,txt2,drawer)
        
        image = image.resize((int(image.width/aa_factor), int(image.height/aa_factor)), Image.ANTIALIAS)
        image.save(filename)

#drawImage("Dave Cantautore","Nature Advocate","out.jpg")
#drawImage("Put Are Labs Menus","Lester Baun Mupas","out.jpg")


