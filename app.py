from dotenv import load_dotenv
import os
import time
import helper

STARTING_WEEK = 6
STARTING_DATE_TS = 1757264400

current_time = time.time()
# calculate current week
current_week = int((current_time - STARTING_DATE_TS) // 604800) + STARTING_WEEK
print("current week:", current_week)

load_dotenv()
usr = os.getenv("USERNAME")
passwd = os.getenv("PASSWORD")

helper.pull_data(usr, passwd)
