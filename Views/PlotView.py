import customtkinter as CTk
import tkinter as Tk
import pandas as pd
import numpy as np
from tkinter import filedialog
import matplotlib.pyplot as plt

class PlotDataPopup(CTk.CTkToplevel):
    def __init__(self):
        super().__init__()

        self.geometry("400x300")

        self.label = CTk.CTkLabel(self, text="Plot Data")

        self.radio_var = Tk.IntVar(value=1)
        self.performance_radio = CTk.CTkRadioButton(self, text="Area Plot", variable=self.radio_var, value=1)
        self.efficiency_radio = CTk.CTkRadioButton(self, text="Bar Plot", variable=self.radio_var, value=2)
        self.plot_button = CTk.CTkButton(self, text="Plot",command=self.plot_event)
        

        self.label.grid(padx=20, pady=20)
        self.performance_radio.grid(padx=20, pady=20)
        self.efficiency_radio.grid(padx=20, pady=20)
        self.plot_button.grid(padx=20, pady=20)

    def plot_event(self):
        selected_radio = self.radio_var.get()
        if selected_radio == 1:
            self.area_plot()
        elif selected_radio == 2:
            self.bar_plot()

    def radiobutton_event(self):
        print("radiobutton toggled, current value:", self.radio_var.get())

    ###### DATA PLOTS #####

    def area_plot(self):
        file_path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
        # file_path = 'random_data.csv'
        df = pd.read_csv(file_path, header=None)  # Assuming the CSV file has no header

        df['TimePerItem_Algo1'] = df.iloc[:, 1] / df.iloc[:, 0]
        df['TimePerItem_Algo2'] = df.iloc[:, 2] / df.iloc[:, 0]

        avg_time_per_item_algo1 = df['TimePerItem_Algo1'].mean()
        avg_time_per_item_algo2 = df['TimePerItem_Algo2'].mean()

        percentage_difference = ((avg_time_per_item_algo2 - avg_time_per_item_algo1) / avg_time_per_item_algo1) * 100

        print(f"Average Time per Item for Algo1: {avg_time_per_item_algo1:.2f}")
        print(f"Average Time per Item for Algo2: {avg_time_per_item_algo2:.2f}")
        print(f"ML-DProSA vs No Algorithm: {percentage_difference:.2f}%")

        plt.figure(figsize=(10, 6))

        plt.fill_between(df.index, df['TimePerItem_Algo1'], label='No algorithm', alpha=0.7, color='orange')
        plt.fill_between(df.index, df['TimePerItem_Algo2'], label='ML-DProSA', alpha=0.5, color='green')

        plt.title('ML-DProSA Performance')
        plt.xlabel('Shopper')
        plt.ylabel('Time per Item')
        plt.legend()
        plt.grid(True)

        plt.show()

    def bar_plot(self):
        file_path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
        # file_path = 'random_data.csv'
        df = pd.read_csv(file_path, header=None)  # Assuming the CSV file has no header

        df['TimePerItem_Algo1'] = df.iloc[:, 1] / df.iloc[:, 0]
        df['TimePerItem_Algo2'] = df.iloc[:, 2] / df.iloc[:, 0]

        avg_time_per_item_algo1 = df['TimePerItem_Algo1'].mean()
        avg_time_per_item_algo2 = df['TimePerItem_Algo2'].mean()

        percentage_difference = ((avg_time_per_item_algo2 - avg_time_per_item_algo1) / avg_time_per_item_algo1) * 100

        print(f"Average Time per Item for Algo1: {avg_time_per_item_algo1:.2f}")
        print(f"Average Time per Item for Algo2: {avg_time_per_item_algo2:.2f}")
        print(f"ML-DProSA vs No Algorithm: {percentage_difference:.2f}%")

        # Create a bar plot
        bar_width = 0.25
        index = np.arange(len(df.index))
        plt.bar(index, df['TimePerItem_Algo1'], width=bar_width, label='No algorithm', alpha=1, color='orange')
        plt.bar(index + bar_width, df['TimePerItem_Algo2'], width=bar_width, label='ML-DProSA', alpha=1, color='green')

        # Customize the plot
        plt.title('ML-DProSA Performance')
        plt.xlabel('Shopper')
        plt.ylabel('Time per Item')
        plt.xticks(index + bar_width, df.index)
        plt.legend()
        plt.grid(False)

        plt.show()