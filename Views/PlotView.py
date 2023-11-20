import customtkinter as CTk
import tkinter as Tk
import pandas as pd
import numpy as np
import math 
from tkinter import filedialog
import matplotlib.pyplot as plt

class PlotDataPopup(CTk.CTkToplevel):
    def __init__(self):
        super().__init__()

        self.geometry("260x700")

        self.default_block_size = 0
        self.default_block_no = 1

        self.label = CTk.CTkLabel(self, text="Plot Data")

        self.radio_var = Tk.IntVar(value=1)
        self.performance_line_radio = CTk.CTkRadioButton(self, text="Line Graph", variable=self.radio_var, value=1)
        self.performance_area_radio = CTk.CTkRadioButton(self, text="Area Graph", variable=self.radio_var, value=2)
        self.performance_bar_radio = CTk.CTkRadioButton(self, text="Bar Graph", variable=self.radio_var, value=3)
        
        self.block_size_var = Tk.StringVar(value=f"Block Size: {self.default_block_size}")
        self.block_size_label = CTk.CTkLabel(self, text=self.block_size_var.get())
        self.block_size_slider = CTk.CTkSlider(self, from_=0, to=100, number_of_steps=10, command=self.block_size_slider_event)

        self.block_no_var = Tk.StringVar(value=f"Block #: {self.default_block_no}")
        self.block_no_label = CTk.CTkLabel(self, text=self.block_no_var.get())
        self.block_no_slider = CTk.CTkSlider(self, from_=1, to=100, number_of_steps=100, command=self.block_no_slider_event)
        
        self.improvement_radio = CTk.CTkRadioButton(self, text="Improvement", variable=self.radio_var, value=4)
        self.plot_button = CTk.CTkButton(self, text="Plot",command=self.plot_event)
        
        self.label.grid(padx=20, pady=20)
        self.performance_line_radio.grid(padx=20, pady=20)
        self.performance_area_radio.grid(padx=20, pady=20)
        self.performance_bar_radio.grid(padx=20, pady=20)
        self.block_size_label.grid(padx=20, pady=20)
        self.block_size_slider.grid(padx=20, pady=20)
        self.block_no_label.grid(padx=20, pady=20)
        self.block_no_slider.grid(padx=20, pady=20)
        self.improvement_radio.grid(padx=20, pady=20)
        self.plot_button.grid(padx=20, pady=20)

        self.block_size = self.default_block_size
        self.block_size_slider.set(self.default_block_size) 
        self.block_no = self.default_block_no
        self.block_no_slider.set(self.default_block_no) 

    def block_size_slider_event(self, block_size): 
        self.block_size_var.set(f"Block size: {int(block_size)}")
        self.block_size_label.configure(text=f"Block size: {int(block_size)}")
        self.block_size = int(block_size)

    def block_no_slider_event(self, block_no): 
        self.block_no_var.set(f"Block #: {int(block_no)}")
        self.block_no_label.configure(text=f"Block #: {int(block_no)}")
        self.block_no = int(block_no)
        print(self.block_no)

    def plot_event(self):
        selected_radio = self.radio_var.get()
        if selected_radio == 1:
            self.performance_line_plot(self.block_size, self.block_no)
        elif selected_radio == 2:
            self.performance_area_plot(self.block_size, self.block_no)
        elif selected_radio == 3:
            self.performance_bar_plot(self.block_size, self.block_no)
        elif selected_radio == 4:
            self.improvement_plot(self.block_size)

    def radiobutton_event(self):
        print("radiobutton toggled, current value:", self.radio_var.get())

    ###### DATA PLOTS #####

    def performance_line_plot(self, block_size, block_no, start_index=None, end_index=None):
        file_path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
        # file_path = 'random_data.csv'
        df = pd.read_csv(file_path, header=None)  # Assuming the CSV file has no header

        df['TimePerItem_Algo1'] = df.iloc[:, 1] / df.iloc[:, 0]
        df['TimePerItem_Algo2'] = df.iloc[:, 2] / df.iloc[:, 0]

        if block_size == 0:
            block_size = len(df)
            block_no = 1

        if start_index is None:
            start_index = (block_no - 1) * block_size
        if end_index is None:
            end_index = min(block_no * block_size, len(df.index))

        avg_time_per_item_algo1 = df['TimePerItem_Algo1'].iloc[start_index:end_index].mean()
        avg_time_per_item_algo2 = df['TimePerItem_Algo2'].iloc[start_index:end_index].mean()

        percentage_difference = abs((avg_time_per_item_algo2 - avg_time_per_item_algo1) / avg_time_per_item_algo1) * 100

        print(f"Average Time per Item for Algo1: {avg_time_per_item_algo1:.2f}")
        print(f"Average Time per Item for Algo2: {avg_time_per_item_algo2:.2f}")
        print(f"ML-DProSA vs No Algorithm: {percentage_difference:.2f}%")

        plt.figure(figsize=(10, 6))

        plt.plot(df.index[start_index:end_index], df['TimePerItem_Algo1'].iloc[start_index:end_index], label='No algorithm', alpha=0.7, color='orange')
        plt.plot(df.index[start_index:end_index], df['TimePerItem_Algo2'].iloc[start_index:end_index], label='ML-DProSA', alpha=0.5, color='green')

        # Add trendlines
        trendline_algo1 = np.polyfit(df.index[start_index:end_index], df['TimePerItem_Algo1'].iloc[start_index:end_index], 1)
        trendline_algo2 = np.polyfit(df.index[start_index:end_index], df['TimePerItem_Algo2'].iloc[start_index:end_index], 1)

        plt.plot(df.index[start_index:end_index], np.polyval(trendline_algo1, df.index[start_index:end_index]), '--', color='orange', label='No algorithm Trendline')
        plt.plot(df.index[start_index:end_index], np.polyval(trendline_algo2, df.index[start_index:end_index]), '--', color='green', label='ML-DProSA Trendline')

        plt.title('ML-DProSA Performance')
        plt.xlabel('Shopper')
        plt.ylabel('Average time per Item')
        plt.legend()
        plt.grid(True)

        plt.annotate(f"No Algorithm (Time per item): {avg_time_per_item_algo1:.2f}s\n"
            f"ML-DProSA (Time per item): {avg_time_per_item_algo2:.2f}s\n"
            f"ML-DProSA vs No Algorithm: {percentage_difference:.2f}%", 
            xy=(-0.1, -0.16), xycoords='axes fraction',
            xytext=(10, 10), textcoords='offset points',
            fontsize=8, color='blue')

        plt.show()

    def performance_area_plot(self, block_size, block_no, start_index=None, end_index=None):
        file_path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
        # file_path = 'random_data.csv'
        df = pd.read_csv(file_path, header=None)  # Assuming the CSV file has no header

        df['TimePerItem_Algo1'] = df.iloc[:, 1] / df.iloc[:, 0]
        df['TimePerItem_Algo2'] = df.iloc[:, 2] / df.iloc[:, 0]

        if block_size == 0:
            block_size = len(df)
            block_no = 1

        if start_index is None:
            start_index = (block_no - 1) * block_size
        if end_index is None:
            end_index = min(block_no * block_size, len(df.index))

        avg_time_per_item_algo1 = df['TimePerItem_Algo1'].iloc[start_index:end_index].mean()
        avg_time_per_item_algo2 = df['TimePerItem_Algo2'].iloc[start_index:end_index].mean()

        percentage_difference = ((avg_time_per_item_algo2 - avg_time_per_item_algo1) / avg_time_per_item_algo1) * 100

        print(f"Average Time per Item for Algo1: {avg_time_per_item_algo1:.2f}")
        print(f"Average Time per Item for Algo2: {avg_time_per_item_algo2:.2f}")
        print(f"ML-DProSA vs No Algorithm: {percentage_difference:.2f}%")

        plt.figure(figsize=(10, 6))

        plt.fill_between(df.index[start_index:end_index], df['TimePerItem_Algo1'].iloc[start_index:end_index], label='No algorithm', alpha=0.7, color='orange')
        plt.fill_between(df.index[start_index:end_index], df['TimePerItem_Algo2'].iloc[start_index:end_index], label='ML-DProSA', alpha=0.5, color='green')

        plt.title('ML-DProSA Performance')
        plt.xlabel('Shopper')
        plt.ylabel('Average time per Item')
        plt.legend()
        plt.grid(True)

        plt.annotate(f"No Algorithm (Time per item): {avg_time_per_item_algo1:.2f}s\n"
            f"ML-DProSA (Time per item): {avg_time_per_item_algo2:.2f}s\n"
            f"ML-DProSA vs No Algorithm: {percentage_difference:.2f}%", 
            xy=(-0.1, -0.16), xycoords='axes fraction',
            xytext=(10, 10), textcoords='offset points',
            fontsize=8, color='blue')

        plt.show()

    def performance_bar_plot(self, block_size, block_no, start_index=None, end_index=None):
        file_path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
        # file_path = 'random_data.csv'
        df = pd.read_csv(file_path, header=None)  # Assuming the CSV file has no header

        df['TimePerItem_Algo1'] = df.iloc[:, 1] / df.iloc[:, 0]
        df['TimePerItem_Algo2'] = df.iloc[:, 2] / df.iloc[:, 0]

        if block_size == 0:
            block_size = len(df)
            block_no = 1

        if block_size == 0:
            block_size = len(df)
            block_no = 1

        if start_index is None:
            start_index = (block_no - 1) * block_size
        if end_index is None:
            end_index = min(block_no * block_size, len(df.index))


        avg_time_per_item_algo1 = df['TimePerItem_Algo1'].iloc[start_index:end_index].mean()
        avg_time_per_item_algo2 = df['TimePerItem_Algo2'].iloc[start_index:end_index].mean()

        percentage_difference = abs((avg_time_per_item_algo2 - avg_time_per_item_algo1) / avg_time_per_item_algo1) * 100

        print(f"Average Time per Item for Algo1: {avg_time_per_item_algo1:.2f}")
        print(f"Average Time per Item for Algo2: {avg_time_per_item_algo2:.2f}")
        print(f"ML-DProSA vs No Algorithm: {percentage_difference:.2f}%")

        bar_width = 0.25
        index = np.arange(start_index, end_index)
        plt.figure(figsize=(10, 6))
        plt.bar(index, df['TimePerItem_Algo1'].iloc[start_index:end_index], width=bar_width, label='No algorithm', alpha=1, color='orange')
        plt.bar(index + bar_width, df['TimePerItem_Algo2'].iloc[start_index:end_index], width=bar_width, label='ML-DProSA', alpha=1, color='green')

        plt.title('ML-DProSA Performance')
        plt.xlabel('Shopper')
        plt.ylabel('Average time per Item')
        plt.xticks(index + bar_width / 2, range(start_index + 1, end_index + 1))
        plt.legend()
        plt.grid(False)

        plt.annotate(f"No Algorithm (Time per item): {avg_time_per_item_algo1:.2f}s\n"
                    f"ML-DProSA (Time per item): {avg_time_per_item_algo2:.2f}s\n"
                    f"ML-DProSA vs No Algorithm: {percentage_difference:.2f}%", 
                    xy=(-0.1, -0.16), xycoords='axes fraction',
                    xytext=(10, 10), textcoords='offset points',
                    fontsize=8, color='blue')

        plt.show()

    def improvement_plot(self, block_size):
        file_path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
        df = pd.read_csv(file_path, header=None)

        # Assuming df has columns: 0 - Number of shoppers, 1 - Time for Algo1, 2 - Time for Algo2

        df['TimePerItem_Algo1'] = df.iloc[:, 1] / df.iloc[:, 0]
        df['TimePerItem_Algo2'] = df.iloc[:, 2] / df.iloc[:, 0]

        avg_time_per_item_algo1 = df['TimePerItem_Algo1'].mean()
        avg_time_per_item_algo2 = df['TimePerItem_Algo2'].mean()

        num_blocks = len(df) // block_size
        improvement_list_algo1 = []
        improvement_list_algo2 = []

        for i in range(num_blocks - 1):  # Loop until the second-to-last block
            start_idx = i * block_size
            end_idx1 = (i + 1) * block_size
            end_idx2 = (i + 2) * block_size

            avg_time_algo1_block1 = df['TimePerItem_Algo1'].iloc[start_idx:end_idx1].mean()
            avg_time_algo2_block1 = df['TimePerItem_Algo2'].iloc[start_idx:end_idx1].mean()

            avg_time_algo1_block2 = df['TimePerItem_Algo1'].iloc[end_idx1:end_idx2].mean()
            avg_time_algo2_block2 = df['TimePerItem_Algo2'].iloc[end_idx1:end_idx2].mean()

            improvement_algo1 = ((avg_time_algo1_block1 - avg_time_algo1_block2) / avg_time_algo1_block1) * 100
            improvement_algo2 = ((avg_time_algo2_block1 - avg_time_algo2_block2) / avg_time_algo2_block1) * 100

            improvement_list_algo1.append(improvement_algo1)
            improvement_list_algo2.append(improvement_algo2)

        count = len(improvement_list_algo1)
        total = sum(improvement_list_algo1)
        improv1_avg = total / count
        
        count = len(improvement_list_algo2)
        total = sum(improvement_list_algo2)
        improv2_avg = total / count

        improv1 = ', '.join(f'{x:.2f}%'.format(x) for x in improvement_list_algo1) 
        improv2 = ', '.join(f'{x:.2f}%'.format(x) for x in improvement_list_algo2)

        print(f"No algorithm (change-over-time): {improv1}")
        print(f"DProSA algorithm (change-over-time): {improv2}")

        bar_width = 0.25
        index = np.arange(num_blocks - 1)  # One less bar for the improvement between blocks
        plt.figure(figsize=(12, 6))
        plt.bar(index, improvement_list_algo1, width=bar_width, label='No algorithm', alpha=1, color='orange')
        plt.bar(index + bar_width, improvement_list_algo2, width=bar_width, label='ML-DProSA', alpha=1, color='green')

        plt.title('ML-DProSA Performance Improvement Between Consecutive Blocks')
        plt.xlabel('Block of Shoppers')
        plt.ylabel('Percent Improvement')
        plt.xticks(index + bar_width / 2, [f'{i * block_size}-{(i + 1) * block_size - 1}' for i in range(num_blocks - 1)])
        plt.legend()
        plt.grid(False)

        plt.annotate(f"No Algorithm (change-over-time): {improv1_avg:.2f}s\n"
            f"ML-DProSA (change-over-time): {improv2_avg:.2f}%\n"
            f"for every {block_size} shoppers, from a total of {len(df)} shoppers", 
            xy=(-0.1, -0.16), xycoords='axes fraction',
            xytext=(10, 10), textcoords='offset points',
            fontsize=8, color='blue')
        

        plt.show()
