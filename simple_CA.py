import numpy as np
import tkinter as tk
import matplotlib.pyplot as plt
import datetime
from PIL import Image, ImageTk

window = tk.Tk()
window.title("simple_CA")
window.geometry('500x550')
window.configure(background='black')
width, height = 500, 500
size = (50, 50)
factor = (500//size[0])
canvas = tk.Canvas(window, width=width, height=height, highlightbackground = "black")
canvas.place(relx=0.5, y=325, anchor="center")
running = 0
capture = 0
borders = 0

def get_neighbours(src, ks): # moore neighbourhood
	neighbours = []
	for c in range(ks[0]):
		for t in range(ks[1]):	
				neighbours.append(np.roll(src, (c-(ks[0]//2),t-(ks[1]//2)), axis=[0,1]))
	return np.sum(neighbours,0)[borders:src.shape[0]-borders, borders:src.shape[1]-borders]

def get_neighbours_vonneumann(src, ks): # moore neighbourhood
	neighbours = []
	for c in range(ks):
		neighbours.append(np.roll(src, (c-(ks//2),0), axis=[0,1]))
	for t in range(ks):	
		neighbours.append(np.roll(src, (0,t-(ks//2)), axis=[0,1]))
	return np.sum(neighbours,0)[borders:src.shape[0]-borders, borders:src.shape[1]-borders]



def scale_im(arr,factor):
	return np.kron(arr, np.ones((factor,factor)))

def draw(event):
	sim[event.y//factor, event.x//factor] = 255

def erase(event):
	sim[event.y//factor, event.x//factor] = 0

def clear():
	global sim
	sim = np.zeros(size, dtype=np.uint8)

def cap():
	global capture
	capture = (capture+1)%2
	if capture:
		capture_text.set("on")
	else:
		capture_text.set("off")

def border():
	global borders
	borders = (borders+1)%2
	if borders:
		border_text.set("on")
	else:
		border_text.set("off")

def randomize():
	global sim
	sim = np.random.choice([0, 255], size=size, p=[6/10, 4/10])

def rule():
	global rule
	rule = (rule+1)%4
	rule_text.set(str(rule))

def run():
	global running
	running = (running+1)%2
	if running:
		run_text.set("running...")
	else:
		run_text.set("stopped")

button_run = tk.Button(window, text="run",command=run)
button_run.grid(row=0,column=0)
run_text = tk.StringVar(value="stopped")
label_run = tk.Label(window, textvariable=run_text, bg="black",fg="white", width=10)
label_run.grid(row=1,column=0)
button_clear = tk.Button(window, text="clear",command=clear)
button_clear.grid(row=0,column=1)
button_rule = tk.Button(window, text="rule",command=rule)
button_rule.grid(row=0,column=2)
rule_text = tk.StringVar(value="0")
label_rule = tk.Label(window, textvariable=rule_text, bg="black",fg="white", width=1)
label_rule.grid(row=1,column=2)
button_border = tk.Button(window, text="border",command=border)
button_border.grid(row=0,column=3)
border_text = tk.StringVar(value="off")
label_border = tk.Label(window, textvariable=border_text, bg="black",fg="white", width=3)
label_border.grid(row=1,column=3)
button_rand = tk.Button(window, text="random",command=randomize)
button_rand.grid(row=0,column=4)
button_capture = tk.Button(window, text="capture",command=cap)
button_capture.grid(row=0,column=5)
capture_text = tk.StringVar(value="off")
label_capture = tk.Label(window, textvariable=capture_text, bg="black",fg="white", width=3)
label_capture.grid(row=1,column=5)


scaler = tk.Scale(window, from_=0, to=1, resolution=0.05, orient="horizontal", bg="black", fg="white")
scaler.grid(row=0,column=6)
scaler.set(0.25)
sim = np.zeros(size, dtype=np.uint8)
canvas.bind("<B1-Motion>", draw)
canvas.bind("<Button-1>", draw)
canvas.bind("<B3-Motion>", erase)
canvas.bind("<Button-3>", erase)


rule = 0
last = datetime.datetime.now()
index = 0
while True:
	delta = datetime.datetime.now() - last
	scaled = scale_im(sim, factor)
	im = ImageTk.PhotoImage(image=Image.fromarray(scaled))
	canvas.create_image(3, 3, anchor="nw", image=im)
	if capture:
		plt.imsave("capture/"+str(index)+".jpg", scaled, cmap="gray")
		index+=1
	window.update_idletasks()
	window.update()
	if running and delta.microseconds > scaler.get()*1000000:
		if rule == 3:
			next_state = get_neighbours(np.pad(sim, [(borders,borders),(borders,borders)], mode="constant"), (3,3)) - sim
			#next_state = get_neighbours_vonneumann(sim, 3)
			sim = (next_state//8+8).astype(np.uint8)
			#sim = (next_state//4+1).astype(np.uint8)
		else:
			next_state = get_neighbours(np.pad(sim//255, [(borders,borders),(borders,borders)], mode="constant"), (3,3)) - sim//255
#			next_state = get_neighbours(sim//255, (3,3)) - sim//255
#			next_state = get_neighbours_vonneumann(sim//255, 3) - sim//255
			if rule == 0:
				sim = np.where(((next_state > 4) | ((next_state == 4) & (sim==0))), 255, 0)
			elif rule == 1:
				sim = np.where(((next_state > 4) | ((next_state == 4) & (sim == 255))), 255, 0) # vote rule
			elif rule == 2:
				sim = np.where((((next_state > 1) & (next_state < 4) & (sim == 255)) | ((sim == 0) & (next_state == 3))), 255, 0) # GOL
		last = datetime.datetime.now()
