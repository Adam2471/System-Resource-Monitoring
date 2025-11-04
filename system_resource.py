# -----------------------------------------------------------------------------
# System Resource Monitoring
# Author : Adam Mubarok
# NIM    : 312310301
# Date   : 2025-11-05
# License: MIT License (see LICENSE file)
# Description:
#   A simple GUI app to monitor CPU, RAM, Disk and Network usage. 
# -----------------------------------------------------------------------------

import tkinter as tk
from tkinter import ttk, messagebox
import psutil
import time
import platform
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from PIL import Image, ImageTk, ImageDraw
import datetime
import os

# === Fungsi Membuat Bingkai Foto Bulat ===
def make_circle_image(path, size=(120, 120)):
    img = Image.open(path).resize(size, Image.LANCZOS).convert("RGBA")
    mask = Image.new("L", size, 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse((0, 0, size[0], size[1]), fill=255)
    img.putalpha(mask)
    return ImageTk.PhotoImage(img)

# === Halaman Utama ===
class ResourceMonitorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("System Resource Monitoring")
        self.root.geometry("800x500")
        self.root.config(bg="white")

        # === Tambahkan Icon Aplikasi ===
        try:
            self.root.iconbitmap("logo.ico")
        except:
            print("⚠️ File icon (logo.ico) tidak ditemukan, menggunakan icon default.")

        # Judul Aplikasi
        title_label = tk.Label(root, text="System Resource Monitor", font=("Inter", 18, "bold"), bg="white")
        title_label.pack(pady=10)

        # Frame utama
        self.frame = tk.Frame(root, bg="white")
        self.frame.pack(pady=10)

        # Label dan Progressbar
        self.cpu_label, self.cpu_bar = self.create_progress("CPU Usage")
        self.ram_label, self.ram_bar = self.create_progress("RAM Usage")
        self.disk_label, self.disk_bar = self.create_progress("Disk Usage")

        # Network
        self.net_label = tk.Label(self.frame, text="Network Usage", font=("Inter", 12, "bold"), bg="white")
        self.net_label.pack(pady=(10, 0))
        self.net_frame = tk.Frame(self.frame, bg="white")
        self.net_frame.pack(fill="x", padx=30)

        self.upload_label = tk.Label(self.net_frame, text="Upload:", bg="white", anchor="w")
        self.upload_label.grid(row=0, column=0, sticky="w")
        self.upload_bar = ttk.Progressbar(self.net_frame, length=180)
        self.upload_bar.grid(row=0, column=1, padx=5)

        self.download_label = tk.Label(self.net_frame, text="Download:", bg="white", anchor="w")
        self.download_label.grid(row=0, column=2, sticky="w", padx=(30, 0))
        self.download_bar = ttk.Progressbar(self.net_frame, length=180)
        self.download_bar.grid(row=0, column=3, padx=5)

        # Tombol di bawah
        button_frame = tk.Frame(root, bg="white")
        button_frame.pack(pady=15)

        ttk.Button(button_frame, text="📊 Lihat Grafik", command=self.show_graphs).grid(row=0, column=0, padx=10)
        ttk.Button(button_frame, text="🧩 System Info", command=self.show_system_info).grid(row=0, column=1, padx=10)
        ttk.Button(button_frame, text="ℹ️ About", command=self.show_about).grid(row=0, column=2, padx=10)
        ttk.Button(button_frame, text="❌ Keluar", command=self.confirm_exit).grid(row=0, column=3, padx=10)

        # Footer
        footer = tk.Label(root, text="© 2025 System Resource Monitoring v1.1 | 312310301 All Rights Reserved", 
                          bg="white", fg="gray", font=("Inter", 9))
        footer.pack(side="bottom", pady=5)

        # Inisialisasi network counter
        self.last_net = psutil.net_io_counters()

        # Label waktu update terakhir
        self.time_label = tk.Label(root, text="Update: --:--:--", bg="white", fg="gray", font=("Inter", 9))
        self.time_label.pack(pady=(0, 5))

        # Mulai update pertama
        self.update_data()

    # === Fungsi Logging Harian ===
    def log_data(self, cpu, ram, disk, net):
        today = datetime.date.today().strftime("%Y-%m-%d")
        log_filename = f"log_{today}.txt"
        log_dir = "logs"
        os.makedirs(log_dir, exist_ok=True)
        log_path = os.path.join(log_dir, log_filename)

        current_time = datetime.datetime.now().strftime("%H:%M:%S")
        log_line = f"[{current_time}] CPU: {cpu:.1f}% | RAM: {ram:.1f}% | Disk: {disk:.1f}% | Network: {net:.2f} MB/s\n"

        with open(log_path, "a") as f:
            f.write(log_line)

    # === Membuat Progress Bar ===
    def create_progress(self, label_text):
        label = tk.Label(self.frame, text=label_text, font=("Inter", 12, "bold"), bg="white")
        label.pack(pady=(10, 0))
        bar = ttk.Progressbar(self.frame, length=500)
        bar.pack(pady=(0, 5))
        return label, bar

    # === Update Data Sistem ===
    def update_data(self):
        cpu_usage = psutil.cpu_percent()
        ram_usage = psutil.virtual_memory().percent
        disk_usage = psutil.disk_usage('/').percent

        self.cpu_bar['value'] = cpu_usage
        self.ram_bar['value'] = ram_usage
        self.disk_bar['value'] = disk_usage

        new_net = psutil.net_io_counters()
        upload_speed = (new_net.bytes_sent - self.last_net.bytes_sent) / 1024
        download_speed = (new_net.bytes_recv - self.last_net.bytes_recv) / 1024
        self.last_net = new_net

        upload_percent = min(upload_speed / 1000 * 100, 100)
        download_percent = min(download_speed / 1000 * 100, 100)
        self.upload_bar['value'] = upload_percent
        self.download_bar['value'] = download_percent

        self.upload_label.config(text=f"Upload: {upload_speed:.1f} KB/s")
        self.download_label.config(text=f"Download: {download_speed:.1f} KB/s")

        current_time = time.strftime("%H:%M:%S")
        self.time_label.config(text=f"Update: {current_time}")

        # === Simpan log setiap kali update ===
        net_speed = (upload_speed + download_speed) / 1024  # jadikan MB/s
        self.log_data(cpu_usage, ram_usage, disk_usage, net_speed)

        # Jadwalkan update selanjutnya setiap 1 detik
        self.root.after(1000, self.update_data)

    # === Halaman System Info ===
    def show_system_info(self):
        sys_win = tk.Toplevel(self.root)
        sys_win.title("System Information")
        sys_win.geometry("400x300")
        sys_win.config(bg="white")

        try:
            sys_win.iconbitmap("logo.ico")
        except:
            pass

        title = tk.Label(sys_win, text="🧩 System Information", font=("Inter", 15, "bold"), bg="white")
        title.pack(pady=(15, 10))

        info_frame = tk.Frame(sys_win, bg="white")
        info_frame.pack(padx=20, pady=10)

        os_name = platform.system()
        os_version = platform.version()
        processor = platform.processor()
        cores = psutil.cpu_count(logical=True)
        ram_total = round(psutil.virtual_memory().total / (1024**3), 2)
        uptime = time.time() - psutil.boot_time()
        uptime_hours = int(uptime // 3600)
        uptime_minutes = int((uptime % 3600) // 60)

        sys_info = [
            ("OS", os_name),
            ("Versi", f"{os_version[:25]}..."),
            ("Processor", processor),
            ("CPU Cores", f"{cores} cores"),
            ("Total RAM", f"{ram_total} GB"),
            ("Uptime", f"{uptime_hours} jam {uptime_minutes} menit"),
        ]

        for i, (k, v) in enumerate(sys_info):
            tk.Label(info_frame, text=f"{k}:", font=("Inter", 11, "bold"), bg="white").grid(row=i, column=0, sticky="w", padx=(5, 10), pady=3)
            tk.Label(info_frame, text=v, font=("Inter", 11), bg="white", wraplength=280, justify="left").grid(row=i, column=1, sticky="w", pady=3)

        ttk.Button(sys_win, text="⬅ Kembali", command=sys_win.destroy).pack(pady=15)

    # === Halaman Grafik ===
    def show_graphs(self):
        def animate(i):
            cpu_data.append(psutil.cpu_percent())
            ram_data.append(psutil.virtual_memory().percent)
            disk_data.append(psutil.disk_usage('/').percent)
            cpu_data[:] = cpu_data[-50:]
            ram_data[:] = ram_data[-50:]
            disk_data[:] = disk_data[-50:]
            ax1.clear(); ax2.clear(); ax3.clear()
            ax1.plot(cpu_data, label='CPU %'); ax1.legend(loc="upper left")
            ax2.plot(ram_data, label='RAM %', color='orange'); ax2.legend(loc="upper left")
            ax3.plot(disk_data, label='Disk %', color='green'); ax3.legend(loc="upper left")
            ax1.set_ylim(0, 100); ax2.set_ylim(0, 100); ax3.set_ylim(0, 100)

        cpu_data, ram_data, disk_data = [], [], []
        fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(7, 6))
        ani = FuncAnimation(fig, animate, interval=1000)
        plt.tight_layout()
        plt.show()

    # === Halaman About ===
    def show_about(self):
        about_window = tk.Toplevel(self.root)
        about_window.title("About")
        about_window.geometry("500x400")
        about_window.config(bg="white")

        try:
            about_window.iconbitmap("logo.ico")
        except:
            pass

        title = tk.Label(about_window, text="About App", font=("Inter", 16, "bold"), bg="white")
        title.pack(pady=(15, 5))

        separator = ttk.Separator(about_window, orient="horizontal")
        separator.pack(fill="x", padx=40, pady=(0, 10))

        frame = tk.Frame(about_window, bg="white")
        frame.pack(pady=10)

        try:
            photo = make_circle_image("adambg.png", size=(110, 110))
            photo_label = tk.Label(frame, image=photo, bg="white")
            photo_label.image = photo
            photo_label.grid(row=0, column=0, rowspan=6, padx=20)
        except:
            tk.Label(frame, text="[Foto Tidak Ditemukan]", bg="white", fg="gray").grid(
                row=0, column=0, rowspan=6, padx=20
            )

        info_frame = tk.Frame(frame, bg="white")
        info_frame.grid(row=0, column=1, columnspan=2, sticky="w")

        info_texts = [
            ("App Name", "System Resource Monitoring"),
            ("Developer", "Adam Mubarok"),
            ("NIM", "312310301"),
            ("Matkul", "Sistem Operasi"),
            ("Universitas", "Pelita Bangsa")
        ]

        for i, (label, value) in enumerate(info_texts):
            tk.Label(info_frame, text=f"{label}", font=("Inter", 11, "bold"), bg="white").grid(row=i, column=0, sticky="w", padx=(10, 10), pady=4)
            tk.Label(info_frame, text=f":  {value}", font=("Inter", 11), bg="white", anchor="w").grid(row=i, column=1, sticky="w", padx=(0, 10), pady=4)

        ttk.Button(about_window, text="⬅ Kembali", command=about_window.destroy).pack(pady=15)

        footer = tk.Label(about_window, text="© 2025 System Resource Monitoring v1.1 | 312310301 All Rights Reserved", 
                          bg="white", fg="gray", font=("Inter", 9))
        footer.pack(side="bottom", pady=5)

    def confirm_exit(self):
        if messagebox.askyesno("Konfirmasi", "Apakah Anda yakin ingin keluar?"):
            self.root.destroy()

# === MAIN PROGRAM ===
root = tk.Tk()
app = ResourceMonitorApp(root)
root.mainloop()
