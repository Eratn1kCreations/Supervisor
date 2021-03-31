# -*- coding: utf-8 -*-
import pytest
import copy
from test_data import *
import graph_creator as gc
import dispatcher as disp
from datetime import datetime, timedelta

def get_graph(robots_raw):
    graph_in = gc.SupervisorGraphCreator(node_dict, edge_dict, pois_raw)
    graph_in.graph = copy.deepcopy(supervisor_graph)
    for robot in robots_raw:
        graph_in.graph.edges[robot["edge"]]["robots"] = graph_in.graph.edges[robot["edge"]]["robots"] + [robot["id"]]
    return graph_in


# ------------------------------ Dispatcher ------------------------------ #
@pytest.mark.dispatcher
def test_dispatcher_check_if_method_exist():
    robots_raw = [
        {"id": "1", "edge": (41, 19), "planningOn": True, "isFree": True, "timeRemaining": 0, "poiId": "1"},
        {"id": "2", "edge": (41, 19), "planningOn": True, "isFree": True, "timeRemaining": 0, "poiId": "1"},
        {"id": "3", "edge": (41, 19), "planningOn": True, "isFree": True, "timeRemaining": 0, "poiId": "1"}
    ]
    robots = {robot["id"]: disp.Robot(robot) for robot in robots_raw}
    dispatcher = disp.Dispatcher(get_graph(robots_raw), robots)
    assert "get_plan_all_free_robots" in dir(dispatcher)
    assert "get_plan_selected_robot" in dir(dispatcher)
    assert "set_plan" in dir(dispatcher)  # OK
    assert "init_robots_plan" in dir(dispatcher)  # OK
    assert "set_tasks" in dir(dispatcher)  # OK
    assert "set_tasks_doing_by_robots" in dir(dispatcher)  # OK
    assert "set_task_assigned_to_robots" in dir(dispatcher)  # OK
    assert "set_other_tasks" in dir(dispatcher)
    assert "set_task_edge" in dir(dispatcher)  # OK
    assert "get_robots_id_blocking_used_poi" in dir(dispatcher)  # OK
    assert "get_robots_using_pois" in dir(dispatcher)  # OK
    assert "get_free_slots_in_pois" in dir(dispatcher)  # OK
    assert "get_free_task_to_assign" in dir(dispatcher)  # OK
    assert "assign_tasks_to_robots" in dir(dispatcher)  # OK
    assert "send_free_robots_to_parking" in dir(dispatcher)  # SKIP
    assert "send_busy_robots_to_parking" in dir(dispatcher)  # SKIP
    assert "get_undone_behaviour_node" in dir(dispatcher)  # OK


@pytest.mark.dispatcher
def test_dispatcher_get_undone_behaviour_node_goto_behaviour():
    robots_raw = [
        {"id": "1", "edge": (41, 19), "planningOn": True, "isFree": True, "timeRemaining": 0, "poiId": "1"}
    ]
    task_raw = {"id": "1",
                "behaviours": [{"id": "1", "parameters": {"to": "4", "name": disp.Behaviour.TYPES["goto"]}},
                               {"id": "2", "parameters": {"name": disp.Behaviour.TYPES["dock"]}},
                               {"id": "3", "parameters": {"name": disp.Behaviour.TYPES["wait"]}},
                               {"id": "4", "parameters": {"name": disp.Behaviour.TYPES["undock"]}}],
                "current_behaviour_index": -1,
                "status": disp.Task.STATUS_LIST["TO_DO"],
                "robot": None,
                "start_time": "2018-06-29 07:55:27",
                "weight": 3,
                "priority": 3}
    task = disp.Task(task_raw)
    robots = {robot["id"]: disp.Robot(robot) for robot in robots_raw}
    dispatcher = disp.Dispatcher(get_graph(robots_raw), robots)
    assert dispatcher.get_undone_behaviour_node(task) == 1

    robots_raw = [
        {"id": "1", "edge": (41, 19), "planningOn": True, "isFree": True, "timeRemaining": 0, "poiId": "1"}
    ]
    task_raw = {"id": "1",
                "behaviours": [{"id": "1", "parameters": {"to": "1", "name": disp.Behaviour.TYPES["goto"]}}],
                "current_behaviour_index": -1,
                "status": disp.Task.STATUS_LIST["TO_DO"],
                "robot": None,
                "start_time": "2018-06-29 07:55:27",
                "weight": 3,
                "priority": 3}
    task = disp.Task(task_raw)
    robots = {robot["id"]: disp.Robot(robot) for robot in robots_raw}
    dispatcher = disp.Dispatcher(get_graph(robots_raw), robots)
    assert dispatcher.get_undone_behaviour_node(task) == 19

    robots_raw = [
        {"id": "1", "edge": (41, 19), "planningOn": True, "isFree": True, "timeRemaining": 0, "poiId": "1"}
    ]
    task_raw = {"id": "1",
                "behaviours": [{"id": "1", "parameters": {"to": "2", "name": disp.Behaviour.TYPES["goto"]}}],
                "current_behaviour_index": -1,
                "status": disp.Task.STATUS_LIST["TO_DO"],
                "robot": None,
                "start_time": "2018-06-29 07:55:27",
                "weight": 3,
                "priority": 3}
    task = disp.Task(task_raw)
    robots = {robot["id"]: disp.Robot(robot) for robot in robots_raw}
    dispatcher = disp.Dispatcher(get_graph(robots_raw), robots)
    assert dispatcher.get_undone_behaviour_node(task) == 17

    robots_raw = [
        {"id": "1", "edge": (41, 19), "planningOn": True, "isFree": True, "timeRemaining": 0, "poiId": "1"}
    ]
    task_raw = {"id": "1",
                "behaviours": [{"id": "1", "parameters": {"to": "3", "name": disp.Behaviour.TYPES["goto"]}},
                               {"id": "3", "parameters": {"name": disp.Behaviour.TYPES["wait"]}}],
                "current_behaviour_index": -1,
                "status": disp.Task.STATUS_LIST["TO_DO"],
                "robot": None,
                "start_time": "2018-06-29 07:55:27",
                "weight": 3,
                "priority": 3}
    task = disp.Task(task_raw)
    robots = {robot["id"]: disp.Robot(robot) for robot in robots_raw}
    dispatcher = disp.Dispatcher(get_graph(robots_raw), robots)
    assert dispatcher.get_undone_behaviour_node(task) == 13

    robots_raw = [
        {"id": "1", "edge": (41, 19), "planningOn": True, "isFree": True, "timeRemaining": 0, "poiId": "1"}
    ]
    task_raw = {"id": "1",
                "behaviours": [{"id": "1", "parameters": {"to": "6", "name": disp.Behaviour.TYPES["goto"]}},
                               {"id": "3", "parameters": {"name": disp.Behaviour.TYPES["wait"]}}],
                "current_behaviour_index": -1,
                "status": disp.Task.STATUS_LIST["TO_DO"],
                "robot": None,
                "start_time": "2018-06-29 07:55:27",
                "weight": 3,
                "priority": 3}
    task = disp.Task(task_raw)
    robots = {robot["id"]: disp.Robot(robot) for robot in robots_raw}
    dispatcher = disp.Dispatcher(get_graph(robots_raw), robots)
    assert dispatcher.get_undone_behaviour_node(task) == 15


@pytest.mark.dispatcher
def test_dispatcher_get_undone_behaviour_node_dock_behaviour():
    robots_raw = [
        {"id": "1", "edge": (41, 19), "planningOn": True, "isFree": True, "timeRemaining": 0, "poiId": "1"}
    ]
    task_raw = {"id": "1",
                "behaviours": [{"id": "1", "parameters": {"to": "4", "name": disp.Behaviour.TYPES["goto"]}},
                               {"id": "2", "parameters": {"name": disp.Behaviour.TYPES["dock"]}},
                               {"id": "3", "parameters": {"name": disp.Behaviour.TYPES["wait"]}},
                               {"id": "4", "parameters": {"name": disp.Behaviour.TYPES["undock"]}}],
                "current_behaviour_index": 1,
                "status": disp.Task.STATUS_LIST["TO_DO"],
                "robot": "1",
                "start_time": "2018-06-29 07:55:27",
                "weight": 3,
                "priority": 3}
    task = disp.Task(task_raw)
    robots = {robot["id"]: disp.Robot(robot) for robot in robots_raw}
    dispatcher = disp.Dispatcher(get_graph(robots_raw), robots)
    print(dispatcher.get_undone_behaviour_node(task))
    assert dispatcher.get_undone_behaviour_node(task) == 2


@pytest.mark.dispatcher
def test_dispatcher_get_undone_behaviour_node_wait_behaviour():
    robots_raw = [
        {"id": "1", "edge": (41, 19), "planningOn": True, "isFree": True, "timeRemaining": 0, "poiId": "1"}
    ]
    task_raw = {"id": "1",
                "behaviours": [{"id": "1", "parameters": {"to": "4", "name": disp.Behaviour.TYPES["goto"]}},
                               {"id": "2", "parameters": {"name": disp.Behaviour.TYPES["dock"]}},
                               {"id": "3", "parameters": {"name": disp.Behaviour.TYPES["wait"]}},
                               {"id": "4", "parameters": {"name": disp.Behaviour.TYPES["undock"]}}],
                "current_behaviour_index": 2,
                "status": disp.Task.STATUS_LIST["TO_DO"],
                "robot": "1",
                "start_time": "2018-06-29 07:55:27",
                "weight": 3,
                "priority": 3}
    task = disp.Task(task_raw)
    robots = {robot["id"]: disp.Robot(robot) for robot in robots_raw}
    dispatcher = disp.Dispatcher(get_graph(robots_raw), robots)
    assert dispatcher.get_undone_behaviour_node(task) == 3


@pytest.mark.dispatcher
def test_dispatcher_get_undone_behaviour_node_dock_behaviour():
    robots_raw = [
        {"id": "1", "edge": (41, 19), "planningOn": True, "isFree": True, "timeRemaining": 0, "poiId": "1"}
    ]
    task_raw = {"id": "1",
                "behaviours": [{"id": "1", "parameters": {"to": "4", "name": disp.Behaviour.TYPES["goto"]}},
                               {"id": "2", "parameters": {"name": disp.Behaviour.TYPES["dock"]}},
                               {"id": "3", "parameters": {"name": disp.Behaviour.TYPES["wait"]}},
                               {"id": "4", "parameters": {"name": disp.Behaviour.TYPES["undock"]}}],
                "current_behaviour_index": 3,
                "status": disp.Task.STATUS_LIST["TO_DO"],
                "robot": "1",
                "start_time": "2018-06-29 07:55:27",
                "weight": 3,
                "priority": 3}
    task = disp.Task(task_raw)
    robots = {robot["id"]: disp.Robot(robot) for robot in robots_raw}
    dispatcher = disp.Dispatcher(get_graph(robots_raw), robots)
    assert dispatcher.get_undone_behaviour_node(task) == 4


@pytest.mark.dispatcher
def test_dispatcher_set_tasks_doing_by_robots_next_goal_free():
    robots_raw = [
        {"id": "1", "edge": (69, 70), "planningOn": True, "isFree": True, "timeRemaining": 0, "poiId": "0"},
        {"id": "2", "edge": (69, 70), "planningOn": True, "isFree": True, "timeRemaining": 0, "poiId": "0"},
        {"id": "3", "edge": (57, 58), "planningOn": True, "isFree": True, "timeRemaining": 0, "poiId": "0"},
        {"id": "4", "edge": (57, 58), "planningOn": True, "isFree": True, "timeRemaining": 0, "poiId": "4"}
    ]
    robots = {robot["id"]: disp.Robot(robot) for robot in robots_raw}
    tasks_raw = [{"id": "3",
                  "behaviours": [{"id": "1", "parameters": {"to": "4", "name": disp.Behaviour.TYPES["goto"]}},
                                 {"id": "2", "parameters": {"name": disp.Behaviour.TYPES["dock"]}},
                                 {"id": "3", "parameters": {"name": disp.Behaviour.TYPES["wait"]}},
                                 {"id": "4", "parameters": {"name": disp.Behaviour.TYPES["undock"]}},
                                 {"id": "5", "parameters": {"to": "1", "name": disp.Behaviour.TYPES["goto"]}}],
                  "current_behaviour_index": 0,  # index tablicy nie zachowania
                  "status": disp.Task.STATUS_LIST["IN_PROGRESS"],
                  "robot": "4",
                  "start_time": "2018-06-29 07:37:27",
                  "weight": 2,
                  "priority": 2
                  },
                 {"id": "4",
                  "behaviours": [{"id": "1", "parameters": {"to": "5", "name": disp.Behaviour.TYPES["goto"]}},
                                 {"id": "2", "parameters": {"name": disp.Behaviour.TYPES["dock"]}},
                                 {"id": "3", "parameters": {"name": disp.Behaviour.TYPES["wait"]}},
                                 {"id": "4", "parameters": {"name": disp.Behaviour.TYPES["undock"]}},
                                 {"id": "5", "parameters": {"to": "1", "name": disp.Behaviour.TYPES["goto"]}}],
                  "current_behaviour_index": -1,  # index tablicy nie zachowania
                  "status": disp.Task.STATUS_LIST["TO_DO"],
                  "robot": None,
                  "start_time": "2018-06-29 07:27:27",
                  "weight": 2,
                  "priority": 2
                  },
                 {"id": "2",
                  "behaviours": [{"id": "1", "parameters": {"to": "5", "name": disp.Behaviour.TYPES["goto"]}},
                                 {"id": "2", "parameters": {"name": disp.Behaviour.TYPES["dock"]}},
                                 {"id": "3", "parameters": {"name": disp.Behaviour.TYPES["wait"]}},
                                 {"id": "4", "parameters": {"name": disp.Behaviour.TYPES["undock"]}},
                                 {"id": "5", "parameters": {"to": "1", "name": disp.Behaviour.TYPES["goto"]}}],
                  "current_behaviour_index": 0,  # index tablicy nie zachowania
                  "status": disp.Task.STATUS_LIST["IN_PROGRESS"],
                  "robot": "3",
                  "start_time": "2018-06-29 07:15:27",
                  "weight": 3,
                  "priority": 3
                  },
                 {"id": "1",
                  "behaviours": [{"id": "1", "parameters": {"to": "7", "name": disp.Behaviour.TYPES["goto"]}},
                                 {"id": "2", "parameters": {"name": disp.Behaviour.TYPES["dock"]}},
                                 {"id": "3", "parameters": {"name": disp.Behaviour.TYPES["wait"]}},
                                 {"id": "4", "parameters": {"name": disp.Behaviour.TYPES["undock"]}},
                                 {"id": "5", "parameters": {"to": "1", "name": disp.Behaviour.TYPES["goto"]}}],
                  "current_behaviour_index": -1,  # index tablicy nie zachowania
                  "status": disp.Task.STATUS_LIST["TO_DO"],
                  "robot": None,
                  "start_time": "2018-06-29 07:23:27",
                  "weight": 2,
                  "priority": 2
                  }
                 ]
    tasks = [disp.Task(data) for data in tasks_raw]
    dispatcher = disp.Dispatcher(get_graph(robots_raw), robots)
    dispatcher.set_tasks(tasks)
    dispatcher.set_tasks_doing_by_robots()
    expected_assign = {"4": "3", "3": "2"}  # robot_id: task id
    for robot in dispatcher.robots_plan.robots.values():
        if robot.id in expected_assign:
            assert expected_assign[robot.id] == robot.task.id

    assert len(dispatcher.unanalyzed_tasks_handler.tasks) == 2


@pytest.mark.dispatcher
def test_dispatcher_set_tasks_doing_by_robots_next_is_blocked():
    robots_raw = [
        {"id": "1", "edge": (33, 23), "planningOn": True, "isFree": True, "timeRemaining": 0, "poiId": "0"},
        {"id": "2", "edge": (33, 23), "planningOn": True, "isFree": True, "timeRemaining": 0, "poiId": "0"},
        {"id": "3", "edge": (33, 23), "planningOn": True, "isFree": True, "timeRemaining": 0, "poiId": "0"},
        {"id": "4", "edge": (33, 23), "planningOn": True, "isFree": True, "timeRemaining": 0, "poiId": "0"},
        {"id": "5", "edge": (33, 23), "planningOn": True, "isFree": True, "timeRemaining": 0, "poiId": "0"},
        {"id": "6", "edge": (5, 6), "planningOn": True, "isFree": True, "timeRemaining": 0, "poiId": "0"},
        {"id": "7", "edge": (15, 16), "planningOn": True, "isFree": True, "timeRemaining": 0, "poiId": "0"}
    ]
    robots = {robot["id"]: disp.Robot(robot) for robot in robots_raw}
    tasks_raw = [{"id": "1",
                  "behaviours": [{"id": "1", "parameters": {"to": "7", "name": disp.Behaviour.TYPES["goto"]}},
                                 {"id": "2", "parameters": {"name": disp.Behaviour.TYPES["dock"]}},
                                 {"id": "3", "parameters": {"name": disp.Behaviour.TYPES["wait"]}},
                                 {"id": "4", "parameters": {"name": disp.Behaviour.TYPES["undock"]}},
                                 {"id": "5", "parameters": {"to": "1", "name": disp.Behaviour.TYPES["goto"]}}],
                  "current_behaviour_index": 0,  # index tablicy nie zachowania
                  "status": disp.Task.STATUS_LIST["IN_PROGRESS"],
                  "robot": "1",
                  "start_time": "2018-06-29 07:37:27",
                  "weight": 2,
                  "priority": 2
                  },
                 {"id": "2",
                  "behaviours": [{"id": "1", "parameters": {"to": "7", "name": disp.Behaviour.TYPES["goto"]}},
                                 {"id": "2", "parameters": {"name": disp.Behaviour.TYPES["dock"]}},
                                 {"id": "3", "parameters": {"name": disp.Behaviour.TYPES["wait"]}},
                                 {"id": "4", "parameters": {"name": disp.Behaviour.TYPES["undock"]}},
                                 {"id": "5", "parameters": {"to": "1", "name": disp.Behaviour.TYPES["goto"]}}],
                  "current_behaviour_index": 0,  # index tablicy nie zachowania
                  "status": disp.Task.STATUS_LIST["IN_PROGRESS"],
                  "robot": "2",
                  "start_time": "2018-06-29 07:37:27",
                  "weight": 2,
                  "priority": 2
                  },
                 {"id": "3",
                  "behaviours": [{"id": "1", "parameters": {"to": "7", "name": disp.Behaviour.TYPES["goto"]}},
                                 {"id": "2", "parameters": {"name": disp.Behaviour.TYPES["dock"]}},
                                 {"id": "3", "parameters": {"name": disp.Behaviour.TYPES["wait"]}},
                                 {"id": "4", "parameters": {"name": disp.Behaviour.TYPES["undock"]}},
                                 {"id": "5", "parameters": {"to": "1", "name": disp.Behaviour.TYPES["goto"]}}],
                  "current_behaviour_index": 0,  # index tablicy nie zachowania
                  "status": disp.Task.STATUS_LIST["IN_PROGRESS"],
                  "robot": "3",
                  "start_time": "2018-06-29 07:37:27",
                  "weight": 2,
                  "priority": 2
                  },
                 {"id": "4",
                  "behaviours": [{"id": "1", "parameters": {"to": "7", "name": disp.Behaviour.TYPES["goto"]}},
                                 {"id": "2", "parameters": {"name": disp.Behaviour.TYPES["dock"]}},
                                 {"id": "3", "parameters": {"name": disp.Behaviour.TYPES["wait"]}},
                                 {"id": "4", "parameters": {"name": disp.Behaviour.TYPES["undock"]}},
                                 {"id": "5", "parameters": {"to": "1", "name": disp.Behaviour.TYPES["goto"]}}],
                  "current_behaviour_index": 0,  # index tablicy nie zachowania
                  "status": disp.Task.STATUS_LIST["IN_PROGRESS"],
                  "robot": "4",
                  "start_time": "2018-06-29 07:37:27",
                  "weight": 2,
                  "priority": 2
                  },
                 {"id": "5",
                  "behaviours": [{"id": "1", "parameters": {"to": "7", "name": disp.Behaviour.TYPES["goto"]}},
                                 {"id": "2", "parameters": {"name": disp.Behaviour.TYPES["dock"]}},
                                 {"id": "3", "parameters": {"name": disp.Behaviour.TYPES["wait"]}},
                                 {"id": "4", "parameters": {"name": disp.Behaviour.TYPES["undock"]}},
                                 {"id": "5", "parameters": {"to": "1", "name": disp.Behaviour.TYPES["goto"]}}],
                  "current_behaviour_index": 0,  # index tablicy nie zachowania
                  "status": disp.Task.STATUS_LIST["IN_PROGRESS"],
                  "robot": "5",
                  "start_time": "2018-06-29 07:37:27",
                  "weight": 2,
                  "priority": 2
                  },
                 {"id": "6",
                  "behaviours": [{"id": "1", "parameters": {"to": "7", "name": disp.Behaviour.TYPES["goto"]}},
                                 {"id": "2", "parameters": {"name": disp.Behaviour.TYPES["dock"]}},
                                 {"id": "3", "parameters": {"name": disp.Behaviour.TYPES["wait"]}},
                                 {"id": "4", "parameters": {"name": disp.Behaviour.TYPES["undock"]}},
                                 {"id": "5", "parameters": {"to": "1", "name": disp.Behaviour.TYPES["goto"]}}],
                  "current_behaviour_index": 2,  # index tablicy nie zachowania
                  "status": disp.Task.STATUS_LIST["IN_PROGRESS"],
                  "robot": "6",
                  "start_time": "2018-06-29 07:37:27",
                  "weight": 2,
                  "priority": 2
                  },
                 {"id": "7",
                  "behaviours": [{"id": "1", "parameters": {"to": "6", "name": disp.Behaviour.TYPES["goto"]}},
                                 {"id": "3", "parameters": {"name": disp.Behaviour.TYPES["wait"]}},
                                 {"id": "1", "parameters": {"to": "7", "name": disp.Behaviour.TYPES["goto"]}},
                                 {"id": "2", "parameters": {"name": disp.Behaviour.TYPES["dock"]}},
                                 {"id": "3", "parameters": {"name": disp.Behaviour.TYPES["wait"]}},
                                 {"id": "4", "parameters": {"name": disp.Behaviour.TYPES["undock"]}}],
                  "current_behaviour_index": 2,  # index tablicy nie zachowania
                  "status": disp.Task.STATUS_LIST["IN_PROGRESS"],
                  "robot": "7",
                  "start_time": "2018-06-29 07:37:27",
                  "weight": 2,
                  "priority": 2
                  }
                 ]
    tasks = [disp.Task(data) for data in tasks_raw]
    dispatcher = disp.Dispatcher(get_graph(robots_raw), robots)
    dispatcher.set_tasks(tasks)
    dispatcher.set_tasks_doing_by_robots()
    robots = {"1": {"edge": None, "end_beh": None},
              "2": {"edge": None, "end_beh": None},
              "3": {"edge": None, "end_beh": None},
              "4": {"edge": None, "end_beh": None},
              "5": {"edge": None, "end_beh": None},
              "6": {"edge": (6, 7), "end_beh": True},
              "7": {"edge": None, "end_beh": None}}
    for robot in dispatcher.robots_plan.robots.values():
        assert robot.id == robot.task.id
        assert robot.next_task_edge == robots[robot.id]["edge"]
        assert robot.end_beh_edge == robots[robot.id]["end_beh"]

    assert len(dispatcher.unanalyzed_tasks_handler.tasks) == 0


@pytest.mark.dispatcher
def test_dispatcher_set_tasks_doing_by_robots_waiting_departure_poi_5():
    robots_raw = [
        {"id": "1", "edge": (9, 10), "planningOn": True, "isFree": True, "timeRemaining": 0, "poiId": "0"},
        {"id": "2", "edge": (44, 45), "planningOn": True, "isFree": True, "timeRemaining": 0, "poiId": "0"}
    ]
    robots = {robot["id"]: disp.Robot(robot) for robot in robots_raw}
    tasks_raw = [{"id": "1",
                  "behaviours": [{"id": "1", "parameters": {"to": "5", "name": disp.Behaviour.TYPES["goto"]}},
                                 {"id": "2", "parameters": {"name": disp.Behaviour.TYPES["dock"]}},
                                 {"id": "3", "parameters": {"name": disp.Behaviour.TYPES["wait"]}},
                                 {"id": "4", "parameters": {"name": disp.Behaviour.TYPES["undock"]}}],
                  "current_behaviour_index": 2,  # index tablicy nie zachowania
                  "status": disp.Task.STATUS_LIST["IN_PROGRESS"],
                  "robot": "1",
                  "start_time": "2018-06-29 07:37:27",
                  "weight": 2,
                  "priority": 2
                  },
                 {"id": "2",
                  "behaviours": [{"id": "1", "parameters": {"to": "5", "name": disp.Behaviour.TYPES["goto"]}},
                                 {"id": "2", "parameters": {"name": disp.Behaviour.TYPES["dock"]}},
                                 {"id": "3", "parameters": {"name": disp.Behaviour.TYPES["wait"]}},
                                 {"id": "4", "parameters": {"name": disp.Behaviour.TYPES["undock"]}}],
                  "current_behaviour_index": 0,  # index tablicy nie zachowania
                  "status": disp.Task.STATUS_LIST["IN_PROGRESS"],
                  "robot": "2",
                  "start_time": "2018-06-29 07:36:27",
                  "weight": 2,
                  "priority": 2
                  }
                 ]
    tasks = [disp.Task(data) for data in tasks_raw]
    dispatcher = disp.Dispatcher(get_graph(robots_raw), robots)
    dispatcher.set_tasks(tasks)
    dispatcher.set_tasks_doing_by_robots()
    robots = {"1": {"edge": (10, 11), "end_beh": True},
              "2": {"edge": None, "end_beh": None}}
    for robot in dispatcher.robots_plan.robots.values():
        # print(robot.id, robot.task.id, robot.next_task_edge, robot.end_beh_edge)
        assert robot.id == robot.task.id
        assert robot.next_task_edge == robots[robot.id]["edge"]
        assert robot.end_beh_edge == robots[robot.id]["end_beh"]

    assert len(dispatcher.unanalyzed_tasks_handler.tasks) == 0


@pytest.mark.dispatcher
def test_dispatcher_set_tasks_doing_by_robots_waiting_departure_poi_5_intersection_priority():
    robots_raw = [
        {"id": "1", "edge": (80, 81), "planningOn": True, "isFree": True, "timeRemaining": 0, "poiId": "0"},
        {"id": "2", "edge": (25, 26), "planningOn": True, "isFree": True, "timeRemaining": 0, "poiId": "0"}
    ]
    robots = {robot["id"]: disp.Robot(robot) for robot in robots_raw}
    tasks_raw = [{"id": "1",
                  "behaviours": [{"id": "1", "parameters": {"to": "5", "name": disp.Behaviour.TYPES["goto"]}},
                                 {"id": "2", "parameters": {"name": disp.Behaviour.TYPES["dock"]}},
                                 {"id": "3", "parameters": {"name": disp.Behaviour.TYPES["wait"]}},
                                 {"id": "4", "parameters": {"name": disp.Behaviour.TYPES["undock"]}}],
                  "current_behaviour_index": 0,  # index tablicy nie zachowania
                  "status": disp.Task.STATUS_LIST["IN_PROGRESS"],
                  "robot": "1",
                  "start_time": "2018-06-29 07:37:27",
                  "weight": 2,
                  "priority": 2
                  },
                 {"id": "2",
                  "behaviours": [{"id": "1", "parameters": {"to": "5", "name": disp.Behaviour.TYPES["goto"]}},
                                 {"id": "2", "parameters": {"name": disp.Behaviour.TYPES["dock"]}},
                                 {"id": "3", "parameters": {"name": disp.Behaviour.TYPES["wait"]}},
                                 {"id": "4", "parameters": {"name": disp.Behaviour.TYPES["undock"]}}],
                  "current_behaviour_index": 0,  # index tablicy nie zachowania
                  "status": disp.Task.STATUS_LIST["IN_PROGRESS"],
                  "robot": "2",
                  "start_time": "2018-06-29 07:36:27",
                  "weight": 2,
                  "priority": 2
                  }
                 ]
    tasks = [disp.Task(data) for data in tasks_raw]
    dispatcher = disp.Dispatcher(get_graph(robots_raw), robots)
    dispatcher.set_tasks(tasks)
    dispatcher.set_tasks_doing_by_robots()
    robots = {"1": {"edge": (81, 44), "end_beh": False},
              "2": {"edge": None, "end_beh": None}}
    for robot in dispatcher.robots_plan.robots.values():
        # print(robot.id, robot.task.id, robot.next_task_edge, robot.end_beh_edge)
        assert robot.id == robot.task.id
        assert robot.next_task_edge == robots[robot.id]["edge"]
        assert robot.end_beh_edge == robots[robot.id]["end_beh"]

    assert len(dispatcher.unanalyzed_tasks_handler.tasks) == 0


@pytest.mark.dispatcher
def test_dispatcher_set_task_assigned_to_robots():
    robots_raw = [
        {"id": "1", "edge": (41, 19), "planningOn": True, "isFree": True, "timeRemaining": 0, "poiId": "0"},
        {"id": "2", "edge": (41, 19), "planningOn": True, "isFree": True, "timeRemaining": 0, "poiId": "0"}
    ]
    robots = {robot["id"]: disp.Robot(robot) for robot in robots_raw}
    tasks_raw = [{"id": "1",
                  "behaviours": [{"id": "1", "parameters": {"to": "5", "name": disp.Behaviour.TYPES["goto"]}},
                                 {"id": "2", "parameters": {"name": disp.Behaviour.TYPES["dock"]}},
                                 {"id": "3", "parameters": {"name": disp.Behaviour.TYPES["wait"]}},
                                 {"id": "4", "parameters": {"name": disp.Behaviour.TYPES["undock"]}}],
                  "current_behaviour_index": -1,  # index tablicy nie zachowania
                  "status": disp.Task.STATUS_LIST["TO_DO"],
                  "robot": "2",
                  "start_time": "2018-06-29 07:37:27",
                  "weight": 2,
                  "priority": 2},
                 {"id": "2",
                  "behaviours": [{"id": "1", "parameters": {"to": "5", "name": disp.Behaviour.TYPES["goto"]}},
                                 {"id": "2", "parameters": {"name": disp.Behaviour.TYPES["dock"]}},
                                 {"id": "3", "parameters": {"name": disp.Behaviour.TYPES["wait"]}},
                                 {"id": "4", "parameters": {"name": disp.Behaviour.TYPES["undock"]}}],
                  "current_behaviour_index": -1,  # index tablicy nie zachowania
                  "status": disp.Task.STATUS_LIST["TO_DO"],
                  "robot": "1",
                  "start_time": "2018-06-29 07:36:27",
                  "weight": 2,
                  "priority": 2}]
    tasks = [disp.Task(data) for data in tasks_raw]
    dispatcher = disp.Dispatcher(get_graph(robots_raw), robots)
    dispatcher.set_tasks(tasks)
    dispatcher.set_task_assigned_to_robots()
    robots = {"1": {"edge": (19, 42), "end_beh": False, "task": "2"},
              "2": {"edge": (19, 42), "end_beh": False, "task": "1"}}
    for robot in dispatcher.robots_plan.robots.values():
        # print(robot.id, robot.task.id, robot.next_task_edge, robot.end_beh_edge)
        assert robot.task.id == robots[robot.id]["task"]
        assert robot.next_task_edge == robots[robot.id]["edge"]
        assert robot.end_beh_edge == robots[robot.id]["end_beh"]

    assert len(dispatcher.unanalyzed_tasks_handler.tasks) == 0

    # zestaww 2
    robots_raw = [
        {"id": "1", "edge": ((41, 19)), "planningOn": True, "isFree": True, "timeRemaining": 0, "poiId": "0"},
        {"id": "2", "edge": (41, 19), "planningOn": True, "isFree": True, "timeRemaining": 0, "poiId": "0"}
    ]
    robots = {robot["id"]: disp.Robot(robot) for robot in robots_raw}
    tasks_raw = [{"id": "1",
                  "behaviours": [{"id": "1", "parameters": {"to": "5", "name": disp.Behaviour.TYPES["goto"]}},
                                 {"id": "2", "parameters": {"name": disp.Behaviour.TYPES["dock"]}},
                                 {"id": "3", "parameters": {"name": disp.Behaviour.TYPES["wait"]}},
                                 {"id": "4", "parameters": {"name": disp.Behaviour.TYPES["undock"]}}],
                  "current_behaviour_index": -1,  # index tablicy nie zachowania
                  "status": disp.Task.STATUS_LIST["TO_DO"],
                  "robot": "2",
                  "start_time": "2018-06-29 07:37:27",
                  "weight": 2,
                  "priority": 2},
                 {"id": "3",
                  "behaviours": [{"id": "1", "parameters": {"to": "5", "name": disp.Behaviour.TYPES["goto"]}},
                                 {"id": "2", "parameters": {"name": disp.Behaviour.TYPES["dock"]}},
                                 {"id": "3", "parameters": {"name": disp.Behaviour.TYPES["wait"]}},
                                 {"id": "4", "parameters": {"name": disp.Behaviour.TYPES["undock"]}}],
                  "current_behaviour_index": -1,  # index tablicy nie zachowania
                  "status": disp.Task.STATUS_LIST["TO_DO"],
                  "robot": None,
                  "start_time": "2018-06-29 07:36:27",
                  "weight": 2,
                  "priority": 2},
                 {"id": "2",
                  "behaviours": [{"id": "1", "parameters": {"to": "5", "name": disp.Behaviour.TYPES["goto"]}},
                                 {"id": "2", "parameters": {"name": disp.Behaviour.TYPES["dock"]}},
                                 {"id": "3", "parameters": {"name": disp.Behaviour.TYPES["wait"]}},
                                 {"id": "4", "parameters": {"name": disp.Behaviour.TYPES["undock"]}}],
                  "current_behaviour_index": -1,  # index tablicy nie zachowania
                  "status": disp.Task.STATUS_LIST["TO_DO"],
                  "robot": "1",
                  "start_time": "2018-06-29 07:36:27",
                  "weight": 2,
                  "priority": 2}]
    tasks = [disp.Task(data) for data in tasks_raw]
    dispatcher = disp.Dispatcher(get_graph(robots_raw), robots)
    dispatcher.set_tasks(tasks)
    dispatcher.set_task_assigned_to_robots()
    robots = {"1": {"edge": (19, 42), "end_beh": False, "task": "2"},
              "2": {"edge": (19, 42), "end_beh": False, "task": "1"}}
    for robot in dispatcher.robots_plan.robots.values():
        # print(robot.id, robot.task.id, robot.next_task_edge, robot.end_beh_edge)
        assert robot.task.id == robots[robot.id]["task"]
        assert robot.next_task_edge == robots[robot.id]["edge"]
        assert robot.end_beh_edge == robots[robot.id]["end_beh"]

    assert len(dispatcher.unanalyzed_tasks_handler.tasks) == 1


@pytest.mark.dispatcher
def test_dispatcher_set_doing_and_assigned_task_to_robots():
    robots_raw = [
        {"id": "1", "edge": (41, 19), "planningOn": True, "isFree": True, "timeRemaining": 0, "poiId": "0"},
        {"id": "2", "edge": (41, 19), "planningOn": True, "isFree": True, "timeRemaining": 0, "poiId": "0"}
    ]
    robots = {robot["id"]: disp.Robot(robot) for robot in robots_raw}
    tasks_raw = [{"id": "1",
                  "behaviours": [{"id": "1", "parameters": {"to": "5", "name": disp.Behaviour.TYPES["goto"]}},
                                 {"id": "2", "parameters": {"name": disp.Behaviour.TYPES["dock"]}},
                                 {"id": "3", "parameters": {"name": disp.Behaviour.TYPES["wait"]}},
                                 {"id": "4", "parameters": {"name": disp.Behaviour.TYPES["undock"]}}],
                  "current_behaviour_index": -1,  # index tablicy nie zachowania
                  "status": disp.Task.STATUS_LIST["TO_DO"],
                  "robot": "2",
                  "start_time": "2018-06-29 07:37:27",
                  "weight": 2,
                  "priority": 2},
                 {"id": "3",
                  "behaviours": [{"id": "1", "parameters": {"to": "5", "name": disp.Behaviour.TYPES["goto"]}},
                                 {"id": "2", "parameters": {"name": disp.Behaviour.TYPES["dock"]}},
                                 {"id": "3", "parameters": {"name": disp.Behaviour.TYPES["wait"]}},
                                 {"id": "4", "parameters": {"name": disp.Behaviour.TYPES["undock"]}}],
                  "current_behaviour_index": 0,  # index tablicy nie zachowania
                  "status": disp.Task.STATUS_LIST["IN_PROGRESS"],
                  "robot": "2",
                  "start_time": "2018-06-29 07:36:27",
                  "weight": 2,
                  "priority": 2},
                 {"id": "2",
                  "behaviours": [{"id": "1", "parameters": {"to": "5", "name": disp.Behaviour.TYPES["goto"]}},
                                 {"id": "2", "parameters": {"name": disp.Behaviour.TYPES["dock"]}},
                                 {"id": "3", "parameters": {"name": disp.Behaviour.TYPES["wait"]}},
                                 {"id": "4", "parameters": {"name": disp.Behaviour.TYPES["undock"]}}],
                  "current_behaviour_index": -1,  # index tablicy nie zachowania
                  "status": disp.Task.STATUS_LIST["TO_DO"],
                  "robot": "1",
                  "start_time": "2018-06-29 07:36:27",
                  "weight": 2,
                  "priority": 2}]
    tasks = [disp.Task(data) for data in tasks_raw]
    dispatcher = disp.Dispatcher(get_graph(robots_raw), robots)
    dispatcher.set_tasks(tasks)
    dispatcher.set_tasks_doing_by_robots()
    dispatcher.set_task_assigned_to_robots()
    robots = {"1": {"edge": (19, 42), "end_beh": False, "task": "2"},
              "2": {"edge": (19, 42), "end_beh": False, "task": "3"}}
    for robot in dispatcher.robots_plan.robots.values():
        # print(robot.id, robot.task.id, robot.next_task_edge, robot.end_beh_edge)
        assert robot.task.id == robots[robot.id]["task"]
        assert robot.next_task_edge == robots[robot.id]["edge"]
        assert robot.end_beh_edge == robots[robot.id]["end_beh"]

    assert len(dispatcher.unanalyzed_tasks_handler.tasks) == 1


@pytest.mark.dispatcher
def test_dispatcher_get_robots_using_pois():
    robots_raw = [
        {"id": "1", "edge": (69, 70), "planningOn": True, "isFree": True, "timeRemaining": 0, "poiId": "0"},
        {"id": "2", "edge": (78, 79), "planningOn": True, "isFree": True, "timeRemaining": 0, "poiId": "0"},
        {"id": "3", "edge": (74, 75), "planningOn": True, "isFree": True, "timeRemaining": 0, "poiId": "0"},
        {"id": "4", "edge": (63, 64), "planningOn": True, "isFree": True, "timeRemaining": 0, "poiId": "0"},
        {"id": "5", "edge": (38, 39), "planningOn": True, "isFree": True, "timeRemaining": 0, "poiId": "0"},
        {"id": "6", "edge": (67, 68), "planningOn": True, "isFree": True, "timeRemaining": 0, "poiId": "0"},
        {"id": "7", "edge": (49, 72), "planningOn": True, "isFree": True, "timeRemaining": 0, "poiId": "0"},
        {"id": "8", "edge": (50, 51), "planningOn": True, "isFree": True, "timeRemaining": 0, "poiId": "0"},
        {"id": "9", "edge": (87, 88), "planningOn": True, "isFree": True, "timeRemaining": 0, "poiId": "0"},
        {"id": "10", "edge": (41, 19), "planningOn": True, "isFree": True, "timeRemaining": 0, "poiId": "0"}
    ]
    robots = {robot["id"]: disp.Robot(robot) for robot in robots_raw}
    tasks_raw = [{"id": "1",
                  "behaviours": [{"id": "1", "parameters": {"to": "4", "name": disp.Behaviour.TYPES["goto"]}},
                                 {"id": "2", "parameters": {"name": disp.Behaviour.TYPES["dock"]}},
                                 {"id": "3", "parameters": {"name": disp.Behaviour.TYPES["wait"]}},
                                 {"id": "4", "parameters": {"name": disp.Behaviour.TYPES["undock"]}}],
                  "current_behaviour_index": 0,  # index tablicy nie zachowania
                  "status": disp.Task.STATUS_LIST["IN_PROGRESS"],
                  "robot": "10",
                  "start_time": "2018-06-29 07:37:27",
                  "weight": 2,
                  "priority": 2},
                 {"id": "2",
                  "behaviours": [{"id": "1", "parameters": {"to": "7", "name": disp.Behaviour.TYPES["goto"]}},
                                 {"id": "2", "parameters": {"name": disp.Behaviour.TYPES["dock"]}},
                                 {"id": "3", "parameters": {"name": disp.Behaviour.TYPES["wait"]}},
                                 {"id": "4", "parameters": {"name": disp.Behaviour.TYPES["undock"]}}],
                  "current_behaviour_index": 0,  # index tablicy nie zachowania
                  "status": disp.Task.STATUS_LIST["IN_PROGRESS"],
                  "robot": "9",
                  "start_time": "2018-06-29 07:37:27",
                  "weight": 2,
                  "priority": 2},
                 {"id": "3",
                  "behaviours": [{"id": "1", "parameters": {"to": "5", "name": disp.Behaviour.TYPES["goto"]}},
                                 {"id": "2", "parameters": {"name": disp.Behaviour.TYPES["dock"]}},
                                 {"id": "3", "parameters": {"name": disp.Behaviour.TYPES["wait"]}},
                                 {"id": "4", "parameters": {"name": disp.Behaviour.TYPES["undock"]}}],
                  "current_behaviour_index": 0,  # index tablicy nie zachowania
                  "status": disp.Task.STATUS_LIST["IN_PROGRESS"],
                  "robot": "8",
                  "start_time": "2018-06-29 07:37:27",
                  "weight": 2,
                  "priority": 2},
                 {"id": "4",
                  "behaviours": [{"id": "1", "parameters": {"to": "6", "name": disp.Behaviour.TYPES["goto"]}},
                                 {"id": "2", "parameters": {"name": disp.Behaviour.TYPES["wait"]}}],
                  "current_behaviour_index": 0,  # index tablicy nie zachowania
                  "status": disp.Task.STATUS_LIST["IN_PROGRESS"],
                  "robot": "7",
                  "start_time": "2018-06-29 07:37:27",
                  "weight": 2,
                  "priority": 2},
                 {"id": "5",
                  "behaviours": [{"id": "1", "parameters": {"to": "3", "name": disp.Behaviour.TYPES["goto"]}},
                                 {"id": "2", "parameters": {"name": disp.Behaviour.TYPES["wait"]}}],
                  "current_behaviour_index": 0,  # index tablicy nie zachowania
                  "status": disp.Task.STATUS_LIST["IN_PROGRESS"],
                  "robot": "6",
                  "start_time": "2018-06-29 07:37:27",
                  "weight": 2,
                  "priority": 2},
                 {"id": "6",
                  "behaviours": [{"id": "1", "parameters": {"to": "7", "name": disp.Behaviour.TYPES["goto"]}},
                                 {"id": "2", "parameters": {"name": disp.Behaviour.TYPES["dock"]}},
                                 {"id": "3", "parameters": {"name": disp.Behaviour.TYPES["wait"]}},
                                 {"id": "4", "parameters": {"name": disp.Behaviour.TYPES["undock"]}}],
                  "current_behaviour_index": 0,  # index tablicy nie zachowania
                  "status": disp.Task.STATUS_LIST["IN_PROGRESS"],
                  "robot": "5",
                  "start_time": "2018-06-29 07:37:27",
                  "weight": 2,
                  "priority": 2},
                 {"id": "7",
                  "behaviours": [{"id": "1", "parameters": {"to": "4", "name": disp.Behaviour.TYPES["goto"]}},
                                 {"id": "2", "parameters": {"name": disp.Behaviour.TYPES["dock"]}},
                                 {"id": "3", "parameters": {"name": disp.Behaviour.TYPES["wait"]}},
                                 {"id": "4", "parameters": {"name": disp.Behaviour.TYPES["undock"]}}],
                  "current_behaviour_index": 0,  # index tablicy nie zachowania
                  "status": disp.Task.STATUS_LIST["IN_PROGRESS"],
                  "robot": "4",
                  "start_time": "2018-06-29 07:37:27",
                  "weight": 2,
                  "priority": 2},
                 {"id": "8",
                  "behaviours": [{"id": "1", "parameters": {"to": "6", "name": disp.Behaviour.TYPES["goto"]}},
                                 {"id": "2", "parameters": {"name": disp.Behaviour.TYPES["wait"]}}],
                  "current_behaviour_index": 0,  # index tablicy nie zachowania
                  "status": disp.Task.STATUS_LIST["IN_PROGRESS"],
                  "robot": "3",
                  "start_time": "2018-06-29 07:37:27",
                  "weight": 2,
                  "priority": 2},
                 {"id": "9",
                  "behaviours": [{"id": "1", "parameters": {"to": "7", "name": disp.Behaviour.TYPES["goto"]}},
                                 {"id": "2", "parameters": {"name": disp.Behaviour.TYPES["dock"]}},
                                 {"id": "3", "parameters": {"name": disp.Behaviour.TYPES["wait"]}},
                                 {"id": "4", "parameters": {"name": disp.Behaviour.TYPES["undock"]}}],
                  "current_behaviour_index": 0,  # index tablicy nie zachowania
                  "status": disp.Task.STATUS_LIST["IN_PROGRESS"],
                  "robot": "2",
                  "start_time": "2018-06-29 07:37:27",
                  "weight": 2,
                  "priority": 2},
                 {"id": "10",
                  "behaviours": [{"id": "1", "parameters": {"to": "3", "name": disp.Behaviour.TYPES["goto"]}},
                                 {"id": "2", "parameters": {"name": disp.Behaviour.TYPES["wait"]}}],
                  "current_behaviour_index": 0,  # index tablicy nie zachowania
                  "status": disp.Task.STATUS_LIST["IN_PROGRESS"],
                  "robot": "1",
                  "start_time": "2018-06-29 07:37:27",
                  "weight": 2,
                  "priority": 2}]
    tasks = [disp.Task(data) for data in tasks_raw]
    dispatcher = disp.Dispatcher(get_graph(robots_raw), robots)
    dispatcher.set_tasks(tasks)
    dispatcher.set_tasks_doing_by_robots()
    robots_using_poi = {"1": 0,
                        "2": 0,
                        "3": 2,
                        "4": 2,
                        "5": 1,
                        "6": 2,
                        "7": 3}
    result = dispatcher.get_robots_using_pois()
    for poi_id in result:
        assert result[poi_id] == robots_using_poi[poi_id]
    assert len(dispatcher.unanalyzed_tasks_handler.tasks) == 0


@pytest.mark.dispatcher
def test_dispatcher_set_doing_and_assigned_task_to_robots_1():
    # zestaw 1
    robots_raw = [
        {"id": "1", "edge": (69, 70), "planningOn": True, "isFree": True, "timeRemaining": 0, "poiId": "0"},
        {"id": "2", "edge": (78, 79), "planningOn": True, "isFree": True, "timeRemaining": 0, "poiId": "0"},
        {"id": "3", "edge": (74, 75), "planningOn": True, "isFree": True, "timeRemaining": 0, "poiId": "0"},
        {"id": "4", "edge": (63, 64), "planningOn": True, "isFree": True, "timeRemaining": 0, "poiId": "0"},
        {"id": "5", "edge": (38, 39), "planningOn": True, "isFree": True, "timeRemaining": 0, "poiId": "0"},
        {"id": "6", "edge": (67, 68), "planningOn": True, "isFree": True, "timeRemaining": 0, "poiId": "0"},
        {"id": "7", "edge": (49, 72), "planningOn": True, "isFree": True, "timeRemaining": 0, "poiId": "0"},
        {"id": "8", "edge": (50, 51), "planningOn": True, "isFree": True, "timeRemaining": 0, "poiId": "0"},
        {"id": "9", "edge": (87, 88), "planningOn": True, "isFree": True, "timeRemaining": 0, "poiId": "0"},
        {"id": "10", "edge": (19, 42), "planningOn": True, "isFree": True, "timeRemaining": 0, "poiId": "0"}
    ]
    robots = {robot["id"]: disp.Robot(robot) for robot in robots_raw}
    tasks_raw = [{"id": "1",
                  "behaviours": [{"id": "1", "parameters": {"to": "4", "name": disp.Behaviour.TYPES["goto"]}},
                                 {"id": "2", "parameters": {"name": disp.Behaviour.TYPES["dock"]}},
                                 {"id": "3", "parameters": {"name": disp.Behaviour.TYPES["wait"]}},
                                 {"id": "4", "parameters": {"name": disp.Behaviour.TYPES["undock"]}}],
                  "current_behaviour_index": 0,  # index tablicy nie zachowania
                  "status": disp.Task.STATUS_LIST["IN_PROGRESS"],
                  "robot": "10",
                  "start_time": "2018-06-29 07:37:27",
                  "weight": 2,
                  "priority": 2},
                 {"id": "2",
                  "behaviours": [{"id": "1", "parameters": {"to": "7", "name": disp.Behaviour.TYPES["goto"]}},
                                 {"id": "2", "parameters": {"name": disp.Behaviour.TYPES["dock"]}},
                                 {"id": "3", "parameters": {"name": disp.Behaviour.TYPES["wait"]}},
                                 {"id": "4", "parameters": {"name": disp.Behaviour.TYPES["undock"]}}],
                  "current_behaviour_index": 0,  # index tablicy nie zachowania
                  "status": disp.Task.STATUS_LIST["IN_PROGRESS"],
                  "robot": "9",
                  "start_time": "2018-06-29 07:37:27",
                  "weight": 2,
                  "priority": 2},
                 {"id": "3",
                  "behaviours": [{"id": "1", "parameters": {"to": "5", "name": disp.Behaviour.TYPES["goto"]}},
                                 {"id": "2", "parameters": {"name": disp.Behaviour.TYPES["dock"]}},
                                 {"id": "3", "parameters": {"name": disp.Behaviour.TYPES["wait"]}},
                                 {"id": "4", "parameters": {"name": disp.Behaviour.TYPES["undock"]}}],
                  "current_behaviour_index": 0,  # index tablicy nie zachowania
                  "status": disp.Task.STATUS_LIST["IN_PROGRESS"],
                  "robot": "8",
                  "start_time": "2018-06-29 07:37:27",
                  "weight": 2,
                  "priority": 2},
                 {"id": "4",
                  "behaviours": [{"id": "1", "parameters": {"to": "6", "name": disp.Behaviour.TYPES["goto"]}},
                                 {"id": "2", "parameters": {"name": disp.Behaviour.TYPES["wait"]}}],
                  "current_behaviour_index": 0,  # index tablicy nie zachowania
                  "status": disp.Task.STATUS_LIST["IN_PROGRESS"],
                  "robot": "7",
                  "start_time": "2018-06-29 07:37:27",
                  "weight": 2,
                  "priority": 2},
                 {"id": "5",
                  "behaviours": [{"id": "1", "parameters": {"to": "3", "name": disp.Behaviour.TYPES["goto"]}},
                                 {"id": "2", "parameters": {"name": disp.Behaviour.TYPES["wait"]}}],
                  "current_behaviour_index": 0,  # index tablicy nie zachowania
                  "status": disp.Task.STATUS_LIST["IN_PROGRESS"],
                  "robot": "6",
                  "start_time": "2018-06-29 07:37:27",
                  "weight": 2,
                  "priority": 2},
                 {"id": "6",
                  "behaviours": [{"id": "1", "parameters": {"to": "7", "name": disp.Behaviour.TYPES["goto"]}},
                                 {"id": "2", "parameters": {"name": disp.Behaviour.TYPES["dock"]}},
                                 {"id": "3", "parameters": {"name": disp.Behaviour.TYPES["wait"]}},
                                 {"id": "4", "parameters": {"name": disp.Behaviour.TYPES["undock"]}}],
                  "current_behaviour_index": 0,  # index tablicy nie zachowania
                  "status": disp.Task.STATUS_LIST["IN_PROGRESS"],
                  "robot": "5",
                  "start_time": "2018-06-29 07:37:27",
                  "weight": 2,
                  "priority": 2},
                 {"id": "7",
                  "behaviours": [{"id": "1", "parameters": {"to": "4", "name": disp.Behaviour.TYPES["goto"]}},
                                 {"id": "2", "parameters": {"name": disp.Behaviour.TYPES["dock"]}},
                                 {"id": "3", "parameters": {"name": disp.Behaviour.TYPES["wait"]}},
                                 {"id": "4", "parameters": {"name": disp.Behaviour.TYPES["undock"]}}],
                  "current_behaviour_index": 0,  # index tablicy nie zachowania
                  "status": disp.Task.STATUS_LIST["IN_PROGRESS"],
                  "robot": "4",
                  "start_time": "2018-06-29 07:37:27",
                  "weight": 2,
                  "priority": 2},
                 {"id": "8",
                  "behaviours": [{"id": "1", "parameters": {"to": "6", "name": disp.Behaviour.TYPES["goto"]}},
                                 {"id": "2", "parameters": {"name": disp.Behaviour.TYPES["wait"]}}],
                  "current_behaviour_index": 0,  # index tablicy nie zachowania
                  "status": disp.Task.STATUS_LIST["IN_PROGRESS"],
                  "robot": "3",
                  "start_time": "2018-06-29 07:37:27",
                  "weight": 2,
                  "priority": 2},
                 {"id": "9",
                  "behaviours": [{"id": "1", "parameters": {"to": "7", "name": disp.Behaviour.TYPES["goto"]}},
                                 {"id": "2", "parameters": {"name": disp.Behaviour.TYPES["dock"]}},
                                 {"id": "3", "parameters": {"name": disp.Behaviour.TYPES["wait"]}},
                                 {"id": "4", "parameters": {"name": disp.Behaviour.TYPES["undock"]}}],
                  "current_behaviour_index": 0,  # index tablicy nie zachowania
                  "status": disp.Task.STATUS_LIST["IN_PROGRESS"],
                  "robot": "2",
                  "start_time": "2018-06-29 07:37:27",
                  "weight": 2,
                  "priority": 2},
                 {"id": "10",
                  "behaviours": [{"id": "1", "parameters": {"to": "3", "name": disp.Behaviour.TYPES["goto"]}},
                                 {"id": "2", "parameters": {"name": disp.Behaviour.TYPES["wait"]}}],
                  "current_behaviour_index": 0,  # index tablicy nie zachowania
                  "status": disp.Task.STATUS_LIST["IN_PROGRESS"],
                  "robot": "1",
                  "start_time": "2018-06-29 07:37:27",
                  "weight": 2,
                  "priority": 2}]
    tasks = [disp.Task(data) for data in tasks_raw]
    dispatcher = disp.Dispatcher(get_graph(robots_raw), robots)
    dispatcher.set_tasks(tasks)
    dispatcher.set_tasks_doing_by_robots()
    robots_using_poi = {"1": 0,  # max 10
                        "2": 0,  # 1
                        "3": 2,  # 8
                        "4": 2,  # 11
                        "5": 1,  # 6 ?? z rysunku krawedzi wynika ze za duzo
                        "6": 2,  # 8
                        "7": 3}  # 6
    free_slots = {"1": 10, "2": 1, "3": 6, "4": 9, "5": 5, "6": 6, "7": 3}
    result = dispatcher.get_free_slots_in_pois()
    for poi_id in result:
        assert result[poi_id] == free_slots[poi_id]
    assert len(dispatcher.unanalyzed_tasks_handler.tasks) == 0


@pytest.mark.dispatcher
def test_dispatcher_set_doing_and_assigned_task_to_robots_2():
    # zestaw 2- niektore roboty blokuja POI i nie maja zadan - zablokowane POI 6 i 4
    robots_raw = [
        {"id": "1", "edge": (3, 4), "planningOn": True, "isFree": True, "timeRemaining": 0, "poiId": "0"},
        {"id": "2", "edge": (15, 16), "planningOn": True, "isFree": True, "timeRemaining": 0, "poiId": "0"},
        {"id": "3", "edge": (74, 75), "planningOn": True, "isFree": True, "timeRemaining": 0, "poiId": "0"},
        {"id": "4", "edge": (63, 64), "planningOn": True, "isFree": True, "timeRemaining": 0, "poiId": "0"},
        {"id": "5", "edge": (38, 39), "planningOn": True, "isFree": True, "timeRemaining": 0, "poiId": "0"},
        {"id": "6", "edge": (67, 68), "planningOn": True, "isFree": True, "timeRemaining": 0, "poiId": "0"},
        {"id": "7", "edge": (49, 72), "planningOn": True, "isFree": True, "timeRemaining": 0, "poiId": "0"},
        {"id": "8", "edge": (50, 51), "planningOn": True, "isFree": True, "timeRemaining": 0, "poiId": "0"},
        {"id": "9", "edge": (87, 88), "planningOn": True, "isFree": True, "timeRemaining": 0, "poiId": "0"},
        {"id": "10", "edge": (19, 42), "planningOn": True, "isFree": True, "timeRemaining": 0, "poiId": "0"}
    ]
    robots = {robot["id"]: disp.Robot(robot) for robot in robots_raw}
    tasks_raw = [{"id": "1",
                  "behaviours": [{"id": "1", "parameters": {"to": "4", "name": disp.Behaviour.TYPES["goto"]}},
                                 {"id": "2", "parameters": {"name": disp.Behaviour.TYPES["dock"]}},
                                 {"id": "3", "parameters": {"name": disp.Behaviour.TYPES["wait"]}},
                                 {"id": "4", "parameters": {"name": disp.Behaviour.TYPES["undock"]}}],
                  "current_behaviour_index": 0,  # index tablicy nie zachowania
                  "status": disp.Task.STATUS_LIST["IN_PROGRESS"],
                  "robot": "10",
                  "start_time": "2018-06-29 07:37:27",
                  "weight": 2,
                  "priority": 2},
                 {"id": "2",
                  "behaviours": [{"id": "1", "parameters": {"to": "7", "name": disp.Behaviour.TYPES["goto"]}},
                                 {"id": "2", "parameters": {"name": disp.Behaviour.TYPES["dock"]}},
                                 {"id": "3", "parameters": {"name": disp.Behaviour.TYPES["wait"]}},
                                 {"id": "4", "parameters": {"name": disp.Behaviour.TYPES["undock"]}}],
                  "current_behaviour_index": 0,  # index tablicy nie zachowania
                  "status": disp.Task.STATUS_LIST["IN_PROGRESS"],
                  "robot": "9",
                  "start_time": "2018-06-29 07:37:27",
                  "weight": 2,
                  "priority": 2},
                 {"id": "3",
                  "behaviours": [{"id": "1", "parameters": {"to": "5", "name": disp.Behaviour.TYPES["goto"]}},
                                 {"id": "2", "parameters": {"name": disp.Behaviour.TYPES["dock"]}},
                                 {"id": "3", "parameters": {"name": disp.Behaviour.TYPES["wait"]}},
                                 {"id": "4", "parameters": {"name": disp.Behaviour.TYPES["undock"]}}],
                  "current_behaviour_index": 0,  # index tablicy nie zachowania
                  "status": disp.Task.STATUS_LIST["IN_PROGRESS"],
                  "robot": "8",
                  "start_time": "2018-06-29 07:37:27",
                  "weight": 2,
                  "priority": 2},
                 {"id": "4",
                  "behaviours": [{"id": "1", "parameters": {"to": "6", "name": disp.Behaviour.TYPES["goto"]}},
                                 {"id": "2", "parameters": {"name": disp.Behaviour.TYPES["wait"]}}],
                  "current_behaviour_index": 0,  # index tablicy nie zachowania
                  "status": disp.Task.STATUS_LIST["IN_PROGRESS"],
                  "robot": "7",
                  "start_time": "2018-06-29 07:37:27",
                  "weight": 2,
                  "priority": 2},
                 {"id": "5",
                  "behaviours": [{"id": "1", "parameters": {"to": "3", "name": disp.Behaviour.TYPES["goto"]}},
                                 {"id": "2", "parameters": {"name": disp.Behaviour.TYPES["wait"]}}],
                  "current_behaviour_index": 0,  # index tablicy nie zachowania
                  "status": disp.Task.STATUS_LIST["IN_PROGRESS"],
                  "robot": "6",
                  "start_time": "2018-06-29 07:37:27",
                  "weight": 2,
                  "priority": 2},
                 {"id": "6",
                  "behaviours": [{"id": "1", "parameters": {"to": "7", "name": disp.Behaviour.TYPES["goto"]}},
                                 {"id": "2", "parameters": {"name": disp.Behaviour.TYPES["dock"]}},
                                 {"id": "3", "parameters": {"name": disp.Behaviour.TYPES["wait"]}},
                                 {"id": "4", "parameters": {"name": disp.Behaviour.TYPES["undock"]}}],
                  "current_behaviour_index": 0,  # index tablicy nie zachowania
                  "status": disp.Task.STATUS_LIST["IN_PROGRESS"],
                  "robot": "5",
                  "start_time": "2018-06-29 07:37:27",
                  "weight": 2,
                  "priority": 2},
                 {"id": "7",
                  "behaviours": [{"id": "1", "parameters": {"to": "4", "name": disp.Behaviour.TYPES["goto"]}},
                                 {"id": "2", "parameters": {"name": disp.Behaviour.TYPES["dock"]}},
                                 {"id": "3", "parameters": {"name": disp.Behaviour.TYPES["wait"]}},
                                 {"id": "4", "parameters": {"name": disp.Behaviour.TYPES["undock"]}}],
                  "current_behaviour_index": 0,  # index tablicy nie zachowania
                  "status": disp.Task.STATUS_LIST["IN_PROGRESS"],
                  "robot": "4",
                  "start_time": "2018-06-29 07:37:27",
                  "weight": 2,
                  "priority": 2},
                 {"id": "8",
                  "behaviours": [{"id": "1", "parameters": {"to": "6", "name": disp.Behaviour.TYPES["goto"]}},
                                 {"id": "2", "parameters": {"name": disp.Behaviour.TYPES["wait"]}}],
                  "current_behaviour_index": 0,  # index tablicy nie zachowania
                  "status": disp.Task.STATUS_LIST["IN_PROGRESS"],
                  "robot": "3",
                  "start_time": "2018-06-29 07:37:27",
                  "weight": 2,
                  "priority": 2},
                 {"id": "9",
                  "behaviours": [{"id": "1", "parameters": {"to": "7", "name": disp.Behaviour.TYPES["goto"]}},
                                 {"id": "2", "parameters": {"name": disp.Behaviour.TYPES["dock"]}},
                                 {"id": "3", "parameters": {"name": disp.Behaviour.TYPES["wait"]}},
                                 {"id": "4", "parameters": {"name": disp.Behaviour.TYPES["undock"]}}],
                  "current_behaviour_index": -1,  # index tablicy nie zachowania
                  "status": disp.Task.STATUS_LIST["TO_DO"],
                  "robot": None,
                  "start_time": "2018-06-29 07:37:27",
                  "weight": 2,
                  "priority": 2},
                 {"id": "10",
                  "behaviours": [{"id": "1", "parameters": {"to": "3", "name": disp.Behaviour.TYPES["goto"]}},
                                 {"id": "2", "parameters": {"name": disp.Behaviour.TYPES["wait"]}}],
                  "current_behaviour_index": -1,  # index tablicy nie zachowania
                  "status": disp.Task.STATUS_LIST["TO_DO"],
                  "robot": None,
                  "start_time": "2018-06-29 07:37:27",
                  "weight": 2,
                  "priority": 2}]
    tasks = [disp.Task(data) for data in tasks_raw]
    dispatcher = disp.Dispatcher(get_graph(robots_raw), robots)
    dispatcher.set_tasks(tasks)
    dispatcher.set_tasks_doing_by_robots()
    robots_using_poi = {"1": 0,  # max 10
                        "2": 0,  # 1
                        "3": 1,  # 8
                        "4": 2,  # 11
                        "5": 1,  # 6 ?? z rysunku krawedzi wynika ze za duzo
                        "6": 2,  # 8
                        "7": 2}  # 6
    free_slots = {"1": 10, "2": 1, "3": 7, "4": 8, "5": 5, "6": 5, "7": 4}
    result = dispatcher.get_free_slots_in_pois()
    for poi_id in result:
        assert result[poi_id] == free_slots[poi_id]


@pytest.mark.dispatcher
def test_dispatcher_get_robots_id_blocking_used_poi():
    robots_raw = [
        {"id": "1", "edge": (7, 8), "planningOn": True, "isFree": True, "timeRemaining": 0, "poiId": "0"},
        {"id": "2", "edge": (13, 14), "planningOn": True, "isFree": True, "timeRemaining": 0, "poiId": "0"},
        {"id": "3", "edge": (41, 19), "planningOn": True, "isFree": True, "timeRemaining": 0, "poiId": "0"},
        {"id": "4", "edge": (41, 19), "planningOn": True, "isFree": True, "timeRemaining": 0, "poiId": "0"},
        {"id": "5", "edge": (15, 16), "planningOn": True, "isFree": True, "timeRemaining": 0, "poiId": "0"},
        {"id": "6", "edge": (11, 12), "planningOn": True, "isFree": True, "timeRemaining": 0, "poiId": "0"},
        {"id": "7", "edge": (3, 4), "planningOn": True, "isFree": True, "timeRemaining": 0, "poiId": "0"},
        {"id": "8", "edge": (41, 19), "planningOn": True, "isFree": True, "timeRemaining": 0, "poiId": "0"},
        {"id": "9", "edge": (41, 19), "planningOn": True, "isFree": True, "timeRemaining": 0, "poiId": "0"},
        {"id": "10", "edge": (31, 17), "planningOn": True, "isFree": True, "timeRemaining": 0, "poiId": "0"}
    ]
    robots = {robot["id"]: disp.Robot(robot) for robot in robots_raw}
    tasks_raw = [{"id": "1",
                  "behaviours": [{"id": "1", "parameters": {"to": "3", "name": disp.Behaviour.TYPES["goto"]}},
                                 {"id": "3", "parameters": {"name": disp.Behaviour.TYPES["wait"]}}],
                  "current_behaviour_index": 0,  # index tablicy nie zachowania
                  "status": disp.Task.STATUS_LIST["IN_PROGRESS"],
                  "robot": "9",
                  "start_time": "2018-06-29 07:37:27",
                  "weight": 2,
                  "priority": 2},
                 {"id": "2",
                  "behaviours": [{"id": "1", "parameters": {"to": "5", "name": disp.Behaviour.TYPES["goto"]}},
                                 {"id": "2", "parameters": {"name": disp.Behaviour.TYPES["dock"]}},
                                 {"id": "3", "parameters": {"name": disp.Behaviour.TYPES["wait"]}},
                                 {"id": "4", "parameters": {"name": disp.Behaviour.TYPES["undock"]}}],
                  "current_behaviour_index": 0,  # index tablicy nie zachowania
                  "status": disp.Task.STATUS_LIST["IN_PROGRESS"],
                  "robot": "4",
                  "start_time": "2018-06-29 07:37:27",
                  "weight": 2,
                  "priority": 2},
                 {"id": "3",
                  "behaviours": [{"id": "1", "parameters": {"to": "6", "name": disp.Behaviour.TYPES["goto"]}},
                                 {"id": "3", "parameters": {"name": disp.Behaviour.TYPES["wait"]}}],
                  "current_behaviour_index": 0,  # index tablicy nie zachowania
                  "status": disp.Task.STATUS_LIST["IN_PROGRESS"],
                  "robot": "3",
                  "start_time": "2018-06-29 07:37:27",
                  "weight": 2,
                  "priority": 2}
                 ]
    tasks = [disp.Task(data) for data in tasks_raw]
    dispatcher = disp.Dispatcher(get_graph(robots_raw), robots)
    dispatcher.set_tasks(tasks)
    dispatcher.set_tasks_doing_by_robots()
    result = dispatcher.get_robots_id_blocking_used_poi()
    # poi do ktorych jada roboty 3 (13,14), 5 (11,12), 6 (15,16)
    expected_result = ["2", "6", "5"]  # id robotow
    assert len(result) == len(expected_result)
    for robot_id in result:
        assert robot_id in expected_result


@pytest.mark.dispatcher
def test_dispatcher_set_task_edge_simple_example():
    # prosty przypadek, w ktorym nalezy ustawic kolejna krawedz przejscia
    robots_raw = [
        {"id": "1", "edge": (7, 8), "planningOn": True, "isFree": True, "timeRemaining": 0, "poiId": "0"}]
    tasks_raw = [{"id": "1",
                  "behaviours": [{"id": "1", "parameters": {"to": "4", "name": disp.Behaviour.TYPES["goto"]}},
                                 {"id": "2", "parameters": {"name": disp.Behaviour.TYPES["dock"]}},
                                 {"id": "3", "parameters": {"name": disp.Behaviour.TYPES["wait"]}},
                                 {"id": "4", "parameters": {"name": disp.Behaviour.TYPES["undock"]}}],
                  "current_behaviour_index": 0,  # index tablicy nie zachowania
                  "status": disp.Task.STATUS_LIST["IN_PROGRESS"],
                  "robot": "1",
                  "start_time": "2018-06-29 07:37:27",
                  "weight": 2,
                  "priority": 2}]
    robots = {}
    for i in range(len(robots_raw)):
        robot = disp.Robot(robots_raw[i])
        robot.task = disp.Task(tasks_raw[i])
        robots[robot.id] = robot
    dispatcher = disp.Dispatcher(get_graph(robots_raw), robots)
    dispatcher.set_task_edge("1")
    assert dispatcher.robots_plan.robots["1"].next_task_edge == (8, 18)


@pytest.mark.dispatcher
def test_dispatcher_set_task_edge_simple_example_intersection_blocked():
    # przypadki w ktorych kolejna krawedz nie moze byc ustawiona
    # - zablokowane skrzyzowanie
    robots_raw = [
        {"id": "1", "edge": (66, 38), "planningOn": True, "isFree": True, "timeRemaining": 0, "poiId": "0"},
        {"id": "2", "edge": (65, 66), "planningOn": True, "isFree": True, "timeRemaining": 0, "poiId": "0"}
    ]
    tasks_raw = [{"id": "1",
                  "behaviours": [{"id": "1", "parameters": {"to": "7", "name": disp.Behaviour.TYPES["goto"]}},
                                 {"id": "2", "parameters": {"name": disp.Behaviour.TYPES["dock"]}},
                                 {"id": "3", "parameters": {"name": disp.Behaviour.TYPES["wait"]}},
                                 {"id": "4", "parameters": {"name": disp.Behaviour.TYPES["undock"]}}],
                  "current_behaviour_index": 0,  # index tablicy nie zachowania
                  "status": disp.Task.STATUS_LIST["IN_PROGRESS"],
                  "robot": "1",
                  "start_time": "2018-06-29 07:37:27",
                  "weight": 2,
                  "priority": 2},
                 {"id": "2",
                  "behaviours": [{"id": "1", "parameters": {"to": "7", "name": disp.Behaviour.TYPES["goto"]}},
                                 {"id": "2", "parameters": {"name": disp.Behaviour.TYPES["dock"]}},
                                 {"id": "3", "parameters": {"name": disp.Behaviour.TYPES["wait"]}},
                                 {"id": "4", "parameters": {"name": disp.Behaviour.TYPES["undock"]}}],
                  "current_behaviour_index": 0,  # index tablicy nie zachowania
                  "status": disp.Task.STATUS_LIST["IN_PROGRESS"],
                  "robot": "2",
                  "start_time": "2018-06-29 07:37:27",
                  "weight": 2,
                  "priority": 2}
                 ]
    robots = {}
    for i in range(len(robots_raw)):
        robot = disp.Robot(robots_raw[i])
        robot.task = disp.Task(tasks_raw[i])
        robots[robot.id] = robot

    dispatcher = disp.Dispatcher(get_graph(robots_raw), [])
    expected_result = {"1": (38, 39), "2": None}  # robot_id: edge
    for i in [robot["id"] for robot in robots_raw]:
        dispatcher.robots_plan.robots[i] = robots[i]
        dispatcher.set_task_edge(i)
        robot = dispatcher.robots_plan.robots[i]
        assert robot.next_task_edge == expected_result[i]


@pytest.mark.dispatcher
def test_dispatcher_set_task_edge_simple_example_poi_7_waiting_edge_blocked_1():
    # przypadki w ktorych kolejna krawedz nie moze byc ustawiona
    # - zablokowana inna krawedz z poi 7
    robots_raw = [
        {"id": "1", "edge": (33, 23), "planningOn": True, "isFree": True, "timeRemaining": 0, "poiId": "0"},
        {"id": "2", "edge": (33, 23), "planningOn": True, "isFree": True, "timeRemaining": 0, "poiId": "0"},
        {"id": "3", "edge": (33, 23), "planningOn": True, "isFree": True, "timeRemaining": 0, "poiId": "0"},
        {"id": "4", "edge": (33, 23), "planningOn": True, "isFree": True, "timeRemaining": 0, "poiId": "0"},
        {"id": "5", "edge": (33, 23), "planningOn": True, "isFree": True, "timeRemaining": 0, "poiId": "0"},
        {"id": "6", "edge": (39, 33), "planningOn": True, "isFree": True, "timeRemaining": 0, "poiId": "0"},
        {"id": "7", "edge": (38, 39), "planningOn": True, "isFree": True, "timeRemaining": 0, "poiId": "0"}
    ]
    tasks_raw = [{"id": "1",
                  "behaviours": [{"id": "1", "parameters": {"to": "7", "name": disp.Behaviour.TYPES["goto"]}},
                                 {"id": "2", "parameters": {"name": disp.Behaviour.TYPES["dock"]}},
                                 {"id": "3", "parameters": {"name": disp.Behaviour.TYPES["wait"]}},
                                 {"id": "4", "parameters": {"name": disp.Behaviour.TYPES["undock"]}}],
                  "current_behaviour_index": 0,  # index tablicy nie zachowania
                  "status": disp.Task.STATUS_LIST["IN_PROGRESS"],
                  "robot": "1",
                  "start_time": "2018-06-29 07:37:27",
                  "weight": 2,
                  "priority": 2},
                 {"id": "2",
                  "behaviours": [{"id": "1", "parameters": {"to": "7", "name": disp.Behaviour.TYPES["goto"]}},
                                 {"id": "2", "parameters": {"name": disp.Behaviour.TYPES["dock"]}},
                                 {"id": "3", "parameters": {"name": disp.Behaviour.TYPES["wait"]}},
                                 {"id": "4", "parameters": {"name": disp.Behaviour.TYPES["undock"]}}],
                  "current_behaviour_index": 0,  # index tablicy nie zachowania
                  "status": disp.Task.STATUS_LIST["IN_PROGRESS"],
                  "robot": "2",
                  "start_time": "2018-06-29 07:37:27",
                  "weight": 2,
                  "priority": 2},
                 {"id": "3",
                  "behaviours": [{"id": "1", "parameters": {"to": "7", "name": disp.Behaviour.TYPES["goto"]}},
                                 {"id": "2", "parameters": {"name": disp.Behaviour.TYPES["dock"]}},
                                 {"id": "3", "parameters": {"name": disp.Behaviour.TYPES["wait"]}},
                                 {"id": "4", "parameters": {"name": disp.Behaviour.TYPES["undock"]}}],
                  "current_behaviour_index": 0,  # index tablicy nie zachowania
                  "status": disp.Task.STATUS_LIST["IN_PROGRESS"],
                  "robot": "3",
                  "start_time": "2018-06-29 07:37:27",
                  "weight": 2,
                  "priority": 2},
                 {"id": "4",
                  "behaviours": [{"id": "1", "parameters": {"to": "7", "name": disp.Behaviour.TYPES["goto"]}},
                                 {"id": "2", "parameters": {"name": disp.Behaviour.TYPES["dock"]}},
                                 {"id": "3", "parameters": {"name": disp.Behaviour.TYPES["wait"]}},
                                 {"id": "4", "parameters": {"name": disp.Behaviour.TYPES["undock"]}}],
                  "current_behaviour_index": 0,  # index tablicy nie zachowania
                  "status": disp.Task.STATUS_LIST["IN_PROGRESS"],
                  "robot": "4",
                  "start_time": "2018-06-29 07:37:27",
                  "weight": 2,
                  "priority": 2},
                 {"id": "5",
                  "behaviours": [{"id": "1", "parameters": {"to": "7", "name": disp.Behaviour.TYPES["goto"]}},
                                 {"id": "2", "parameters": {"name": disp.Behaviour.TYPES["dock"]}},
                                 {"id": "3", "parameters": {"name": disp.Behaviour.TYPES["wait"]}},
                                 {"id": "4", "parameters": {"name": disp.Behaviour.TYPES["undock"]}}],
                  "current_behaviour_index": 0,  # index tablicy nie zachowania
                  "status": disp.Task.STATUS_LIST["IN_PROGRESS"],
                  "robot": "5",
                  "start_time": "2018-06-29 07:37:27",
                  "weight": 2,
                  "priority": 2},
                 {"id": "6",
                  "behaviours": [{"id": "1", "parameters": {"to": "7", "name": disp.Behaviour.TYPES["goto"]}},
                                 {"id": "2", "parameters": {"name": disp.Behaviour.TYPES["dock"]}},
                                 {"id": "3", "parameters": {"name": disp.Behaviour.TYPES["wait"]}},
                                 {"id": "4", "parameters": {"name": disp.Behaviour.TYPES["undock"]}}],
                  "current_behaviour_index": 0,  # index tablicy nie zachowania
                  "status": disp.Task.STATUS_LIST["IN_PROGRESS"],
                  "robot": "6",
                  "start_time": "2018-06-29 07:37:27",
                  "weight": 2,
                  "priority": 2},
                 {"id": "7",
                  "behaviours": [{"id": "1", "parameters": {"to": "1", "name": disp.Behaviour.TYPES["goto"]}}],
                  "current_behaviour_index": 0,  # index tablicy nie zachowania
                  "status": disp.Task.STATUS_LIST["IN_PROGRESS"],
                  "robot": "7",
                  "start_time": "2018-06-29 07:37:27",
                  "weight": 2,
                  "priority": 2}
                 ]
    robots = {}
    for i in range(len(robots_raw)):
        robot = disp.Robot(robots_raw[i])
        robot.task = disp.Task(tasks_raw[i])
        robots[robot.id] = robot
    dispatcher = disp.Dispatcher(get_graph(robots_raw), [])
    expected_result = {"1": (23, 5), "2": None, "3": None, "4": None, "5": None, "6": None, "7": None}
    # robot_id: edge
    # robot "6" znajdujacy sie po zjezdzie ze skrzyzowania nie moze jechac dalej, bo aktualnie maksymalna liczba robotow
    # znajduje sie na krawedzi
    for r_id in [robot["id"] for robot in robots_raw]:
        dispatcher.robots_plan.robots[r_id] = robots[r_id]
        dispatcher.set_task_edge(r_id)
        robot = dispatcher.robots_plan.robots[r_id]
        assert robot.next_task_edge == expected_result[r_id]


@pytest.mark.dispatcher
def test_dispatcher_set_task_edge_simple_example_poi_7_waiting_edge_blocked_2():
    # przypadki w ktorych kolejna krawedz nie moze byc ustawiona
    # - zablokowana inna krawedz z poi 7

    robots_raw = [
        {"id": "1", "edge": (33, 23), "planningOn": True, "isFree": True, "timeRemaining": 0, "poiId": "0"},
        {"id": "2", "edge": (33, 23), "planningOn": True, "isFree": True, "timeRemaining": 0, "poiId": "0"},
        {"id": "3", "edge": (33, 23), "planningOn": True, "isFree": True, "timeRemaining": 0, "poiId": "0"},
        {"id": "4", "edge": (33, 23), "planningOn": True, "isFree": True, "timeRemaining": 0, "poiId": "0"},
        {"id": "6", "edge": (39, 33), "planningOn": True, "isFree": True, "timeRemaining": 0, "poiId": "0"},
        {"id": "7", "edge": (38, 39), "planningOn": True, "isFree": True, "timeRemaining": 0, "poiId": "0"}
    ]
    tasks_raw = [{"id": "1",
                  "behaviours": [{"id": "1", "parameters": {"to": "7", "name": disp.Behaviour.TYPES["goto"]}},
                                 {"id": "2", "parameters": {"name": disp.Behaviour.TYPES["dock"]}},
                                 {"id": "3", "parameters": {"name": disp.Behaviour.TYPES["wait"]}},
                                 {"id": "4", "parameters": {"name": disp.Behaviour.TYPES["undock"]}}],
                  "current_behaviour_index": 0,  # index tablicy nie zachowania
                  "status": disp.Task.STATUS_LIST["IN_PROGRESS"],
                  "robot": "1",
                  "start_time": "2018-06-29 07:37:27",
                  "weight": 2,
                  "priority": 2},
                 {"id": "2",
                  "behaviours": [{"id": "1", "parameters": {"to": "7", "name": disp.Behaviour.TYPES["goto"]}},
                                 {"id": "2", "parameters": {"name": disp.Behaviour.TYPES["dock"]}},
                                 {"id": "3", "parameters": {"name": disp.Behaviour.TYPES["wait"]}},
                                 {"id": "4", "parameters": {"name": disp.Behaviour.TYPES["undock"]}}],
                  "current_behaviour_index": 0,  # index tablicy nie zachowania
                  "status": disp.Task.STATUS_LIST["IN_PROGRESS"],
                  "robot": "2",
                  "start_time": "2018-06-29 07:37:27",
                  "weight": 2,
                  "priority": 2},
                 {"id": "3",
                  "behaviours": [{"id": "1", "parameters": {"to": "7", "name": disp.Behaviour.TYPES["goto"]}},
                                 {"id": "2", "parameters": {"name": disp.Behaviour.TYPES["dock"]}},
                                 {"id": "3", "parameters": {"name": disp.Behaviour.TYPES["wait"]}},
                                 {"id": "4", "parameters": {"name": disp.Behaviour.TYPES["undock"]}}],
                  "current_behaviour_index": 0,  # index tablicy nie zachowania
                  "status": disp.Task.STATUS_LIST["IN_PROGRESS"],
                  "robot": "3",
                  "start_time": "2018-06-29 07:37:27",
                  "weight": 2,
                  "priority": 2},
                 {"id": "4",
                  "behaviours": [{"id": "1", "parameters": {"to": "7", "name": disp.Behaviour.TYPES["goto"]}},
                                 {"id": "2", "parameters": {"name": disp.Behaviour.TYPES["dock"]}},
                                 {"id": "3", "parameters": {"name": disp.Behaviour.TYPES["wait"]}},
                                 {"id": "4", "parameters": {"name": disp.Behaviour.TYPES["undock"]}}],
                  "current_behaviour_index": 0,  # index tablicy nie zachowania
                  "status": disp.Task.STATUS_LIST["IN_PROGRESS"],
                  "robot": "4",
                  "start_time": "2018-06-29 07:37:27",
                  "weight": 2,
                  "priority": 2},
                 {"id": "6",
                  "behaviours": [{"id": "1", "parameters": {"to": "7", "name": disp.Behaviour.TYPES["goto"]}},
                                 {"id": "2", "parameters": {"name": disp.Behaviour.TYPES["dock"]}},
                                 {"id": "3", "parameters": {"name": disp.Behaviour.TYPES["wait"]}},
                                 {"id": "4", "parameters": {"name": disp.Behaviour.TYPES["undock"]}}],
                  "current_behaviour_index": 0,  # index tablicy nie zachowania
                  "status": disp.Task.STATUS_LIST["IN_PROGRESS"],
                  "robot": "6",
                  "start_time": "2018-06-29 07:37:27",
                  "weight": 2,
                  "priority": 2},
                 {"id": "7",
                  "behaviours": [{"id": "1", "parameters": {"to": "1", "name": disp.Behaviour.TYPES["goto"]}}],
                  "current_behaviour_index": 0,  # index tablicy nie zachowania
                  "status": disp.Task.STATUS_LIST["IN_PROGRESS"],
                  "robot": "7",
                  "start_time": "2018-06-29 07:37:27",
                  "weight": 2,
                  "priority": 2}
                 ]
    robots = {}
    for i in range(len(robots_raw)):
        robot = disp.Robot(robots_raw[i])
        robot.task = disp.Task(tasks_raw[i])
        robots[robot.id] = robot
    dispatcher = disp.Dispatcher(get_graph(robots_raw), [])
    expected_result = {"1": (23, 5), "2": None, "3": None, "4": None, "6": (33, 23), "7": None}
    # robot_id: edge
    # robot "6" znajdujacy sie po zjezdzie ze skrzyzowania nie moze jechac dalej, bo aktualnie maksymalna liczba robotow
    # znajduje sie na krawedzi
    for i in [robot["id"] for robot in robots_raw]:
        dispatcher.robots_plan.robots[i] = robots[i]
        dispatcher.set_task_edge(i)
        robot = dispatcher.robots_plan.robots[i]
        assert robot.next_task_edge == expected_result[i]


@pytest.mark.dispatcher
def test_dispatcher_set_task_edge_simple_example_blocked_goal_7():
    # przypadki w ktorych kolejna krawedz nie moze byc ustawiona
    # - zablokowany dojazd do kolejnego POI - jeden robot bez zadania, a reszta w drodze i na krawedzi przed POI,
    # robot, ktory ma zadanie i ma jechac dalej ma zostac w poprzednim POI
    robots_raw = [
        {"id": "1", "edge": (7, 8), "planningOn": True, "isFree": True, "timeRemaining": 0, "poiId": "0"},
        #  bez zadania
        {"id": "2", "edge": (33, 23), "planningOn": True, "isFree": True, "timeRemaining": 0, "poiId": "0"},
        {"id": "3", "edge": (33, 23), "planningOn": True, "isFree": True, "timeRemaining": 0, "poiId": "0"},
        {"id": "4", "edge": (39, 33), "planningOn": True, "isFree": True, "timeRemaining": 0, "poiId": "0"},
        {"id": "5", "edge": (38, 39), "planningOn": True, "isFree": True, "timeRemaining": 0, "poiId": "0"},
        {"id": "6", "edge": (38, 39), "planningOn": True, "isFree": True, "timeRemaining": 0, "poiId": "0"},
        {"id": "7", "edge": (15, 16), "planningOn": True, "isFree": True, "timeRemaining": 0, "poiId": "0"}
    ]
    tasks_raw = [{"id": "1",
                  "behaviours": [{"id": "1", "parameters": {"to": "7", "name": disp.Behaviour.TYPES["goto"]}},
                                 {"id": "2", "parameters": {"name": disp.Behaviour.TYPES["dock"]}},
                                 {"id": "3", "parameters": {"name": disp.Behaviour.TYPES["wait"]}},
                                 {"id": "4", "parameters": {"name": disp.Behaviour.TYPES["undock"]}}],
                  "current_behaviour_index": 0,  # index tablicy nie zachowania
                  "status": disp.Task.STATUS_LIST["IN_PROGRESS"],
                  "robot": "2",
                  "start_time": "2018-06-29 07:37:27",
                  "weight": 2,
                  "priority": 2},
                 {"id": "2",
                  "behaviours": [{"id": "1", "parameters": {"to": "7", "name": disp.Behaviour.TYPES["goto"]}},
                                 {"id": "2", "parameters": {"name": disp.Behaviour.TYPES["dock"]}},
                                 {"id": "3", "parameters": {"name": disp.Behaviour.TYPES["wait"]}},
                                 {"id": "4", "parameters": {"name": disp.Behaviour.TYPES["undock"]}}],
                  "current_behaviour_index": 0,  # index tablicy nie zachowania
                  "status": disp.Task.STATUS_LIST["IN_PROGRESS"],
                  "robot": "3",
                  "start_time": "2018-06-29 07:37:27",
                  "weight": 2,
                  "priority": 2},
                 {"id": "3",
                  "behaviours": [{"id": "1", "parameters": {"to": "7", "name": disp.Behaviour.TYPES["goto"]}},
                                 {"id": "2", "parameters": {"name": disp.Behaviour.TYPES["dock"]}},
                                 {"id": "3", "parameters": {"name": disp.Behaviour.TYPES["wait"]}},
                                 {"id": "4", "parameters": {"name": disp.Behaviour.TYPES["undock"]}}],
                  "current_behaviour_index": 0,  # index tablicy nie zachowania
                  "status": disp.Task.STATUS_LIST["IN_PROGRESS"],
                  "robot": "4",
                  "start_time": "2018-06-29 07:37:27",
                  "weight": 2,
                  "priority": 2},
                 {"id": "4",
                  "behaviours": [{"id": "1", "parameters": {"to": "7", "name": disp.Behaviour.TYPES["goto"]}},
                                 {"id": "2", "parameters": {"name": disp.Behaviour.TYPES["dock"]}},
                                 {"id": "3", "parameters": {"name": disp.Behaviour.TYPES["wait"]}},
                                 {"id": "4", "parameters": {"name": disp.Behaviour.TYPES["undock"]}}],
                  "current_behaviour_index": 0,  # index tablicy nie zachowania
                  "status": disp.Task.STATUS_LIST["IN_PROGRESS"],
                  "robot": "5",
                  "start_time": "2018-06-29 07:37:27",
                  "weight": 2,
                  "priority": 2},
                 {"id": "5",
                  "behaviours": [{"id": "1", "parameters": {"to": "7", "name": disp.Behaviour.TYPES["goto"]}},
                                 {"id": "2", "parameters": {"name": disp.Behaviour.TYPES["dock"]}},
                                 {"id": "3", "parameters": {"name": disp.Behaviour.TYPES["wait"]}},
                                 {"id": "4", "parameters": {"name": disp.Behaviour.TYPES["undock"]}}],
                  "current_behaviour_index": 0,  # index tablicy nie zachowania
                  "status": disp.Task.STATUS_LIST["IN_PROGRESS"],
                  "robot": "6",
                  "start_time": "2018-06-29 07:37:27",
                  "weight": 2,
                  "priority": 2},
                 {"id": "6",
                  "behaviours": [{"id": "1", "parameters": {"to": "7", "name": disp.Behaviour.TYPES["goto"]}},
                                 {"id": "2", "parameters": {"name": disp.Behaviour.TYPES["wait"]}},
                                 {"id": "3", "parameters": {"to": "7", "name": disp.Behaviour.TYPES["goto"]}},
                                 {"id": "4", "parameters": {"name": disp.Behaviour.TYPES["dock"]}},
                                 {"id": "5", "parameters": {"name": disp.Behaviour.TYPES["wait"]}},
                                 {"id": "6", "parameters": {"name": disp.Behaviour.TYPES["undock"]}}],
                  "current_behaviour_index": 2,  # index tablicy nie zachowania
                  "status": disp.Task.STATUS_LIST["IN_PROGRESS"],
                  "robot": "7",
                  "start_time": "2018-06-29 07:37:27",
                  "weight": 2,
                  "priority": 2}
                 ]
    robots = {}
    for i in range(len(robots_raw)):
        if i == 0:
            robots[robots_raw[i]["id"]] = disp.Robot(robots_raw[i])
        else:
            robot = disp.Robot(robots_raw[i])
            robot.task = disp.Task(tasks_raw[i-1])
            robots[robot.id] = robot
    dispatcher = disp.Dispatcher(get_graph(robots_raw), [])
    expected_result = {"1": None, "2": None, "3": None, "4": (33, 23), "5": None, "6": None, "7": None}
    # robot_id: edge
    for i in [robot["id"] for robot in robots_raw]:
        dispatcher.robots_plan.robots[i] = robots[i]
        if i != "1":
            dispatcher.set_task_edge(i)
        robot = dispatcher.robots_plan.robots[i]
        # print(i, robot.next_task_edge,  expected_result[i])
        assert robot.next_task_edge == expected_result[i]


@pytest.mark.dispatcher
def test_dispatcher_set_task_edge_blocked_goal_waiting_departure_nodeintersection():
    # przypadki w ktorych kolejna krawedz nie moze byc ustawiona
    # blokady w okolicach wezla waiting-departure poi 3
    # robot na skrzyzowaniu w wezle waiting-departure
    robots_raw = [
        {"id": "1", "edge": (57, 58), "planningOn": True, "isFree": True, "timeRemaining": 0, "poiId": "0"},
        {"id": "2", "edge": (57, 58), "planningOn": True, "isFree": True, "timeRemaining": 0, "poiId": "0"}
    ]
    tasks_raw = [{"id": "1",
                  "behaviours": [{"id": "1", "parameters": {"to": "3", "name": disp.Behaviour.TYPES["goto"]}},
                                 {"id": "2", "parameters": {"name": disp.Behaviour.TYPES["wait"]}}],
                  "current_behaviour_index": 0,  # index tablicy nie zachowania
                  "status": disp.Task.STATUS_LIST["IN_PROGRESS"],
                  "robot": "1",
                  "start_time": "2018-06-29 07:37:27",
                  "weight": 2,
                  "priority": 2},
                 {"id": "2",
                  "behaviours": [{"id": "1", "parameters": {"to": "3", "name": disp.Behaviour.TYPES["goto"]}},
                                 {"id": "2", "parameters": {"name": disp.Behaviour.TYPES["wait"]}}],
                  "current_behaviour_index": 0,  # index tablicy nie zachowania
                  "status": disp.Task.STATUS_LIST["IN_PROGRESS"],
                  "robot": "2",
                  "start_time": "2018-06-29 07:37:27",
                  "weight": 2,
                  "priority": 2}]
    robots = {}
    for i in range(len(robots_raw)):
        robot = disp.Robot(robots_raw[i])
        robot.task = disp.Task(tasks_raw[i-1])
        robots[robot.id] = robot
    dispatcher = disp.Dispatcher(get_graph(robots_raw), [])
    expected_result = {"1": (58, 29), "2": None}
    # robot_id: edge
    for i in [robot["id"] for robot in robots_raw]:
        dispatcher.robots_plan.robots[i] = robots[i]
        robot = dispatcher.robots_plan.robots[i]
        dispatcher.set_task_edge(i)
        assert robot.next_task_edge == expected_result[i]


@pytest.mark.dispatcher
def test_dispatcher_set_task_edge_blocked_goal_waiting_departure_node_before_poi():
    # przed poi
    # robot na skrzyzowaniu w wezle waiting-departure
    robots_raw = [
        {"id": "1", "edge": (29, 13), "planningOn": True, "isFree": True, "timeRemaining": 0, "poiId": "0"},
        {"id": "2", "edge": (57, 58), "planningOn": True, "isFree": True, "timeRemaining": 0, "poiId": "0"}
    ]
    tasks_raw = [{"id": "1",
                  "behaviours": [{"id": "1", "parameters": {"to": "3", "name": disp.Behaviour.TYPES["goto"]}},
                                 {"id": "2", "parameters": {"name": disp.Behaviour.TYPES["wait"]}}],
                  "current_behaviour_index": 1,  # index tablicy nie zachowania
                  "status": disp.Task.STATUS_LIST["IN_PROGRESS"],
                  "robot": "1",
                  "start_time": "2018-06-29 07:37:27",
                  "weight": 2,
                  "priority": 2},
                 {"id": "2",
                  "behaviours": [{"id": "1", "parameters": {"to": "3", "name": disp.Behaviour.TYPES["goto"]}},
                                 {"id": "2", "parameters": {"name": disp.Behaviour.TYPES["wait"]}}],
                  "current_behaviour_index": 0,  # index tablicy nie zachowania
                  "status": disp.Task.STATUS_LIST["IN_PROGRESS"],
                  "robot": "2",
                  "start_time": "2018-06-29 07:37:27",
                  "weight": 2,
                  "priority": 2}]
    robots = {}
    for i in range(len(robots_raw)):
        robot = disp.Robot(robots_raw[i])
        robot.task = disp.Task(tasks_raw[i])
        robots[robot.id] = robot
    dispatcher = disp.Dispatcher(get_graph(robots_raw), [])
    expected_result = {"1": (13, 14), "2": None}
    # robot_id: edge
    for i in [robot["id"] for robot in robots_raw]:
        dispatcher.robots_plan.robots[i] = robots[i]
        robot = dispatcher.robots_plan.robots[i]
        dispatcher.set_task_edge(i)
        assert robot.next_task_edge == expected_result[i]


@pytest.mark.dispatcher
def test_dispatcher_set_task_edge_blocked_goal_waiting_departure_node_in_poi():
    # w poi
    # robot na skrzyzowaniu w wezle waiting-departure
    robots_raw = [
        {"id": "1", "edge": (13, 14), "planningOn": True, "isFree": True, "timeRemaining": 0, "poiId": "0"},
        {"id": "2", "edge": (57, 58), "planningOn": True, "isFree": True, "timeRemaining": 0, "poiId": "0"}
    ]
    tasks_raw = [{"id": "1",
                  "behaviours": [{"id": "1", "parameters": {"to": "3", "name": disp.Behaviour.TYPES["goto"]}},
                                 {"id": "2", "parameters": {"name": disp.Behaviour.TYPES["wait"]}},
                                 {"id": "3", "parameters": {"to": "1", "name": disp.Behaviour.TYPES["goto"]}}],
                  "current_behaviour_index": 2,  # index tablicy nie zachowania
                  "status": disp.Task.STATUS_LIST["IN_PROGRESS"],
                  "robot": "1",
                  "start_time": "2018-06-29 07:37:27",
                  "weight": 2,
                  "priority": 2},
                 {"id": "2",
                  "behaviours": [{"id": "1", "parameters": {"to": "3", "name": disp.Behaviour.TYPES["goto"]}},
                                 {"id": "2", "parameters": {"name": disp.Behaviour.TYPES["wait"]}}],
                  "current_behaviour_index": 0,  # index tablicy nie zachowania
                  "status": disp.Task.STATUS_LIST["IN_PROGRESS"],
                  "robot": "2",
                  "start_time": "2018-06-29 07:37:27",
                  "weight": 2,
                  "priority": 2}]
    robots = {}
    for i in range(len(robots_raw)):
        robot = disp.Robot(robots_raw[i])
        robot.task = disp.Task(tasks_raw[i])
        robots[robot.id] = robot
    dispatcher = disp.Dispatcher(get_graph(robots_raw), [])
    expected_result = {"1": (14, 30), "2": None}
    # robot_id: edge
    for i in [robot["id"] for robot in robots_raw]:
        dispatcher.robots_plan.robots[i] = robots[i]
        robot = dispatcher.robots_plan.robots[i]
        dispatcher.set_task_edge(i)
        assert robot.next_task_edge == expected_result[i]


@pytest.mark.dispatcher
def test_dispatcher_get_free_task_to_assign():
    tasks_raw = [{"id": "1",
                  "behaviours": [{"id": "1", "parameters": {"to": "3", "name": disp.Behaviour.TYPES["goto"]}},
                                 {"id": "2", "parameters": {"name": disp.Behaviour.TYPES["wait"]}}],
                  "current_behaviour_index": -1,  # index tablicy nie zachowania
                  "status": disp.Task.STATUS_LIST["TO_DO"],
                  "robot": None,
                  "start_time": "2018-06-29 07:37:27",
                  "weight": 2,
                  "priority": 2},
                 {"id": "2",
                  "behaviours": [{"id": "1", "parameters": {"to": "3", "name": disp.Behaviour.TYPES["goto"]}},
                                 {"id": "2", "parameters": {"name": disp.Behaviour.TYPES["wait"]}}],
                  "current_behaviour_index": -1,  # index tablicy nie zachowania
                  "status": disp.Task.STATUS_LIST["TO_DO"],
                  "robot": None,
                  "start_time": "2018-06-29 07:37:27",
                  "weight": 2,
                  "priority": 2},
                 {"id": "3",
                  "behaviours": [{"id": "1", "parameters": {"to": "3", "name": disp.Behaviour.TYPES["goto"]}},
                                 {"id": "2", "parameters": {"name": disp.Behaviour.TYPES["wait"]}}],
                  "current_behaviour_index": -1,  # index tablicy nie zachowania
                  "status": disp.Task.STATUS_LIST["TO_DO"],
                  "robot": None,
                  "start_time": "2018-06-29 07:37:27",
                  "weight": 2,
                  "priority": 2},
                 {"id": "4",
                  "behaviours": [{"id": "1", "parameters": {"to": "3", "name": disp.Behaviour.TYPES["goto"]}},
                                 {"id": "2", "parameters": {"name": disp.Behaviour.TYPES["wait"]}}],
                  "current_behaviour_index": -1,  # index tablicy nie zachowania
                  "status": disp.Task.STATUS_LIST["TO_DO"],
                  "robot": None,
                  "start_time": "2018-06-29 07:37:27",
                  "weight": 2,
                  "priority": 2}
                 ]
    tasks = [disp.Task(data) for data in tasks_raw]
    dispatcher = disp.Dispatcher(get_graph([]), [])
    dispatcher.set_tasks(tasks)
    assert len(dispatcher.get_free_task_to_assign(3)) == 3
    assert len(dispatcher.get_free_task_to_assign(10)) == 4


@pytest.mark.dispatcher
def test_dispatcher_get_free_task_to_assign_skip_blocked_poi_task():
    robots_raw = [
        {"id": "1", "edge": (7, 8), "planningOn": True, "isFree": True, "timeRemaining": 0, "poiId": "0"},
        {"id": "2", "edge": (33, 23), "planningOn": True, "isFree": True, "timeRemaining": 0, "poiId": "0"},
        {"id": "3", "edge": (33, 23), "planningOn": True, "isFree": True, "timeRemaining": 0, "poiId": "0"},
        {"id": "4", "edge": (33, 23), "planningOn": True, "isFree": True, "timeRemaining": 0, "poiId": "0"},
        {"id": "5", "edge": (33, 23), "planningOn": True, "isFree": True, "timeRemaining": 0, "poiId": "0"},
        {"id": "6", "edge": (33, 23), "planningOn": True, "isFree": True, "timeRemaining": 0, "poiId": "0"},
        {"id": "7", "edge": (15, 16), "planningOn": True, "isFree": True, "timeRemaining": 0, "poiId": "0"},
        {"id": "8", "edge": (3, 4), "planningOn": True, "isFree": True, "timeRemaining": 0, "poiId": "0"}
    ]
    robots = {robot["id"]: disp.Robot(robot) for robot in robots_raw}
    tasks_raw = [{"id": "1",
                  "behaviours": [{"id": "1", "parameters": {"to": "7", "name": disp.Behaviour.TYPES["goto"]}},
                                 {"id": "2", "parameters": {"name": disp.Behaviour.TYPES["dock"]}},
                                 {"id": "3", "parameters": {"name": disp.Behaviour.TYPES["wait"]}},
                                 {"id": "4", "parameters": {"name": disp.Behaviour.TYPES["undock"]}}],
                  "current_behaviour_index": 0,  # index tablicy nie zachowania
                  "status": disp.Task.STATUS_LIST["IN_PROGRESS"],
                  "robot": "2",
                  "start_time": "2018-06-29 07:37:27",
                  "weight": 2,
                  "priority": 2},
                 {"id": "2",
                  "behaviours": [{"id": "1", "parameters": {"to": "7", "name": disp.Behaviour.TYPES["goto"]}},
                                 {"id": "2", "parameters": {"name": disp.Behaviour.TYPES["dock"]}},
                                 {"id": "3", "parameters": {"name": disp.Behaviour.TYPES["wait"]}},
                                 {"id": "4", "parameters": {"name": disp.Behaviour.TYPES["undock"]}}],
                  "current_behaviour_index": 0,  # index tablicy nie zachowania
                  "status": disp.Task.STATUS_LIST["IN_PROGRESS"],
                  "robot": "3",
                  "start_time": "2018-06-29 07:37:27",
                  "weight": 2,
                  "priority": 2},
                 {"id": "3",
                  "behaviours": [{"id": "1", "parameters": {"to": "7", "name": disp.Behaviour.TYPES["goto"]}},
                                 {"id": "2", "parameters": {"name": disp.Behaviour.TYPES["dock"]}},
                                 {"id": "3", "parameters": {"name": disp.Behaviour.TYPES["wait"]}},
                                 {"id": "4", "parameters": {"name": disp.Behaviour.TYPES["undock"]}}],
                  "current_behaviour_index": 0,  # index tablicy nie zachowania
                  "status": disp.Task.STATUS_LIST["IN_PROGRESS"],
                  "robot": "4",
                  "start_time": "2018-06-29 07:37:27",
                  "weight": 2,
                  "priority": 2},
                 {"id": "4",
                  "behaviours": [{"id": "1", "parameters": {"to": "7", "name": disp.Behaviour.TYPES["goto"]}},
                                 {"id": "2", "parameters": {"name": disp.Behaviour.TYPES["dock"]}},
                                 {"id": "3", "parameters": {"name": disp.Behaviour.TYPES["wait"]}},
                                 {"id": "4", "parameters": {"name": disp.Behaviour.TYPES["undock"]}}],
                  "current_behaviour_index": 0,  # index tablicy nie zachowania
                  "status": disp.Task.STATUS_LIST["IN_PROGRESS"],
                  "robot": "5",
                  "start_time": "2018-06-29 07:37:27",
                  "weight": 2,
                  "priority": 2},
                 {"id": "5",
                  "behaviours": [{"id": "1", "parameters": {"to": "7", "name": disp.Behaviour.TYPES["goto"]}},
                                 {"id": "2", "parameters": {"name": disp.Behaviour.TYPES["dock"]}},
                                 {"id": "3", "parameters": {"name": disp.Behaviour.TYPES["wait"]}},
                                 {"id": "4", "parameters": {"name": disp.Behaviour.TYPES["undock"]}}],
                  "current_behaviour_index": 0,  # index tablicy nie zachowania
                  "status": disp.Task.STATUS_LIST["IN_PROGRESS"],
                  "robot": "6",
                  "start_time": "2018-06-29 07:37:27",
                  "weight": 2,
                  "priority": 2},
                 {"id": "6",
                  "behaviours": [{"id": "1", "parameters": {"to": "7", "name": disp.Behaviour.TYPES["goto"]}},
                                 {"id": "2", "parameters": {"name": disp.Behaviour.TYPES["dock"]}},
                                 {"id": "3", "parameters": {"name": disp.Behaviour.TYPES["wait"]}},
                                 {"id": "4", "parameters": {"name": disp.Behaviour.TYPES["undock"]}}],
                  "current_behaviour_index": -1,  # index tablicy nie zachowania
                  "status": disp.Task.STATUS_LIST["TO_DO"],
                  "robot": None,
                  "start_time": "2018-06-29 07:37:27",
                  "weight": 2,
                  "priority": 2},
                 {"id": "7",
                  "behaviours": [{"id": "1", "parameters": {"to": "3", "name": disp.Behaviour.TYPES["goto"]}},
                                 {"id": "2", "parameters": {"name": disp.Behaviour.TYPES["wait"]}}],
                  "current_behaviour_index": -1,  # index tablicy nie zachowania
                  "status": disp.Task.STATUS_LIST["TO_DO"],
                  "robot": None,
                  "start_time": "2018-06-29 07:37:27",
                  "weight": 2,
                  "priority": 2},
                 {"id": "8",
                  "behaviours": [{"id": "1", "parameters": {"to": "3", "name": disp.Behaviour.TYPES["goto"]}},
                                 {"id": "2", "parameters": {"name": disp.Behaviour.TYPES["wait"]}}],
                  "current_behaviour_index": -1,  # index tablicy nie zachowania
                  "status": disp.Task.STATUS_LIST["TO_DO"],
                  "robot": None,
                  "start_time": "2018-06-29 07:37:27",
                  "weight": 2,
                  "priority": 2}
                 ]
    tasks = [disp.Task(data) for data in tasks_raw]
    dispatcher = disp.Dispatcher(get_graph(robots_raw), robots)
    dispatcher.set_tasks(tasks)
    dispatcher.set_tasks_doing_by_robots()
    received_tasks = dispatcher.get_free_task_to_assign(3)
    assert len(received_tasks) == 2
    for task in received_tasks:
        assert task.get_poi_goal() != "7"

    received_tasks = dispatcher.get_free_task_to_assign(1)
    assert len(received_tasks) == 1
    for task in received_tasks:
        assert task.get_poi_goal() != "7"


@pytest.mark.dispatcher
def test_dispatcher_assign_tasks_to_robots():
    robots_raw = [
        {"id": "1", "edge": (41, 19), "planningOn": True, "isFree": True, "timeRemaining": 0, "poiId": "0"},
        {"id": "2", "edge": (15, 16), "planningOn": True, "isFree": True, "timeRemaining": 0, "poiId": "0"},
        {"id": "3", "edge": (41, 19), "planningOn": True, "isFree": True, "timeRemaining": 0, "poiId": "0"},
        {"id": "4", "edge": (3, 4), "planningOn": True, "isFree": True, "timeRemaining": 0, "poiId": "0"},
        {"id": "5", "edge": (41, 19), "planningOn": True, "isFree": True, "timeRemaining": 0, "poiId": "0"},
        {"id": "6", "edge": (41, 19), "planningOn": True, "isFree": True, "timeRemaining": 0, "poiId": "0"},
        {"id": "7", "edge": (41, 19), "planningOn": True, "isFree": True, "timeRemaining": 0, "poiId": "0"},
        {"id": "8", "edge": (11, 12), "planningOn": True, "isFree": True, "timeRemaining": 0, "poiId": "0"}
    ]
    robots = {robot["id"]: disp.Robot(robot) for robot in robots_raw}
    tasks_raw = [{"id": "1",
                  "behaviours": [{"id": "1", "parameters": {"to": "7", "name": disp.Behaviour.TYPES["goto"]}},
                                 {"id": "2", "parameters": {"name": disp.Behaviour.TYPES["dock"]}},
                                 {"id": "3", "parameters": {"name": disp.Behaviour.TYPES["wait"]}},
                                 {"id": "4", "parameters": {"name": disp.Behaviour.TYPES["undock"]}}],
                  "current_behaviour_index": -1,  # index tablicy nie zachowania
                  "status": disp.Task.STATUS_LIST["TO_DO"],
                  "robot": None,
                  "start_time": "2018-06-29 07:37:27",
                  "weight": 2,
                  "priority": 2},
                 {"id": "2",
                  "behaviours": [{"id": "1", "parameters": {"to": "7", "name": disp.Behaviour.TYPES["goto"]}},
                                 {"id": "2", "parameters": {"name": disp.Behaviour.TYPES["dock"]}},
                                 {"id": "3", "parameters": {"name": disp.Behaviour.TYPES["wait"]}},
                                 {"id": "4", "parameters": {"name": disp.Behaviour.TYPES["undock"]}}],
                  "current_behaviour_index": -1,  # index tablicy nie zachowania
                  "status": disp.Task.STATUS_LIST["TO_DO"],
                  "robot": None,
                  "start_time": "2018-06-29 07:37:27",
                  "weight": 2,
                  "priority": 2},
                 {"id": "3",
                  "behaviours": [{"id": "1", "parameters": {"to": "7", "name": disp.Behaviour.TYPES["goto"]}},
                                 {"id": "2", "parameters": {"name": disp.Behaviour.TYPES["dock"]}},
                                 {"id": "3", "parameters": {"name": disp.Behaviour.TYPES["wait"]}},
                                 {"id": "4", "parameters": {"name": disp.Behaviour.TYPES["undock"]}}],
                  "current_behaviour_index": -1,  # index tablicy nie zachowania
                  "status": disp.Task.STATUS_LIST["TO_DO"],
                  "robot": None,
                  "start_time": "2018-06-29 07:37:27",
                  "weight": 2,
                  "priority": 2},
                 {"id": "4",
                  "behaviours": [{"id": "1", "parameters": {"to": "7", "name": disp.Behaviour.TYPES["goto"]}},
                                 {"id": "2", "parameters": {"name": disp.Behaviour.TYPES["dock"]}},
                                 {"id": "3", "parameters": {"name": disp.Behaviour.TYPES["wait"]}},
                                 {"id": "4", "parameters": {"name": disp.Behaviour.TYPES["undock"]}}],
                  "current_behaviour_index": -1,  # index tablicy nie zachowania
                  "status": disp.Task.STATUS_LIST["TO_DO"],
                  "robot": None,
                  "start_time": "2018-06-29 07:37:27",
                  "weight": 2,
                  "priority": 2},
                 {"id": "5",
                  "behaviours": [{"id": "1", "parameters": {"to": "7", "name": disp.Behaviour.TYPES["goto"]}},
                                 {"id": "2", "parameters": {"name": disp.Behaviour.TYPES["dock"]}},
                                 {"id": "3", "parameters": {"name": disp.Behaviour.TYPES["wait"]}},
                                 {"id": "4", "parameters": {"name": disp.Behaviour.TYPES["undock"]}}],
                  "current_behaviour_index": -1,  # index tablicy nie zachowania
                  "status": disp.Task.STATUS_LIST["TO_DO"],
                  "robot": None,
                  "start_time": "2018-06-29 07:37:27",
                  "weight": 2,
                  "priority": 2},
                 {"id": "6",
                  "behaviours": [{"id": "1", "parameters": {"to": "7", "name": disp.Behaviour.TYPES["goto"]}},
                                 {"id": "2", "parameters": {"name": disp.Behaviour.TYPES["dock"]}},
                                 {"id": "3", "parameters": {"name": disp.Behaviour.TYPES["wait"]}},
                                 {"id": "4", "parameters": {"name": disp.Behaviour.TYPES["undock"]}}],
                  "current_behaviour_index": -1,  # index tablicy nie zachowania
                  "status": disp.Task.STATUS_LIST["TO_DO"],
                  "robot": None,
                  "start_time": "2018-06-29 07:37:27",
                  "weight": 2,
                  "priority": 2},
                 {"id": "7",
                  "behaviours": [{"id": "1", "parameters": {"to": "3", "name": disp.Behaviour.TYPES["goto"]}},
                                 {"id": "2", "parameters": {"name": disp.Behaviour.TYPES["wait"]}}],
                  "current_behaviour_index": -1,  # index tablicy nie zachowania
                  "status": disp.Task.STATUS_LIST["TO_DO"],
                  "robot": None,
                  "start_time": "2018-06-29 07:37:27",
                  "weight": 2,
                  "priority": 2},
                 {"id": "8",
                  "behaviours": [{"id": "1", "parameters": {"to": "3", "name": disp.Behaviour.TYPES["goto"]}},
                                 {"id": "2", "parameters": {"name": disp.Behaviour.TYPES["wait"]}}],
                  "current_behaviour_index": -1,  # index tablicy nie zachowania
                  "status": disp.Task.STATUS_LIST["TO_DO"],
                  "robot": None,
                  "start_time": "2018-06-29 07:37:27",
                  "weight": 2,
                  "priority": 2}
                 ]
    tasks = [disp.Task(data) for data in tasks_raw]
    dispatcher = disp.Dispatcher(get_graph(robots_raw), robots)
    dispatcher.set_tasks(tasks)
    dispatcher.assign_tasks_to_robots([tasks[3], tasks[7], tasks[0]], ["4", "8", "2"])  # poi zadania: 7 3 7 robot:4 5 6
    assert len(dispatcher.unanalyzed_tasks_handler.tasks) == len(tasks_raw) - 3
    result = {"4": "2", "8": "4", "1": "8"}  # task id: robot id
    robots_with_tasks = [robot for robot in dispatcher.robots_plan.robots.values() if robot.task is not None]
    for robot in robots_with_tasks:
        if robot.task.id in result:
            assert result[robot.task.id] == robot.id


@pytest.mark.dispatcher
def test_dispatcher_from_queue_to_parking():
    robots_raw = [
        {"id": "1", "edge": (41, 19), "planningOn": True, "isFree": True, "timeRemaining": 0, "poiId": "0"}
    ]
    robots = {robot["id"]: disp.Robot(robot) for robot in robots_raw}
    tasks_raw = [
        {"id": "1",
         "behaviours": [{"id": "1", "parameters": {"to": "2", "name": disp.Behaviour.TYPES["goto"]}}],
         "current_behaviour_index": -1,
         "status": disp.Task.STATUS_LIST["TO_DO"],
         "robot": "1",
         "start_time": "2018-06-29 07:55:27",
         "weight": 3,
         "priority": 3
         },
    ]
    tasks = [disp.Task(data) for data in tasks_raw]
    dispatcher = disp.Dispatcher(get_graph(robots_raw), robots)
    plan = dispatcher.get_plan_all_free_robots(get_graph(robots_raw), robots, tasks)
    expected_result = {"1": {"taskId": "1", "nextEdge": (19, 42), "endBeh": False}}
    # print(plan)
    assert expected_result == plan


@pytest.mark.dispatcher
def test_dispatcher_from_queue_to_parking_2_robots():
    robots_raw = [
        {"id": "1", "edge": (41, 19), "planningOn": True, "isFree": True, "timeRemaining": 0, "poiId": "0"},
        {"id": "2", "edge": (41, 19), "planningOn": True, "isFree": True, "timeRemaining": 0, "poiId": "0"}
    ]
    robots = {robot["id"]: disp.Robot(robot) for robot in robots_raw}
    tasks_raw = [
        {"id": "1",
         "behaviours": [{"id": "1", "parameters": {"to": "2", "name": disp.Behaviour.TYPES["goto"]}}],
         "current_behaviour_index": -1,
         "status": disp.Task.STATUS_LIST["TO_DO"],
         "robot": "1",
         "start_time": "2018-06-29 07:55:27",
         "weight": 3,
         "priority": 3
         },
        {"id": "2",
         "behaviours": [{"id": "1", "parameters": {"to": "2", "name": disp.Behaviour.TYPES["goto"]}}],
         "current_behaviour_index": -1,
         "status": disp.Task.STATUS_LIST["TO_DO"],
         "robot": "2",
         "start_time": "2018-06-29 07:55:27",
         "weight": 3,
         "priority": 3
         },
    ]
    tasks = [disp.Task(data) for data in tasks_raw]
    dispatcher = disp.Dispatcher(get_graph(robots_raw), robots)
    plan = dispatcher.get_plan_all_free_robots(get_graph(robots_raw), robots, tasks)
    expected_result = {"1": {"taskId": "1", "nextEdge": (19, 42), "endBeh": False}}
    assert expected_result == plan


@pytest.mark.dispatcher
def test_dispatcher_from_different_pois_and_queues():
    robots_raw = [
        {"id": "1", "edge": (78, 79), "planningOn": True, "isFree": True, "timeRemaining": 0, "poiId": "0"},
        {"id": "2", "edge": (69, 70), "planningOn": True, "isFree": True, "timeRemaining": 0, "poiId": "0"},
        {"id": "3", "edge": (82, 83), "planningOn": True, "isFree": True, "timeRemaining": 0, "poiId": "0"},
        {"id": "4", "edge": (87, 88), "planningOn": True, "isFree": True, "timeRemaining": 0, "poiId": "0"},
        {"id": "5", "edge": (41, 19), "planningOn": True, "isFree": True, "timeRemaining": 0, "poiId": "0"},
        {"id": "6", "edge": (41, 19), "planningOn": True, "isFree": True, "timeRemaining": 0, "poiId": "0"},
        {"id": "7", "edge": (41, 19), "planningOn": True, "isFree": True, "timeRemaining": 0, "poiId": "0"}
    ]
    robots = {robot["id"]: disp.Robot(robot) for robot in robots_raw}
    tasks_raw = [
        {"id": "1",
         "behaviours": [{"id": "1", "parameters": {"to": "7", "name": disp.Behaviour.TYPES["goto"]}},
                        {"id": "2", "parameters": {"name": disp.Behaviour.TYPES["dock"]}},
                        {"id": "3", "parameters": {"name": disp.Behaviour.TYPES["wait"]}},
                        {"id": "4", "parameters": {"name": disp.Behaviour.TYPES["undock"]}}],
         "current_behaviour_index": -1,
         "status": disp.Task.STATUS_LIST["TO_DO"],
         "robot": "1",
         "start_time": "2018-06-29 07:15:27",
         "weight": 3,
         "priority": 3
         },
        {"id": "2",
         "behaviours": [{"id": "1", "parameters": {"to": "7", "name": disp.Behaviour.TYPES["goto"]}},
                        {"id": "2", "parameters": {"name": disp.Behaviour.TYPES["dock"]}},
                        {"id": "3", "parameters": {"name": disp.Behaviour.TYPES["wait"]}},
                        {"id": "4", "parameters": {"name": disp.Behaviour.TYPES["undock"]}}],
         "current_behaviour_index": -1,
         "status": disp.Task.STATUS_LIST["TO_DO"],
         "robot": "2",
         "start_time": "2018-06-29 07:18:27",
         "weight": 2,
         "priority": 2
         },
        {"id": "3",
         "behaviours": [{"id": "1", "parameters": {"to": "7", "name": disp.Behaviour.TYPES["goto"]}},
                        {"id": "2", "parameters": {"name": disp.Behaviour.TYPES["dock"]}},
                        {"id": "3", "parameters": {"name": disp.Behaviour.TYPES["wait"]}},
                        {"id": "4", "parameters": {"name": disp.Behaviour.TYPES["undock"]}}],
         "current_behaviour_index": -1,
         "status": disp.Task.STATUS_LIST["TO_DO"],
         "robot": "3",
         "start_time": "2018-06-29 07:19:27",
         "weight": 3,
         "priority": 3
         },
        {"id": "4",
         "behaviours": [{"id": "1", "parameters": {"to": "7", "name": disp.Behaviour.TYPES["goto"]}},
                        {"id": "2", "parameters": {"name": disp.Behaviour.TYPES["dock"]}},
                        {"id": "3", "parameters": {"name": disp.Behaviour.TYPES["wait"]}},
                        {"id": "4", "parameters": {"name": disp.Behaviour.TYPES["undock"]}}],
         "current_behaviour_index": -1,
         "status": disp.Task.STATUS_LIST["TO_DO"],
         "robot": "4",
         "start_time": "2018-06-29 07:22:27",
         "weight": 2,
         "priority": 2
         },
        {"id": "5",
         "behaviours": [{"id": "1", "parameters": {"to": "7", "name": disp.Behaviour.TYPES["goto"]}},
                        {"id": "2", "parameters": {"name": disp.Behaviour.TYPES["dock"]}},
                        {"id": "3", "parameters": {"name": disp.Behaviour.TYPES["wait"]}},
                        {"id": "4", "parameters": {"name": disp.Behaviour.TYPES["undock"]}}],
         "current_behaviour_index": -1,
         "status": disp.Task.STATUS_LIST["TO_DO"],
         "robot": None,
         "start_time": "2018-06-29 07:24:27",
         "weight": 3,
         "priority": 3
         },
        {"id": "6",
         "behaviours": [{"id": "1", "parameters": {"to": "7", "name": disp.Behaviour.TYPES["goto"]}},
                        {"id": "2", "parameters": {"name": disp.Behaviour.TYPES["dock"]}},
                        {"id": "3", "parameters": {"name": disp.Behaviour.TYPES["wait"]}},
                        {"id": "4", "parameters": {"name": disp.Behaviour.TYPES["undock"]}}],
         "current_behaviour_index": -1,
         "status": disp.Task.STATUS_LIST["TO_DO"],
         "robot": None,
         "start_time": "2018-06-29 07:27:27",
         "weight": 2,
         "priority": 2
         },
        {"id": "7",
         "behaviours": [{"id": "1", "parameters": {"to": "7", "name": disp.Behaviour.TYPES["goto"]}},
                        {"id": "2", "parameters": {"name": disp.Behaviour.TYPES["dock"]}},
                        {"id": "3", "parameters": {"name": disp.Behaviour.TYPES["wait"]}},
                        {"id": "4", "parameters": {"name": disp.Behaviour.TYPES["undock"]}}],
         "current_behaviour_index": -1,
         "status": disp.Task.STATUS_LIST["TO_DO"],
         "robot": None,
         "start_time": "2018-06-29 07:29:27",
         "weight": 3,
         "priority": 3
         },
        {"id": "8",
         "behaviours": [{"id": "1", "parameters": {"to": "7", "name": disp.Behaviour.TYPES["goto"]}},
                        {"id": "2", "parameters": {"name": disp.Behaviour.TYPES["dock"]}},
                        {"id": "3", "parameters": {"name": disp.Behaviour.TYPES["wait"]}},
                        {"id": "4", "parameters": {"name": disp.Behaviour.TYPES["undock"]}}],
         "current_behaviour_index": -1,
         "status": disp.Task.STATUS_LIST["TO_DO"],
         "robot": None,
         "start_time": "2018-06-29 07:35:27",
         "weight": 2,
         "priority": 2
         }
    ]
    tasks = [disp.Task(data) for data in tasks_raw]
    dispatcher = disp.Dispatcher(get_graph(robots_raw), robots)
    plan = dispatcher.get_plan_all_free_robots(get_graph(robots_raw), robots, tasks)
    expected_result = {"1": {"taskId": "1", "nextEdge": (79, 65), "endBeh": False},
                       "2": {"taskId": "2", "nextEdge": (70, 36), "endBeh": False},
                       "3": {"taskId": "3", "nextEdge": (83, 87), "endBeh": False},
                       "4": {"taskId": "4", "nextEdge": (88, 33), "endBeh": False},
                       "5": {"taskId": "5", "nextEdge": (19, 42), "endBeh": False},
                       "6": {"taskId": "7", "nextEdge": (19, 42), "endBeh": False}}
    # for step in plan:
        # print(step, plan[step])

    assert len(plan) == 6

    assert plan["1"] == expected_result["1"]
    plan.pop("1")
    assert plan["2"] == expected_result["2"]
    plan.pop("2")
    assert plan["3"] == expected_result["3"]
    plan.pop("3")
    assert plan["4"] == expected_result["4"]
    plan.pop("4")
    expected_steps = [expected_result["5"], expected_result["6"]]
    given_steps = [step_plan for step_plan in plan.values()]

    for step_plan in expected_steps:
        assert step_plan in given_steps
        # print("given_steps", given_steps)
        given_steps.remove(step_plan)


@pytest.mark.dispatcher
def test_dispatcher_from_poi6_to_poi7():
    robots_raw = [
        {"id": "1", "edge": (15, 16), "planningOn": True, "isFree": True, "timeRemaining": 0, "poiId": "0"}
    ]
    robots = {robot["id"]: disp.Robot(robot) for robot in robots_raw}
    tasks_raw = [
        {"id": "1",
         "behaviours": [{"id": "1", "parameters": {"to": "7", "name": disp.Behaviour.TYPES["goto"]}},
                        {"id": "2", "parameters": {"name": disp.Behaviour.TYPES["dock"]}},
                        {"id": "3", "parameters": {"name": disp.Behaviour.TYPES["wait"]}},
                        {"id": "4", "parameters": {"name": disp.Behaviour.TYPES["undock"]}}],
         "current_behaviour_index": 0,
         "status": disp.Task.STATUS_LIST["IN_PROGRESS"],
         "robot": "1",
         "start_time": "2018-06-29 07:55:27",
         "weight": 3,
         "priority": 3
         }
    ]
    tasks = [disp.Task(data) for data in tasks_raw]
    dispatcher = disp.Dispatcher(get_graph(robots_raw), robots)
    plan = dispatcher.get_plan_selected_robot(get_graph(robots_raw), robots, tasks, "1")
    # print(plan)
    expected_result = {"taskId": "1", "nextEdge": (16, 24), "endBeh": False}
    assert expected_result == plan

    robots_raw = [
        {"id": "1", "edge": (16, 24), "planningOn": True, "isFree": True, "timeRemaining": 0, "poiId": "0"}
    ]
    robots = {robot["id"]: disp.Robot(robot) for robot in robots_raw}
    tasks_raw = [
        {"id": "1",
         "behaviours": [{"id": "1", "parameters": {"to": "7", "name": disp.Behaviour.TYPES["goto"]}},
                        {"id": "2", "parameters": {"name": disp.Behaviour.TYPES["dock"]}},
                        {"id": "3", "parameters": {"name": disp.Behaviour.TYPES["wait"]}},
                        {"id": "4", "parameters": {"name": disp.Behaviour.TYPES["undock"]}}],
         "current_behaviour_index": 0,
         "status": disp.Task.STATUS_LIST["IN_PROGRESS"],
         "robot": "1",
         "start_time": "2018-06-29 07:55:27",
         "weight": 3,
         "priority": 3
         }
    ]
    tasks = [disp.Task(data) for data in tasks_raw]
    dispatcher = disp.Dispatcher(get_graph(robots_raw), robots)
    plan = dispatcher.get_plan_selected_robot(get_graph(robots_raw), robots, tasks, "1")
    # print(plan)
    expected_result = {"taskId": "1", "nextEdge": (24, 71), "endBeh": False}
    assert expected_result == plan


@pytest.mark.dispatcher
def test_dispatcher_assigned_tasks_swap_battery():
    # 1 zadanie przypisane normalnie, bo zaplanowana wymiana jest duzo pozniej              - brak wymiany
    # 2 zadanie - niewlasciwego typu, przypisac normalne zadanie                            - brak wymiany
    # 3 zadanie - brak wymiany w planie                                                     - brak wymiany
    # 4 zadanie - zlecenie wymiany, przekroczony start_time                                 - wymiana
    # 5 zadanie - dalsze wykonywanie zadan spowoduje rozladowanie robota, konieczna wymiana - wymiana
    robots_raw = [
        {"id": "1", "edge": (41, 19), "planningOn": True, "isFree": True, "timeRemaining": 0, "poiId": "0"},
        {"id": "2", "edge": (41, 19), "planningOn": True, "isFree": True, "timeRemaining": 0, "poiId": "0"},
        {"id": "3", "edge": (41, 19), "planningOn": True, "isFree": True, "timeRemaining": 0, "poiId": "0"},
        {"id": "4", "edge": (41, 19), "planningOn": True, "isFree": True, "timeRemaining": 0, "poiId": "0"},
        {"id": "5", "edge": (41, 19), "planningOn": True, "isFree": True, "timeRemaining": 0, "poiId": "0"}
    ]
    robots = {}
    for robot in robots_raw:
        new_robot = disp.Robot(robot)
        new_robot.battery.max_capacity = 40.0
        new_robot.battery.capacity = 1.0 if robot["id"] == "5" else 40.0
        new_robot.battery.drive_usage = 5.0
        new_robot.battery.stand_usage = 3.5
        robots[robot["id"]] = new_robot

    now = datetime.strptime(datetime.now().strftime("%Y-%m-%d %H:%M:%S"), ("%Y-%m-%d %H:%M:%S"))
    swap_time = (now + timedelta(minutes=15)).strftime("%Y-%m-%d %H:%M:%S")

    tasks_raw = [{"id": "1",
                  "behaviours": [{"id": "1", "parameters": {"to": "7", "name": disp.Behaviour.TYPES["goto"]}},
                                 {"id": "2", "parameters": {"name": disp.Behaviour.TYPES["dock"]}},
                                 {"id": "3", "parameters": {"name": disp.Behaviour.TYPES["wait"]}},
                                 {"id": "4", "parameters": {"name": disp.Behaviour.TYPES["undock"]}}],
                  "current_behaviour_index": -1,  # index tablicy nie zachowania
                  "status": disp.Task.STATUS_LIST["TO_DO"],
                  "robot": "1",
                  "start_time": "2018-06-29 07:37:27",
                  "weight": 2,
                  "priority": 2},
                 {"id": "2",
                  "behaviours": [{"id": "1", "parameters": {"to": "6", "name": disp.Behaviour.TYPES["goto"]}},
                                 {"id": "2", "parameters": {"name": disp.Behaviour.TYPES["wait"]}}],
                  "current_behaviour_index": -1,  # index tablicy nie zachowania
                  "status": disp.Task.STATUS_LIST["TO_DO"],
                  "robot": "2",
                  "start_time": "2018-06-29 07:37:27",
                  "weight": 2,
                  "priority": 2},
                 {"id": "3",
                  "behaviours": [{"id": "1", "parameters": {"to": "7", "name": disp.Behaviour.TYPES["goto"]}},
                                 {"id": "2", "parameters": {"name": disp.Behaviour.TYPES["dock"]}},
                                 {"id": "3", "parameters": {"name": disp.Behaviour.TYPES["wait"]}},
                                 {"id": "4", "parameters": {"name": disp.Behaviour.TYPES["undock"]}}],
                  "current_behaviour_index": -1,  # index tablicy nie zachowania
                  "status": disp.Task.STATUS_LIST["TO_DO"],
                  "robot": "3",
                  "start_time": "2018-06-29 07:37:27",
                  "weight": 2,
                  "priority": 2},
                 {"id": "4",
                  "behaviours": [{"id": "1", "parameters": {"to": "7", "name": disp.Behaviour.TYPES["goto"]}},
                                 {"id": "2", "parameters": {"name": disp.Behaviour.TYPES["dock"]}},
                                 {"id": "3", "parameters": {"name": disp.Behaviour.TYPES["wait"]}},
                                 {"id": "4", "parameters": {"name": disp.Behaviour.TYPES["undock"]}}],
                  "current_behaviour_index": -1,  # index tablicy nie zachowania
                  "status": disp.Task.STATUS_LIST["TO_DO"],
                  "robot": "4",
                  "start_time": "2018-06-29 07:37:27",
                  "weight": 2,
                  "priority": 2},
                 {"id": "5",
                  "behaviours": [{"id": "1", "parameters": {"to": "6", "name": disp.Behaviour.TYPES["goto"]}},
                                 {"id": "3", "parameters": {"name": disp.Behaviour.TYPES["wait"]}}],
                  "current_behaviour_index": -1,  # index tablicy nie zachowania
                  "status": disp.Task.STATUS_LIST["TO_DO"],
                  "robot": "5",
                  "start_time": "2018-06-29 07:37:27",
                  "weight": 2,
                  "priority": 2},
                 {"id": "swap_6",
                  "behaviours": [{"id": "1", "parameters": {"to": "4", "name": disp.Behaviour.TYPES["goto"]}},
                                 {"id": "2", "parameters": {"name": disp.Behaviour.TYPES["dock"]}},
                                 {"id": "3", "parameters": {"name": disp.Behaviour.TYPES["bat_ex"]}},
                                 {"id": "4", "parameters": {"name": disp.Behaviour.TYPES["undock"]}}],
                  "current_behaviour_index": -1,  # index tablicy nie zachowania
                  "status": disp.Task.STATUS_LIST["TO_DO"],
                  "robot": "1",
                  "start_time": swap_time,
                  "weight": 2,
                  "priority": 2},
                 {"id": "swap_7",
                  "behaviours": [{"id": "1", "parameters": {"to": "4", "name": disp.Behaviour.TYPES["goto"]}},
                                 {"id": "2", "parameters": {"name": disp.Behaviour.TYPES["dock"]}},
                                 {"id": "3", "parameters": {"name": disp.Behaviour.TYPES["bat_ex"]}},
                                 {"id": "4", "parameters": {"name": disp.Behaviour.TYPES["undock"]}}],
                  "current_behaviour_index": -1,  # index tablicy nie zachowania
                  "status": disp.Task.STATUS_LIST["TO_DO"],
                  "robot": "4",
                  "start_time": "2018-06-29 07:37:27",
                  "weight": 2,
                  "priority": 2},
                 {"id": "swap_8",
                  "behaviours": [{"id": "1", "parameters": {"to": "4", "name": disp.Behaviour.TYPES["goto"]}},
                                 {"id": "2", "parameters": {"name": disp.Behaviour.TYPES["dock"]}},
                                 {"id": "3", "parameters": {"name": disp.Behaviour.TYPES["bat_ex"]}},
                                 {"id": "4", "parameters": {"name": disp.Behaviour.TYPES["undock"]}}],
                  "current_behaviour_index": -1,  # index tablicy nie zachowania
                  "status": disp.Task.STATUS_LIST["TO_DO"],
                  "robot": "5",
                  "start_time": swap_time,
                  "weight": 2,
                  "priority": 2}
                 ]
    tasks = [disp.Task(data) for data in tasks_raw]
    dispatcher = disp.Dispatcher(get_graph(robots_raw), robots)
    dispatcher.set_tasks(tasks)
    dispatcher.separate_swap_tasks()
    dispatcher.swap_tasks.pop("3")
    print(dispatcher.swap_tasks)
    dispatcher.set_task_assigned_to_robots()

    assert dispatcher.robots_plan.robots["1"].task.id == tasks[0].id
    assert dispatcher.robots_plan.robots["2"].task.id == tasks[1].id
    assert dispatcher.robots_plan.robots["3"].task.id == tasks[2].id
    assert dispatcher.robots_plan.robots["4"].task.id == tasks[6].id
    assert dispatcher.robots_plan.robots["5"].task.id == tasks[7].id

@pytest.mark.dispatcher
def test_dispatcher_assigned_tasks_in_progress_swap_task():
    # 1 zadanie przypisane normalnie, bo zaplanowana wymiana jest duzo pozniej              - brak wymiany
    # 4 zadanie - zlecenie wymiany, przekroczony start_time                                 - wymiana
    # 5 zadanie - dalsze wykonywanie zadan spowoduje rozladowanie robota, konieczna wymiana - wymiana
    robots_raw = [
        {"id": "1", "edge": (41, 19), "planningOn": True, "isFree": True, "timeRemaining": 0, "poiId": "0"},
        {"id": "4", "edge": (41, 19), "planningOn": True, "isFree": True, "timeRemaining": 0, "poiId": "0"},
        {"id": "5", "edge": (41, 19), "planningOn": True, "isFree": True, "timeRemaining": 0, "poiId": "0"}
    ]
    robots = {}
    for robot in robots_raw:
        new_robot = disp.Robot(robot)
        new_robot.battery.max_capacity = 40.0
        new_robot.battery.capacity = 1.0 if robot["id"] == "5" else 40.0
        new_robot.battery.drive_usage = 5.0
        new_robot.battery.stand_usage = 3.5
        robots[robot["id"]] = new_robot

    now = datetime.strptime(datetime.now().strftime("%Y-%m-%d %H:%M:%S"), ("%Y-%m-%d %H:%M:%S"))
    swap_time = (now + timedelta(minutes=15)).strftime("%Y-%m-%d %H:%M:%S")

    tasks_raw = [{"id": "1",
                  "behaviours": [{"id": "1", "parameters": {"to": "7", "name": disp.Behaviour.TYPES["goto"]}},
                                 {"id": "2", "parameters": {"name": disp.Behaviour.TYPES["dock"]}},
                                 {"id": "3", "parameters": {"name": disp.Behaviour.TYPES["wait"]}},
                                 {"id": "4", "parameters": {"name": disp.Behaviour.TYPES["undock"]}}],
                  "current_behaviour_index": -1,  # index tablicy nie zachowania
                  "status": disp.Task.STATUS_LIST["TO_DO"],
                  "robot": "1",
                  "start_time": "2018-06-29 07:37:27",
                  "weight": 2,
                  "priority": 2},
                 {"id": "4",
                  "behaviours": [{"id": "1", "parameters": {"to": "7", "name": disp.Behaviour.TYPES["goto"]}},
                                 {"id": "2", "parameters": {"name": disp.Behaviour.TYPES["dock"]}},
                                 {"id": "3", "parameters": {"name": disp.Behaviour.TYPES["wait"]}},
                                 {"id": "4", "parameters": {"name": disp.Behaviour.TYPES["undock"]}}],
                  "current_behaviour_index": -1,  # index tablicy nie zachowania
                  "status": disp.Task.STATUS_LIST["TO_DO"],
                  "robot": "4",
                  "start_time": "2018-06-29 07:37:27",
                  "weight": 2,
                  "priority": 2},
                 {"id": "5",
                  "behaviours": [{"id": "1", "parameters": {"to": "6", "name": disp.Behaviour.TYPES["goto"]}},
                                 {"id": "3", "parameters": {"name": disp.Behaviour.TYPES["wait"]}}],
                  "current_behaviour_index": -1,  # index tablicy nie zachowania
                  "status": disp.Task.STATUS_LIST["TO_DO"],
                  "robot": "5",
                  "start_time": "2018-06-29 07:37:27",
                  "weight": 2,
                  "priority": 2},
                 {"id": "6",
                  "behaviours": [{"id": "1", "parameters": {"to": "4", "name": disp.Behaviour.TYPES["goto"]}},
                                 {"id": "2", "parameters": {"name": disp.Behaviour.TYPES["dock"]}},
                                 {"id": "3", "parameters": {"name": disp.Behaviour.TYPES["bat_ex"]}},
                                 {"id": "4", "parameters": {"name": disp.Behaviour.TYPES["undock"]}}],
                  "current_behaviour_index": -1,  # index tablicy nie zachowania
                  "status": disp.Task.STATUS_LIST["TO_DO"],
                  "robot": "1",
                  "start_time": swap_time,
                  "weight": 2,
                  "priority": 2},
                 {"id": "7",
                  "behaviours": [{"id": "1", "parameters": {"to": "4", "name": disp.Behaviour.TYPES["goto"]}},
                                 {"id": "2", "parameters": {"name": disp.Behaviour.TYPES["dock"]}},
                                 {"id": "3", "parameters": {"name": disp.Behaviour.TYPES["bat_ex"]}},
                                 {"id": "4", "parameters": {"name": disp.Behaviour.TYPES["undock"]}}],
                  "current_behaviour_index": -1,  # index tablicy nie zachowania
                  "status": disp.Task.STATUS_LIST["IN_PROGRESS"],
                  "robot": "4",
                  "start_time": "2018-06-29 07:37:27",
                  "weight": 2,
                  "priority": 2},
                 {"id": "8",
                  "behaviours": [{"id": "1", "parameters": {"to": "4", "name": disp.Behaviour.TYPES["goto"]}},
                                 {"id": "2", "parameters": {"name": disp.Behaviour.TYPES["dock"]}},
                                 {"id": "3", "parameters": {"name": disp.Behaviour.TYPES["bat_ex"]}},
                                 {"id": "4", "parameters": {"name": disp.Behaviour.TYPES["undock"]}}],
                  "current_behaviour_index": -1,  # index tablicy nie zachowania
                  "status": disp.Task.STATUS_LIST["TO_DO"],
                  "robot": "5",
                  "start_time": swap_time,
                  "weight": 2,
                  "priority": 2}
                 ]
    tasks = [disp.Task(data) for data in tasks_raw]
    dispatcher = disp.Dispatcher(get_graph(robots_raw), robots)
    dispatcher.set_tasks(tasks)
    dispatcher.init_robots_plan(robots)
    dispatcher.set_tasks_doing_by_robots()

    assert dispatcher.robots_plan.robots["1"].task == None
    assert dispatcher.robots_plan.robots["4"].task.id == tasks[4].id
    assert dispatcher.robots_plan.robots["5"].task == None

@pytest.mark.dispatcher
def test_dispatcher_free_robots_go_to_current_poi_goal():
    node_dict = {
        "1": {'pos': (0, 0), 'type': {'id': 2, 'nodeSection': 2}, 'name': None, 'poiId': '1'},
        "2": {'pos': (5, 0), 'type': {'id': 14, 'nodeSection': 5}, 'name': None, 'poiId': '0'},
        "3": {'pos': (5, -5), 'type': {'id': 14, 'nodeSection': 5}, 'name': None, 'poiId': '0'},
        "4": {'pos': (15, -5), 'type': {'id': 14, 'nodeSection': 5}, 'name': None, 'poiId': '0'},
        "5": {'pos': (15, -10), 'type': {'id': 1, 'nodeSection': 1}, 'name': None, 'poiId': '2'},
    }

    edge_dict = {
        "1": {"startNode": "1", "endNode": "2", "type": gc.way_type["narrowTwoWay"], "isActive": True},
        "2": {"startNode": "2", "endNode": "3", "type": gc.way_type["twoWay"], "isActive": True},
        "3": {"startNode": "3", "endNode": "4", "type": gc.way_type["twoWay"], "isActive": True},
        "4": {"startNode": "4", "endNode": "5", "type": gc.way_type["narrowTwoWay"], "isActive": True},
    }

    pois_raw = [{"id": "1", "pose": None, "type": gc.base_node_type["load"]},
                {"id": "2", "pose": None, "type": gc.base_node_type["charger"]}]

    graph_in = gc.SupervisorGraphCreator(node_dict, edge_dict, pois_raw)

    robots_raw = [
        {"id": "1", "edge": None, "planningOn": True, "isFree": True, "timeRemaining": 0, "poiId": "1"}
    ]

    robots = {}
    for robot in robots_raw:
        new_robot = disp.Robot(robot)
        new_robot.battery.max_capacity = 40.0
        new_robot.battery.capacity = 40.0
        new_robot.battery.drive_usage = 5.0
        new_robot.battery.stand_usage = 3.5
        robots[robot["id"]] = new_robot

    now = datetime.strptime(datetime.now().strftime("%Y-%m-%d %H:%M:%S"), ("%Y-%m-%d %H:%M:%S"))
    swap_time = (now + timedelta(minutes=15)).strftime("%Y-%m-%d %H:%M:%S")

    tasks_raw = [{"id": "1",
                  "behaviours": [{"id": "1", "parameters": {"to": "1", "name": disp.Behaviour.TYPES["goto"]}},
                                 {"id": "2", "parameters": {"name": disp.Behaviour.TYPES["wait"]}}],
                  "current_behaviour_index": -1,  # index tablicy nie zachowania
                  "status": disp.Task.STATUS_LIST["TO_DO"],
                  "robot": None,
                  "start_time": "2018-06-29 07:37:27",
                  "weight": 2,
                  "priority": 2}
                 ]
    tasks = [disp.Task(data) for data in tasks_raw]
    dispatcher = disp.Dispatcher(graph_in, robots)
    dispatcher.set_tasks(tasks)
    dispatcher.init_robots_plan(robots)
    assert dispatcher.get_plan_all_free_robots(graph_in,robots,tasks) == {'1': {'taskId': '1', 'nextEdge': (6, 5), 'endBeh': True}}
