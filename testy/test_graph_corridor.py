# -*- coding: utf-8 -*-
import pytest
from test_data import node_dict, edge_dict, pois_raw
import graph_creator as gc

gc.OFFLINE_TEST = False
gc.MAIN_CORRIDOR_WIDTH = 0.3
gc.ROBOT_CORRIDOR_WIDTH = 0.3
gc.WAITING_STOP_DIST_TO_INTERSECTION = 0.4 + 0.3
graph = gc.SupervisorGraphCreator(node_dict, edge_dict, pois_raw)


def truncate(n):
    multiplier = 10 ** 3
    return int(n * multiplier) / multiplier


# ------------------------------ Graph corridors ------------------------------ #
@pytest.mark.graph
def test_graph_corridor_generator_1_main_path():
    # print(graph.get_corridor_path((52, 53)))
    # graph.print_corridor((52, 53))
    result = [(truncate(point[0]), truncate(point[1])) for point in graph.get_corridor_path((52, 53))]
    # print(result)
    assert result == [(-4.3, -5.15), (-0.7, -5.15)]


@pytest.mark.graph
def test_graph_corridor_generator_2_intersection():
    start = 53
    end = 47
    # print(graph.get_corridor_path((start, end)))
    # graph.print_corridor((start, end))
    result = [(truncate(point[0]), truncate(point[1])) for point in graph.get_corridor_path((start, end))]
    # print(result)
    assert result == [(-0.7, -5.15), (-0.15, -5.15), (0.15, -5.15), (0.7, -5.15)]


@pytest.mark.graph
def test_graph_corridor_generator_3_main_path():
    start = 58
    end = 59
    # print(graph.get_corridor_path((start, end)))
    # graph.print_corridor((start, end))
    result = [(truncate(point[0]), truncate(point[1])) for point in graph.get_corridor_path((start, end))]
    # print(result)
    assert result == [(-7.15, -2.7), (-7.15, -5.15), (-5.7, -5.15)]


@pytest.mark.graph
def test_graph_corridor_generator_4_main_path():
    start = 56
    end = 57
    # print(graph.get_corridor_path((start, end)))
    # graph.print_corridor((start, end))
    result = [(truncate(point[0]), truncate(point[1])) for point in graph.get_corridor_path((start, end))]
    # print(result)
    assert result == [(-5.7, -4.85), (-6.85, -4.85), (-6.85, -2.7)]


@pytest.mark.graph
def test_graph_corridor_generator_5_waiting_poi_edge():
    start = 51
    end = 21
    # print(graph.get_corridor_path((start, end)))
    # graph.print_corridor((start, end))
    result = [(truncate(point[0]), truncate(point[1])) for point in graph.get_corridor_path((start, end))]
    # print(result)
    assert result == [(-5, -5.7), (-5, -8)]


@pytest.mark.graph
def test_graph_corridor_generator_6_waiting_poi_edge():
    start = 21
    end = 13
    # print(graph.get_corridor_path((start, end)))
    # graph.print_corridor((start, end))
    result = [(truncate(point[0]), truncate(point[1])) for point in graph.get_corridor_path((start, end))]
    # print(result)
    assert result == [(-5, -8), (-3, -8)]


@pytest.mark.graph
def test_graph_corridor_generator_7_departure_poi_edge():
    start = 14
    end = 20
    # print(graph.get_corridor_path((start, end)))
    # graph.print_corridor((start, end))
    result = [(truncate(point[0]), truncate(point[1])) for point in graph.get_corridor_path((start, end))]
    # print(result)
    assert result == [(-3, -8), (0, -8)]


@pytest.mark.graph
def test_graph_corridor_generator_8_departure_poi_edge():
    start = 20
    end = 50
    # print(graph.get_corridor_path((start, end)))
    # graph.print_corridor((start, end))
    result = [(truncate(point[0]), truncate(point[1])) for point in graph.get_corridor_path((start, end))]
    # print(result)
    assert result == [(0, -8), (0, -5.7)]


@pytest.mark.graph
def test_graph_corridor_generator_9_waiting_edge():
    start = 22
    end = 9
    # print(graph.get_corridor_path((start, end)))
    # graph.print_corridor((start, end))
    result = [(truncate(point[0]), truncate(point[1])) for point in graph.get_corridor_path((start, end))]
    # print(result)
    assert result == [(-5, -2), (-5, 0)]


@pytest.mark.graph
def test_graph_corridor_generator_10_departure_edge():
    start = 12
    end = 23
    # print(graph.get_corridor_path((start, end)))
    # graph.print_corridor((start, end))
    result = [(truncate(point[0]), truncate(point[1])) for point in graph.get_corridor_path((start, end))]
    # print(result)
    assert result == [(-5, 0), (-5, 2)]


@pytest.mark.graph
def test_graph_corridor_generator_11_queue():
    start = 49
    end = 17
    # print(graph.get_corridor_path((start, end)))
    # graph.print_corridor((start, end))
    result = [(truncate(point[0]), truncate(point[1])) for point in graph.get_corridor_path((start, end))]
    # print(result)
    assert result == [(-3, 5.7), (-3, 7), (-5, 7)]


@pytest.mark.graph
def test_graph_corridor_generator_12_queue():
    start = 17
    end = 61
    # print(graph.get_corridor_path((start, end)))
    # graph.print_corridor((start, end))
    result = [(truncate(point[0]), truncate(point[1])) for point in graph.get_corridor_path((start, end))]
    # print(result)
    assert result == [(-5, 7), (-5, 5.7)]


@pytest.mark.graph
def test_graph_corridor_generator_13_wait_dep_poi_dock():
    start = 43
    end = 5
    # print(graph.get_corridor_path((start, end)))
    # graph.print_corridor((start, end))
    result = [(truncate(point[0]), truncate(point[1])) for point in graph.get_corridor_path((start, end))]
    # print(result)
    assert result == [(8.7, -7), (12, -7)]


@pytest.mark.graph
def test_graph_corridor_generator_14_wait_dep_poi():
    start = 8
    end = 44
    # print(graph.get_corridor_path((start, end)))
    # graph.print_corridor((start, end))
    result = [(truncate(point[0]), truncate(point[1])) for point in graph.get_corridor_path((start, end))]
    # print(result)
    assert result == [(12, -7), (8.7, -7)]


@pytest.mark.graph
def test_graph_corridor_generator_15_parking():
    start = 79
    end = 24
    # print(graph.get_corridor_path((start, end)))
    # graph.print_corridor((start, end))
    result = [(truncate(point[0]), truncate(point[1])) for point in graph.get_corridor_path((start, end))]
    # print(result)
    assert result == [(3, 5.7), (3, 7)]


@pytest.mark.graph
def test_graph_corridor_generator_16_parking():
    start = 24
    end = 80
    # print(graph.get_corridor_path((start, end)))
    # graph.print_corridor((start, end))
    result = [(truncate(point[0]), truncate(point[1])) for point in graph.get_corridor_path((start, end))]
    # print(result)
    assert result == [(3, 7), (3, 5.7)]


@pytest.mark.graph
def test_graph_corridor_generator_17_wait_dep_poi():
    start = 89
    end = 15
    # print(graph.get_corridor_path((start, end)))
    # graph.print_corridor((start, end))
    result = [(truncate(point[0]), truncate(point[1])) for point in graph.get_corridor_path((start, end))]
    # print(result)
    assert result == [(11, 5.7), (11, 7)]


@pytest.mark.graph
def test_graph_corridor_generator_18_wait_dep_poi():
    start = 16
    end = 90
    # print(graph.get_corridor_path((start, end)))
    # graph.print_corridor((start, end))
    result = [(truncate(point[0]), truncate(point[1])) for point in graph.get_corridor_path((start, end))]
    # print(result)
    assert result == [(11, 7), (11, 5.7)]


# -------------------------- Drugi zestaw danych, wezly normalne w okolicach poi -------------------------
def get_id(name, node_list):
    for i in node_list.keys():
        if node_list[i]["name"] == name:
            return i


pois_raw2 = [
    {"id": "1", "pose": None, "type": gc.base_node_type["queue"]},  # "name": "Q", "pos": (6,4)
    {"id": "2", "pose": None, "type": gc.base_node_type["parking"]},  # "name": "P", "pos": (4,-2)
    {"id": "3", "pose": None, "type": gc.base_node_type["unload"]},  # "name": "POI1", "pos": (-6,-4)
    {"id": "4", "pose": None, "type": gc.base_node_type["load"]},  # "name": "POI2", "pos": (14,0)
]

node_dict2 = {
    1: {"name": "Q", "pos": (6, 4), "type": gc.base_node_type["queue"], "poiId": "1"},
    2: {"name": "P", "pos": (4, -2), "type": gc.base_node_type["parking"], "poiId": "2"},
    3: {"name": "POI1", "pos": (-6, -4), "type": gc.base_node_type["unload"], "poiId": "3"},
    4: {"name": "POI2", "pos": (14, 0), "type": gc.base_node_type["load"], "poiId": "4"},
    5: {"name": "I1", "pos": (-12, 2), "type": gc.base_node_type["intersection"], "poiId": "0"},
    6: {"name": "N1", "pos": (-12, 0), "type": gc.base_node_type["normal"], "poiId": "0"},
    7: {"name": "N2", "pos": (-10, 4), "type": gc.base_node_type["normal"], "poiId": "0"},
    8: {"name": "N3", "pos": (-10, 2), "type": gc.base_node_type["normal"], "poiId": "0"},
    9: {"name": "N4", "pos": (-10, 0), "type": gc.base_node_type["normal"], "poiId": "0"},
    10: {"name": "W", "pos": (-10, -2), "type": gc.base_node_type["waiting"], "poiId": "0"},
    11: {"name": "N5", "pos": (-8, -2), "type": gc.base_node_type["normal"], "poiId": "0"},
    12: {"name": "N6", "pos": (-8, -4), "type": gc.base_node_type["normal"], "poiId": "0"},
    13: {"name": "N7", "pos": (-6, 4), "type": gc.base_node_type["normal"], "poiId": "0"},
    14: {"name": "N8", "pos": (-6, 2), "type": gc.base_node_type["normal"], "poiId": "0"},
    15: {"name": "N9", "pos": (-4, -2), "type": gc.base_node_type["normal"], "poiId": "0"},
    16: {"name": "N10", "pos": (-4, -4), "type": gc.base_node_type["normal"], "poiId": "0"},
    17: {"name": "D", "pos": (-2, -2), "type": gc.base_node_type["departure"], "poiId": "0"},
    18: {"name": "I2", "pos": (0, 2), "type": gc.base_node_type["intersection"], "poiId": "0"},
    19: {"name": "N11", "pos": (0, -2), "type": gc.base_node_type["normal"], "poiId": "0"},
    20: {"name": "N12", "pos": (2, 4), "type": gc.base_node_type["normal"], "poiId": "0"},
    21: {"name": "I3", "pos": (2, 2), "type": gc.base_node_type["intersection"], "poiId": "0"},
    22: {"name": "N13", "pos": (2, -2), "type": gc.base_node_type["normal"], "poiId": "0"},
    23: {"name": "N14", "pos": (6, 0), "type": gc.base_node_type["normal"], "poiId": "0"},
    24: {"name": "N15", "pos": (8, 0), "type": gc.base_node_type["normal"], "poiId": "0"},
    25: {"name": "WD", "pos": (8, -2), "type": gc.base_node_type["waiting-departure"], "poiId": "0"},
    26: {"name": "N16", "pos": (10, 4), "type": gc.base_node_type["normal"], "poiId": "0"},
    27: {"name": "I4", "pos": (10, 2), "type": gc.base_node_type["intersection"], "poiId": "0"},
    28: {"name": "N17", "pos": (12, 0), "type": gc.base_node_type["normal"], "poiId": "0"},
    29: {"name": "N18", "pos": (12, -2), "type": gc.base_node_type["normal"], "poiId": "0"},
    30: {"name": "I5", "pos": (6, 2), "type": gc.base_node_type["intersection"], "poiId": "0"}
}

edge_dict2 = {
    # Krawędzie dojazdu do miejsca oczekiwania na dojazd do stanowiska
    1: {"startNode": get_id("I1", node_dict2), "endNode": get_id("N3", node_dict2),
        "type": gc.way_type["twoWay"], "isActive": True},
    2: {"startNode": get_id("N3", node_dict2), "endNode": get_id("N2", node_dict2),
        "type": gc.way_type["twoWay"], "isActive": True},
    3: {"startNode": get_id("N2", node_dict2), "endNode": get_id("N7", node_dict2),
        "type": gc.way_type["twoWay"], "isActive": True},
    4: {"startNode": get_id("N7", node_dict2), "endNode": get_id("N8", node_dict2),
        "type": gc.way_type["twoWay"], "isActive": True},
    5: {"startNode": get_id("N8", node_dict2), "endNode": get_id("I2", node_dict2),
        "type": gc.way_type["twoWay"], "isActive": True},
    6: {"startNode": get_id("I1", node_dict2), "endNode": get_id("N1", node_dict2),
        "type": gc.way_type["oneWay"], "isActive": True},
    7: {"startNode": get_id("N1", node_dict2), "endNode": get_id("N4", node_dict2),
        "type": gc.way_type["oneWay"], "isActive": True},
    8: {"startNode": get_id("N4", node_dict2), "endNode": get_id("W", node_dict2),
        "type": gc.way_type["oneWay"], "isActive": True},
    9: {"startNode": get_id("W", node_dict2), "endNode": get_id("N5", node_dict2),
        "type": gc.way_type["oneWay"], "isActive": True},
    10: {"startNode": get_id("N5", node_dict2), "endNode": get_id("N6", node_dict2),
         "type": gc.way_type["oneWay"], "isActive": True},
    11: {"startNode": get_id("N6", node_dict2), "endNode": get_id("POI1", node_dict2),
         "type": gc.way_type["oneWay"], "isActive": True},
    12: {"startNode": get_id("POI1", node_dict2), "endNode": get_id("N10", node_dict2),
         "type": gc.way_type["oneWay"], "isActive": True},
    13: {"startNode": get_id("N10", node_dict2), "endNode": get_id("N9", node_dict2),
         "type": gc.way_type["oneWay"], "isActive": True},
    14: {"startNode": get_id("N9", node_dict2), "endNode": get_id("D", node_dict2),
         "type": gc.way_type["oneWay"], "isActive": True},
    15: {"startNode": get_id("D", node_dict2), "endNode": get_id("N11", node_dict2),
         "type": gc.way_type["oneWay"], "isActive": True},
    16: {"startNode": get_id("N11", node_dict2), "endNode": get_id("I2", node_dict2),
         "type": gc.way_type["oneWay"], "isActive": True},
    17: {"startNode": get_id("I2", node_dict2), "endNode": get_id("I3", node_dict2),
         "type": gc.way_type["twoWay"], "isActive": True},
    18: {"startNode": get_id("I3", node_dict2), "endNode": get_id("N12", node_dict2),
         "type": gc.way_type["oneWay"], "isActive": True},
    19: {"startNode": get_id("N12", node_dict2), "endNode": get_id("Q", node_dict2),
         "type": gc.way_type["oneWay"], "isActive": True},
    20: {"startNode": get_id("Q", node_dict2), "endNode": get_id("N16", node_dict2),
         "type": gc.way_type["oneWay"], "isActive": True},
    21: {"startNode": get_id("N16", node_dict2), "endNode": get_id("I4", node_dict2),
         "type": gc.way_type["oneWay"], "isActive": True},
    22: {"startNode": get_id("I3", node_dict2), "endNode": get_id("I5", node_dict2),
         "type": gc.way_type["twoWay"], "isActive": True},
    23: {"startNode": get_id("I5", node_dict2), "endNode": get_id("I4", node_dict2),
         "type": gc.way_type["twoWay"], "isActive": True},
    24: {"startNode": get_id("I5", node_dict2), "endNode": get_id("N14", node_dict2),
         "type": gc.way_type["twoWay"], "isActive": True},
    25: {"startNode": get_id("N14", node_dict2), "endNode": get_id("N15", node_dict2),
         "type": gc.way_type["twoWay"], "isActive": True},
    26: {"startNode": get_id("N15", node_dict2), "endNode": get_id("WD", node_dict2),
         "type": gc.way_type["twoWay"], "isActive": True},
    27: {"startNode": get_id("WD", node_dict2), "endNode": get_id("N18", node_dict2),
         "type": gc.way_type["narrowTwoWay"], "isActive": True},
    28: {"startNode": get_id("N18", node_dict2), "endNode": get_id("N17", node_dict2),
         "type": gc.way_type["narrowTwoWay"], "isActive": True},
    29: {"startNode": get_id("N17", node_dict2), "endNode": get_id("POI2", node_dict2),
         "type": gc.way_type["narrowTwoWay"], "isActive": True},
    30: {"startNode": get_id("I3", node_dict2), "endNode": get_id("N13", node_dict2),
         "type": gc.way_type["narrowTwoWay"], "isActive": True},
    31: {"startNode": get_id("N13", node_dict2), "endNode": get_id("P", node_dict2),
         "type": gc.way_type["narrowTwoWay"], "isActive": True}
}
graph2 = gc.SupervisorGraphCreator(node_dict2, edge_dict2, pois_raw2)


@pytest.mark.graph
def test_graph_corridor_generator_19a_before_waiting_poi():
    start = 13
    end = 7
    # print(graph2.get_corridor_path((start, end)))
    # graph2.print_corridor((start, end))
    result = [(truncate(point[0]), truncate(point[1])) for point in graph2.get_corridor_path((start, end))]
    # print(result)
    assert result == [(-12, 1.3), (-12, 0), (-10, 0), (-10, -2)]


def test_graph_corridor_generator_19b_after_waiting_poi():
    start = 7
    end = 1
    # print(graph2.get_corridor_path((start, end)))
    # graph2.print_corridor((start, end))
    result = [(truncate(point[0]), truncate(point[1])) for point in graph2.get_corridor_path((start, end))]
    # print(result)
    assert result == [(-10, -2), (-8, -2), (-8, -4), (-6, -4)]


def test_graph_corridor_generator_20a_normal_wait_departure_before_poi():
    start = 2
    end = 8
    # print(graph2.get_corridor_path((start, end)))
    # graph2.print_corridor((start, end))
    result = [(truncate(point[0]), truncate(point[1])) for point in graph2.get_corridor_path((start, end))]
    # print(result)
    assert result == [(-6, -4), (-4, -4), (-4, -2), (-2, -2)]


def test_graph_corridor_generator_20b_normal_wait_departure_after_poi():
    start = 8
    end = 14
    # print(graph2.get_corridor_path((start, end)))
    # graph2.print_corridor((start, end))
    result = [(truncate(point[0]), truncate(point[1])) for point in graph2.get_corridor_path((start, end))]
    # print(result)
    assert result == [(-2, -2), (0, -2), (0, 1.3)]


def test_graph_corridor_generator_21a_before_poi_wait_dep():
    start = 29
    end = 30
    # print(graph2.get_corridor_path((start, end)))
    # graph2.print_corridor((start, end))
    result = [(truncate(point[0]), truncate(point[1])) for point in graph2.get_corridor_path((start, end))]
    # print(result)
    assert result == [(5.85, 1.3), (5.85, -0.15), (7.85, -0.15), (7.85, -1.3)]


def test_graph_corridor_generator_21b_before_poi_wait_dep():
    start = 31
    end = 32
    # print(graph2.get_corridor_path((start, end)))
    # graph2.print_corridor((start, end))
    result = [(truncate(point[0]), truncate(point[1])) for point in graph2.get_corridor_path((start, end))]
    # print(result)
    assert result == [(8.15, -1.3), (8.15, 0.15), (6.15, 0.15), (6.15, 1.3)]


def test_graph_corridor_generator_21c_intersection():
    start = 30
    end = 31
    # print(graph2.get_corridor_path((start, end)))
    # graph2.print_corridor((start, end))
    result = [(truncate(point[0]), truncate(point[1])) for point in graph2.get_corridor_path((start, end))]
    # print(result)
    assert result == [(7.85, -1.3), (8.15, -1.3)]


def test_graph_corridor_generator_21d_intersection():
    start = 30
    end = 33
    # print(graph2.get_corridor_path((start, end)))
    # graph2.print_corridor((start, end))
    result = [(truncate(point[0]), truncate(point[1])) for point in graph2.get_corridor_path((start, end))]
    # print(result)
    assert result == [(7.85, -1.3), (7.85, -1.85), (8.15, -2.0), (8.7, -2.0)]


def test_graph_corridor_generator_21e_intersection():
    start = 34
    end = 31
    # print(graph2.get_corridor_path((start, end)))
    # graph2.print_corridor((start, end))
    result = [(truncate(point[0]), truncate(point[1])) for point in graph2.get_corridor_path((start, end))]
    # print(result)
    assert result == [(8.7, -2.0), (8.15, -2.0), (8.15, -1.85), (8.15, -1.3)]


def test_graph_corridor_generator_21f_intersection():
    start = 34
    end = 33
    # print(graph2.get_corridor_path((start, end)))
    # graph2.print_corridor((start, end))
    result = [(truncate(point[0]), truncate(point[1])) for point in graph2.get_corridor_path((start, end))]
    # print(result)
    assert result == [(8.7, -2.0), (8.7, -2.0)]


def test_graph_corridor_generator_21f_after_poi():
    start = 33
    end = 3
    # print(graph2.get_corridor_path((start, end)))
    # graph2.print_corridor((start, end))
    result = [(truncate(point[0]), truncate(point[1])) for point in graph2.get_corridor_path((start, end))]
    # print(result)
    assert result == [(8.7, -2), (12, -2), (12, 0), (14, 0)]


def test_graph_corridor_generator_21g_after_poi():
    start = 4
    end = 34
    # print(graph2.get_corridor_path((start, end)))
    # graph2.print_corridor((start, end))
    result = [(truncate(point[0]), truncate(point[1])) for point in graph2.get_corridor_path((start, end))]
    # print(result)
    assert result == [(14, 0), (12, 0), (12, -2), (8.7, -2)]


def test_graph_corridor_generator_22a_parking():
    start = 35
    end = 6
    # print(graph2.get_corridor_path((start, end)))
    # graph2.print_corridor((start, end))
    result = [(truncate(point[0]), truncate(point[1])) for point in graph2.get_corridor_path((start, end))]
    # print(result)
    assert result == [(2, 1.3), (2, -2), (4, -2)]


def test_graph_corridor_generator_22b_parking():
    start = 6
    end = 36
    # print(graph2.get_corridor_path((start, end)))
    # graph2.print_corridor((start, end))
    result = [(truncate(point[0]), truncate(point[1])) for point in graph2.get_corridor_path((start, end))]
    # print(result)
    assert result == [(4, -2), (2, -2), (2, 1.3)]


def test_graph_corridor_generator_23a_queue():
    start = 19
    end = 5
    # print(graph2.get_corridor_path((start, end)))
    # graph2.print_corridor((start, end))
    result = [(truncate(point[0]), truncate(point[1])) for point in graph2.get_corridor_path((start, end))]
    # print(result)
    assert result == [(2, 2.7), (2, 4), (6, 4)]


def test_graph_corridor_generator_23b_queue():
    start = 5
    end = 20
    # print(graph2.get_corridor_path((start, end)))
    # graph2.print_corridor((start, end))
    result = [(truncate(point[0]), truncate(point[1])) for point in graph2.get_corridor_path((start, end))]
    # print(result)
    assert result == [(6, 4), (10, 4), (10, 2.7)]


# -------------------------- 3 zestaw danych, waiting-departure poi -------------------------
def get_id(name, node_list):
    for i in node_list.keys():
        if node_list[i]["name"] == name:
            return i


pois_raw3 = [
    {"id": "1", "pose": None, "type": gc.base_node_type["unload-dock"]},  # "name": "POI1", "pos": (-6,-4)
    {"id": "2", "pose": None, "type": gc.base_node_type["load-dock"]},  # "name": "POI2", "pos": (14,0)
]

node_dict3 = {
    1: {"name": "POI1", "pos": (-6, -4), "type": gc.base_node_type["unload"], "poiId": "1"},
    2: {"name": "POI2", "pos": (14, 0), "type": gc.base_node_type["load"], "poiId": "2"},
    3: {"name": "I1", "pos": (-12, 2), "type": gc.base_node_type["intersection"], "poiId": "0"},
    4: {"name": "N1", "pos": (-12, 0), "type": gc.base_node_type["normal"], "poiId": "0"},
    5: {"name": "N2", "pos": (-10, 4), "type": gc.base_node_type["normal"], "poiId": "0"},
    6: {"name": "N3", "pos": (-10, 2), "type": gc.base_node_type["normal"], "poiId": "0"},
    7: {"name": "N4", "pos": (-10, 0), "type": gc.base_node_type["normal"], "poiId": "0"},
    8: {"name": "W", "pos": (-10, -2), "type": gc.base_node_type["waiting"], "poiId": "0"},
    9: {"name": "N5", "pos": (-8, -2), "type": gc.base_node_type["normal"], "poiId": "0"},
    10: {"name": "N6", "pos": (-8, -4), "type": gc.base_node_type["normal"], "poiId": "0"},
    11: {"name": "N7", "pos": (-6, 4), "type": gc.base_node_type["normal"], "poiId": "0"},
    12: {"name": "N8", "pos": (-6, 2), "type": gc.base_node_type["normal"], "poiId": "0"},
    13: {"name": "N9", "pos": (-4, -2), "type": gc.base_node_type["normal"], "poiId": "0"},
    14: {"name": "N10", "pos": (-4, -4), "type": gc.base_node_type["normal"], "poiId": "0"},
    15: {"name": "D", "pos": (-2, -2), "type": gc.base_node_type["departure"], "poiId": "0"},
    16: {"name": "I2", "pos": (0, 2), "type": gc.base_node_type["intersection"], "poiId": "0"},
    17: {"name": "N11", "pos": (0, -2), "type": gc.base_node_type["normal"], "poiId": "0"},
    18: {"name": "N14", "pos": (6, 0), "type": gc.base_node_type["normal"], "poiId": "0"},
    19: {"name": "N15", "pos": (8, 0), "type": gc.base_node_type["normal"], "poiId": "0"},
    20: {"name": "WD", "pos": (8, -2), "type": gc.base_node_type["waiting-departure"], "poiId": "0"},
    21: {"name": "N17", "pos": (12, 0), "type": gc.base_node_type["normal"], "poiId": "0"},
    22: {"name": "N18", "pos": (12, -2), "type": gc.base_node_type["normal"], "poiId": "0"},
    23: {"name": "I5", "pos": (6, 2), "type": gc.base_node_type["intersection"], "poiId": "0"}
}

edge_dict3 = {
    # Krawędzie dojazdu do miejsca oczekiwania na dojazd do stanowiska
    1: {"startNode": get_id("I1", node_dict3), "endNode": get_id("N3", node_dict3),
        "type": gc.way_type["twoWay"], "isActive": True},
    2: {"startNode": get_id("N3", node_dict3), "endNode": get_id("N2", node_dict3),
        "type": gc.way_type["twoWay"], "isActive": True},
    3: {"startNode": get_id("N2", node_dict3), "endNode": get_id("N7", node_dict3),
        "type": gc.way_type["twoWay"], "isActive": True},
    4: {"startNode": get_id("N7", node_dict3), "endNode": get_id("N8", node_dict3),
        "type": gc.way_type["twoWay"], "isActive": True},
    5: {"startNode": get_id("N8", node_dict3), "endNode": get_id("I2", node_dict3),
        "type": gc.way_type["twoWay"], "isActive": True},
    6: {"startNode": get_id("I1", node_dict3), "endNode": get_id("N1", node_dict3),
        "type": gc.way_type["oneWay"], "isActive": True},
    7: {"startNode": get_id("N1", node_dict3), "endNode": get_id("N4", node_dict3),
        "type": gc.way_type["oneWay"], "isActive": True},
    8: {"startNode": get_id("N4", node_dict3), "endNode": get_id("W", node_dict3),
        "type": gc.way_type["oneWay"], "isActive": True},
    9: {"startNode": get_id("W", node_dict3), "endNode": get_id("N5", node_dict3),
        "type": gc.way_type["oneWay"], "isActive": True},
    10: {"startNode": get_id("N5", node_dict3), "endNode": get_id("N6", node_dict3),
         "type": gc.way_type["oneWay"], "isActive": True},
    11: {"startNode": get_id("N6", node_dict3), "endNode": get_id("POI1", node_dict3),
         "type": gc.way_type["oneWay"], "isActive": True},
    12: {"startNode": get_id("POI1", node_dict3), "endNode": get_id("N10", node_dict3),
         "type": gc.way_type["oneWay"], "isActive": True},
    13: {"startNode": get_id("N10", node_dict3), "endNode": get_id("N9", node_dict3),
         "type": gc.way_type["oneWay"], "isActive": True},
    14: {"startNode": get_id("N9", node_dict3), "endNode": get_id("D", node_dict3),
         "type": gc.way_type["oneWay"], "isActive": True},
    15: {"startNode": get_id("D", node_dict3), "endNode": get_id("N11", node_dict3),
         "type": gc.way_type["oneWay"], "isActive": True},
    16: {"startNode": get_id("N11", node_dict3), "endNode": get_id("I2", node_dict3),
         "type": gc.way_type["oneWay"], "isActive": True},
    17: {"startNode": get_id("I2", node_dict3), "endNode": get_id("I5", node_dict3),
         "type": gc.way_type["twoWay"], "isActive": True},
    18: {"startNode": get_id("I5", node_dict3), "endNode": get_id("N14", node_dict3),
         "type": gc.way_type["twoWay"], "isActive": True},
    19: {"startNode": get_id("N14", node_dict3), "endNode": get_id("N15", node_dict3),
         "type": gc.way_type["twoWay"], "isActive": True},
    20: {"startNode": get_id("N15", node_dict3), "endNode": get_id("WD", node_dict3),
         "type": gc.way_type["twoWay"], "isActive": True},
    21: {"startNode": get_id("WD", node_dict3), "endNode": get_id("N18", node_dict3),
         "type": gc.way_type["narrowTwoWay"], "isActive": True},
    22: {"startNode": get_id("N18", node_dict3), "endNode": get_id("N17", node_dict3),
         "type": gc.way_type["narrowTwoWay"], "isActive": True},
    23: {"startNode": get_id("N17", node_dict3), "endNode": get_id("POI2", node_dict3),
         "type": gc.way_type["narrowTwoWay"], "isActive": True},

}
graph3 = gc.SupervisorGraphCreator(node_dict3, edge_dict3, pois_raw3)


@pytest.mark.graph
def test_graph_corridor_generator_24a_normal_waiting_poi_before():
    start = 11
    end = 5
    # print(graph3.get_corridor_path((start, end)))
    # graph3.print_corridor((start, end))
    result = [(truncate(point[0]), truncate(point[1])) for point in graph3.get_corridor_path((start, end))]
    # print(result)
    assert result == [(-12, 1.3), (-12, 0), (-10, 0), (-10, -2)]


@pytest.mark.graph
def test_graph_corridor_generator_24b_normal_waiting_poi_after():
    start = 5
    end = 1
    # print(graph3.get_corridor_path((start, end)))
    # graph3.print_corridor((start, end))
    result = [(truncate(point[0]), truncate(point[1])) for point in graph3.get_corridor_path((start, end))]
    # print(result)
    assert result == [(-10, -2), (-8, -2), (-8, -4), (-6, -4)]


@pytest.mark.graph
def test_graph_corridor_generator_25a_normal_departure_poi():
    start = 2
    end = 6
    # print(graph3.get_corridor_path((start, end)))
    # graph3.print_corridor((start, end))
    result = [(truncate(point[0]), truncate(point[1])) for point in graph3.get_corridor_path((start, end))]
    # print(result)
    assert result == [(-6, -4), (-4, -4), (-4, -2), (-2, -2)]


@pytest.mark.graph
def test_graph_corridor_generator_25b_after_departure_poi():
    start = 6
    end = 12
    # print(graph3.get_corridor_path((start, end)))
    # graph3.print_corridor((start, end))
    result = [(truncate(point[0]), truncate(point[1])) for point in graph3.get_corridor_path((start, end))]
    # print(result)
    assert result == [(-2, -2), (0, -2), (0, 1.3)]


@pytest.mark.graph
def test_graph_corridor_generator_26a_wait_dep_before_poi():
    start = 17
    end = 18
    # print(graph3.get_corridor_path((start, end)))
    # graph3.print_corridor((start, end))
    result = [(truncate(point[0]), truncate(point[1])) for point in graph3.get_corridor_path((start, end))]
    # print(result)
    assert result == [(5.85, 1.3), (5.85, -0.15), (7.85, -0.15), (7.85, -1.3)]


@pytest.mark.graph
def test_graph_corridor_generator_26b_wait_dep_before_poi():
    start = 19
    end = 20
    # print(graph3.get_corridor_path((start, end)))
    # graph3.print_corridor((start, end))
    result = [(truncate(point[0]), truncate(point[1])) for point in graph3.get_corridor_path((start, end))]
    # print(result)
    assert result == [(8.15, -1.3), (8.15, 0.15), (6.15, 0.15), (6.15, 1.3)]


@pytest.mark.graph
def test_graph_corridor_generator_26c_intersection_wait_dep_poi():
    start = 18
    end = 19
    # print(graph3.get_corridor_path((start, end)))
    # graph3.print_corridor((start, end))
    result = [(truncate(point[0]), truncate(point[1])) for point in graph3.get_corridor_path((start, end))]
    # print(result)
    assert result == [(7.85, -1.3), (8.15, -1.3)]


@pytest.mark.graph
def test_graph_corridor_generator_26d_intersection_wait_dep_poi():
    start = 18
    end = 21
    # print(graph3.get_corridor_path((start, end)))
    # graph3.print_corridor((start, end))
    result = [(truncate(point[0]), truncate(point[1])) for point in graph3.get_corridor_path((start, end))]
    # print(result)
    assert result == [(7.85, -1.3), (7.85, -1.85), (8.15, -2.0), (8.7, -2.0)]


@pytest.mark.graph
def test_graph_corridor_generator_26e_intersection_wait_dep_poi():
    start = 22
    end = 19
    # print(graph3.get_corridor_path((start, end)))
    # graph3.print_corridor((start, end))
    result = [(truncate(point[0]), truncate(point[1])) for point in graph3.get_corridor_path((start, end))]
    # print(result)
    assert result == [(8.7, -2.0), (8.15, -2.0), (8.15, -1.85), (8.15, -1.3)]


@pytest.mark.graph
def test_graph_corridor_generator_26f_intersection_wait_dep_poi():
    start = 22
    end = 21
    # print(graph3.get_corridor_path((start, end)))
    # graph3.print_corridor((start, end))
    result = [(truncate(point[0]), truncate(point[1])) for point in graph3.get_corridor_path((start, end))]
    # print(result)
    assert result == [(8.7, -2.0), (8.7, -2.0)]


@pytest.mark.graph
def test_graph_corridor_generator_26g_intersection_after_wait_dep_poi():
    start = 21
    end = 3
    # print(graph3.get_corridor_path((start, end)))
    # graph3.print_corridor((start, end))
    result = [(truncate(point[0]), truncate(point[1])) for point in graph3.get_corridor_path((start, end))]
    # print(result)
    assert result == [(8.7, -2), (12, -2), (12, 0), (14, 0)]


@pytest.mark.graph
def test_graph_corridor_generator_26h_intersection_after_wait_dep_poi():
    start = 4
    end = 22
    # print(graph3.get_corridor_path((start, end)))
    # graph3.print_corridor((start, end))
    result = [(truncate(point[0]), truncate(point[1])) for point in graph3.get_corridor_path((start, end))]
    # print(result)
    assert result == [(14, 0), (12, 0), (12, -2), (8.7, -2)]
