import pandas as pd
import numpy as np
from scipy.cluster.hierarchy import dendrogram, linkage
from sklearn.cluster import AgglomerativeClustering
#import math
import csv
import time
import os

from Models._dprosa import \
    initialize_timegap, add_timegap, check_timegap, normalize_timegaps,\
    dict_to_matrix, agglomerative_clustering, kmeans_clustering, sort_shopping_list


class serverDprosa():
    def __init__(self):

        super().__init__()
        # initialize class variables
        self.default_timegap = 10000
        self.item_list = []
        self.total_shoppers = 0
        self.timegap_dict = {}
        self.threshold_dict = {}
        self.cluster_dict = {}
        self.centroid_dict = {}
        self.timegap_matrix = np.array([])
        self.default_n_clusters = 0
        self.default_distance_threshold = 60
        self.shopping_list = []

        self.threshold_var = 60
        self.nclusters_var = 0

    def compilereadCSV(self,directory):
        self.start_time = time.time()
        '''
        ------------------------------------------------------------ COMPILE CSV ------------------------------------------------------------
        '''
        print("Compiling CSV")

        # Create a new directory for the compiled CSV files
        compiled_directory = os.path.join(directory, 'CSVRecordings', 'compiled_csv')
        os.makedirs(compiled_directory, exist_ok=True)

        compiledname = "CompiledData.csv"
        # output_file = os.path.join(compiled_directory, 'compiledData.csv')
        
        num = 1
        base_name, extension = os.path.splitext(compiledname)

        output_file = os.path.join(compiled_directory, compiledname)

        while os.path.exists(output_file):
            compiledname = f"{base_name}_{num}{extension}"
            output_file = os.path.join(compiled_directory, compiledname)
            num += 1

        csvdirectory = os.path.join(directory, 'CSVRecordings')

        print(f"Accessing files in folder: {csvdirectory}")

        csv_files = [f for f in os.listdir(csvdirectory) if f.endswith('.csv')]
        csv_files.sort()

        # Delete the existing CSV file if it exists
        if os.path.exists(output_file):
            os.remove(output_file)

        with open(output_file, 'a', newline='') as output_csv:
            writer = csv.writer(output_csv)

            for csv_file in csv_files:
                file_path = os.path.join(csvdirectory, csv_file)
                with open(file_path, 'r', errors='replace') as input_csv:
                    csv_text = input_csv.read().replace('\x00', '')
                    csv_lines = csv_text.splitlines()

                    reader = csv.reader(csv_lines)

                    for row in reader:
                        writer.writerow(row)
        print("Done compiling CSV")

        '''
        ------------------------------------------------------------ TIMEGAP ------------------------------------------------------------
        '''
        # Check if the file has data
        if os.path.getsize(output_file) == 0:
            print("No data collected yet...")
            return False  # File has no data
        
        else:
            df = pd.read_csv(output_file, header=None)
            print("--- %s seconds ---    || AFTER CSV READ" % (time.time() - self.start_time))

            self.item_list = sorted(df[(df.iloc[:, 2].apply(lambda x: isinstance(x, (int, float))) | \
                                        df.iloc[:, 2].apply(lambda x: str(x).isdigit() or x == 'Good'))].iloc[:, 0].unique())

            print("--- %s seconds ---    || AFTER SORTING" % (time.time() - self.start_time))

                
            self.timegap_dict, self.threshold_dict = initialize_timegap(self.item_list, self.default_timegap)
            print("--- %s seconds ---    || AFTER INIT TIMEGAP" % (time.time() - self.start_time))
            self.timegap_dict, self.total_shoppers = add_timegap(df, self.timegap_dict, self.threshold_dict,True)

            print("--- %s seconds ---    || AFTER ADD TIMEGAP" % (time.time() - self.start_time))
            self.timegap_dict = normalize_timegaps(self.timegap_dict)
            self.timegap_dict = dict(sorted(self.timegap_dict.items(), key=lambda x: x[1]))
            print("--- %s seconds ---    || AFTER TIMEGAP DICT" % (time.time() - self.start_time))
            
            return True
           

    def print_data(self):
        self.running_time = 0    
        print(f"Total Items: {len(self.item_list)}")
        print(f"Total Pairs: {len(self.timegap_dict)}")
        print(f"Total Shoppers: {self.total_shoppers}")
        if (len(self.item_list)==0):
            print(f"Total Clusters: 0")
        else:
            print(f"Total Clusters: {self.n_clusters}")
        #print(f"Running time: {self.running_time:.2f}s\n\n")

    def cluster_event(self,directory):
        self.timegap_matrix = dict_to_matrix(self.item_list, self.timegap_dict)
        self.cluster_dict, self.centroid_dict, self.n_clusters= agglomerative_clustering(self.item_list, self.timegap_matrix, self.threshold_var, self.nclusters_var)
        #self.cluster_dendrogram()
        self.export_as_csv(directory)
        #self.centroid_dict = self.calculate_centroid()
        #print(self.centroid_dict)
        #self.adjust_clusters()



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

    def print_shopping_list(self):
        for i, item in enumerate(self.shopping_list):
            self.print('end', f"{i+1}. {item}\n")

    def export_as_csv(self,directory):

        # Create a new directory for the compiled CSV files
        compiled_directory = os.path.join(directory, 'clusteredCSV')
        os.makedirs(compiled_directory, exist_ok=True)

        clustercsv = os.path.join(compiled_directory, 'clusters.csv')

        print(f"Accessing file in folder: {compiled_directory}")

        # Prepare CSV data
        csv_data = []
        for cluster, items in self.cluster_dict.items():
            for item in items:
                csv_data.append([item, cluster])

        # Create a CSV string
        csv_string = ""
        with open(clustercsv, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['Item', 'Cluster'])
            writer.writerows(csv_data)
        
        print("--- %s seconds ---    || DONE..." % (time.time() - self.start_time))
        
        return csv_string
    
    def timegap_cluster(self):
        return self.timegap_dict, self.cluster_dict
    
    '''------------------------------------------------------------ SORTING ------------------------------------------------------------'''
    def sort_shoppingList(self,X,shopping_list, timegap_dict, cluster_dict):
        shopping_list = sort_shopping_list(X, shopping_list, timegap_dict, cluster_dict)
        if X in shopping_list:
            shopping_list.remove(X)
        if X == None:
            shopping_list.pop(0)
        return shopping_list, timegap_dict, cluster_dict
    
    def convertData(self,string):
        itemlist = string.split(',')
        # Remove empty elements from the list
        itemlist = [item.strip() for item in itemlist if item.strip()]
        return itemlist