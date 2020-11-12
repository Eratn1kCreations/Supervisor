import graph_creator as gc

node_list = {  # kluczem jest ID wezla
    1: {"name": "D1", "pos": (14, 24), "type": gc.base_node_type["waiting"], "poiId": 0},
    2: {"name": "D2", "pos": (8, 13), "type": gc.base_node_type["waiting"], "poiId": 0},
    3: {"name": "D3", "pos": (20, 17), "type": gc.base_node_type["waiting"], "poiId": 0},
    4: {"name": "D4", "pos": (20, 7), "type": gc.base_node_type["waiting"], "poiId": 0},
    5: {"name": "D5", "pos": (27, 14), "type": gc.base_node_type["waiting"], "poiId": 0},
    6: {"name": "D6", "pos": (29, 24), "type": gc.base_node_type["waiting"], "poiId": 0},
    7: {"name": "D7", "pos": (8, 20), "type": gc.base_node_type["waiting"], "poiId": 0},
    8: {"name": "D8", "pos": (4, 6), "type": gc.base_node_type["waiting"], "poiId": 0},
    9: {"name": "D9", "pos": (13, 6), "type": gc.base_node_type["waiting"], "poiId": 0},
    10: {"name": "D10", "pos": (28, 7), "type": gc.base_node_type["waiting"], "poiId": 0},
    11: {"name": "D11", "pos": (33, 17), "type": gc.base_node_type["waiting"], "poiId": 0},
    
    12: {"name": "O1", "pos": (12, 24), "type": gc.base_node_type["departure"], "poiId": 0},
    13: {"name": "O2", "pos": (10, 13), "type": gc.base_node_type["departure"], "poiId": 0},
    14: {"name": "O3", "pos": (20, 19), "type": gc.base_node_type["departure"], "poiId": 0},
    15: {"name": "O4", "pos": (20, 9), "type": gc.base_node_type["departure"], "poiId": 0},
    16: {"name": "O5", "pos": (27, 16), "type": gc.base_node_type["departure"], "poiId": 0},
    17: {"name": "O6", "pos": (29, 22), "type": gc.base_node_type["departure"], "poiId": 0},
    18: {"name": "O7", "pos": (6, 20), "type": gc.base_node_type["departure"], "poiId": 0},
    19: {"name": "O8", "pos": (6, 6), "type": gc.base_node_type["departure"], "poiId": 0},
    20: {"name": "O9", "pos": (15, 6), "type": gc.base_node_type["departure"], "poiId": 0},
    21: {"name": "O10", "pos": (28, 9), "type": gc.base_node_type["departure"], "poiId": 0},
    22: {"name": "O11", "pos": (33, 19), "type": gc.base_node_type["departure"], "poiId": 0},
    
    23: {"name": "S1", "pos": (13, 24), "type": gc.base_node_type["load-unload-dock"], "poiId": 1},
    24: {"name": "S2", "pos": (9, 13), "type": gc.base_node_type["load-unload-dock"], "poiId": 2},
    25: {"name": "S3", "pos": (20, 18), "type": gc.base_node_type["load-unload-dock"], "poiId": 3},
    26: {"name": "S4", "pos": (20, 8), "type": gc.base_node_type["load-unload"], "poiId": 4},
    27: {"name": "S5", "pos": (27, 15), "type": gc.base_node_type["load-unload"], "poiId": 5},
    28: {"name": "S6", "pos": (29, 23), "type": gc.base_node_type["load-unload"], "poiId": 6},
    29: {"name": "S7", "pos": (7, 20), "type": gc.base_node_type["load-unload"], "poiId": 7},
    30: {"name": "S8", "pos": (5, 6), "type": gc.base_node_type["load-unload"], "poiId": 8},
    31: {"name": "S9", "pos": (14, 6), "type": gc.base_node_type["load-unload"], "poiId": 9},
    32: {"name": "S10", "pos": (28, 8), "type": gc.base_node_type["load-unload-dock"], "poiId": 10},
    33: {"name": "S11", "pos": (33, 18), "type": gc.base_node_type["load-unload"], "poiId": 11},
    
    34: {"name": "P1", "pos": (11, 16), "type": gc.base_node_type["parking"], "poiId": 12},
    35: {"name": "P2", "pos": (13, 16), "type": gc.base_node_type["parking"], "poiId": 13},
    36: {"name": "P3", "pos": (17, 1), "type": gc.base_node_type["parking"], "poiId": 14},
    37: {"name": "P4", "pos": (20, 1), "type": gc.base_node_type["parking"], "poiId": 15},
    38: {"name": "P5", "pos": (24, 1), "type": gc.base_node_type["parking"], "poiId": 16},
    
    39: {"name": "WP1", "pos": (17, 12), "type": gc.base_node_type["queue"], "poiId": 17},
    40: {"name": "WP2", "pos": (26, 25), "type": gc.base_node_type["queue"], "poiId": 18},

    41: {"name": "L1", "pos": (32, 3), "type": gc.base_node_type["charger"], "poiId": 19},
    42: {"name": "DL2", "pos": (32, 4), "type": gc.base_node_type["waiting"], "poiId": 0},
    43: {"name": "OL3", "pos": (32, 2), "type": gc.base_node_type["departure"], "poiId": 0},

    44: {"name": "Z1", "pos": (12, 19), "type": gc.base_node_type["normal"], "poiId": 0},
    45: {"name": "Z2", "pos": (20, 10), "type": gc.base_node_type["normal"], "poiId": 0},
    46: {"name": "Z3", "pos": (20, 13), "type": gc.base_node_type["normal"], "poiId": 0},
    47: {"name": "Z4", "pos": (6, 14), "type": gc.base_node_type["normal"], "poiId": 0},
    48: {"name": "Z5", "pos": (17, 3), "type": gc.base_node_type["normal"], "poiId": 0},
    49: {"name": "Z6", "pos": (16, 13), "type": gc.base_node_type["normal"], "poiId": 0},
    50: {"name": "Z7", "pos": (25, 25), "type": gc.base_node_type["normal"], "poiId": 0},
    51: {"name": "Z8", "pos": (30, 4), "type": gc.base_node_type["normal"], "poiId": 0},
    52: {"name": "Z9", "pos": (30, 2), "type": gc.base_node_type["normal"], "poiId": 0},
    53: {"name": "Z10", "pos": (19, 24), "type": gc.base_node_type["normal"], "poiId": 0},
    
    54: {"name": "N1", "pos": (19, 23), "type": gc.base_node_type["intersection"], "poiId": 0},
    55: {"name": "N2", "pos": (25, 24), "type": gc.base_node_type["intersection"], "poiId": 0},
    56: {"name": "N3", "pos": (26, 24), "type": gc.base_node_type["intersection"], "poiId": 0},
    57: {"name": "N4", "pos": (26, 22), "type": gc.base_node_type["intersection"], "poiId": 0},
    58: {"name": "N5", "pos": (26, 19), "type": gc.base_node_type["intersection"], "poiId": 0},
    59: {"name": "N6", "pos": (26, 17), "type": gc.base_node_type["intersection"], "poiId": 0},
    60: {"name": "N7", "pos": (26, 16), "type": gc.base_node_type["intersection"], "poiId": 0},
    61: {"name": "N8", "pos": (26, 14), "type": gc.base_node_type["intersection"], "poiId": 0},
    62: {"name": "N9", "pos": (26, 9), "type": gc.base_node_type["intersection"], "poiId": 0},
    63: {"name": "N10", "pos": (26, 7), "type": gc.base_node_type["intersection"], "poiId": 0},
    64: {"name": "N11", "pos": (26, 3), "type": gc.base_node_type["intersection"], "poiId": 0},
    65: {"name": "N12", "pos": (24, 3), "type": gc.base_node_type["intersection"], "poiId": 0},
    66: {"name": "N13", "pos": (20, 3), "type": gc.base_node_type["intersection"], "poiId": 0},
    67: {"name": "N14", "pos": (19, 3), "type": gc.base_node_type["intersection"], "poiId": 0},
    68: {"name": "N15", "pos": (30, 3), "type": gc.base_node_type["intersection"], "poiId": 0},
    69: {"name": "N16", "pos": (14, 23), "type": gc.base_node_type["intersection"], "poiId": 0},
    70: {"name": "N17", "pos": (12, 23), "type": gc.base_node_type["intersection"], "poiId": 0},
    71: {"name": "N18", "pos": (8, 19), "type": gc.base_node_type["intersection"], "poiId": 0},
    72: {"name": "N19", "pos": (6, 19), "type": gc.base_node_type["intersection"], "poiId": 0},
    73: {"name": "N20", "pos": (8, 14), "type": gc.base_node_type["intersection"], "poiId": 0},
    74: {"name": "N21", "pos": (10, 14), "type": gc.base_node_type["intersection"], "poiId": 0},
    75: {"name": "N22", "pos": (11, 14), "type": gc.base_node_type["intersection"], "poiId": 0},
    76: {"name": "N23", "pos": (13, 14), "type": gc.base_node_type["intersection"], "poiId": 0},
    77: {"name": "N24", "pos": (16, 14), "type": gc.base_node_type["intersection"], "poiId": 0},
    78: {"name": "N25", "pos": (17, 14), "type": gc.base_node_type["intersection"], "poiId": 0},
    79: {"name": "N26", "pos": (19, 19), "type": gc.base_node_type["intersection"], "poiId": 0},
    80: {"name": "N27", "pos": (19, 17), "type": gc.base_node_type["intersection"], "poiId": 0},
    81: {"name": "N28", "pos": (19, 14), "type": gc.base_node_type["intersection"], "poiId": 0},
    82: {"name": "N29", "pos": (19, 9), "type": gc.base_node_type["intersection"], "poiId": 0},
    83: {"name": "N30", "pos": (19, 8), "type": gc.base_node_type["intersection"], "poiId": 0},
    84: {"name": "N31", "pos": (19, 7), "type": gc.base_node_type["intersection"], "poiId": 0},
    85: {"name": "N32", "pos": (15, 8), "type": gc.base_node_type["intersection"], "poiId": 0},
    86: {"name": "N33", "pos": (13, 8), "type": gc.base_node_type["intersection"], "poiId": 0},
    87: {"name": "N34", "pos": (6, 8), "type": gc.base_node_type["intersection"], "poiId": 0},
    88: {"name": "N35", "pos": (4, 8), "type": gc.base_node_type["intersection"], "poiId": 0},
}

edge_list = {
    #  Krawędzie dojazdu do miejsca oczekiwania na dojazd do stanowiska
    1: {"startNode": 69, "endNode": 1, "type": gc.way_type["oneWay"], "isActive": True},
    2: {"startNode": 73, "endNode": 2, "type": gc.way_type["oneWay"], "isActive": True},
    3: {"startNode": 80, "endNode": 3, "type": gc.way_type["oneWay"], "isActive": True},
    4: {"startNode": 84, "endNode": 4, "type": gc.way_type["oneWay"], "isActive": True},
    5: {"startNode": 61, "endNode": 5, "type": gc.way_type["oneWay"], "isActive": True},
    6: {"startNode": 56, "endNode": 6, "type": gc.way_type["oneWay"], "isActive": True},
    7: {"startNode": 71, "endNode": 7, "type": gc.way_type["oneWay"], "isActive": True},
    8: {"startNode": 88, "endNode": 8, "type": gc.way_type["oneWay"], "isActive": True},
    9: {"startNode": 86, "endNode": 9, "type": gc.way_type["oneWay"], "isActive": True},
    10: {"startNode": 63, "endNode": 10, "type": gc.way_type["oneWay"], "isActive": True},
    11: {"startNode": 59, "endNode": 11, "type": gc.way_type["oneWay"], "isActive": True},
    
    #  Krawędzie dojazdu do stanowiska
    12: {"startNode": 1, "endNode": 23, "type": gc.way_type["oneWay"], "isActive": True},
    13: {"startNode": 2, "endNode": 24, "type": gc.way_type["oneWay"], "isActive": True},
    14: {"startNode": 3, "endNode": 25, "type": gc.way_type["oneWay"], "isActive": True},
    15: {"startNode": 4, "endNode": 26, "type": gc.way_type["oneWay"], "isActive": True},
    16: {"startNode": 5, "endNode": 27, "type": gc.way_type["oneWay"], "isActive": True},
    17: {"startNode": 6, "endNode": 28, "type": gc.way_type["oneWay"], "isActive": True},
    18: {"startNode": 7, "endNode": 29, "type": gc.way_type["oneWay"], "isActive": True},
    19: {"startNode": 8, "endNode": 30, "type": gc.way_type["oneWay"], "isActive": True},
    20: {"startNode": 9, "endNode": 31, "type": gc.way_type["oneWay"], "isActive": True},
    21: {"startNode": 10, "endNode": 32, "type": gc.way_type["oneWay"], "isActive": True},
    22: {"startNode": 11, "endNode": 33, "type": gc.way_type["oneWay"], "isActive": True},

    #  Krawędzie odjazdu od stanowiska
    23: {"startNode": 23, "endNode": 12, "type": gc.way_type["oneWay"], "isActive": True},
    24: {"startNode": 24, "endNode": 13, "type": gc.way_type["oneWay"], "isActive": True},
    25: {"startNode": 25, "endNode": 14, "type": gc.way_type["oneWay"], "isActive": True},
    26: {"startNode": 26, "endNode": 15, "type": gc.way_type["oneWay"], "isActive": True},
    27: {"startNode": 27, "endNode": 16, "type": gc.way_type["oneWay"], "isActive": True},
    28: {"startNode": 28, "endNode": 17, "type": gc.way_type["oneWay"], "isActive": True},
    29: {"startNode": 29, "endNode": 18, "type": gc.way_type["oneWay"], "isActive": True},
    30: {"startNode": 30, "endNode": 19, "type": gc.way_type["oneWay"], "isActive": True},
    31: {"startNode": 31, "endNode": 20, "type": gc.way_type["oneWay"], "isActive": True},
    32: {"startNode": 32, "endNode": 21, "type": gc.way_type["oneWay"], "isActive": True},
    33: {"startNode": 33, "endNode": 22, "type": gc.way_type["oneWay"], "isActive": True},
    
    #  Krawędzie odjazdu od stanowiska do głównego szlaku komunikacyjnego
    34: {"startNode": 12, "endNode": 70, "type": gc.way_type["oneWay"], "isActive": True},
    35: {"startNode": 13, "endNode": 74, "type": gc.way_type["oneWay"], "isActive": True},
    36: {"startNode": 14, "endNode": 79, "type": gc.way_type["oneWay"], "isActive": True},
    37: {"startNode": 15, "endNode": 82, "type": gc.way_type["oneWay"], "isActive": True},
    38: {"startNode": 16, "endNode": 60, "type": gc.way_type["oneWay"], "isActive": True},
    39: {"startNode": 17, "endNode": 57, "type": gc.way_type["oneWay"], "isActive": True},
    40: {"startNode": 18, "endNode": 72, "type": gc.way_type["oneWay"], "isActive": True},
    41: {"startNode": 19, "endNode": 87, "type": gc.way_type["oneWay"], "isActive": True},
    42: {"startNode": 20, "endNode": 85, "type": gc.way_type["oneWay"], "isActive": True},
    43: {"startNode": 21, "endNode": 62, "type": gc.way_type["oneWay"], "isActive": True},
    44: {"startNode": 22, "endNode": 58, "type": gc.way_type["oneWay"], "isActive": True},

    #  krawędzie dla parkingów
    45: {"startNode": 34, "endNode": 75, "type": gc.way_type["narrowTwoWay"], "isActive": True},
    46: {"startNode": 35, "endNode": 76, "type": gc.way_type["narrowTwoWay"], "isActive": True},
    47: {"startNode": 36, "endNode": 48, "type": gc.way_type["narrowTwoWay"], "isActive": True},
    48: {"startNode": 37, "endNode": 66, "type": gc.way_type["narrowTwoWay"], "isActive": True},
    49: {"startNode": 38, "endNode": 65, "type": gc.way_type["narrowTwoWay"], "isActive": True},

    #  krawędzie dla węzłow postojowych
    50: {"startNode": 77, "endNode": 49, "type": gc.way_type["oneWay"], "isActive": True},
    51: {"startNode": 49, "endNode": 39, "type": gc.way_type["oneWay"], "isActive": True},
    52: {"startNode": 39, "endNode": 78, "type": gc.way_type["oneWay"], "isActive": True},
    53: {"startNode": 55, "endNode": 50, "type": gc.way_type["oneWay"], "isActive": True},
    54: {"startNode": 50, "endNode": 40, "type": gc.way_type["oneWay"], "isActive": True},
    55: {"startNode": 40, "endNode": 56, "type": gc.way_type["oneWay"], "isActive": True},

    #  krawędzie dla ładowarek
    56: {"startNode": 68, "endNode": 51, "type": gc.way_type["oneWay"], "isActive": True},
    57: {"startNode": 51, "endNode": 42, "type": gc.way_type["oneWay"], "isActive": True},
    58: {"startNode": 42, "endNode": 41, "type": gc.way_type["oneWay"], "isActive": True},
    59: {"startNode": 41, "endNode": 43, "type": gc.way_type["oneWay"], "isActive": True},
    60: {"startNode": 43, "endNode": 52, "type": gc.way_type["oneWay"], "isActive": True},
    61: {"startNode": 52, "endNode": 68, "type": gc.way_type["oneWay"], "isActive": True},
    
    #  krawędzie dla skrzyżowań i zwykłych przejazdów
    62: {"startNode": 72, "endNode": 71, "type": gc.way_type["twoWay"], "isActive": True},
    63: {"startNode": 71, "endNode": 44, "type": gc.way_type["twoWay"], "isActive": True},
    64: {"startNode": 44, "endNode": 70, "type": gc.way_type["twoWay"], "isActive": True},
    65: {"startNode": 70, "endNode": 69, "type": gc.way_type["twoWay"], "isActive": True},
    66: {"startNode": 69, "endNode": 54, "type": gc.way_type["twoWay"], "isActive": True},
    67: {"startNode": 54, "endNode": 53, "type": gc.way_type["twoWay"], "isActive": True},
    68: {"startNode": 53, "endNode": 55, "type": gc.way_type["twoWay"], "isActive": True},
    69: {"startNode": 55, "endNode": 56, "type": gc.way_type["twoWay"], "isActive": True},
    70: {"startNode": 56, "endNode": 57, "type": gc.way_type["twoWay"], "isActive": True},
    71: {"startNode": 57, "endNode": 58, "type": gc.way_type["twoWay"], "isActive": True},
    72: {"startNode": 58, "endNode": 59, "type": gc.way_type["twoWay"], "isActive": True},
    73: {"startNode": 59, "endNode": 60, "type": gc.way_type["twoWay"], "isActive": True},
    74: {"startNode": 60, "endNode": 61, "type": gc.way_type["twoWay"], "isActive": True},
    75: {"startNode": 61, "endNode": 62, "type": gc.way_type["twoWay"], "isActive": True},
    76: {"startNode": 62, "endNode": 63, "type": gc.way_type["twoWay"], "isActive": True},
    77: {"startNode": 63, "endNode": 64, "type": gc.way_type["twoWay"], "isActive": True},
    78: {"startNode": 64, "endNode": 68, "type": gc.way_type["twoWay"], "isActive": True},
    79: {"startNode": 64, "endNode": 65, "type": gc.way_type["twoWay"], "isActive": True},
    80: {"startNode": 65, "endNode": 66, "type": gc.way_type["twoWay"], "isActive": True},
    81: {"startNode": 66, "endNode": 67, "type": gc.way_type["twoWay"], "isActive": True},
    82: {"startNode": 67, "endNode": 48, "type": gc.way_type["narrowTwoWay"], "isActive": True},
    83: {"startNode": 67, "endNode": 84, "type": gc.way_type["twoWay"], "isActive": True},
    84: {"startNode": 84, "endNode": 83, "type": gc.way_type["twoWay"], "isActive": True},
    85: {"startNode": 83, "endNode": 85, "type": gc.way_type["twoWay"], "isActive": True},
    86: {"startNode": 85, "endNode": 86, "type": gc.way_type["twoWay"], "isActive": True},
    87: {"startNode": 86, "endNode": 87, "type": gc.way_type["twoWay"], "isActive": True},
    88: {"startNode": 87, "endNode": 88, "type": gc.way_type["twoWay"], "isActive": True},
    89: {"startNode": 83, "endNode": 82, "type": gc.way_type["twoWay"], "isActive": True},
    90: {"startNode": 82, "endNode": 45, "type": gc.way_type["twoWay"], "isActive": True},
    91: {"startNode": 45, "endNode": 46, "type": gc.way_type["twoWay"], "isActive": True},
    92: {"startNode": 46, "endNode": 81, "type": gc.way_type["twoWay"], "isActive": True},
    93: {"startNode": 81, "endNode": 80, "type": gc.way_type["twoWay"], "isActive": True},
    94: {"startNode": 80, "endNode": 79, "type": gc.way_type["twoWay"], "isActive": True},
    95: {"startNode": 79, "endNode": 54, "type": gc.way_type["twoWay"], "isActive": True},
    96: {"startNode": 81, "endNode": 78, "type": gc.way_type["twoWay"], "isActive": True},
    97: {"startNode": 78, "endNode": 77, "type": gc.way_type["twoWay"], "isActive": True},
    98: {"startNode": 77, "endNode": 76, "type": gc.way_type["twoWay"], "isActive": True},
    99: {"startNode": 76, "endNode": 75, "type": gc.way_type["twoWay"], "isActive": True},
    100: {"startNode": 75, "endNode": 74, "type": gc.way_type["twoWay"], "isActive": True},
    101: {"startNode": 74, "endNode": 73, "type": gc.way_type["twoWay"], "isActive": True},
    102: {"startNode": 73, "endNode": 47, "type": gc.way_type["twoWay"], "isActive": True},
    103: {"startNode": 47, "endNode": 72, "type": gc.way_type["twoWay"], "isActive": True}
}

graf = gc.SupervisorGraphCreator(node_list, edge_list)
print("wezly grafu")
for node in graf.get_graph().nodes(data=True):
    print(node)
print("krawedzie grafu")
for edge in graf.get_graph().edges(data=True):
    print(edge)
graf.print_graph()
