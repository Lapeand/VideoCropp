import tkinter as tk
from tkinter import filedialog, messagebox
import numpy as np
from moviepy.editor import VideoFileClip
import os
import threading

def extract_frames_moviepy(video_path, output_folder, frames_count, interval_mode, second_mode):
    if len(os.listdir(output_folder)) > 0:
        for item in os.listdir(output_folder):
            item_path = os.path.join(output_folder, item)
            if os.path.isfile(item_path):
                os.remove(item_path)

    clip = VideoFileClip(video_path)
    duration = clip.duration

    if second_mode:
        times = list(range(0, int(duration)))  # каждый кадр раз в секунду
    elif interval_mode:
        times = list(range(0, int(duration), 60))  # каждую минуту
        if duration - times[-1] >= 30:
            times.append(int(duration))
    else:
        times = np.linspace(0, duration, num=frames_count, endpoint=False)

    for i, t in enumerate(times):
        frame_path = os.path.join(output_folder, f"frame_{i:04d}.jpg")
        clip.save_frame(frame_path, t)
        print(f"Сохранён кадр {i} в {t:.2f} сек: {frame_path}")

    clip.close()
    messagebox.showinfo("Готово", f"Сохранено {len(times)} кадров в папку:\n{output_folder}")

def select_video():
    path = filedialog.askopenfilename(title="Выберите видео", filetypes=[("MP4 файлы", "*.mp4"), ("Все файлы", "*.*")])
    if path:
        video_path_var.set(path)
        try:
            duration = VideoFileClip(path).duration
            duration_var.set(f"{duration:.2f} секунд")
        except Exception as e:
            duration_var.set("Ошибка при чтении")
            messagebox.showerror("Ошибка", str(e))

def select_folder():
    path = filedialog.askdirectory(title="Выберите папку для сохранения кадров")
    if path:
        folder_path_var.set(path)

def start_process():
    video_path = video_path_var.get()
    output_folder = folder_path_var.get()
    interval_mode = interval_mode_var.get()
    second_mode = second_mode_var.get()

    if not video_path or not output_folder:
        messagebox.showerror("Ошибка", "Укажите путь к видео и/или папке для сохранения.")
        return

    try:
        if interval_mode or second_mode:
            frames_count = 0
        else:
            frames_count = int(frames_count_var.get())
        threading.Thread(
            target=extract_frames_moviepy,
            args=(video_path, output_folder, frames_count, interval_mode, second_mode),
            daemon=True
        ).start()
    except Exception as e:
        messagebox.showerror("Ошибка", str(e))

# --------------------Форма---------------------------------
root = tk.Tk()
root.title("Извлечение кадров из видео")
root.geometry("550x390")

video_path_var = tk.StringVar()
folder_path_var = tk.StringVar()
frames_count_var = tk.StringVar(value="Выбрать -->>")
duration_var = tk.StringVar(value="—")
interval_mode_var = tk.BooleanVar(value=False)
second_mode_var = tk.BooleanVar(value=False)

tk.Label(root, text="Выберите видео:").pack(pady=5)
tk.Entry(root, textvariable=video_path_var, width=60).pack()
tk.Button(root, text="Обзор...", command=select_video).pack(pady=2)

tk.Label(root, text="Длительность видео:").pack()
tk.Label(root, textvariable=duration_var, font=("Arial", 10, "bold")).pack()

tk.Label(root, text="Выберите папку для кадров:").pack(pady=5)
tk.Entry(root, textvariable=folder_path_var, width=60).pack()
tk.Button(root, text="Обзор...", command=select_folder).pack(pady=2)

tk.Label(root, text="Сколько кадров извлечь:").pack(pady=5)
frame = tk.Frame(root)
frame.pack()
options = ["1", "10", "20", "50", "100", "150", "300"]
menu = tk.OptionMenu(frame, frames_count_var, *options)
menu.pack(side="left")

def toggle_optionmenu():
    # если выбран "каждую секунду" — заблокировать остальное
    if second_mode_var.get():
        interval_mode_var.set(False)
        menu.configure(state="disabled")
        chk_minute.configure(state="disabled")
    elif interval_mode_var.get():
        second_mode_var.set(False)
        menu.configure(state="disabled")
        chk_second.configure(state="disabled")
    else:
        menu.configure(state="normal")
        chk_minute.configure(state="normal")
        chk_second.configure(state="normal")


chk_second = tk.Checkbutton(frame, text="Каждую секунду", variable=second_mode_var, command=toggle_optionmenu)
chk_second.pack(side="left", padx=10)

chk_minute = tk.Checkbutton(frame, text="Каждую минуту", variable=interval_mode_var, command=toggle_optionmenu)
chk_minute.pack(side="left", padx=10)


tk.Button(root, text="Обработать видео", command=start_process).pack(pady=15)

root.mainloop()