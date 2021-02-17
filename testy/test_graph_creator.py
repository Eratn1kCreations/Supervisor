# -*- coding: utf-8 -*-
import pytest
from test_data import *
import graph_creator as gc
import math

gc.OFFLINE_TEST = False
gc.ROBOT_CORRIDOR_WIDTH = 0.3
gc.ROBOT_LENGTH = 0.4
gc.MAIN_CORRIDOR_WIDTH = 0.3
gc.WAITING_STOP_DIST_TO_INTERSECTION = gc.ROBOT_LENGTH / 2 + gc.MAIN_CORRIDOR_WIDTH


def print_graph_data(graph):
    """
    graph (SupervisorGraphCreator)
    """
    graph.print_graph((30, 10))
    print("  {:<6} {:<3} {:<10} {:<7} {:<4} {:<8} {:<4} {:<15} {:<15}".format("edge", "id", "maxRobots",
                                                                              "weight", "beh", "groupId",
                                                                              "way", "sourceEdges", "sourceNodes",
                                                                              "timeAdded", "behaviours"))
    for edge in graph.graph.edges(data=True):
        edge_data = edge[2]
        if "maxRobots" not in edge_data:
            edge_data["maxRobots"] = None
        if "wayType" not in edge_data:
            edge_data["wayType"] = None
        print("{:<7} {:<8} {:<8} {:<6} {:<6} {:<6} {:<3} {:<15} {:<15}".format(str(edge[0]) + "," + str(edge[1]),
                                                                               str(edge_data["id"]),
                                                                               str(edge_data["maxRobots"]),
                                                                               str(edge_data["weight"]),
                                                                               str(edge_data["behaviour"]),
                                                                               str(edge_data["edgeGroupId"]),
                                                                               str(edge_data["wayType"]),
                                                                               str(edge_data["sourceEdges"]),
                                                                               str(edge_data["sourceNodes"])))


def get_expected_nodes(nodes_raw, edges_raw):
    nodes_count = len([node for node in nodes_raw.values()
                       if node["type"]["nodeSection"] == gc.base_node_section_type["noChanges"]])
    dock_wait_undock_nodes = len([node for node in nodes_raw.values()
                                  if node["type"]["nodeSection"] == gc.base_node_section_type["dockWaitUndock"]])
    nodes_count += dock_wait_undock_nodes * 4
    wait_poi_nodes = len([node for node in nodes_raw.values()
                          if node["type"]["nodeSection"] == gc.base_node_section_type["waitPOI"]])
    nodes_count += wait_poi_nodes * 2
    intersection_nodes = [i for i in nodes_raw
                          if nodes_raw[i]["type"]["nodeSection"] == gc.base_node_section_type["intersection"]]
    for node in intersection_nodes:
        connected_edges_two_way = len([edge for edge in edges_raw.values() if edge["type"] != gc.way_type["oneWay"]
                                       and node in [edge["startNode"], edge["endNode"]]])
        connected_edges_one_way = len([edge for edge in edges_raw.values() if edge["type"] == gc.way_type["oneWay"]
                                       and node in [edge["startNode"], edge["endNode"]]])

        # print(node, connected_edges_two_way, connected_edges_one_way, intersection_edges)
        nodes_count += connected_edges_two_way * 2 + connected_edges_one_way
    return nodes_count


def get_expected_edges_intersections_and_pois(nodes_raw, edges_raw):
    edges_count = 0
    dock_wait_undock_nodes = len([node for node in nodes_raw.values()
                                  if node["type"]["nodeSection"] == gc.base_node_section_type["dockWaitUndock"]])
    edges_count += dock_wait_undock_nodes * 4
    wait_poi_nodes = len([node for node in nodes_raw.values()
                          if node["type"]["nodeSection"] == gc.base_node_section_type["waitPOI"]])
    edges_count += wait_poi_nodes * 2
    intersection_nodes = [i for i in nodes_raw
                          if nodes_raw[i]["type"]["nodeSection"] == gc.base_node_section_type["intersection"]]
    # print("intersection_nodes", intersection_nodes, "count", edges_count)
    for node in intersection_nodes:
        edges_two_way = len([edge for edge in edges_raw.values() if edge["type"] != gc.way_type["oneWay"]
                             and node in [edge["startNode"], edge["endNode"]]])
        edges_one_way = len([edge for edge in edges_raw.values() if edge["type"] == gc.way_type["oneWay"]
                             and node in [edge["startNode"], edge["endNode"]]])

        # intersection_edges = edges_two_way * edges_two_way + edges_two_way * edges_one_way
        # print(node, connected_edges_two_way, connected_edges_one_way, intersection_edges)
        edges_count += edges_two_way * edges_two_way + edges_two_way * edges_one_way

    return edges_count


def check_graph_position(expected_pose, graph_nodes):
    expected_error_position = 0.05  # suma bledow w wyznaczeniu pozycji dla wszystkich wezlow
    assigned_nodes = {i: [] for i in expected_pose.keys()}
    for node in graph_nodes:
        node_pose = node[1]["pos"]
        shortest_dist = None
        received_key = None
        for pose in assigned_nodes.keys():
            distance = math.sqrt(math.pow(pose[0] - node_pose[0], 2) + math.pow(pose[1] - node_pose[1], 2))
            if shortest_dist is None:
                shortest_dist = distance
                received_key = pose
            elif shortest_dist > distance:
                shortest_dist = distance
                received_key = pose
        if received_key is not None:
            assigned_nodes[received_key] = assigned_nodes[received_key] + [node[0]]

    proper_assigned = True
    for key in expected_pose.keys():
        if expected_pose[key] != len(assigned_nodes[key]):
            proper_assigned = False
    if not proper_assigned:
        return False

    distance = 0
    for key in expected_pose.keys():
        A = key
        for node_id in assigned_nodes[key]:
            B = graph_nodes[node_id]["pos"]
            distance += math.sqrt(math.pow(A[0] - B[0], 2) + math.pow(A[1] - B[1], 2))
    return distance <= expected_error_position


@pytest.mark.graph_creator_valid_data
def test_graph():
    # skrzyzowanie - skrzyzowanie (co najmniej 3 drogi)
    nodes = {
        "1": {'name': 'D1', 'pos': (5, 5), 'type': gc.base_node_type["intersection"], "poiId": "0"},
        "2": {'name': 'D2', 'pos': (10, 5), 'type': gc.base_node_type["intersection"], "poiId": "0"},
        "3": {'name': 'D3', 'pos': (15, 5), 'type': gc.base_node_type["intersection"], "poiId": "0"},
        "4": {'name': 'D4', 'pos': (10, 8), 'type': gc.base_node_type["intersection"], "poiId": "0"}
    }

    edges = {
        "1": {'startNode': "1", 'endNode': "2", 'type': gc.way_type["twoWay"], 'isActive': True},
        "2": {'startNode': "3", 'endNode': "2", 'type': gc.way_type["oneWay"], 'isActive': True},
        "3": {'startNode': "4", 'endNode': "2", 'type': gc.way_type["narrowTwoWay"], 'isActive': True},
    }

    graph = gc.SupervisorGraphCreator(nodes, edges, [])
    expected_pose = {
        (5 + gc.WAITING_STOP_DIST_TO_INTERSECTION, 5 + gc.MAIN_CORRIDOR_WIDTH / 2): 1,
        (5 + gc.WAITING_STOP_DIST_TO_INTERSECTION, 5 - gc.MAIN_CORRIDOR_WIDTH / 2): 1,
        (10 - gc.WAITING_STOP_DIST_TO_INTERSECTION, 5 + gc.MAIN_CORRIDOR_WIDTH / 2): 1,
        (10 - gc.WAITING_STOP_DIST_TO_INTERSECTION, 5 - gc.MAIN_CORRIDOR_WIDTH / 2): 1,
        (10, 5 + gc.WAITING_STOP_DIST_TO_INTERSECTION): 2,
        (10 + gc.WAITING_STOP_DIST_TO_INTERSECTION, 5): 1,
        (15 - gc.WAITING_STOP_DIST_TO_INTERSECTION, 5): 1,
        (10, 8 - gc.WAITING_STOP_DIST_TO_INTERSECTION): 2
    }
    # print(sorted(expected_pose))
    # print(sorted({node[1]["pos"] for node in graph.graph.nodes(data=True)}))
    # print("nodes", len(graph.graph.nodes), get_expected_nodes(nodes, edges))
    # print("edges", len(graph.graph.edges), get_expected_edges_intersections_and_pois(nodes, edges)+5)
    assert len(graph.graph.nodes) == get_expected_nodes(nodes, edges)
    assert len(graph.graph.edges) == get_expected_edges_intersections_and_pois(nodes, edges) + 5
    assert check_graph_position(expected_pose, graph.graph.nodes(data=True))
    # graph.print_graph()
    # print_graph_data(graph)


@pytest.mark.graph_creator_valid_data
def test_graph_2():
    # skrzyzowanie - skrzyzowanie (co najmniej 3 drogi)
    nodes = {
        "1": {'name': 'D1', 'pos': (5, 5), 'type': gc.base_node_type["intersection"], "poiId": "0"},
        "2": {'name': 'D2', 'pos': (10, 5), 'type': gc.base_node_type["intersection"], "poiId": "0"},
        "3": {'name': 'D3', 'pos': (15, 5), 'type': gc.base_node_type["intersection"], "poiId": "0"},
        "4": {'name': 'D4', 'pos': (10, 8), 'type': gc.base_node_type["intersection"], "poiId": "0"}
    }

    edges = {
        "1": {'startNode': "2", 'endNode': "1", 'type': gc.way_type["twoWay"], 'isActive': True},
        "2": {'startNode': "3", 'endNode': "2", 'type': gc.way_type["oneWay"], 'isActive': True},
        "3": {'startNode': "4", 'endNode': "2", 'type': gc.way_type["narrowTwoWay"], 'isActive': True},
    }

    graph = gc.SupervisorGraphCreator(nodes, edges, [])
    # graph.print_graph()
    expected_pose = {
        (5 + gc.WAITING_STOP_DIST_TO_INTERSECTION, 5 + gc.MAIN_CORRIDOR_WIDTH / 2): 1,
        (5 + gc.WAITING_STOP_DIST_TO_INTERSECTION, 5 - gc.MAIN_CORRIDOR_WIDTH / 2): 1,
        (10 - gc.WAITING_STOP_DIST_TO_INTERSECTION, 5 + gc.MAIN_CORRIDOR_WIDTH / 2): 1,
        (10 - gc.WAITING_STOP_DIST_TO_INTERSECTION, 5 - gc.MAIN_CORRIDOR_WIDTH / 2): 1,
        (10, 5 + gc.WAITING_STOP_DIST_TO_INTERSECTION): 2,
        (10 + gc.WAITING_STOP_DIST_TO_INTERSECTION, 5): 1,
        (15 - gc.WAITING_STOP_DIST_TO_INTERSECTION, 5): 1,
        (10, 8 - gc.WAITING_STOP_DIST_TO_INTERSECTION): 2
    }
    assert len(graph.graph.nodes) == get_expected_nodes(nodes, edges)
    assert len(graph.graph.edges) == get_expected_edges_intersections_and_pois(nodes, edges) + 5
    assert check_graph_position(expected_pose, graph.graph.nodes(data=True))
    # print_graph_data(graph)


@pytest.mark.graph_creator_valid_data
def test_graph_3():
    # skrzyzowanie - skrzyzowanie (co najmniej 3 drogi)
    nodes = {
        "1": {'name': 'D1', 'pos': (5, 5), 'type': gc.base_node_type["intersection"], "poiId": "0"},
        "2": {'name': 'D2', 'pos': (10, 5), 'type': gc.base_node_type["intersection"], "poiId": "0"},
        "3": {'name': 'D3', 'pos': (15, 5), 'type': gc.base_node_type["intersection"], "poiId": "0"},
        "4": {'name': 'D4', 'pos': (10, 8), 'type': gc.base_node_type["intersection"], "poiId": "0"}
    }

    edges = {
        "1": {'startNode': "1", 'endNode': "2", 'type': gc.way_type["twoWay"], 'isActive': True},
        "2": {'startNode': "2", 'endNode': "3", 'type': gc.way_type["oneWay"], 'isActive': True},
        "3": {'startNode': "4", 'endNode': "2", 'type': gc.way_type["narrowTwoWay"], 'isActive': True}
    }

    graph = gc.SupervisorGraphCreator(nodes, edges, [])
    # graph.print_graph()
    expected_pose = {
        (5 + gc.WAITING_STOP_DIST_TO_INTERSECTION, 5 + gc.MAIN_CORRIDOR_WIDTH / 2): 1,
        (5 + gc.WAITING_STOP_DIST_TO_INTERSECTION, 5 - gc.MAIN_CORRIDOR_WIDTH / 2): 1,
        (10 - gc.WAITING_STOP_DIST_TO_INTERSECTION, 5 + gc.MAIN_CORRIDOR_WIDTH / 2): 1,
        (10 - gc.WAITING_STOP_DIST_TO_INTERSECTION, 5 - gc.MAIN_CORRIDOR_WIDTH / 2): 1,
        (10, 5 + gc.WAITING_STOP_DIST_TO_INTERSECTION): 2,
        (10 + gc.WAITING_STOP_DIST_TO_INTERSECTION, 5): 1,
        (15 - gc.WAITING_STOP_DIST_TO_INTERSECTION, 5): 1,
        (10, 8 - gc.WAITING_STOP_DIST_TO_INTERSECTION): 2
    }
    assert len(graph.graph.nodes) == get_expected_nodes(nodes, edges)
    assert len(graph.graph.edges) == get_expected_edges_intersections_and_pois(nodes, edges) + 5
    assert check_graph_position(expected_pose, graph.graph.nodes(data=True))
    # print_graph_data(graph)


@pytest.mark.graph_creator_valid_data
def test_graph_4():
    # skrzyzowanie - skrzyzowanie (co najmniej 3 drogi)
    nodes = {
        "1": {'name': 'D1', 'pos': (5, 5), 'type': gc.base_node_type["intersection"], "poiId": "0"},
        "2": {'name': 'D2', 'pos': (10, 5), 'type': gc.base_node_type["intersection"], "poiId": "0"},
        "3": {'name': 'D3', 'pos': (15, 5), 'type': gc.base_node_type["intersection"], "poiId": "0"},
        "4": {'name': 'D4', 'pos': (10, 8), 'type': gc.base_node_type["intersection"], "poiId": "0"}
    }

    edges = {
        "1": {'startNode': "1", 'endNode': "2", 'type': gc.way_type["twoWay"], 'isActive': True},
        "2": {'startNode': "3", 'endNode': "2", 'type': gc.way_type["oneWay"], 'isActive': True},
        "3": {'startNode': "2", 'endNode': "4", 'type': gc.way_type["narrowTwoWay"], 'isActive': True},
    }

    graph = gc.SupervisorGraphCreator(nodes, edges, [])
    # graph.print_graph()
    expected_pose = {
        (5 + gc.WAITING_STOP_DIST_TO_INTERSECTION, 5 + gc.MAIN_CORRIDOR_WIDTH / 2): 1,
        (5 + gc.WAITING_STOP_DIST_TO_INTERSECTION, 5 - gc.MAIN_CORRIDOR_WIDTH / 2): 1,
        (10 - gc.WAITING_STOP_DIST_TO_INTERSECTION, 5 + gc.MAIN_CORRIDOR_WIDTH / 2): 1,
        (10 - gc.WAITING_STOP_DIST_TO_INTERSECTION, 5 - gc.MAIN_CORRIDOR_WIDTH / 2): 1,
        (10, 5 + gc.WAITING_STOP_DIST_TO_INTERSECTION): 2,
        (10 + gc.WAITING_STOP_DIST_TO_INTERSECTION, 5): 1,
        (15 - gc.WAITING_STOP_DIST_TO_INTERSECTION, 5): 1,
        (10, 8 - gc.WAITING_STOP_DIST_TO_INTERSECTION): 2
    }
    assert len(graph.graph.nodes) == get_expected_nodes(nodes, edges)
    assert len(graph.graph.edges) == get_expected_edges_intersections_and_pois(nodes, edges) + 5
    assert check_graph_position(expected_pose, graph.graph.nodes(data=True))
    # print_graph_data(graph)


@pytest.mark.graph_creator_valid_data
def test_graph_5():
    # skrzyzowanie - wezel normalny - skrzyzowanie
    nodes = {
        "1": {'name': 'D1', 'pos': (5, 5), 'type': gc.base_node_type["intersection"], "poiId": "0"},
        "2": {'name': 'D2', 'pos': (10, 5), 'type': gc.base_node_type["normal"], "poiId": "0"},
        "3": {'name': 'D3', 'pos': (15, 5), 'type': gc.base_node_type["intersection"], "poiId": "0"},
    }

    edges = {
        "1": {'startNode': "1", 'endNode': "2", 'type': gc.way_type["twoWay"], 'isActive': True},
        "2": {'startNode': "2", 'endNode': "3", 'type': gc.way_type["twoWay"], 'isActive': True},
    }

    graph = gc.SupervisorGraphCreator(nodes, edges, [])
    # graph.print_graph()
    expected_pose = {
        (5 + gc.WAITING_STOP_DIST_TO_INTERSECTION, 5 + gc.MAIN_CORRIDOR_WIDTH / 2): 1,
        (5 + gc.WAITING_STOP_DIST_TO_INTERSECTION, 5 - gc.MAIN_CORRIDOR_WIDTH / 2): 1,
        (15 - gc.WAITING_STOP_DIST_TO_INTERSECTION, 5 + gc.MAIN_CORRIDOR_WIDTH / 2): 1,
        (15 - gc.WAITING_STOP_DIST_TO_INTERSECTION, 5 - gc.MAIN_CORRIDOR_WIDTH / 2): 1,
    }
    assert len(graph.graph.nodes) == get_expected_nodes(nodes, edges)
    assert len(graph.graph.edges) == get_expected_edges_intersections_and_pois(nodes, edges) + 2
    assert check_graph_position(expected_pose, graph.graph.nodes(data=True))
    # print_graph_data(graph)


@pytest.mark.graph_creator_valid_data
def test_graph_6():
    # skrzyzowanie - wezel normalny - skrzyzowanie
    nodes = {
        "1": {'name': 'D1', 'pos': (5, 5), 'type': gc.base_node_type["intersection"], "poiId": "0"},
        "2": {'name': 'D2', 'pos': (7, 5), 'type': gc.base_node_type["normal"], "poiId": "0"},
        "3": {'name': 'D2', 'pos': (8, 5), 'type': gc.base_node_type["normal"], "poiId": "0"},
        "4": {'name': 'D3', 'pos': (15, 5), 'type': gc.base_node_type["intersection"], "poiId": "0"}
    }

    edges = {
        "1": {'startNode': "1", 'endNode': "2", 'type': gc.way_type["twoWay"], 'isActive': True},
        "2": {'startNode': "2", 'endNode': "3", 'type': gc.way_type["twoWay"], 'isActive': True},
        "3": {'startNode': "3", 'endNode': "4", 'type': gc.way_type["twoWay"], 'isActive': True},
    }

    graph = gc.SupervisorGraphCreator(nodes, edges, [])
    # graph.print_graph()
    expected_pose = {
        (5 + gc.WAITING_STOP_DIST_TO_INTERSECTION, 5 + gc.MAIN_CORRIDOR_WIDTH / 2): 1,
        (5 + gc.WAITING_STOP_DIST_TO_INTERSECTION, 5 - gc.MAIN_CORRIDOR_WIDTH / 2): 1,
        (15 - gc.WAITING_STOP_DIST_TO_INTERSECTION, 5 + gc.MAIN_CORRIDOR_WIDTH / 2): 1,
        (15 - gc.WAITING_STOP_DIST_TO_INTERSECTION, 5 - gc.MAIN_CORRIDOR_WIDTH / 2): 1,
    }
    assert len(graph.graph.nodes) == get_expected_nodes(nodes, edges)
    assert len(graph.graph.edges) == get_expected_edges_intersections_and_pois(nodes, edges) + 2
    assert check_graph_position(expected_pose, graph.graph.nodes(data=True))
    # print_graph_data(graph)


@pytest.mark.graph_creator_valid_data
def test_graph_7():
    # skrzyzowanie - wezel normalny - skrzyzowanie
    nodes = {
        "1": {'name': 'D1', 'pos': (5, 5), 'type': gc.base_node_type["intersection"], "poiId": "0"},
        "2": {'name': 'D2', 'pos': (10, 5), 'type': gc.base_node_type["normal"], "poiId": "0"},
        "3": {'name': 'D3', 'pos': (15, 5), 'type': gc.base_node_type["intersection"], "poiId": "0"},
    }

    edges = {
        "1": {'startNode': "1", 'endNode': "2", 'type': gc.way_type["twoWay"], 'isActive': True},
        "2": {'startNode': "2", 'endNode': "3", 'type': gc.way_type["twoWay"], 'isActive': True},
    }

    graph = gc.SupervisorGraphCreator(nodes, edges, [])
    # graph.print_graph()
    expected_pose = {
        (5 + gc.WAITING_STOP_DIST_TO_INTERSECTION, 5 + gc.MAIN_CORRIDOR_WIDTH / 2): 1,
        (5 + gc.WAITING_STOP_DIST_TO_INTERSECTION, 5 - gc.MAIN_CORRIDOR_WIDTH / 2): 1,
        (15 - gc.WAITING_STOP_DIST_TO_INTERSECTION, 5 + gc.MAIN_CORRIDOR_WIDTH / 2): 1,
        (15 - gc.WAITING_STOP_DIST_TO_INTERSECTION, 5 - gc.MAIN_CORRIDOR_WIDTH / 2): 1,
    }
    assert len(graph.graph.nodes) == get_expected_nodes(nodes, edges)
    assert len(graph.graph.edges) == get_expected_edges_intersections_and_pois(nodes, edges) + 2
    assert check_graph_position(expected_pose, graph.graph.nodes(data=True))
    # print_graph_data(graph)


@pytest.mark.graph_creator_valid_data
def test_graph_8():
    # skrzyzowanie - wezel normalny - skrzyzowanie
    nodes = {
        "1": {'name': 'D1', 'pos': (5, 5), 'type': gc.base_node_type["intersection"], "poiId": "0"},
        "2": {'name': 'D2', 'pos': (10, 5), 'type': gc.base_node_type["normal"], "poiId": "0"},
        "3": {'name': 'D3', 'pos': (15, 5), 'type': gc.base_node_type["intersection"], "poiId": "0"},
    }

    edges = {
        "1": {'startNode': "1", 'endNode': "2", 'type': gc.way_type["narrowTwoWay"], 'isActive': True},
        "2": {'startNode': "3", 'endNode': "2", 'type': gc.way_type["narrowTwoWay"], 'isActive': True},
    }

    graph = gc.SupervisorGraphCreator(nodes, edges, [])
    # graph.print_graph()
    expected_pose = {
        (5 + gc.WAITING_STOP_DIST_TO_INTERSECTION, 5): 2,
        (15 - gc.WAITING_STOP_DIST_TO_INTERSECTION, 5): 2,
    }
    assert len(graph.graph.nodes) == get_expected_nodes(nodes, edges)
    assert len(graph.graph.edges) == get_expected_edges_intersections_and_pois(nodes, edges) + 2
    assert check_graph_position(expected_pose, graph.graph.nodes(data=True))
    # print_graph_data(graph)


@pytest.mark.graph_creator_valid_data
def test_graph_9():
    # skrzyzowanie - wezel normalny - skrzyzowanie
    nodes = {
        "1": {'name': 'D1', 'pos': (5, 5), 'type': gc.base_node_type["intersection"], "poiId": "0"},
        "2": {'name': 'D2', 'pos': (10, 5), 'type': gc.base_node_type["normal"], "poiId": "0"},
        "3": {'name': 'D3', 'pos': (15, 5), 'type': gc.base_node_type["intersection"], "poiId": "0"}
    }

    edges = {
        "1": {'startNode': "1", 'endNode': "2", 'type': gc.way_type["narrowTwoWay"], 'isActive': True},
        "2": {'startNode': "2", 'endNode': "3", 'type': gc.way_type["narrowTwoWay"], 'isActive': True},
    }

    graph = gc.SupervisorGraphCreator(nodes, edges, [])
    # graph.print_graph()
    expected_pose = {
        (5 + gc.WAITING_STOP_DIST_TO_INTERSECTION, 5): 2,
        (15 - gc.WAITING_STOP_DIST_TO_INTERSECTION, 5): 2,
    }
    assert len(graph.graph.nodes) == get_expected_nodes(nodes, edges)
    assert len(graph.graph.edges) == get_expected_edges_intersections_and_pois(nodes, edges) + 2
    assert check_graph_position(expected_pose, graph.graph.nodes(data=True))
    # print_graph_data(graph)


@pytest.mark.graph_creator_valid_data
def test_graph_10():
    # skrzyzowanie - wezel normalny - skrzyzowanie
    nodes = {
        "1": {'name': 'D1', 'pos': (5, 5), 'type': gc.base_node_type["intersection"], "poiId": "0"},
        "2": {'name': 'D2', 'pos': (10, 5), 'type': gc.base_node_type["normal"], "poiId": "0"},
        "3": {'name': 'D3', 'pos': (15, 5), 'type': gc.base_node_type["intersection"], "poiId": "0"},
    }

    edges = {
        "1": {'startNode': "1", 'endNode': "2", 'type': gc.way_type["oneWay"], 'isActive': True},
        "2": {'startNode': "2", 'endNode': "3", 'type': gc.way_type["oneWay"], 'isActive': True},

    }

    graph = gc.SupervisorGraphCreator(nodes, edges, [])
    # graph.print_graph()
    expected_pose = {
        (5 + gc.WAITING_STOP_DIST_TO_INTERSECTION, 5): 1,
        (15 - gc.WAITING_STOP_DIST_TO_INTERSECTION, 5): 1,
    }
    assert len(graph.graph.nodes) == get_expected_nodes(nodes, edges)
    assert len(graph.graph.edges) == get_expected_edges_intersections_and_pois(nodes, edges) + 1
    assert check_graph_position(expected_pose, graph.graph.nodes(data=True))
    # print_graph_data(graph)


@pytest.mark.graph_creator_valid_data
def test_graph_11():
    # pomiedzy stanowiskami z dokowaniem (intersection - waiting - poi - departure - intersection) - one way
    nodes = {
        "1": {'name': 'D2', 'pos': (1, 5), 'type': gc.base_node_type["intersection"], "poiId": "0"},
        "2": {'name': 'D2', 'pos': (3, 5), 'type': gc.base_node_type["waiting"], "poiId": "0"},
        "3": {'name': 'D2', 'pos': (6, 5), 'type': gc.base_node_type["charger"], "poiId": "19"},
        "4": {'name': 'D2', 'pos': (9, 5), 'type': gc.base_node_type["departure"], "poiId": "0"},
        "5": {'name': 'D2', 'pos': (12, 5), 'type': gc.base_node_type["intersection"], "poiId": "0"},
    }

    edges = {
        "1": {'startNode': "1", 'endNode': "2", 'type': gc.way_type["oneWay"], 'isActive': True},
        "2": {'startNode': "2", 'endNode': "3", 'type': gc.way_type["oneWay"], 'isActive': True},
        "3": {'startNode': "3", 'endNode': "4", 'type': gc.way_type["oneWay"], 'isActive': True},
        "4": {'startNode': "4", 'endNode': "5", 'type': gc.way_type["oneWay"], 'isActive': True}
    }
    pois_raw = [
        {"id": "19", "pose": (6, 5), "type": gc.base_node_type["charger"]}
    ]
    graph = gc.SupervisorGraphCreator(nodes, edges, pois_raw)
    # graph.print_graph()
    expected_pose = {
        (1 + gc.WAITING_STOP_DIST_TO_INTERSECTION, 5): 1,
        (3, 5): 1,
        (6, 5): 4,
        (9, 5): 1,
        (12 - gc.WAITING_STOP_DIST_TO_INTERSECTION, 5): 1
    }
    assert len(graph.graph.nodes) == get_expected_nodes(nodes, edges)
    assert len(graph.graph.edges) == get_expected_edges_intersections_and_pois(nodes, edges) + 4
    assert check_graph_position(expected_pose, graph.graph.nodes(data=True))
    # print_graph_data(graph)


@pytest.mark.graph_creator_valid_data
def test_graph_12():
    # pomiedzy stanowiskami z dokowaniem (intersection - waiting - poi - departure - intersection) - one way
    nodes = {
        "1": {'name': 'D2', 'pos': (1, 5), 'type': gc.base_node_type["intersection"], "poiId": "0"},
        "2": {'name': 'D2', 'pos': (3, 5), 'type': gc.base_node_type["waiting"], "poiId": "0"},
        "3": {'name': 'D2', 'pos': (6, 5), 'type': gc.base_node_type["load-dock"], "poiId": "1"},
        "4": {'name': 'D2', 'pos': (9, 5), 'type': gc.base_node_type["departure"], "poiId": "0"},
        "5": {'name': 'D2', 'pos': (12, 5), 'type': gc.base_node_type["intersection"], "poiId": "0"},
    }

    edges = {
        "1": {'startNode': "1", 'endNode': "2", 'type': gc.way_type["oneWay"], 'isActive': True},
        "2": {'startNode': "2", 'endNode': "3", 'type': gc.way_type["oneWay"], 'isActive': True},
        "3": {'startNode': "3", 'endNode': "4", 'type': gc.way_type["oneWay"], 'isActive': True},
        "4": {'startNode': "4", 'endNode': "5", 'type': gc.way_type["oneWay"], 'isActive': True}
    }

    pois_raw = [
        {"id": "1", "pose": (6, 5), "type": gc.base_node_type["load-dock"]}
    ]
    graph = gc.SupervisorGraphCreator(nodes, edges, pois_raw)
    # graph.print_graph()
    expected_pose = {
        (1 + gc.WAITING_STOP_DIST_TO_INTERSECTION, 5): 1,
        (3, 5): 1,
        (6, 5): 4,
        (9, 5): 1,
        (12 - gc.WAITING_STOP_DIST_TO_INTERSECTION, 5): 1
    }
    assert len(graph.graph.nodes) == get_expected_nodes(nodes, edges)
    assert len(graph.graph.edges) == get_expected_edges_intersections_and_pois(nodes, edges) + 4
    assert check_graph_position(expected_pose, graph.graph.nodes(data=True))
    # print_graph_data(graph)


@pytest.mark.graph_creator_valid_data
def test_graph_13():
    # pomiedzy stanowiskami z dokowaniem (intersection - waiting - poi - departure - intersection) - one way
    nodes = {
        "1": {'name': 'D2', 'pos': (1, 5), 'type': gc.base_node_type["intersection"], "poiId": "0"},
        "2": {'name': 'D2', 'pos': (3, 5), 'type': gc.base_node_type["waiting"], "poiId": "0"},
        "3": {'name': 'D2', 'pos': (6, 5), 'type': gc.base_node_type["unload-dock"], "poiId": "10"},
        "4": {'name': 'D2', 'pos': (9, 5), 'type': gc.base_node_type["departure"], "poiId": "0"},
        "5": {'name': 'D2', 'pos': (12, 5), 'type': gc.base_node_type["intersection"], "poiId": "0"},
    }

    edges = {
        "1": {'startNode': "1", 'endNode': "2", 'type': gc.way_type["oneWay"], 'isActive': True},
        "2": {'startNode': "2", 'endNode': "3", 'type': gc.way_type["oneWay"], 'isActive': True},
        "3": {'startNode': "3", 'endNode': "4", 'type': gc.way_type["oneWay"], 'isActive': True},
        "4": {'startNode': "4", 'endNode': "5", 'type': gc.way_type["oneWay"], 'isActive': True}
    }

    pois_raw = [
        {"id": "10", "pose": (6, 5), "type": gc.base_node_type["unload-dock"]}
    ]
    graph = gc.SupervisorGraphCreator(nodes, edges, pois_raw)
    # graph.print_graph()
    expected_pose = {
        (1 + gc.WAITING_STOP_DIST_TO_INTERSECTION, 5): 1,
        (3, 5): 1,
        (6, 5): 4,
        (9, 5): 1,
        (12 - gc.WAITING_STOP_DIST_TO_INTERSECTION, 5): 1
    }
    assert len(graph.graph.nodes) == get_expected_nodes(nodes, edges)
    assert len(graph.graph.edges) == get_expected_edges_intersections_and_pois(nodes, edges) + 4
    assert check_graph_position(expected_pose, graph.graph.nodes(data=True))
    # print_graph_data(graph)


@pytest.mark.graph_creator_valid_data
def test_graph_14():
    # pomiedzy stanowiskami z dokowaniem (intersection - waiting - poi - departure - intersection) - one way
    nodes = {
        "1": {'name': 'D2', 'pos': (1, 5), 'type': gc.base_node_type["intersection"], "poiId": "0"},
        "2": {'name': 'D2', 'pos': (3, 5), 'type': gc.base_node_type["waiting"], "poiId": "0"},
        "3": {'name': 'D2', 'pos': (6, 5), 'type': gc.base_node_type["load-unload-dock"], "poiId": "10"},
        "4": {'name': 'D2', 'pos': (9, 5), 'type': gc.base_node_type["departure"], "poiId": "0"},
        "5": {'name': 'D2', 'pos': (12, 5), 'type': gc.base_node_type["intersection"], "poiId": "0"},
    }

    edges = {
        "1": {'startNode': "1", 'endNode': "2", 'type': gc.way_type["oneWay"], 'isActive': True},
        "2": {'startNode': "2", 'endNode': "3", 'type': gc.way_type["oneWay"], 'isActive': True},
        "3": {'startNode': "3", 'endNode': "4", 'type': gc.way_type["oneWay"], 'isActive': True},
        "4": {'startNode': "4", 'endNode': "5", 'type': gc.way_type["oneWay"], 'isActive': True}
    }

    pois_raw = [
        {"id": "10", "pose": (6, 5), "type": gc.base_node_type["load-unload-dock"]}
    ]
    graph = gc.SupervisorGraphCreator(nodes, edges, pois_raw)
    # graph.print_graph()
    expected_pose = {
        (1 + gc.WAITING_STOP_DIST_TO_INTERSECTION, 5): 1,
        (3, 5): 1,
        (6, 5): 4,
        (9, 5): 1,
        (12 - gc.WAITING_STOP_DIST_TO_INTERSECTION, 5): 1
    }
    assert len(graph.graph.nodes) == get_expected_nodes(nodes, edges)
    assert len(graph.graph.edges) == get_expected_edges_intersections_and_pois(nodes, edges) + 4
    assert check_graph_position(expected_pose, graph.graph.nodes(data=True))
    # print_graph_data(graph)


@pytest.mark.graph_creator_valid_data
def test_graph_15():
    # pomiedzy stanowiskami z dokowaniem (intersection - waiting - poi - departure - intersection) - one way
    nodes = {
        "1": {'name': 'D2', 'pos': (1, 5), 'type': gc.base_node_type["intersection"], "poiId": "0"},
        "2": {'name': 'D2', 'pos': (1, 5), 'type': gc.base_node_type["normal"], "poiId": "0"},
        "3": {'name': 'D2', 'pos': (3, 5), 'type': gc.base_node_type["waiting"], "poiId": "0"},
        "4": {'name': 'D2', 'pos': (6, 5), 'type': gc.base_node_type["load-unload-dock"], "poiId": "10"},
        "5": {'name': 'D2', 'pos': (9, 5), 'type': gc.base_node_type["departure"], "poiId": "0"},
        "6": {'name': 'D2', 'pos': (12, 5), 'type': gc.base_node_type["intersection"], "poiId": "0"},
    }

    edges = {
        "1": {'startNode': "1", 'endNode': "2", 'type': gc.way_type["oneWay"], 'isActive': True},
        "2": {'startNode': "2", 'endNode': "3", 'type': gc.way_type["oneWay"], 'isActive': True},
        "3": {'startNode': "3", 'endNode': "4", 'type': gc.way_type["oneWay"], 'isActive': True},
        "4": {'startNode': "4", 'endNode': "5", 'type': gc.way_type["oneWay"], 'isActive': True},
        "5": {'startNode': "5", 'endNode': "6", 'type': gc.way_type["oneWay"], 'isActive': True}
    }

    pois_raw = [
        {"id": "10", "pose": (6, 5), "type": gc.base_node_type["load-unload-dock"]}
    ]
    graph = gc.SupervisorGraphCreator(nodes, edges, pois_raw)
    # graph.print_graph()
    expected_pose = {
        (1 + gc.WAITING_STOP_DIST_TO_INTERSECTION, 5): 1,
        (3, 5): 1,
        (6, 5): 4,
        (9, 5): 1,
        (12 - gc.WAITING_STOP_DIST_TO_INTERSECTION, 5): 1
    }
    assert len(graph.graph.nodes) == get_expected_nodes(nodes, edges)
    assert len(graph.graph.edges) == get_expected_edges_intersections_and_pois(nodes, edges) + 4
    assert check_graph_position(expected_pose, graph.graph.nodes(data=True))
    # print_graph_data(graph)


@pytest.mark.graph_creator_valid_data
def test_graph_16():
    # pomiedzy stanowiskami z dokowaniem (intersection - waiting - poi - departure - intersection) - one way
    nodes = {
        "1": {'name': 'D2', 'pos': (1, 5), 'type': gc.base_node_type["intersection"], "poiId": "0"},
        "2": {'name': 'D2', 'pos': (2, 5), 'type': gc.base_node_type["waiting"], "poiId": "0"},
        "3": {'name': 'D2', 'pos': (3, 5), 'type': gc.base_node_type["normal"], "poiId": "0"},
        "4": {'name': 'D2', 'pos': (6, 5), 'type': gc.base_node_type["load-unload-dock"], "poiId": "10"},
        "5": {'name': 'D2', 'pos': (9, 5), 'type': gc.base_node_type["departure"], "poiId": "0"},
        "6": {'name': 'D2', 'pos': (12, 5), 'type': gc.base_node_type["intersection"], "poiId": "0"},
    }

    edges = {
        "1": {'startNode': "1", 'endNode': "2", 'type': gc.way_type["oneWay"], 'isActive': True},
        "2": {'startNode': "2", 'endNode': "3", 'type': gc.way_type["oneWay"], 'isActive': True},
        "3": {'startNode': "3", 'endNode': "4", 'type': gc.way_type["oneWay"], 'isActive': True},
        "4": {'startNode': "4", 'endNode': "5", 'type': gc.way_type["oneWay"], 'isActive': True},
        "5": {'startNode': "5", 'endNode': "6", 'type': gc.way_type["oneWay"], 'isActive': True}
    }

    pois_raw = [
        {"id": "10", "pose": (6, 5), "type": gc.base_node_type["load-unload-dock"]}
    ]
    graph = gc.SupervisorGraphCreator(nodes, edges, pois_raw)
    # graph.print_graph()
    expected_pose = {
        (1 + gc.WAITING_STOP_DIST_TO_INTERSECTION, 5): 1,
        (2, 5): 1,
        (6, 5): 4,
        (9, 5): 1,
        (12 - gc.WAITING_STOP_DIST_TO_INTERSECTION, 5): 1
    }
    assert len(graph.graph.nodes) == get_expected_nodes(nodes, edges)
    assert len(graph.graph.edges) == get_expected_edges_intersections_and_pois(nodes, edges) + 4
    assert check_graph_position(expected_pose, graph.graph.nodes(data=True))
    # print_graph_data(graph)


@pytest.mark.graph_creator_valid_data
def test_graph_17():
    # pomiedzy stanowiskami z dokowaniem (intersection - waiting - poi - departure - intersection) - one way
    nodes = {
        "1": {'name': 'D2', 'pos': (1, 5), 'type': gc.base_node_type["intersection"], "poiId": "0"},
        "2": {'name': 'D2', 'pos': (3, 5), 'type': gc.base_node_type["waiting"], "poiId": "0"},
        "3": {'name': 'D2', 'pos': (5, 5), 'type': gc.base_node_type["load-unload-dock"], "poiId": "10"},
        "4": {'name': 'D2', 'pos': (7, 5), 'type': gc.base_node_type["normal"], "poiId": "0"},
        "5": {'name': 'D2', 'pos': (9, 5), 'type': gc.base_node_type["departure"], "poiId": "0"},
        "6": {'name': 'D2', 'pos': (12, 5), 'type': gc.base_node_type["intersection"], "poiId": "0"},
    }

    edges = {
        "1": {'startNode': "1", 'endNode': "2", 'type': gc.way_type["oneWay"], 'isActive': True},
        "2": {'startNode': "2", 'endNode': "3", 'type': gc.way_type["oneWay"], 'isActive': True},
        "3": {'startNode': "3", 'endNode': "4", 'type': gc.way_type["oneWay"], 'isActive': True},
        "4": {'startNode': "4", 'endNode': "5", 'type': gc.way_type["oneWay"], 'isActive': True},
        "5": {'startNode': "5", 'endNode': "6", 'type': gc.way_type["oneWay"], 'isActive': True}
    }

    pois_raw = [
        {"id": "10", "pose": (5, 5), "type": gc.base_node_type["load-unload-dock"]}
    ]
    graph = gc.SupervisorGraphCreator(nodes, edges, pois_raw)
    # graph.print_graph()
    expected_pose = {
        (1 + gc.WAITING_STOP_DIST_TO_INTERSECTION, 5): 1,
        (3, 5): 1,
        (5, 5): 4,
        (9, 5): 1,
        (12 - gc.WAITING_STOP_DIST_TO_INTERSECTION, 5): 1
    }
    assert len(graph.graph.nodes) == get_expected_nodes(nodes, edges)
    assert len(graph.graph.edges) == get_expected_edges_intersections_and_pois(nodes, edges) + 4
    assert check_graph_position(expected_pose, graph.graph.nodes(data=True))
    # print_graph_data(graph)


@pytest.mark.graph_creator_valid_data
def test_graph_18():
    # pomiedzy stanowiskami z dokowaniem (intersection - waiting - poi - departure - intersection) - one way
    nodes = {
        "1": {'name': 'D2', 'pos': (1, 5), 'type': gc.base_node_type["intersection"], "poiId": "0"},
        "2": {'name': 'D2', 'pos': (3, 5), 'type': gc.base_node_type["waiting"], "poiId": "0"},
        "3": {'name': 'D2', 'pos': (6, 5), 'type': gc.base_node_type["load-unload-dock"], "poiId": "3"},
        "4": {'name': 'D2', 'pos': (9, 5), 'type': gc.base_node_type["departure"], "poiId": "0"},
        "5": {'name': 'D2', 'pos': (10, 5), 'type': gc.base_node_type["normal"], "poiId": "0"},
        "6": {'name': 'D2', 'pos': (12, 5), 'type': gc.base_node_type["intersection"], "poiId": "0"},
    }

    edges = {
        "1": {'startNode': "1", 'endNode': "2", 'type': gc.way_type["oneWay"], 'isActive': True},
        "2": {'startNode': "2", 'endNode': "3", 'type': gc.way_type["oneWay"], 'isActive': True},
        "3": {'startNode': "3", 'endNode': "4", 'type': gc.way_type["oneWay"], 'isActive': True},
        "4": {'startNode': "4", 'endNode': "5", 'type': gc.way_type["oneWay"], 'isActive': True},
        "5": {'startNode': "5", 'endNode': "6", 'type': gc.way_type["oneWay"], 'isActive': True}
    }

    pois_raw = [
        {"id": "3", "pose": (6, 5), "type": gc.base_node_type["load-unload-dock"]}
    ]
    graph = gc.SupervisorGraphCreator(nodes, edges, pois_raw)
    # graph.print_graph()
    expected_pose = {
        (1 + gc.WAITING_STOP_DIST_TO_INTERSECTION, 5): 1,
        (3, 5): 1,
        (6, 5): 4,
        (9, 5): 1,
        (12 - gc.WAITING_STOP_DIST_TO_INTERSECTION, 5): 1
    }
    assert len(graph.graph.nodes) == get_expected_nodes(nodes, edges)
    assert len(graph.graph.edges) == get_expected_edges_intersections_and_pois(nodes, edges) + 4
    assert check_graph_position(expected_pose, graph.graph.nodes(data=True))
    # print_graph_data(graph)


@pytest.mark.graph_creator_valid_data
def test_graph_19():
    # pomiedzy stanowiskami z dokowaniem (intersection - waiting - poi - departure - intersection) - one way
    nodes = {
        "1": {'name': 'D2', 'pos': (1, 5), 'type': gc.base_node_type["intersection"], "poiId": "0"},
        "2": {'name': 'D2', 'pos': (3, 5), 'type': gc.base_node_type["waiting"], "poiId": "0"},
        "3": {'name': 'D2', 'pos': (6, 5), 'type': gc.base_node_type["load"], "poiId": "5"},
        "4": {'name': 'D2', 'pos': (9, 5), 'type': gc.base_node_type["departure"], "poiId": "0"},
        "5": {'name': 'D2', 'pos': (12, 5), 'type': gc.base_node_type["intersection"], "poiId": "0"},
    }

    edges = {
        "1": {'startNode': "1", 'endNode': "2", 'type': gc.way_type["oneWay"], 'isActive': True},
        "2": {'startNode': "2", 'endNode': "3", 'type': gc.way_type["oneWay"], 'isActive': True},
        "3": {'startNode': "3", 'endNode': "4", 'type': gc.way_type["oneWay"], 'isActive': True},
        "4": {'startNode': "4", 'endNode': "5", 'type': gc.way_type["oneWay"], 'isActive': True}
    }

    pois_raw = [
        {"id": "5", "pose": (6, 5), "type": gc.base_node_type["load"]}
    ]
    graph = gc.SupervisorGraphCreator(nodes, edges, pois_raw)
    # graph.print_graph()
    expected_pose = {
        (1 + gc.WAITING_STOP_DIST_TO_INTERSECTION, 5): 1,
        (3, 5): 1,
        (6, 5): 2,
        (9, 5): 1,
        (12 - gc.WAITING_STOP_DIST_TO_INTERSECTION, 5): 1
    }
    assert len(graph.graph.nodes) == get_expected_nodes(nodes, edges)
    assert len(graph.graph.edges) == get_expected_edges_intersections_and_pois(nodes, edges) + 4
    assert check_graph_position(expected_pose, graph.graph.nodes(data=True))
    # print_graph_data(graph)


@pytest.mark.graph_creator_valid_data
def test_graph_20():
    # pomiedzy stanowiskami z dokowaniem (intersection - waiting - poi - departure - intersection) - one way
    nodes = {
        "1": {'name': 'D2', 'pos': (1, 5), 'type': gc.base_node_type["intersection"], "poiId": "0"},
        "2": {'name': 'D2', 'pos': (3, 5), 'type': gc.base_node_type["waiting"], "poiId": "0"},
        "3": {'name': 'D2', 'pos': (6, 5), 'type': gc.base_node_type["unload"], "poiId": "4"},
        "4": {'name': 'D2', 'pos': (9, 5), 'type': gc.base_node_type["departure"], "poiId": "0"},
        "5": {'name': 'D2', 'pos': (12, 5), 'type': gc.base_node_type["intersection"], "poiId": "0"},
    }

    edges = {
        "1": {'startNode': "1", 'endNode': "2", 'type': gc.way_type["oneWay"], 'isActive': True},
        "2": {'startNode': "2", 'endNode': "3", 'type': gc.way_type["oneWay"], 'isActive': True},
        "3": {'startNode': "3", 'endNode': "4", 'type': gc.way_type["oneWay"], 'isActive': True},
        "4": {'startNode': "4", 'endNode': "5", 'type': gc.way_type["oneWay"], 'isActive': True}
    }

    pois_raw = [
        {"id": "4", "pose": (6, 5), "type": gc.base_node_type["load"]}
    ]
    graph = gc.SupervisorGraphCreator(nodes, edges, pois_raw)
    # graph.print_graph()
    expected_pose = {
        (1 + gc.WAITING_STOP_DIST_TO_INTERSECTION, 5): 1,
        (3, 5): 1,
        (6, 5): 2,
        (9, 5): 1,
        (12 - gc.WAITING_STOP_DIST_TO_INTERSECTION, 5): 1
    }
    assert len(graph.graph.nodes) == get_expected_nodes(nodes, edges)
    assert len(graph.graph.edges) == get_expected_edges_intersections_and_pois(nodes, edges) + 4
    assert check_graph_position(expected_pose, graph.graph.nodes(data=True))
    # print_graph_data(graph)


@pytest.mark.graph_creator_valid_data
def test_graph_21():
    # pomiedzy stanowiskami z dokowaniem (intersection - waiting - poi - departure - intersection) - one way
    nodes = {
        "1": {'name': 'D2', 'pos': (1, 5), 'type': gc.base_node_type["intersection"], "poiId": "0"},
        "2": {'name': 'D2', 'pos': (3, 5), 'type': gc.base_node_type["waiting"], "poiId": "0"},
        "3": {'name': 'D2', 'pos': (6, 5), 'type': gc.base_node_type["load-unload"], "poiId": "3"},
        "4": {'name': 'D2', 'pos': (9, 5), 'type': gc.base_node_type["departure"], "poiId": "0"},
        "5": {'name': 'D2', 'pos': (12, 5), 'type': gc.base_node_type["intersection"], "poiId": "0"},
    }

    edges = {
        "1": {'startNode': "1", 'endNode': "2", 'type': gc.way_type["oneWay"], 'isActive': True},
        "2": {'startNode': "2", 'endNode': "3", 'type': gc.way_type["oneWay"], 'isActive': True},
        "3": {'startNode': "3", 'endNode': "4", 'type': gc.way_type["oneWay"], 'isActive': True},
        "4": {'startNode': "4", 'endNode': "5", 'type': gc.way_type["oneWay"], 'isActive': True}
    }

    pois_raw = [
        {"id": "3", "pose": (6, 5), "type": gc.base_node_type["load"]}
    ]
    graph = gc.SupervisorGraphCreator(nodes, edges, pois_raw)
    # graph.print_graph()
    expected_pose = {
        (1 + gc.WAITING_STOP_DIST_TO_INTERSECTION, 5): 1,
        (3, 5): 1,
        (6, 5): 2,
        (9, 5): 1,
        (12 - gc.WAITING_STOP_DIST_TO_INTERSECTION, 5): 1
    }
    assert len(graph.graph.nodes) == get_expected_nodes(nodes, edges)
    assert len(graph.graph.edges) == get_expected_edges_intersections_and_pois(nodes, edges) + 4
    assert check_graph_position(expected_pose, graph.graph.nodes(data=True))
    # print_graph_data(graph)


@pytest.mark.graph_creator_valid_data
def test_graph_22():
    # pomiedzy stanowiskami z dokowaniem (intersection - waiting - poi - departure - intersection) - one way
    nodes = {
        "1": {'name': 'D2', 'pos': (1, 5), 'type': gc.base_node_type["intersection"], "poiId": "0"},
        "2": {'name': 'D2', 'pos': (3, 5), 'type': gc.base_node_type["normal"], "poiId": "0"},
        "3": {'name': 'D2', 'pos': (3, 5), 'type': gc.base_node_type["waiting"], "poiId": "0"},
        "4": {'name': 'D2', 'pos': (6, 5), 'type': gc.base_node_type["load-unload"], "poiId": "6"},
        "5": {'name': 'D2', 'pos': (9, 5), 'type': gc.base_node_type["departure"], "poiId": "0"},
        "6": {'name': 'D2', 'pos': (12, 5), 'type': gc.base_node_type["intersection"], "poiId": "0"},
    }

    edges = {
        "1": {'startNode': "1", 'endNode': "2", 'type': gc.way_type["oneWay"], 'isActive': True},
        "2": {'startNode': "2", 'endNode': "3", 'type': gc.way_type["oneWay"], 'isActive': True},
        "3": {'startNode': "3", 'endNode': "4", 'type': gc.way_type["oneWay"], 'isActive': True},
        "4": {'startNode': "4", 'endNode': "5", 'type': gc.way_type["oneWay"], 'isActive': True},
        "5": {'startNode': "5", 'endNode': "6", 'type': gc.way_type["oneWay"], 'isActive': True}
    }

    pois_raw = [
        {"id": "6", "pose": (6, 5), "type": gc.base_node_type["load"]}
    ]
    graph = gc.SupervisorGraphCreator(nodes, edges, pois_raw)
    # graph.print_graph()
    expected_pose = {
        (1 + gc.WAITING_STOP_DIST_TO_INTERSECTION, 5): 1,
        (3, 5): 1,
        (6, 5): 2,
        (9, 5): 1,
        (12 - gc.WAITING_STOP_DIST_TO_INTERSECTION, 5): 1
    }
    assert len(graph.graph.nodes) == get_expected_nodes(nodes, edges)
    assert len(graph.graph.edges) == get_expected_edges_intersections_and_pois(nodes, edges) + 4
    assert check_graph_position(expected_pose, graph.graph.nodes(data=True))
    # print_graph_data(graph)


@pytest.mark.graph_creator_valid_data
def test_graph_23():
    # pomiedzy stanowiskami z dokowaniem (intersection - waiting - poi - departure - intersection) - one way
    nodes = {
        "1": {'name': 'D2', 'pos': (1, 5), 'type': gc.base_node_type["intersection"], "poiId": "0"},
        "2": {'name': 'D2', 'pos': (3, 5), 'type': gc.base_node_type["waiting"], "poiId": "0"},
        "3": {'name': 'D2', 'pos': (3, 5), 'type': gc.base_node_type["normal"], "poiId": "0"},
        "4": {'name': 'D2', 'pos': (6, 5), 'type': gc.base_node_type["load-unload"], "poiId": "8"},
        "5": {'name': 'D2', 'pos': (9, 5), 'type': gc.base_node_type["departure"], "poiId": "0"},
        "6": {'name': 'D2', 'pos': (12, 5), 'type': gc.base_node_type["intersection"], "poiId": "0"},
    }

    edges = {
        "1": {'startNode': "1", 'endNode': "2", 'type': gc.way_type["oneWay"], 'isActive': True},
        "2": {'startNode': "2", 'endNode': "3", 'type': gc.way_type["oneWay"], 'isActive': True},
        "3": {'startNode': "3", 'endNode': "4", 'type': gc.way_type["oneWay"], 'isActive': True},
        "4": {'startNode': "4", 'endNode': "5", 'type': gc.way_type["oneWay"], 'isActive': True},
        "5": {'startNode': "5", 'endNode': "6", 'type': gc.way_type["oneWay"], 'isActive': True}
    }

    pois_raw = [
        {"id": "8", "pose": (6, 5), "type": gc.base_node_type["load-unload"]}
    ]
    graph = gc.SupervisorGraphCreator(nodes, edges, pois_raw)
    # graph.print_graph()
    expected_pose = {
        (1 + gc.WAITING_STOP_DIST_TO_INTERSECTION, 5): 1,
        (3, 5): 1,
        (6, 5): 2,
        (9, 5): 1,
        (12 - gc.WAITING_STOP_DIST_TO_INTERSECTION, 5): 1
    }
    assert len(graph.graph.nodes) == get_expected_nodes(nodes, edges)
    assert len(graph.graph.edges) == get_expected_edges_intersections_and_pois(nodes, edges) + 4
    assert check_graph_position(expected_pose, graph.graph.nodes(data=True))
    # print_graph_data(graph)


@pytest.mark.graph_creator_valid_data
def test_graph_24():
    # pomiedzy stanowiskami z dokowaniem (intersection - waiting - poi - departure - intersection) - one way
    nodes = {
        "1": {'name': 'D2', 'pos': (1, 5), 'type': gc.base_node_type["intersection"], "poiId": "0"},
        "2": {'name': 'D2', 'pos': (3, 5), 'type': gc.base_node_type["waiting"], "poiId": "0"},
        "3": {'name': 'D2', 'pos': (6, 5), 'type': gc.base_node_type["load-unload"], "poiId": "9"},
        "4": {'name': 'D2', 'pos': (7, 5), 'type': gc.base_node_type["normal"], "poiId": "0"},
        "5": {'name': 'D2', 'pos': (9, 5), 'type': gc.base_node_type["departure"], "poiId": "0"},
        "6": {'name': 'D2', 'pos': (12, 5), 'type': gc.base_node_type["intersection"], "poiId": "0"},
    }

    edges = {
        "1": {'startNode': "1", 'endNode': "2", 'type': gc.way_type["oneWay"], 'isActive': True},
        "2": {'startNode': "2", 'endNode': "3", 'type': gc.way_type["oneWay"], 'isActive': True},
        "3": {'startNode': "3", 'endNode': "4", 'type': gc.way_type["oneWay"], 'isActive': True},
        "4": {'startNode': "4", 'endNode': "5", 'type': gc.way_type["oneWay"], 'isActive': True},
        "5": {'startNode': "5", 'endNode': "6", 'type': gc.way_type["oneWay"], 'isActive': True}
    }

    pois_raw = [
        {"id": "9", "pose": (6, 5), "type": gc.base_node_type["load-unload"]}
    ]
    graph = gc.SupervisorGraphCreator(nodes, edges, pois_raw)
    # graph.print_graph()
    expected_pose = {
        (1 + gc.WAITING_STOP_DIST_TO_INTERSECTION, 5): 1,
        (3, 5): 1,
        (6, 5): 2,
        (9, 5): 1,
        (12 - gc.WAITING_STOP_DIST_TO_INTERSECTION, 5): 1
    }
    assert len(graph.graph.nodes) == get_expected_nodes(nodes, edges)
    assert len(graph.graph.edges) == get_expected_edges_intersections_and_pois(nodes, edges) + 4
    assert check_graph_position(expected_pose, graph.graph.nodes(data=True))
    # print_graph_data(graph)


@pytest.mark.graph_creator_valid_data
def test_graph_25():
    # pomiedzy stanowiskami z dokowaniem (intersection - waiting - poi - departure - intersection) - one way
    nodes = {
        "1": {'name': 'D2', 'pos': (1, 5), 'type': gc.base_node_type["intersection"], "poiId": "0"},
        "2": {'name': 'D2', 'pos': (3, 5), 'type': gc.base_node_type["waiting"], "poiId": "0"},
        "3": {'name': 'D2', 'pos': (6, 5), 'type': gc.base_node_type["load-unload"], "poiId": "1"},
        "4": {'name': 'D2', 'pos': (9, 5), 'type': gc.base_node_type["departure"], "poiId": "0"},
        "5": {'name': 'D2', 'pos': (10, 5), 'type': gc.base_node_type["normal"], "poiId": "0"},
        "6": {'name': 'D2', 'pos': (12, 5), 'type': gc.base_node_type["intersection"], "poiId": "0"},
    }

    edges = {
        "1": {'startNode': "1", 'endNode': "2", 'type': gc.way_type["oneWay"], 'isActive': True},
        "2": {'startNode': "2", 'endNode': "3", 'type': gc.way_type["oneWay"], 'isActive': True},
        "3": {'startNode': "3", 'endNode': "4", 'type': gc.way_type["oneWay"], 'isActive': True},
        "4": {'startNode': "4", 'endNode': "5", 'type': gc.way_type["oneWay"], 'isActive': True},
        "5": {'startNode': "5", 'endNode': "6", 'type': gc.way_type["oneWay"], 'isActive': True}
    }

    pois_raw = [
        {"id": "1", "pose": (6, 5), "type": gc.base_node_type["load-unload"]}
    ]
    graph = gc.SupervisorGraphCreator(nodes, edges, pois_raw)
    # graph.print_graph()
    expected_pose = {
        (1 + gc.WAITING_STOP_DIST_TO_INTERSECTION, 5): 1,
        (3, 5): 1,
        (6, 5): 2,
        (9, 5): 1,
        (12 - gc.WAITING_STOP_DIST_TO_INTERSECTION, 5): 1
    }
    assert len(graph.graph.nodes) == get_expected_nodes(nodes, edges)
    assert len(graph.graph.edges) == get_expected_edges_intersections_and_pois(nodes, edges) + 4
    assert check_graph_position(expected_pose, graph.graph.nodes(data=True))
    # print_graph_data(graph)


@pytest.mark.graph_creator_valid_data
def test_graph_26():
    # pomiedzy stanowiskami z dokowaniem (intersection - waiting-departure - poi - waiting-departure - intersection) -
    # two(narrow)way
    nodes = {
        "1": {'name': 'D2', 'pos': (1, 5), 'type': gc.base_node_type["intersection"], "poiId": "0"},
        "2": {'name': 'D2', 'pos': (3, 5), 'type': gc.base_node_type["waiting-departure"], "poiId": "0"},
        "3": {'name': 'D2', 'pos': (9, 5), 'type': gc.base_node_type["load-dock"], "poiId": "10"}
    }

    edges = {
        "1": {'startNode': "1", 'endNode': "2", 'type': gc.way_type["twoWay"], 'isActive': True},
        "2": {'startNode': "2", 'endNode': "3", 'type': gc.way_type["narrowTwoWay"], 'isActive': True}
    }

    pois_raw = [
        {"id": "10", "pose": (6, 5), "type": gc.base_node_type["load-dock"]}
    ]
    graph = gc.SupervisorGraphCreator(nodes, edges, pois_raw)
    # graph.print_graph()
    expected_pose = {
        (1 + gc.WAITING_STOP_DIST_TO_INTERSECTION, 5 + gc.MAIN_CORRIDOR_WIDTH / 2): 1,
        (1 + gc.WAITING_STOP_DIST_TO_INTERSECTION, 5 - gc.MAIN_CORRIDOR_WIDTH / 2): 1,
        (3 - gc.WAITING_STOP_DIST_TO_INTERSECTION, 5 + gc.MAIN_CORRIDOR_WIDTH / 2): 1,
        (3 - gc.WAITING_STOP_DIST_TO_INTERSECTION, 5 - gc.MAIN_CORRIDOR_WIDTH / 2): 1,
        (3 + gc.WAITING_STOP_DIST_TO_INTERSECTION, 5): 2,
        (9, 5): 4,
    }
    assert len(graph.graph.nodes) == get_expected_nodes(nodes, edges)
    assert len(graph.graph.edges) == get_expected_edges_intersections_and_pois(nodes, edges) + 4
    assert check_graph_position(expected_pose, graph.graph.nodes(data=True))
    # print_graph_data(graph)


@pytest.mark.graph_creator_valid_data
def test_graph_27():
    # pomiedzy stanowiskami z dokowaniem (intersection - waiting-departure - poi - waiting-departure - intersection) -
    # two(narrow)way
    nodes = {
        "1": {'name': 'D2', 'pos': (1, 5), 'type': gc.base_node_type["intersection"], "poiId": "0"},
        "2": {'name': 'D2', 'pos': (3, 5), 'type': gc.base_node_type["waiting-departure"], "poiId": "0"},
        "3": {'name': 'D2', 'pos': (6, 5), 'type': gc.base_node_type["unload-dock"], "poiId": "8"}
    }

    edges = {
        "1": {'startNode': "1", 'endNode': "2", 'type': gc.way_type["twoWay"], 'isActive': True},
        "2": {'startNode': "2", 'endNode': "3", 'type': gc.way_type["narrowTwoWay"], 'isActive': True}
    }
    pois_raw = [
        {"id": "8", "pose": (6, 5), "type": gc.base_node_type["unload-dock"]}
    ]
    graph = gc.SupervisorGraphCreator(nodes, edges, pois_raw)
    # graph.print_graph()
    expected_pose = {
        (1 + gc.WAITING_STOP_DIST_TO_INTERSECTION, 5 + gc.MAIN_CORRIDOR_WIDTH / 2): 1,
        (1 + gc.WAITING_STOP_DIST_TO_INTERSECTION, 5 - gc.MAIN_CORRIDOR_WIDTH / 2): 1,
        (3 - gc.WAITING_STOP_DIST_TO_INTERSECTION, 5 + gc.MAIN_CORRIDOR_WIDTH / 2): 1,
        (3 - gc.WAITING_STOP_DIST_TO_INTERSECTION, 5 - gc.MAIN_CORRIDOR_WIDTH / 2): 1,
        (3 + gc.WAITING_STOP_DIST_TO_INTERSECTION, 5): 2,
        (6, 5): 4,
    }
    assert len(graph.graph.nodes) == get_expected_nodes(nodes, edges)
    assert len(graph.graph.edges) == get_expected_edges_intersections_and_pois(nodes, edges) + 4
    assert check_graph_position(expected_pose, graph.graph.nodes(data=True))
    # print_graph_data(graph)


@pytest.mark.graph_creator_valid_data
def test_graph_28():
    # pomiedzy stanowiskami z dokowaniem (intersection - waiting-departure - poi - waiting-departure - intersection) -
    # two(narrow)way
    nodes = {
        "1": {'name': 'D2', 'pos': (1, 5), 'type': gc.base_node_type["intersection"], "poiId": "0"},
        "2": {'name': 'D2', 'pos': (3, 5), 'type': gc.base_node_type["waiting-departure"], "poiId": "0"},
        "3": {'name': 'D2', 'pos': (6, 5), 'type': gc.base_node_type["load-unload-dock"], "poiId": "1"}
    }

    edges = {
        "1": {'startNode': "1", 'endNode': "2", 'type': gc.way_type["twoWay"], 'isActive': True},
        "2": {'startNode': "2", 'endNode': "3", 'type': gc.way_type["narrowTwoWay"], 'isActive': True}
    }

    pois_raw = [
        {"id": "1", "pose": (6, 5), "type": gc.base_node_type["load-unload-dock"]}
    ]
    graph = gc.SupervisorGraphCreator(nodes, edges, pois_raw)
    # graph.print_graph()
    expected_pose = {
        (1 + gc.WAITING_STOP_DIST_TO_INTERSECTION, 5 + gc.MAIN_CORRIDOR_WIDTH / 2): 1,
        (1 + gc.WAITING_STOP_DIST_TO_INTERSECTION, 5 - gc.MAIN_CORRIDOR_WIDTH / 2): 1,
        (3 - gc.WAITING_STOP_DIST_TO_INTERSECTION, 5 + gc.MAIN_CORRIDOR_WIDTH / 2): 1,
        (3 - gc.WAITING_STOP_DIST_TO_INTERSECTION, 5 - gc.MAIN_CORRIDOR_WIDTH / 2): 1,
        (3 + gc.WAITING_STOP_DIST_TO_INTERSECTION, 5): 2,
        (6, 5): 4,
    }
    assert len(graph.graph.nodes) == get_expected_nodes(nodes, edges)
    assert len(graph.graph.edges) == get_expected_edges_intersections_and_pois(nodes, edges) + 4
    assert check_graph_position(expected_pose, graph.graph.nodes(data=True))
    # print_graph_data(graph)


@pytest.mark.graph_creator_valid_data
def test_graph_29():
    # pomiedzy stanowiskami z dokowaniem (intersection - waiting-departure - poi - waiting-departure - intersection) -
    # two(narrow)way
    nodes = {
        "1": {'name': 'D2', 'pos': (1, 5), 'type': gc.base_node_type["intersection"], "poiId": "0"},
        "2": {'name': 'D2', 'pos': (3, 5), 'type': gc.base_node_type["normal"], "poiId": "0"},
        "3": {'name': 'D2', 'pos': (6, 5), 'type': gc.base_node_type["waiting-departure"], "poiId": "0"},
        "4": {'name': 'D2', 'pos': (9, 5), 'type': gc.base_node_type["load-unload-dock"], "poiId": "2"}
    }

    edges = {
        "1": {'startNode': "1", 'endNode': "2", 'type': gc.way_type["twoWay"], 'isActive': True},
        "2": {'startNode': "2", 'endNode': "3", 'type': gc.way_type["twoWay"], 'isActive': True},
        "3": {'startNode': "3", 'endNode': "4", 'type': gc.way_type["narrowTwoWay"], 'isActive': True}
    }

    pois_raw = [
        {"id": "2", "pose": (9, 5), "type": gc.base_node_type["load-unload-dock"]}
    ]
    graph = gc.SupervisorGraphCreator(nodes, edges, pois_raw)
    # graph.print_graph()
    expected_pose = {
        (1 + gc.WAITING_STOP_DIST_TO_INTERSECTION, 5 + gc.MAIN_CORRIDOR_WIDTH / 2): 1,
        (1 + gc.WAITING_STOP_DIST_TO_INTERSECTION, 5 - gc.MAIN_CORRIDOR_WIDTH / 2): 1,
        (6 - gc.WAITING_STOP_DIST_TO_INTERSECTION, 5 + gc.MAIN_CORRIDOR_WIDTH / 2): 1,
        (6 - gc.WAITING_STOP_DIST_TO_INTERSECTION, 5 - gc.MAIN_CORRIDOR_WIDTH / 2): 1,
        (6 + gc.WAITING_STOP_DIST_TO_INTERSECTION, 5): 2,
        (9, 5): 4,
    }
    assert len(graph.graph.nodes) == get_expected_nodes(nodes, edges)
    assert len(graph.graph.edges) == get_expected_edges_intersections_and_pois(nodes, edges) + 4
    assert check_graph_position(expected_pose, graph.graph.nodes(data=True))
    # print_graph_data(graph)


@pytest.mark.graph_creator_valid_data
def test_graph_30():
    # pomiedzy stanowiskami z dokowaniem (intersection - waiting-departure - poi - waiting-departure - intersection) -
    # two(narrow)way
    nodes = {
        "1": {'name': 'D2', 'pos': (1, 5), 'type': gc.base_node_type["intersection"], "poiId": "0"},
        "2": {'name': 'D2', 'pos': (3, 5), 'type': gc.base_node_type["waiting-departure"], "poiId": "0"},
        "3": {'name': 'D2', 'pos': (6, 5), 'type': gc.base_node_type["normal"], "poiId": "0"},
        "4": {'name': 'D2', 'pos': (9, 5), 'type': gc.base_node_type["load-unload-dock"], "poiId": "3"}
    }

    edges = {
        "1": {'startNode': "1", 'endNode': "2", 'type': gc.way_type["twoWay"], 'isActive': True},
        "2": {'startNode': "2", 'endNode': "3", 'type': gc.way_type["narrowTwoWay"], 'isActive': True},
        "3": {'startNode': "3", 'endNode': "4", 'type': gc.way_type["narrowTwoWay"], 'isActive': True}
    }

    pois_raw = [
        {"id": "3", "pose": (9, 5), "type": gc.base_node_type["load-unload-dock"]}
    ]
    graph = gc.SupervisorGraphCreator(nodes, edges, pois_raw)
    # graph.print_graph()
    expected_pose = {
        (1 + gc.WAITING_STOP_DIST_TO_INTERSECTION, 5 + gc.MAIN_CORRIDOR_WIDTH / 2): 1,
        (1 + gc.WAITING_STOP_DIST_TO_INTERSECTION, 5 - gc.MAIN_CORRIDOR_WIDTH / 2): 1,
        (3 - gc.WAITING_STOP_DIST_TO_INTERSECTION, 5 + gc.MAIN_CORRIDOR_WIDTH / 2): 1,
        (3 - gc.WAITING_STOP_DIST_TO_INTERSECTION, 5 - gc.MAIN_CORRIDOR_WIDTH / 2): 1,
        (3 + gc.WAITING_STOP_DIST_TO_INTERSECTION, 5): 2,
        (9, 5): 4,
    }
    assert len(graph.graph.nodes) == get_expected_nodes(nodes, edges)
    assert len(graph.graph.edges) == get_expected_edges_intersections_and_pois(nodes, edges) + 4
    assert check_graph_position(expected_pose, graph.graph.nodes(data=True))
    # print_graph_data(graph)


@pytest.mark.graph_creator_valid_data
def test_graph_31():
    # pomiedzy stanowiskami bez dokowana (intersection - waiting-departure - poi - waiting-departure - intersection) -
    # two(narrow)way
    nodes = {
        "1": {'name': 'D2', 'pos': (1, 5), 'type': gc.base_node_type["intersection"], "poiId": "0"},
        "2": {'name': 'D2', 'pos': (3, 5), 'type': gc.base_node_type["waiting-departure"], "poiId": "0"},
        "3": {'name': 'D2', 'pos': (5, 5), 'type': gc.base_node_type["load"], "poiId": "4"}
    }

    edges = {
        "1": {'startNode': "1", 'endNode': "2", 'type': gc.way_type["twoWay"], 'isActive': True},
        "2": {'startNode': "2", 'endNode': "3", 'type': gc.way_type["narrowTwoWay"], 'isActive': True}
    }

    pois_raw = [
        {"id": "4", "pose": (5, 5), "type": gc.base_node_type["load"]}
    ]
    graph = gc.SupervisorGraphCreator(nodes, edges, pois_raw)
    # graph.print_graph()
    expected_pose = {
        (1 + gc.WAITING_STOP_DIST_TO_INTERSECTION, 5 + gc.MAIN_CORRIDOR_WIDTH / 2): 1,
        (1 + gc.WAITING_STOP_DIST_TO_INTERSECTION, 5 - gc.MAIN_CORRIDOR_WIDTH / 2): 1,
        (3 - gc.WAITING_STOP_DIST_TO_INTERSECTION, 5 + gc.MAIN_CORRIDOR_WIDTH / 2): 1,
        (3 - gc.WAITING_STOP_DIST_TO_INTERSECTION, 5 - gc.MAIN_CORRIDOR_WIDTH / 2): 1,
        (3 + gc.WAITING_STOP_DIST_TO_INTERSECTION, 5): 2,
        (5, 5): 2,
    }
    assert len(graph.graph.nodes) == get_expected_nodes(nodes, edges)
    assert len(graph.graph.edges) == get_expected_edges_intersections_and_pois(nodes, edges) + 4
    assert check_graph_position(expected_pose, graph.graph.nodes(data=True))
    # print_graph_data


@pytest.mark.graph_creator_valid_data
def test_graph_32():
    # pomiedzy stanowiskami bez dokowana (intersection - waiting-departure - poi - waiting-departure - intersection) -
    # two(narrow)way
    nodes = {
        "1": {'name': 'D2', 'pos': (1, 5), 'type': gc.base_node_type["intersection"], "poiId": "0"},
        "2": {'name': 'D2', 'pos': (3, 5), 'type': gc.base_node_type["waiting-departure"], "poiId": "0"},
        "3": {'name': 'D2', 'pos': (6, 5), 'type': gc.base_node_type["unload"], "poiId": "5"}
    }

    edges = {
        "1": {'startNode': "1", 'endNode': "2", 'type': gc.way_type["twoWay"], 'isActive': True},
        "2": {'startNode': "2", 'endNode': "3", 'type': gc.way_type["narrowTwoWay"], 'isActive': True}
    }

    pois_raw = [
        {"id": "5", "pose": (6, 5), "type": gc.base_node_type["unload"]}
    ]
    graph = gc.SupervisorGraphCreator(nodes, edges, pois_raw)
    # graph.print_graph()
    expected_pose = {
        (1 + gc.WAITING_STOP_DIST_TO_INTERSECTION, 5 + gc.MAIN_CORRIDOR_WIDTH / 2): 1,
        (1 + gc.WAITING_STOP_DIST_TO_INTERSECTION, 5 - gc.MAIN_CORRIDOR_WIDTH / 2): 1,
        (3 - gc.WAITING_STOP_DIST_TO_INTERSECTION, 5 + gc.MAIN_CORRIDOR_WIDTH / 2): 1,
        (3 - gc.WAITING_STOP_DIST_TO_INTERSECTION, 5 - gc.MAIN_CORRIDOR_WIDTH / 2): 1,
        (3 + gc.WAITING_STOP_DIST_TO_INTERSECTION, 5): 2,
        (6, 5): 2,
    }
    assert len(graph.graph.nodes) == get_expected_nodes(nodes, edges)
    assert len(graph.graph.edges) == get_expected_edges_intersections_and_pois(nodes, edges) + 4
    assert check_graph_position(expected_pose, graph.graph.nodes(data=True))
    # print_graph_data(graph)


@pytest.mark.graph_creator_valid_data
def test_graph_33():
    # pomiedzy stanowiskami bez dokowana (intersection - waiting-departure - poi - waiting-departure - intersection) -
    # two(narrow)way
    nodes = {
        "1": {'name': 'D2', 'pos': (1, 5), 'type': gc.base_node_type["intersection"], "poiId": "0"},
        "2": {'name': 'D2', 'pos': (3, 5), 'type': gc.base_node_type["waiting-departure"], "poiId": "0"},
        "3": {'name': 'D2', 'pos': (6, 5), 'type': gc.base_node_type["load-unload"], "poiId": "6"}
    }

    edges = {
        "1": {'startNode': "1", 'endNode': "2", 'type': gc.way_type["twoWay"], 'isActive': True},
        "2": {'startNode': "2", 'endNode': "3", 'type': gc.way_type["narrowTwoWay"], 'isActive': True}
    }

    pois_raw = [
        {"id": "6", "pose": (6, 5), "type": gc.base_node_type["load-unload"]}
    ]
    graph = gc.SupervisorGraphCreator(nodes, edges, pois_raw)
    # graph.print_graph()
    expected_pose = {
        (1 + gc.WAITING_STOP_DIST_TO_INTERSECTION, 5 + gc.MAIN_CORRIDOR_WIDTH / 2): 1,
        (1 + gc.WAITING_STOP_DIST_TO_INTERSECTION, 5 - gc.MAIN_CORRIDOR_WIDTH / 2): 1,
        (3 - gc.WAITING_STOP_DIST_TO_INTERSECTION, 5 + gc.MAIN_CORRIDOR_WIDTH / 2): 1,
        (3 - gc.WAITING_STOP_DIST_TO_INTERSECTION, 5 - gc.MAIN_CORRIDOR_WIDTH / 2): 1,
        (3 + gc.WAITING_STOP_DIST_TO_INTERSECTION, 5): 2,
        (6, 5): 2,
    }
    assert len(graph.graph.nodes) == get_expected_nodes(nodes, edges)
    assert len(graph.graph.edges) == get_expected_edges_intersections_and_pois(nodes, edges) + 4
    assert check_graph_position(expected_pose, graph.graph.nodes(data=True))
    # print_graph_data(graph)


@pytest.mark.graph_creator_valid_data
def test_graph_34():
    # pomiedzy stanowiskami bez dokowana (intersection - waiting-departure - poi - waiting-departure - intersection) -
    # two(narrow)way
    nodes = {
        "1": {'name': 'D2', 'pos': (1, 5), 'type': gc.base_node_type["intersection"], "poiId": "0"},
        "2": {'name': 'D2', 'pos': (3, 5), 'type': gc.base_node_type["normal"], "poiId": "0"},
        "3": {'name': 'D2', 'pos': (5, 5), 'type': gc.base_node_type["waiting-departure"], "poiId": "0"},
        "4": {'name': 'D2', 'pos': (7, 5), 'type': gc.base_node_type["load-unload"], "poiId": "7"}
    }

    edges = {
        "1": {'startNode': "1", 'endNode': "2", 'type': gc.way_type["twoWay"], 'isActive': True},
        "2": {'startNode': "2", 'endNode': "3", 'type': gc.way_type["twoWay"], 'isActive': True},
        "3": {'startNode': "3", 'endNode': "4", 'type': gc.way_type["narrowTwoWay"], 'isActive': True}
    }

    pois_raw = [
        {"id": "7", "pose": (7, 5), "type": gc.base_node_type["load-unload"]}
    ]
    graph = gc.SupervisorGraphCreator(nodes, edges, pois_raw)
    # graph.print_graph()
    expected_pose = {
        (1 + gc.WAITING_STOP_DIST_TO_INTERSECTION, 5 + gc.MAIN_CORRIDOR_WIDTH / 2): 1,
        (1 + gc.WAITING_STOP_DIST_TO_INTERSECTION, 5 - gc.MAIN_CORRIDOR_WIDTH / 2): 1,
        (5 - gc.WAITING_STOP_DIST_TO_INTERSECTION, 5 + gc.MAIN_CORRIDOR_WIDTH / 2): 1,
        (5 - gc.WAITING_STOP_DIST_TO_INTERSECTION, 5 - gc.MAIN_CORRIDOR_WIDTH / 2): 1,
        (5 + gc.WAITING_STOP_DIST_TO_INTERSECTION, 5): 2,
        (7, 5): 2,
    }
    assert len(graph.graph.nodes) == get_expected_nodes(nodes, edges)
    assert len(graph.graph.edges) == get_expected_edges_intersections_and_pois(nodes, edges) + 4
    assert check_graph_position(expected_pose, graph.graph.nodes(data=True))
    # print_graph_data(graph)


@pytest.mark.graph_creator_valid_data
def test_graph_35():
    # pomiedzy stanowiskami bez dokowana (intersection - waiting-departure - poi - waiting-departure - intersection) -
    # two(narrow)way
    nodes = {
        "1": {'name': 'D2', 'pos': (1, 5), 'type': gc.base_node_type["intersection"], "poiId": "0"},
        "2": {'name': 'D2', 'pos': (3, 5), 'type': gc.base_node_type["waiting-departure"], "poiId": "0"},
        "3": {'name': 'D2', 'pos': (5, 5), 'type': gc.base_node_type["normal"], "poiId": "0"},
        "4": {'name': 'D2', 'pos': (7, 5), 'type': gc.base_node_type["load-unload"], "poiId": "8"}
    }

    edges = {
        "1": {'startNode': "1", 'endNode': "2", 'type': gc.way_type["twoWay"], 'isActive': True},
        "2": {'startNode': "2", 'endNode': "3", 'type': gc.way_type["narrowTwoWay"], 'isActive': True},
        "3": {'startNode': "3", 'endNode': "4", 'type': gc.way_type["narrowTwoWay"], 'isActive': True}
    }

    pois_raw = [
        {"id": "8", "pose": (7, 5), "type": gc.base_node_type["load-unload"]}
    ]
    graph = gc.SupervisorGraphCreator(nodes, edges, pois_raw)
    # graph.print_graph()
    expected_pose = {
        (1 + gc.WAITING_STOP_DIST_TO_INTERSECTION, 5 + gc.MAIN_CORRIDOR_WIDTH / 2): 1,
        (1 + gc.WAITING_STOP_DIST_TO_INTERSECTION, 5 - gc.MAIN_CORRIDOR_WIDTH / 2): 1,
        (3 - gc.WAITING_STOP_DIST_TO_INTERSECTION, 5 + gc.MAIN_CORRIDOR_WIDTH / 2): 1,
        (3 - gc.WAITING_STOP_DIST_TO_INTERSECTION, 5 - gc.MAIN_CORRIDOR_WIDTH / 2): 1,
        (3 + gc.WAITING_STOP_DIST_TO_INTERSECTION, 5): 2,
        (7, 5): 2,
    }
    assert len(graph.graph.nodes) == get_expected_nodes(nodes, edges)
    assert len(graph.graph.edges) == get_expected_edges_intersections_and_pois(nodes, edges) + 4
    assert check_graph_position(expected_pose, graph.graph.nodes(data=True))
    # print_graph_data(graph)


@pytest.mark.graph_creator_valid_data
def test_graph_36():
    # #prawidlowy drugie poi zwykle np ladowarka
    nodes = {
        "1": {'name': 'D2', 'pos': (1, 3), 'type': gc.base_node_type["intersection"], "poiId": "0"},
        "2": {'name': 'D2', 'pos': (1, 0), 'type': gc.base_node_type["waiting-departure"], "poiId": "0"},
        "4": {'name': 'D2', 'pos': (7, 0), 'type': gc.base_node_type["load-unload"], "poiId": "8"},
        "5": {'name': 'D2', 'pos': (1, 9), 'type': gc.base_node_type["intersection"], "poiId": "0"},
        "6": {'name': 'D2', 'pos': (1, 17), 'type': gc.base_node_type["intersection"], "poiId": "0"},
        "7": {'name': 'D2', 'pos': (3, 9), 'type': gc.base_node_type["waiting"], "poiId": "0"},
        "8": {'name': 'D2', 'pos': (3, 13), 'type': gc.base_node_type["charger"], "poiId": "2"},
        "9": {'name': 'D2', 'pos': (3, 17), 'type': gc.base_node_type["departure"], "poiId": "0"}
    }

    edges = {
        "1": {'startNode': "1", 'endNode': "2", 'type': gc.way_type["twoWay"], 'isActive': True},
        "3": {'startNode': "2", 'endNode': "4", 'type': gc.way_type["narrowTwoWay"], 'isActive': True},
        "4": {'startNode': "1", 'endNode': "5", 'type': gc.way_type["twoWay"], 'isActive': True},
        "5": {'startNode': "5", 'endNode': "6", 'type': gc.way_type["twoWay"], 'isActive': True},
        "6": {'startNode': "5", 'endNode': "7", 'type': gc.way_type["oneWay"], 'isActive': True},
        "7": {'startNode': "7", 'endNode': "8", 'type': gc.way_type["oneWay"], 'isActive': True},
        "8": {'startNode': "8", 'endNode': "9", 'type': gc.way_type["oneWay"], 'isActive': True},
        "9": {'startNode': "9", 'endNode': "6", 'type': gc.way_type["oneWay"], 'isActive': True}
    }

    pois_raw = [
        {"id": "8", "pose": (7, 3), "type": gc.base_node_type["load-unload"]},
        {"id": "2", "pose": (3, 13), "type": gc.base_node_type["charger"]}
    ]
    graph = gc.SupervisorGraphCreator(nodes, edges, pois_raw)
    # graph.print_graph()
    expected_pose = {
        (3, 17): 1,
        (3, 13): 4,
        (3, 9): 1,
        (1 + gc.WAITING_STOP_DIST_TO_INTERSECTION, 17): 1,
        (1 + gc.MAIN_CORRIDOR_WIDTH / 2, 17 - gc.WAITING_STOP_DIST_TO_INTERSECTION): 1,
        (1 - gc.MAIN_CORRIDOR_WIDTH / 2, 17 - gc.WAITING_STOP_DIST_TO_INTERSECTION): 1,
        (1 + gc.WAITING_STOP_DIST_TO_INTERSECTION, 9): 1,
        (1 + gc.MAIN_CORRIDOR_WIDTH / 2, 9 + gc.WAITING_STOP_DIST_TO_INTERSECTION): 1,
        (1 + gc.MAIN_CORRIDOR_WIDTH / 2, 9 - gc.WAITING_STOP_DIST_TO_INTERSECTION): 1,
        (1 - gc.MAIN_CORRIDOR_WIDTH / 2, 9 + gc.WAITING_STOP_DIST_TO_INTERSECTION): 1,
        (1 - gc.MAIN_CORRIDOR_WIDTH / 2, 9 - gc.WAITING_STOP_DIST_TO_INTERSECTION): 1,
        (1 + gc.MAIN_CORRIDOR_WIDTH / 2, 3 + gc.WAITING_STOP_DIST_TO_INTERSECTION): 1,
        (1 + gc.MAIN_CORRIDOR_WIDTH / 2, 3 - gc.WAITING_STOP_DIST_TO_INTERSECTION): 1,
        (1 - gc.MAIN_CORRIDOR_WIDTH / 2, 3 + gc.WAITING_STOP_DIST_TO_INTERSECTION): 1,
        (1 - gc.MAIN_CORRIDOR_WIDTH / 2, 3 - gc.WAITING_STOP_DIST_TO_INTERSECTION): 1,
        (1 + gc.MAIN_CORRIDOR_WIDTH / 2, 0 + gc.WAITING_STOP_DIST_TO_INTERSECTION): 1,
        (1 - gc.MAIN_CORRIDOR_WIDTH / 2, 0 + gc.WAITING_STOP_DIST_TO_INTERSECTION): 1,
        (1 + gc.WAITING_STOP_DIST_TO_INTERSECTION, 0): 2,
        (7, 0): 2
    }
    assert len(graph.graph.nodes) == get_expected_nodes(nodes, edges)
    assert len(graph.graph.edges) == get_expected_edges_intersections_and_pois(nodes, edges) + 12
    assert check_graph_position(expected_pose, graph.graph.nodes(data=True))
    # print_graph_data(graph)


@pytest.mark.graph_creator_valid_data
def test_graph_37():
    # intersection - parking - intersection (dwukierunkowa waska)
    nodes = {
        "1": {'name': 'D2', 'pos': (1, 5), 'type': gc.base_node_type["intersection"], "poiId": "0"},
        "2": {'name': 'D2', 'pos': (3, 5), 'type': gc.base_node_type["parking"], "poiId": "12"}
    }

    edges = {
        "1": {'startNode': "1", 'endNode': "2", 'type': gc.way_type["narrowTwoWay"], 'isActive': True}
    }

    pois_raw = [
        {"id": "12", "pose": (3, 5), "type": gc.base_node_type["parking"]}
    ]
    graph = gc.SupervisorGraphCreator(nodes, edges, pois_raw)
    # graph.print_graph()
    expected_pose = {
        (3, 5): 1,
        (1 + gc.WAITING_STOP_DIST_TO_INTERSECTION, 5): 2
    }
    assert len(graph.graph.nodes) == get_expected_nodes(nodes, edges)
    assert len(graph.graph.edges) == get_expected_edges_intersections_and_pois(nodes, edges) + 2
    assert check_graph_position(expected_pose, graph.graph.nodes(data=True))
    # print_graph_data(graph)


@pytest.mark.graph_creator_valid_data
def test_graph_38():
    # intersection - parking - intersection (dwukierunkowa waska)
    nodes = {
        "1": {'name': 'D2', 'pos': (1, 5), 'type': gc.base_node_type["intersection"], "poiId": "0"},
        "2": {'name': 'D2', 'pos': (1, 5), 'type': gc.base_node_type["normal"], "poiId": "0"},
        "3": {'name': 'D2', 'pos': (3, 5), 'type': gc.base_node_type["parking"], "poiId": "13"}
    }

    edges = {
        "1": {'startNode': "1", 'endNode': "2", 'type': gc.way_type["narrowTwoWay"], 'isActive': True},
        "2": {'startNode': "2", 'endNode': "3", 'type': gc.way_type["narrowTwoWay"], 'isActive': True}
    }

    pois_raw = [
        {"id": "13", "pose": (3, 5), "type": gc.base_node_type["parking"]}
    ]
    graph = gc.SupervisorGraphCreator(nodes, edges, pois_raw)
    # graph.print_graph()
    expected_pose = {
        (3, 5): 1,
        (1 + gc.WAITING_STOP_DIST_TO_INTERSECTION, 5): 2
    }
    assert len(graph.graph.nodes) == get_expected_nodes(nodes, edges)
    assert len(graph.graph.edges) == get_expected_edges_intersections_and_pois(nodes, edges) + 2
    assert check_graph_position(expected_pose, graph.graph.nodes(data=True))
    # print_graph_data(graph)


@pytest.mark.graph_creator_valid_data
def test_graph_39():
    # intersection - queue - intersection (droga jednokierunkowa)
    nodes = {
        "1": {'name': 'D2', 'pos': (1, 5), 'type': gc.base_node_type["intersection"], "poiId": "0"},
        "2": {'name': 'D2', 'pos': (3, 5), 'type': gc.base_node_type["queue"], "poiId": "17"},
        "3": {'name': 'D2', 'pos': (5, 5), 'type': gc.base_node_type["intersection"], "poiId": "0"}
    }

    edges = {
        "1": {'startNode': "1", 'endNode': "2", 'type': gc.way_type["oneWay"], 'isActive': True},
        "2": {'startNode': "2", 'endNode': "3", 'type': gc.way_type["oneWay"], 'isActive': True}
    }

    pois_raw = [
        {"id": "17", "pose": (3, 5), "type": gc.base_node_type["queue"]}
    ]
    graph = gc.SupervisorGraphCreator(nodes, edges, pois_raw)
    # graph.print_graph()
    expected_pose = {
        (1 + gc.WAITING_STOP_DIST_TO_INTERSECTION, 5): 1,
        (3, 5): 1,
        (5 - gc.WAITING_STOP_DIST_TO_INTERSECTION, 5): 1
    }
    assert len(graph.graph.nodes) == get_expected_nodes(nodes, edges)
    assert len(graph.graph.edges) == get_expected_edges_intersections_and_pois(nodes, edges) + 2
    assert check_graph_position(expected_pose, graph.graph.nodes(data=True))
    # print_graph_data(graph)


@pytest.mark.graph_creator_valid_data
def test_graph_40():
    # intersection - queue - intersection (droga jednokierunkowa)
    nodes = {
        "1": {'name': 'D2', 'pos': (1, 5), 'type': gc.base_node_type["intersection"], "poiId": "0"},
        "2": {'name': 'D2', 'pos': (3, 5), 'type': gc.base_node_type["normal"], "poiId": "0"},
        "3": {'name': 'D2', 'pos': (5, 5), 'type': gc.base_node_type["queue"], "poiId": "18"},
        "4": {'name': 'D2', 'pos': (7, 5), 'type': gc.base_node_type["intersection"], "poiId": "0"}
    }

    edges = {
        "1": {'startNode': "1", 'endNode': "2", 'type': gc.way_type["oneWay"], 'isActive': True},
        "2": {'startNode': "2", 'endNode': "3", 'type': gc.way_type["oneWay"], 'isActive': True},
        "3": {'startNode': "3", 'endNode': "4", 'type': gc.way_type["oneWay"], 'isActive': True}
    }

    pois_raw = [
        {"id": "18", "pose": (5, 5), "type": gc.base_node_type["queue"]}
    ]
    graph = gc.SupervisorGraphCreator(nodes, edges, pois_raw)
    # graph.print_graph()
    expected_pose = {
        (1 + gc.WAITING_STOP_DIST_TO_INTERSECTION, 5): 1,
        (5, 5): 1,
        (7 - gc.WAITING_STOP_DIST_TO_INTERSECTION, 5): 1
    }
    assert len(graph.graph.nodes) == get_expected_nodes(nodes, edges)
    assert len(graph.graph.edges) == get_expected_edges_intersections_and_pois(nodes, edges) + 2
    assert check_graph_position(expected_pose, graph.graph.nodes(data=True))
    # print_graph_data(graph)


@pytest.mark.graph_creator_valid_data
def test_graph_41():
    # intersection - queue - intersection (droga jednokierunkowa)
    nodes = {
        "1": {'name': 'D2', 'pos': (1, 5), 'type': gc.base_node_type["intersection"], "poiId": "0"},
        "2": {'name': 'D2', 'pos': (3, 5), 'type': gc.base_node_type["queue"], "poiId": "18"},
        "3": {'name': 'D2', 'pos': (5, 5), 'type': gc.base_node_type["normal"], "poiId": "0"},
        "4": {'name': 'D2', 'pos': (7, 5), 'type': gc.base_node_type["intersection"], "poiId": "0"}
    }

    edges = {
        "1": {'startNode': "1", 'endNode': "2", 'type': gc.way_type["oneWay"], 'isActive': True},
        "2": {'startNode': "2", 'endNode': "3", 'type': gc.way_type["oneWay"], 'isActive': True},
        "3": {'startNode': "3", 'endNode': "4", 'type': gc.way_type["oneWay"], 'isActive': True}
    }

    pois_raw = [
        {"id": "18", "pose": (3, 5), "type": gc.base_node_type["queue"]}
    ]
    graph = gc.SupervisorGraphCreator(nodes, edges, pois_raw)
    # graph.print_graph()
    expected_pose = {
        (1 + gc.WAITING_STOP_DIST_TO_INTERSECTION, 5): 1,
        (3, 5): 1,
        (7 - gc.WAITING_STOP_DIST_TO_INTERSECTION, 5): 1
    }
    assert len(graph.graph.nodes) == get_expected_nodes(nodes, edges)
    assert len(graph.graph.edges) == get_expected_edges_intersections_and_pois(nodes, edges) + 2
    assert check_graph_position(expected_pose, graph.graph.nodes(data=True))
    # print_graph_data(graph)


# ---------------------------- Testy nieprawidlowe dane ----------------------------------------- #
@pytest.mark.graph_creator_exception
def test_graph_exception_1():
    # Prawidłowa konfiguracja: skrzyzowanie - skrzyzowanie (co najmniej 3 drogi) - rozne typy drog
    nodes = {
        "1": {'name': 'D1', 'pos': (5, 5), 'type': gc.base_node_type["intersection"]},
        "2": {'name': 'D2', 'pos': (10, 5), 'type': gc.base_node_type["normal"]},
        "3": {'name': 'D3', 'pos': (15, 5), 'type': gc.base_node_type["intersection"]},
    }

    edges = {
        "1": {'startNode': "1", 'endNode': "2", 'type': gc.way_type["narrowTwoWay"], 'isActive': True},
        "2": {'startNode': "3", 'endNode': "2", 'type': gc.way_type["twoWay"], 'isActive': True},
    }

    try:
        gc.SupervisorGraphCreator(nodes, edges, [])
    except gc.GraphError:
        assert True
    else:
        assert False
    # GraphError: Different path type connected to normal nodes.


@pytest.mark.graph_creator_exception
def test_graph_exception_2():
    # Prawidłowa konfiguracja: skrzyzowanie - skrzyzowanie (co najmniej 3 drogi) - rozne typy drog
    nodes = {
        "1": {'name': 'D1', 'pos': (5, 5), 'type': gc.base_node_type["intersection"]},
        "2": {'name': 'D2', 'pos': (10, 5), 'type': gc.base_node_type["normal"]},
        "3": {'name': 'D3', 'pos': (15, 5), 'type': gc.base_node_type["intersection"]},
    }

    edges = {
        "1": {'startNode': "2", 'endNode': "1", 'type': gc.way_type["narrowTwoWay"], 'isActive': True},
        "2": {'startNode': "3", 'endNode': "2", 'type': gc.way_type["twoWay"], 'isActive': True},
    }

    try:
        gc.SupervisorGraphCreator(nodes, edges, [])
    except gc.GraphError:
        assert True
    else:
        assert False
    # GraphError: Different path type connected to normal nodes.


@pytest.mark.graph_creator_exception
def test_graph_exception_3():
    # Prawidłowa konfiguracja: skrzyzowanie - skrzyzowanie (co najmniej 3 drogi) - rozne typy drog
    nodes = {
        "1": {'name': 'D1', 'pos': (5, 5), 'type': gc.base_node_type["intersection"]},
        "2": {'name': 'D2', 'pos': (10, 5), 'type': gc.base_node_type["normal"]},
        "3": {'name': 'D3', 'pos': (15, 5), 'type': gc.base_node_type["intersection"]},
    }

    edges = {
        "1": {'startNode': "1", 'endNode': "2", 'type': gc.way_type["oneWay"], 'isActive': True},
        "2": {'startNode': "3", 'endNode': "2", 'type': gc.way_type["twoWay"], 'isActive': True},
    }

    try:
        gc.SupervisorGraphCreator(nodes, edges, [])
    except gc.GraphError:
        assert True
    else:
        assert False
    # GraphError: Different path type connected to normal nodes.


@pytest.mark.graph_creator_exception
def test_graph_exception_4():
    # Prawidłowa konfiguracja: skrzyzowanie - skrzyzowanie (co najmniej 3 drogi) - rozne typy drog
    nodes = {
        "1": {'name': 'D1', 'pos': (5, 5), 'type': gc.base_node_type["intersection"]},
        "2": {'name': 'D2', 'pos': (10, 5), 'type': gc.base_node_type["normal"]},
        "3": {'name': 'D3', 'pos': (15, 5), 'type': gc.base_node_type["intersection"]},
    }

    edges = {
        "1": {'startNode': "2", 'endNode': "1", 'type': gc.way_type["oneWay"], 'isActive': True},
        "2": {'startNode': "3", 'endNode': "2", 'type': gc.way_type["twoWay"], 'isActive': True},
    }

    try:
        gc.SupervisorGraphCreator(nodes, edges, [])
    except gc.GraphError:
        assert True
    else:
        assert False
    # GraphError: Normal nodes error. Path contains normal nodes should start and end from different type of node.


@pytest.mark.graph_creator_exception
def test_graph_exception_5():
    # Prawidłowa konfiguracja: skrzyzowanie - skrzyzowanie (co najmniej 3 drogi) - rozne typy drog
    nodes = {
        "1": {'name': 'D1', 'pos': (5, 5), 'type': gc.base_node_type["intersection"]},
        "2": {'name': 'D2', 'pos': (10, 5), 'type': gc.base_node_type["normal"]},
        "3": {'name': 'D3', 'pos': (15, 5), 'type': gc.base_node_type["intersection"]},
    }

    edges = {
        "1": {'startNode': "1", 'endNode': "2", 'type': gc.way_type["narrowTwoWay"], 'isActive': True},
        "2": {'startNode': "3", 'endNode': "2", 'type': gc.way_type["oneWay"], 'isActive': True},
    }

    try:
        gc.SupervisorGraphCreator(nodes, edges, [])
    except gc.GraphError:
        assert True
    else:
        assert False
    # GraphError: Path contains normal nodes should be end different type of nodes.


@pytest.mark.graph_creator_exception
def test_graph_exception_6():
    # Prawidłowa konfiguracja: skrzyzowanie - skrzyzowanie (co najmniej 3 drogi) - rozne typy drog
    nodes = {
        "1": {'name': 'D1', 'pos': (5, 5), 'type': gc.base_node_type["intersection"]},
        "2": {'name': 'D2', 'pos': (10, 5), 'type': gc.base_node_type["normal"]},
        "3": {'name': 'D3', 'pos': (15, 5), 'type': gc.base_node_type["intersection"]},
    }

    edges = {
        "1": {'startNode': "2", 'endNode': "1", 'type': gc.way_type["narrowTwoWay"], 'isActive': True},
        "2": {'startNode': "3", 'endNode': "2", 'type': gc.way_type["oneWay"], 'isActive': True},
    }

    try:
        gc.SupervisorGraphCreator(nodes, edges, [])
    except gc.GraphError:
        assert True
    else:
        assert False
    # GraphError: Path contains normal nodes should be end different type of nodes.


@pytest.mark.graph_creator_exception
def test_graph_exception_7():
    # Prawidłowa konfiguracja: skrzyzowanie - skrzyzowanie (co najmniej 3 drogi) - rozne typy drog
    nodes = {
        "1": {'name': 'D1', 'pos': (5, 5), 'type': gc.base_node_type["intersection"]},
        "2": {'name': 'D2', 'pos': (10, 5), 'type': gc.base_node_type["normal"]},
        "3": {'name': 'D3', 'pos': (15, 5), 'type': gc.base_node_type["intersection"]},
    }

    edges = {
        "1": {'startNode': "1", 'endNode': "2", 'type': gc.way_type["narrowTwoWay"], 'isActive': True},
        "2": {'startNode': "2", 'endNode': "3", 'type': gc.way_type["oneWay"], 'isActive': True},
    }

    try:
        gc.SupervisorGraphCreator(nodes, edges, [])
    except gc.GraphError:
        assert True
    else:
        assert False
    # GraphError: Normal nodes error. Path contains normal nodes should start and end from different type of node.


@pytest.mark.graph_creator_exception
def test_graph_exception_8():
    # Prawidłowa konfiguracja: skrzyzowanie - skrzyzowanie (co najmniej 3 drogi) - rozne typy drog
    nodes = {
        "1": {'name': 'D1', 'pos': (5, 5), 'type': gc.base_node_type["intersection"]},
        "2": {'name': 'D2', 'pos': (10, 5), 'type': gc.base_node_type["normal"]},
        "3": {'name': 'D3', 'pos': (15, 5), 'type': gc.base_node_type["intersection"]},
    }

    edges = {
        "1": {'startNode': "1", 'endNode': "2", 'type': gc.way_type["oneWay"], 'isActive': True},
        "2": {'startNode': "3", 'endNode': "2", 'type': gc.way_type["oneWay"], 'isActive': True},
    }

    try:
        gc.SupervisorGraphCreator(nodes, edges, [])
    except gc.GraphError:
        assert True
    else:
        assert False
    # GraphError: Path contains normal nodes should be end different type of nodes.


@pytest.mark.graph_creator_exception
def test_graph_exception_9():
    # Prawidłowa konfiguracja: pomiedzy stanowiskami z dokowaniem
    # (intersection - waiting - poi - departure - intersection) - one way
    nodes = {
        "1": {'name': 'D2', 'pos': (1, 5), 'type': gc.base_node_type["intersection"]},
        "2": {'name': 'D2', 'pos': (3, 5), 'type': gc.base_node_type["waiting"]},
        "3": {'name': 'D2', 'pos': (6, 5), 'type': gc.base_node_type["load-unload-dock"]},
        "4": {'name': 'D2', 'pos': (9, 5), 'type': gc.base_node_type["departure"]},
        "5": {'name': 'D2', 'pos': (12, 5), 'type': gc.base_node_type["intersection"]},
    }

    edges = {
        "1": {'startNode': "1", 'endNode': "2", 'type': gc.way_type["twoWay"], 'isActive': True},
        "2": {'startNode': "2", 'endNode': "3", 'type': gc.way_type["oneWay"], 'isActive': True},
        "3": {'startNode': "3", 'endNode': "4", 'type': gc.way_type["oneWay"], 'isActive': True},
        "4": {'startNode': "4", 'endNode': "5", 'type': gc.way_type["oneWay"], 'isActive': True}
    }

    try:
        gc.SupervisorGraphCreator(nodes, edges, [])
    except gc.GraphError:
        assert True
    else:
        assert False
    # GraphError: Only one POI node should be connected as output with waiting node.


@pytest.mark.graph_creator_exception
def test_graph_exception_10():
    # Prawidłowa konfiguracja: pomiedzy stanowiskami z dokowaniem
    # (intersection - waiting - poi - departure - intersection) - one way
    nodes = {
        "1": {'name': 'D2', 'pos': (1, 5), 'type': gc.base_node_type["intersection"]},
        "2": {'name': 'D2', 'pos': (3, 5), 'type': gc.base_node_type["waiting"]},
        "3": {'name': 'D2', 'pos': (6, 5), 'type': gc.base_node_type["load-unload-dock"]},
        "4": {'name': 'D2', 'pos': (9, 5), 'type': gc.base_node_type["departure"]},
        "5": {'name': 'D2', 'pos': (12, 5), 'type': gc.base_node_type["intersection"]},
    }

    edges = {
        "1": {'startNode': "1", 'endNode': "2", 'type': gc.way_type["oneWay"], 'isActive': True},
        "2": {'startNode': "2", 'endNode': "3", 'type': gc.way_type["twoWay"], 'isActive': True},
        "3": {'startNode': "3", 'endNode': "4", 'type': gc.way_type["oneWay"], 'isActive': True},
        "4": {'startNode': "4", 'endNode': "5", 'type': gc.way_type["oneWay"], 'isActive': True}
    }

    try:
        gc.SupervisorGraphCreator(nodes, edges, [])
    except gc.GraphError:
        assert True
    else:
        assert False
    # GraphError: Only one departure/waiting-departure POI should be connected with POI.


@pytest.mark.graph_creator_exception
def test_graph_exception_11():
    # Prawidłowa konfiguracja: pomiedzy stanowiskami z dokowaniem
    # (intersection - waiting - poi - departure - intersection) - one way
    nodes = {
        "1": {'name': 'D2', 'pos': (1, 5), 'type': gc.base_node_type["intersection"]},
        "2": {'name': 'D2', 'pos': (3, 5), 'type': gc.base_node_type["waiting"]},
        "3": {'name': 'D2', 'pos': (6, 5), 'type': gc.base_node_type["load-unload-dock"]},
        "4": {'name': 'D2', 'pos': (9, 5), 'type': gc.base_node_type["departure"]},
        "5": {'name': 'D2', 'pos': (12, 5), 'type': gc.base_node_type["intersection"]},
    }

    edges = {
        "1": {'startNode': "1", 'endNode': "2", 'type': gc.way_type["oneWay"], 'isActive': True},
        "2": {'startNode': "2", 'endNode': "3", 'type': gc.way_type["oneWay"], 'isActive': True},
        "3": {'startNode': "3", 'endNode': "4", 'type': gc.way_type["twoWay"], 'isActive': True},
        "4": {'startNode': "4", 'endNode': "5", 'type': gc.way_type["oneWay"], 'isActive': True}
    }

    try:
        gc.SupervisorGraphCreator(nodes, edges, [])
    except gc.GraphError:
        assert True
    else:
        assert False
    # GraphError: Only one waiting/waiting-departure POI should be connected with POI.


@pytest.mark.graph_creator_exception
def test_graph_exception_12():
    # Prawidłowa konfiguracja: pomiedzy stanowiskami z dokowaniem
    # (intersection - waiting - poi - departure - intersection) - one way
    nodes = {
        "1": {'name': 'D2', 'pos': (1, 5), 'type': gc.base_node_type["intersection"]},
        "2": {'name': 'D2', 'pos': (3, 5), 'type': gc.base_node_type["waiting"]},
        "3": {'name': 'D2', 'pos': (6, 5), 'type': gc.base_node_type["load-unload-dock"]},
        "4": {'name': 'D2', 'pos': (9, 5), 'type': gc.base_node_type["departure"]},
        "5": {'name': 'D2', 'pos': (12, 5), 'type': gc.base_node_type["intersection"]},
    }

    edges = {
        "1": {'startNode': "1", 'endNode': "2", 'type': gc.way_type["oneWay"], 'isActive': True},
        "2": {'startNode': "2", 'endNode': "3", 'type': gc.way_type["oneWay"], 'isActive': True},
        "3": {'startNode': "3", 'endNode': "4", 'type': gc.way_type["oneWay"], 'isActive': True},
        "4": {'startNode': "4", 'endNode': "5", 'type': gc.way_type["twoWay"], 'isActive': True}
    }

    try:
        gc.SupervisorGraphCreator(nodes, edges, [])
    except gc.GraphError:
        assert True
    else:
        assert False
    # GraphError: Only one POI node should be connected as input with departure node.


@pytest.mark.graph_creator_exception
def test_graph_exception_13():
    # Prawidłowa konfiguracja: pomiedzy stanowiskami z dokowaniem
    # (intersection - waiting - poi - departure - intersection) - one way
    nodes = {
        "1": {'name': 'D2', 'pos': (1, 5), 'type': gc.base_node_type["intersection"]},
        "2": {'name': 'D2', 'pos': (3, 5), 'type': gc.base_node_type["waiting"]},
        "3": {'name': 'D2', 'pos': (6, 5), 'type': gc.base_node_type["load-unload-dock"]},
        "4": {'name': 'D2', 'pos': (9, 5), 'type': gc.base_node_type["departure"]},
        "5": {'name': 'D2', 'pos': (12, 5), 'type': gc.base_node_type["intersection"]},
    }

    edges = {
        "1": {'startNode': "1", 'endNode': "2", 'type': gc.way_type["narrowTwoWay"], 'isActive': True},
        "2": {'startNode': "2", 'endNode': "3", 'type': gc.way_type["oneWay"], 'isActive': True},
        "3": {'startNode': "3", 'endNode': "4", 'type': gc.way_type["oneWay"], 'isActive': True},
        "4": {'startNode': "4", 'endNode': "5", 'type': gc.way_type["oneWay"], 'isActive': True}
    }

    try:
        gc.SupervisorGraphCreator(nodes, edges, [])
    except gc.GraphError:
        assert True
    else:
        assert False
    # GraphError: Only one POI node should be connected as output with waiting node.


@pytest.mark.graph_creator_exception
def test_graph_exception_14():
    # Prawidłowa konfiguracja: pomiedzy stanowiskami z dokowaniem
    # (intersection - waiting - poi - departure - intersection) - one way
    nodes = {
        "1": {'name': 'D2', 'pos': (1, 5), 'type': gc.base_node_type["intersection"]},
        "2": {'name': 'D2', 'pos': (3, 5), 'type': gc.base_node_type["waiting"]},
        "3": {'name': 'D2', 'pos': (6, 5), 'type': gc.base_node_type["load-unload-dock"]},
        "4": {'name': 'D2', 'pos': (9, 5), 'type': gc.base_node_type["departure"]},
        "5": {'name': 'D2', 'pos': (12, 5), 'type': gc.base_node_type["intersection"]},
    }

    edges = {
        "1": {'startNode': "1", 'endNode': "2", 'type': gc.way_type["oneWay"], 'isActive': True},
        "2": {'startNode': "2", 'endNode': "3", 'type': gc.way_type["narrowTwoWay"], 'isActive': True},
        "3": {'startNode': "3", 'endNode': "4", 'type': gc.way_type["oneWay"], 'isActive': True},
        "4": {'startNode': "4", 'endNode': "5", 'type': gc.way_type["oneWay"], 'isActive': True}
    }

    try:
        gc.SupervisorGraphCreator(nodes, edges, [])
    except gc.GraphError:
        assert True
    else:
        assert False
    # GraphError: Only one departure/waiting-departure POI should be connected with POI.


@pytest.mark.graph_creator_exception
def test_graph_exception_15():
    # Prawidłowa konfiguracja: pomiedzy stanowiskami z dokowaniem
    # (intersection - waiting - poi - departure - intersection) - one way
    nodes = {
        "1": {'name': 'D2', 'pos': (1, 5), 'type': gc.base_node_type["intersection"]},
        "2": {'name': 'D2', 'pos': (3, 5), 'type': gc.base_node_type["waiting"]},
        "3": {'name': 'D2', 'pos': (6, 5), 'type': gc.base_node_type["load-unload-dock"]},
        "4": {'name': 'D2', 'pos': (9, 5), 'type': gc.base_node_type["departure"]},
        "5": {'name': 'D2', 'pos': (12, 5), 'type': gc.base_node_type["intersection"]},
    }

    edges = {
        "1": {'startNode': "1", 'endNode': "2", 'type': gc.way_type["oneWay"], 'isActive': True},
        "2": {'startNode': "2", 'endNode': "3", 'type': gc.way_type["oneWay"], 'isActive': True},
        "3": {'startNode': "3", 'endNode': "4", 'type': gc.way_type["narrowTwoWay"], 'isActive': True},
        "4": {'startNode': "4", 'endNode': "5", 'type': gc.way_type["oneWay"], 'isActive': True}
    }

    try:
        gc.SupervisorGraphCreator(nodes, edges, [])
    except gc.GraphError:
        assert True
    else:
        assert False
    # GraphError: Only one waiting/waiting-departure POI should be connected with POI.


@pytest.mark.graph_creator_exception
def test_graph_exception_16():
    # Prawidłowa konfiguracja: pomiedzy stanowiskami z dokowaniem
    # (intersection - waiting - poi - departure - intersection) - one way
    nodes = {
        "1": {'name': 'D2', 'pos': (1, 5), 'type': gc.base_node_type["intersection"]},
        "2": {'name': 'D2', 'pos': (3, 5), 'type': gc.base_node_type["waiting"]},
        "3": {'name': 'D2', 'pos': (6, 5), 'type': gc.base_node_type["load-unload-dock"]},
        "4": {'name': 'D2', 'pos': (9, 5), 'type': gc.base_node_type["departure"]},
        "5": {'name': 'D2', 'pos': (12, 5), 'type': gc.base_node_type["intersection"]},
    }

    edges = {
        "1": {'startNode': "1", 'endNode': "2", 'type': gc.way_type["oneWay"], 'isActive': True},
        "2": {'startNode': "2", 'endNode': "3", 'type': gc.way_type["oneWay"], 'isActive': True},
        "3": {'startNode': "3", 'endNode': "4", 'type': gc.way_type["oneWay"], 'isActive': True},
        "4": {'startNode': "4", 'endNode': "5", 'type': gc.way_type["narrowTwoWay"], 'isActive': True}
    }

    try:
        gc.SupervisorGraphCreator(nodes, edges, [])
    except gc.GraphError:
        assert True
    else:
        assert False
    # GraphError: Only one POI node should be connected as input with departure node.


@pytest.mark.graph_creator_exception
def test_graph_exception_17():
    # Prawidłowa konfiguracja: pomiedzy stanowiskami z dokowaniem
    # (intersection - waiting - poi - departure - intersection) - one way
    nodes = {
        "1": {'name': 'D2', 'pos': (1, 5), 'type': gc.base_node_type["intersection"]},
        "2": {'name': 'D2', 'pos': (1, 5), 'type': gc.base_node_type["normal"]},
        "3": {'name': 'D2', 'pos': (3, 5), 'type': gc.base_node_type["waiting"]},
        "4": {'name': 'D2', 'pos': (6, 5), 'type': gc.base_node_type["load-unload-dock"]},
        "5": {'name': 'D2', 'pos': (9, 5), 'type': gc.base_node_type["departure"]},
        "6": {'name': 'D2', 'pos': (12, 5), 'type': gc.base_node_type["intersection"]}
    }

    edges = {
        "1": {'startNode': "1", 'endNode': "2", 'type': gc.way_type["twoWay"], 'isActive': True},
        "2": {'startNode': "2", 'endNode': "3", 'type': gc.way_type["oneWay"], 'isActive': True},
        "3": {'startNode': "3", 'endNode': "4", 'type': gc.way_type["oneWay"], 'isActive': True},
        "4": {'startNode': "4", 'endNode': "5", 'type': gc.way_type["oneWay"], 'isActive': True},
        "5": {'startNode': "5", 'endNode': "6", 'type': gc.way_type["oneWay"], 'isActive': True}

    }

    try:
        gc.SupervisorGraphCreator(nodes, edges, [])
    except gc.GraphError:
        assert True
    else:
        assert False
    # GraphError: Normal nodes error. Path contains normal nodes should start and end from different type of node.


@pytest.mark.graph_creator_exception
def test_graph_exception_18():
    # Prawidłowa konfiguracja: pomiedzy stanowiskami z dokowaniem
    # (intersection - waiting - poi - departure - intersection) - one way
    nodes = {
        "1": {'name': 'D2', 'pos': (1, 5), 'type': gc.base_node_type["intersection"]},
        "2": {'name': 'D2', 'pos': (1, 5), 'type': gc.base_node_type["normal"]},
        "3": {'name': 'D2', 'pos': (3, 5), 'type': gc.base_node_type["waiting"]},
        "4": {'name': 'D2', 'pos': (6, 5), 'type': gc.base_node_type["load-unload-dock"]},
        "5": {'name': 'D2', 'pos': (9, 5), 'type': gc.base_node_type["departure"]},
        "6": {'name': 'D2', 'pos': (12, 5), 'type': gc.base_node_type["intersection"]}
    }

    edges = {
        "1": {'startNode': "1", 'endNode': "2", 'type': gc.way_type["narrowTwoWay"], 'isActive': True},
        "2": {'startNode': "2", 'endNode': "3", 'type': gc.way_type["oneWay"], 'isActive': True},
        "3": {'startNode': "3", 'endNode': "4", 'type': gc.way_type["oneWay"], 'isActive': True},
        "4": {'startNode': "4", 'endNode': "5", 'type': gc.way_type["oneWay"], 'isActive': True},
        "5": {'startNode': "5", 'endNode': "6", 'type': gc.way_type["oneWay"], 'isActive': True}
    }

    try:
        gc.SupervisorGraphCreator(nodes, edges, [])
    except gc.GraphError:
        assert True
    else:
        assert False
    # GraphError: Normal nodes error. Path contains normal nodes should start and end from different type of node.


@pytest.mark.graph_creator_exception
def test_graph_exception_19():
    # Prawidłowa konfiguracja: pomiedzy stanowiskami z dokowaniem
    # (intersection - waiting - poi - departure - intersection) - one way
    nodes = {
        "1": {'name': 'D2', 'pos': (1, 5), 'type': gc.base_node_type["intersection"]},
        "2": {'name': 'D2', 'pos': (1, 5), 'type': gc.base_node_type["normal"]},
        "3": {'name': 'D2', 'pos': (3, 5), 'type': gc.base_node_type["waiting"]},
        "4": {'name': 'D2', 'pos': (6, 5), 'type': gc.base_node_type["load-unload-dock"]},
        "5": {'name': 'D2', 'pos': (9, 5), 'type': gc.base_node_type["departure"]},
        "6": {'name': 'D2', 'pos': (12, 5), 'type': gc.base_node_type["intersection"]}
    }

    edges = {
        "1": {'startNode': "1", 'endNode': "2", 'type': gc.way_type["oneWay"], 'isActive': True},
        "2": {'startNode': "2", 'endNode': "3", 'type': gc.way_type["twoWay"], 'isActive': True},
        "3": {'startNode': "3", 'endNode': "4", 'type': gc.way_type["oneWay"], 'isActive': True},
        "4": {'startNode': "4", 'endNode': "5", 'type': gc.way_type["oneWay"], 'isActive': True},
        "5": {'startNode': "5", 'endNode': "6", 'type': gc.way_type["oneWay"], 'isActive': True}
    }

    try:
        gc.SupervisorGraphCreator(nodes, edges, [])
    except gc.GraphError:
        assert True
    else:
        assert False
    # GraphError: Different path type connected to normal nodes.


@pytest.mark.graph_creator_exception
def test_graph_exception_20():
    # Prawidłowa konfiguracja: pomiedzy stanowiskami z dokowaniem
    # (intersection - waiting - poi - departure - intersection) - one way
    nodes = {
        "1": {'name': 'D2', 'pos': (1, 5), 'type': gc.base_node_type["intersection"]},
        "2": {'name': 'D2', 'pos': (1, 5), 'type': gc.base_node_type["normal"]},
        "3": {'name': 'D2', 'pos': (3, 5), 'type': gc.base_node_type["waiting"]},
        "4": {'name': 'D2', 'pos': (6, 5), 'type': gc.base_node_type["load-unload-dock"]},
        "5": {'name': 'D2', 'pos': (9, 5), 'type': gc.base_node_type["departure"]},
        "6": {'name': 'D2', 'pos': (12, 5), 'type': gc.base_node_type["intersection"]}
    }

    edges = {
        "1": {'startNode': "1", 'endNode': "2", 'type': gc.way_type["oneWay"], 'isActive': True},
        "2": {'startNode': "2", 'endNode': "3", 'type': gc.way_type["narrowTwoWay"], 'isActive': True},
        "3": {'startNode': "3", 'endNode': "4", 'type': gc.way_type["oneWay"], 'isActive': True},
        "4": {'startNode': "4", 'endNode': "5", 'type': gc.way_type["oneWay"], 'isActive': True},
        "5": {'startNode': "5", 'endNode': "6", 'type': gc.way_type["oneWay"], 'isActive': True}
    }

    try:
        gc.SupervisorGraphCreator(nodes, edges, [])
    except gc.GraphError:
        assert True
    else:
        assert False
    # GraphError: Different path type connected to normal nodes.


@pytest.mark.graph_creator_exception
def test_graph_exception_21():
    # Prawidłowa konfiguracja: pomiedzy stanowiskami z dokowaniem
    # (intersection - waiting - poi - departure - intersection) - one way
    nodes = {
        "1": {'name': 'D2', 'pos': (1, 5), 'type': gc.base_node_type["intersection"]},
        "2": {'name': 'D2', 'pos': (3, 5), 'type': gc.base_node_type["waiting"]},
        "3": {'name': 'D2', 'pos': (1, 5), 'type': gc.base_node_type["normal"]},
        "4": {'name': 'D2', 'pos': (6, 5), 'type': gc.base_node_type["load-unload-dock"]},
        "5": {'name': 'D2', 'pos': (9, 5), 'type': gc.base_node_type["departure"]},
        "6": {'name': 'D2', 'pos': (12, 5), 'type': gc.base_node_type["intersection"]}
    }

    edges = {
        "1": {'startNode': "1", 'endNode': "2", 'type': gc.way_type["oneWay"], 'isActive': True},
        "2": {'startNode': "2", 'endNode': "3", 'type': gc.way_type["twoWay"], 'isActive': True},
        "3": {'startNode': "3", 'endNode': "4", 'type': gc.way_type["oneWay"], 'isActive': True},
        "4": {'startNode': "4", 'endNode': "5", 'type': gc.way_type["oneWay"], 'isActive': True},
        "5": {'startNode': "5", 'endNode': "6", 'type': gc.way_type["oneWay"], 'isActive': True}
    }

    try:
        gc.SupervisorGraphCreator(nodes, edges, [])
    except gc.GraphError:
        assert True
    else:
        assert False
    # GraphError: Normal nodes error. Path contains normal nodes should start and end from different type of node.


@pytest.mark.graph_creator_exception
def test_graph_exception_23():
    # Prawidłowa konfiguracja: pomiedzy stanowiskami z dokowaniem
    # (intersection - waiting - poi - departure - intersection) - one way
    nodes = {
        "1": {'name': 'D2', 'pos': (1, 5), 'type': gc.base_node_type["intersection"]},
        "2": {'name': 'D2', 'pos': (3, 5), 'type': gc.base_node_type["waiting"]},
        "3": {'name': 'D2', 'pos': (1, 5), 'type': gc.base_node_type["normal"]},
        "4": {'name': 'D2', 'pos': (6, 5), 'type': gc.base_node_type["load-unload-dock"]},
        "5": {'name': 'D2', 'pos': (9, 5), 'type': gc.base_node_type["departure"]},
        "6": {'name': 'D2', 'pos': (12, 5), 'type': gc.base_node_type["intersection"]}
    }

    edges = {
        "1": {'startNode': "1", 'endNode': "2", 'type': gc.way_type["oneWay"], 'isActive': True},
        "2": {'startNode': "2", 'endNode': "3", 'type': gc.way_type["narrowTwoWay"], 'isActive': True},
        "3": {'startNode': "3", 'endNode': "4", 'type': gc.way_type["oneWay"], 'isActive': True},
        "4": {'startNode': "4", 'endNode': "5", 'type': gc.way_type["oneWay"], 'isActive': True},
        "5": {'startNode': "5", 'endNode': "6", 'type': gc.way_type["oneWay"], 'isActive': True}
    }

    try:
        gc.SupervisorGraphCreator(nodes, edges, [])
    except gc.GraphError:
        assert True
    else:
        assert False
    # GraphError: Normal nodes error. Path contains normal nodes should start and end from different type of node.


@pytest.mark.graph_creator_exception
def test_graph_exception_24():
    # Prawidłowa konfiguracja: pomiedzy stanowiskami z dokowaniem
    # (intersection - waiting - poi - departure - intersection) - one way
    nodes = {
        "1": {'name': 'D2', 'pos': (1, 5), 'type': gc.base_node_type["intersection"]},
        "2": {'name': 'D2', 'pos': (3, 5), 'type': gc.base_node_type["waiting"]},
        "3": {'name': 'D2', 'pos': (1, 5), 'type': gc.base_node_type["normal"]},
        "4": {'name': 'D2', 'pos': (6, 5), 'type': gc.base_node_type["load-unload-dock"]},
        "5": {'name': 'D2', 'pos': (9, 5), 'type': gc.base_node_type["departure"]},
        "6": {'name': 'D2', 'pos': (12, 5), 'type': gc.base_node_type["intersection"]}
    }

    edges = {
        "1": {'startNode': "1", 'endNode': "2", 'type': gc.way_type["oneWay"], 'isActive': True},
        "2": {'startNode': "2", 'endNode': "3", 'type': gc.way_type["oneWay"], 'isActive': True},
        "3": {'startNode': "3", 'endNode': "4", 'type': gc.way_type["twoWay"], 'isActive': True},
        "4": {'startNode': "4", 'endNode': "5", 'type': gc.way_type["oneWay"], 'isActive': True},
        "5": {'startNode': "5", 'endNode': "6", 'type': gc.way_type["oneWay"], 'isActive': True}
    }

    try:
        gc.SupervisorGraphCreator(nodes, edges, [])
    except gc.GraphError:
        assert True
    else:
        assert False
    # GraphError: Different path type connected to normal nodes.


@pytest.mark.graph_creator_exception
def test_graph_exception_25():
    # Prawidłowa konfiguracja: pomiedzy stanowiskami z dokowaniem
    # (intersection - waiting - poi - departure - intersection) - one way
    nodes = {
        "1": {'name': 'D2', 'pos': (1, 5), 'type': gc.base_node_type["intersection"]},
        "2": {'name': 'D2', 'pos': (3, 5), 'type': gc.base_node_type["waiting"]},
        "3": {'name': 'D2', 'pos': (6, 5), 'type': gc.base_node_type["load-unload-dock"]},
        "4": {'name': 'D2', 'pos': (1, 5), 'type': gc.base_node_type["normal"]},
        "5": {'name': 'D2', 'pos': (9, 5), 'type': gc.base_node_type["departure"]},
        "6": {'name': 'D2', 'pos': (12, 5), 'type': gc.base_node_type["intersection"]}
    }

    edges = {
        "1": {'startNode': "1", 'endNode': "2", 'type': gc.way_type["oneWay"], 'isActive': True},
        "2": {'startNode': "2", 'endNode': "3", 'type': gc.way_type["oneWay"], 'isActive': True},
        "3": {'startNode': "3", 'endNode': "4", 'type': gc.way_type["twoWay"], 'isActive': True},
        "4": {'startNode': "4", 'endNode': "5", 'type': gc.way_type["oneWay"], 'isActive': True},
        "5": {'startNode': "5", 'endNode': "6", 'type': gc.way_type["oneWay"], 'isActive': True}
    }

    try:
        gc.SupervisorGraphCreator(nodes, edges, [])
    except gc.GraphError:
        assert True
    else:
        assert False
    # GraphError: Normal nodes error. Path contains normal nodes should start and end from different type of node.


@pytest.mark.graph_creator_exception
def test_graph_exception_26():
    # Prawidłowa konfiguracja: pomiedzy stanowiskami z dokowaniem
    # (intersection - waiting - poi - departure - intersection) - one way
    nodes = {
        "1": {'name': 'D2', 'pos': (1, 5), 'type': gc.base_node_type["intersection"]},
        "2": {'name': 'D2', 'pos': (3, 5), 'type': gc.base_node_type["waiting"]},
        "3": {'name': 'D2', 'pos': (6, 5), 'type': gc.base_node_type["load-unload-dock"]},
        "4": {'name': 'D2', 'pos': (1, 5), 'type': gc.base_node_type["normal"]},
        "5": {'name': 'D2', 'pos': (9, 5), 'type': gc.base_node_type["departure"]},
        "6": {'name': 'D2', 'pos': (12, 5), 'type': gc.base_node_type["intersection"]}
    }

    edges = {
        "1": {'startNode': "1", 'endNode': "2", 'type': gc.way_type["oneWay"], 'isActive': True},
        "2": {'startNode': "2", 'endNode': "3", 'type': gc.way_type["oneWay"], 'isActive': True},
        "3": {'startNode': "3", 'endNode': "4", 'type': gc.way_type["narrowTwoWay"], 'isActive': True},
        "4": {'startNode': "4", 'endNode': "5", 'type': gc.way_type["oneWay"], 'isActive': True},
        "5": {'startNode': "5", 'endNode': "6", 'type': gc.way_type["oneWay"], 'isActive': True}
    }

    try:
        gc.SupervisorGraphCreator(nodes, edges, [])
    except gc.GraphError:
        assert True
    else:
        assert False
    # GraphError: Normal nodes error. Path contains normal nodes should start and end from different type of node.


@pytest.mark.graph_creator_exception
def test_graph_exception_27():
    # Prawidłowa konfiguracja: pomiedzy stanowiskami z dokowaniem
    # (intersection - waiting - poi - departure - intersection) - one way
    nodes = {
        "1": {'name': 'D2', 'pos': (1, 5), 'type': gc.base_node_type["intersection"]},
        "2": {'name': 'D2', 'pos': (3, 5), 'type': gc.base_node_type["waiting"]},
        "3": {'name': 'D2', 'pos': (6, 5), 'type': gc.base_node_type["load-unload-dock"]},
        "4": {'name': 'D2', 'pos': (1, 5), 'type': gc.base_node_type["normal"]},
        "5": {'name': 'D2', 'pos': (9, 5), 'type': gc.base_node_type["departure"]},
        "6": {'name': 'D2', 'pos': (12, 5), 'type': gc.base_node_type["intersection"]}
    }

    edges = {
        "1": {'startNode': "1", 'endNode': "2", 'type': gc.way_type["oneWay"], 'isActive': True},
        "2": {'startNode': "2", 'endNode': "3", 'type': gc.way_type["oneWay"], 'isActive': True},
        "3": {'startNode': "3", 'endNode': "4", 'type': gc.way_type["oneWay"], 'isActive': True},
        "4": {'startNode': "4", 'endNode': "5", 'type': gc.way_type["twoWay"], 'isActive': True},
        "5": {'startNode': "5", 'endNode': "6", 'type': gc.way_type["oneWay"], 'isActive': True}
    }

    try:
        gc.SupervisorGraphCreator(nodes, edges, [])
    except gc.GraphError:
        assert True
    else:
        assert False
    # GraphError: Different path type connected to normal nodes.


@pytest.mark.graph_creator_exception
def test_graph_exception_28():
    # Prawidłowa konfiguracja: pomiedzy stanowiskami z dokowaniem
    # (intersection - waiting - poi - departure - intersection) - one way
    nodes = {
        "1": {'name': 'D2', 'pos': (1, 5), 'type': gc.base_node_type["intersection"]},
        "2": {'name': 'D2', 'pos': (3, 5), 'type': gc.base_node_type["waiting"]},
        "3": {'name': 'D2', 'pos': (6, 5), 'type': gc.base_node_type["load-unload-dock"]},
        "4": {'name': 'D2', 'pos': (1, 5), 'type': gc.base_node_type["normal"]},
        "5": {'name': 'D2', 'pos': (9, 5), 'type': gc.base_node_type["departure"]},
        "6": {'name': 'D2', 'pos': (12, 5), 'type': gc.base_node_type["intersection"]}
    }

    edges = {
        '1': {'startNode': "1", 'endNode': "2", 'type': gc.way_type["oneWay"], 'isActive': True},
        '2': {'startNode': "2", 'endNode': "3", 'type': gc.way_type["oneWay"], 'isActive': True},
        '3': {'startNode': "3", 'endNode': "4", 'type': gc.way_type["oneWay"], 'isActive': True},
        '4': {'startNode': "4", 'endNode': "5", 'type': gc.way_type["narrowTwoWay"], 'isActive': True},
        "5": {'startNode': "5", 'endNode': "6", 'type': gc.way_type["oneWay"], 'isActive': True}
    }

    try:
        gc.SupervisorGraphCreator(nodes, edges, [])
    except gc.GraphError:
        assert True
    else:
        assert False
    # GraphError: Different path type connected to normal nodes.


@pytest.mark.graph_creator_exception
def test_graph_exception_29():
    # Prawidłowa konfiguracja: pomiedzy stanowiskami z dokowaniem
    # (intersection - waiting - poi - departure - intersection) - one way
    nodes = {
        "1": {'name': 'D2', 'pos': (1, 5), 'type': gc.base_node_type["intersection"]},
        "2": {'name': 'D2', 'pos': (3, 5), 'type': gc.base_node_type["waiting"]},
        "3": {'name': 'D2', 'pos': (6, 5), 'type': gc.base_node_type["load-unload-dock"]},
        "4": {'name': 'D2', 'pos': (9, 5), 'type': gc.base_node_type["departure"]},
        "5": {'name': 'D2', 'pos': (1, 5), 'type': gc.base_node_type["normal"]},
        "6": {'name': 'D2', 'pos': (12, 5), 'type': gc.base_node_type["intersection"]}
    }

    edges = {
        "1": {'startNode': "1", 'endNode': "2", 'type': gc.way_type["oneWay"], 'isActive': True},
        "2": {'startNode': "2", 'endNode': "3", 'type': gc.way_type["oneWay"], 'isActive': True},
        "3": {'startNode': "3", 'endNode': "4", 'type': gc.way_type["oneWay"], 'isActive': True},
        "4": {'startNode': "4", 'endNode': "5", 'type': gc.way_type["twoWay"], 'isActive': True},
        "5": {'startNode': "5", 'endNode': "6", 'type': gc.way_type["oneWay"], 'isActive': True}
    }

    try:
        gc.SupervisorGraphCreator(nodes, edges, [])
    except gc.GraphError:
        assert True
    else:
        assert False
    # GraphError: Normal nodes error. Path contains normal nodes should start and end from different type of node.


@pytest.mark.graph_creator_exception
def test_graph_exception_30():
    # Prawidłowa konfiguracja: pomiedzy stanowiskami z dokowaniem
    # (intersection - waiting - poi - departure - intersection) - one way
    nodes = {
        "1": {'name': 'D2', 'pos': (1, 5), 'type': gc.base_node_type["intersection"]},
        "2": {'name': 'D2', 'pos': (3, 5), 'type': gc.base_node_type["waiting"]},
        "3": {'name': 'D2', 'pos': (6, 5), 'type': gc.base_node_type["load-unload-dock"]},
        "4": {'name': 'D2', 'pos': (9, 5), 'type': gc.base_node_type["departure"]},
        "5": {'name': 'D2', 'pos': (1, 5), 'type': gc.base_node_type["normal"]},
        "6": {'name': 'D2', 'pos': (12, 5), 'type': gc.base_node_type["intersection"]}
    }

    edges = {
        "1": {'startNode': "1", 'endNode': "2", 'type': gc.way_type["oneWay"], 'isActive': True},
        "2": {'startNode': "2", 'endNode': "3", 'type': gc.way_type["oneWay"], 'isActive': True},
        "3": {'startNode': "3", 'endNode': "4", 'type': gc.way_type["oneWay"], 'isActive': True},
        "4": {'startNode': "4", 'endNode': "5", 'type': gc.way_type["narrowTwoWay"], 'isActive': True},
        "5": {'startNode': "5", 'endNode': "6", 'type': gc.way_type["oneWay"], 'isActive': True}
    }

    try:
        gc.SupervisorGraphCreator(nodes, edges, [])
    except gc.GraphError:
        assert True
    else:
        assert False
    # GraphError: Normal nodes error. Path contains normal nodes should start and end from different type of node.


@pytest.mark.graph_creator_exception
def test_graph_exception_31():
    # Prawidłowa konfiguracja: pomiedzy stanowiskami z dokowaniem
    # (intersection - waiting - poi - departure - intersection) - one way
    nodes = {
        "1": {'name': 'D2', 'pos': (1, 5), 'type': gc.base_node_type["intersection"]},
        "2": {'name': 'D2', 'pos': (3, 5), 'type': gc.base_node_type["waiting"]},
        "3": {'name': 'D2', 'pos': (6, 5), 'type': gc.base_node_type["load-unload-dock"]},
        "4": {'name': 'D2', 'pos': (9, 5), 'type': gc.base_node_type["departure"]},
        "5": {'name': 'D2', 'pos': (1, 5), 'type': gc.base_node_type["normal"]},
        "6": {'name': 'D2', 'pos': (12, 5), 'type': gc.base_node_type["intersection"]}
    }

    edges = {
        "1": {'startNode': "1", 'endNode': "2", 'type': gc.way_type["oneWay"], 'isActive': True},
        "2": {'startNode': "2", 'endNode': "3", 'type': gc.way_type["oneWay"], 'isActive': True},
        "3": {'startNode': "3", 'endNode': "4", 'type': gc.way_type["oneWay"], 'isActive': True},
        "4": {'startNode': "4", 'endNode': "5", 'type': gc.way_type["oneWay"], 'isActive': True},
        "5": {'startNode': "5", 'endNode': "6", 'type': gc.way_type["twoWay"], 'isActive': True}
    }

    try:
        gc.SupervisorGraphCreator(nodes, edges, [])
    except gc.GraphError:
        assert True
    else:
        assert False
    # GraphError: Different path type connected to normal nodes.


@pytest.mark.graph_creator_exception
def test_graph_exception_32():
    # Prawidłowa konfiguracja: pomiedzy stanowiskami z dokowaniem
    # (intersection - waiting - poi - departure - intersection) - one way
    nodes = {
        "1": {'name': 'D2', 'pos': (1, 5), 'type': gc.base_node_type["intersection"]},
        "2": {'name': 'D2', 'pos': (3, 5), 'type': gc.base_node_type["waiting"]},
        "3": {'name': 'D2', 'pos': (6, 5), 'type': gc.base_node_type["load-unload-dock"]},
        "4": {'name': 'D2', 'pos': (9, 5), 'type': gc.base_node_type["departure"]},
        "5": {'name': 'D2', 'pos': (1, 5), 'type': gc.base_node_type["normal"]},
        "6": {'name': 'D2', 'pos': (12, 5), 'type': gc.base_node_type["intersection"]}
    }

    edges = {
        "1": {'startNode': "1", 'endNode': "2", 'type': gc.way_type["oneWay"], 'isActive': True},
        "2": {'startNode': "2", 'endNode': "3", 'type': gc.way_type["oneWay"], 'isActive': True},
        "3": {'startNode': "3", 'endNode': "4", 'type': gc.way_type["oneWay"], 'isActive': True},
        "4": {'startNode': "4", 'endNode': "5", 'type': gc.way_type["oneWay"], 'isActive': True},
        "5": {'startNode': "5", 'endNode': "6", 'type': gc.way_type["narrowTwoWay"], 'isActive': True}
    }

    try:
        gc.SupervisorGraphCreator(nodes, edges, [])
    except gc.GraphError:
        assert True
    else:
        assert False
    # GraphError: Different path type connected to normal nodes.


@pytest.mark.graph_creator_exception
def test_graph_exception_33():
    # Prawidłowa konfiguracja: pomiedzy stanowiskami z dokowaniem
    # (intersection - waiting - poi - departure - intersection) - one way
    nodes = {
        "1": {'name': 'D2', 'pos': (1, 5), 'type': gc.base_node_type["intersection"]},
        "2": {'name': 'D2', 'pos': (3, 5), 'type': gc.base_node_type["waiting"]},
        "3": {'name': 'D2', 'pos': (6, 5), 'type': gc.base_node_type["load-unload-dock"]},
        "4": {'name': 'D2', 'pos': (9, 5), 'type': gc.base_node_type["departure"]},
        "5": {'name': 'D2', 'pos': (12, 5), 'type': gc.base_node_type["intersection"]}
    }

    edges = {
        "1": {'startNode': "1", 'endNode': "2", 'type': gc.way_type["oneWay"], 'isActive': True},
        "2": {'startNode': "3", 'endNode': "2", 'type': gc.way_type["oneWay"], 'isActive': True},
        "3": {'startNode': "3", 'endNode': "4", 'type': gc.way_type["oneWay"], 'isActive': True},
        "4": {'startNode': "4", 'endNode': "5", 'type': gc.way_type["oneWay"], 'isActive': True}
    }

    try:
        gc.SupervisorGraphCreator(nodes, edges, [])
    except gc.GraphError:
        assert True
    else:
        assert False
    # GraphError: Only one waiting/waiting-departure POI should be connected with POI.


@pytest.mark.graph_creator_exception
def test_graph_exception_34():
    # Prawidłowa konfiguracja: pomiedzy stanowiskami z dokowaniem
    # (intersection - waiting - poi - departure - intersection) - one way
    nodes = {
        "1": {'name': 'D2', 'pos': (1, 5), 'type': gc.base_node_type["intersection"]},
        "2": {'name': 'D2', 'pos': (3, 5), 'type': gc.base_node_type["waiting"]},
        "3": {'name': 'D2', 'pos': (6, 5), 'type': gc.base_node_type["load-unload-dock"]},
        "4": {'name': 'D2', 'pos': (9, 5), 'type': gc.base_node_type["departure"]},
        "5": {'name': 'D2', 'pos': (12, 5), 'type': gc.base_node_type["intersection"]}
    }

    edges = {
        "1": {'startNode': "2", 'endNode': "1", 'type': gc.way_type["oneWay"], 'isActive': True},
        "2": {'startNode': "2", 'endNode': "3", 'type': gc.way_type["oneWay"], 'isActive': True},
        "3": {'startNode': "3", 'endNode': "4", 'type': gc.way_type["oneWay"], 'isActive': True},
        "4": {'startNode': "4", 'endNode': "5", 'type': gc.way_type["oneWay"], 'isActive': True}
    }

    try:
        gc.SupervisorGraphCreator(nodes, edges, [])
    except gc.GraphError:
        assert True
    else:
        assert False
    # GraphError: Only one intersection node should be connected as input with waiting node.


@pytest.mark.graph_creator_exception
def test_graph_exception_35():
    # Prawidłowa konfiguracja: pomiedzy stanowiskami z dokowaniem
    # (intersection - waiting - poi - departure - intersection) - one way
    nodes = {
        "1": {'name': 'D2', 'pos': (1, 5), 'type': gc.base_node_type["intersection"]},
        "2": {'name': 'D2', 'pos': (3, 5), 'type': gc.base_node_type["waiting"]},
        "3": {'name': 'D2', 'pos': (6, 5), 'type': gc.base_node_type["load-unload-dock"]},
        "4": {'name': 'D2', 'pos': (9, 5), 'type': gc.base_node_type["departure"]},
        "5": {'name': 'D2', 'pos': (12, 5), 'type': gc.base_node_type["intersection"]}
    }

    edges = {
        "1": {'startNode': "1", 'endNode': "2", 'type': gc.way_type["oneWay"], 'isActive': True},
        "2": {'startNode': "2", 'endNode': "3", 'type': gc.way_type["oneWay"], 'isActive': True},
        "3": {'startNode': "4", 'endNode': "3", 'type': gc.way_type["oneWay"], 'isActive': True},
        "4": {'startNode': "4", 'endNode': "5", 'type': gc.way_type["oneWay"], 'isActive': True}
    }

    try:
        gc.SupervisorGraphCreator(nodes, edges, [])
    except gc.GraphError:
        assert True
    else:
        assert False
    # GraphError: Only one waiting/waiting-departure POI should be connected with POI.


@pytest.mark.graph_creator_exception
def test_graph_exception_36():
    # Prawidłowa konfiguracja: pomiedzy stanowiskami z dokowaniem
    # (intersection - waiting - poi - departure - intersection) - one way
    nodes = {
        "1": {'name': 'D2', 'pos': (1, 5), 'type': gc.base_node_type["intersection"]},
        "2": {'name': 'D2', 'pos': (3, 5), 'type': gc.base_node_type["waiting"]},
        "3": {'name': 'D2', 'pos': (6, 5), 'type': gc.base_node_type["load-unload-dock"]},
        "4": {'name': 'D2', 'pos': (9, 5), 'type': gc.base_node_type["departure"]},
        "5": {'name': 'D2', 'pos': (12, 5), 'type': gc.base_node_type["intersection"]}
    }

    edges = {
        "1": {'startNode': "1", 'endNode': "2", 'type': gc.way_type["oneWay"], 'isActive': True},
        "2": {'startNode': "2", 'endNode': "3", 'type': gc.way_type["oneWay"], 'isActive': True},
        "3": {'startNode': "3", 'endNode': "4", 'type': gc.way_type["oneWay"], 'isActive': True},
        "4": {'startNode': "5", 'endNode': "4", 'type': gc.way_type["oneWay"], 'isActive': True}
    }

    try:
        gc.SupervisorGraphCreator(nodes, edges, [])
    except gc.GraphError:
        assert True
    else:
        assert False
    # GraphError: Only one POI node should be connected as input with departure node.


@pytest.mark.graph_creator_exception
def test_graph_exception_37():
    # Prawidłowa konfiguracja: pomiedzy stanowiskami z dokowaniem
    # (intersection - waiting - poi - departure - intersection) - one way
    nodes = {
        "1": {'name': 'D2', 'pos': (1, 5), 'type': gc.base_node_type["intersection"]},
        "2": {'name': 'D2', 'pos': (3, 5), 'type': gc.base_node_type["waiting"]},
        "3": {'name': 'D2', 'pos': (6, 5), 'type': gc.base_node_type["load-unload-dock"]},
        "4": {'name': 'D2', 'pos': (9, 5), 'type': gc.base_node_type["departure"]},
        "5": {'name': 'D2', 'pos': (12, 5), 'type': gc.base_node_type["intersection"]}
    }

    edges = {
        "1": {'startNode': "1", 'endNode': "2", 'type': gc.way_type["oneWay"], 'isActive': True},
        "2": {'startNode': "3", 'endNode': "2", 'type': gc.way_type["oneWay"], 'isActive': True},
        "3": {'startNode': "4", 'endNode': "3", 'type': gc.way_type["oneWay"], 'isActive': True},
        "4": {'startNode': "4", 'endNode': "5", 'type': gc.way_type["oneWay"], 'isActive': True}
    }

    try:
        gc.SupervisorGraphCreator(nodes, edges, [])
    except gc.GraphError:
        assert True
    else:
        assert False
    # GraphError: Connected POI with given nodes not allowed. Available connection: waiting->POI->departure
    # or waiting-departure->POI-> waiting-departure


@pytest.mark.graph_creator_exception
def test_graph_exception_38():
    # Prawidłowa konfiguracja: pomiedzy stanowiskami bez dokowana
    # (intersection - waiting - poi - departure - intersection) - one way
    nodes = {
        "1": {'name': 'D2', 'pos': (1, 5), 'type': gc.base_node_type["intersection"]},
        "2": {'name': 'D2', 'pos': (3, 5), 'type': gc.base_node_type["waiting"]},
        "3": {'name': 'D2', 'pos': (6, 5), 'type': gc.base_node_type["load"]},
        "4": {'name': 'D2', 'pos': (9, 5), 'type': gc.base_node_type["departure"]},
        "5": {'name': 'D2', 'pos': (12, 5), 'type': gc.base_node_type["intersection"]},
    }

    edges = {
        "1": {'startNode': "1", 'endNode': "2", 'type': gc.way_type["twoWay"], 'isActive': True},
        "2": {'startNode': "2", 'endNode': "3", 'type': gc.way_type["oneWay"], 'isActive': True},
        "3": {'startNode': "3", 'endNode': "4", 'type': gc.way_type["oneWay"], 'isActive': True},
        "4": {'startNode': "4", 'endNode': "5", 'type': gc.way_type["oneWay"], 'isActive': True}
    }

    try:
        gc.SupervisorGraphCreator(nodes, edges, [])
    except gc.GraphError:
        assert True
    else:
        assert False
    # GraphError: Only one POI node should be connected as output with waiting node.


@pytest.mark.graph_creator_exception
def test_graph_exception_39():
    # Prawidłowa konfiguracja: pomiedzy stanowiskami bez dokowana
    # (intersection - waiting - poi - departure - intersection) - one way
    nodes = {
        "1": {'name': 'D2', 'pos': (1, 5), 'type': gc.base_node_type["intersection"]},
        "2": {'name': 'D2', 'pos': (3, 5), 'type': gc.base_node_type["waiting"]},
        "3": {'name': 'D2', 'pos': (6, 5), 'type': gc.base_node_type["load"]},
        "4": {'name': 'D2', 'pos': (9, 5), 'type': gc.base_node_type["departure"]},
        "5": {'name': 'D2', 'pos': (12, 5), 'type': gc.base_node_type["intersection"]},
    }

    edges = {
        "1": {'startNode': "1", 'endNode': "2", 'type': gc.way_type["oneWay"], 'isActive': True},
        "2": {'startNode': "2", 'endNode': "3", 'type': gc.way_type["twoWay"], 'isActive': True},
        "3": {'startNode': "3", 'endNode': "4", 'type': gc.way_type["oneWay"], 'isActive': True},
        "4": {'startNode': "4", 'endNode': "5", 'type': gc.way_type["oneWay"], 'isActive': True}
    }

    try:
        gc.SupervisorGraphCreator(nodes, edges, [])
    except gc.GraphError:
        assert True
    else:
        assert False
    # GraphError: Only one departure/waiting-departure POI should be connected with POI.


@pytest.mark.graph_creator_exception
def test_graph_exception_40():
    # Prawidłowa konfiguracja: pomiedzy stanowiskami bez dokowana
    # (intersection - waiting - poi - departure - intersection) - one way
    nodes = {
        "1": {'name': 'D2', 'pos': (1, 5), 'type': gc.base_node_type["intersection"]},
        "2": {'name': 'D2', 'pos': (3, 5), 'type': gc.base_node_type["waiting"]},
        "3": {'name': 'D2', 'pos': (6, 5), 'type': gc.base_node_type["load"]},
        "4": {'name': 'D2', 'pos': (9, 5), 'type': gc.base_node_type["departure"]},
        "5": {'name': 'D2', 'pos': (12, 5), 'type': gc.base_node_type["intersection"]},
    }

    edges = {
        "1": {'startNode': "1", 'endNode': "2", 'type': gc.way_type["oneWay"], 'isActive': True},
        "2": {'startNode': "2", 'endNode': "3", 'type': gc.way_type["oneWay"], 'isActive': True},
        "3": {'startNode': "3", 'endNode': "4", 'type': gc.way_type["twoWay"], 'isActive': True},
        "4": {'startNode': "4", 'endNode': "5", 'type': gc.way_type["oneWay"], 'isActive': True}
    }

    try:
        gc.SupervisorGraphCreator(nodes, edges, [])
    except gc.GraphError:
        assert True
    else:
        assert False
    # GraphError: Only one waiting/waiting-departure POI should be connected with POI.


@pytest.mark.graph_creator_exception
def test_graph_exception_41():
    # Prawidłowa konfiguracja: pomiedzy stanowiskami bez dokowana
    # (intersection - waiting - poi - departure - intersection) - one way
    nodes = {
        "1": {'name': 'D2', 'pos': (1, 5), 'type': gc.base_node_type["intersection"]},
        "2": {'name': 'D2', 'pos': (3, 5), 'type': gc.base_node_type["waiting"]},
        "3": {'name': 'D2', 'pos': (6, 5), 'type': gc.base_node_type["load"]},
        "4": {'name': 'D2', 'pos': (9, 5), 'type': gc.base_node_type["departure"]},
        "5": {'name': 'D2', 'pos': (12, 5), 'type': gc.base_node_type["intersection"]},
    }

    edges = {
        "1": {'startNode': "1", 'endNode': "2", 'type': gc.way_type["oneWay"], 'isActive': True},
        "2": {'startNode': "2", 'endNode': "3", 'type': gc.way_type["oneWay"], 'isActive': True},
        "3": {'startNode': "3", 'endNode': "4", 'type': gc.way_type["oneWay"], 'isActive': True},
        "4": {'startNode': "4", 'endNode': "5", 'type': gc.way_type["twoWay"], 'isActive': True}
    }

    try:
        gc.SupervisorGraphCreator(nodes, edges, [])
    except gc.GraphError:
        assert True
    else:
        assert False
    # GraphError: Only one POI node should be connected as input with departure node.


@pytest.mark.graph_creator_exception
def test_graph_exception_42():
    # Prawidłowa konfiguracja: pomiedzy stanowiskami bez dokowana
    # (intersection - waiting - poi - departure - intersection) - one way
    nodes = {
        "1": {'name': 'D2', 'pos': (1, 5), 'type': gc.base_node_type["intersection"]},
        "2": {'name': 'D2', 'pos': (3, 5), 'type': gc.base_node_type["waiting"]},
        "3": {'name': 'D2', 'pos': (6, 5), 'type': gc.base_node_type["load"]},
        "4": {'name': 'D2', 'pos': (9, 5), 'type': gc.base_node_type["departure"]},
        "5": {'name': 'D2', 'pos': (12, 5), 'type': gc.base_node_type["intersection"]},
    }

    edges = {
        "1": {'startNode': "1", 'endNode': "2", 'type': gc.way_type["narrowTwoWay"], 'isActive': True},
        "2": {'startNode': "2", 'endNode': "3", 'type': gc.way_type["oneWay"], 'isActive': True},
        "3": {'startNode': "3", 'endNode': "4", 'type': gc.way_type["oneWay"], 'isActive': True},
        "4": {'startNode': "4", 'endNode': "5", 'type': gc.way_type["oneWay"], 'isActive': True}
    }

    try:
        gc.SupervisorGraphCreator(nodes, edges, [])
    except gc.GraphError:
        assert True
    else:
        assert False
    # GraphError: Only one POI node should be connected as output with waiting node.


@pytest.mark.graph_creator_exception
def test_graph_exception_43():
    # Prawidłowa konfiguracja: pomiedzy stanowiskami bez dokowana
    # (intersection - waiting - poi - departure - intersection) - one way
    nodes = {
        "1": {'name': 'D2', 'pos': (1, 5), 'type': gc.base_node_type["intersection"]},
        "2": {'name': 'D2', 'pos': (3, 5), 'type': gc.base_node_type["waiting"]},
        "3": {'name': 'D2', 'pos': (6, 5), 'type': gc.base_node_type["load"]},
        "4": {'name': 'D2', 'pos': (9, 5), 'type': gc.base_node_type["departure"]},
        "5": {'name': 'D2', 'pos': (12, 5), 'type': gc.base_node_type["intersection"]},
    }

    edges = {
        "1": {'startNode': "1", 'endNode': "2", 'type': gc.way_type["oneWay"], 'isActive': True},
        "2": {'startNode': "2", 'endNode': "3", 'type': gc.way_type["narrowTwoWay"], 'isActive': True},
        "3": {'startNode': "3", 'endNode': "4", 'type': gc.way_type["oneWay"], 'isActive': True},
        "4": {'startNode': "4", 'endNode': "5", 'type': gc.way_type["oneWay"], 'isActive': True}
    }

    try:
        gc.SupervisorGraphCreator(nodes, edges, [])
    except gc.GraphError:
        assert True
    else:
        assert False
    # GraphError: Only one departure/waiting-departure POI should be connected with POI.


@pytest.mark.graph_creator_exception
def test_graph_exception_44():
    # Prawidłowa konfiguracja: pomiedzy stanowiskami bez dokowana
    # (intersection - waiting - poi - departure - intersection) - one way
    nodes = {
        "1": {'name': 'D2', 'pos': (1, 5), 'type': gc.base_node_type["intersection"]},
        "2": {'name': 'D2', 'pos': (3, 5), 'type': gc.base_node_type["waiting"]},
        "3": {'name': 'D2', 'pos': (6, 5), 'type': gc.base_node_type["load"]},
        "4": {'name': 'D2', 'pos': (9, 5), 'type': gc.base_node_type["departure"]},
        "5": {'name': 'D2', 'pos': (12, 5), 'type': gc.base_node_type["intersection"]},
    }

    edges = {
        "1": {'startNode': "1", 'endNode': "2", 'type': gc.way_type["oneWay"], 'isActive': True},
        "2": {'startNode': "2", 'endNode': "3", 'type': gc.way_type["oneWay"], 'isActive': True},
        "3": {'startNode': "3", 'endNode': "4", 'type': gc.way_type["narrowTwoWay"], 'isActive': True},
        "4": {'startNode': "4", 'endNode': "5", 'type': gc.way_type["oneWay"], 'isActive': True}
    }

    try:
        gc.SupervisorGraphCreator(nodes, edges, [])
    except gc.GraphError:
        assert True
    else:
        assert False
    # GraphError: Only one waiting/waiting-departure POI should be connected with POI.


@pytest.mark.graph_creator_exception
def test_graph_exception_45():
    # Prawidłowa konfiguracja: pomiedzy stanowiskami bez dokowana
    # (intersection - waiting - poi - departure - intersection) - one way
    nodes = {
        "1": {'name': 'D2', 'pos': (1, 5), 'type': gc.base_node_type["intersection"]},
        "2": {'name': 'D2', 'pos': (3, 5), 'type': gc.base_node_type["waiting"]},
        "3": {'name': 'D2', 'pos': (6, 5), 'type': gc.base_node_type["load"]},
        "4": {'name': 'D2', 'pos': (9, 5), 'type': gc.base_node_type["departure"]},
        "5": {'name': 'D2', 'pos': (12, 5), 'type': gc.base_node_type["intersection"]},
    }

    edges = {
        "1": {'startNode': "1", 'endNode': "2", 'type': gc.way_type["oneWay"], 'isActive': True},
        "2": {'startNode': "2", 'endNode': "3", 'type': gc.way_type["oneWay"], 'isActive': True},
        "3": {'startNode': "3", 'endNode': "4", 'type': gc.way_type["oneWay"], 'isActive': True},
        "4": {'startNode': "4", 'endNode': "5", 'type': gc.way_type["narrowTwoWay"], 'isActive': True}
    }

    try:
        gc.SupervisorGraphCreator(nodes, edges, [])
    except gc.GraphError:
        assert True
    else:
        assert False
    # GraphError: Only one POI node should be connected as input with departure node.


@pytest.mark.graph_creator_exception
def test_graph_exception_46():
    # Prawidłowa konfiguracja: pomiedzy stanowiskami bez dokowana
    # (intersection - waiting - poi - departure - intersection) - one way
    nodes = {
        "1": {'name': 'D2', 'pos': (1, 5), 'type': gc.base_node_type["intersection"]},
        "2": {'name': 'D2', 'pos': (1, 5), 'type': gc.base_node_type["normal"]},
        "3": {'name': 'D2', 'pos': (3, 5), 'type': gc.base_node_type["waiting"]},
        "4": {'name': 'D2', 'pos': (6, 5), 'type': gc.base_node_type["load"]},
        "5": {'name': 'D2', 'pos': (9, 5), 'type': gc.base_node_type["departure"]},
        "6": {'name': 'D2', 'pos': (12, 5), 'type': gc.base_node_type["intersection"]}
    }

    edges = {
        "1": {'startNode': "1", 'endNode': "2", 'type': gc.way_type["twoWay"], 'isActive': True},
        "2": {'startNode': "2", 'endNode': "3", 'type': gc.way_type["oneWay"], 'isActive': True},
        "3": {'startNode': "3", 'endNode': "4", 'type': gc.way_type["oneWay"], 'isActive': True},
        "4": {'startNode': "4", 'endNode': "5", 'type': gc.way_type["oneWay"], 'isActive': True},
        "5": {'startNode': "5", 'endNode': "6", 'type': gc.way_type["oneWay"], 'isActive': True}
    }

    try:
        gc.SupervisorGraphCreator(nodes, edges, [])
    except gc.GraphError:
        assert True
    else:
        assert False
    # GraphError: Normal nodes error. Path contains normal nodes should start and end from different type of node.


@pytest.mark.graph_creator_exception
def test_graph_exception_47():
    # Prawidłowa konfiguracja: pomiedzy stanowiskami bez dokowana
    # (intersection - waiting - poi - departure - intersection) - one way
    nodes = {
        "1": {'name': 'D2', 'pos': (1, 5), 'type': gc.base_node_type["intersection"]},
        "2": {'name': 'D2', 'pos': (1, 5), 'type': gc.base_node_type["normal"]},
        "3": {'name': 'D2', 'pos': (3, 5), 'type': gc.base_node_type["waiting"]},
        "4": {'name': 'D2', 'pos': (6, 5), 'type': gc.base_node_type["load"]},
        "5": {'name': 'D2', 'pos': (9, 5), 'type': gc.base_node_type["departure"]},
        "6": {'name': 'D2', 'pos': (12, 5), 'type': gc.base_node_type["intersection"]}
    }

    edges = {
        "1": {'startNode': "1", 'endNode': "2", 'type': gc.way_type["narrowTwoWay"], 'isActive': True},
        "2": {'startNode': "2", 'endNode': "3", 'type': gc.way_type["oneWay"], 'isActive': True},
        "3": {'startNode': "3", 'endNode': "4", 'type': gc.way_type["oneWay"], 'isActive': True},
        "4": {'startNode': "4", 'endNode': "5", 'type': gc.way_type["oneWay"], 'isActive': True},
        "5": {'startNode': "5", 'endNode': "6", 'type': gc.way_type["oneWay"], 'isActive': True}
    }

    try:
        gc.SupervisorGraphCreator(nodes, edges, [])
    except gc.GraphError:
        assert True
    else:
        assert False
    # GraphError: Normal nodes error. Path contains normal nodes should start and end from different type of node.


@pytest.mark.graph_creator_exception
def test_graph_exception_48():
    # Prawidłowa konfiguracja: pomiedzy stanowiskami bez dokowana
    # (intersection - waiting - poi - departure - intersection) - one way
    nodes = {
        "1": {'name': 'D2', 'pos': (1, 5), 'type': gc.base_node_type["intersection"]},
        "2": {'name': 'D2', 'pos': (1, 5), 'type': gc.base_node_type["normal"]},
        "3": {'name': 'D2', 'pos': (3, 5), 'type': gc.base_node_type["waiting"]},
        "4": {'name': 'D2', 'pos': (6, 5), 'type': gc.base_node_type["load"]},
        "5": {'name': 'D2', 'pos': (9, 5), 'type': gc.base_node_type["departure"]},
        "6": {'name': 'D2', 'pos': (12, 5), 'type': gc.base_node_type["intersection"]}
    }

    edges = {
        "1": {'startNode': "1", 'endNode': "2", 'type': gc.way_type["oneWay"], 'isActive': True},
        "2": {'startNode': "2", 'endNode': "3", 'type': gc.way_type["twoWay"], 'isActive': True},
        "3": {'startNode': "3", 'endNode': "4", 'type': gc.way_type["oneWay"], 'isActive': True},
        "4": {'startNode': "4", 'endNode': "5", 'type': gc.way_type["oneWay"], 'isActive': True},
        "5": {'startNode': "5", 'endNode': "6", 'type': gc.way_type["oneWay"], 'isActive': True}
    }

    try:
        gc.SupervisorGraphCreator(nodes, edges, [])
    except gc.GraphError:
        assert True
    else:
        assert False
    # GraphError: Different path type connected to normal nodes.


@pytest.mark.graph_creator_exception
def test_graph_exception_49():
    # Prawidłowa konfiguracja: pomiedzy stanowiskami bez dokowana
    # (intersection - waiting - poi - departure - intersection) - one way
    nodes = {
        "1": {'name': 'D2', 'pos': (1, 5), 'type': gc.base_node_type["intersection"]},
        "2": {'name': 'D2', 'pos': (1, 5), 'type': gc.base_node_type["normal"]},
        "3": {'name': 'D2', 'pos': (3, 5), 'type': gc.base_node_type["waiting"]},
        "4": {'name': 'D2', 'pos': (6, 5), 'type': gc.base_node_type["load"]},
        "5": {'name': 'D2', 'pos': (9, 5), 'type': gc.base_node_type["departure"]},
        "6": {'name': 'D2', 'pos': (12, 5), 'type': gc.base_node_type["intersection"]}
    }

    edges = {
        "1": {'startNode': "1", 'endNode': "2", 'type': gc.way_type["oneWay"], 'isActive': True},
        "2": {'startNode': "2", 'endNode': "3", 'type': gc.way_type["narrowTwoWay"], 'isActive': True},
        "3": {'startNode': "3", 'endNode': "4", 'type': gc.way_type["oneWay"], 'isActive': True},
        "4": {'startNode': "4", 'endNode': "5", 'type': gc.way_type["oneWay"], 'isActive': True},
        "5": {'startNode': "5", 'endNode': "6", 'type': gc.way_type["oneWay"], 'isActive': True}
    }

    try:
        gc.SupervisorGraphCreator(nodes, edges, [])
    except gc.GraphError:
        assert True
    else:
        assert False
    # GraphError: Different path type connected to normal nodes.


@pytest.mark.graph_creator_exception
def test_graph_exception_50():
    # Prawidłowa konfiguracja: pomiedzy stanowiskami bez dokowana
    # (intersection - waiting - poi - departure - intersection) - one way
    nodes = {
        "1": {'name': 'D2', 'pos': (1, 5), 'type': gc.base_node_type["intersection"]},
        "2": {'name': 'D2', 'pos': (3, 5), 'type': gc.base_node_type["waiting"]},
        "3": {'name': 'D2', 'pos': (1, 5), 'type': gc.base_node_type["normal"]},
        "4": {'name': 'D2', 'pos': (6, 5), 'type': gc.base_node_type["load"]},
        "5": {'name': 'D2', 'pos': (9, 5), 'type': gc.base_node_type["departure"]},
        "6": {'name': 'D2', 'pos': (12, 5), 'type': gc.base_node_type["intersection"]}
    }

    edges = {
        "1": {'startNode': "1", 'endNode': "2", 'type': gc.way_type["oneWay"], 'isActive': True},
        "2": {'startNode': "2", 'endNode': "3", 'type': gc.way_type["twoWay"], 'isActive': True},
        "3": {'startNode': "3", 'endNode': "4", 'type': gc.way_type["oneWay"], 'isActive': True},
        "4": {'startNode': "4", 'endNode': "5", 'type': gc.way_type["oneWay"], 'isActive': True},
        "5": {'startNode': "5", 'endNode': "6", 'type': gc.way_type["oneWay"], 'isActive': True}
    }

    try:
        gc.SupervisorGraphCreator(nodes, edges, [])
    except gc.GraphError:
        assert True
    else:
        assert False
    # GraphError: Normal nodes error. Path contains normal nodes should start and end from different type of node.


@pytest.mark.graph_creator_exception
def test_graph_exception_51():
    # Prawidłowa konfiguracja: pomiedzy stanowiskami bez dokowana
    # (intersection - waiting - poi - departure - intersection) - one way
    nodes = {
        "1": {'name': 'D2', 'pos': (1, 5), 'type': gc.base_node_type["intersection"]},
        "2": {'name': 'D2', 'pos': (3, 5), 'type': gc.base_node_type["waiting"]},
        "3": {'name': 'D2', 'pos': (1, 5), 'type': gc.base_node_type["normal"]},
        "4": {'name': 'D2', 'pos': (6, 5), 'type': gc.base_node_type["load-unload"]},
        "5": {'name': 'D2', 'pos': (9, 5), 'type': gc.base_node_type["departure"]},
        "6": {'name': 'D2', 'pos': (12, 5), 'type': gc.base_node_type["intersection"]}
    }

    edges = {
        "1": {'startNode': "1", 'endNode': "2", 'type': gc.way_type["oneWay"], 'isActive': True},
        "2": {'startNode': "2", 'endNode': "3", 'type': gc.way_type["narrowTwoWay"], 'isActive': True},
        "3": {'startNode': "3", 'endNode': "4", 'type': gc.way_type["oneWay"], 'isActive': True},
        "4": {'startNode': "4", 'endNode': "5", 'type': gc.way_type["oneWay"], 'isActive': True},
        "5": {'startNode': "5", 'endNode': "6", 'type': gc.way_type["oneWay"], 'isActive': True}
    }

    try:
        gc.SupervisorGraphCreator(nodes, edges, [])
    except gc.GraphError:
        assert True
    else:
        assert False
    # GraphError: Normal nodes error. Path contains normal nodes should start and end from different type of node.


@pytest.mark.graph_creator_exception
def test_graph_exception_52():
    # Prawidłowa konfiguracja: pomiedzy stanowiskami bez dokowana
    # (intersection - waiting - poi - departure - intersection) - one way
    nodes = {
        "1": {'name': 'D2', 'pos': (1, 5), 'type': gc.base_node_type["intersection"]},
        "2": {'name': 'D2', 'pos': (3, 5), 'type': gc.base_node_type["waiting"]},
        "3": {'name': 'D2', 'pos': (1, 5), 'type': gc.base_node_type["normal"]},
        "4": {'name': 'D2', 'pos': (6, 5), 'type': gc.base_node_type["load-unload"]},
        "5": {'name': 'D2', 'pos': (9, 5), 'type': gc.base_node_type["departure"]},
        "6": {'name': 'D2', 'pos': (12, 5), 'type': gc.base_node_type["intersection"]}
    }

    edges = {
        "1": {'startNode': "1", 'endNode': "2", 'type': gc.way_type["oneWay"], 'isActive': True},
        "2": {'startNode': "2", 'endNode': "3", 'type': gc.way_type["oneWay"], 'isActive': True},
        "3": {'startNode': "3", 'endNode': "4", 'type': gc.way_type["twoWay"], 'isActive': True},
        "4": {'startNode': "4", 'endNode': "5", 'type': gc.way_type["oneWay"], 'isActive': True},
        "5": {'startNode': "5", 'endNode': "6", 'type': gc.way_type["oneWay"], 'isActive': True}
    }

    try:
        gc.SupervisorGraphCreator(nodes, edges, [])
    except gc.GraphError:
        assert True
    else:
        assert False
    # GraphError: Different path type connected to normal nodes.


@pytest.mark.graph_creator_exception
def test_graph_exception_53():
    # Prawidłowa konfiguracja: pomiedzy stanowiskami bez dokowana
    # (intersection - waiting - poi - departure - intersection) - one way
    nodes = {
        "1": {'name': 'D2', 'pos': (1, 5), 'type': gc.base_node_type["intersection"]},
        "2": {'name': 'D2', 'pos': (3, 5), 'type': gc.base_node_type["waiting"]},
        "3": {'name': 'D2', 'pos': (6, 5), 'type': gc.base_node_type["load-unload"]},
        "4": {'name': 'D2', 'pos': (1, 5), 'type': gc.base_node_type["normal"]},
        "5": {'name': 'D2', 'pos': (9, 5), 'type': gc.base_node_type["departure"]},
        "6": {'name': 'D2', 'pos': (12, 5), 'type': gc.base_node_type["intersection"]}
    }

    edges = {
        "1": {'startNode': "1", 'endNode': "2", 'type': gc.way_type["oneWay"], 'isActive': True},
        "2": {'startNode': "2", 'endNode': "3", 'type': gc.way_type["oneWay"], 'isActive': True},
        "3": {'startNode': "3", 'endNode': "4", 'type': gc.way_type["twoWay"], 'isActive': True},
        "4": {'startNode': "4", 'endNode': "5", 'type': gc.way_type["oneWay"], 'isActive': True},
        "5": {'startNode': "5", 'endNode': "6", 'type': gc.way_type["oneWay"], 'isActive': True}
    }

    try:
        gc.SupervisorGraphCreator(nodes, edges, [])
    except gc.GraphError:
        assert True
    else:
        assert False
    # GraphError: Normal nodes error. Path contains normal nodes should start and end from different type of node.


@pytest.mark.graph_creator_exception
def test_graph_exception_54():
    # Prawidłowa konfiguracja: pomiedzy stanowiskami bez dokowana
    # (intersection - waiting - poi - departure - intersection) - one way
    nodes = {
        "1": {'name': 'D2', 'pos': (1, 5), 'type': gc.base_node_type["intersection"]},
        "2": {'name': 'D2', 'pos': (3, 5), 'type': gc.base_node_type["waiting"]},
        "3": {'name': 'D2', 'pos': (6, 5), 'type': gc.base_node_type["load-unload"]},
        "4": {'name': 'D2', 'pos': (1, 5), 'type': gc.base_node_type["normal"]},
        "5": {'name': 'D2', 'pos': (9, 5), 'type': gc.base_node_type["departure"]},
        "6": {'name': 'D2', 'pos': (12, 5), 'type': gc.base_node_type["intersection"]}
    }

    edges = {
        "1": {'startNode': "1", 'endNode': "2", 'type': gc.way_type["oneWay"], 'isActive': True},
        "2": {'startNode': "2", 'endNode': "3", 'type': gc.way_type["oneWay"], 'isActive': True},
        "3": {'startNode': "3", 'endNode': "4", 'type': gc.way_type["narrowTwoWay"], 'isActive': True},
        "4": {'startNode': "4", 'endNode': "5", 'type': gc.way_type["oneWay"], 'isActive': True},
        "5": {'startNode': "5", 'endNode': "6", 'type': gc.way_type["oneWay"], 'isActive': True}
    }

    try:
        gc.SupervisorGraphCreator(nodes, edges, [])
    except gc.GraphError:
        assert True
    else:
        assert False
    # GraphError: Normal nodes error. Path contains normal nodes should start and end from different type of node.


@pytest.mark.graph_creator_exception
def test_graph_exception_55():
    # Prawidłowa konfiguracja: pomiedzy stanowiskami bez dokowana
    # (intersection - waiting - poi - departure - intersection) - one way
    nodes = {
        "1": {'name': 'D2', 'pos': (1, 5), 'type': gc.base_node_type["intersection"]},
        "2": {'name': 'D2', 'pos': (3, 5), 'type': gc.base_node_type["waiting"]},
        "3": {'name': 'D2', 'pos': (6, 5), 'type': gc.base_node_type["load-unload"]},
        "4": {'name': 'D2', 'pos': (1, 5), 'type': gc.base_node_type["normal"]},
        "5": {'name': 'D2', 'pos': (9, 5), 'type': gc.base_node_type["departure"]},
        "6": {'name': 'D2', 'pos': (12, 5), 'type': gc.base_node_type["intersection"]}
    }

    edges = {
        "1": {'startNode': "1", 'endNode': "2", 'type': gc.way_type["oneWay"], 'isActive': True},
        "2": {'startNode': "2", 'endNode': "3", 'type': gc.way_type["oneWay"], 'isActive': True},
        "3": {'startNode': "3", 'endNode': "4", 'type': gc.way_type["oneWay"], 'isActive': True},
        "4": {'startNode': "4", 'endNode': "5", 'type': gc.way_type["twoWay"], 'isActive': True},
        "5": {'startNode': "5", 'endNode': "6", 'type': gc.way_type["oneWay"], 'isActive': True}
    }

    try:
        gc.SupervisorGraphCreator(nodes, edges, [])
    except gc.GraphError:
        assert True
    else:
        assert False
    # GraphError: Different path type connected to normal nodes.


@pytest.mark.graph_creator_exception
def test_graph_exception_56():
    # Prawidłowa konfiguracja: pomiedzy stanowiskami bez dokowana
    # (intersection - waiting - poi - departure - intersection) - one way
    nodes = {
        "1": {'name': 'D2', 'pos': (1, 5), 'type': gc.base_node_type["intersection"]},
        "2": {'name': 'D2', 'pos': (3, 5), 'type': gc.base_node_type["waiting"]},
        "3": {'name': 'D2', 'pos': (6, 5), 'type': gc.base_node_type["load"]},
        "4": {'name': 'D2', 'pos': (1, 5), 'type': gc.base_node_type["normal"]},
        "5": {'name': 'D2', 'pos': (9, 5), 'type': gc.base_node_type["departure"]},
        "6": {'name': 'D2', 'pos': (12, 5), 'type': gc.base_node_type["intersection"]}
    }

    edges = {
        "1": {'startNode': "1", 'endNode': "2", 'type': gc.way_type["oneWay"], 'isActive': True},
        "2": {'startNode': "2", 'endNode': "3", 'type': gc.way_type["oneWay"], 'isActive': True},
        "3": {'startNode': "3", 'endNode': "4", 'type': gc.way_type["oneWay"], 'isActive': True},
        "4": {'startNode': "4", 'endNode': "5", 'type': gc.way_type["narrowTwoWay"], 'isActive': True},
        "5": {'startNode': "5", 'endNode': "6", 'type': gc.way_type["oneWay"], 'isActive': True}
    }

    try:
        gc.SupervisorGraphCreator(nodes, edges, [])
    except gc.GraphError:
        assert True
    else:
        assert False
    # GraphError: Different path type connected to normal nodes.


@pytest.mark.graph_creator_exception
def test_graph_exception_57():
    # Prawidłowa konfiguracja: pomiedzy stanowiskami bez dokowana
    # (intersection - waiting - poi - departure - intersection) - one way
    nodes = {
        "1": {'name': 'D2', 'pos': (1, 5), 'type': gc.base_node_type["intersection"]},
        "2": {'name': 'D2', 'pos': (3, 5), 'type': gc.base_node_type["waiting"]},
        "3": {'name': 'D2', 'pos': (6, 5), 'type': gc.base_node_type["load-unload"]},
        "4": {'name': 'D2', 'pos': (9, 5), 'type': gc.base_node_type["departure"]},
        "5": {'name': 'D2', 'pos': (1, 5), 'type': gc.base_node_type["normal"]},
        "6": {'name': 'D2', 'pos': (12, 5), 'type': gc.base_node_type["intersection"]}
    }

    edges = {
        "1": {'startNode': "1", 'endNode': "2", 'type': gc.way_type["oneWay"], 'isActive': True},
        "2": {'startNode': "2", 'endNode': "3", 'type': gc.way_type["oneWay"], 'isActive': True},
        "3": {'startNode': "3", 'endNode': "4", 'type': gc.way_type["oneWay"], 'isActive': True},
        "4": {'startNode': "4", 'endNode': "5", 'type': gc.way_type["twoWay"], 'isActive': True},
        "5": {'startNode': "5", 'endNode': "6", 'type': gc.way_type["oneWay"], 'isActive': True}
    }

    try:
        gc.SupervisorGraphCreator(nodes, edges, [])
    except gc.GraphError:
        assert True
    else:
        assert False
    # GraphError: Normal nodes error. Path contains normal nodes should start and end from different type of node.


@pytest.mark.graph_creator_exception
def test_graph_exception_58():
    # Prawidłowa konfiguracja: pomiedzy stanowiskami bez dokowana
    # (intersection - waiting - poi - departure - intersection) - one way
    nodes = {
        "1": {'name': 'D2', 'pos': (1, 5), 'type': gc.base_node_type["intersection"]},
        "2": {'name': 'D2', 'pos': (3, 5), 'type': gc.base_node_type["waiting"]},
        "3": {'name': 'D2', 'pos': (6, 5), 'type': gc.base_node_type["load-unload"]},
        "4": {'name': 'D2', 'pos': (9, 5), 'type': gc.base_node_type["departure"]},
        "5": {'name': 'D2', 'pos': (1, 5), 'type': gc.base_node_type["normal"]},
        "6": {'name': 'D2', 'pos': (12, 5), 'type': gc.base_node_type["intersection"]}
    }

    edges = {
        "1": {'startNode': "1", 'endNode': "2", 'type': gc.way_type["oneWay"], 'isActive': True},
        "2": {'startNode': "2", 'endNode': "3", 'type': gc.way_type["oneWay"], 'isActive': True},
        "3": {'startNode': "3", 'endNode': "4", 'type': gc.way_type["oneWay"], 'isActive': True},
        "4": {'startNode': "4", 'endNode': "5", 'type': gc.way_type["narrowTwoWay"], 'isActive': True},
        "5": {'startNode': "5", 'endNode': "6", 'type': gc.way_type["oneWay"], 'isActive': True}
    }

    try:
        gc.SupervisorGraphCreator(nodes, edges, [])
    except gc.GraphError:
        assert True
    else:
        assert False
    # GraphError: Normal nodes error. Path contains normal nodes should start and end from different type of node.


@pytest.mark.graph_creator_exception
def test_graph_exception_59():
    # Prawidłowa konfiguracja: pomiedzy stanowiskami bez dokowana
    # (intersection - waiting - poi - departure - intersection) - one way
    nodes = {
        "1": {'name': 'D2', 'pos': (1, 5), 'type': gc.base_node_type["intersection"]},
        "2": {'name': 'D2', 'pos': (3, 5), 'type': gc.base_node_type["waiting"]},
        "3": {'name': 'D2', 'pos': (6, 5), 'type': gc.base_node_type["load"]},
        "4": {'name': 'D2', 'pos': (9, 5), 'type': gc.base_node_type["departure"]},
        "5": {'name': 'D2', 'pos': (1, 5), 'type': gc.base_node_type["normal"]},
        "6": {'name': 'D2', 'pos': (12, 5), 'type': gc.base_node_type["intersection"]}
    }

    edges = {
        "1": {'startNode': "1", 'endNode': "2", 'type': gc.way_type["oneWay"], 'isActive': True},
        "2": {'startNode': "2", 'endNode': "3", 'type': gc.way_type["oneWay"], 'isActive': True},
        "3": {'startNode': "3", 'endNode': "4", 'type': gc.way_type["oneWay"], 'isActive': True},
        "4": {'startNode': "4", 'endNode': "5", 'type': gc.way_type["oneWay"], 'isActive': True},
        "5": {'startNode': "5", 'endNode': "6", 'type': gc.way_type["twoWay"], 'isActive': True}
    }

    try:
        gc.SupervisorGraphCreator(nodes, edges, [])
    except gc.GraphError:
        assert True
    else:
        assert False
    # GraphError: Different path type connected to normal nodes.


@pytest.mark.graph_creator_exception
def test_graph_exception_60():
    # Prawidłowa konfiguracja: pomiedzy stanowiskami bez dokowana
    # (intersection - waiting - poi - departure - intersection) - one way
    nodes = {
        "1": {'name': 'D2', 'pos': (1, 5), 'type': gc.base_node_type["intersection"]},
        "2": {'name': 'D2', 'pos': (3, 5), 'type': gc.base_node_type["waiting"]},
        "3": {'name': 'D2', 'pos': (6, 5), 'type': gc.base_node_type["load-unload"]},
        "4": {'name': 'D2', 'pos': (9, 5), 'type': gc.base_node_type["departure"]},
        "5": {'name': 'D2', 'pos': (1, 5), 'type': gc.base_node_type["normal"]},
        "6": {'name': 'D2', 'pos': (12, 5), 'type': gc.base_node_type["intersection"]}
    }

    edges = {
        "1": {'startNode': "1", 'endNode': "2", 'type': gc.way_type["oneWay"], 'isActive': True},
        "2": {'startNode': "2", 'endNode': "3", 'type': gc.way_type["oneWay"], 'isActive': True},
        "3": {'startNode': "3", 'endNode': "4", 'type': gc.way_type["oneWay"], 'isActive': True},
        "4": {'startNode': "4", 'endNode': "5", 'type': gc.way_type["oneWay"], 'isActive': True},
        "5": {'startNode': "5", 'endNode': "6", 'type': gc.way_type["narrowTwoWay"], 'isActive': True}
    }

    try:
        gc.SupervisorGraphCreator(nodes, edges, [])
    except gc.GraphError:
        assert True
    else:
        assert False
    # GraphError: Different path type connected to normal nodes.


@pytest.mark.graph_creator_exception
def test_graph_exception_61():
    # Prawidłowa konfiguracja: pomiedzy stanowiskami bez dokowana
    # (intersection - waiting - poi - departure - intersection) - one way
    nodes = {
        "1": {'name': 'D2', 'pos': (1, 5), 'type': gc.base_node_type["intersection"]},
        "2": {'name': 'D2', 'pos': (3, 5), 'type': gc.base_node_type["waiting"]},
        "3": {'name': 'D2', 'pos': (6, 5), 'type': gc.base_node_type["load-unload"]},
        "4": {'name': 'D2', 'pos': (9, 5), 'type': gc.base_node_type["departure"]},
        "5": {'name': 'D2', 'pos': (12, 5), 'type': gc.base_node_type["intersection"]}
    }

    edges = {
        "1": {'startNode': "1", 'endNode': "2", 'type': gc.way_type["oneWay"], 'isActive': True},
        "2": {'startNode': "3", 'endNode': "2", 'type': gc.way_type["oneWay"], 'isActive': True},
        "3": {'startNode': "3", 'endNode': "4", 'type': gc.way_type["oneWay"], 'isActive': True},
        "4": {'startNode': "4", 'endNode': "5", 'type': gc.way_type["oneWay"], 'isActive': True}
    }

    try:
        gc.SupervisorGraphCreator(nodes, edges, [])
    except gc.GraphError:
        assert True
    else:
        assert False
    # GraphError: Only one waiting/waiting-departure POI should be connected with POI.


@pytest.mark.graph_creator_exception
def test_graph_exception_62():
    # Prawidłowa konfiguracja: pomiedzy stanowiskami z dokowaniem
    # (intersection - waiting-departure - poi z dokowaniem - waiting-departure - intersection) - two(narrow)way
    nodes = {
        "1": {'name': 'D2', 'pos': (1, 5), 'type': gc.base_node_type["intersection"]},
        "2": {'name': 'D2', 'pos': (3, 5), 'type': gc.base_node_type["waiting-departure"]},
        "3": {'name': 'D2', 'pos': (6, 5), 'type': gc.base_node_type["load-dock"]}
    }

    edges = {
        "1": {'startNode': "1", 'endNode': "2", 'type': gc.way_type["narrowTwoWay"], 'isActive': True},
        "2": {'startNode': "2", 'endNode': "3", 'type': gc.way_type["narrowTwoWay"], 'isActive': True}
    }

    try:
        gc.SupervisorGraphCreator(nodes, edges, [])
    except gc.GraphError:
        assert True
    else:
        assert False
    # GraphError: Edges should be twoWay in connection intersection<->waiting-departure.


@pytest.mark.graph_creator_exception
def test_graph_exception_63():
    # Prawidłowa konfiguracja: pomiedzy stanowiskami z dokowaniem
    # (intersection - waiting-departure - poi z dokowaniem - waiting-departure - intersection) - two(narrow)way
    nodes = {
        "1": {'name': 'D2', 'pos': (1, 5), 'type': gc.base_node_type["intersection"]},
        "2": {'name': 'D2', 'pos': (3, 5), 'type': gc.base_node_type["waiting-departure"]},
        "3": {'name': 'D2', 'pos': (6, 5), 'type': gc.base_node_type["load-dock"]}
    }

    edges = {
        "1": {'startNode': "1", 'endNode': "2", 'type': gc.way_type["oneWay"], 'isActive': True},
        "2": {'startNode': "2", 'endNode': "3", 'type': gc.way_type["narrowTwoWay"], 'isActive': True}

    }

    try:
        gc.SupervisorGraphCreator(nodes, edges, [])
    except gc.GraphError:
        assert True
    else:
        assert False
    # GraphError: Too much nodes connected with witing-departure node.


@pytest.mark.graph_creator_exception
def test_graph_exception_64():
    # Prawidłowa konfiguracja: pomiedzy stanowiskami z dokowaniem
    # (intersection - waiting-departure - poi z dokowaniem - waiting-departure - intersection) - two(narrow)way
    nodes = {
        "1": {'name': 'D2', 'pos': (1, 5), 'type': gc.base_node_type["intersection"]},
        "2": {'name': 'D2', 'pos': (3, 5), 'type': gc.base_node_type["waiting-departure"]},
        "3": {'name': 'D2', 'pos': (6, 5), 'type': gc.base_node_type["load-dock"]}
    }

    edges = {
        "1": {'startNode': "1", 'endNode': "2", 'type': gc.way_type["twoWay"], 'isActive': True},
        "2": {'startNode': "2", 'endNode': "3", 'type': gc.way_type["oneWay"], 'isActive': True}
    }

    try:
        gc.SupervisorGraphCreator(nodes, edges, [])
    except gc.GraphError:
        assert True
    else:
        assert False
    # GraphError: Only one departure/waiting-departure POI should be connected with POI.


@pytest.mark.graph_creator_exception
def test_graph_exception_65():
    # Prawidłowa konfiguracja: pomiedzy stanowiskami z dokowaniem
    # (intersection - waiting-departure - poi z dokowaniem - waiting-departure - intersection) - two(narrow)way
    nodes = {
        "1": {'name': 'D2', 'pos': (1, 5), 'type': gc.base_node_type["intersection"]},
        "2": {'name': 'D2', 'pos': (3, 5), 'type': gc.base_node_type["waiting-departure"]},
        "3": {'name': 'D2', 'pos': (6, 5), 'type': gc.base_node_type["load-dock"]}
    }

    edges = {
        "1": {'startNode': "1", 'endNode': "2", 'type': gc.way_type["twoWay"], 'isActive': True},
        "2": {'startNode': "2", 'endNode': "3", 'type': gc.way_type["twoWay"], 'isActive': True}
    }

    try:
        gc.SupervisorGraphCreator(nodes, edges, [])
    except gc.GraphError:
        assert True
    else:
        assert False
    # GraphError: Edges should be narrow two way in connection waiting-departure->POI->waiting-departure


@pytest.mark.graph_creator_exception
def test_graph_exception_66():
    # Prawidłowa konfiguracja: pomiedzy stanowiskami z dokowaniem
    # (intersection - waiting-departure - poi z dokowaniem - waiting-departure - intersection) - two(narrow)way
    nodes = {
        "1": {'name': 'D2', 'pos': (1, 5), 'type': gc.base_node_type["intersection"]},
        "2": {'name': 'D2', 'pos': (3, 5), 'type': gc.base_node_type["waiting-departure"]},
        "3": {'name': 'D2', 'pos': (3, 5), 'type': gc.base_node_type["waiting-departure"]},
        "4": {'name': 'D2', 'pos': (6, 5), 'type': gc.base_node_type["load-dock"]}
    }

    edges = {
        "1": {'startNode': "1", 'endNode': "2", 'type': gc.way_type["twoWay"], 'isActive': True},
        "2": {'startNode': "2", 'endNode': "3", 'type': gc.way_type["narrowTwoWay"], 'isActive': True},
        "3": {'startNode': "3", 'endNode': "4", 'type': gc.way_type["narrowTwoWay"], 'isActive': True},
    }

    try:
        gc.SupervisorGraphCreator(nodes, edges, [])
    except gc.GraphError:
        assert True
    else:
        assert False
    # GraphError: Connected waiting-departure node with given nodes not allowed. Node should be connected with
    # intersection and POI.


@pytest.mark.graph_creator_exception
def test_graph_exception_67():
    # Prawidłowa konfiguracja: pomiedzy stanowiskami bez dokowana
    # (intersection - waiting-departure - poi - waiting-departure - intersection) - two(narrow)way
    nodes = {
        "1": {'name': 'D2', 'pos': (1, 5), 'type': gc.base_node_type["intersection"]},
        "2": {'name': 'D2', 'pos': (3, 5), 'type': gc.base_node_type["waiting-departure"]},
        "3": {'name': 'D2', 'pos': (6, 5), 'type': gc.base_node_type["load"]}
    }

    edges = {
        "1": {'startNode': "1", 'endNode': "2", 'type': gc.way_type["narrowTwoWay"], 'isActive': True},
        "2": {'startNode': "2", 'endNode': "3", 'type': gc.way_type["narrowTwoWay"], 'isActive': True}
    }

    try:
        gc.SupervisorGraphCreator(nodes, edges, [])
    except gc.GraphError:
        assert True
    else:
        assert False
    # GraphError: Edges should be twoWay in connection intersection<->waiting-departure.


@pytest.mark.graph_creator_exception
def test_graph_exception_68():
    # Prawidłowa konfiguracja: pomiedzy stanowiskami bez dokowana
    # (intersection - waiting-departure - poi - waiting-departure - intersection) - two(narrow)way
    nodes = {
        "1": {'name': 'D2', 'pos': (1, 5), 'type': gc.base_node_type["intersection"]},
        "2": {'name': 'D2', 'pos': (3, 5), 'type': gc.base_node_type["waiting-departure"]},
        "3": {'name': 'D2', 'pos': (6, 5), 'type': gc.base_node_type["load"]}
    }

    edges = {
        "1": {'startNode': "1", 'endNode': "2", 'type': gc.way_type["oneWay"], 'isActive': True},
        "2": {'startNode': "2", 'endNode': "3", 'type': gc.way_type["narrowTwoWay"], 'isActive': True}

    }

    try:
        gc.SupervisorGraphCreator(nodes, edges, [])
    except gc.GraphError:
        assert True
    else:
        assert False
    # GraphError: Too much nodes connected with witing-departure node.


@pytest.mark.graph_creator_exception
def test_graph_exception_69():
    # Prawidłowa konfiguracja: pomiedzy stanowiskami bez dokowana
    # (intersection - waiting-departure - poi - waiting-departure - intersection) - two(narrow)way
    nodes = {
        "1": {'name': 'D2', 'pos': (1, 5), 'type': gc.base_node_type["intersection"]},
        "2": {'name': 'D2', 'pos': (3, 5), 'type': gc.base_node_type["waiting-departure"]},
        "3": {'name': 'D2', 'pos': (6, 5), 'type': gc.base_node_type["load"]}
    }

    edges = {
        "1": {'startNode': "1", 'endNode': "2", 'type': gc.way_type["twoWay"], 'isActive': True},
        "2": {'startNode': "2", 'endNode': "3", 'type': gc.way_type["oneWay"], 'isActive': True}
    }

    try:
        gc.SupervisorGraphCreator(nodes, edges, [])
    except gc.GraphError:
        assert True
    else:
        assert False
    # GraphError: Only one departure/waiting-departure POI should be connected with POI.


@pytest.mark.graph_creator_exception
def test_graph_exception_70():
    # Prawidłowa konfiguracja: pomiedzy stanowiskami bez dokowana
    # (intersection - waiting-departure - poi - waiting-departure - intersection) - two(narrow)way
    nodes = {
        "1": {'name': 'D2', 'pos': (1, 5), 'type': gc.base_node_type["intersection"]},
        "2": {'name': 'D2', 'pos': (3, 5), 'type': gc.base_node_type["waiting-departure"]},
        "3": {'name': 'D2', 'pos': (6, 5), 'type': gc.base_node_type["load"]}
    }

    edges = {
        "1": {'startNode': "1", 'endNode': "2", 'type': gc.way_type["twoWay"], 'isActive': True},
        "2": {'startNode': "2", 'endNode': "3", 'type': gc.way_type["twoWay"], 'isActive': True}
    }

    try:
        gc.SupervisorGraphCreator(nodes, edges, [])
    except gc.GraphError:
        assert True
    else:
        assert False
    # GraphError: Edges should be narrow two way in connection waiting-departure->POI->waiting-departure


@pytest.mark.graph_creator_exception
def test_graph_exception_71():
    # Prawidłowa konfiguracja: pomiedzy stanowiskami bez dokowana
    # (intersection - waiting-departure - poi - waiting-departure - intersection) - two(narrow)way
    nodes = {
        "1": {'name': 'D2', 'pos': (1, 5), 'type': gc.base_node_type["intersection"]},
        "2": {'name': 'D2', 'pos': (3, 5), 'type': gc.base_node_type["waiting-departure"]},
        "3": {'name': 'D2', 'pos': (3, 5), 'type': gc.base_node_type["waiting-departure"]},
        "4": {'name': 'D2', 'pos': (6, 5), 'type': gc.base_node_type["load"]}
    }

    edges = {
        "1": {'startNode': "1", 'endNode': "2", 'type': gc.way_type["twoWay"], 'isActive': True},
        "2": {'startNode': "2", 'endNode': "3", 'type': gc.way_type["narrowTwoWay"], 'isActive': True},
        "3": {'startNode': "3", 'endNode': "4", 'type': gc.way_type["narrowTwoWay"], 'isActive': True},
    }

    try:
        gc.SupervisorGraphCreator(nodes, edges, [])
    except gc.GraphError:
        assert True
    else:
        assert False
    # GraphError: Connected waiting-departure node with given nodes not allowed. Node should be connected
    # with intersection and POI.


@pytest.mark.graph_creator_exception
def test_graph_exception_72():
    # Prawidłowa konfiguracja: intersection - parking - intersection (dwukierunkowa waska)
    nodes = {
        "1": {'name': 'D2', 'pos': (1, 5), 'type': gc.base_node_type["intersection"]},
        "2": {'name': 'D2', 'pos': (3, 5), 'type': gc.base_node_type["parking"]},
        "3": {'name': 'D2', 'pos': (3, 5), 'type': gc.base_node_type["intersection"]}
    }

    edges = {
        "1": {'startNode': "1", 'endNode': "2", 'type': gc.way_type["narrowTwoWay"], 'isActive': True},
        "2": {'startNode': "2", 'endNode': "3", 'type': gc.way_type["narrowTwoWay"], 'isActive': True}
    }

    try:
        gc.SupervisorGraphCreator(nodes, edges, [])
    except gc.GraphError:
        assert True
    else:
        assert False
    # GraphError: Only one intersection node should be connected as input with parking.


@pytest.mark.graph_creator_exception
def test_graph_exception_73():
    # Prawidłowa konfiguracja: intersection - parking - intersection (dwukierunkowa waska)
    nodes = {
        "1": {'name': 'D2', 'pos': (1, 5), 'type': gc.base_node_type["intersection"]},
        "2": {'name': 'D2', 'pos': (3, 5), 'type': gc.base_node_type["parking"]}
    }

    edges = {
        "1": {'startNode': "1", 'endNode': "2", 'type': gc.way_type["oneWay"], 'isActive': True}
    }

    try:
        gc.SupervisorGraphCreator(nodes, edges, [])
    except gc.GraphError:
        assert True
    else:
        assert False
    # GraphError: Only one intersection node should be connected as output with parking.


@pytest.mark.graph_creator_exception
def test_graph_exception_74():
    # Prawidłowa konfiguracja: intersection - parking - intersection (dwukierunkowa waska)
    nodes = {
        "1": {'name': 'D2', 'pos': (1, 5), 'type': gc.base_node_type["intersection"]},
        "2": {'name': 'D2', 'pos': (3, 5), 'type': gc.base_node_type["parking"]}
    }

    edges = {
        "1": {'startNode': "1", 'endNode': "2", 'type': gc.way_type["twoWay"], 'isActive': True}
    }

    try:
        gc.SupervisorGraphCreator(nodes, edges, [])
    except gc.GraphError:
        assert True
    else:
        assert False
    # GraphError: Edges should be narrow two way in connection intersection->parking->intersection.


@pytest.mark.graph_creator_exception
def test_graph_exception_75():
    # Prawidłowa konfiguracja: intersection - queue - intersection (droga jednokierunkowa)
    nodes = {
        "1": {'name': 'D2', 'pos': (1, 5), 'type': gc.base_node_type["intersection"]},
        "2": {'name': 'D2', 'pos': (3, 5), 'type': gc.base_node_type["queue"]},
        "3": {'name': 'D2', 'pos': (3, 5), 'type': gc.base_node_type["intersection"]}
    }

    edges = {
        "1": {'startNode': "1", 'endNode': "2", 'type': gc.way_type["twoWay"], 'isActive': True},
        "2": {'startNode': "2", 'endNode': "3", 'type': gc.way_type["oneWay"], 'isActive': True}
    }

    try:
        gc.SupervisorGraphCreator(nodes, edges, [])
    except gc.GraphError:
        assert True
    else:
        assert False
    # GraphError: Only one intersection node should be connected as output with queue.


@pytest.mark.graph_creator_exception
def test_graph_exception_76():
    # Prawidłowa konfiguracja: intersection - queue - intersection (droga jednokierunkowa)
    nodes = {
        "1": {'name': 'D2', 'pos': (1, 5), 'type': gc.base_node_type["intersection"]},
        "2": {'name': 'D2', 'pos': (3, 5), 'type': gc.base_node_type["queue"]},
        "3": {'name': 'D2', 'pos': (3, 5), 'type': gc.base_node_type["intersection"]}
    }

    edges = {
        "1": {'startNode': "1", 'endNode': "2", 'type': gc.way_type["oneWay"], 'maxRobots': 3, 'weight': 1,
              'isActive': True},
        "2": {'startNode': "2", 'endNode': "3", 'type': gc.way_type["twoWay"], 'maxRobots': 3, 'weight': 1,
              'isActive': True}
    }

    try:
        gc.SupervisorGraphCreator(nodes, edges, [])
    except gc.GraphError:
        assert True
    else:
        assert False
    # GraphError: Only one intersection node should be connected as input with queue.


@pytest.mark.graph_creator_exception
def test_graph_exception_77():
    # Prawidłowa konfiguracja: intersection - queue - intersection (droga jednokierunkowa)
    nodes = {
        "1": {'name': 'D2', 'pos': (1, 5), 'type': gc.base_node_type["intersection"]},
        "2": {'name': 'D2', 'pos': (3, 5), 'type': gc.base_node_type["queue"]},
        "3": {'name': 'D2', 'pos': (3, 5), 'type': gc.base_node_type["intersection"]}
    }

    edges = {
        "1": {'startNode': "1", 'endNode': "2", 'type': gc.way_type["narrowTwoWay"], 'isActive': True},
        "2": {'startNode': "2", 'endNode': "3", 'type': gc.way_type["oneWay"], 'isActive': True}
    }

    try:
        gc.SupervisorGraphCreator(nodes, edges, [])
    except gc.GraphError:
        assert True
    else:
        assert False
    # GraphError: Only one intersection node should be connected as output with queue.


@pytest.mark.graph_creator_exception
def test_graph_exception_78():
    # Prawidłowa konfiguracja: intersection - queue - intersection (droga jednokierunkowa)
    nodes = {
        "1": {'name': 'D2', 'pos': (1, 5), 'type': gc.base_node_type["intersection"]},
        "2": {'name': 'D2', 'pos': (3, 5), 'type': gc.base_node_type["queue"]},
        "3": {'name': 'D2', 'pos': (3, 5), 'type': gc.base_node_type["intersection"]}
    }

    edges = {
        "1": {'startNode': "1", 'endNode': "2", 'type': gc.way_type["oneWay"], 'maxRobots': 3, 'weight': 1,
              'isActive': True},
        "2": {'startNode': "2", 'endNode': "3", 'type': gc.way_type["narrowTwoWay"], 'maxRobots': 3, 'weight': 1,
              'isActive': True}
    }

    try:
        gc.SupervisorGraphCreator(nodes, edges, [])
    except gc.GraphError:
        assert True
    else:
        assert False
    # GraphError: Only one intersection node should be connected as input with queue.


@pytest.mark.graph_creator_exception
def test_graph_exception_79():
    # Prawidłowa konfiguracja: intersection - queue - intersection (droga jednokierunkowa)
    nodes = {
        "1": {'name': 'D2', 'pos': (1, 5), 'type': gc.base_node_type["intersection"]},
        "2": {'name': 'D2', 'pos': (3, 5), 'type': gc.base_node_type["normal"]},
        "3": {'name': 'D2', 'pos': (3, 5), 'type': gc.base_node_type["queue"]},
        "4": {'name': 'D2', 'pos': (3, 5), 'type': gc.base_node_type["intersection"]}
    }

    edges = {
        "1": {'startNode': "1", 'endNode': "2", 'type': gc.way_type["twoWay"], 'maxRobots': 3, 'weight': 1,
              'isActive': True},
        "2": {'startNode': "2", 'endNode': "3", 'type': gc.way_type["oneWay"], 'maxRobots': 3, 'weight': 1,
              'isActive': True},
        "3": {'startNode': "3", 'endNode': "4", 'type': gc.way_type["oneWay"], 'maxRobots': 3, 'weight': 1,
              'isActive': True}
    }

    try:
        gc.SupervisorGraphCreator(nodes, edges, [])
    except gc.GraphError:
        assert True
    else:
        assert False
    # GraphError: Normal nodes error. Path contains normal nodes should start and end from different type of node.
