# -*- coding: utf-8 -*-
import pytest
from test_data import *
import graph_creator as gc
import dispatcher as disp
from datetime import datetime, timedelta

graph_in = gc.SupervisorGraphCreator(node_dict, edge_dict, pois_raw)
graph_in.graph = supervisor_graph


# ------------------------------ PoisManager ------------------------------ #
@pytest.mark.pois_manager
def test_pois_manager_check_if_method_exist():
    pois_manager = disp.PoisManager(graph_in)
    assert "set_pois" in dir(pois_manager)
    assert "check_if_queue" in dir(pois_manager)
    assert "get_raw_pois_dict" in dir(pois_manager)
    assert "get_type" in dir(pois_manager)

    assert "pois" in dir(pois_manager)


@pytest.mark.pois_manager
def test_pois_manager_set_pois():
    pois_manager = disp.PoisManager(graph_in)
    assert pois_manager.pois == {poi["id"]: poi["type"] for poi in pois_raw}


@pytest.mark.pois_manager
def test_pois_manager_check_if_queue():
    pois_manager = disp.PoisManager(graph_in)
    assert pois_manager.check_if_queue("1")
    assert not pois_manager.check_if_queue("5")


@pytest.mark.pois_manager
def test_pois_manager_check_if_queue_throws_exception_when_poi_doesnt_exist_on_graph():
    pois_manager = disp.PoisManager(graph_in)
    poi_id = "20"
    try:
        pois_manager.check_if_queue(poi_id)
    except disp.PoisManagerError as error:
        assert "Poi id '{}' doesn't exist".format(poi_id) == str(error)
    else:
        assert False


@pytest.mark.pois_manager
def test_pois_manager_get_raw_pois_dict():
    pois_manager = disp.PoisManager(graph_in)
    assert pois_manager.get_raw_pois_dict() == {poi["id"]: None for poi in pois_raw}


@pytest.mark.pois_manager
def test_pois_manager_get_type():
    pois_manager = disp.PoisManager(graph_in)
    assert pois_manager.get_type("1") == gc.base_node_type["queue"]
    assert pois_manager.get_type("5") == gc.base_node_type["unload-dock"]


@pytest.mark.pois_manager
def test_pois_manager_get_type_throws_exception_when_poi_doesnt_exist_on_graph():
    pois_manager = disp.PoisManager(graph_in)
    poi_id = "20"
    try:
        pois_manager.get_type(poi_id)
    except disp.PoisManagerError as error:
        assert "Poi id '{}' doesn't exist".format(poi_id) == str(error)
    else:
        assert False


# ------------------------------ PlanningGraph ------------------------------ #
@pytest.mark.planing_graph
def test_planning_graph_check_if_method_exist():
    planning_graph = disp.PlanningGraph(graph_in)
    assert "block_other_pois" in dir(planning_graph)
    assert "set_robot_on_future_edge" in dir(planning_graph)
    assert "get_robots_on_future_edge" in dir(planning_graph)
    assert "get_robots_on_edge" in dir(planning_graph)
    assert "get_end_go_to_node" in dir(planning_graph)
    assert "get_end_docking_node" in dir(planning_graph)
    assert "get_end_wait_node" in dir(planning_graph)
    assert "get_end_undocking_node" in dir(planning_graph)
    assert "get_max_allowed_robots_using_pois" in dir(planning_graph)
    assert "get_group_id" in dir(planning_graph)
    assert "get_edges_by_group" in dir(planning_graph)
    assert "get_max_allowed_robots" in dir(planning_graph)
    assert "get_poi" in dir(planning_graph)
    assert "get_path" in dir(planning_graph)
    assert "get_path_length" in dir(planning_graph)
    assert "get_base_pois_edges" in dir(planning_graph)
    assert "is_intersection_edge" in dir(planning_graph)
    assert "select_next_task" in dir(planning_graph)
    assert "_get_task_travel_stands_time" in dir(planning_graph)

    assert "graph" in dir(planning_graph)
    assert "pois" in dir(planning_graph)
    assert "future_blocked_edges" in dir(planning_graph)


@pytest.mark.planing_graph
def test_planning_graph_block_other_pois():
    robot_node = 69  # skrzyzowanie
    target_node = 16  # Poi id 6
    planning_graph = disp.PlanningGraph(graph_in)
    planning_graph.block_other_pois(robot_node, target_node)
    other_pois_nodes = []
    for node_data in planning_graph.graph.graph.nodes(data=True):
        if node_data[1]["poiId"] != "6":
            other_pois_nodes.append(node_data[1]["poiId"])
    for blocked_poi_node in other_pois_nodes:
        try:
            nx.shortest_path(planning_graph.graph.graph, source=robot_node, target=blocked_poi_node,
                             weight='planWeight')
        except nx.NetworkXNoPath:
            assert True
        else:
            assert False

    robot_node = 10  # robot jest w jakims POI, dozwolone poruszanie w ramach POI w którym się znajduje oraz nastepnym
    target_node = 16  # Poi id 6
    planning_graph = disp.PlanningGraph(graph_in)
    planning_graph.block_other_pois(robot_node, target_node)
    other_pois_nodes = []
    for node_data in planning_graph.graph.graph.nodes(data=True):
        if node_data[1]["poiId"] != "6":
            other_pois_nodes.append(node_data[1]["poiId"])
    for blocked_poi_node in other_pois_nodes:
        try:
            nx.shortest_path(planning_graph.graph.graph, source=robot_node, target=blocked_poi_node,
                             weight='planWeight')
        except nx.NetworkXNoPath:
            assert True
        else:
            assert False

    robot_node = 16  # robot jest w jakims POI, dozwolone poruszanie w ramach POI w którym się znajduje oraz nastepnym
    target_node = 15  # Poi id 6
    planning_graph = disp.PlanningGraph(graph_in)
    planning_graph.block_other_pois(robot_node, target_node)
    other_pois_nodes = [node_data[1]["poiId"] for node_data in planning_graph.graph.graph.nodes(data=True)
                        if node_data[1]["poiId"] != "6"]
    for blocked_poi_node in other_pois_nodes:
        try:
            nx.shortest_path(planning_graph.graph.graph, source=robot_node, target=blocked_poi_node,
                             weight='planWeight')
        except nx.NetworkXNoPath:
            assert True
        else:
            assert False


@pytest.mark.planing_graph
def test_planning_graph_set_robot_on_future_edge():
    planning_graph = disp.PlanningGraph(graph_in)
    new_edge = (63, 64)
    robot_id = "zxc"
    planning_graph.set_robot_on_future_edge(new_edge, robot_id)
    assert planning_graph.future_blocked_edges[new_edge] == [robot_id]

    planning_graph.set_robot_on_future_edge(new_edge, "robot2")
    assert planning_graph.future_blocked_edges[new_edge] == [robot_id, "robot2"]


@pytest.mark.planing_graph
def test_planning_graph_get_robot_on_future_edge():
    planning_graph = disp.PlanningGraph(graph_in)
    new_edge = (63, 64)
    robot_id = "zxc"
    planning_graph.set_robot_on_future_edge(new_edge, robot_id)
    assert planning_graph.get_robots_on_future_edge(new_edge) == [robot_id]

    planning_graph.set_robot_on_future_edge(new_edge, "robot2")
    assert planning_graph.get_robots_on_future_edge(new_edge) == [robot_id, "robot2"]


@pytest.mark.planing_graph
def test_planning_graph_get_end_go_to_node():
    graph_in.graph = supervisor_graph
    # queue
    planning_graph = disp.PlanningGraph(graph_in)
    assert planning_graph.get_end_go_to_node(pois_raw[0]["id"], pois_raw[0]["type"]) \
           == [node_data[0] for node_data in graph_in.graph.nodes(data=True)
               if node_data[1]["poiId"] == pois_raw[0]["id"]][0]
    # parking
    planning_graph = disp.PlanningGraph(graph_in)
    assert planning_graph.get_end_go_to_node(pois_raw[1]["id"], pois_raw[1]["type"]) \
           == [node_data[0] for node_data in graph_in.graph.nodes(data=True)
               if node_data[1]["poiId"] == pois_raw[1]["id"]][0]
    # # poi z dokowaniem - ladowarka
    planning_graph = disp.PlanningGraph(graph_in)
    assert planning_graph.get_end_go_to_node(pois_raw[3]["id"], pois_raw[3]["type"]) \
           == [node_data[0] for node_data in graph_in.graph.nodes(data=True)
               if node_data[1]["poiId"] == pois_raw[3]["id"]
               and node_data[1]["nodeType"] == gc.new_node_type["dock"]][0]
    # #poi bez dokowania poi 6
    planning_graph = disp.PlanningGraph(graph_in)
    assert planning_graph.get_end_go_to_node(pois_raw[5]["id"], pois_raw[5]["type"]) \
           == [node_data[0] for node_data in graph_in.graph.nodes(data=True)
               if node_data[1]["poiId"] == pois_raw[5]["id"]
               and node_data[1]["nodeType"] == gc.new_node_type["wait"]][0]


@pytest.mark.planing_graph
def test_planning_graph_get_end_go_to_node_throws_error_when_missing_poi_on_graph():
    graph_in.graph = supervisor_graph
    planning_graph = disp.PlanningGraph(graph_in)
    try:
        planning_graph.get_end_go_to_node("54", gc.base_node_type["load"])
    except disp.PlaningGraphError as error:
        assert "POI 54 doesn't exist on graph." == str(error)
    else:
        assert False


@pytest.mark.planing_graph
def test_planning_graph_get_end_docking_node():
    graph_in.graph = supervisor_graph
    planning_graph = disp.PlanningGraph(graph_in)
    poi_id = "4"
    expected_result = [node_data[0] for node_data in graph_in.graph.nodes(data=True)
                       if node_data[1]["poiId"] == poi_id and node_data[1]["nodeType"] == gc.new_node_type["wait"]][0]
    assert planning_graph.get_end_docking_node(poi_id) == expected_result


@pytest.mark.planing_graph
def test_planning_graph_get_end_docking_node_throws_error_missing_poi():
    graph_in.graph = supervisor_graph
    planning_graph = disp.PlanningGraph(graph_in)
    poi_id = "10"
    try:
        planning_graph.get_end_docking_node(poi_id)
    except disp.PlaningGraphError as error:
        assert "POI {} doesn't exist on graph.".format(poi_id) == str(error)
    else:
        assert False


@pytest.mark.planing_graph
def test_planning_graph_get_end_docking_node_throws_error_no_docking_poi():
    graph_in.graph = supervisor_graph
    planning_graph = disp.PlanningGraph(graph_in)
    poi_id = "1"
    try:
        planning_graph.get_end_docking_node(poi_id)
    except disp.PlaningGraphError as error:
        assert "POI {} should be one of docking type.".format(poi_id) == str(error)
    else:
        assert False

    planning_graph = disp.PlanningGraph(graph_in)
    poi_id = "2"
    try:
        planning_graph.get_end_docking_node(poi_id)
    except disp.PlaningGraphError as error:
        assert "POI {} should be one of docking type.".format(poi_id) == str(error)
    else:
        assert False

    planning_graph = disp.PlanningGraph(graph_in)
    poi_id = "6"
    try:
        planning_graph.get_end_docking_node(poi_id)
    except disp.PlaningGraphError as error:
        assert "POI {} should be one of docking type.".format(poi_id) == str(error)
    else:
        assert False


@pytest.mark.planing_graph
def test_planning_graph_get_end_wait_node():
    planning_graph = disp.PlanningGraph(graph_in)
    # poi z dokowaniem
    assert planning_graph.get_end_wait_node(pois_raw[3]["id"], pois_raw[3]["type"]) \
           == [node_data[0] for node_data in graph_in.graph.nodes(data=True)
               if node_data[1]["poiId"] == pois_raw[3]["id"]
               and node_data[1]["nodeType"] == gc.new_node_type["undock"]][0]

    # poi bez dokowania
    assert planning_graph.get_end_wait_node(pois_raw[2]["id"], pois_raw[2]["type"]) \
           == [node_data[0] for node_data in graph_in.graph.nodes(data=True)
               if node_data[1]["poiId"] == pois_raw[2]["id"] and node_data[1]["nodeType"] == gc.new_node_type["end"]][0]


@pytest.mark.planing_graph
def test_planning_graph_get_end_wait_node_throws_error_missing_poi():
    planning_graph = disp.PlanningGraph(graph_in)
    poi_id = "10"
    try:
        planning_graph.get_end_wait_node(poi_id, gc.base_node_section_type["waitPOI"])
    except disp.PlaningGraphError as error:
        assert "POI {} doesn't exist on graph.".format(poi_id) == str(error)
    else:
        assert False


@pytest.mark.planing_graph
def test_planning_graph_get_end_wait_node_throws_error_no_stands_poi():
    # poi jest parkingiem
    planning_graph = disp.PlanningGraph(graph_in)
    try:
        planning_graph.get_end_wait_node(pois_raw[0]["id"], pois_raw[0]["type"])
    except disp.PlaningGraphError as error:
        assert "POI {} should be one of docking/wait POI.".format(pois_raw[0]["id"]) == str(error)
    else:
        assert False

    # poi jest kolejka
    planning_graph = disp.PlanningGraph(graph_in)
    try:
        planning_graph.get_end_wait_node(pois_raw[1]["id"], pois_raw[1]["type"])
    except disp.PlaningGraphError as error:
        assert "POI {} should be one of docking/wait POI.".format(pois_raw[1]["id"]) == str(error)
    else:
        assert False


@pytest.mark.planing_graph
def test_planning_graph_get_end_undocking_node():
    planning_graph = disp.PlanningGraph(graph_in)
    # poi z dokowaniem
    poi_id = "4"
    assert planning_graph.get_end_undocking_node(poi_id) \
           == [node_data[0] for node_data in graph_in.graph.nodes(data=True) if node_data[1]["poiId"] == poi_id
               and node_data[1]["nodeType"] == gc.new_node_type["end"]][0]


@pytest.mark.planing_graph
def test_planning_graph_get_end_undocking_node_throws_error_missing_poi():
    planning_graph = disp.PlanningGraph(graph_in)
    poi_id = "10"
    try:
        planning_graph.get_end_undocking_node(poi_id)
    except disp.PlaningGraphError as error:
        assert "POI {} doesn't exist on graph.".format(poi_id) == str(error)
    else:
        assert False


@pytest.mark.planing_graph
def test_planning_graph_get_end_undocking_node_throws_error_no_docking_poi():
    planning_graph = disp.PlanningGraph(graph_in)
    try:
        planning_graph.get_end_undocking_node(pois_raw[0]["id"])
    except disp.PlaningGraphError as error:
        assert "POI {} should be one of docking/wait POI.".format(pois_raw[0]["id"]) == str(error)
    else:
        assert False


@pytest.mark.planing_graph
def test_planning_graph_get_max_allowed_robots_using_pois():
    planning_graph = disp.PlanningGraph(graph_in)
    # dla kazdego typu poi oczekiwac moze co najmniej 1 robot
    # dla parkingow 1
    max_robots = planning_graph.get_max_allowed_robots_using_pois()
    assert max_robots[pois_raw[1]["id"]] == 1
    for max_poi_robots in max_robots.values():
        assert max_poi_robots >= 1

    expected_result = {'1': 10, '2': 1, '3': 8, '4': 11, '5': 6, '6': 8, '7': 6}
    # warunek na zwrócenie tych samych kluczy
    assert len(expected_result.keys() - max_robots.keys()) == 0
    assert len(max_robots.keys() - expected_result.keys()) == 0
    # warunek na zwrócenie tych samych wartości
    for i in expected_result.keys():
        assert expected_result[i] == max_robots[i]


@pytest.mark.planing_graph
def test_planning_graph_get_robots_on_edge_group_0():
    planning_graph = disp.PlanningGraph(graph_in)
    new_edge = (63, 64)
    planning_graph.graph.graph.edges[new_edge]["robots"] = ["r1", "r2", "r3"]
    given_robots = planning_graph.get_robots_on_edge(new_edge)
    assert len(given_robots) == 3
    assert given_robots == ["r1", "r2", "r3"]

    planning_graph = disp.PlanningGraph(graph_in)
    new_edge = (63, 64)
    robots = ["r1", "r2", "r3", "r1", "r2", "r3", "r1", "r2", "r3", "r1", "r2", "r3"]
    planning_graph.graph.graph.edges[new_edge]["robots"] = robots
    given_robots = planning_graph.get_robots_on_edge(new_edge)
    assert len(given_robots) == len(robots)
    assert given_robots == robots


@pytest.mark.planing_graph
def test_planning_graph_get_group_id_edges_belongs_to_the_same_group():
    planning_graph = disp.PlanningGraph(graph_in)
    # skrzyzowanie 71 -> 65, 80; 79 -> 65, 80; 64 -> 65, 80
    assert planning_graph.get_group_id((71, 65)) == planning_graph.get_group_id((71, 80))
    assert planning_graph.get_group_id((71, 65)) == planning_graph.get_group_id((79, 65))
    assert planning_graph.get_group_id((71, 65)) == planning_graph.get_group_id((79, 80))
    assert planning_graph.get_group_id((71, 65)) == planning_graph.get_group_id((64, 65))
    assert planning_graph.get_group_id((71, 65)) == planning_graph.get_group_id((64, 80))

    # poi 7:  23 5 6 7 8 18
    assert planning_graph.get_group_id((23, 5)) == planning_graph.get_group_id((5, 6))
    assert planning_graph.get_group_id((5, 6)) == planning_graph.get_group_id((6, 7))
    assert planning_graph.get_group_id((6, 7)) == planning_graph.get_group_id((7, 8))
    assert planning_graph.get_group_id((7, 8)) == planning_graph.get_group_id((8, 18))

    # poi 6:  22 15 16 24
    assert planning_graph.get_group_id((22, 15)) == planning_graph.get_group_id((15, 16))
    assert planning_graph.get_group_id((22, 15)) == planning_graph.get_group_id((16, 24))

    # parking:  31 17 32
    assert planning_graph.get_group_id((31, 17)) == planning_graph.get_group_id((17, 32))

    # waiting departure poi bez dokowania 3:
    assert planning_graph.get_group_id((58, 59)) == planning_graph.get_group_id((58, 29))
    assert planning_graph.get_group_id((58, 59)) == planning_graph.get_group_id((30, 59))
    assert planning_graph.get_group_id((58, 59)) == planning_graph.get_group_id((30, 29))
    assert planning_graph.get_group_id((58, 59)) == planning_graph.get_group_id((29, 13))
    assert planning_graph.get_group_id((58, 59)) == planning_graph.get_group_id((13, 14))
    assert planning_graph.get_group_id((58, 59)) == planning_graph.get_group_id((14, 30))
    assert planning_graph.get_group_id((58, 59)) == planning_graph.get_group_id((30, 59))
    assert planning_graph.get_group_id((58, 59)) == planning_graph.get_group_id((30, 29))
    assert planning_graph.get_group_id((58, 59)) == planning_graph.get_group_id((29, 13))
    assert planning_graph.get_group_id((58, 59)) == planning_graph.get_group_id((13, 14))
    assert planning_graph.get_group_id((58, 59)) == planning_graph.get_group_id((14, 30))

    print("group id", planning_graph.graph.graph.edges[(16, 24)])


@pytest.mark.planing_graph
def test_planning_graph_get_base_pois_edges():
    planning_graph = disp.PlanningGraph(graph_in)
    expected_result = {"1": (41, 19),
                       "2": (31, 17),
                       "3": (13, 14),
                       "4": (3, 4),
                       "5": (11, 12),
                       "6": (15, 16),
                       "7": (7, 8),
                       }
    result = planning_graph.get_base_pois_edges()
    assert len(expected_result) == len(result)

    for poi in expected_result:
        expected_edge = expected_result[poi]
        assert result[poi] == expected_edge


@pytest.mark.planing_graph
def test_planning_graph_is_intersection_edge():
    planning_graph = disp.PlanningGraph(graph_in)
    # skrzyżowanie POI - queue
    assert planning_graph.is_intersection_edge((42, 82))
    assert planning_graph.is_intersection_edge((35, 41))
    # skrzyżowanie POI - parking
    assert planning_graph.is_intersection_edge((68, 31))
    # skrzyżowanie POI - waiting-departure source node
    assert planning_graph.is_intersection_edge((58, 59))
    assert planning_graph.is_intersection_edge((58, 29))
    assert planning_graph.is_intersection_edge((39, 33))

    # krawędzie niebędące skrzyżowaniami
    assert not planning_graph.is_intersection_edge((41, 19))
    assert not planning_graph.is_intersection_edge((19, 42))
    assert not planning_graph.is_intersection_edge((31, 17))
    assert not planning_graph.is_intersection_edge((54, 55))
    assert not planning_graph.is_intersection_edge((56, 21))
    assert not planning_graph.is_intersection_edge((21, 1))
    assert not planning_graph.is_intersection_edge((1, 2))
    assert not planning_graph.is_intersection_edge((2, 3))
    assert not planning_graph.is_intersection_edge((3, 4))
    assert not planning_graph.is_intersection_edge((4, 20))
    assert not planning_graph.is_intersection_edge((20, 43))
    assert not planning_graph.is_intersection_edge((29, 13))
    assert not planning_graph.is_intersection_edge((13, 14))
    assert not planning_graph.is_intersection_edge((14, 30))


@pytest.mark.planing_graph
def test_get_task_travel_stands_time():
    planning_graph = disp.PlanningGraph(graph_in)
    node_id = 19
    task = {"id": "1",
            "behaviours": [{"id": "1", "parameters": {"to": "7", "name": disp.Behaviour.TYPES["goto"]}},
                           {"id": "2", "parameters": {"name": disp.Behaviour.TYPES["dock"]}},
                           {"id": "3", "parameters": {"name": disp.Behaviour.TYPES["wait"]}},
                           {"id": "4", "parameters": {"name": disp.Behaviour.TYPES["undock"]}},
                           {"id": "5", "parameters": {"to": "6", "name": disp.Behaviour.TYPES["goto"]}},
                           {"id": "6", "parameters": {"name": disp.Behaviour.TYPES["wait"]}}
                           ],
            "current_behaviour_index": -1,  # index tablicy nie zachowania
            "status": disp.Task.STATUS_LIST["TO_DO"],
            "robot": None,
            "start_time": "2018-06-29 07:37:27",
            "weight": 2,
            "priority": 2}

    drive_time = planning_graph.get_path_length(19, 5) + planning_graph.get_path_length(5, 6)
    drive_time += planning_graph.get_path_length(7, 8) + planning_graph.get_path_length(8, 15)
    stand_time = planning_graph.get_path_length(6, 7) + planning_graph.get_path_length(15, 16)

    result = planning_graph._get_task_travel_stands_time(node_id, disp.Task(task))
    assert result["drive_time"] == drive_time
    assert result["stand_time"] == stand_time


@pytest.mark.planing_graph
def test_select_next_task_passed_swap_start_time():
    planning_graph = disp.PlanningGraph(graph_in)
    task = disp.Task({"id": "1",
                      "behaviours": [{"id": "1", "parameters": {"to": "7", "name": disp.Behaviour.TYPES["goto"]}},
                                     {"id": "2", "parameters": {"name": disp.Behaviour.TYPES["dock"]}},
                                     {"id": "3", "parameters": {"name": disp.Behaviour.TYPES["wait"]}},
                                     {"id": "4", "parameters": {"name": disp.Behaviour.TYPES["undock"]}},
                                     {"id": "5", "parameters": {"to": "6", "name": disp.Behaviour.TYPES["goto"]}},
                                     {"id": "6", "parameters": {"name": disp.Behaviour.TYPES["wait"]}}
                                     ],
                      "current_behaviour_index": -1,  # index tablicy nie zachowania
                      "status": disp.Task.STATUS_LIST["TO_DO"],
                      "robot": None,
                      "start_time": "2018-06-29 07:37:27",
                      "weight": 2,
                      "priority": 2})

    swap_task = disp.Task({"id": "swap_1",
                           "behaviours": [{"id": "1", "parameters": {"to": "4", "name": disp.Behaviour.TYPES["goto"]}},
                                          {"id": "2", "parameters": {"name": disp.Behaviour.TYPES["dock"]}},
                                          {"id": "3", "parameters": {"name": disp.Behaviour.TYPES["wait"]}},
                                          {"id": "4", "parameters": {"name": disp.Behaviour.TYPES["undock"]}}
                                          ],
                           "current_behaviour_index": -1,  # index tablicy nie zachowania
                           "status": disp.Task.STATUS_LIST["TO_DO"],
                           "robot": None,
                           "start_time": "2018-06-29 07:37:27",
                           "weight": 2,
                           "priority": 2})

    robot = disp.Robot({"id": "1", "edge": (41, 19), "planningOn": True, "isFree": True, "timeRemaining": 0,
                        "poiId": "0"})

    result = planning_graph.select_next_task(task, swap_task, robot)
    assert result.id == swap_task.id


@pytest.mark.planing_graph
def test_select_next_task_critical_battery_lvl():
    planning_graph = disp.PlanningGraph(graph_in)
    task = disp.Task({"id": "1",
                      "behaviours": [{"id": "1", "parameters": {"to": "7", "name": disp.Behaviour.TYPES["goto"]}},
                                     {"id": "2", "parameters": {"name": disp.Behaviour.TYPES["dock"]}},
                                     {"id": "3", "parameters": {"name": disp.Behaviour.TYPES["wait"]}},
                                     {"id": "4", "parameters": {"name": disp.Behaviour.TYPES["undock"]}},
                                     {"id": "5", "parameters": {"to": "6", "name": disp.Behaviour.TYPES["goto"]}},
                                     {"id": "6", "parameters": {"name": disp.Behaviour.TYPES["wait"]}}
                                     ],
                      "current_behaviour_index": -1,  # index tablicy nie zachowania
                      "status": disp.Task.STATUS_LIST["TO_DO"],
                      "robot": None,
                      "start_time": "2018-06-29 07:37:27",
                      "weight": 2,
                      "priority": 2})

    now = datetime.strptime(datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "%Y-%m-%d %H:%M:%S")
    swap_time = (now + timedelta(minutes=15)).strftime("%Y-%m-%d %H:%M:%S")
    swap_task = disp.Task({"id": "swap_1",
                           "behaviours": [{"id": "1", "parameters": {"to": "4", "name": disp.Behaviour.TYPES["goto"]}},
                                          {"id": "2", "parameters": {"name": disp.Behaviour.TYPES["dock"]}},
                                          {"id": "3", "parameters": {"name": disp.Behaviour.TYPES["wait"]}},
                                          {"id": "4", "parameters": {"name": disp.Behaviour.TYPES["undock"]}}
                                          ],
                           "current_behaviour_index": -1,  # index tablicy nie zachowania
                           "status": disp.Task.STATUS_LIST["TO_DO"],
                           "robot": None,
                           "start_time": swap_time,
                           "weight": 2,
                           "priority": 2})

    robot = disp.Robot(
            {"id": "1", "edge": (41, 19), "planningOn": True, "isFree": True, "timeRemaining": 0, "poiId": "0"})
    robot.battery.max_capacity = 40.0
    robot.battery.capacity = 1.1
    robot.battery.drive_usage = 5.0
    robot.battery.stand_usage = 3.5
    robot.battery.remaining_working_time = 20.0
    print(robot.battery.get_critical_capacity())
    result = planning_graph.select_next_task(task, swap_task, robot)
    assert result.id == swap_task.id


@pytest.mark.planing_graph
def test_select_next_task_assign():
    planning_graph = disp.PlanningGraph(graph_in)
    task = disp.Task({"id": "1",
                      "behaviours": [{"id": "1", "parameters": {"to": "7", "name": disp.Behaviour.TYPES["goto"]}},
                                     {"id": "2", "parameters": {"name": disp.Behaviour.TYPES["dock"]}},
                                     {"id": "3", "parameters": {"name": disp.Behaviour.TYPES["wait"]}},
                                     {"id": "4", "parameters": {"name": disp.Behaviour.TYPES["undock"]}},
                                     {"id": "5", "parameters": {"to": "6", "name": disp.Behaviour.TYPES["goto"]}},
                                     {"id": "6", "parameters": {"name": disp.Behaviour.TYPES["wait"]}}
                                     ],
                      "current_behaviour_index": -1,  # index tablicy nie zachowania
                      "status": disp.Task.STATUS_LIST["TO_DO"],
                      "robot": None,
                      "start_time": "2018-06-29 07:37:27",
                      "weight": 2,
                      "priority": 2})

    now = datetime.strptime(datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "%Y-%m-%d %H:%M:%S")
    swap_time = (now + timedelta(minutes=15)).strftime("%Y-%m-%d %H:%M:%S")
    swap_task = disp.Task({"id": "swap_1",
                           "behaviours": [{"id": "1", "parameters": {"to": "4", "name": disp.Behaviour.TYPES["goto"]}},
                                          {"id": "2", "parameters": {"name": disp.Behaviour.TYPES["dock"]}},
                                          {"id": "3", "parameters": {"name": disp.Behaviour.TYPES["wait"]}},
                                          {"id": "4", "parameters": {"name": disp.Behaviour.TYPES["undock"]}}
                                          ],
                           "current_behaviour_index": -1,  # index tablicy nie zachowania
                           "status": disp.Task.STATUS_LIST["TO_DO"],
                           "robot": None,
                           "start_time": swap_time,
                           "weight": 2,
                           "priority": 2})

    robot = disp.Robot(
            {"id": "1", "edge": (41, 19), "planningOn": True, "isFree": True, "timeRemaining": 0, "poiId": "0"})
    robot.battery.max_capacity = 40.0
    robot.battery.capacity = 10.0
    robot.battery.drive_usage = 5.0
    robot.battery.stand_usage = 3.5
    robot.battery.remaining_working_time = 20.0
    result = planning_graph.select_next_task(task, swap_task, robot)
    assert result.id == task.id
    print(type(task) == disp.Task)
