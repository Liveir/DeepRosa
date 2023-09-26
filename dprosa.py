import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
from scipy.cluster.hierarchy import dendrogram, linkage
from sklearn.cluster import AgglomerativeClustering
import math
import csv
import time
from itertools import combinations
import networkx as nx
import matplotlib.pyplot as plt
import matplotlib.cm as cm
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import tkinter
import tkinter.messagebox
from tkinter import filedialog
import customtkinter as CTk


CTk.set_appearance_mode("system")
CTk.set_default_color_theme("green")

class dprosaGUI(CTk.CTk):
    def __init__(self):
        super().__init__()

        # configure window
        self.title("Deep Rosa Visualizer")
        self.geometry("1200x1000")
        self.timegap_dict = {}
        self.cluster_dict = {}
        self.max_clusters = 120 # maximum number of clusters allowed (does not have to be reached)
        self.threshold_increment = 25 # value to increment timegap threshold for cluster assignment of items
        self.shopping_list = []

        # configure grid layout (4x4)
        #self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure((1, 2, 3), weight=1)
        self.grid_rowconfigure((0, 1, 2), weight=1)

        # sidebar frame
        self.sidebar_frame = CTk.CTkFrame(self, width=250, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, rowspan=4, sticky="nsew")
        self.logo_label = CTk.CTkLabel(self.sidebar_frame, text="Deep Rosa", font=CTk.CTkFont(size=20, weight="bold"))
        self.logo_label.grid(row=0, column=0, padx=20, pady=20)
        self.sidebar_upload_btn = CTk.CTkButton(self.sidebar_frame, text="Upload", command=self.upload_event)
        self.sidebar_upload_btn.grid(row=1, column=0, padx=20, pady=10)
        self.sidebar_reset_btn = CTk.CTkButton(self.sidebar_frame, text="Reset", fg_color="indianred1", command=self.reset_event)
        self.sidebar_reset_btn.grid(row=2, column=0, padx=20, pady=10)

        self.sidebar_cluster_var = tkinter.StringVar(value="No. of Clusters: 120")
        self.sidebar_cluster_label = CTk.CTkLabel(self.sidebar_frame, text=self.sidebar_cluster_var.get(), anchor='w')
        self.sidebar_cluster_label.grid(row=3, column=0, padx=20, pady=(10, 0))
        self.sidebar_cluster_slider = CTk.CTkSlider(self.sidebar_frame, from_=20, to=500, number_of_steps=480, command=self.change_cluster_slider_event)
        self.sidebar_cluster_slider.grid(row=4, column=0, padx=(20, 10), pady=(10, 10), sticky="ew")
        self.sidebar_threshold_var = tkinter.StringVar(value="Threshold Increment: 5")
        self.sidebar_threshold_label = CTk.CTkLabel(self.sidebar_frame, text=self.sidebar_threshold_var.get(), anchor='w')
        self.sidebar_threshold_label.grid(row=5, column=0, padx=20, pady=(10, 0))
        self.sidebar_threshold_slider = CTk.CTkSlider(self.sidebar_frame, from_=1, to=10, number_of_steps=9, command=self.change_threshold_slider_event)
        self.sidebar_threshold_slider.grid(row=6, column=0, padx=(20, 10), pady=(10, 10), sticky="ew")
        self.sidebar_cluster_btn = CTk.CTkButton(self.sidebar_frame, text="Cluster", command=self.cluster_event)
        self.sidebar_cluster_btn.grid(row=7, column=0, padx=20, pady=(10,10))

        self.plots_var = tkinter.IntVar(value=0)
        self.plots_radio_label = CTk.CTkLabel(self.sidebar_frame, text="Graph Selector")
        self.plots_radio_label.grid(row=8, column=0, padx=10, pady=10, stick="")
        self.items_graph_radio = CTk.CTkRadioButton(self.sidebar_frame, text="Items Graph", variable=self.plots_var, value=1, command=self.plot_preview_event)
        self.items_graph_radio.grid(row=9, column=0, pady=10, padx=20, sticky="w")
        self.cluster_graph_radio = CTk.CTkRadioButton(self.sidebar_frame, text="Cluster Graph", variable=self.plots_var, value=2, command=self.plot_preview_event)
        self.cluster_graph_radio.grid(row=10, column=0, pady=10, padx=20, sticky="w")
        self.distance_matrix_radio = CTk.CTkRadioButton(self.sidebar_frame, text="Distance Matrix", variable=self.plots_var, value=3, command=self.plot_preview_event)
        self.distance_matrix_radio.grid(row=11, column=0, pady=(10, 100), padx=20, sticky="w")

        self.ui_settings_label = CTk.CTkLabel(self.sidebar_frame, text="UI Settings:", anchor="w")
        self.ui_settings_label.grid(row=14, column=0, padx=20, pady=(10, 0))
        self.appearance_mode_menu = CTk.CTkOptionMenu(self.sidebar_frame, values=["System", "Light", "Dark"], command=self.change_appearance_mode_event)
        self.appearance_mode_menu.grid(row=15, column=0, padx=20, pady=(10, 20))

        # data info frame
        self.data_info_tab = CTk.CTkTabview(self, height=800, width=450)
        self.data_info_tab.grid(row=0, rowspan=2, column=1, padx=(10,5), pady=10, sticky="nsew")
        self.data_info_tab.add("General")
        self.data_info_tab.add("All Items")
        self.data_info_tab.add("Timegaps")
        self.data_info_tab.tab("General").grid_columnconfigure(0, weight=1)
        self.data_info_tab.tab("All Items").grid_columnconfigure(0, weight=1)
        self.data_info_tab.tab("Timegaps").grid_columnconfigure(0, weight=1)

        self.general_text = CTk.CTkTextbox(self.data_info_tab.tab("General"), height=800, width=470)
        self.general_text.grid(row=0, column=0, sticky="nsew")

        self.items_text = CTk.CTkTextbox(self.data_info_tab.tab("All Items"), height=800, width=470)
        self.items_text.grid(row=0, column=0, sticky="nsew")

        self.timegaps_text = CTk.CTkTextbox(self.data_info_tab.tab("Timegaps"), height=800, width=470)
        self.timegaps_text.grid(row=0, column=0, sticky="nsew")

        # clustered items frame
        self.cluster_info_frame = CTk.CTkFrame(self, width=250)
        self.cluster_info_frame.grid(row=0, column=2, padx=5, pady=(10,5), sticky="nsew")

        temp = []
        temp.append("Cluster 1")

        self.cluster_back_btn = CTk.CTkButton(master=self.cluster_info_frame, text="<", command=self.cluster_prev, width=50)
        self.cluster_back_btn.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")
        self.cluster_next_btn = CTk.CTkButton(master=self.cluster_info_frame, text=">", command=self.cluster_next, width=50)
        self.cluster_next_btn.grid(row=0, column=1, padx=5, pady=5, sticky="nsew")
        self.cluster_list_menu = CTk.CTkOptionMenu(master=self.cluster_info_frame, values=temp, command=self.print_cluster, width=50)
        self.cluster_list_menu.grid(row=0, column=2, padx=5, pady=5, sticky="nsew")
        self.cluster_info_text = CTk.CTkTextbox(master=self.cluster_info_frame, height=280)
        self.cluster_info_text.grid(row=1, column=0, columnspan=3, padx=5, pady=5, sticky="nsew")
        
        # shopping list 
        self.shopping_list_frame = CTk.CTkFrame(self, width=260)
        self.shopping_list_frame.grid(row=0, column=3, padx=(5,10), pady=(10,5), sticky="nsew")
        self.shopping_list_label = CTk.CTkLabel(master=self.shopping_list_frame, text="Shopping List", anchor="w")
        self.shopping_list_label.grid(row=0, column=0, columnspan=2, padx=5, pady=5, sticky="nsew")
        self.shopping_list_entry = CTk.CTkEntry(master=self.shopping_list_frame, placeholder_text="Search...")
        self.shopping_list_entry.grid(row=1, column=0, padx=5, pady=5, sticky="nsew")
        self.sort_list_btn = CTk.CTkButton(master=self.shopping_list_frame, text="Sort", command=self.sort_shopping_list, width=70)
        self.sort_list_btn.grid(row=1, column=1, padx=5, pady=5, sticky="nsew")
        self.shopping_list_text = CTk.CTkTextbox(master=self.shopping_list_frame, height=250)
        self.shopping_list_text.grid(row=2, column=0, columnspan=2, padx=5, pady=5, sticky="nsew")
        self.shopping_list_entry.bind("<Return>", self.search_item)

        # plot display frame
        self.plot_preview_frame = CTk.CTkFrame(self, height=520, width=520)
        self.plot_preview_frame.grid(row=1, rowspan=1, column=2, columnspan=2, padx=(5,10), pady=(5,10), sticky="nsew")

        # set default values
        self.appearance_mode_menu.set("System")
        self.reset_event()

    # UI EVENTS

    def change_appearance_mode_event(self, appearance_mode):
        if appearance_mode == 'System':
            CTk.set_appearance_mode("system")
        elif appearance_mode == 'Light':
            CTk.set_appearance_mode("light")
        elif appearance_mode == 'Dark':
            CTk.set_appearance_mode("dark")

    def change_cluster_slider_event(self, kcluster): 
        self.sidebar_cluster_var.set(f"No. of Clusters: {int(kcluster)}")
        self.sidebar_cluster_label = CTk.CTkLabel(self.sidebar_frame, text=self.sidebar_cluster_var.get(), anchor='w')
        self.sidebar_cluster_label.grid(row=3, column=0, padx=20, pady=(10, 0))
        self.max_clusters = int(kcluster)

    def change_threshold_slider_event(self, threshold): 
        self.sidebar_threshold_var.set(f"Threshold Increment: {int(threshold)}")
        self.sidebar_threshold_label = CTk.CTkLabel(self.sidebar_frame, text=self.sidebar_threshold_var.get(), anchor='w')
        self.sidebar_threshold_label.grid(row=5, column=0, padx=20, pady=(10, 0))
        self.threshold_increment = int(threshold)

    def print_data(self):
        self.running_time = 0
        self.general_text.configure(state='normal')
        self.general_text.delete(1.0, 'end')
        self.general_text.insert('end', f"Total Items: {len(self.item_list)}\n")
        self.general_text.insert('end', f"Total Pairs: {len(self.timegap_dict)}\n")
        self.general_text.insert('end', f"Total Shoppers: {self.total_shoppers}\n\n")
        self.general_text.insert('end', f"Running time: {self.running_time:.2f}s\n\n")
        self.general_text.configure(state='disabled')

        self.items_text.configure(state='normal')
        self.items_text.delete(1.0, 'end')
        for i, item in enumerate(self.item_list):
            self.items_text.insert('end', f"{i + 1}. {item}\n")
        self.items_text.configure(state='disabled')

        self.timegaps_text.configure(state='normal')
        self.timegaps_text.delete(1.0, 'end')
        for i, (key, value) in enumerate(self.timegap_dict.items()):
            item_x, item_y = key
            self.timegaps_text.insert('end', f"{i + 1}. {item_x}, {item_y} - {value:.2f}\n")
        self.timegaps_text.configure(state='disabled')

    '''
    def print_cluster(self, cluster_string, cluster_labels):
        cluster_int = int(cluster_string.split()[-1])
        self.k_pos = cluster_int
        self.cluster_info_text.configure(state='normal')
        self.cluster_info_text.delete(1.0, 'end')
        cluster_items = [item for i, item in enumerate(self.items) if cluster_labels[i] == cluster_int - 1]
        for i, item in enumerate(cluster_items):
            self.cluster_info_text.insert('end', f"{i+1}. {item}\n")
        self.cluster_info_text.configure(state='disabled')
    '''

    def print_cluster(self, cluster_string): 
        cluster_int = int(cluster_string.split()[-1])
        self.k_pos = cluster_int
        self.cluster_info_text.configure(state='normal')
        self.cluster_info_text.delete(1.0, 'end')
        cluster_items = self.cluster_dict.get(cluster_int-1, [])
        for i, item in enumerate(cluster_items):
            self.cluster_info_text.insert('end', f"{i+1}. {item}\n")
        self.cluster_info_text.configure(state='disabled')

    def print_shopping_list(self):
        self.shopping_list_text.configure(state='normal')
        self.shopping_list_text.delete(1.0, 'end')
        for i, item in enumerate(self.shopping_list):
            self.shopping_list_text.insert('end', f"{i+1}. {item}\n")
        self.shopping_list_text.configure(state='disabled')
    

    # BUTTON EVENTS
    
    def upload_event(self):
        file_path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
        df = pd.read_csv(file_path, header=None)
        self.item_list = sorted(df[(df.iloc[:, 2].apply(lambda x: isinstance(x, (int, float))) | \
                                    df.iloc[:, 2].apply(lambda x: str(x).isdigit() or x == 'Good'))].iloc[:, 0].unique())
        
        self.timegap_dict, self.total_shoppers = self.init_timegap()
        self.timegap_dict, self.total_shoppers = self.add_timegap(df) 
        self.timegap_dict = dict(sorted(self.timegap_dict.items(), key=lambda x: x[1]))     #sort from lowest timegap
        #self.approximate_missing_timegaps()
        self.print_data()
        self.data_info_tab.configure(state='normal')
        self.sidebar_upload_btn.configure(state='disabled')
        self.sidebar_cluster_slider.configure(state='normal')
        self.sidebar_threshold_slider.configure(state='normal')
        self.sidebar_cluster_btn.configure(state='normal')
        self.sidebar_reset_btn.configure(state='normal')
        self.shopping_list_entry.configure(state='normal')
        self.items_graph_radio.configure(state='normal')

    def cluster_event(self):
        self.dict_to_matrix()
        self.agglomerative_clustering()
        #self.cluster_dendrogram()
        self.export_as_csv()
        self.centroid_dict = self.calculate_centroid()
        #print(self.centroid_dict)
        #self.adjust_clusters()
        self.cluster_graph_radio.configure(state='normal')
        self.sidebar_cluster_slider.configure(state='disabled')
        self.sidebar_cluster_btn.configure(state='disabled')
        self.cluster_back_btn.configure(state='normal')
        self.cluster_next_btn.configure(state='normal')
        self.cluster_list_menu.configure(state='normal')
        temp = []
        for i in range(0, self.k):
            temp.append(f"Cluster {i+1}")
        self.cluster_list_menu.configure(values=temp)
        self.print_cluster("Cluster 1")
        

    def cluster_prev(self):
        direction = "prev"
        self.cluster_arrows_event(direction)

    def cluster_next(self):
        direction = "next"
        self.cluster_arrows_event(direction)
    
    def cluster_arrows_event(self, direction):
        if direction == "prev":
            self.k_pos = self.k_pos - 1
            if self.k_pos < 1:
                self.k_pos = self.k
        elif direction == "next":
            self.k_pos = self.k_pos + 1
            if self.k_pos > self.k:
                self.k_pos = 1

        self.cluster_list_menu.set(f"Cluster {self.k_pos}")
        self.print_cluster(f"Cluster {self.k_pos}")

    def reset_event(self):

        self.timegap_dict.clear()
        self.cluster_dict.clear()
        
        self.sidebar_upload_btn.configure(state='normal')

        self.data_info_tab.configure(state='disabled')
        self.general_text.configure(state='normal')
        self.items_text.configure(state='normal')
        self.timegaps_text.configure(state='normal')
        self.general_text.delete(1.0, 'end')
        self.items_text.delete(1.0, 'end')
        self.timegaps_text.delete(1.0, 'end')
        self.general_text.configure(state='disabled')
        self.items_text.configure(state='disabled')
        self.timegaps_text.configure(state='disabled') 

        self.sidebar_cluster_var = tkinter.StringVar(value="No. of Clusters: 120")
        self.sidebar_cluster_label.configure(text="No of Clusters: 120")  
        self.sidebar_cluster_slider.set(120) 
        self.sidebar_cluster_slider.configure(state='disabled')
        self.sidebar_threshold_var = tkinter.StringVar(value="Threshold Increment: 5")
        self.sidebar_threshold_label.configure(text="Threshold Increment: 5")
        self.sidebar_threshold_slider.set(5)
        self.sidebar_threshold_slider.configure(state='disabled')
        self.sidebar_cluster_btn.configure(state='disabled')
        self.sidebar_reset_btn.configure(state='disabled')

        self.cluster_back_btn.configure(state='disabled')
        self.cluster_next_btn.configure(state='disabled')
        self.cluster_list_menu.set("Cluster 1")
        self.cluster_list_menu.configure(state='disabled')
        self.cluster_info_text.configure(state='normal')
        self.cluster_info_text.delete(1.0, 'end')
        self.cluster_info_text.configure(state='disabled')

        self.shopping_list_entry.delete(0, 'end')
        self.shopping_list_entry.configure(state='disabled')
        self.shopping_list_text.configure(state='normal')
        self.shopping_list_text.delete(1.0, 'end')
        self.shopping_list_text.configure(state='disabled')

        self.plots_var.set(0)
        self.items_graph_radio.configure(state='disabled')
        self.cluster_graph_radio.configure(state='disabled')
        self.distance_matrix_radio.configure(state='disabled')

        for widget in self.plot_preview_frame.winfo_children():
            widget.destroy()

    def plot_preview_event(self):
        plots_var = self.plots_var.get()
        for widget in self.plot_preview_frame.winfo_children():
            widget.destroy()
            
        if plots_var == 1:
            self.items_graph()
        elif plots_var == 2:
            self.cluster_graph()
        elif plots_var == 3:
            self.distance_matrix()

    def search_item(self, key):
        if key:
            item = self.shopping_list_entry.get()
            if item in self.item_list:
                self.shopping_list.append(item)
                self.shopping_list_entry.delete(0, 'end')
                self.print_shopping_list()
                #print(self.shopping_list)

    # FUNCTIONS

    def init_timegap(self):
        timegap_dict = {}
        threshold_dict = {}
        total_shoppers = 0
        for key1 in self.item_list:
            for key2 in self.item_list:
                if key1 != key2:
                    pair = tuple(sorted((key1, key2)))
                    if pair not in timegap_dict:
                        timegap_dict[pair] = [100000]

        sorted_timegap_dict = dict(sorted(timegap_dict.items(), key=lambda x: x[0]))

        for pair in sorted_timegap_dict:
            threshold_dict[pair] = 0
        
        self.threshold_dict = threshold_dict
        return sorted_timegap_dict, total_shoppers
 
    def add_timegap(self, df):
        #start_time = time.time()
        timegap_dict = self.timegap_dict
        total_shoppers = self.total_shoppers
        temp_dict = {}

        print_max = 1
        for index in range(len(df)):
            value_x = df.iloc[index, 1]
            if value_x == 0:
                print_max+=1
        
        print_max = int(print_max/5)
        print_count = 0

        for index in range(len(df)):
            item_x = df.iloc[index, 0]
            value_x = df.iloc[index, 1]
            if index == len(df) - 1:
                value_x_next = 0
            else:
                value_x_next = df.iloc[index + 1, 1] 
            status_x = df.iloc[index, 2]

            if (isinstance(status_x, (int, float)) or str(status_x).isdigit() or status_x == 'Good'):
                # if first item in the last
                if value_x == 0:
                    total_shoppers += 1
                    temp_dict.clear()
                    temp_dict[item_x] = value_x

                else:
                    temp_dict[item_x] = value_x

                # if last item in list
                if value_x_next == 0 and len(temp_dict) != 1:
                    sorted_keys = sorted(temp_dict.keys())
                    num_items = len(sorted_keys)

                    for i in range(num_items - 1):
                        key1 = list(temp_dict.keys())[i]
                        key2 = list(temp_dict.keys())[i + 1]
                        pair = tuple(sorted((key1, key2)))
                        diff = abs(temp_dict[key1] - temp_dict[key2])

                        if pair in timegap_dict:
                            if diff < (int(timegap_dict[pair][-1]) - 10) or diff > (int(timegap_dict[pair][-1]) + 10):
                                self.threshold_dict[pair] += 1
                                if self.threshold_dict[pair] >= 3:
                                    timegap_dict[pair] = [sum(timegap_dict[pair]) / len(timegap_dict[pair])]
                                    self.threshold_dict[pair] == 0

                            timegap_dict[pair].append(diff)
                        else:
                            timegap_dict[pair] = [diff]

                    temp_dict.clear()
                    
                    print_count+=1
                    #print(f"{print_count} / {print_max}")

                    '''
                    if print_count == print_max or index == len(df) - 1:
                        for pair in timegap_dict:
                            temp_dict[pair] = sum(timegap_dict[pair]) / len(timegap_dict[pair])

                        self.timegap_dict = dict(sorted(temp_dict.items(), key=lambda x: x[0]))
                        temp_dict.clear()

                        self.dict_to_matrix()
                        self.kmeans_clustering()
                        self.cluster_graph(0, 17)
                        print_count = 0                  
                    '''


        for key in timegap_dict:
            timegap_dict[key] = sum(timegap_dict[key]) / len(timegap_dict[key])

        sorted_timegap_dict = dict(sorted(timegap_dict.items(), key=lambda x: x[0]))

        #end_time = time.time()
        return sorted_timegap_dict, total_shoppers
    
    def dict_to_matrix(self):
        items = self.item_list
        matrix = np.zeros((len(items), len(items)))

        for i in range(len(items)):
            for j in range(len(items)):
                if i != j:
                    key = (items[i], items[j])
                    if key in self.timegap_dict:
                        matrix[i][j] = self.timegap_dict[key]
                        matrix[j][i] = self.timegap_dict[key]

        self.timegap_matrix = matrix
    
    def kmeans_clustering(self):
        k = 120
        kmeans = KMeans(n_clusters=k, n_init=10)
        kmeans.fit(self.timegap_matrix)
        cluster_labels = kmeans.labels_
        clustered_items = {}
        total_clusters = len(set(cluster_labels))

        for cluster in range(total_clusters):
            clustered_items[cluster] = []

        for item, label in zip(self.item_list, cluster_labels):
            clustered_items[label].append(item)
        
        self.cluster_dict = clustered_items
        self.k = 120

    def cluster_graph(self, i, j):
        distances1 = []  # Distances from item 1
        distances2 = []  # Distances from item 2

        for _, items in self.cluster_dict.items():
            for item in items:
                distance1 = self.timegap_dict.get((self.item_list[i], item), 0.0)
                distance2 = self.timegap_dict.get((self.item_list[j], item), 0.0)
                distances1.append(distance1)
                distances2.append(distance2)

        plt.figure(figsize=(8, 6))
        plt.scatter(distances1, distances2, c='blue', marker='o', label='Clustered Items')
        plt.xlabel(f'Distance from Item {self.item_list[i]}')
        plt.ylabel(f'Distance from Item {self.item_list[j]}')
        plt.title(f'Scatter Plot of Clustered Items')
        plt.legend()
        plt.grid(True)
        plt.show()
    
    def agglomerative_clustering(self):
        k = 120
        agglomerative = AgglomerativeClustering(n_clusters=k, affinity='precomputed', linkage='complete')
        cluster_labels = agglomerative.fit_predict(self.timegap_matrix)

        # Create a dictionary to store the cluster assignments
        clustered_items = {}
        for label in set(cluster_labels):
            clustered_items[label] = []

        # Assign items to clusters
        for item, label in zip(self.item_list, cluster_labels):
            clustered_items[label].append(item)

        self.cluster_dict = clustered_items
        print(self.cluster_dict)
        self.k = 120

    def cluster_dendrogram(self):
        # Calculate the linkage matrix from the distances
        distances = [self.cluster_dict[label] for label in sorted(self.cluster_dict.keys())]
        linkage_matrix = linkage(distances, method='ward')  # You can adjust the linkage method as needed

        plt.figure(figsize=(10, 8))
        dendrogram(linkage_matrix, labels=sorted(self.cluster_dict.keys()))
        plt.xlabel('Cluster Index')
        plt.ylabel('Distance')
        plt.title('Dendrogram of Agglomerative Clustering')
        plt.show()

    def calculate_centroid(self):
        centroid_dict = {}

        for cluster_index, cluster_items in self.cluster_dict.items():
            for i in range(0, len(cluster_items)-1):
                item_x = cluster_items[i]
                for j in range(0, len(cluster_items)-1):
                    if i != j:
                        item_y = cluster_items[j]
                        pair = (item_x, item_y)
                        sorted_pair = tuple(sorted(list(pair)))
                        if sorted_pair in self.timegap_dict:
                            if cluster_index not in centroid_dict:
                                centroid_dict[cluster_index] = []
                            centroid_dict[cluster_index].append(self.timegap_dict[sorted_pair])

        for cluster_index, cluster_values in centroid_dict.items():
            if len(cluster_values) > 0:
                centroid_dict[cluster_index] = sum(cluster_values) / len(cluster_values)
        
        return centroid_dict     

    def sort_shopping_list(self):
        self.sorted_list = self.shopping_list
        self.cluster_anchor = 0
        self.sorted_list = sorted(
            self.sorted_list,
            key=lambda x: (
                -1 if any(x in value for value in self.cluster_dict.get(self.cluster_anchor-1, [])) else 0,
                next((key for key, value in self.cluster_dict.items() if x in value), 0)
            )
        )

        for i in range(len(self.sorted_list) - 1):
            item_x = self.sorted_list[i]
            item_y = self.sorted_list[i + 1]
            cluster_x = next((key for key, value in self.cluster_dict.items() if item_x in value), None)
            cluster_y = next((key for key, value in self.cluster_dict.items() if item_y in value), None)

            if cluster_x is not None and cluster_x == cluster_y:
                continue

            min_timegap = float('inf')
            min_timegap_item = None

            for j in range(i + 1, len(self.sorted_list)):
                next_item = self.sorted_list[j]

                if (item_x, next_item) in self.timegap_dict:
                    timegap = self.timegap_dict[(item_x, next_item)]

                    if timegap < min_timegap:
                        min_timegap = timegap
                        min_timegap_item = next_item

            if min_timegap_item is not None:
                index_min_timegap_item = self.sorted_list.index(min_timegap_item)
                self.sorted_list[i + 1], self.sorted_list[index_min_timegap_item] = self.sorted_list[index_min_timegap_item], self.sorted_list[i + 1]

        self.shopping_list = self.sorted_list
        self.print_shopping_list()

    def approximate_missing_timegaps(self):
        lowest = None
        item_combinations = list(combinations(self.item_list, 2))
        for pair in item_combinations:
            z1, z2 = pair
            if pair not in self.timegap_dict:
                new_dict = {}
                for pair1, timegap1 in self.timegap_dict.items():
                    x1, x2 = pair1
                    for pair2, timegap2 in self.timegap_dict.items():
                        y1, y2 = pair2
                        if (
                            (x1 == y1 and y2 == z1 and x2 == z2) or (x1 == y1 and x2 == z1 and y1 == z2) or
                            (y1 == z1 and x1 == y2 and x2 == z2) or (y1 == z1 and x1 == z2 and x2 == y2) or
                            (x1 == z1 and x1 == y1 and y2 == z2) or (x1 == z1 and y1 == z2 and x2 == y2)
                        ):
                            timegap_sum = timegap1 + timegap2
                            if lowest is None or timegap_sum < lowest:
                                lowest = timegap_sum
                                new_dict = {}
                                new_dict[pair1] = timegap1
                                new_dict[pair2] = timegap2

                temp_dict = {}
                timegap = timegap1 + timegap2
                temp_dict[pair] = timegap

        self.timegap_dict = {**self.timegap_dict, **temp_dict}

    def export_as_csv(self):
        # Prepare CSV data
        csv_data = []
        for cluster, items in self.cluster_dict.items():
            for item in items:
                csv_data.append([item, cluster])

        # Create a CSV string
        csv_string = ""
        with open('clusters.csv', mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['Item', 'Cluster'])
            writer.writerows(csv_data)
        
        return csv_string


dprosa = dprosaGUI()
dprosa.mainloop()