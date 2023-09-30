"""
Dynamic Proximity Sorting Algorithm // dprosa

These routines perform data processing, clustering, and 
sorting of some input data.

Authors: Johnfil Initan, Vince Abella, Jake Perez

"""

import numpy as np
from sklearn.cluster import KMeans
from sklearn.cluster import AgglomerativeClustering

########################################################
# Data Processing

def initialize_timegap(L=list, default_timegap=int):
    '''
    Initializes dictionary of timegaps with default values.

    Parameters
    -----------
    L : list
        List of items that act as datapoints.

    default_timegap : int
        Default value for timegaps between pairs of items.

    Returns
    -----------
    TD : dictionary (string, list)
        Key is comma-separated pair of items while value
        is timegap between items.

    TH : dictionary (string, int)
        Key is comma-separated pair of items while value
        is the threshold that determines when the timegap
        of the pair is refreshed, or if there are potentially
        multiple instances of the pair.

    '''
    TD = {}
    TH = {}

    for key1 in L:
        for key2 in L:
            if key1 != key2:
                pair = tuple(sorted((key1, key2)))
                if pair not in TD:
                    TD[pair] = [default_timegap]

    TD = dict(sorted(TD.items(), key=lambda x: x[0]))

    for pair in TD:
        TH[pair] = 0

    return TD, TH

def add_timegap(df, TD=dict, TH=dict, appended=False):
    '''
    Adds dictionary of timegaps with default values.

    Parameters
    -----------
    df : DataFrame
        Contains three columns: item, timestamp, status.
        Item represents a grocery item; timestamp is when
        the item was acquired relative to the first item,
        and status signifies integrity of data for that row.

    TD : dictionary (string, list)
        Key is comma-separated pair of items while value
        is timegap between items.

    TH : dictionary (string, int)
        Key is comma-separated pair of items while value
        is the threshold that determines when the timegap
        of the pair is refreshed, or if there are potentially
        multiple instances of the pair.

    appended : Boolean, default=False
        Determines if list is single or is a bulk file of
        multiple lists appended together.

    Returns
    -----------
    TD : dictionary (string, list)
        Key is comma-separated pair of items while value
        is timegap between items.

    n_lists : int, default=0
        The total number of lists. 
    
    instances : dict (string, int)
        A dictionary containing then number of instances (value)
        that an item (key) appears, determined using modal analysis.

    '''
    temp = {}
    n_lists = 0

    if appended == True:
        for index in range(len(df)):
            item = df.iloc[index, 0]
            timestamp = df.iloc[index, 1]
            if index == len(df) - 1:
                timestamp_next = 0
            else:
                timestamp_next = df.iloc[index + 1, 1] 
            status = df.iloc[index, 2]

            if (isinstance(status, (int, float)) or str(status).isdigit() or status == 'Good'):
                # if first item in the last
                if timestamp == 0:
                    n_lists += 1
                    temp.clear()
                    temp[item] = timestamp
                else:
                    temp[item] = timestamp

                # if last item in list
                if timestamp_next == 0 and len(temp) != 1:
                    sorted_keys = sorted(temp.keys())
                    n_items = len(sorted_keys)

                    for i in range(n_items - 1):
                        key1 = list(temp.keys())[i]
                        key2 = list(temp.keys())[i + 1]
                        pair = tuple(sorted((key1, key2)))
                        diff = abs(temp[key1] - temp[key2])
                        
                        TD = check_timegap(TD, TH, pair, diff)

    for values in TD.values():
        if len(values) > 1:
            values.pop(0)

    modes, instances = check_instances(TD)
    #print(modes)
    print(instances)

    for key in TD:
        TD[key] = sum(TD[key]) / len(TD[key])

    TD = dict(sorted(TD.items(), key=lambda x: x[0]))
    return TD, n_lists, instances

def check_timegap(TD=dict, TH=dict, key=tuple, value=int):
    '''
    Checks threshold dictionary (Y) to determine if 
    the timegap of the pair needs to be refreshed, or 
    if there are potentially multiple instances of the pair.

    Parameters
    -----------
    TD : dictionary (string, list)
        Key is comma-separated pair of items while value
        is timegap between items.

    TH : dictionary (string, int)
        Key is comma-separated pair of items while value
        is the threshold that determines when the timegap
        of the pair is refreshed, or if there are potentially
        multiple instances of the pair.
    
    key : tuple
        A tupled pair of items.
    
    value : int
        The absolute difference or timegap between two 
        sequential pair of items (key).

    Returns
    -----------
    TD : dictionary (string, list)
        Key is comma-separated pair of items while value
        is timegap between items.
        
    '''
    if key in TD:
        if value < (int(TD[key][-1]) - 10) or value > (int(TD[key][-1]) + 10):
            TH[key] += 1
            if TH[key] >= 3:
                TD[key] = [sum(TD[key][-3:]) / len(TD[key][-3:])]
                TH[key] == 0

        TD[key].append(value)
    else:
        TD[key] = [value]
    
    return TD

def check_instances(TD=dict):
    '''
    Routine to determine the number of instances that an item
    potentially appears, using modal analysis to count how many
    peak points there are for a given item. If an item has
    multiple instances, TD will be modified to include the new
    instances. 

    Parameters
    -----------
    TD : dictionary (string, list)
        Key is comma-separated pair of items while value
        is timegap between items.

    Returns
    -----------
    TD : dictionary (string, list)
        Key is comma-separated pair of items while value
        is timegap between items.
    
    instances : dict (string, int)
        A dictionary containing then number of instances
        (value)that an item (key) appears, determined using
        modal analysis.

    '''
    if TD:
        for key, value in TD.items():
            if isinstance(value, list):
                TD[key] = [int(num) if isinstance(num, float) else num for num in value]
            
    modes = {}
    instances = {}
    for key, value in TD.items():
        frequency = {}
        for v in value:
            frequency[v] = frequency.get(v, 0) + 1

        max_frequency = max(frequency.values())
        m = [v for v, f in frequency.items() if f == max_frequency]
        modes[key] = m

        item, _ = key
        if item not in instances:
            instances[item] = [len(m)]
    
    for key, value in instances.items():
        frequency = {}
        for v in value:
            frequency[v] = frequency.get(v, 0) + 1
        
        max_frequency = max(frequency.values())
        m = [v for v, f in frequency.items() if f == max_frequency]
        instances[key] = m

    return modes, instances


def dict_to_matrix(L=list, TD=dict):
    '''
    Converts dictionary to matrix format where rows [i] is
    list of items and columns [j] is also list of items, thus,
    n_elements = n_features. Value at [i][j] represents timegaps
    between items.

    Parameters
    -----------
    L : list
        List of items that act as datapoints.

    TD : dictionary (string, list)
        Key is comma-separated pair of items while value
        is timegap between items.

    Returns
    -----------
    TX : distance matrix (NumPy array)
        The rows [i] and columns [j] represent a list of items,
        thus, n_elements = n_features. Value at [i][j] represents
        timegaps between items.
        
    '''
    TX = np.zeros((len(L), len(L)))

    for i in range(len(L)):
        for j in range(len(L)):
            if i != j:
                key = (L[i], L[j])
                if key in TD:
                    TX[i][j] = TD[key]
                    TX[j][i] = TD[key]
    
    return TX


########################################################
# Clustering

def agglomerative_clustering(L=list, TX=list):
    '''
    Initializes dictionary of timegaps with default values.

    Parameters
    -----------
    L : list
        List of items that act as datapoints.

    TX : distance matrix (NumPy array)
        The rows [i] and columns [j] represent a list of items,
        thus, n_elements = n_features. Value at [i][j] represents
        timegaps between items.

    Returns
    -----------
    TC : dictionary (int, list)
        Key is cluster number while value is list of items 
        inside that cluster.

    n_clusters_ : int
        The number of clusters found by the algorithm. If
        ``distance_threshold=None``, it will be equal to 
        the given ``n_clusters``.

    '''
    agglo = AgglomerativeClustering(n_clusters=None, 
                                    metric='precomputed', 
                                    linkage='average', 
                                    distance_threshold=50
                                    )
    agglo.fit(TX)
    labels = agglo.labels_
    n_clusters = agglo.n_clusters_
    TC = {}

    for i in range(n_clusters):
        TC[i] = []

    for item, label in zip(L, labels):
        TC[label].append(item)

    return TC, n_clusters

def kmeans_clustering(L=list, TX=list):
    '''
    Initializes dictionary of timegaps with default values.

    Parameters
    -----------
    L : list
        List of items that act as datapoints.

    TX : distance matrix (NumPy array)
        The rows [i] and columns [j] represent a list of items,
        thus, n_elements = n_features. Value at [i][j] represents
        timegaps between items.

    Returns
    -----------
    TC : dictionary (int, list)
        Key is cluster number while value is list of items 
        inside that cluster.

    n_clusters_ : int
        The number of clusters found by the algorithm. If
        ``distance_threshold=None``, it will be equal to 
        the given ``n_clusters``.

    '''
    n_clusters = 50
    dissimilarity_matrix = 1 - (TX / np.max(TX))

    kmeans = KMeans(n_clusters=n_clusters, n_init=10)
    kmeans.fit(dissimilarity_matrix)
    labels = kmeans.labels_
    TC = {}

    for i in range(n_clusters):
        TC[i] = []

    for item, label in zip(L, labels):
        TC[label].append(item)

    return TC, n_clusters
