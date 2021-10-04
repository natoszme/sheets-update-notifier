import requests
from bs4 import BeautifulSoup as BS
import pandas as pd
from IPython.display import display_html
import math
import threading
import smtplib
from datetime import datetime

def last_saved_grade():
	f = open("last_grade.txt", "r")
	grade = f.read()
	return int(grade) if grade else 0

def last_updated_grade():
	URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSyNWDTH0_RrnMRjKwuN5XTewYI_SzHmGS_IKUBx4TRfkJlnZUD_CbQv4a7fEvisgcx0GGVVC3BeMKR/pubhtml?gid=1278203653&single=true"

	response = requests.get(url = URL)

	soupResponse = BS(response.content, features="lxml")
	htmlBody = soupResponse.body
	viewport = htmlBody.find('div',attrs={'id' : "sheets-viewport"})

	table = str(viewport.next_element.next_element.next_element)

	df = pd.read_html(table)[0]
	columns = [2, 18]

	df1 = df.iloc[:, columns]
	df1.columns = ["last_name", "grade"]
	my_row = df1.loc[df1['last_name'] == "SZMEDRA"]
	grade = my_row.iloc[0]["grade"]

	print("retrieved grade:", grade)

	# use pandas.isnull() since math.isnan breaks with real strings
	return int(grade)

def update_grade(new_grade):
	print("about to update grade", new_grade)
	f = open("last_grade.txt", "w")
	f.write(str(new_grade))

def notify_update(grade):
	SERVER = "smtp.live.com"
	PORT = 587
	FROM = "nato_sz7@hotmail.com"
	TO = ["natoszmedra@gmail.com"] # must be a list

	SUBJECT = "[IASC] Exam grade updated"
	message = """Hola, Nato!

	Tu nota del parcial de IASC es """ + str(grade)

	server = smtplib.SMTP(SERVER, PORT)
	server.connect(SERVER, PORT)
	server.ehlo()
	server.starttls()
	server.ehlo()
	print("about to send mail!", message)
	#server.login(mail, password)
	server.sendmail(FROM, TO, message)
	server.quit()

def notify_grade_update():
	saved = last_saved_grade()
	updated = last_updated_grade()

	print("new:", updated)
	print("old:", saved)

	if (saved != updated):
		update_grade(updated)
		notify_update(updated)
	else:
		print("no news yet")

def cron_task():
	threading.Timer(60, cron_task).start()
	print("\n\n\nRunning script at", datetime.now())
	notify_grade_update()
	print("Finished running script at", datetime.now())

cron_task()