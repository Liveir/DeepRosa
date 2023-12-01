import customtkinter as CTk
import tkinter as Tk
import pandas as pd
import numpy as np
import os 
from tkinter import filedialog
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('TkAgg')


class PlotDataPopup(CTk.CTkToplevel):
    def __init__(self):
        super().__init__()

        self.geometry("260x700")

        self.default_block_size = 0
        self.default_block_no = 1

        self.label = CTk.CTkLabel(self, text="Plot Data")

        self.radio_var = Tk.IntVar(value=1)
        self.performance_line_radio = CTk.CTkRadioButton(self, text="Performance Graph", variable=self.radio_var, value=1)
        self.performance_area_radio = CTk.CTkRadioButton(self, text="Improvement Graph", variable=self.radio_var, value=2)
        self.dwell_time_radio = CTk.CTkRadioButton(self, text="Dwell Time Graph", variable=self.radio_var, value=3)
        self.list_size_radio = CTk.CTkRadioButton(self, text="Shopping List Sizes", variable=self.radio_var, value=4)
  
        self.block_size_var = Tk.StringVar(value=f"Block Size: {self.default_block_size}")
        self.block_size_label = CTk.CTkLabel(self, text=self.block_size_var.get())
        self.block_size_slider = CTk.CTkSlider(self, from_=0, to=500, number_of_steps=50, command=self.block_size_slider_event)

        self.block_no_var = Tk.StringVar(value=f"Block #: {self.default_block_no}")
        self.block_no_label = CTk.CTkLabel(self, text=self.block_no_var.get())
        self.block_no_slider = CTk.CTkSlider(self, from_=1, to=100, number_of_steps=100, command=self.block_no_slider_event)
        
        self.plot_button = CTk.CTkButton(self, text="Plot",command=self.plot_event)
        
        self.label.grid(padx=20, pady=20)
        self.performance_line_radio.grid(padx=20, pady=20)
        self.performance_area_radio.grid(padx=20, pady=20)
        self.dwell_time_radio.grid(padx=20, pady=20)
        self.list_size_radio.grid(padx=20, pady=20)
        self.block_size_label.grid(padx=20, pady=20)
        self.block_size_slider.grid(padx=20, pady=20)
        self.block_no_label.grid(padx=20, pady=20)
        self.block_no_slider.grid(padx=20, pady=20)
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
            self.improvement_line_plot(self.block_size)
        elif selected_radio == 3:
            self.dwell_time_plot(self.block_size, self.block_no)
        elif selected_radio == 4:
            self.list_size_plot()

    def radiobutton_event(self):
        print("radiobutton toggled, current value:", self.radio_var.get())

    ###### DATA PLOTS #####

    def performance_line_plot(self, block_size, block_no, start_index=None, end_index=None):
        file_path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
        # file_path = 'random_data.csv'
        df = pd.read_csv(file_path, header=None)  # Assuming the CSV file has no header

        if block_size == 0:
            block_size = len(df)
            block_no = 1

        if start_index is None:
            start_index = (block_no - 1) * block_size
        if end_index is None:
            end_index = min(block_no * block_size, len(df.index))
    
        df['TimePerItem_NS'] = df.iloc[:, 1] / df.iloc[:, 0]
        df['TimePerItem_AG'] = df.iloc[:, 2] / df.iloc[:, 0]
        df['TimePerItem_AP'] = df.iloc[:, 3] / df.iloc[:, 0]

        avg_tpi_ns = df['TimePerItem_NS'].iloc[start_index:end_index].mean()
        avg_tpi_ag = df['TimePerItem_AG'].iloc[start_index:end_index].mean()
        avg_tpi_ap = df['TimePerItem_AP'].iloc[start_index:end_index].mean()

        print(f"Average Time per Item for Setup X: {avg_tpi_ns:.2f}")
        print(f"Average Time per Item for DProSA-AG: {avg_tpi_ag:.2f}")
        print(f"Average Time per Item for DProSA-AP: {avg_tpi_ap:.2f}")

        plt.figure(figsize=(10, 6))

        plt.plot(df.index[start_index:end_index] + 1, df['TimePerItem_NS'].iloc[start_index:end_index], alpha=0.1, color='grey')
        plt.plot(df.index[start_index:end_index] + 1, df['TimePerItem_AG'].iloc[start_index:end_index], alpha=0.1, color='orange')
        plt.plot(df.index[start_index:end_index] + 1, df['TimePerItem_AP'].iloc[start_index:end_index], alpha=0.1, color='green')

        # plt.scatter(df.index[start_index:end_index] + 1, df['TimePerItem_NS'].iloc[start_index:end_index], label='Setup X (no algorithm)', alpha=0.5, color='grey')
        # plt.scatter(df.index[start_index:end_index] + 1, df['TimePerItem_AG'].iloc[start_index:end_index], label='ML-DProSA (agglomerative)', alpha=0.5, color='orange')
        # plt.scatter(df.index[start_index:end_index] + 1, df['TimePerItem_AP'].iloc[start_index:end_index], label='ML-DProSA (affinity propagation)', alpha=0.5, color='green')

        # Add trendlines
        trendline_ns = np.polyfit(df.index[start_index:end_index] + 1, df['TimePerItem_NS'].iloc[start_index:end_index], 1)
        trendline_ag = np.polyfit(df.index[start_index:end_index] + 1, df['TimePerItem_AG'].iloc[start_index:end_index], 1)
        trendline_ap = np.polyfit(df.index[start_index:end_index] + 1, df['TimePerItem_AP'].iloc[start_index:end_index], 1)

        plt.plot(df.index[start_index:end_index] + 1, np.polyval(trendline_ns, df.index[start_index:end_index]), '--', label='No Algorithm', color='grey')
        plt.plot(df.index[start_index:end_index] + 1, np.polyval(trendline_ag, df.index[start_index:end_index]), '--', label='DProSA-AG', color='orange')
        plt.plot(df.index[start_index:end_index] + 1, np.polyval(trendline_ap, df.index[start_index:end_index]), '--', label='DProSA-AP', color='green')

        filename = os.path.basename(file_path) 
        filename = filename.split(".csv")[0]

        plt.title('Performance Comparison for Config ' + filename)
        plt.xlabel('Shopper')
        plt.ylabel('Average time per item')
        plt.legend()
        plt.grid(True)
        plt.ylim(0, 40)

        plt.annotate(f"No Sorting (average time per item): {avg_tpi_ns:.2f}s\n"
            f"DProSA-AG (average time per item): {avg_tpi_ag:.2f}s\n"
            f"DProSA-AP (average time per item): {avg_tpi_ap:.2f}s", 
            xy=(-0.1, -0.16), xycoords='axes fraction',
            xytext=(10, 10), textcoords='offset points',
            fontsize=8, color='blue')
        plt.show()

    def improvement_line_plot(self, block_size):
        file_path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
        df = pd.read_csv(file_path, header=None)

        df['TimePerItem_NS'] = df.iloc[:, 1] / df.iloc[:, 0]
        df['TimePerItem_AG'] = df.iloc[:, 2] / df.iloc[:, 0]
        df['TimePerItem_AP'] = df.iloc[:, 3] / df.iloc[:, 0]

        avg_tpi_ns = df['TimePerItem_NS'].iloc[0:len(df)].mean()
        avg_tpi_ag = df['TimePerItem_AG'].iloc[0:len(df)].mean()
        avg_tpi_ap = df['TimePerItem_AP'].iloc[0:len(df)].mean()

        if block_size >= len(df) or block_size == 0:
            block_size = 1
            
        df_grouped = df.groupby(df.index // block_size)
        avg_grp_tpi_ns = df_grouped['TimePerItem_NS'].mean()
        avg_grp_tpi_ag = df_grouped['TimePerItem_AG'].mean()
        avg_grp_tpi_ap = df_grouped['TimePerItem_AP'].mean()

        plt.figure(figsize=(10, 6))

        plt.plot(avg_grp_tpi_ns.index * block_size + block_size, avg_grp_tpi_ns, label='No Sorting', alpha=1, color='grey')
        plt.plot(avg_grp_tpi_ag.index * block_size + block_size, avg_grp_tpi_ag, label='DProSA-AG', alpha=1, color='orange')
        plt.plot(avg_grp_tpi_ap.index * block_size + block_size, avg_grp_tpi_ap, label='DProSA-AP', alpha=1, color='green')

        filename = os.path.basename(file_path) 
        filename = filename.split(".csv")[0]

        plt.title('Improvement Comparison for Config ' + filename)
        plt.xlabel(f'Averaged every {block_size} shoppers')
        plt.ylabel('Average time per item')
        plt.legend()
        plt.grid(True)
        plt.ylim(15, 30)

        plt.annotate(f"No Sorting (average time per item): {avg_tpi_ns:.2f}s\n"
            f"DProSA-AG (average time per item): {avg_tpi_ag:.2f}s\n"
            f"DProSA-AP (average time per item): {avg_tpi_ap:.2f}s", 
            xy=(-0.1, -0.16), xycoords='axes fraction',
            xytext=(10, 10), textcoords='offset points',
            fontsize=8, color='blue')

        plt.show()

    def dwell_time_plot(self, block_size, block_no, start_index=None, end_index=None):
        file_path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
        # file_path = 'random_data.csv'
        df = pd.read_csv(file_path, header=None)  # Assuming the CSV file has no header

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

        df['DwellTime_NS'] = df.iloc[:, 1]
        df['DwellTime_AG'] = df.iloc[:, 2]
        df['DwellTime_AP'] = df.iloc[:, 3]

        dwell_time_ns = df['DwellTime_NS'].iloc[start_index:end_index].mean()
        dwell_time_ag = df['DwellTime_AG'].iloc[start_index:end_index].mean()
        dwell_time_ap = df['DwellTime_AP'].iloc[start_index:end_index].mean()

        print(f"Average Time per Item for No Sorting: {dwell_time_ns:.2f}")
        print(f"Average Time per Item for DProSA-AG: {dwell_time_ag:.2f}")
        print(f"Average Time per Item for DProSA-AP: {dwell_time_ap:.2f}")

        bar_width = 0.25
        index = np.arange(start_index, end_index)
        plt.figure(figsize=(10, 6))
        plt.bar(index, df['DwellTime_NS'].iloc[start_index:end_index], width=bar_width, label='No Sorting', alpha=1, color='grey')
        plt.bar(index + bar_width, df['DwellTime_AG'].iloc[start_index:end_index], width=bar_width, label='DProSA-AG', alpha=1, color='orange')
        plt.bar(index + 2*bar_width, df['DwellTime_AP'].iloc[start_index:end_index], width=bar_width, label='DProSA-AP', alpha=1, color='green')

        filename = os.path.basename(file_path) 
        filename = filename.split(".csv")[0]

        plt.title('Dwell Times for Config ' + filename)
        plt.xlabel('Shopper')
        plt.ylabel('Dwell Time')
        plt.xticks(index + bar_width / 2, range(start_index + 1, end_index + 1))
        plt.legend()
        plt.grid(False)

        plt.annotate(f"No Sorting (dwell time): {dwell_time_ns:.2f}s\n"
            f"DProSA-AG (dwell time): {dwell_time_ag:.2f}s\n"
            f"DProSA-AP (dwell time): {dwell_time_ap:.2f}s", 
            xy=(-0.1, -0.16), xycoords='axes fraction',
            xytext=(10, 10), textcoords='offset points',
            fontsize=8, color='blue')

        plt.show()


    def list_size_plot(self):
        file_path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
        df = pd.read_csv(file_path, header=None)  # Assuming the CSV file has no header

        # Extract the first column
        values = df.iloc[:, 0]

        # Define color ranges
        color_map = np.zeros_like(values, dtype='str')
        color_map[(values >= 5) & (values <= 7)] = 'green'
        color_map[(values >= 8) & (values <= 14)] = 'yellow'
        color_map[(values >= 15) & (values <= 21)] = 'red'

        # Create a bar plot
        plt.figure(figsize=(10, 6))
        bars = plt.bar(np.arange(len(values)), values, color=color_map)

        # Add labels and title
        filename = os.path.basename(file_path) 
        filename = filename.split(".csv")[0]

        plt.xlabel('Index')
        plt.ylabel('Values')
        plt.title('Shopping List Sizes of Config ' + filename)

        # Add legend for colors
        legend_labels = {
            'green': '5-9',
            'yellow': '10-14',
            'red': '15-21'
        }

        handles = [plt.Rectangle((0, 0), 1, 1, color=color) for color in legend_labels.keys()]
        plt.legend(handles, legend_labels.values(), title='Color Ranges', loc='upper right')

        # Show the plot
        plt.show()