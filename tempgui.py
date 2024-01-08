import tkinter as tk
from tkinter import ttk
import paho.mqtt.client as mqtt
import json
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from pygame import mixer

class MQTTSubscriber:
    def __init__(self, master):
        self.master = master
        master.title("MQTT Subscriber")

        # Variables to store MQTT server address and port
        self.server_address = tk.StringVar(value="localhost")
        self.server_port = tk.IntVar(value=1883)

        # MQTT client setup
        self.client = mqtt.Client()
        self.client.on_message = self.on_message

        # GUI setup
        self.setup_gui()

    def setup_gui(self):
        # Entry for MQTT server address
        ttk.Label(self.master, text="Server Address:").grid(row=0, column=0, sticky="w")
        address_entry = ttk.Entry(self.master, textvariable=self.server_address)
        address_entry.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        # Scale for MQTT server port
        ttk.Label(self.master, text="Server Port:").grid(row=1, column=0, sticky="w")
        port_scale = ttk.Scale(self.master, from_=1500, to=2000, variable=self.server_port, orient="horizontal")
        port_scale.grid(row=1, column=1, padx=5, pady=5, sticky="ew")
        
        # Entry to display the current port value
        port_entry = ttk.Entry(self.master, textvariable=self.server_port, state="readonly", width=6)
        port_entry.grid(row=1, column=2, padx=5, pady=5, sticky="w")

        # Button to connect to MQTT broker
        connect_button = ttk.Button(self.master, text="Connect", command=self.connect_to_broker)
        connect_button.grid(row=2, column=0, columnspan=3, pady=10)

        # Matplotlib plot
        self.fig, self.ax = plt.subplots()
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.master)
        self.canvas.get_tk_widget().grid(row=3, column=0, columnspan=3)

        # Set initial value in the port entry
        self.update_port_entry()

        # Update the port entry when the scale is adjusted
        port_scale.config(command=lambda value: self.update_port_entry())

        # Play music continuously
        self.play_music()

    def update_port_entry(self):
        # Update the port entry to show the current scale value
        self.server_port.set(int(self.server_port.get()))

    def connect_to_broker(self):
        try:
            # Connect to MQTT broker
            server_address = self.server_address.get()
            server_port = self.server_port.get()
            self.client.connect(server_address, server_port, 60)
            self.client.subscribe("fh-ece21")  # replace this text with the topic to subscribe to
            self.client.loop_start()

            # Clear the plot
            self.ax.clear()

            # Initial empty plot
            self.plot_temperatures({})
        except Exception as e:
            # Handle connection error
            tk.messagebox.showerror("Error", f"Failed to connect: {str(e)}")

    def on_message(self, client, userdata, msg):
        try:
            # Decode JSON data from the received message payload
            data = json.loads(msg.payload.decode())
            self.plot_temperatures(data)
        except json.JSONDecodeError:
            print("Invalid JSON data")

    def plot_temperatures(self, data):
        # Clear existing plot
        self.ax.clear()

        # Plot each sensor's temperature
        for i, (sensor, temperature) in enumerate(data.items()):
            self.ax.plot([i], [temperature], marker="o", label=sensor)

        # Set plot labels and legend
        self.ax.set_xlabel("Sensor")
        self.ax.set_ylabel("Temperature")
        self.ax.legend()

        # Redraw the canvas
        self.canvas.draw()

    def play_music(self):
        mixer.init()
        mixer.music.load('BoilingPotGUI\chipi.mp3')  # Replace with the path to your music file
        mixer.music.play(-1)  # -1 indicates infinite loop


def main():
    root = tk.Tk()
    app = MQTTSubscriber(root)
    root.mainloop()


if __name__ == "__main__":
    main()
