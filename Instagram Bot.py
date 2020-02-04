#Import Libraries
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from time import sleep
from time import time
from random import uniform
from random import sample
from random import randint
import logins
import os
import inspect
import csv
import datetime
import pytz



#Create Bot
class Instabot:
    def __init__(self, timezone, runtime):

        #Initialize variables
        self.data_folder = str(os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))) #Import from same folder as python file
        self.hashtags = [y for x in list(csv.reader(open(self.data_folder + "\\Hashtags.csv","rt",encoding = "utf-8"))) for y in x]
        self.links_visited = []
        self.dead_links = []
        self.counter = 0
        self.timezone = timezone
        self.runtime = runtime


    #Open up Instagram in Chrome and log in
    def boot_instagram(self):

        #Bootup
        self.driver = webdriver.Chrome(executable_path = self.data_folder + "\\chromedriver79.exe")

        #Open webpage
        self.driver.get("https://instagram.com")
        sleep(uniform(4.5, 5))

        #Click "Log in"
        self.driver.find_element_by_xpath("//a[contains(text(), 'Log in')]").click()
        sleep(uniform(2.5, 3))

        #Enter login info
        self.driver.find_element_by_xpath("//input[@name=\"username\"]").send_keys(logins.username)
        self.driver.find_element_by_xpath("//input[@name=\"password\"]").send_keys(logins.pwd)
        self.driver.find_element_by_xpath('//button[@type="submit"]').click()
        sleep(uniform(2.5, 3))

        #Click out of pop-up
        self.driver.find_element_by_xpath("//button[contains(text(), 'Not Now')]").click()
        sleep(uniform(1.5, 2.5))

        self.start = time()


    #Go to hashtag and return links for all latest pictures with given hashtag
    def get_links(self, hashtag):
        self.driver.get("https://www.instagram.com/explore/tags/%s/" %hashtag)
        sleep(uniform(0.1, 0.5))
        links = [link for link in [a.get_attribute("href") for a in self.driver.find_elements_by_tag_name("a")] if "/p/" in link and link not in self.links_visited][:randint(25,32)]
        return links


    #Go to each photo link and like
    #If photo not found, skip
    def like_photos(self, links_list):
        self.links_visited += links_list
        
        for link in links_list:
            try:
                self.driver.get(link)
                sleep(uniform(0.1, 0.5))

                #Click heart to like photo
                self.driver.find_element_by_xpath("/html/body/div[1]/section/main/div/div/article/div[2]/section[1]/span[1]/button").click() 
                sleep(uniform(1, 2))
                
                self.counter += 1
                
            except:
                self.dead_links.append(link)
                continue


    #Pick batch of random hashtags from hashtag list and go through them one by one
    #Dividing into batches and liking seperately with a delay between them to prevent Instagram from shutting down account because of suspicious activity
    def get_hashtags(self):      
        for hashtag in sample(self.hashtags, randint(5, 8)):
            self.hashtags_searched.append(hashtag)
            self.like_photos(self.get_links(hashtag))


    #Current time in given timezone
    def current_time(self, timezone):
        return datetime.datetime.now(pytz.timezone(timezone)).strftime("%H:%M:%S")


    #Calculate time with delta in seconds for given timezone
    def future_time(self, delta, timezone):
        return (datetime.datetime.now(pytz.timezone(timezone)) + datetime.timedelta(seconds=delta)).strftime("%H:%M:%S")


    #Print status updates
    def print_info(self, pause):
        print("Time Spent: %s" %round(time() - self.start), ", ", "Likes Given: %s" %self.counter, ", ",
              "Hashtags Searched: %s" %(' '.join([str(elem) for elem in self.hashtags_searched])))
        
        if pause > 0:
            print("Current Time: %s" %self.current_time(self.timezone), ", ", "Restart Program: %s" %self.future_time(pause, self.timezone))
            sleep(pause)
            

    #Write information to CSV file
    def csv_writer(self, data, path):
        with open(path,"wt") as csv_file:
            writer = csv.writer(csv_file, delimiter=',')
            for line in data:
                writer.writerow(line)
        csv_file.close()


    #Put it all together and run until runtime finished
    def run_bot(self):
        self.boot_instagram()
        
        while time() - self.start < self.runtime:
            self.hashtags_searched = []
            self.get_hashtags()
            self.print_info(uniform(2000, 4000))

        self.print_info(0)
        self.driver.quit()
        self.csv_writer(self.dead_links, self.data_folder + "\\Dead Links.csv")



my_bot = Instabot("US/Eastern", 86400)
my_bot.run_bot()
