"""
Dynamic Proximity Sorting Algorithm // dprosa

These routines perform data processing, clustering, and 
sorting of some input data.

Authors: Johnfil Initan, Vince Abella, Jake Perez

"""

import numpy as np

from scipy.signal import argrelextrema
from scipy.stats import gaussian_kde

from sklearn.cluster import KMeans
from sklearn.cluster import AgglomerativeClustering

########################################################
# Data Processing

def initialize_timegap(L=list, default_timegap=float):
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
                        if pair in TD:
                            TD[pair].append(diff)

    for values in TD.values():
        if len(values) > 1:
            values.pop(0)

    return TD, n_lists

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

def normalize_timegaps(TD=dict):
    '''
    Finds the average of a list of timegaps.

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
        
    '''

    for key in TD:
        TD[key] = sum(TD[key]) / len(TD[key])

    TD = dict(sorted(TD.items(), key=lambda x: x[0]))

    return TD

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

def agglomerative_clustering(L=list, TX=list, distance_threshold=int, n_clusters=int):
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

    distance_threshold : int, default=None
        The linkage distance threshold at or above which
        clusters will not be merged. If not ``None``, 
        ``n_clusters`` must be ``None``.
    
    n_clusters_ : int
        The number of clusters found by the algorithm. If
        ``distance_threshold=None``, it will be equal to 
        the given ``n_clusters``.

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
    if distance_threshold == 0:
        distance_threshold = None
        
    if n_clusters == 0:
        n_clusters = None
    
    agglo = AgglomerativeClustering(n_clusters=n_clusters, 
                                    metric='precomputed', 
                                    linkage='average', 
                                    distance_threshold=distance_threshold
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
        The number of clusters set by the user.

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


########################################################
# Search and Sorting

def sort_shopping_list(X=None, SL=list, TD=dict, TC=dict):
    '''
    Sorts a list of items based on their respective clusters.

    Parameters
    -----------
    X : str or None, optional
        Item being acquired. If X is None, the list will be
        sorted based on cluster number. If X is not None, the list
        is sorted relative to X as the first item, and its cluster
        is always the first cluster.
        
    SL : list
        List of items to be sorted.

    TD : dictionary (string, list)
        Key is comma-separated pair of items while the value
        is the time gap between items.

    TC : dictionary (int, list)
        Key is cluster number while the value is a list of items 
        inside that cluster.

    Returns
    -----------
    SL : list
        List of sorted items.
        
    '''

    # If X is provided, find its cluster number
    if X is not None:
        cluster_x = search_item_cluster(X, TC)
        if cluster_x is not None:
            # Move X to the front of the list
            SL.remove(X)
            SL.insert(0, X)
    else:
        cluster_x = None

    # Sort the list based on cluster number and time gaps
    SL = sorted(
        SL,
        key=lambda x: (
            0 if cluster_x is not None and x == X else next((key for key, value in TC.items() if x in value), float('inf')),
            -1 if any(x in value for value in TC.values()) else 0
        )
    )

    for i in range(len(SL) - 1):
        item_x = SL[i]
        item_y = SL[i + 1]
        cluster_x = next((key for key, value in TC.items() if item_x in value), None)
        cluster_y = next((key for key, value in TC.items() if item_y in value), None)

        if cluster_x is not None and cluster_x == cluster_y:
            continue

        min_timegap = float('inf')
        min_timegap_item = None

        for j in range(i + 1, len(SL)):
            next_item = SL[j]

            if (item_x, next_item) in TD:
                timegap = TD[(item_x, next_item)]

                if timegap < min_timegap:
                    min_timegap = timegap
                    min_timegap_item = next_item

        if min_timegap_item is not None:
            index = SL.index(min_timegap_item)
            SL[i + 1], SL[index] = SL[index], SL[i + 1]

    return SL

def search_item_cluster(X=str, TC=dict):
    '''
    Determines the cluster that an item belongs to.

    Parameters
    -----------
    X : str
        The item.

    TC : dictionary (int, list)
        Key is cluster number while value is a list of items 
        inside that cluster.

    Returns
    -----------
    key : int
        The cluster number for X.

    '''
    for key, value in TC.items():
        if isinstance(value, list):
            if X in value:
                return key
        else:
            if value == X:
                return key


