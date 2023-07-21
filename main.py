import requests, json, subprocess, re, ctypes, sys, tkinter as tk, ttkbootstrap as ttk

# UAC Elevation prompt for firewall access
if not ctypes.windll.shell32.IsUserAnAdmin():
	ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
	sys.exit(0)

root = ttk.Window(themename="darkly")
root.title("MM Region Changer v1.4")
root.geometry("400x600")
root.resizable(height = None, width = None)

# Constants
res = json.loads(requests.get("https://api.steampowered.com/ISteamApps/GetSDRConfig/v1?appid=730").content.decode("utf8"))

selected_cities = []
cities_current = {}
checkboxes = []
abbrv = {
    'ams': 'Amsterdam, Netherlands', 'atl': 'Atlanta, USA',
    'bom': 'Bombay, India', 'dxb': 'Dubai, UAE',
    'eat': 'Wenatchee, USA', 'eze': 'Buenos Aires, Argentina',
    'fra': 'Frankfurt, Germany', 'waw': 'Warsaw, Poland',
    'gru': 'Sao Paulo, Brazil', 'hkg': 'Hong Kong',
    'iad': 'Washington DC, USA', 'jnb': 'Cape Town, South Africa',
	'lax': 'Los Angeles, USA', 'lhr': 'London, UK',
    'lim': 'Lima, Peru', 'lux': 'Luxembourg',
    'maa': 'Chennai, India', 'mad': 'Madrid, Spain',
    'man': 'Manila, Philippines', 'okc': 'Oklahoma, USA',
    'ord': 'Chicago, USA', 'par': 'Paris, France',
    'scl': 'Santiago, Chile', 'sea': 'Seattle, USA',
    'seo': 'Seoul, South Korea', 'sgp': 'Singapore',
    'shb': 'Nakashibetsu, Japan', 'sto': 'Stockholm, Sweden',
    'sto2': 'Stockholm, Sweden', 'syd': 'Sydney, Australia',
    'tyo': 'Tokyo North, Japan', 'tyo1': 'Tokyo South, Japan',
    'vie': 'Vienna, Austria'
}
regions = {
	"Europe West": ["ams", "fra", "lhr", "par", "mad"],
	"Europe East": ["sto", "sto2", "waw", "vie"], # 99.9% russians
	"USA East": ["atl", "iad", "ord"],
	"USA West": ["lax", "sea"],
	"South America": ["eze", "gru", "lim", "scl"],
	"Asia": ["bom", "dxb", "hkg", "maa", "sgp", "seo", "shb", "tyo", "tyo1"],
	"Oceania": ["syd"], # vegemite i reckon brah aye mate
	"Africa": ["jnb"]
}
cities = {
	"ams": tk.IntVar(), "atl": tk.IntVar(), "bom": tk.IntVar(), "dxb": tk.IntVar(),
	"eze": tk.IntVar(), "fra": tk.IntVar(), "gru": tk.IntVar(),"sto2": tk.IntVar(),
	"hkg": tk.IntVar(), "iad": tk.IntVar(), "jnb": tk.IntVar(), "lax": tk.IntVar(),
	"lhr": tk.IntVar(), "lim": tk.IntVar(), "maa": tk.IntVar(), "mad": tk.IntVar(),
	"ord": tk.IntVar(), "par": tk.IntVar(), "scl": tk.IntVar(), "sea": tk.IntVar(),
	"seo": tk.IntVar(), "sgp": tk.IntVar(), "shb": tk.IntVar(), "sto": tk.IntVar(),
	"syd": tk.IntVar(), "tyo": tk.IntVar(), "vie": tk.IntVar(), "waw": tk.IntVar(),
	"tyo1": tk.IntVar()
}

# Functions
def filter():
	relays = []
	for city, data in res["pops"].items():
		if city in selected_cities or not city in cities: continue
		for relay in data["relays"]:
			relays.append(relay["ipv4"])
	
	subprocess.run(
		'netsh advfirewall firewall delete rule name="MM-Region-Changer"',
		creationflags=subprocess.CREATE_NO_WINDOW)
	subprocess.run(
		f'netsh advfirewall firewall add rule name="MM-Region-Changer" dir=out action=block remoteip={",".join(relays)}',
		creationflags=subprocess.CREATE_NO_WINDOW)
	update_labels()

def reset():
	subprocess.run(
		'netsh advfirewall firewall delete rule name="MM-Region-Changer"',
		creationflags=subprocess.CREATE_NO_WINDOW)
	update_labels()

def select_ip():
	global cities_current
	for abbrv, data in cities.items():
		if data.get() == cities_current[abbrv]: continue
		if data.get() == 0:
			selected_cities.remove(abbrv)
		else:
			selected_cities.append(abbrv)

	cities_current = {city: val.get() for city, val in cities.items()}

def update_labels():

	rule_stdout = subprocess.run(
		'netsh advfirewall firewall show rule name="MM-Region-Changer"',
		capture_output=True, encoding="utf-8").stdout
	print(rule_stdout)

	if "eIP:" in rule_stdout:
		state_label.configure(text="Enabled", foreground="green")
		filter_button.configure(text="Update")

		blocked_ips = re.findall(r'\b(?:\d{1,3}\.){3}\d{1,3}(?!\d)', rule_stdout)
		for city, data in res["pops"].items():
			if not city in cities: continue
			for relay in data["relays"]:
				if relay["ipv4"] in blocked_ips: continue
				cities[city].set(1)
				
	else:
		state_label.configure(text="Disabled", foreground="red")
		filter_button.configure(text="Enable")
		for city in cities.values():
			city.set(0)

# Design
title = ttk.Label(root, text="MM Region Changer", font="Calibri 30 normal").pack()
state_label = ttk.Label(root, text="Disabled", font="Calibri 21 normal", foreground="red")
state_label.pack()

button_frame = ttk.Frame(root)
filter_button = ttk.Button(button_frame, text="Filter Regions", command=filter, width=55)
reset_button = ttk.Button(button_frame, text="Reset", command=reset, width=55)
filter_button.pack()
reset_button.pack(pady=10)
button_frame.pack()

server_frame1 = ttk.Frame(root)
server_frame2 = ttk.Frame(root)

region_count = 0
for region, iata in regions.items():
	region_count += 1
	server_frame = server_frame1 if region_count < 5 else server_frame2

	ttk.Label(server_frame, text=region, font="Calibri 18 bold").pack(pady=5)
	for city in iata:

		check = ttk.Checkbutton(
			server_frame,
			text=f"{abbrv[city]}",
			variable=cities[city],
			command=select_ip
		)
		checkboxes.append(check)
		check.state(['!alternate'])
		check.pack(anchor=tk.W)

server_frame1.pack(side=tk.LEFT, padx=10)
server_frame2.pack(side=tk.RIGHT, padx=20)
cities_current = {f"{city}": val.get() for city, val in cities.items()}

update_labels()
root.mainloop()