import networkx as nx
import graph_creator as gc

node_dict = {
    "1": {"name": "Q1", "pos": (-5, 7), "type": gc.base_node_type["queue"], "poiId": "1"},
    "2": {"name": "N1", "pos": (-3, 7), "type": gc.base_node_type["normal"], "poiId": "0"},
    "3": {"name": "I1", "pos": (-5, 5), "type": gc.base_node_type["intersection"], "poiId": "0"},
    "4": {"name": "I2", "pos": (-3, 5), "type": gc.base_node_type["intersection"], "poiId": "0"},
    "5": {"name": "I3", "pos": (3, 5), "type": gc.base_node_type["intersection"], "poiId": "0"},
    "6": {"name": "P1", "pos": (3, 7), "type": gc.base_node_type["parking"], "poiId": "2"},
    "7": {"name": "I4", "pos": (8, 5), "type": gc.base_node_type["intersection"], "poiId": "0"},
    "8": {"name": "WD1", "pos": (11, 5), "type": gc.base_node_type["waiting-departure"], "poiId": "0"},
    "9": {"name": "POI3", "pos": (11, 7), "type": gc.base_node_type["unload"], "poiId": "3"},
    "10": {"name": "I5", "pos": (8, 2), "type": gc.base_node_type["intersection"], "poiId": "0"},
    "11": {"name": "D1", "pos": (12, 2), "type": gc.base_node_type["departure"], "poiId": "0"},
    "12": {"name": "C1", "pos": (12, 0), "type": gc.base_node_type["charger"], "poiId": "4"},
    "13": {"name": "W1", "pos": (12, -2), "type": gc.base_node_type["waiting"], "poiId": "0"},
    "14": {"name": "I6", "pos": (8, -2), "type": gc.base_node_type["intersection"], "poiId": "0"},
    "15": {"name": "I7", "pos": (8, -5), "type": gc.base_node_type["intersection"], "poiId": "0"},
    "16": {"name": "WD2", "pos": (8, -7), "type": gc.base_node_type["waiting-departure"], "poiId": "0"},
    "17": {"name": "POI4", "pos": (12, -7), "type": gc.base_node_type["unload-dock"], "poiId": "5"},
    "18": {"name": "I8", "pos": (0, -5), "type": gc.base_node_type["intersection"], "poiId": "0"},
    "19": {"name": "D2", "pos": (0, -8), "type": gc.base_node_type["departure"], "poiId": "0"},
    "20": {"name": "POI1", "pos": (-3, -8), "type": gc.base_node_type["load"], "poiId": "6"},
    "21": {"name": "W2", "pos": (-5, -8), "type": gc.base_node_type["waiting"], "poiId": "0"},
    "22": {"name": "I9", "pos": (-5, -5), "type": gc.base_node_type["intersection"], "poiId": "0"},
    "23": {"name": "N2", "pos": (-7, -5), "type": gc.base_node_type["normal"], "poiId": "0"},
    "24": {"name": "I10", "pos": (-7, -2), "type": gc.base_node_type["intersection"], "poiId": "0"},
    "25": {"name": "W3", "pos": (-5, -2), "type": gc.base_node_type["waiting"], "poiId": "0"},
    "26": {"name": "POI2", "pos": (-5, 0), "type": gc.base_node_type["load-dock"], "poiId": "7"},
    "27": {"name": "D3", "pos": (-5, 2), "type": gc.base_node_type["departure"], "poiId": "0"},
    "28": {"name": "I11", "pos": (-7, 2), "type": gc.base_node_type["intersection"], "poiId": "0"},
    "29": {"name": "N3", "pos": (-7, 5), "type": gc.base_node_type["normal"], "poiId": "0"},
    "30": {"name": "POI8", "pos": (5, 2), "type": gc.base_node_type["charger"], "poiId": "8"},
    "31": {"name": "POI9", "pos": (0,-2), "type": gc.base_node_type["load"], "poiId": "9"},
    "32": {"name": "POI10", "pos": (-10,2), "type": gc.base_node_type["load-dock"], "poiId": "10"},
}

edge_dict = {
    # Krawędzie dojazdu do miejsca oczekiwania na dojazd do stanowiska
    "1": {"startNode": "2", "endNode": "1", "type": gc.way_type["oneWay"], "isActive": True},
    "2": {"startNode": "4", "endNode": "2", "type": gc.way_type["oneWay"], "isActive": True},
    "3": {"startNode": "1", "endNode": "3", "type": gc.way_type["oneWay"], "isActive": True},
    "4": {"startNode": "3", "endNode": "4", "type": gc.way_type["twoWay"], "isActive": True},
    "5": {"startNode": "4", "endNode": "5", "type": gc.way_type["twoWay"], "isActive": True},
    "6": {"startNode": "5", "endNode": "6", "type": gc.way_type["narrowTwoWay"], "isActive": True},
    "7": {"startNode": "5", "endNode": "7", "type": gc.way_type["twoWay"], "isActive": True},
    "8": {"startNode": "7", "endNode": "8", "type": gc.way_type["twoWay"], "isActive": True},
    "9": {"startNode": "8", "endNode": "9", "type": gc.way_type["narrowTwoWay"], "isActive": True},
    "10": {"startNode": "7", "endNode": "10", "type": gc.way_type["twoWay"], "isActive": True},
    "11": {"startNode": "11", "endNode": "10", "type": gc.way_type["oneWay"], "isActive": True},
    "12": {"startNode": "12", "endNode": "11", "type": gc.way_type["oneWay"], "isActive": True},
    "13": {"startNode": "13", "endNode": "12", "type": gc.way_type["oneWay"], "isActive": True},
    "14": {"startNode": "14", "endNode": "13", "type": gc.way_type["oneWay"], "isActive": True},
    "15": {"startNode": "10", "endNode": "14", "type": gc.way_type["twoWay"], "isActive": True},
    "16": {"startNode": "14", "endNode": "15", "type": gc.way_type["twoWay"], "isActive": True},
    "17": {"startNode": "15", "endNode": "16", "type": gc.way_type["twoWay"], "isActive": True},
    "18": {"startNode": "16", "endNode": "17", "type": gc.way_type["narrowTwoWay"], "isActive": True},
    "19": {"startNode": "15", "endNode": "18", "type": gc.way_type["twoWay"], "isActive": True},
    "20": {"startNode": "19", "endNode": "18", "type": gc.way_type["oneWay"], "isActive": True},
    "21": {"startNode": "20", "endNode": "19", "type": gc.way_type["oneWay"], "isActive": True},
    "22": {"startNode": "21", "endNode": "20", "type": gc.way_type["oneWay"], "isActive": True},
    "23": {"startNode": "22", "endNode": "21", "type": gc.way_type["oneWay"], "isActive": True},
    "24": {"startNode": "22", "endNode": "18", "type": gc.way_type["twoWay"], "isActive": True},
    "25": {"startNode": "22", "endNode": "23", "type": gc.way_type["twoWay"], "isActive": True},
    "26": {"startNode": "23", "endNode": "24", "type": gc.way_type["twoWay"], "isActive": True},
    "27": {"startNode": "24", "endNode": "25", "type": gc.way_type["oneWay"], "isActive": True},
    "28": {"startNode": "25", "endNode": "26", "type": gc.way_type["oneWay"], "isActive": True},
    "29": {"startNode": "26", "endNode": "27", "type": gc.way_type["oneWay"], "isActive": True},
    "30": {"startNode": "27", "endNode": "28", "type": gc.way_type["oneWay"], "isActive": True},
    "31": {"startNode": "24", "endNode": "28", "type": gc.way_type["twoWay"], "isActive": True},
    "32": {"startNode": "28", "endNode": "29", "type": gc.way_type["twoWay"], "isActive": True},
    "33": {"startNode": "29", "endNode": "3", "type": gc.way_type["twoWay"], "isActive": True},
    "34": {"startNode": "30", "endNode": "10", "type": gc.way_type["narrowTwoWay"], "isActive": True},
    "35": {"startNode": "31", "endNode": "18", "type": gc.way_type["narrowTwoWay"], "isActive": True},
    "36": {"startNode": "32", "endNode": "28", "type": gc.way_type["narrowTwoWay"], "isActive": True},
}

pois_raw = [
    {"id": "1", "pose": None, "type": gc.base_node_type["queue"]},  # "name": "Q", "pos": (-5,7)
    {"id": "2", "pose": None, "type": gc.base_node_type["parking"]},  # "name": "P", "pos": (3,7)
    {"id": "3", "pose": None, "type": gc.base_node_type["unload"]},  # "name": "POI3", "pos": (11,7)
    {"id": "4", "pose": None, "type": gc.base_node_type["charger"]},  # "name": "C", "pos": (12,0)
    {"id": "5", "pose": None, "type": gc.base_node_type["unload-dock"]},  # "name": "POI4", "pos": (12,7)
    {"id": "6", "pose": None, "type": gc.base_node_type["load"]},  # "name": "POI1", "pos": (-3,-8)
    {"id": "7", "pose": None, "type": gc.base_node_type["load-dock"]},  # "name": "POI2", "pos": (-6,0)
    {"id": "8", "pose": None, "type": gc.base_node_type["charger"]},  # "name": "POI8", "pos": (5,7)
    {"id": "9", "pose": None, "type": gc.base_node_type["load"]},  # "name": "POI9", "pos": (0,-2)
    {"id": "10", "pose": None, "type": gc.base_node_type["load-dock"]}  # "name": "POI10", "pos": (-10,2)

]
