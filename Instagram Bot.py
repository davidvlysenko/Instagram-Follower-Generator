#Import Libraries
from selenium import webdriver
from time import sleep
from time import time
from random import uniform
from random import choice
from random import randint
from datetime import datetime
import logins
import os
import inspect
import csv



#Create Bot
class Instabot:
    def __init__(self, hashtag, max_likes_htag, max_likes_total):

        #Initialize variables
        self.data_folder = str(os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))) #Import from same folder as python file
        self.links_record = [y for x in list(csv.reader(open(self.data_folder + "\\Links Record.csv", "rt", encoding = "utf-8"))) for y in x if x != []]
        self.hashtags_searched = []
        self.like_record = []
        self.dead_links = []
        self.counter = 0
        self.max_likes_htag = max_likes_htag
        self.max_likes_total = randint(round(0.67 * max_likes_total), max_likes_total)
        
        self.chromedriver = "\\chromedriver79.exe"
        self.instagram = "https://instagram.com"
        self.login = "//a[contains(text(), 'Log in')]"
        self.my_username = "//input[@name=\"username\"]"
        self.my_password = "//input[@name=\"password\"]"
        self.submit = '//button[@type="submit"]'
        self.notnow = "/html/body/div[4]/div/div/div[3]/button[2]"
        self.heartcolor = "//*[local-name() = 'svg']"
        self.heartbutton = "/html/body/div[1]/section/main/div/div/article/div[2]/section[1]/span[1]/button"
        self.photo_username = "/html/body/div[1]/section/main/div/div/article/header/div[2]/div[1]/div[1]/a"
        
        if hashtag == "rand":
            self.hashtags = [y for x in list(csv.reader(open(self.data_folder + "\\Hashtags.csv", "rt", encoding = "utf-8"))) for y in x]
            self.rand_hashtag = True
        else:
            self.hashtags = [hashtag]
            self.rand_hashtag = False

    

    #Open up Instagram in Chrome and log in
    def boot_instagram(self):

        #Bootup
        self.driver = webdriver.Chrome(executable_path = self.data_folder + self.chromedriver)

        #Open webpage
        self.driver.get(self.instagram)
        sleep(uniform(4.5, 5))

        #Two differt log-in screens depending on whether computer recognized
        try:
            #Click "Log in"
            self.driver.find_element_by_xpath(self.login).click()
            sleep(uniform(2.5, 3))
        except:
            pass

        #Enter login info
        self.driver.find_element_by_xpath(self.my_username).send_keys(logins.username)
        self.driver.find_element_by_xpath(self.my_password).send_keys(logins.pwd)
        self.driver.find_element_by_xpath(self.submit).click()
        sleep(uniform(4, 5))

        #Click out of pop-up
        self.driver.find_element_by_xpath(self.notnow).click()
        sleep(uniform(1.5, 2.5))

        self.start = time()
        

    #Go to hashtag and return links for all latest pictures with given hashtag
    def get_links(self, hashtag):
        
        links = []
        if self.rand_hashtag == True: 
            #Select a random number of most recent photos from the hashtag to like
            hashtag_likes = randint(round(0.67 * self.max_likes_htag), self.max_likes_htag)
        else:
            hashtag_likes = self.max_likes_total
        
        
        #Go to hashtag dashboard
        self.driver.get("https://www.instagram.com/explore/tags/%s/" %hashtag)
        sleep(uniform(2, 3))
        
        while len(links) < hashtag_likes:
            
            #Make sure that the links haven't been visited before in order to cut down on visiting liked photos
            #Must combine with old links links since you've scrolled 
            links = list(set([link for link in links + [a.get_attribute("href") for a in self.driver.find_elements_by_tag_name("a")]
                              if "/p/" in link and link not in self.links_record]))
            sleep(uniform(0.5, 1))
            
            #If there aren't enough unvisited photos in the first screeen, then scroll down until there are
            if len(links) < hashtag_likes:
                self.driver.execute_script("window.scrollTo(0,document.body.scrollHeight)")
                
        return links[:hashtag_likes]


    #Go to each photo link and like
    def like_photos(self, hashtag):
        
        #Get the first 33 links from the hashtag
        links_list = self.get_links(hashtag)
        self.hashtags_searched.append(hashtag)

        for link in links_list:
            if self.counter < self.max_likes_total:
                self.links_record.append(link)
                
                try:
                    self.driver.get(link)
                    sleep(uniform(0.1, 0.5))
                    
                    #Liked - rgb(237, 73, 86); Not liked - rgb(38, 38, 38)
                    #If not already liked (acts as a double check for links_record)
                    if self.driver.find_element_by_xpath(self.heartcolor).value_of_css_property("fill") == "rgb(38, 38, 38)":                    
                        
                        #Click heart to like photo
                        self.driver.find_element_by_xpath(self.heartbutton).click() 
                        
                        #Record usernme, hashtag, and datetime to track last interaction with user
                        self.like_record.append([self.driver.find_element_by_xpath(self.photo_username).get_attribute("href").split("/")[-2],
                                                 datetime.now().strftime("%m/%d/%Y"), hashtag])
                        self.counter += 1
                    
                    sleep(uniform(1, 2))
                       
                except:
                    self.dead_links.append([link])
                    continue
                
            else:
                break
            
               
    #Convert all hashtags into bytes, to be used for hashtags in foreign langauges        
    def rus_bytes(self, my_string):
        return str(list(my_string.encode()))[1:-1].replace("'", "")


    #Write information to CSV file
    def csv_writer(self, data, path, write_type):
        with open(path, write_type) as csv_file:
            writer = csv.writer(csv_file, delimiter=',')
            for line in data:
                writer.writerow(line)
        csv_file.close()


    #Put it all together and run until runtime finished
    def run_bot(self):
        self.boot_instagram()
        
        while self.counter < self.max_likes_total:
            self.like_photos(choice(self.hashtags))
            
        self.driver.quit()
        
        self.csv_writer(self.dead_links, self.data_folder + "\\Dead Links.csv", "wt")
        self.csv_writer([x[:-1] + [self.rus_bytes(x[-1])] for x in self.like_record], self.data_folder + "\\Like Record.csv", "a")
        self.csv_writer([[x] for x in self.links_record], self.data_folder + "\\Links Record.csv", "wt")
        
        print("Time Spent: %s" %round(time() - self.start), ", ", "Likes Given: %s" %self.counter, ", ",
              "Hashtags Searched: %s" %(' '.join([str(elem) for elem in self.hashtags_searched])))



#If searching through random hashtags in Hashtags.csv enter: "rand", number of likes per hashtag, number of likes total
#If seraching through specific hashtag, enter: hashtag, 0, number of likes total
my_bot = Instabot("rand", 5, 10)
my_bot.run_bot()
