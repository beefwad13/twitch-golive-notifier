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
already_live = []

def initial_setup():
	arr_streamers = []
	
	if gFAVORITE_STREAMERS:
		arr_streamers =  gFAVORITE_STREAMERS
		print("Favorite Streamers set to:")
		print(gFAVORITE_STREAMERS)
		
	def show_text():
		if txt_add_streamer_value.get() != "":

			arr_streamers.append(txt_add_streamer_value.get())
		txt_add_streamer_value.set("")
		lbl_streamer_names_value.set(arr_streamers)

	def runCheckr():
		for streamer in arr_streamers:
			url = 'https://id.twitch.tv/oauth2/token'
			myobj = {'client_id': gCLIENTID, 'client_secret': gCLIENT_SECRET, 'grant_type': 'client_credentials'}
			x = requests.post(url, data=myobj)
			myobj = (x.json())
			auth_token = "Bearer " + (myobj['access_token'])
			is_live_check = (is_streamer_live(streamer, auth_token))
			if is_live_check:
				if streamer not in already_live:
					print(streamer + " went live at " + datetime.now().strftime("%d/%m/%Y %H:%M:%S"))
					alert_popup(gAPP_TITLE, "{} is live!".format(streamer),
								"https://twitch.tv/{}".format(streamer),streamer)
					already_live.append(streamer)
			if not is_live_check:
				if streamer in already_live:
					already_live.remove(streamer)
		win_main.after(5000, runCheckr)

	win_main = Tk()
	win_main.title(gAPP_TITLE)
	w = 400 # width
	h = 200 # height
	x = (win_main.winfo_screenwidth() - w)/2
	y = (win_main.winfo_screenheight() - h)/2
	win_main.geometry('%dx%d+%d+%d' % (w, h, x, y))
	txt_add_streamer_value = StringVar()
	txt_add_streamer = Entry(win_main, width=10, textvariable=txt_add_streamer_value)
	txt_add_streamer.config(state=NORMAL)
	txt_add_streamer.pack()

	btn_add = Button(win_main, text="Add", command=show_text)
	btn_add.pack()

	lbl_streamer_names_value = StringVar()
	lbl_streamer_names = Label(win_main, textvariable=lbl_streamer_names_value)
	lbl_streamer_names.pack()
	lbl_streamer_names_value.set(arr_streamers)
	
	win_main.after(5000,runCheckr())
	win_main.mainloop()

def alert_popup(popup_title, popup_msg, streamer_url, streamer):
	if gSOUND_ALERT:
		playsound(gSOUND_ALERT)
	
	# Create popup window
	win_popup = Tk()
	win_popup.title(popup_title)
	w = 400	 # width
	h = 200	 # height
	x = (win_popup.winfo_screenwidth() - w)/2
	y = (win_popup.winfo_screenheight() - h)/2
	win_popup.geometry('%dx%d+%d+%d' % (w, h, x, y))
	win_msg = popup_msg + '\n' + streamer_url
	lbl_win_msg = Label(win_popup, text=win_msg, width=120, height=5, font=(None,12))
	win_popup.attributes('-topmost',True) # put on top
	lbl_win_msg.pack()
	
	#Close button
	btn_close = Button(win_popup, text="close", command=win_popup.destroy, width=10)

	#Open Stream button
	def open_stream(url):
		webbrowser.open_new(url)
	btn_open_stream = Label(win_popup, text="Click to Watch " + streamer + " now", fg="blue", cursor="hand2", font=(None,20))
	btn_open_stream.pack()
	btn_open_stream.bind("<Button-1>", lambda e: open_stream("https://twitch.tv/{}".format(streamer)))
	btn_close.pack()
	
	mainloop()

def is_streamer_live(streamer_name, my_token):

	headers = {
		'Client-ID': gCLIENTID,
		'authorization': my_token
	}
	
	params = (
		('user_login', streamer_name),
	)

	try:
		response = requests.get('https://api.twitch.tv/helix/streams', headers=headers, params=params)
		json_data = json.loads(response.map(response)[0])
		json_data = json_data['data'][0]
		return True

	except:
		return False

streams = initial_setup()