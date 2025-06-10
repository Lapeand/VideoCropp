import tkinter as tk
from tkinter import filedialog, messagebox
from moviepy.editor import VideoFileClip
import os
import threading
import numpy as np

def extract_frames_moviepy(video_path, output_folder, fps_interval, interval_mode, second_mode, clear_folder):
    if clear_folder and len(os.listdir(output_folder)) > 0:
        for item in os.listdir(output_folder):
            item_path = os.path.join(output_folder, item)
            if os.path.isfile(item_path):
                os.remove(item_path)
        start_index = 0
    else:
        existing_files = [f for f in os.listdir(output_folder) if f.startswith("frame_") and f.endswith(".jpg")]
        indices = [int(f[6:10]) for f in existing_files if f[6:10].isdigit()]
        start_index = max(indices) + 1 if indices else 0

    clip = VideoFileClip(video_path)
    duration = clip.duration

    if second_mode:
        times = list(range(0, int(duration)))  # каждая секунда
    elif interval_mode:
        times = list(range(0, int(duration), 60))  # каждая минута
        if duration - times[-1] >= 30:
            times.append(int(duration))
    else:
        step = float(fps_interval)
        times = np.arange(0, duration, step)

    for i, t in enumerate(times):
        frame_path = os.path.join(output_folder, f"frame_{i + start_index:04d}.jpg")
        clip.save_frame(frame_path, t)
        print(f"Сохранён кадр {i + start_index} в {t:.2f} сек: {frame_path}")

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
    clear_folder = clear_folder_var.get()

    if not video_path or not output_folder:
        messagebox.showerror("Ошибка", "Укажите путь к видео и/или папке для сохранения.")
        return

    try:
        if not (interval_mode or second_mode):
            interval_text = frames_count_var.get()
            fps_interval = float(interval_text)
        else:
            fps_interval = 0.0
        threading.Thread(
            target=extract_frames_moviepy,
            args=(video_path, output_folder, fps_interval, interval_mode, second_mode, clear_folder),
            daemon=True
        ).start()
    except Exception as e:
        messagebox.showerror("Ошибка", str(e))

# -------------------- GUI ---------------------------------
root = tk.Tk()
root.title("Извлечение кадров из видео")
root.geometry("550x400")

video_path_var = tk.StringVar()
folder_path_var = tk.StringVar()
frames_count_var = tk.StringVar(value="0.666")  # default: 1 кадр / 1.5 сек
duration_var = tk.StringVar(value="—")
interval_mode_var = tk.BooleanVar(value=False)
second_mode_var = tk.BooleanVar(value=False)
clear_folder_var = tk.BooleanVar(value=True)


tk.Label(root, text="Выберите видео:").pack(pady=5)
tk.Entry(root, textvariable=video_path_var, width=60).pack()
tk.Button(root, text="Обзор...", command=select_video).pack(pady=2)

tk.Label(root, text="Длительность видео:").pack()
tk.Label(root, textvariable=duration_var, font=("Arial", 10, "bold")).pack()

tk.Label(root, text="Выберите папку для кадров:").pack(pady=5)
tk.Entry(root, textvariable=folder_path_var, width=60).pack()
tk.Button(root, text="Обзор...", command=select_folder).pack(pady=2)

tk.Label(root, text="Выбор интервала между кадрами (сек):").pack(pady=5)
frame = tk.Frame(root)
frame.pack()

# Новый список интервалов между кадрами
fps_options = ["0.666", "1", "2", "3", "4", "5", "10", "15", "20", "25", "30"]
menu = tk.OptionMenu(frame, frames_count_var, *fps_options)
menu.pack(side="left")

def toggle_optionmenu():
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

footer_frame = tk.Frame(root)
footer_frame.pack(pady=10)

chk_clear = tk.Checkbutton(footer_frame, text="Очистить папку", variable=clear_folder_var)
chk_clear.pack(side="left", padx=10)

tk.Button(footer_frame, text="Обработать видео", command=start_process).pack(side="left")

root.mainloop()