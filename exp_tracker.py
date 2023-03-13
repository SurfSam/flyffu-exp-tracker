import re
import sched
import tkinter as tk
from datetime import datetime, timedelta

import cv2
import numpy as np
import pandas as pd
import pytesseract
from PIL import ImageGrab
from scipy import stats

pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# position and dimensions of exp bar
EXP_X = 159
EXP_Y = 195
EXP_WIDTH = 90
EXP_HEIGHT = 19

# position and dimensions of tool
TOOL_X = 265
TOOL_Y = 71
TOOL_WIDTH = 520
TOOL_HEIGHT = 35

class ExpTracker:

    def __init__(self):

        self.level_diff = 0
        self.x_offset = EXP_X
        self.y_offset = EXP_Y

        self.width = EXP_WIDTH
        self.height = EXP_HEIGHT

        self.REGEX_PATTERN = re.compile(r"[^\d]", re.IGNORECASE)

        self.window = tk.Tk()

        padx = 5
        pady = 5

        bg_color = "gray"
        fg_color = "white"

        self.window.title("Exp Tracker")
        self.window.geometry('%dx%d+%d+%d' % (TOOL_WIDTH, TOOL_HEIGHT, TOOL_X, TOOL_Y))
        self.window.attributes('-topmost', 1)
        self.window.overrideredirect(True)

        self.window.config(bg=bg_color)

        frame = tk.Frame(self.window, width=w, height=h)
        frame.grid(row=0, column=0, padx=padx, pady=pady)
        frame.pack(fill="both", expand=True)
        frame.config(bg=bg_color)
        frame.rowconfigure(0, weight=1)
        frame.columnconfigure(1, weight=1)
        frame.columnconfigure(2, weight=1)
        frame.columnconfigure(3, weight=1)

        self.window.reset_button = tk.Button(
            frame, text="Reset", command=self.reset)
        self.window.reset_button.grid(column=0, row=0, padx=padx)
        self.window.reset_button.config(bg=bg_color)
        self.window.reset_button.config(fg=fg_color)

        self.minute_var = tk.StringVar()
        self.window.per_minute_text = tk.Label(
            frame, textvariable=self.minute_var)
        self.window.per_minute_text.grid(column=1, row=0)
        self.window.per_minute_text.config(bg=bg_color)
        self.window.per_minute_text.config(fg=fg_color)

        self.five_minute_var = tk.StringVar()
        self.window.five_minute_text = tk.Label(
            frame, textvariable=self.five_minute_var)
        self.window.five_minute_text.grid(column=2, row=0)
        self.window.five_minute_text.config(bg=bg_color)
        self.window.five_minute_text.config(fg=fg_color)

        self.hour_var = tk.StringVar()
        self.window.per_hour_text = tk.Label(frame, textvariable=self.hour_var)
        self.window.per_hour_text.grid(column=3, row=0)
        self.window.per_hour_text.config(bg=bg_color)
        self.window.per_hour_text.config(fg=fg_color)

        self.window.quit_button = tk.Button(
            frame, text="Quit", command=self.quit)
        self.window.quit_button.grid(column=4, row=0, padx=padx)
        self.window.quit_button.config(bg=bg_color)
        self.window.quit_button.config(fg=fg_color)

        self.reset()

        self.window.after(0, self.event_loop)

        self.window.mainloop()

    def quit(self):
        exit(0)

    def reset(self):
        self.data = list()
        self.minute_var.set("Last minute: 0.00%")
        self.five_minute_var.set("Last 5: 0.00%")
        self.hour_var.set("Last hour: 0.00%")

    def event_loop(self):

        # if self.cycles == 0:
        self.track_exp()

        self.calc_values()

        # self.cycles = (self.cycles+1) % 5

        self.window.after(1000, self.event_loop)

    def recognize_text(self, image):

        text = pytesseract.image_to_string(image)

        return re.sub(self.REGEX_PATTERN, '', text)

    def get_exp(self):

        x, y, w, h = self.x_offset, self.y_offset, self.width, self.height
        img = ImageGrab.grab(
            bbox=(x, y, x+w, y+h))
        img = cv2.cvtColor(np.array(img), cv2.COLOR_BGR2GRAY)

        enhanced_pic = cv2.resize(img, (w * 4, h * 4))
        exp = self.recognize_text(enhanced_pic)

        if not exp.isnumeric():
            raise Exception("Could not recognize numeric EXP")

        exp = int(exp) / 10000

        if exp > 100 or exp < 0:
            raise Exception("Inaccurate EXP reading")
        
        return exp

    def track_exp(self):
        try:

            now = datetime.now()
            exp = self.get_exp()

            # shitty way to assume level up
            if len(self.data) > 0 and exp < 30 and self.data[-1]['exp'] > 70:
                self.level_diff += 1
                print("Assuming level up")

            self.data.append({'timestamp': now, 'exp': exp, 'level': self.level_diff})
        except Exception as err:
            print(err)

    def get_filtered_diff(self, df: pd.DataFrame, column='exp'):

        filtered_df = df[(np.abs(stats.zscore(df[column])) < 3)]

        if len(filtered_df) == 0:
            return "NaN"
        
        start, end = filtered_df[column].iloc[[0, -1]]
        start_level, end_level = filtered_df['level'].iloc[[0, -1]]

        level_diff = end_level - start_level

        return round(end + level_diff * 100 - start, 4)

    def calc_values(self):

        if len(self.data) == 0:
            return


        df = pd.DataFrame(self.data)
        df.set_index('timestamp', inplace=True)

        now = datetime.now()
        last_minute = df.between_time(
            (now - timedelta(minutes=1)).time(), now.time())
        last_five = df.between_time(
            (now - timedelta(minutes=5)).time(), now.time())
        last_hour = df.between_time(
            (now - timedelta(hours=1)).time(), now.time())

        minute_exp = self.get_filtered_diff(last_minute)
        five_exp = self.get_filtered_diff(last_five)
        hour_exp = self.get_filtered_diff(last_hour)

        self.minute_var.set("Last minute: " + str(minute_exp) + "%")
        self.five_minute_var.set("Last Five: " + str(five_exp) + "%")
        self.hour_var.set("Last hour: " + str(hour_exp) + "%")


ExpTracker()
