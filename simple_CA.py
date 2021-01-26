import numpy as np
import tkinter as tk
from PIL import Image, ImageTk
import time

window = tk.Tk()
window.title("simple_CA")
window.geometry('600x600')
window.configure(background='black')
width, height = 500, 500
size = (50, 50)
factor = 10
canvas = tk.Canvas(window, width=width, height=height, highlightbackground = "black")
canvas.place(relx=0.5, rely=0.5, anchor="center")
running = 0

def get_neighbours(src, ks): # moore neighbourhood
	neighbours = []
	for c in range(ks[0]):
		for t in range(ks[1]):	
				neighbours.append(np.roll(src, (c-(ks[0]//2),t-(ks[1]//2)), axis=[0,1]))
	return np.sum(neighbours,0)

def scale_im(arr,factor):
	return np.kron(arr, np.ones((factor,factor)))

def draw(event):
	sim[event.y//factor, event.x//factor] = 255

def erase(event):
	sim[event.y//factor, event.x//factor] = 0

def clear():
	global sim
	sim = np.zeros(size, dtype=np.uint8)

def randomize():
	global sim
	sim = np.random.choice([0, 255], size=size, p=[6/10, 4/10])

def rule():
	global rule
	rule = (rule+1)%3

def run():
	global running
	running = (running+1)%2

button_run = tk.Button(window, text="run",command=run)
button_run.grid(row=0,column=0)
button_clear = tk.Button(window, text="clear",command=clear)
button_clear.grid(row=0,column=1)
button_rule = tk.Button(window, text="rule",command=rule)
button_rule.grid(row=0,column=2)
button_rand = tk.Button(window, text="random",command=randomize)
button_rand.grid(row=0,column=3)
sim = np.zeros(size, dtype=np.uint8)
canvas.bind("<B1-Motion>", draw)
canvas.bind("<Button-1>", draw)
canvas.bind("<B3-Motion>", erase)
canvas.bind("<Button-3>", erase)


rule = 0
while True:
	im = ImageTk.PhotoImage(image=Image.fromarray(scale_im(sim, factor)))
	canvas.create_image(3, 3, anchor="nw", image=im)
	window.update_idletasks()
	window.update()
	if running:
		next_state = get_neighbours(sim//255, (3,3)) - sim//255
		if rule == 0:
			sim = np.where((((next_state > 1) & (next_state < 4) & (sim == 255)) | ((sim == 0) & (next_state == 3))), 255, 0) # GOL
		elif rule == 1:
			sim = np.where(((next_state > 4) | ((next_state == 4) & (sim==0))), 255, 0)
		elif rule == 2 :
			sim = np.where(((next_state > 4) | ((next_state == 4) & (sim == 255))), 255, 0) # vote rule
#		time.sleep(0.5)
