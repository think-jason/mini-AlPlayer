import Tkinter as tk
import tkFileDialog
import pygame

from PIL import Image, ImageTk

import os
import sys
from datetime import timedelta
import random
from mutagen.mp3 import MP3
from ttk import Progressbar, Notebook, Frame, Scrollbar,Style
reload(sys)
sys.setdefaultencoding('utf8')

class MusicPlayer:
    def __init__(self, root):
        self.root = root
        self.root.title("Music Player")
        self.root.geometry("400x600")
        
        iconfile="D:\\entertainment\\pic\\aiIcon.gif"
        iconfile = iconfile.encode('gb2312')
        self.icon = tk.PhotoImage(file=iconfile)
        self.root.tk.call('wm', 'iconphoto', self.root._w, self.icon)

        
        pygame.init()
        pygame.mixer.init()
        
        self.track = tk.StringVar()
        self.status = tk.StringVar()
        self.song_length = 0
        self.paused_time = 0
        self.playing = False
        self._update_progress_id = None
        self.main_path = None
        self.volume = 0.7
        self.playlist = []
        self.current_index = None
        
        
        self.lyrics = []
        self.current_lyric_index = 0

        # Local tab for opening local songs
        tab_frame = Notebook(self.root)
        tab_frame.pack(fill=tk.BOTH, expand=True)
        
        self.local_tab = Frame(tab_frame)
        self.lrc_tab = Frame(tab_frame)
        
        tab_frame.add(self.lrc_tab, text="LRC List")
        tab_frame.add(self.local_tab, text="Local")
        self.tab_frame = tab_frame

        
        # Open songs Listbox with scrollbar
        listbox_frame = Frame(self.local_tab)
        listbox_frame.place(relheight=0.8, relwidth=1.0)  # 80% height, 100% width
              
        self.song_listbox = tk.Listbox(listbox_frame, selectmode=tk.SINGLE, font=("times new roman", 10), width=30)
        self.song_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        
        scrollbar = Scrollbar(listbox_frame, orient=tk.VERTICAL)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        scrollbar.config(command=self.song_listbox.yview)
        self.song_listbox.config(yscrollcommand=scrollbar.set)

        # bind click on playlist item
        self.song_listbox.bind("<<ListboxSelect>>", self.play_song)
       
        # Track frame for song label and status label
        track_frame = tk.Frame(self.lrc_tab, bg="sky blue", bd=5, relief=tk.GROOVE)
        track_frame.place(relx=0, rely=0.8, relwidth=1.0, relheight=0.1)  # 10% height, 100% width
        
        
      

        songtrack = tk.Label(track_frame, textvariable=self.track, width=50, font=("times new roman", 10, "bold"), bg="sky blue", fg="white",anchor="w")
        songtrack.grid(row=0, column=0, padx=2, pady=5, sticky="w")  # Align to the left

        trackstatus = tk.Label(track_frame, textvariable=self.status, font=("times new roman", 10, "bold"), bg="sky blue", fg="white", anchor="w")
        trackstatus.grid(row=0, column=1, padx=(2, 20), pady=5, sticky="ew")  # Align to the left with less padding

        # Adjust column configuration to make sure both labels are visible
        track_frame.columnconfigure(0, weight=10)
        track_frame.columnconfigure(1, weight=1)

        # Progress bar and total time label frame
        progress_frame = tk.Frame(track_frame, bg="sky blue")
        progress_frame.grid(row=1, column=0, columnspan=2, padx=1, pady=1, sticky="ew")  # Span across both columns

        # current time label
        self.current_time_label = tk.Label(progress_frame, text="00:00", font=("times new roman", 10, "bold"), bg="sky blue", fg="white")
        self.current_time_label.grid(row=0, column=0, padx=(4, 0), pady=1, sticky="w")  # Align to the left

        # Progress bar
        style = Style()
        style.configure("Custom.Horizontal.TProgressbar", troughcolor="sky blue", bordercolor="sky blue", background="blue")
        self.progress = Progressbar(progress_frame, orient=tk.HORIZONTAL, length=300, mode='determinate', style="Custom.Horizontal.TProgressbar")
        self.progress.grid(row=0, column=1, padx=1, pady=1, sticky="ew")  # Expand to fill the space

        # Total time label
        self.total_time_label = tk.Label(progress_frame, text="00:00", font=("times new roman", 10, "bold"), bg="sky blue", fg="white")
        self.total_time_label.grid(row=0, column=2, padx=(2, 0), pady=1, sticky="e")  # Align to the right

        # Adjust column configuration for progress_frame to make sure it behaves properly
        progress_frame.columnconfigure(0, weight=1)
        progress_frame.columnconfigure(1, weight=3)
        progress_frame.columnconfigure(2, weight=1)
        # Song title label in LRC List tab
        self.lrc_song_title = tk.Label(self.lrc_tab, text="", font=("times new roman", 14, "bold"), bg="white", fg="black")
        #self.lrc_song_title.pack(fill=tk.X, padx=5, pady=5)
        self.lrc_song_title.place(relx=0, rely=0, relwidth=1.0, relheight=0.05)
        
        
        # Lyrics display in lrc_tab
        self.lyrics_text = tk.Text(self.lrc_tab, font=("times new roman", 12), bg="white", fg="black", state=tk.DISABLED)
        #self.lyrics_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.lyrics_text.place(relx=0, rely=0.05, relwidth=1.0, relheight=0.75)
        
        # Button frame for control buttons
        button_frame = tk.Frame(self.lrc_tab, bg="sky blue", bd=5, relief=tk.GROOVE)
        button_frame.place(relx=0, rely=0.9, relwidth=1.0, relheight=0.1)  # 10% height, 100% width
        
        self.play_pause_btn = tk.Button(button_frame, text="Play", command=self.toggle_play_pause, width=6, height=1, font=("times new roman", 10, "bold"), fg="navyblue", bg="white", state=tk.DISABLED)
        self.play_pause_btn.grid(row=0, column=0, padx=10, pady=5)
        
        self.load_btn = tk.Button(button_frame, text="Load", command=self.load_song, width=6, height=1, font=("times new roman", 10, "bold"), fg="navyblue", bg="white")
        self.load_btn.grid(row=0, column=1, padx=10, pady=5)
        
        self.song_prev_btn = tk.Button(button_frame, text="<<", command=self.prev_song, width=6, height=1, font=("times new roman", 10, "bold"), fg="navyblue", bg="white")
        self.song_prev_btn.grid(row=0, column=2, padx=10, pady=5)
        
        self.song_next_btn = tk.Button(button_frame, text=">>", command=self.next_song, width=6, height=1, font=("times new roman", 10, "bold"), fg="navyblue", bg="white")
        self.song_next_btn.grid(row=0, column=3, padx=10, pady=5)

        
        
    def load_song(self):
        self.track.set("Loading...")
        folder_path = tkFileDialog.askdirectory()
        if folder_path:
            self.main_path = folder_path
            
            for file_name in os.listdir(folder_path):
                if file_name.endswith((".mp3", ".wav")):
                    if isinstance(file_name, str):
                        file_name = unicode(file_name, 'gbk')
                    if file_name not in self.playlist:
                        self.playlist.append(file_name)
                        print("file_name = " + file_name)
                        self.song_listbox.insert(tk.END, file_name)
                    
        if self.playlist:
            self.track.set(os.path.basename(self.playlist[0]))
            #file_path = file_path.encode('gb2312')
            self.status.set("Loaded")
            self.play_pause_btn.config(state=tk.NORMAL)

    def update_progess(self):
        if pygame.mixer.music.get_busy() and self.playing:
            current_time = float(pygame.mixer.music.get_pos()) / 1000.0
            self.progress["value"] = current_time
            self._update_progress_id = self.root.after(1000, self.update_progess)
            print("update_progess:self._update_progress_i;d = " + str(self._update_progress_id))
            #remaining_time = self.song_length - current_time
            time_format = timedelta(seconds=int(current_time))
            hms = str(time_format).split('.')[0]
            self.current_time_label.config(text=hms[-5:])
        else:
            self
    
    def toggle_play_pause(self):
        if self.playing:
            self.pause_song()
        else:
            self.play_song()
            
    def play_song(self, event=None):
        if event:
            if self.playlist is None:
                print("playlist is none")
                return
            self.current_index = self.song_listbox.curselection()[0]
            print("current index = " + str(self.current_index))
        if self.current_index is None:
            self.current_index = 0
   
        self.status.set("Playing")
        
        file_path = os.path.join(self.main_path, self.playlist[int(self.current_index)])
        print("filename = " + self.playlist[int(self.current_index)])
        self.lrc_song_title.config(text=self.playlist[int(self.current_index)])
        if self.paused_time == 0:
            self.progress["value"] = 0
            #print("main_path = " + self.main_path)
            #print("current_index = " + str(self.current_index))
            self.track.set(os.path.basename(self.playlist[int(self.current_index)]))
            self.song_length = MP3(file_path).info.length
            self.progress["maximum"] = self.song_length
            pygame.mixer.music.load(file_path.encode('gbk'))
            self.song_listbox.selection_clear(0, tk.END)
            self.song_listbox.selection_set(self.current_index)
            pygame.mixer.music.play()
            
        else:
            pygame.mixer.music.unpause()
        
        self.playing = True
        self.play_pause_btn.config(text="Pause")
        pygame.mixer.music.set_volume(self.volume)
        time_format = timedelta(seconds=int(self.song_length))
        hms = str(time_format).split('.')[0]
        self.total_time_label.config(text=hms[-5:])
        self.pause_progress()
        self.load_lyrics(file_path)
        self.tab_frame.select(self.lrc_tab)  # Switch to lrc_tab when playing
        self.update_progess()
        self.update_lyrics(file_path)
        self.check_state()
        
        
    def pause_progress(self):
        try:
            if self._update_progress_id is not None:
                self.root.after_cancel(self._update_progress_id)
                self._update_progress_id = None
        except Exception as e:
            pass   
    
    def check_state(self):
        if not self.playing:
          return
        if pygame.mixer.music.get_busy():
            self.root.after(1000, self.check_state)
        else:
            self.next_song(False)
            
            
    def next_song(self, isNotAuto=True):
        if isNotAuto:
            self.stop_song()
        if self.current_index is not None:
            self.song_listbox.itemconfig(self.current_index, bg="white")
        else:
            print("current index = -1")
            self.current_index = -1
        #self.current_index = random.randint(0, len(self.playlist) - 1)
        self.current_index = (self.current_index + 1) % (len(self.playlist))
        self.song_listbox.see(self.current_index)
        self.paused_time = 0
        self.playing = True
        self.play_song()
        
    def prev_song(self, isNotAuto=True):
        if isNotAuto:
            self.stop_song()
        if self.current_index is not None:
            self.song_listbox.itemconfig(self.current_index, bg="white")
        else:
            self.curren_index = len(self.playlist)
        #self.current_index = random.randint(0, len(self.playlist) - 1)
        if self.current_index == 0:
            self.current_index = len(self.playlist)
        self.current_index = (self.current_index - 1) % (len(self.playlist))
        self.song_listbox.see(self.current_index)
        self.paused_time = 0
        self.playing = True
        self.play_song()
             
    def pause_song(self):
        self.status.set("Paused")
        self.playing = False
        self.update_progess()
        pygame.mixer.music.pause()
        self.pause_progress()
        self.paused_time = float(pygame.mixer.music.get_pos()) / 1000.0
        self.play_pause_btn.config(text="Play")
        
    def stop_song(self):
        self.status.set("Stopped")
        pygame.mixer.music.stop()
        self.progress["value"] = 0
        self.track.set("")
        self.init_state()
        self.pause_progress()
    
    def init_state(self):
        self.song_length = 0
        self.paused_time = 0
        self.volume = 0.7
        self.playing = False
        
    def volume_up(self):
        if self.volume < 1:
            self.volume += 0.1
            pygame.mixer.music.set_volume(self.volume)
        
        
    def volume_down(self):
        if self.volume > 0:
            self.volume -= 0.1
            pygame.mixer.music.set_volume(self.volume)
    
    def load_lyrics(self, song_path):          
        lrc_path = song_path.rsplit(".", 1)[0] + ".lrc"
        self.lyrics = []
        if os.path.exists(lrc_path):
            with open(lrc_path, "r") as file:
                self.lyrics = self.parse_lrc(file.readlines())
        self.current_lyric_index = 0

    def parse_lrc(self, lines):
        lyrics = []
        for line in lines:
            if line.startswith("["):
                time_part, lyrics_part = line.strip().split("]", 1)
                time_part = time_part[1:]
                minutes, seconds = time_part.split(":")
                total_seconds = int(minutes) * 60 + float(seconds)
                lyrics.append((total_seconds, lyrics_part))
        return lyrics
            
    def update_lyrics(self, file_path):
        if not self.playing:
            return
        lrc_path = file_path.rsplit(".", 1)[0] + ".lrc"
        if not os.path.exists(lrc_path):
            return
        current_time = pygame.mixer.music.get_pos() / 1000.0
        while (self.current_lyric_index < len(self.lyrics) - 1 and
               current_time >= self.lyrics[self.current_lyric_index + 1][0]):
            self.current_lyric_index += 1
        
        # Get the start and end indices for displaying lyrics
        start_index = max(0, self.current_lyric_index - 4)
        end_index = min(len(self.lyrics), self.current_lyric_index + 5)

        # Clear and update lyrics text
        self.lyrics_text.config(state=tk.NORMAL)
        self.lyrics_text.delete('1.0', tk.END)
        
        for i in range(start_index, end_index):
            lyric_time, lyric_text = self.lyrics[i]
            if i == self.current_lyric_index:
                self.lyrics_text.insert(tk.END, lyric_text + "\n", "current_lyric")
            else:
                self.lyrics_text.insert(tk.END, lyric_text + "\n")

        self.lyrics_text.tag_config("current_lyric", background="red", foreground="white", font=("times new roman", 10, "bold"))
        self.lyrics_text.config(state=tk.DISABLED)

        if current_time < self.song_length:
            self.root.after(1000, self.update_lyrics(file_path))
    


if __name__ == "__main__":
    root = tk.Tk()
    app = MusicPlayer(root)
    root.mainloop()
