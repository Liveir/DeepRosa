
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
import os

class dprosa():
    def __init__(dat):
        dat.start_time = time.time()
        dat.connected()
        print("--- %s seconds ---    || connecting" % (time.time() - dat.start_time))
        dat.current_directory = os.getcwd()
        #dat.compile_recording()
        dat.read_compile()
        print("--- %s seconds ---    || AFTER READ_COMPILE" % (time.time() - dat.start_time))
        dat.cluster_event()
        print("--- %s seconds ---    || AFTER CLUSTER..." % (time.time() - dat.start_time))
        dat.success()
        print("--- %s seconds ---    || DONE..." % (time.time() - dat.start_time))


    def compile_recording(dat):
        output_file = os.path.join(dat.current_directory, 'v6.1.csv')
        parent_directory = os.path.abspath(os.path.join(dat.current_directory, os.pardir))
        child_folder_path = os.path.join(parent_directory, 'CSVRecordings')

        if os.path.exists(child_folder_path):
            print(f"Accessing files in child folder: {child_folder_path}")

            csv_files = [f for f in os.listdir(child_folder_path) if f.endswith('.csv')]
            csv_files.sort()

            # Delete the existing CSV file if it exists
            if os.path.exists(output_file):
                os.remove(output_file)

            with open(output_file, 'a', newline='') as output_csv:
                writer = csv.writer(output_csv)

                for csv_file in csv_files:
                    file_path = os.path.join(child_folder_path, csv_file)
                    with open(file_path, 'r', errors='replace') as input_csv:
                        csv_text = input_csv.read().replace('\x00', '')
                        csv_lines = csv_text.splitlines()

                        reader = csv.reader(csv_lines)

                        for row in reader:
                            writer.writerow(row)
        else:
            print(f"Child folder does not exist: {child_folder_path}")

    def cluster_event(dat):
        dat.dict_to_matrix()

        dat.agglomerative_clustering()

        #dat.cluster_dendrogram()
        dat.export_as_csv()
        dat.centroid_dict = dat.calculate_centroid()
        #print(dat.centroid_dict)
        #dat.adjust_clusters()



    def agglomerative_clustering(dat):
        k = 120
        agglomerative = AgglomerativeClustering(n_clusters=None, metric='precomputed', linkage='average', distance_threshold=50)
        cluster_labels = agglomerative.fit_predict(dat.timegap_matrix)

        clustered_items = {}
        for label in set(cluster_labels):
            clustered_items[label] = []

        for item, label in zip(dat.item_list, cluster_labels):
            clustered_items[label].append(item)

        dat.cluster_dict = clustered_items
        # print(dat.cluster_dict)
        dat.k = 120


    def calculate_centroid(dat):
        centroid_dict = {}

        for cluster_index, cluster_items in dat.cluster_dict.items():
            for i in range(0, len(cluster_items)-1):
                item_x = cluster_items[i]
                for j in range(0, len(cluster_items)-1):
                    if i != j:
                        item_y = cluster_items[j]
                        pair = (item_x, item_y)
                        sorted_pair = tuple(sorted(list(pair)))
                        if sorted_pair in dat.timegap_dict:
                            if cluster_index not in centroid_dict:
                                centroid_dict[cluster_index] = []
                            centroid_dict[cluster_index].append(dat.timegap_dict[sorted_pair])

        for cluster_index, cluster_values in centroid_dict.items():
            if len(cluster_values) > 0:
                centroid_dict[cluster_index] = sum(cluster_values) / len(cluster_values)
        
        return centroid_dict  

    def sort_shopping_list(dat):
        dat.sorted_list = dat.shopping_list
        dat.cluster_anchor = 0
        dat.sorted_list = sorted(
            dat.sorted_list,
            key=lambda x: (
                -1 if any(x in value for value in dat.cluster_dict.get(dat.cluster_anchor-1, [])) else 0,
                next((key for key, value in dat.cluster_dict.items() if x in value), 0)
            )
        )   
        for i in range(len(dat.sorted_list) - 1):
            item_x = dat.sorted_list[i]
            item_y = dat.sorted_list[i + 1]
            cluster_x = next((key for key, value in dat.cluster_dict.items() if item_x in value), None)
            cluster_y = next((key for key, value in dat.cluster_dict.items() if item_y in value), None)

            if cluster_x is not None and cluster_x == cluster_y:
                continue

            min_timegap = float('inf')
            min_timegap_item = None

            for j in range(i + 1, len(dat.sorted_list)):
                next_item = dat.sorted_list[j]

                if (item_x, next_item) in dat.timegap_dict:
                    timegap = dat.timegap_dict[(item_x, next_item)]

                    if timegap < min_timegap:
                        min_timegap = timegap
                        min_timegap_item = next_item

            if min_timegap_item is not None:
                index_min_timegap_item = dat.sorted_list.index(min_timegap_item)
                dat.sorted_list[i + 1], dat.sorted_list[index_min_timegap_item] = dat.sorted_list[index_min_timegap_item], dat.sorted_list[i + 1]

        dat.shopping_list = dat.sorted_list
        dat.print_shopping_list()

    def print_shopping_list(dat):
        for i, item in enumerate(dat.shopping_list):
            dat.print('end', f"{i+1}. {item}\n")


    def dict_to_matrix(dat):
        items = dat.item_list
        matrix = np.zeros((len(items), len(items)))

        for i in range(len(items)):
            for j in range(len(items)):
                if i != j:
                    key = (items[i], items[j])
                    if key in dat.timegap_dict:
                        matrix[i][j] = dat.timegap_dict[key]
                        matrix[j][i] = dat.timegap_dict[key]

        timegap_matrix = matrix

    def export_as_csv(dat):
        # Prepare CSV data
        csv_data = []
        for cluster, items in dat.cluster_dict.items():
            for item in items:
                csv_data.append([item, cluster])

        # Create a CSV string
        csv_string = ""
        with open('clusters.csv', mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['Item', 'Cluster'])
            writer.writerows(csv_data)
        
        return csv_string

    def read_compile(dat):
        csv_path = os.path.join(dat.current_directory,'v6.1.csv' )
        #csv_path = 'v6.1.csv'
        print(csv_path)
        df = pd.read_csv(csv_path, header=None)
        print("--- %s seconds ---    || AFTER CSV READ" % (time.time() - dat.start_time))
        
        dat.item_list = sorted(df[(df.iloc[:, 2].apply(lambda x: isinstance(x, (int, float))) | \
                                    df.iloc[:, 2].apply(lambda x: str(x).isdigit() or x == 'Good'))].iloc[:, 0].unique())
        
        '''
        #------------------------------------ ALTERNATIVE METHOD
        # Check if a value is numeric (int or float)
        def is_numeric(value):
            return isinstance(value, (int, float)) or (isinstance(value, str) and value.isdigit())

        # Filter the DataFrame based on specified conditions
        filtered_df = df[(df.iloc[:, 2].apply(is_numeric) | (df.iloc[:, 2] == 'Good'))]

        # Extract unique items from the first column and sort them
        dat.item_list = sorted(filtered_df.iloc[:, 0].unique())
        #------------------------------------
        '''
        print("--- %s seconds ---    || AFTER SORTING" % (time.time() - dat.start_time))

       
        dat.timegap_dict, dat.total_shoppers = dat.init_timegap()
        print("--- %s seconds ---    || AFTER INIT TIMEGAP" % (time.time() - dat.start_time))
        dat.timegap_dict, dat.total_shoppers = dat.add_timegap(df) 
        print("--- %s seconds ---    || AFTER ADD TIMEGAP" % (time.time() - dat.start_time))
        dat.timegap_dict = dict(sorted(dat.timegap_dict.items(), key=lambda x: x[1]))     #sort from lowest timegap
       

        print("--- %s seconds ---    || AFTER TIMEGAP DICT" % (time.time() - dat.start_time))
        
        #approximate_missing_timegaps()
        dat.print_data()

    def print_data(dat):
        dat.running_time = 0    
        print(f"Total Items: {len(dat.item_list)}\n")
        print(f"Total Pairs: {len(dat.timegap_dict)}\n")
        print(f"Total Shoppers: {dat.total_shoppers}\n\n")
        #print(f"Running time: {dat.running_time:.2f}s\n\n")

    def init_timegap(dat):
        timegap_dict = {}
        threshold_dict = {}
        total_shoppers = 0
        for key1 in dat.item_list:
            for key2 in dat.item_list:
                if key1 != key2:
                    pair = tuple(sorted((key1, key2)))
                    if pair not in timegap_dict:
                        timegap_dict[pair] = [100000]

        sorted_timegap_dict = dict(sorted(timegap_dict.items(), key=lambda x: x[0]))

        for pair in sorted_timegap_dict:
            threshold_dict[pair] = 0
        
        dat.threshold_dict = threshold_dict
        return sorted_timegap_dict, total_shoppers
 
    def add_timegap(dat, df):
        timegap_dict = dat.timegap_dict
        total_shoppers = dat.total_shoppers
        temp_dict = {}
        print_max = len(df) // 5

        for index in range(len(df)):
            item_x, value_x, status_x = df.iloc[index]
            value_x_next = 0 if index == len(df) - 1 else df.iloc[index + 1, 1]

            if value_x == 0:
                total_shoppers += 1
                temp_dict.clear()
                temp_dict[item_x] = value_x
            else:
                temp_dict[item_x] = value_x

            if value_x_next == 0 and len(temp_dict) != 1:
                sorted_keys = sorted(temp_dict.keys())
                num_items = len(sorted_keys)

                for i in range(num_items - 1):
                    key1, key2 = sorted_keys[i], sorted_keys[i + 1]
                    pair = tuple(sorted((key1, key2)))
                    diff = abs(temp_dict[key1] - temp_dict[key2])

                    if pair in timegap_dict:
                        timegap_values = timegap_dict[pair]
                        if diff < timegap_values[-1] - 10 or diff > timegap_values[-1] + 10:
                            if pair not in dat.threshold_dict:
                                dat.threshold_dict[pair] = 1
                            else:
                                dat.threshold_dict[pair] += 1

                            if dat.threshold_dict[pair] >= 3:
                                timegap_values.append(sum(timegap_values[-3:]) / 3)
                                dat.threshold_dict[pair] = 0
                        timegap_values.append(diff)
                    else:
                        timegap_dict[pair] = [diff]

                temp_dict.clear()

        for values in timegap_dict.values():
            if len(values) > 1:
                values.pop(0)

        for key in timegap_dict:
            timegap_dict[key] = sum(timegap_dict[key]) / len(timegap_dict[key])

        sorted_timegap_dict = dict(sorted(timegap_dict.items(), key=lambda x: x[0]))
        return sorted_timegap_dict, total_shoppers


    
    def dict_to_matrix(dat):
        items = dat.item_list
        matrix = np.zeros((len(items), len(items)))

        for i in range(len(items)):
            for j in range(len(items)):
                if i != j:
                    key = (items[i], items[j])
                    if key in dat.timegap_dict:
                        matrix[i][j] = dat.timegap_dict[key]
                        matrix[j][i] = dat.timegap_dict[key]

        dat.timegap_matrix = matrix

    def success(dat):
        current_directory = os.getcwd()
        connectPath = os.path.join(current_directory, 'pythonConnection')
        new_content = 'Success1'

        try:
            # Read the existing content of the file if it exists
            if not os.path.exists(connectPath):
                # Create the file if it doesn't exist
                with open(connectPath, 'w') as f:
                    f.write(new_content + '\n')
            else:
                with open(connectPath, 'r') as f:
                    lines = f.readlines()

                # Insert the string at the 2nd line
                lines.insert(1, new_content + '\n')

                lines.insert(2, '------------' + '\n')

                # Write the updated content back to the file
                with open(connectPath, 'w') as f:
                    f.writelines(lines)

            print('Success.')
        except Exception as e:
            print(f'An error occurred: {str(e)}')
    
    def connected(dat):
        current_directory = os.getcwd()
        connectPath = os.path.join(current_directory, 'pythonConnection')
        new_content = 'connected1'

        try:
            # Read the existing content of the file if it exists
            if not os.path.exists(connectPath):
                # Create the file if it doesn't exist
                with open(connectPath, 'w') as f:
                    f.write(new_content + '\n')
            else:
                with open(connectPath, 'r') as f:
                    lines = f.readlines()

                # Insert the string at the 2nd line
                lines.insert(0, new_content + '\n')

                # Write the updated content back to the file
                with open(connectPath, 'w') as f:
                    f.writelines(lines)

            print('Success.')
        except Exception as e:
            print(f'An error occurred: {str(e)}')


dprosa = dprosa()
