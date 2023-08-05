# import libraries
import os
import random
import threading
from tkinter import *
from tkinter import filedialog

import pygame
from pygame import mixer

import config


# Create a GUI window
root = Tk()
root.title("Music Player")
root.geometry("920x400+290+85")
root.configure(background="#0f1a2b")
root.resizable(False, False)
music_thread = None
mixer.init()
pygame.init()
stop = False
current_index = 0
message_counter = 0
announcement_index = 0


is_playlist = False
is_announcement = False
ABSOLUTE_PATH = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.path.join(ABSOLUTE_PATH, "config.py")


# Create a function to open a file




##########################################################################################
#ADD
def addmusic(path):
    global is_playlist
    try:
        Playlist.delete(0, END)
        is_playlist = True

        if path:
            os.chdir(path)
            songs = os.listdir(path)

            for song in songs:
                if song.endswith(".mp3"):
                    Playlist.insert(END, song)
    except FileNotFoundError:
            is_playlist = False
            Playlist.insert(END, "Папка не найдена")

def addannouncement(path):
    global is_announcement
    try:
        Announcement_List.delete(0, END)
        is_announcement = True
        if path:
            os.chdir(path)
            songs = os.listdir(path)

            for song in songs:
                if song.endswith(".mp3"):
                    Announcement_List.insert(END, song)
    except FileNotFoundError:
            is_announcement = False
            Announcement_List.insert(END, "Папка не найдена")
##########################################################################################
#VOLUME

def change_volume(volume):
    if Playlist.curselection():
        volume = volume / 100  # Преобразование значения громкости из диапазона 0-100 в диапазон 0-1
        mixer.music.set_volume(volume)

def on_volume_change(event):
    volume = volume_scale.get()
    change_volume(volume)

def change_volume_ann(volume):
    if Announcement_List.curselection():
        volume = volume / 100  # Преобразование значения громкости из диапазона 0-100 в диапазон 0-1
        mixer.music.set_volume(volume)

def on_volume_change_ann(event):
    volume = volume_scale_ann.get()
    change_volume_ann(volume)

##########################################################################################
def playaudiomessage(message_path):
    global message_counter
    if message_path:
        Announcement_List.selection_clear(0, END)

            # Выделяем текущий трек
        Announcement_List.selection_set(announcement_index)
        volume= volume_scale_ann.get()
        change_volume_ann(volume)
        mixer.music.load(message_path)
        mixer.music.play()
        current_song.set("Объявление: " + os.path.basename(message_path))
       
        message_counter = 0
        while pygame.mixer.music.get_busy():
            pygame.event.wait()

def play_selected_message(event):
    global message_counter
    global announcement_index
    message_counter = config.ANNOUNCEMENT_SONG_NUMBER
    announcement_index = Announcement_List.curselection()[0]
    mixer.music.stop()

def play_audio_playlist(message_path):
    global message_counter
    if message_path:
        Playlist.selection_clear(0, END)
    
            # Выделяем текущий трек
        Playlist.selection_set(current_index)
        volume= volume_scale.get()
        change_volume(volume)
        mixer.music.load(message_path)
        mixer.music.play()
        current_song.set("Объявление: " + os.path.basename(message_path))
        
        while pygame.mixer.music.get_busy():
                pygame.event.wait()


def play_selected_playlist(event):
    global message_counter
    global current_index
    message_counter -= 1
    current_index = Playlist.curselection()[0] -1
    mixer.music.stop()
###########################################################################################

def select_message_folder():
    folder_path = filedialog.askdirectory()
    if folder_path:
        config.MESSAGE_FOLDER = folder_path
        with open(CONFIG_PATH, "w") as config_file:
            config_file.write(f"MESSAGE_FOLDER = '{folder_path}'\n")
            config_file.write(f"ANNOUNCEMENT_SONG_NUMBER = {config.ANNOUNCEMENT_SONG_NUMBER}\n")
            config_file.write(f"TEST_MODE = {config.TEST_MODE}\n")
            config_file.write(f"PLAYLIST_FOLDER = '{config.PLAYLIST_FOLDER}'\n")
        addannouncement(folder_path)


def select_playlist_folder():
    folder_path = filedialog.askdirectory()
    if folder_path:
        config.PLAYLIST_FOLDER = folder_path
        with open(CONFIG_PATH, "w") as config_file:
            config_file.write(f"PLAYLIST_FOLDER = '{folder_path}'\n")
            config_file.write(f"ANNOUNCEMENT_SONG_NUMBER = {config.ANNOUNCEMENT_SONG_NUMBER}\n")
            config_file.write(f"TEST_MODE = {config.TEST_MODE}\n")
            config_file.write(f"MESSAGE_FOLDER = '{config.MESSAGE_FOLDER}'\n")
        addmusic(folder_path)
##############################################################################################

def listboxshufle(listbox: Listbox):
    somelist = list(listbox.get(0, END))
    random.shuffle(somelist)
    listbox.delete(0, END)
    for file in somelist:
        listbox.insert(END, file)


###############################################################################################
#Start
def playmusic():
    global stop
    global current_index
    global announcement_index
    global is_playlist
    global is_announcement
    global play_state
    global message_counter
    
    announcements_song_number = config.ANNOUNCEMENT_SONG_NUMBER
    stop = False
    message_counter = 0
    
    
    if not Playlist.get(0, END):
        addmusic(config.PLAYLIST_FOLDER)
    if not Announcement_List.get(0, END):
        addannouncement(config.MESSAGE_FOLDER)
    ann_list = list(Announcement_List.get(0, END))
    
    while True and is_playlist and is_announcement:
        if stop:
            break
        
        
        current_index = 0
        listboxshufle(Playlist)
        playlist = list(Playlist.get(0, END))
        if not playlist:
            Playlist.insert(0, 'в папке нет музыки')
            break
        if not ann_list:
            Announcement_List.insert(0, 'в папке нет сообщений')
            break
        
        mixer.music.set_endevent(pygame.USEREVENT)

        while current_index < len(playlist):
            if stop:
                break
            
            if (
                message_counter >= announcements_song_number
                and announcements_song_number > 0
            ):
                if announcement_index >= len(ann_list):
                    listboxshufle(Announcement_List)
                    ann_list = list(Announcement_List.get(0, END))
                    announcement_index = 0

                message_path = os.path.join(
                    config.MESSAGE_FOLDER, ann_list[announcement_index]
                )

                playaudiomessage(message_path)
                announcement_index += 1
            if stop:
                break
            if play_state.get() != 'Играет':
                play_state.set('Играет')
            
            music_path = os.path.join(config.PLAYLIST_FOLDER, playlist[current_index])

            play_audio_playlist(music_path)
           
            # Ожидание завершения воспроизведения текущей музыки

            message_counter += 1
            current_index += 1
            
            # Ожидание завершения воспроизведения текущей музыки
            
        # Ожидание завершения воспроизведения последней музыки
        while pygame.mixer.music.get_busy():
            pygame.event.wait()

        mixer.music.set_endevent()  # Сбрасываем callback-функцию


def play_music_in_thread():
    global music_thread
    if music_thread:
        stopped()  # Останавлив
    music_thread = threading.Thread(target=playmusic)
    music_thread.start()

def continue_music():
    global play_state
    if play_state.get() == 'Пауза':
        play_state.set('Играет')
    mixer.music.unpause()

def pause_music():
    global play_state
    if play_state.get() == 'Играет':
        play_state.set('Пауза')
    mixer.music.pause()
###################################################################
#CLOSE
def stopped():
    global stop
    global music_thread
    global play_state
    play_state.set("Стоп")
    stop = True
    mixer.music.stop()
    mixer.music.unload()
    if music_thread:
        music_thread.join()  # Ждем завершения потока не более 5 секунд
        

# Дожидаемся завершения потока

def on_closing():
    global music_thread
    if music_thread:
        stopped()  # Останавливаем музыку перед выходом
    root.destroy()

###########################################################################
def play_next_song():
    global current_index
    global message_counter
    if not config.TEST_MODE:
        message_counter -= 1
    if current_index < Playlist.size():
        mixer.music.stop()
    else:
        current_index -= 1
        mixer.music.stop()
    


def play_previous_song():
    global message_counter
    global current_index
    message_counter -= 1
    if current_index > 1:
        print(current_index)
        mixer.music.stop()
        current_index -= 2
    else:
        mixer.music.stop()
        current_index = 0
#############################################################################

# icon

root.title("Управление музыкой")
root.protocol("WM_DELETE_WINDOW", on_closing)

image_icon = PhotoImage(file="images/logo.png")
root.iconphoto(False, image_icon)

# Label
Menu = PhotoImage(file="images/menu.png")
Label(root, image=Menu, bg="#0f1a2b").pack(padx=10, pady=50, side=RIGHT)


###########################################################################
current_song = StringVar()
current_song_label = Label(
    root, textvariable=current_song, bg="#0f1a2b", fg="white", font=("Arial", 12)
)
current_song_label.place(x=330, y=350)

############################################################################
play_state = StringVar()
play_state_lable = Label(
    root, textvariable=play_state, bg="#0f1a2b", fg="white", font=("Arial", 12)
)
play_state_lable.place(x=330, y=20)
play_state.set("Стоп")
############################################################################
Button(
    root,
    text="Папка музыки",
    width=15,
    height=2,
    font=("arial", 10, "bold"),
    fg="Black",
    bg="#21b3de",
    command=select_playlist_folder,
).place(x=330, y=50)

ButtonMessageFolder = Button(
    root,
    text="Папка объявлений",
    width=15,
    height=2,
    font=("arial", 10, "bold"),
    fg="Black",
    bg="#21b3de",
    command=select_message_folder,
)
ButtonMessageFolder.place(x=735, y=50)

##########################################################################

Frame_Music = Frame(root, bd=2, relief=RIDGE)
Frame_Music.place(x=330, y=100, width=570, height=250)

# Определяем область для Song List
Frame_Song_List = Frame(Frame_Music)
Frame_Song_List.pack(side=LEFT, fill=BOTH, expand=True)  # Используем параметр expand=True
Frame_Music.columnconfigure(0, weight=1)  # Устанавливаем вес для первой колонки

# Определяем область для Announcement List и делаем ее шире
Frame_Announcement_List = Frame(Frame_Music)
Frame_Announcement_List.pack(side=LEFT, fill=BOTH, expand=True)  # Используем параметр expand=True
Frame_Music.columnconfigure(1, weight=2, )  # Устанавливаем вес для второй колонки

Scroll = Scrollbar(Frame_Music)
Playlist = Listbox(
    Frame_Song_List,
    width=50,
    font=("Aloja", 10),
    bg="#000000",
    fg="white",
    selectbackground="lightblue",
    cursor="hand2",
    bd=0,
    yscrollcommand=Scroll.set,
)
Playlist.pack(side=LEFT, fill=BOTH)
Playlist.bind("<Double-Button-1>", play_selected_playlist)
Scroll.config(command=Playlist.yview)
Scroll.pack(side=RIGHT, fill=Y)

Announcement_List = Listbox(
    Frame_Announcement_List,
    width=50,
    font=("Aloja", 10),
    bg="#000000",
    fg="white",
    selectbackground="lightblue",
    cursor="hand2",
    bd=0,
    yscrollcommand=Scroll.set,
)
Announcement_List.pack(side=LEFT, fill=BOTH)
Announcement_List.bind("<Double-Button-1>", play_selected_message)








#####################################################################################################################
#### remote botton
ButtonPlay = PhotoImage(file="images/play.png")
play_button = Button(
    root, image=ButtonPlay, bg="#0f1a2b", bd=0, command=play_music_in_thread
)
play_button.place(x=80, y=150)
play_button.config(highlightthickness=2, highlightbackground="white")

ButtonStop = PhotoImage(file="images/stop.png")
stop_button = Button(
    root, image=ButtonStop, bg="#0f1a2b", bd=0, command=stopped
)
stop_button.place(x=150, y=150)
stop_button.config(highlightthickness=2, highlightbackground="white")

ButtonResume = PhotoImage(file="images/resume.png")
resume_button = Button(
    root, image=ButtonResume, bg="#0f1a2b", bd=0, command=continue_music
)
resume_button.place(x=80, y=225)
resume_button.config(highlightthickness=2, highlightbackground="white")

ButtonPause = PhotoImage(file="images/pause.png")
pause_button = Button(
    root, image=ButtonPause, bg="#0f1a2b", bd=0, command=pause_music
)
pause_button.place(x=150, y=225)
pause_button.config(highlightthickness=2, highlightbackground="white")

ButtonPrevious = PhotoImage(file="images/previous.png")
previous_button = Button(
    root, image=ButtonPrevious, bg="#0f1a2b", bd=0, command=play_previous_song
)
previous_button.place(x=10, y=225)
previous_button.config(highlightthickness=2, highlightbackground="white")

ButtonNext = PhotoImage(file="images/next.png")
next_button = Button(
    root, image=ButtonNext, bg="#0f1a2b", bd=0, command=play_next_song
)
next_button.place(x=220, y=225)
next_button.config(highlightthickness=2, highlightbackground="white")

#########################################################################################################################
#VOLUME BUTTON
volume_scale = Scale(
    root,
    from_=0,
    to=100,
    orient=HORIZONTAL,
    label="Громкость музыки",
    command=on_volume_change,
    length=180,       # Длина ползунка в пикселях
    troughcolor="#333333",  # Цвет фона ползунка
    sliderrelief="flat",    # Убирает рамку вокруг ползунка
    sliderlength=10,        # Длина ползунка в пикселях
)
volume_scale.set(50)  # Установите начальное значение громкости (от 0 до 100)
volume_scale.place(x = 10, y = 10)#расположение в пространстве

volume_scale_ann = Scale(
    root,
    from_=0,
    to=100,
    orient=HORIZONTAL,
    label="Громкость объявлений",
    command=on_volume_change_ann,
    length=180,       # Длина ползунка в пикселях
    troughcolor="#333333",  # Цвет фона ползунка
    sliderrelief="flat",    # Убирает рамку вокруг ползунка
    sliderlength=10,        # Длина ползунка в пикселях
)

volume_scale_ann.set(50)  # Установите начальное значение громкости (от 0 до 100)
volume_scale_ann.place(x = 10, y = 80)#расположение в пространстве



################################################################################################################################


#settings







def open_settings_window():
    settings_window = Toplevel(root)
    settings_window.title("Настройки")
    settings_window.geometry("300x200")  # Немного увеличил высоту для флажка

    Label(settings_window, text="Настройки", font=("Arial", 14)).pack(pady=10)

    message_counter_label = Label(settings_window, text="Количество песен до объявления:")
    message_counter_label.pack()

    message_counter_entry = Entry(settings_window)
    message_counter_entry.pack()
    message_counter_entry.insert(0, config.ANNOUNCEMENT_SONG_NUMBER)

    test_mode_var = IntVar()
    test_mode_var.set(config.TEST_MODE)  # Устанавливаем значение переменной в зависимости от конфигурации
    test_mode_checkbox = Checkbutton(settings_window, text="Тестовый режим", variable=test_mode_var)
    test_mode_checkbox.pack()

    buttons_frame = Frame(settings_window)
    buttons_frame.pack(pady=10, padx=10, side=BOTTOM)

    def save_settings():
        announcements_song_number = int(message_counter_entry.get())
        config.ANNOUNCEMENT_SONG_NUMBER = announcements_song_number
        config.TEST_MODE = test_mode_var.get()
        with open(CONFIG_PATH, "w") as config_file:
            config_file.write(
                f"ANNOUNCEMENT_SONG_NUMBER = {announcements_song_number}\n"
            )
            config_file.write(f"MESSAGE_FOLDER = '{config.MESSAGE_FOLDER}'\n")
            config_file.write(f"TEST_MODE = {test_mode_var.get()}\n")  # Сохраняем значение тестового режима
            config_file.write(f"PLAYLIST_FOLDER = '{config.PLAYLIST_FOLDER}'\n")
        settings_window.destroy()

    save_button = Button(buttons_frame, text="Сохранить", command=save_settings)
    save_button.pack(side=LEFT, padx=5)

    cancel_button = Button(
        buttons_frame, text="Отмена", command=settings_window.destroy
    )
    cancel_button.pack(side=LEFT, padx=5)

# Создаем кнопку "Настройки" на главном окне
settings_button = Button(
    root,
    text="Настройки",
    command=open_settings_window,
    bg="#5F9EA0",
    fg="black",
    bd=0,
    activebackground="#00CED1",
    highlightthickness=0,
)
settings_button.place(x=800, y=10)
########################################################################################################################
# Execute Tkinter
root.mainloop()
