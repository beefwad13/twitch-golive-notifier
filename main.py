from playsound import playsound
from tkinter import *
import requests
import json
import webbrowser
from datetime import datetime
import config
import threading




# GLOBAL VARS
gAPP_TITLE = "TwitchCheckr v6.9.420.0001"
gCLIENTID = config.twitch_client_id
gCLIENT_SECRET = config.twitch_client_secret
gSOUND_ALERT = config.alert_sound
gFAVORITE_STREAMERS = config.favorite_streamers
gSTATUS_CHECK_FREQUENCY = config.status_check_frequency
already_live = []

def initial_setup():
	console_log("Setting up...")
	arr_streamers = []

	new_auth_token = get_twitch_auth_token()
	
	if gFAVORITE_STREAMERS:
		arr_streamers = gFAVORITE_STREAMERS
		print("Favorite Streamers set to:")
		print(gFAVORITE_STREAMERS)

	console_log("Start threads...")
	threading.Timer(gSTATUS_CHECK_FREQUENCY / 1000, check_for_status_update, args=(arr_streamers, new_auth_token)).start()
	create_main_window(arr_streamers)

def check_for_status_update(arr_streamers, auth_token):	
	console_log("Checking for status updates...")

	#def check_api_for_streamer_status():
	for streamer in arr_streamers:
		is_live = (is_streamer_live(streamer, auth_token))

		if is_live:
			if streamer not in already_live:
				console_log(streamer + " is live!")
				show_alert_popup(streamer)
				already_live.append(streamer)

		if not is_live:
			if streamer in already_live:
				console_log(streamer + " went offline")
				already_live.remove(streamer)

	console_log("Next check in " + str(gSTATUS_CHECK_FREQUENCY / 1000) + " seconds")
	threading.Timer(gSTATUS_CHECK_FREQUENCY / 1000, check_for_status_update, args=(arr_streamers, auth_token)).start()

def create_main_window(arr_streamers):

	def add_streamer_to_ui():
		if txt_add_streamer_value.get() != "":
			arr_streamers.append(txt_add_streamer_value.get())
		txt_add_streamer_value.set("")
		lbl_streamer_names_value.set(("\n").join(arr_streamers))

	# Create main window
	win_main = Tk()
	win_main.title(gAPP_TITLE)
	w = 400 # width
	h = 200 # height
	x = (win_main.winfo_screenwidth() - w)/2
	y = (win_main.winfo_screenheight() - h)/2
	win_main.geometry('%dx%d+%d+%d' % (w, h, x, y))
	txt_add_streamer_value = StringVar()
	txt_add_streamer = Entry(win_main, width=60, textvariable=txt_add_streamer_value)
	txt_add_streamer.config(state=NORMAL)
	txt_add_streamer.pack()

	# Create add button
	btn_add = Button(win_main, text="Add", command=add_streamer_to_ui, foreground="white", background="green", height=2, width=24)
	btn_add.pack()

	# Create label to show streamer list
	lbl_streamer_list = Label(win_main, text="Watch list:", font="None 12 underline")
	lbl_streamer_list.pack()

	lbl_streamer_names_value = StringVar()
	lbl_streamer_names = Label(win_main, textvariable=lbl_streamer_names_value)
	lbl_streamer_names.pack()
	lbl_streamer_names_value.set(("\n").join(arr_streamers))
	
	# Display window
	#win_main.bind('<Visibility', threading.Timer(5.0, check_for_status_update(arr_streamers, auth_token)).start())
	win_main.mainloop()

def show_alert_popup(streamer):
	popup_title = gAPP_TITLE + " " + "{} IS LIVE!".format(streamer)
	popup_msg = "{} is live!".format(streamer)
	streamer_url = "https://twitch.tv/{}".format(streamer)


	# Play optiona sound
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
	
	win_popup.mainloop()

def is_streamer_live(streamer_name, my_token):

	headers = {
		'Client-ID': gCLIENTID,
		'authorization': my_token
	}
	
	params = (
		('user_login', streamer_name),
	)

	try:
		console_log("Checking if [" + streamer_name + "] is live...")
		response = requests.get('https://api.twitch.tv/helix/streams', headers=headers, params=params)
		json_data = json.loads(response.text)
		json_data = json_data['data'][0]
		return True

	except:
		console_log("Not live or error occured")
		return False

def get_twitch_auth_token():
	console_log("Getting twitch token...")
	url = 'https://id.twitch.tv/oauth2/token'
	data_obj = {'client_id': gCLIENTID, 'client_secret': gCLIENT_SECRET, 'grant_type': 'client_credentials'}
	x = requests.post(url, data=data_obj)
	data_obj = (x.json())
	console_log("Done getting twitch token")
	return "Bearer " + (data_obj['access_token'])

def get_timestamp():
	return datetime.now().strftime("%d/%m/%Y %H:%M:%S")

def console_log(msg):
	print(get_timestamp() + ": " + msg)




streams = initial_setup()