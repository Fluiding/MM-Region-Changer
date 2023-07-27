import urllib3
import json
import re
import os
import tkinter as tk
import ttkbootstrap as ttk

rule_name: str = "MM-Region-Changer"
filter_cmd: str
reset_cmd: str = f'netsh advfirewall firewall delete rule name="{rule_name}"'

# UAC Elevation prompt for firewall access

root = ttk.Window(themename="darkly")
root.resizable(False, False)
root.title("MM Region Changer v1.5")
root.geometry("400x690")

# Constants
res: dict = json.loads(urllib3.PoolManager().request("GET", "https://api.steampowered.com/ISteamApps/GetSDRConfig/v1?appid=730").data.decode("utf8"))
selected_cities: list[str] = []
cities_current: dict = {}
checkboxes: list[ttk.Checkbutton] = []

cities: dict = {

	"Europe West": {
		"ams": ["Amsterdam, Netherlands", tk.IntVar()],
		"fra": ["Frankfurt, Germany", tk.IntVar()],
		"lhr": ["London, UK", tk.IntVar()],
		"mad": ["Madrid, Spain", tk.IntVar()],
		"par": ["Paris, France", tk.IntVar()],
		"mst1": ["Strasbourg, France", tk.IntVar()],
		"mlx1": ["Luxembourg", tk.IntVar()],
	},
	
	"Europe East": { # (99.9% russians 👎)
		"vie": ["Vienna, Austria", tk.IntVar()],
		"waw": ["Warsaw, Poland", tk.IntVar()],
		"sto": ["Stockholm, Sweden", tk.IntVar()],
		"sto2": ["Stockholm, Sweden", tk.IntVar()],
	},

	"USA East": {
		"atl": ["Atlanta, Georgia", tk.IntVar()],
		"iad": ["Sterling City, Texas", tk.IntVar()],
		"mny1": ["New York", tk.IntVar()],
		"mmi1": ["Miami, Florida", tk.IntVar()],
	},
	
	"USA West": {
		"dfw": ["Dallas, Texas", tk.IntVar()],
		"lax": ["Los Angeles", tk.IntVar()],
		"ord": ["Chicago, Illinois", tk.IntVar()],
		"sea": ["Seattle, Washington", tk.IntVar()],
		"msa1": ["Salt Lake City, Utah", tk.IntVar()],
		"msl1": ["St. Louis Missouri", tk.IntVar()],
	},

	"Asia": {
		"bom": ["Mumbai, India", tk.IntVar()],
		"maa": ["Chennai, India", tk.IntVar()],
		"dxb": ["Dubai, UAE", tk.IntVar()],
		"seo": ["Seoul, South Korea", tk.IntVar()],
		"sgp": ["Singapore", tk.IntVar()],
		"tyo": ["Tokyo North, Japan", tk.IntVar()],
		"tyo1": ["Tokyo South, Japan", tk.IntVar()],
		"hkg": ["Hong Kong, China", tk.IntVar()],
		"pwz": ["Zhejiang, China", tk.IntVar()],
		"pwu": ["Hebei, China", tk.IntVar()],
		"pww": ["Wuhan, China", tk.IntVar()],
		"shb": ["Shanghai, China", tk.IntVar()],
		"sham": ["Shanghai, China", tk.IntVar()],
		"shat": ["Shanghai, China", tk.IntVar()],
		"shau": ["Shanghai, China", tk.IntVar()],
		"pwg": ["Guangdong, China", tk.IntVar()],
		"canm": ["Guangdong, China", tk.IntVar()],
		"cant": ["Guangdong, China", tk.IntVar()],
		"canu": ["Guangdong, China", tk.IntVar()],
		"pwj": ["Tianjin, China", tk.IntVar()],
		"tsnm": ["Tianjin, China", tk.IntVar()],
		"tsnt": ["Tianjin, China", tk.IntVar()],
		"tsnu": ["Tianjin, China", tk.IntVar()],
	},

	"Oceania": {
		"syd": ["Sydney, Australia", tk.IntVar()]
	},

	"Africa": {
		"jnb": ["Cape Town, South Africa", tk.IntVar()]
	}
}

# Functions
def find_city(_city):
	for region in cities.values():
		for city, data in region.items():
			if city == _city: return data
	return {}

def filter():
	relays: list[str] = []
	for city, data in res["pops"].items():
		if not any(city in region for region in cities.values()): continue
		if city in selected_cities: continue
		for relay in data["relays"]:
			relays.append(relay["ipv4"])
	
	filter_cmd = f'netsh advfirewall firewall add rule name="MM-Region-Changer" dir=out action=block remoteip={",".join(relays)}'
	os.system(reset_cmd)
	os.system(filter_cmd)
	update_labels()

def reset():
	os.system(reset_cmd)
	update_labels()

def select_ip():
	global cities_current
	for region in cities.values():
		for abbrv, data in region.items():
			if data[1].get() == cities_current[abbrv]: continue
			if data[1].get() == 0:
				selected_cities.remove(abbrv)
			else:
				selected_cities.append(abbrv)

	for region in cities.values():
		for city, data in region.items():
			cities_current[city] = data[1].get()

def update_labels():

	output = os.popen('netsh advfirewall firewall show rule name="MM-Region-Changer"')
	rule_stdout = output.read()
	output.close()
	print(rule_stdout)

	if "eIP:" in rule_stdout:
		state_label.configure(text="Enabled", foreground="green")
		filter_button.configure(text="Update")

		blocked_ips: list[str] = re.findall(r'\b(?:\d{1,3}\.){3}\d{1,3}(?!\d)', rule_stdout)
		for city, data in res["pops"].items():
			if not any(city in region for region in cities.values()): continue
			for relay in data["relays"]:
				if relay["ipv4"] in blocked_ips: continue
				find_city(city)[1].set(1)
				
	else:
		state_label.configure(text="Disabled", foreground="red")
		filter_button.configure(text="Enable")
		for region in cities.values():
			for city in region.values():
				city[1].set(0)

# Design
title: None = ttk.Label(root, text="MM Region Changer", font="Calibri 30 normal").pack()
state_label: ttk.Label = ttk.Label(root, text="Disabled", font="Calibri 21 normal", foreground="red")
state_label.pack()

button_frame: ttk.Frame = ttk.Frame(root)
filter_button: ttk.Button = ttk.Button(button_frame, text="Filter Regions", command=filter, width=55)
reset_button: ttk.Button = ttk.Button(button_frame, text="Reset", command=reset, width=55)
filter_button.pack()
reset_button.pack(pady=10)
button_frame.pack()

server_frame1: ttk.Frame = ttk.Frame(root)
server_frame2: ttk.Frame = ttk.Frame(root)

region_count: int = 0
for region, data in cities.items():
	region_count += 1
	current_frame: ttk.Frame = server_frame1 if region_count < 5 else server_frame2

	ttk.Label(current_frame, text=region, font="Calibri 18 bold").pack(pady=5)
	for city in data.values():

		check: ttk.Checkbutton = ttk.Checkbutton(
			current_frame,
			text=f"{city[0]}",
			variable=city[1],
			command=select_ip
		)
		checkboxes.append(check)
		check.state(['!alternate'])
		check.pack(anchor=tk.W)

server_frame1.pack(side=tk.LEFT, padx=10, anchor=tk.N)
server_frame2.pack(side=tk.RIGHT, padx=20, anchor=tk.N)

cities_current: dict = {}
for region in cities.values():
	for city, data in region.items():
		cities_current[city] = data[1].get()

update_labels()
root.mainloop()
