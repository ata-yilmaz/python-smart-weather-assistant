import json
from datetime import datetime
import tkinter as tk
from tkinter import messagebox
import urllib.request


class WeatherApp:

  def __init__(self, root):
    self.root = root
    self.root.title("Smart Weather Assistant & Recommendations")
    self.root.geometry("540x670")
    self.root.resizable(False, False)
    self.root.configure(bg="#E3F2FD")  # Açık mavi tema arka planı

    # Şehirlerin Koordinat Veri Tabanı (Alfabetik Sıralı)
    self.cities = {
        "Adana": {"lat": 37.0, "lon": 35.3213},
        "Ankara": {"lat": 39.9334, "lon": 32.8597},
        "İstanbul": {"lat": 41.0082, "lon": 28.9784},
        "İzmir": {"lat": 38.4192, "lon": 27.1287},
    }

    self.current_city = "Adana"  # Alfabetik ilk şehir varsayılan
    self.weather_data = None
    self.selected_day_index = 0
    self.day_buttons = []

    # Ana arayüz bileşenlerini oluştur
    self.create_main_layout()
    self.load_city_weather(self.current_city)

  def create_main_layout(self):
    # Üst Başlık
    self.title_label = tk.Label(
        self.root,
        text="Smart Weather Assistant",
        font=("Segoe UI", 16, "bold"),
        bg="#E3F2FD",
        fg="#0D47A1",
    )
    self.title_label.pack(pady=10)

    # Şehir Sekmeleri Çerçevesi (Tabs - Alfabetik Sıralı)
    tabs_frame = tk.Frame(self.root, bg="#E3F2FD")
    tabs_frame.pack(pady=5)

    self.city_buttons = {}
    for city_name in self.cities.keys():
      btn = tk.Button(
          tabs_frame,
          text=city_name,
          font=("Segoe UI", 10, "bold"),
          width=10,
          bg="#FFFFFF",
          fg="#0D47A1",
          command=lambda c=city_name: self.switch_city(c),
      )
      btn.pack(side="left", padx=4)
      self.city_buttons[city_name] = btn

    # 7 Günlük Tahmin Kutuları Çerçevesi
    self.forecast_frame = tk.LabelFrame(
        self.root,
        text=" 7-Day Forecast ",
        font=("Segoe UI", 11, "bold"),
        bg="#E3F2FD",
        fg="#0D47A1",
    )
    self.forecast_frame.pack(pady=8, padx=15, fill="x")

    self.grid_frame = tk.Frame(self.forecast_frame, bg="#E3F2FD")
    self.grid_frame.pack(pady=5, padx=5)

    # Gelişmiş Detay ve Öneri Paneli
    self.detail_frame = tk.LabelFrame(
        self.root,
        text=" Daily Details & Smart Recommendations ",
        font=("Segoe UI", 11, "bold"),
        bg="#E3F2FD",
        fg="#0D47A1",
    )
    self.detail_frame.pack(pady=10, padx=15, fill="both", expand=True)

    # İçeriklerin yer alacağı ana taşıyıcı çerçeve (Detay ekranı)
    self.detail_content_frame = tk.Frame(self.detail_frame, bg="#FFFFFF")
    self.detail_content_frame.pack(fill="both", expand=True, padx=8, pady=8)

  def switch_city(self, city_name):
    self.current_city = city_name
    # Sekmelerin renklerini güncelle (Aktif şehir koyu mavi, diğerleri beyaz)
    for c, btn in self.city_buttons.items():
      if c == city_name:
        btn.config(bg="#0D47A1", fg="white")
      else:
        btn.config(bg="#FFFFFF", fg="#0D47A1")

    self.load_city_weather(city_name)

  def load_city_weather(self, city_name):
    lat = self.cities[city_name]["lat"]
    lon = self.cities[city_name]["lon"]

    try:
      url = (
          f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&daily=temperature_2m_max,temperature_2m_min,weathercode,relative_humidity_2m_max,windspeed_10m_max&timezone=auto"
      )
      req = urllib.request.urlopen(url)
      response = req.read().decode("utf-8")
      self.weather_data = json.loads(response)
      self.selected_day_index = 0
      self.update_forecast_boxes()
      self.show_day_details(0)
    except Exception as e:
      messagebox.showerror(
          "Connection Error",
          "Could not fetch weather data. Check your internet connection!",
      )
      self.weather_data = None

  def get_weather_description(self, code):
    if code == 0:
      return "Clear Sky ☀️"
    elif code in [1, 2, 3]:
      return "Partly Cloudy ⛅"
    elif code in [45, 48]:
      return "Foggy 🌫️"
    elif code in [51, 53, 55, 61, 63, 65, 80, 81, 82]:
      return "Rainy 🌧️"
    elif code in [71, 73, 75, 85, 86]:
      return "Snowy ❄️"
    elif code in [95, 96, 99]:
      return "Thunderstorm ⚡"
    else:
      return "Pleasant 🌤️"

  def get_recommendations(self, temp_max, condition_type, wind_speed):
    recs = []
    if "Rainy" in condition_type or "Thunderstorm" in condition_type:
      recs.append("• ☂️ Don't forget to take your umbrella or raincoat!")
    if "Clear Sky" in condition_type and temp_max > 22:
      recs.append("• 🕶️ Sunglasses and a hat are strongly recommended.")
      recs.append("• 🧺 Perfect weather for a park picnic!")
    if (
        temp_max >= 18
        and temp_max <= 28
        and "Rainy" not in condition_type
        and wind_speed < 20
    ):
      recs.append("• 🚲 Ideal weather for a bike ride around the city or park!")
    if temp_max < 15:
      recs.append("• 🧥 You should wear a warm coat or jacket.")
    if wind_speed > 25:
      recs.append("• 💨 It's quite windy outside, take precautions!")

    if not recs:
      recs.append("• ✨ Standard pleasant day, enjoy it!")

    return "\n".join(recs)

  def update_forecast_boxes(self):
    # Eski kutucukları temizle
    for widget in self.grid_frame.winfo_children():
      widget.destroy()

    daily = self.weather_data["daily"]
    self.dates = daily["time"]
    self.max_temps = daily["temperature_2m_max"]
    self.min_temps = daily["temperature_2m_min"]
    self.weather_codes = daily["weathercode"]
    self.humidities = daily["relative_humidity_2m_max"]
    self.wind_speeds = daily["windspeed_10m_max"]

    self.day_buttons = []
    for i in range(len(self.dates)):
      date_obj = datetime.strptime(self.dates[i], "%Y-%m-%d")
      day_short = date_obj.strftime("%a")
      date_num = date_obj.strftime("%d %b")

      btn = tk.Button(
          self.grid_frame,
          text=f"{day_short}\n{date_num}\n{self.max_temps[i]}° / {self.min_temps[i]}°",
          font=("Segoe UI", 9),
          width=9,
          height=3,
          command=lambda idx=i: self.show_day_details(idx),
      )
      row_idx = 0 if i < 4 else 1
      col_idx = i if i < 4 else i - 4
      btn.grid(row=row_idx, column=col_idx, padx=4, pady=4)
      self.day_buttons.append(btn)

    self.update_box_styles()

  def update_box_styles(self):
    for i, btn in enumerate(self.day_buttons):
      if i == 0:  # Bugün
        btn.config(bg="#0D47A1", fg="white", bd=3)
      else:
        btn.config(bg="#FFFFFF", fg="#0D47A1", bd=1)

      if i == self.selected_day_index:
        btn.config(relief="sunken")
      else:
        btn.config(relief="raised")

  def show_day_details(self, index):
    self.selected_day_index = index
    self.update_box_styles()

    # İçerik çerçevesini temizle
    for widget in self.detail_content_frame.winfo_children():
      widget.destroy()

    date_str = self.dates[index]
    t_max = self.max_temps[index]
    t_min = self.min_temps[index]
    code = self.weather_codes[index]
    humidity = self.humidities[index]
    wind = self.wind_speeds[index]
    cond_text = self.get_weather_description(code)

    day_status = " (TODAY)" if index == 0 else ""

    # Üst Bilgi Satırı: Sol Büyük Hava Durumu | Sağ Tarih
    top_row = tk.Frame(self.detail_content_frame, bg="#FFFFFF")
    top_row.pack(fill="x", padx=10, pady=5)

    cond_label = tk.Label(
        top_row,
        text=cond_text,
        font=("Segoe UI", 15, "bold"),
        bg="#FFFFFF",
        fg="#0D47A1",
    )
    cond_label.pack(side="left")

    date_label = tk.Label(
        top_row,
        text=f"📅 {date_str}{day_status}",
        font=("Segoe UI", 10, "bold"),
        bg="#FFFFFF",
        fg="#555555",
    )
    date_label.pack(side="right")

    # Ayırıcı Çizgi
    separator = tk.Frame(
        self.detail_content_frame, height=2, bg="#E0E0E0", bd=0
    )
    separator.pack(fill="x", padx=10, pady=8)

    # Detaylar (Sıcaklık, Nem, Rüzgar)
    details_text = (
        f"• Temperature : Max {t_max}°C / Min {t_min}°C\n"
        f"• Humidity    : {humidity}%\n"
        f"• Wind Speed  : {wind} km/h"
    )
    details_label = tk.Label(
        self.detail_content_frame,
        text=details_text,
        font=("Segoe UI", 11),
        bg="#FFFFFF",
        fg="#222222",
        justify="left",
    )
    details_label.pack(anchor="w", padx=10, pady=5)

    # Öneriler Başlığı (Bold ve Vurgulu)
    rec_title = tk.Label(
        self.detail_content_frame,
        text="💡 RECOMMENDED ITEMS & ACTIVITIES:",
        font=("Segoe UI", 10, "bold"),
        bg="#FFFFFF",
        fg="#0D47A1",
    )
    rec_title.pack(anchor="w", padx=10, pady=(10, 2))

    # Öneriler İçeriği
    recommendations = self.get_recommendations(t_max, cond_text, wind)
    rec_label = tk.Label(
        self.detail_content_frame,
        text=recommendations,
        font=("Segoe UI", 10),
        bg="#FFFFFF",
        fg="#333333",
        justify="left",
    )
    rec_label.pack(anchor="w", padx=15, pady=2)


if __name__ == "__main__":
  root = tk.Tk()
  app = WeatherApp(root)
  root.mainloop()
