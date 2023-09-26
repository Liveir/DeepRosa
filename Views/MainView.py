import customtkinter as CTk
import tkinter as Tk

class GUI(CTk.CTk):
    def __init__(self):
        super().__init__()

        # configure window
        self.title("Deep Rosa Visualizer")
        self.geometry("1200x1000")
        self.timegap_dict = {}
        self.cluster_dict = {}
        self.max_clusters = 60 # maximum number of clusters allowed (does not have to be reached)
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
        self.sidebar_import_btn = CTk.CTkButton(self.sidebar_frame, text="import", command=self.import_event)
        self.sidebar_import_btn.grid(row=1, column=0, padx=20, pady=10)
        self.sidebar_reset_btn = CTk.CTkButton(self.sidebar_frame, text="Reset", fg_color="indianred1", command=self.reset_event)
        self.sidebar_reset_btn.grid(row=2, column=0, padx=20, pady=10)

        self.sidebar_cluster_var = Tk.StringVar(value="No. of Clusters: 60")
        self.sidebar_cluster_label = CTk.CTkLabel(self.sidebar_frame, text=self.sidebar_cluster_var.get(), anchor='w')
        self.sidebar_cluster_label.grid(row=3, column=0, padx=20, pady=(10, 0))
        self.sidebar_cluster_slider = CTk.CTkSlider(self.sidebar_frame, from_=20, to=500, number_of_steps=480, command=self.change_cluster_slider_event)
        self.sidebar_cluster_slider.grid(row=4, column=0, padx=(20, 10), pady=(10, 10), sticky="ew")
        self.sidebar_threshold_var = Tk.StringVar(value="Threshold Increment: 5")
        self.sidebar_threshold_label = CTk.CTkLabel(self.sidebar_frame, text=self.sidebar_threshold_var.get(), anchor='w')
        self.sidebar_threshold_label.grid(row=5, column=0, padx=20, pady=(10, 0))
        self.sidebar_threshold_slider = CTk.CTkSlider(self.sidebar_frame, from_=1, to=10, number_of_steps=9, command=self.change_threshold_slider_event)
        self.sidebar_threshold_slider.grid(row=6, column=0, padx=(20, 10), pady=(10, 10), sticky="ew")
        self.sidebar_cluster_btn = CTk.CTkButton(self.sidebar_frame, text="Cluster", command=self.cluster_event)
        self.sidebar_cluster_btn.grid(row=7, column=0, padx=20, pady=(10,10))

        self.plots_var = Tk.IntVar(value=0)
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

app = GUI()
app.mainloop()