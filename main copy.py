from playsound import playsound
from tkinter import *
import requests
import json
import webbrowser
from datetime import datetime
import config

# GLOBAL VARS
gAPP_TITLE = "TwitchCheckr v6.9.420.0001"
gCLIENTID = config.twitch_client_id
gCLIENT_SECRET = config.twitch_client_secret
gSOUND_ALERT = config.alert_sound
gFAVORITE_STREAMERS = config.favorite_streamers


def initial_setup():
	listOfStreamers = []
	
	if gFAVORITE_STREAMERS:
		listOfStreamers =  gFAVORITE_STREAMERS
		print("Favorite Streamers set to:")
		print(gFAVORITE_STREAMERS)
		
	def show_text():
		if entry_text.get() != "":

			listOfStreamers.append(entry_text.get())
		entry_text.set("")
		label_text.set(listOfStreamers)
	def runCheckr():
		for streamer in listOfStreamers:
			url = 'https://id.twitch.tv/oauth2/token'
			myobj = {'client_id': gCLIENTID, 'client_secret': gCLIENT_SECRET, 'grant_type': 'client_credentials'}
			x = requests.post(url, data=myobj)
			myobj = (x.json())
			myToken = "Bearer " + (myobj['access_token'])
			StreamerLive = (isStreamLive(streamer, myToken))
			if StreamerLive:
				if streamer not in isLive:
					print(streamer + " went live at " + datetime.now().strftime("%d/%m/%Y %H:%M:%S"))
					alert_popup(gAPP_TITLE, "{} is live!".format(streamer),
								"https://twitch.tv/{}".format(streamer),streamer)
					isLive.append(streamer)
			if not StreamerLive:
				if streamer in isLive:
					isLive.remove(streamer)
		root.after(5000, runCheckr)

	root = Tk()
	root.title(gAPP_TITLE)
	w = 400	 # popup window width
	h = 200	 # popup window height
	sw = root.winfo_screenwidth()
	sh = root.winfo_screenheight()
	x = (sw - w)/2
	y = (sh - h)/2
	root.geometry('%dx%d+%d+%d' % (w, h, x, y))
	entry_text = StringVar()
	entry = Entry(root, width=10, textvariable=entry_text)
	entry.config(state=NORMAL)
	entry.pack()

	button = Button(root, text="Add", command=show_text)
	button.pack()


	label_text = StringVar()
	label = Label(root, textvariable=label_text)
	label.pack()
	label_text.set(listOfStreamers)
	#runCheckr()
	root.after(5000,runCheckr())
	root.mainloop()

def alert_popup(title, message, path,streamer):
	playsound(gSOUND_ALERT)
	"""Generate a pop-up window for special messages."""
	root = Tk()
	root.title(title)
	w = 400	 # popup window width
	h = 200	 # popup window height
	sw = root.winfo_screenwidth()
	sh = root.winfo_screenheight()
	x = (sw - w)/2
	y = (sh - h)/2
	root.geometry('%dx%d+%d+%d' % (w, h, x, y))
	m = message
	m += '\n'
	m += path
	w = Label(root, text=m, width=120, height=5, font=(None,12))
	root.attributes('-topmost',True) #Make the window jump above all
	w.pack()
	
	#Close button
	c = Button(root, text="close", command=root.destroy, width=10)

	#Streamer button
	b = Label(root, text="Click to Watch " + streamer + " now", fg="blue", cursor="hand2", font=(None,20))
	b.pack()
	b.bind("<Button-1>", lambda e: clickHandlerStreamerName("https://twitch.tv/{}".format(streamer)))
	#b.grid(row=0,column=1)
	#c.grid(row=1,column=2)
	c.pack()
	# TextBox Creation

	mainloop()

def isStreamLive(streamer_name, myToken):

	headers = {
		'Client-ID': gCLIENTID,
		'authorization': myToken
	}

	params = (
		('user_login', streamer_name),
	)

	try:
		response = requests.get('https://api.twitch.tv/helix/streams', headers=headers, params=params)
		json_data = json.loads(response.text)
		json_data = json_data['data'][0]
		return True

	except:
		return False

def clickHandlerStreamerName(url):
		webbrowser.open_new(url)
isLive = []

streams = initial_setup()
