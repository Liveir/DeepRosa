"""
MainView

Root window for DeepRosa experimenting application.

Authors: Johnfil Initan, Vince Abella, Jake Perez

"""

import pandas as pd
import numpy as np
import time

import customtkinter as CTk
import tkinter as Tk
from tkinter import filedialog
from PIL import Image

from Models._dprosa import \
    initialize_timegap, add_timegap, check_timegap, normalize_timegaps,\
    dict_to_matrix, sort_shopping_list, \
    agglomerative_clustering, kmeans_clustering, affinity_propagation_clustering

from Views.PlotView import PlotDataPopup

########################################################
CTk.set_appearance_mode("system")
CTk.set_default_color_theme("green")

########################################################
# Main Interface

class DeepRosaGUI(CTk.CTk):
    """
    Deep Rosa GUI

    Graphical user interface for the Deep Rosa experimenting application.

    Attributes
    -----------
    default_timegap : int
        The default value set for all pairs created during the 
        initialization of timegap_dict.
    
    item_list : list
        A list of all grocery items in a supermarket.

    total_shoppers : int
        This is equivalent to the total number of concatenated
        shopping lists read from a CSV file.
    
    timegap_dict : dict
        A dictionary containing pairs of items as keys (thus 
        length of the dictionary is equal to the combination
        of 2 items from a set of N set of items where N is the
        length of item_list), while the values are the timegaps
        between the two items.
    
    threshold_dict : dict
        A dictionary containing the same keys in timegap_dict,
        but the values are threshold values which is referenced
        in order to determine whether an item has multiple
        instances or if the item was reshelved.

    cluster_dict : dict
        A dictionary containing cluster numbers as keys, and a
        list of string-type items as the values.
    
    timegap_matrix : NumPy array
        A distance matrix used to store the data in timegap_dict
        but represented in matrix form. This is used as the input
        for AgglomerativeClustering, and other possible models
        that can use precomputed distance matrices as inputs. For
        KMeansClustering, this is automatically converted to a
        dissimilarity matrix; while for AffinityPropagation, this
        is automatically converted to a similarity matrix.
    
    default_n_clusters : int
        The default number of clusters used for the clustering
        models. This value is initialized when launching the GUI,
        and stored in a different, adjustable variable via a
        slider. For AgglomerativeClustering, the slider must be
        set to 0 if the distance threshold is not 0. For 
        KMeansClustering, the slider must not be 0. For 
        AffinityPropagation, this does not matter.
    
    default_distance_threshold : int
        The default number of clusters used for the clustering
        models. This value is initialized when launching the GUI,
        and stored in a different, adjustable variable via a
        slider. For AgglomerativeClustering, the slider must be
        set to 0 if the number of clusters is not 0. For 
        AffinityPropagation and KMeansClustering, the slider 
        does not matter. 

    shopping_list : list
        A list of shopping lists that simulates the actual
        grocery shopping experience.
        
    """
    def __init__(self):

        super().__init__()

        # configure window
        self.title("Deep Rosa v1.7")
        self.geometry("1200x1000")

        # initialize class variables
        self.default_timegap = 10000
        self.item_list = []
        self.total_shoppers = 0
        self.timegap_dict = {}
        self.threshold_dict = {}
        self.cluster_dict = {}
        self.clustergap_dict = {}
        self.timegap_matrix = np.array([])
        self.default_n_clusters = 0
        self.default_distance_threshold = 60
        self.shopping_list = []


        # configure grid layout (4x4)
        self.grid_columnconfigure((1, 2, 3), weight=1)
        self.grid_rowconfigure((0, 1, 2), weight=1)

        # sidebar frame
        self.sidebar_frame = CTk.CTkFrame(self, width=250, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, rowspan=4, sticky="nsew")
        self.logo = CTk.CTkImage(light_image=Image.open("Assets/DeepRosa.png"),
                                 dark_image=Image.open("Assets/DeepRosa.png"),
                                 size=(120,120)
                                 )
        self.logo_label = CTk.CTkLabel(self.sidebar_frame, image=self.logo, text="", font=CTk.CTkFont(size=20, weight="bold"))
        self.logo_label.grid(row=1, column=0, padx=20, pady=(20,5))
        self.app_label = CTk.CTkLabel(self.sidebar_frame, text="Deep Rosa", font=CTk.CTkFont(size=20, weight="bold"))
        self.app_label.grid(row=2, column=0, padx=20, pady=(5,50))

        self.sidebar_import_btn = CTk.CTkButton(self.sidebar_frame, text="Import", command=self.import_event)
        self.sidebar_import_btn.grid(row=4, column=0, padx=20, pady=10)
        self.sidebar_plot_btn = CTk.CTkButton(self.sidebar_frame, text="Plot", command=self.plot_event)
        self.sidebar_plot_btn.grid(row=5, column=0, padx=20, pady=10)
        self.sidebar_reset_btn = CTk.CTkButton(self.sidebar_frame, text="Reset", fg_color="indianred1", command=self.reset_event)
        self.sidebar_reset_btn.grid(row=6, column=0, padx=20, pady=10)

        self.sidebar_nclusters_var = Tk.StringVar(value=f"No. of Clusters: {self.default_n_clusters}")
        self.sidebar_cluster_label = CTk.CTkLabel(self.sidebar_frame, text=self.sidebar_nclusters_var.get())
        self.sidebar_cluster_label.grid(row=8, column=0, padx=20, pady=(10, 0))
        self.sidebar_cluster_slider = CTk.CTkSlider(self.sidebar_frame, from_=0, to=500, number_of_steps=501, command=self.change_cluster_slider_event)
        self.sidebar_cluster_slider.grid(row=9, column=0, padx=(20, 10), pady=(10, 10), sticky="ew")

        self.sidebar_threshold_var = Tk.StringVar(value=f"Cluster Threshold: {self.default_distance_threshold}")
        self.sidebar_threshold_label = CTk.CTkLabel(self.sidebar_frame, text=self.sidebar_threshold_var.get())
        self.sidebar_threshold_label.grid(row=10, column=0, padx=20, pady=(10, 0))
        self.sidebar_threshold_slider = CTk.CTkSlider(self.sidebar_frame, from_=0, to=100, number_of_steps=101, command=self.change_threshold_slider_event)
        self.sidebar_threshold_slider.grid(row=11, column=0, padx=(20, 10), pady=(10, 10), sticky="ew")

        self.sidebar_cluster_btn = CTk.CTkButton(self.sidebar_frame, text="Cluster", command=self.cluster_event)
        self.sidebar_cluster_btn.grid(row=12, column=0, padx=20, pady=(10,10))

        self.cluster_radio_sel = Tk.IntVar(value=1)
        self.cluster_radio_label = CTk.CTkLabel(self.sidebar_frame, text="Clustering Model")
            
        self.agglo_cluster_radio = CTk.CTkRadioButton(self.sidebar_frame, text="Agglomerative", variable=self.cluster_radio_sel, value=1, command=self.clustering_select_event)
        self.agglo_cluster_radio.grid(row=14, column=0, pady=10, padx=30, sticky="w")
        self.kmeans_cluster_radio = CTk.CTkRadioButton(self.sidebar_frame, text="K-Means", variable=self.cluster_radio_sel, value=2, command=self.clustering_select_event)
        self.kmeans_cluster_radio.grid(row=15, column=0, pady=10, padx=30, sticky="w")
        self.affinity_cluster_radio = CTk.CTkRadioButton(self.sidebar_frame, text="Affinity Propagation", variable=self.cluster_radio_sel, value=3, command=self.clustering_select_event)
        self.affinity_cluster_radio.grid(row=16, column=0, pady=10, padx=30, sticky="w")

        self.ui_settings_label = CTk.CTkLabel(self.sidebar_frame, text="UI Settings:", anchor="w")
        self.ui_settings_label.grid(row=17, column=0, padx=20, pady=(10, 0))
        self.appearance_mode_menu = CTk.CTkOptionMenu(self.sidebar_frame, values=["System", "Light", "Dark"], command=self.change_appearance_mode_event)
        self.appearance_mode_menu.grid(row=18, column=0, padx=20, pady=(10, 20))

        # data info frame
        self.data_info_tab = CTk.CTkTabview(self, height=800, width=450)
        self.data_info_tab.grid(row=0, rowspan=2, column=1, padx=(10,5), pady=10, sticky="nsew")
        self.data_info_tab.add("General")
        self.data_info_tab.add("All Items")
        self.data_info_tab.add("Item Timegaps")
        self.data_info_tab.add("Cluster Timegaps")

        self.data_info_tab.tab("General").grid_columnconfigure(0, weight=1)
        self.data_info_tab.tab("All Items").grid_columnconfigure(0, weight=1)
        self.data_info_tab.tab("Item Timegaps").grid_columnconfigure(0, weight=1)
        self.data_info_tab.tab("Cluster Timegaps").grid_columnconfigure(0, weight=1)

        self.general_text = CTk.CTkTextbox(self.data_info_tab.tab("General"), height=800, width=470)
        self.general_text.grid(row=0, column=0, sticky="nsew")

        self.items_text = CTk.CTkTextbox(self.data_info_tab.tab("All Items"), height=800, width=470)
        self.items_text.grid(row=0, column=0, sticky="nsew")

        self.timegaps_text = CTk.CTkTextbox(self.data_info_tab.tab("Item Timegaps"), height=800, width=470)
        self.timegaps_text.grid(row=0, column=0, sticky="nsew")

        self.clustergaps_text = CTk.CTkTextbox(self.data_info_tab.tab("Cluster Timegaps"), height=800, width=470)
        self.clustergaps_text.grid(row=0, column=0, sticky="nsew")

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
        self.shopping_list_entry = CTk.CTkEntry(master=self.shopping_list_frame, placeholder_text="Add an item...")
        self.shopping_list_entry.grid(row=1, column=0, padx=5, pady=5, sticky="nsew")
        self.sort_list_btn = CTk.CTkButton(master=self.shopping_list_frame, text="Sort", width=70, command=self.sort_shopping_list)
        self.sort_list_btn.grid(row=1, column=1, padx=5, pady=5, sticky="nsew")
        self.shopping_list_text = CTk.CTkTextbox(master=self.shopping_list_frame, height=200)
        self.shopping_list_text.grid(row=2, column=0, columnspan=2, padx=5, pady=5, sticky="nsew")
        self.shopping_list_entry.bind("<Return>", self.add_item_to_list)

        self.pick_list_entry = CTk.CTkEntry(master=self.shopping_list_frame, placeholder_text="Pick an item...")
        self.pick_list_entry.grid(row=3, column=0, padx=5, pady=5, sticky="nsew")
        self.clear_list_btn = CTk.CTkButton(master=self.shopping_list_frame, text="Clear", width=70, fg_color="indianred1", command=self.clear_shopping_list)
        self.clear_list_btn.grid(row=3, column=1, padx=5, pady=5, sticky="nsew")
        self.pick_list_entry.bind("<Return>", self.pick_from_shopping_list)

        # plot display frame
        self.plot_preview_frame = CTk.CTkFrame(self, height=100, width=520)
        self.plot_preview_frame.grid(row=1, rowspan=1, column=2, columnspan=2, padx=(5,10), pady=(5,10), sticky="nsew")

        # set default values
        self.appearance_mode_menu.set("System")
        self.reset_event()



    ####### UI EVENTS ######

    def change_appearance_mode_event(self, appearance_mode):
        if appearance_mode == 'System':
            CTk.set_appearance_mode("system")
        elif appearance_mode == 'Light':
            CTk.set_appearance_mode("light")
        elif appearance_mode == 'Dark':
            CTk.set_appearance_mode("dark")

    def change_cluster_slider_event(self, nclusters): 
        self.sidebar_nclusters_var.set(f"No. of Clusters: {int(nclusters)}")
        self.sidebar_cluster_label.configure(text=f"No. of Clusters: {int(nclusters)}")
        self.nclusters_var = int(nclusters)

    def change_threshold_slider_event(self, threshold): 
        self.sidebar_threshold_var.set(f"Distance Threshold: {int(threshold)}")
        self.sidebar_threshold_label.configure(text=f"Distance Threshold: {int(threshold)}")
        self.threshold_var = int(threshold)

    def cluster_prev(self):
        direction = "prev"
        self.cluster_arrows_event(direction)

    def cluster_next(self):
        direction = "next"
        self.cluster_arrows_event(direction)
    
    def cluster_arrows_event(self, direction):
        if direction == "prev":
            self.cluster_pos = self.cluster_pos - 1
            if self.cluster_pos < 1:
                self.cluster_pos = self.n_clusters
        elif direction == "next":
            self.cluster_pos = self.cluster_pos + 1
            if self.cluster_pos > self.n_clusters:
                self.cluster_pos = 1

        self.cluster_list_menu.set(f"Cluster {self.cluster_pos}")
        self.print_cluster(f"Cluster {self.cluster_pos}")

    def clustering_select_event(self):
        self.cluster_sel = self.cluster_radio_sel.get()



    ####### PRINT EVENTS ######

    def print_data(self):
        # Print General Information
        self.general_text.configure(state='normal')
        self.general_text.delete(1.0, 'end')
        self.general_text.insert('end', f"Total Items: {len(self.item_list)}\n")
        self.general_text.insert('end', f"Total Pairs: {len([key for key in self.timegap_dict if self.timegap_dict[key] != self.default_timegap])}\n")
        self.general_text.insert('end', f"Total Shoppers: {self.total_shoppers}\n")
        self.general_text.configure(state='disabled')
        
        # Print All Items
        self.items_text.configure(state='normal')
        self.items_text.delete(1.0, 'end')
        for i, item in enumerate(self.item_list):
            self.items_text.insert('end', f"{i + 1}. {item}\n")
        self.items_text.configure(state='disabled')

        # Print Timegaps
        self.timegaps_text.configure(state='normal')
        self.timegaps_text.delete(1.0, 'end')
        for i, (key, value) in enumerate(self.timegap_dict.items()):
            item_x, item_y = key
            if value < self.default_timegap:
                self.timegaps_text.insert('end', f"{i + 1}. {item_x}, {item_y} - {value:.2f}\n")
        self.timegaps_text.configure(state='disabled')

        # Print Proximity Calculation Time
        self.general_text.configure(state='normal')
        self.general_text.insert('end', f"Proximity Calculation Time: {self.proximity_time:.2f}s\n\n")
        self.general_text.configure(state='disabled')

    def print_cluster(self, cluster_string): 
        cluster_int = int(cluster_string.split()[-1])
        self.cluster_pos = cluster_int
        self.cluster_info_text.configure(state='normal')
        self.cluster_info_text.delete(1.0, 'end')
        cluster_items = self.cluster_dict.get(cluster_int-1, [])
        for i, item in enumerate(cluster_items):
            self.cluster_info_text.insert('end', f"{i+1}. {item}\n")
        self.cluster_info_text.configure(state='disabled')

    def print_cluster_timegaps(self):
        self.clustergaps_text.configure(state='normal')
        for i, (key, value) in enumerate(self.clustergap_dict.items()):
            cluster_x, cluster_y = key
            self.clustergaps_text.insert('end', f"Cluster {cluster_x+1}, Cluster {cluster_y+1} - {value:.2f}\n")
        self.clustergaps_text.configure(state='disabled')

    def print_shopping_list(self):
        self.shopping_list_text.configure(state='normal')
        self.shopping_list_text.delete(1.0, 'end')
        for i, item in enumerate(self.shopping_list):
            self.shopping_list_text.insert('end', f"{i+1}. {item}\n")
        self.shopping_list_text.configure(state='disabled')






    ###### MAIN FUNCTIONS #####

    def reset_event(self):

        self.timegap_dict.clear()
        self.cluster_dict.clear()
        self.shopping_list.clear()
        self.timegap_matrix = np.array([])
        
        self.sidebar_import_btn.configure(state='normal')
        self.sidebar_plot_btn.configure(state='normal')

        self.nclusters_var = self.default_n_clusters
        self.threshold_var = self.default_distance_threshold
        self.sidebar_nclusters_var = Tk.StringVar(value=f"No. of Clusters: {self.default_n_clusters}")
        self.sidebar_cluster_label.configure(text=f"No of Clusters: {self.default_n_clusters}")  
        self.sidebar_cluster_slider.set(self.default_n_clusters) 
        self.sidebar_cluster_slider.configure(state='disabled')
        self.sidebar_threshold_var = Tk.StringVar(value=f"Distance Threshold: {self.default_distance_threshold}")
        self.sidebar_threshold_label.configure(text=f"Distance Threshold: {self.default_distance_threshold}")
        self.sidebar_threshold_slider.set(self.default_distance_threshold)
        self.sidebar_threshold_slider.configure(state='disabled')
        self.sidebar_cluster_btn.configure(state='disabled')
        self.sidebar_reset_btn.configure(state='disabled')

        self.data_info_tab.configure(state='disabled')
        self.general_text.configure(state='normal')
        self.items_text.configure(state='normal')
        self.timegaps_text.configure(state='normal')
        self.clustergaps_text.configure(state='normal')
        self.general_text.delete(1.0, 'end')
        self.items_text.delete(1.0, 'end')
        self.timegaps_text.delete(1.0, 'end')
        self.clustergaps_text.delete(1.0, 'end')
        self.general_text.configure(state='disabled')
        self.items_text.configure(state='disabled')
        self.timegaps_text.configure(state='disabled') 
        self.clustergaps_text.configure(state='disabled') 

        self.cluster_back_btn.configure(state='disabled')
        self.cluster_next_btn.configure(state='disabled')
        self.cluster_list_menu.set("Cluster 1")
        self.cluster_list_menu.configure(state='disabled')
        self.cluster_info_text.configure(state='normal')
        self.cluster_info_text.delete(1.0, 'end')
        self.cluster_info_text.configure(state='disabled')

        self.shopping_list_entry.delete(0, 'end')
        self.shopping_list_entry.configure(state='disabled')
        self.sort_list_btn.configure(state='disabled')
        self.shopping_list_text.configure(state='normal')
        self.shopping_list_text.delete(1.0, 'end')
        self.shopping_list_text.configure(state='disabled')
        self.pick_list_entry.delete(0, 'end')
        self.pick_list_entry.configure(state='disabled')
        self.clear_list_btn.configure(state='disabled')

        self.cluster_radio_sel.set(1)
        self.clustering_select_event()
        self.agglo_cluster_radio.configure(state='disabled')
        self.agglo_cluster_radio.select()
        self.kmeans_cluster_radio.configure(state='disabled')
        self.affinity_cluster_radio.configure(state='disabled')


        self.toplevel_window = None

    def import_event(self):
        file_path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
        df = pd.read_csv(file_path, header=None)
        self.item_list = sorted(df[(df.iloc[:, 2].apply(lambda x: isinstance(x, (int, float))) | \
                                    df.iloc[:, 2].apply(lambda x: str(x).isdigit() or x == 'Good'))].iloc[:, 0].unique())

        start_time = time.time()
        self.timegap_dict, self.threshold_dict = initialize_timegap(self.item_list, self.default_timegap)
        self.timegap_dict, self.total_shoppers = add_timegap(df, self.timegap_dict, self.threshold_dict, True) 
        self.timegap_dict = normalize_timegaps(self.timegap_dict)
        #self.instances_dict = item_instances(self.timegap_dict)
        self.timegap_dict = dict(sorted(self.timegap_dict.items(), key=lambda x: x[1]))     #sort from lowest timegap
        end_time = time.time()
        self.proximity_time = abs(start_time-end_time)

        self.print_data()

        self.data_info_tab.configure(state='normal')
        self.sidebar_import_btn.configure(state='disabled')
        self.sidebar_cluster_slider.configure(state='normal')
        self.sidebar_threshold_slider.configure(state='normal')
        self.sidebar_cluster_btn.configure(state='normal')
        self.sidebar_reset_btn.configure(state='normal')
        self.kmeans_cluster_radio.configure(state='normal')
        self.agglo_cluster_radio.configure(state='normal')
        self.affinity_cluster_radio.configure(state='normal')


    def cluster_event(self):
        self.timegap_matrix = dict_to_matrix(self.item_list, self.timegap_dict)

        start_time = time.time()
        if self.cluster_sel == 1:
            self.cluster_dict, self.clustergap_dict, self.n_clusters= agglomerative_clustering(self.item_list, self.timegap_matrix, self.threshold_var, self.nclusters_var)
        elif self.cluster_sel == 2:
            self.cluster_dict, self.n_clusters= kmeans_clustering(self.item_list, self.timegap_matrix, self.nclusters_var)
        elif self.cluster_sel == 3:
            self.cluster_dict, self.clustergap_dict, self.n_clusters= affinity_propagation_clustering(self.item_list, self.timegap_matrix, 0.9, 500, 15)
        
        end_time = time.time()
        self.clustering_time = abs(start_time-end_time)
        self.print_cluster_timegaps()

        self.cluster_back_btn.configure(state='normal')
        self.cluster_next_btn.configure(state='normal')
        self.cluster_list_menu.configure(state='normal')
        temp = []
        for i in range(0, self.n_clusters):
            temp.append(f"Cluster {i+1}")
        self.cluster_list_menu.configure(values=temp)
        self.print_cluster("Cluster 1")

        self.print_data()
        self.general_text.configure(state='normal')
        self.general_text.insert('end', f"Total Clusters: {self.n_clusters}\n")
        self.general_text.configure(state='disabled')

        self.general_text.configure(state='normal')
        self.general_text.insert('end', f"Time to cluster: {self.clustering_time:.2f}\n\n")
        self.general_text.configure(state='disabled')

        self.shopping_list_entry.configure(state='normal')
        self.sort_list_btn.configure(state='normal')
        self.pick_list_entry.configure(state='normal')
        self.clear_list_btn.configure(state='normal')
        

    def plot_event(self):
        if self.toplevel_window is None or not self.toplevel_window.winfo_exists():
            self.toplevel_window = PlotDataPopup()  # create window if its None or destroyed
        else:
            self.toplevel_window.focus()  # if window exists focus it
    
    
    ###### SORT EVENTS #####

    def add_item_to_list(self, key):
        if key:
            item = self.shopping_list_entry.get()
            if item in self.item_list:
                self.shopping_list.append(item)
                self.shopping_list_entry.delete(0, 'end')
                self.print_shopping_list()

    def sort_shopping_list(self):
        self.shopping_list = sort_shopping_list(None, self.shopping_list, self.clustergap_dict, self.cluster_dict)
        self.print_shopping_list()
    
    def pick_from_shopping_list(self, key):
        if key:
            if self.shopping_list:
                item = self.pick_list_entry.get()
                if item in self.shopping_list:
                    self.shopping_list = sort_shopping_list(item, self.shopping_list, self.clustergap_dict, self.cluster_dict)
                    self.shopping_list.remove(item)
                    self.print_shopping_list()
                    self.pick_list_entry.delete(0, 'end')
 
    def clear_shopping_list(self):
        self.shopping_list.clear()
        self.shopping_list_text.configure(state='normal')
        self.shopping_list_text.delete(1.0, 'end')
        self.shopping_list_text.configure(state='disabled')
