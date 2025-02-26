import tkinter as tk
from tkinter import ttk
import pyautogui             
from pynput import mouse     
import PIL.ImageGrab
from PIL import Image, ImageTk
import ctypes
from tkinter.messagebox import showinfo
import time
import json

"""Open the json files the store the color RGB info and corresponding names. If none exist, initiate empty lists to hold them"""
with open("./assets/memory.json", "r") as file:
    try:
        colors = json.load(file)
    except json.JSONDecodeError:
        colors = []
with open("./assets/names.json", "r") as file1:
    try:
        names = json.load(file1)
    except json.JSONDecodeError:
        names = []
        
"""Write to the json files before closing the root window so that the color library is preserved between sessions of use"""
def on_closing():
    with open("./assets/memory.json", "w") as file:
        json.dump(colors, file)
    with open("./assets/names.json", "w") as file:
        json.dump(listbox.get(0, tk.END), file)
    root.destroy()
    
"""Start the listener that detects when a color is selected"""    
def start_listener():
    global mouse_listener
    mouse_listener = mouse.Listener(on_click=on_click)
    mouse_listener.start()
    ctypes.windll.user32.SetSystemCursor(ctypes.windll.user32.LoadImageW(0, "./assets/crosshair.cur", 2, 0, 0, 0x00000010), 32512)
    screen_overlay()

"""Stop the listener because a color has been chosen"""
def stop_listener():
    global mouse_listener
    mouse_listener.stop()
    ctypes.windll.user32.SystemParametersInfoW(0x0057, 0, None, 0)
    
"""Grabs the color of the pixel that was clicked and adds it to the library"""    
def on_click(x, y, button, pressed):
    if pressed:
        stop_listener()
        for widget in root.winfo_children():
            if isinstance(widget, tk.Toplevel):
                widget.destroy()
        color = get_pixel_color(x, y)
        color = list(color)
        if color not in colors:
            colors.append(color)
            listbox.insert(tk.END, f"Color {colors.index(color)}")
        else:
            showinfo(title="Notification", message="That color is already in your library!")
            
"""Helper function to on_click that actually obtains the color of the pixel selected"""             
def get_pixel_color(x, y):
    screen = PIL.ImageGrab.grab()
    color = screen.getpixel((x, y))
    return color

"""Creates a class that defines the color magnifying glass"""
class ColorMagnifier:
    def __init__(self, parent):
        self.window = tk.Toplevel(parent)
        self.window.overrideredirect(True)
        self.window.wm_attributes("-topmost", True)
        self.label = tk.Label(self.window, width=50, height=50, bd=2, relief="solid", highlightbackground="black")
        self.label.pack()
        self.update_color()

    def get_pixel_color(self):
        x, y = pyautogui.position()
        color = pyautogui.pixel(x, y)
        return rgb_to_hex(color)

    def update_color(self):
        color = self.get_pixel_color()
        self.label.configure(bg=color) 
        x, y = pyautogui.position()
        self.window.geometry(f"{50}x{50}+{x+20}+{y+20}") 
        self.window.after(50, self.update_color) 

"""Creates an overlay which is a screenshot of the display screen at the time 'Grab a color' button is pressed. This prevents interacting with display screen while attempting to grab a color"""
def screen_overlay():
    screenshot = pyautogui.screenshot()
    screenshot_image = ImageTk.PhotoImage(screenshot)
    overlay = tk.Toplevel(root)
    overlay.attributes('-fullscreen', True)  
    overlay.screenshot_image = screenshot_image
    canvas = tk.Canvas(overlay, width=overlay.winfo_screenwidth(), height=overlay.winfo_screenheight())
    canvas.pack(fill="both", expand=True)
    canvas.create_image(0, 0, anchor="nw", image=overlay.screenshot_image)
    magnifier = ColorMagnifier(overlay)
                              
"""Function to convert RGB color info into hexadecimal format"""
def rgb_to_hex(rgb):
    return "#{:02x}{:02x}{:02x}".format(*rgb)

"""Function to convert RGB color info into CMYK format"""
def rgb_to_cmyk(rgb):
    r, g, b = rgb[0] / 255.0, rgb[1] / 255.0, rgb[2] / 255.0
    k = 1 - max(r, g, b)
    if k == 1: 
        return 0, 0, 0, 100
    c = (1 - r - k) / (1 - k)
    m = (1 - g - k) / (1 - k)
    y = (1 - b - k) / (1 - k)
    return round(c * 100), round(m * 100), round(y * 100), round(k * 100)

"""Function to convert RGB color info into HSL format"""
def rgb_to_hsl(rgb):
    r, g, b = rgb[0] / 255.0, rgb[1] / 255.0, rgb[2] / 255.0
    max_val, min_val = max(r, g, b), min(r, g, b)
    delta = max_val - min_val
    l = (max_val + min_val) / 2
    if delta == 0:
        s = 0  
    else:
        s = delta / (1 - abs(2 * l - 1))
    if delta == 0:
        h = 0  
    elif max_val == r:
        h = 60 * (((g - b) / delta) % 6)
    elif max_val == g:
        h = 60 * (((b - r) / delta) + 2)
    elif max_val == b:
        h = 60 * (((r - g) / delta) + 4)
    h = round(h) 
    s = round(s * 100) 
    l = round(l * 100)
    return h, s, l

"""Function that display's the selected color in the demo window"""
def display_color(event):
    selected_index = listbox.curselection()  
    if selected_index:
        info_box.config(state="normal")
        info_box.delete("1.0", "end")
        color = colors[selected_index[0]] 
        hex_color = rgb_to_hex(color)
        color_canvas.config(bg=hex_color)
        delete_button.config(state="normal")
        rename_button.config(state="normal")
        color_info = []
        color_info.append(f"RGB: {color}")
        color_info.append(f"Hex: {rgb_to_hex(color)}")
        color_info.append(f"CMYK: {rgb_to_cmyk(color)}")
        color_info.append(f"HSL: {rgb_to_hsl(color)}")
        info_box.insert(tk.END, "\n".join(color_info))
        info_box.config(state="disabled")


"""Removes the selected color from the library"""
def delete_color():
    selected_index = listbox.curselection() 
    if selected_index:
        colors.pop(selected_index[0])
        listbox.delete(selected_index[0])
        color_canvas.config(bg="white")
        delete_button.config(state="disabled")
        rename_button.config(state="disabled")
        info_box.config(state="normal")
        info_box.delete("1.0", "end")

"""Renames a color in the library"""
def rename_color():
    selected_index = listbox.curselection()
    if selected_index:
        def commit(event):
            name = name_entry.get()
            listbox.delete(selected_index[0])
            listbox.insert(selected_index[0], name)
            entry_window.destroy()
            color_canvas.config(bg="white")
            delete_button.config(state="disabled")
            rename_button.config(state="disabled")
            info_box.config(state="normal")
            info_box.delete("1.0", "end")
        entry_window = ttk.Frame(root, height=250, width=400)
        entry_window.place(x=400, y=375)
        text_label = ttk.Label(entry_window, text="Enter new name below:")
        text_label.pack(expand=True)
        new_name = tk.StringVar()
        name_entry = ttk.Entry(entry_window, textvariable=new_name)
        name_entry.pack(expand=True)
        finish_btn = ttk.Button(entry_window, text="Rename")
        finish_btn.pack(expand=True)
        finish_btn.bind("<Button-1>", commit)
        name_entry.focus()
        
"""Create the Main Window"""
root = tk.Tk()                                               
root.title("Color Grabber")                                      
root.geometry("1200x1000-150-150")                                 
root.iconbitmap("./assets/color-wheel-icon.ico")      

"""Create the list for Colors"""
color_list = tk.Variable(value=names)
listbox = tk.Listbox(root, listvariable=color_list)
listbox.place(x=25, y=80, width=600, height=800)
list_label = ttk.Label(root, text="My Color Library:")                                      
list_label.place(x=25, y=20, width=200, height=60)
listbox.bind("<<ListboxSelect>>", display_color)

"""Create the button for grabbing colors"""
dropper_icon = tk.PhotoImage(file='./assets/dropper_icon.png')                     
grab_button = ttk.Button(root, image=dropper_icon, text='Grab a color', compound=tk.LEFT, command=start_listener) 
grab_button.place(x=700, y=40, width=400, height=75)                                      

"""Create the canvas for displaying colors"""
color_canvas = tk.Canvas(root, width=400, height=400, bg="white")
color_canvas.place(x=700, y=150)

"""Create the color info listbox"""
info_box = tk.Text(root)
info_box.place(x=700, y=620, width=400, height=200)
info_label = ttk.Label(root, text="Color Info:")
info_label.place(x=700, y=570, width=200, height=40)

"""Create Rename and Delete Buttons"""
rename_button = ttk.Button(root, text="Rename Color", state="disabled", command=rename_color)
delete_button = ttk.Button(root, text="Delete Color", state="disabled", command=delete_color)
rename_button.place(x=700, y=850, width=200, height=50)
delete_button.place(x=700, y=920, width=200, height=50)

root.protocol("WM_DELETE_WINDOW", on_closing)
root.mainloop()

                                                                       
