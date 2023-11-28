'''----------------------------------------------------------------------------------------
Title:          serverDprosa.py
Description:    This file contains the server-side implementation of the DPROSA algorithm.
Author:         Jake Mark Perez, Johnfil Initan, and Vincent Abella
Date:           November 2023
Version:        1.0
Revision History:
----------------------------------------------------------------------------------------'''

#libraries
import pandas as pd
import numpy as np
#from scipy.cluster.hierarchy import dendrogram, linkage
#from sklearn.cluster import AgglomerativeClustering
import csv
import time
import os
import json
from datetime import datetime

from Models._dprosa import \
    initialize_timegap, add_timegap, check_timegap, normalize_timegaps,\
    dict_to_matrix, sort_shopping_list, \
    agglomerative_clustering, kmeans_clustering, affinity_propagation_clustering


# Global variables
sort_directory = ''
sort_suffix_time = ''

'''----------------------------------------------------------------------------------------
Class name:     serverDprosa
Description:    This class contains the server-side implementation of the DPROSA algorithm.
Params:         None
Returns:        None
----------------------------------------------------------------------------------------'''   
class serverDprosa():
    '''----------------------------------------------------------------------------------------
    def name:      __init__
    Description:   This function is the constructor of the serverDprosa class.
    Params:        None
    Returns:       None
    ----------------------------------------------------------------------------------------'''  
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

        self.sort_time = 0.0

    '''----------------------------------------------------------------------------------------
    def name:      compileCSV
    Description:   This function compiles all the CSV files in the CSVRecordings folder.
    Params:        directory - the directory of the CSV files
    Returns:       True if the file has data, False otherwise
    ----------------------------------------------------------------------------------------'''
    def compilereadCSV(self, directory):
        global sort_directory
        self.start_time = time.time()

        print("Compiling CSV")
        sort_directory = directory
        # Create a new directory for the compiled CSV files
        compiled_directory = os.path.join(directory, 'Server Data Files', 'compiled_csv')
        os.makedirs(compiled_directory, exist_ok=True)

        current_time = time.strftime("%Y%m%d%H%M%S")
        compiledname = f"CompiledData_{current_time}.csv"
        output_file = os.path.join(compiled_directory, compiledname)

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

        # Check if the file has data
        if os.path.getsize(output_file) == 0:
            print("No data collected yet...")
            return False  # File has no data
        else:
            df = pd.read_csv(output_file, header=None)
            self.getTimegapDict(df)

            return True
        

    '''----------------------------------------------------------------------------------------
    def name:      getTimegapDict
    Description:   This function gets the timegap dictionary from the CSV file.
    Params:        df - the dataframe of the CSV file
    Returns:       None
    ----------------------------------------------------------------------------------------'''    
    def getTimegapDict(self,df):
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


    '''----------------------------------------------------------------------------------------
    def name:      print_data
    Description:   Prints the data of the DPROSA algorithm.
    Params:        None
    Returns:       None
    ----------------------------------------------------------------------------------------'''    
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

    '''----------------------------------------------------------------------------------------
    def name:      cluster_event
    Description:   Clusters the items in the CSV file.
    Params:        directory - the directory of the CSV files
                   clusterNo - type of cluster
    Returns:       None
    ----------------------------------------------------------------------------------------'''    
    def cluster_event(self,directory,clusterNo):
        self.timegap_matrix = dict_to_matrix(self.item_list, self.timegap_dict)

        if(clusterNo == 0 or clusterNo == 1):
            self.cluster_dict, self.centroid_dict, self.n_clusters= agglomerative_clustering(self.item_list, self.timegap_matrix, self.threshold_var, self.nclusters_var)
        else:
            self.cluster_dict, self.centroid_dict, self.n_clusters= affinity_propagation_clustering(self.item_list, self.timegap_matrix, 0.9, 500, 15)

            
        #self.cluster_dendrogram()
        self.export_as_csv(directory)
        #self.centroid_dict = self.calculate_centroid()
        #print(self.centroid_dict)
        #self.adjust_clusters()


    '''----------------------------------------------------------------------------------------
    def name:      calculate_centroid
    Description:   Calculates the centroid of the clusters.
    Params:        None
    Returns:       centroid_dict - the dictionary of the centroid of the clusters
    ----------------------------------------------------------------------------------------'''    
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

    '''----------------------------------------------------------------------------------------
    def name:      print_shopping_list
    Description:   Prints the shopping list.
    Params:        None
    Returns:       None
    ----------------------------------------------------------------------------------------'''
    def print_shopping_list(self):
        for i, item in enumerate(self.shopping_list):
            self.print('end', f"{i+1}. {item}\n")

    '''----------------------------------------------------------------------------------------
    def name:      export_as_csv
    Description:   Exports the clustered items as a CSV file.
    Params:        directory - the directory of the CSV files
    Returns:       csv_string - the string of the CSV file
    ----------------------------------------------------------------------------------------'''    
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
    

    '''----------------------------------------------------------------------------------------
    def name:      timegap_cluster
    Description:   Returns the timegap and cluster dictionaries.
    Params:        None
    Returns:       timegap_dict - the dictionary of the timegaps
    ----------------------------------------------------------------------------------------'''    
    def timegap_cluster(self):
        return self.timegap_dict, self.cluster_dict
    

    '''----------------------------------------------------------------------------------------
    def name:      sort_shoppingList
    Description:   Sorts the shopping list.
    Params:        X - the item to be removed from the shopping list
                   shopping_list - the shopping list to be sorted
                   timegap_dict - the dictionary of the timegaps
                   cluster_dict - the dictionary of the clusters
    Returns:       shopping_list - the sorted shopping list
                   timegap_dict - the updated dictionary of the timegaps
                   cluster_dict - the updated dictionary of the clusters  
    ----------------------------------------------------------------------------------------'''    
    def sort_shoppingList(self,X,shopping_list, timegap_dict, cluster_dict, customerNumber):

        if X == None:
            # Record start time  
            start_sort = time.perf_counter_ns()

        shopping_list = sort_shopping_list(X, shopping_list, timegap_dict, cluster_dict)

        if X == None:
            # Calculate elapsed time
            self.sort_time = time.perf_counter_ns() - start_sort
            self.sort_time_csv(customerNumber)


        if X in shopping_list:
            shopping_list.remove(X)
        if X == None:
            shopping_list.pop(0)
        return shopping_list, timegap_dict, cluster_dict
    

    '''----------------------------------------------------------------------------------------
    def name:      convertData
    Description:   Converts the string to a list.
    Params:        string - the string to be converted
    Returns:       itemlist - the list of the string
    ----------------------------------------------------------------------------------------'''    
    def convertData(self,string):
        itemlist = string.split(',')
        # Remove empty elements from the list
        itemlist = [item.strip() for item in itemlist if item.strip()]
        return itemlist
    

    '''----------------------------------------------------------------------------------------
    def name:      storeClusterTimeDict
    Description:   Stores the cluster and timegap dictionaries as JSON files.
    Params:        directory - the directory of the CSV files
    Returns:       None
    ----------------------------------------------------------------------------------------'''    
    def storeClusterTimeDict(self, directory):
        clusters_dict = self.cluster_dict
        timegaps_dict = self.timegap_dict

        # Convert tuple keys to strings in timegaps_dict
        timegaps_dict_str_keys = {str(key): value for key, value in timegaps_dict.items()}

        # Create the child directory "Clusters_and_Timegaps" if it doesn't exist
        child_directory = os.path.join(directory,"Server Data Files", "Clusters_and_Timegaps")
        if not os.path.exists(child_directory):
            os.makedirs(child_directory)

        # Generate a timestamp to use as a suffix for both filenames
        current_time_suffix = datetime.now().strftime("%Y%m%d%H%M%S")

        # Write clusters dictionary to a file with the timestamp as suffix
        clusters_file_path = os.path.join(child_directory, f"clusters_{current_time_suffix}.json")

        with open(clusters_file_path, 'w') as clusters_file:
            json.dump(clusters_dict, clusters_file)

        # Write timegaps dictionary to a file with the same timestamp as suffix
        timegaps_file_path = os.path.join(child_directory, f"timegaps_{current_time_suffix}.json")

        with open(timegaps_file_path, 'w') as timegaps_file:
            json.dump(timegaps_dict_str_keys, timegaps_file)

        # Print the paths for confirmation
        print(f"Clusters file stored at: {clusters_file_path}")
        print(f"Timegaps file stored at: {timegaps_file_path}")

    '''----------------------------------------------------------------------------------------
    def name:      sort_time_csv
    Description:   Stores the sort time as a CSV file.
    Params:        customerNumber - the number of customers
    Returns:       None
    ----------------------------------------------------------------------------------------'''    
    def sort_time_csv(self, customerNumber):
        global sort_directory
        global sort_suffix_time
        # Create a new directory for the compiled CSV files
        sort_time_directory = os.path.join(sort_directory,"Server Data Files", "Sort_Time")
        if not os.path.exists(sort_time_directory):
            os.makedirs(sort_time_directory)

        # Determine the file name based on the customerNumber
        if customerNumber == 1:
            sort_suffix_time = datetime.now().strftime("%Y%m%d_%H%M%S")
            sort_time_file = os.path.join(sort_time_directory, f'sortTime_{sort_suffix_time}.csv')
        elif customerNumber > 1:
            sort_time_file = os.path.join(sort_time_directory, f'sortTime_{sort_suffix_time}.csv')

        # Check if the file exists
        file_exists = os.path.isfile(sort_time_file)

        # Open the file in append mode, create it if it doesn't exist
        with open(sort_time_file, mode='a', newline='') as file:
            # Create a CSV writer object
            writer = csv.writer(file)

            # If the file doesn't exist, write the header row
            if not file_exists:
                writer.writerow(['Customer Number', 'Sort Time(ns)'])

            # Write the new values of customerNumber and sort time as a new row
            writer.writerow([customerNumber, self.sort_time])

        print(f"Values appended to {sort_time_file} successfully.")
        print(f"Customer Number: {customerNumber} Sort time: {self.sort_time} nanoseconds\n\n")

