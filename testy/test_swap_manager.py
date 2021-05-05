# -*- coding: utf-8 -*-
import pytest
from dispatcher import Robot, Task
import battery_swap_manager as swap
import graph_creator as gc
from datetime import datetime, timedelta

swap.SWAP_TIME = 3.0
swap.SWAP_TIME_BEFORE_ALERT = 5.0
swap.REPLAN_THRESHOLD = 1

pois_raw = [
    {"id": "1", "pose": None, "type": gc.base_node_type["queue"]},  # "name": "Q", "pos": (-5,7)
    {"id": "2", "pose": None, "type": gc.base_node_type["parking"]},  # "name": "P", "pos": (3,7)
    {"id": "3", "pose": None, "type": gc.base_node_type["unload"]},  # "name": "POI3", "pos": (11,7)
    {"id": "4", "pose": None, "type": gc.base_node_type["charger"]},  # "name": "C", "pos": (12,0)
    {"id": "5", "pose": None, "type": gc.base_node_type["unload-dock"]},  # "name": "POI4", "pos": (12,7)
    {"id": "6", "pose": None, "type": gc.base_node_type["load"]},  # "name": "POI1", "pos": (-3,-8)
    {"id": "7", "pose": None, "type": gc.base_node_type["charger"]}  # "name": "POI2", "pos": (-6,0)
]


@pytest.mark.swap_manager
def test_init():
    robots_raw = [
        {"id": "1", "edge": (41, 19), "planningOn": True, "isFree": True, "timeRemaining": 0, "poiId": "1"},
        {"id": "2", "edge": (41, 19), "planningOn": True, "isFree": True, "timeRemaining": 0, "poiId": "1"}
    ]
    robots = {data["id"]: Robot(data) for data in robots_raw}
    manager = swap.BatterySwapManager(robots, pois_raw)

    assert len(manager.swap_plan) == len(robots)
    for i in manager.swap_plan:
        assert "new" in manager.swap_plan[i]
        assert "updated" in manager.swap_plan[i]
        assert "in_progress" in manager.swap_plan[i]
        assert "tasks" in manager.swap_plan[i]
        for task in manager.swap_plan[i]["tasks"]:
            assert type(task) == Task


@pytest.mark.swap_manager
def test_task_id_name():
    robots_raw = [
        {"id": "1", "edge": (41, 19), "planningOn": True, "isFree": True, "timeRemaining": 0, "poiId": "1"},
        {"id": "2", "edge": (41, 19), "planningOn": True, "isFree": True, "timeRemaining": 0, "poiId": "1"}
    ]
    robots = {data["id"]: Robot(data) for data in robots_raw}
    manager = swap.BatterySwapManager(robots, pois_raw)

    assert len(manager.swap_plan) == len(robots)
    for i in manager.swap_plan:
        for task in manager.swap_plan[i]["tasks"]:
            assert "swap" in task.id


@pytest.mark.swap_manager
def test_swap_stations_1():
    robots_raw = [
        {"id": "1", "edge": (41, 19), "planningOn": True, "isFree": True, "timeRemaining": 0, "poiId": "1"},
        {"id": "2", "edge": (41, 19), "planningOn": True, "isFree": True, "timeRemaining": 0, "poiId": "1"}
    ]
    robots = {data["id"]: Robot(data) for data in robots_raw}
    manager = swap.BatterySwapManager(robots, pois_raw)

    swap_stations = [poi["id"] for poi in pois_raw if poi["type"] == gc.base_node_type["charger"]]
    assert len(swap_stations) == len(manager.swap_stations)
    for i in swap_stations:
        assert i in manager.swap_stations

    for robot_plan in manager.swap_plan.values():
        for task in robot_plan["tasks"]:
            assert task.behaviours[0].get_poi() in swap_stations


@pytest.mark.swap_manager
def test_swap_stations_multiple():
    pois_raw_data = [
        {"id": "1", "pose": None, "type": gc.base_node_type["queue"]},
        {"id": "2", "pose": None, "type": gc.base_node_type["charger"]},
        {"id": "3", "pose": None, "type": gc.base_node_type["unload"]},
        {"id": "4", "pose": None, "type": gc.base_node_type["charger"]},
        {"id": "5", "pose": None, "type": gc.base_node_type["unload-dock"]},
        {"id": "6", "pose": None, "type": gc.base_node_type["load"]},
        {"id": "7", "pose": None, "type": gc.base_node_type["charger"]}
    ]
    robots_raw = [
        {"id": "1", "edge": (41, 19), "planningOn": True, "isFree": True, "timeRemaining": 0, "poiId": "1"},
        {"id": "2", "edge": (41, 19), "planningOn": True, "isFree": True, "timeRemaining": 0, "poiId": "1"},
        {"id": "3", "edge": (41, 19), "planningOn": True, "isFree": True, "timeRemaining": 0, "poiId": "1"},
        {"id": "4", "edge": (41, 19), "planningOn": True, "isFree": True, "timeRemaining": 0, "poiId": "1"},
        {"id": "5", "edge": (41, 19), "planningOn": True, "isFree": True, "timeRemaining": 0, "poiId": "1"},
        {"id": "6", "edge": (41, 19), "planningOn": True, "isFree": True, "timeRemaining": 0, "poiId": "1"},
        {"id": "7", "edge": (41, 19), "planningOn": True, "isFree": True, "timeRemaining": 0, "poiId": "1"},
        {"id": "8", "edge": (41, 19), "planningOn": True, "isFree": True, "timeRemaining": 0, "poiId": "1"},
        {"id": "9", "edge": (41, 19), "planningOn": True, "isFree": True, "timeRemaining": 0, "poiId": "1"},
        {"id": "10", "edge": (41, 19), "planningOn": True, "isFree": True, "timeRemaining": 0, "poiId": "1"}
    ]
    robots = {data["id"]: Robot(data) for data in robots_raw}
    manager = swap.BatterySwapManager(robots, pois_raw_data)

    swap_stations = [poi["id"] for poi in pois_raw_data if poi["type"] == gc.base_node_type["charger"]]
    assert len(swap_stations) == len(manager.swap_stations)
    for i in swap_stations:
        assert i in manager.swap_stations

    for robot_plan in manager.swap_plan.values():
        for task in robot_plan["tasks"]:
            assert task.behaviours[0].get_poi() in swap_stations


@pytest.mark.swap_manager
def test_get_new_swap_tasks():
    robots_raw = [
        {"id": "1", "edge": (41, 19), "planningOn": True, "isFree": True, "timeRemaining": 0, "poiId": "1"},
        {"id": "2", "edge": (41, 19), "planningOn": True, "isFree": True, "timeRemaining": 0, "poiId": "1"},
        {"id": "3", "edge": (41, 19), "planningOn": True, "isFree": True, "timeRemaining": 0, "poiId": "1"},
        {"id": "4", "edge": (41, 19), "planningOn": True, "isFree": True, "timeRemaining": 0, "poiId": "1"},
        {"id": "5", "edge": (41, 19), "planningOn": True, "isFree": True, "timeRemaining": 0, "poiId": "1"},
        {"id": "6", "edge": (41, 19), "planningOn": True, "isFree": True, "timeRemaining": 0, "poiId": "1"},
        {"id": "7", "edge": (41, 19), "planningOn": True, "isFree": True, "timeRemaining": 0, "poiId": "1"},
        {"id": "8", "edge": (41, 19), "planningOn": True, "isFree": True, "timeRemaining": 0, "poiId": "1"},
        {"id": "9", "edge": (41, 19), "planningOn": True, "isFree": True, "timeRemaining": 0, "poiId": "1"},
        {"id": "10", "edge": (41, 19), "planningOn": True, "isFree": True, "timeRemaining": 0, "poiId": "1"}
    ]
    robots = {data["id"]: Robot(data) for data in robots_raw}
    manager = swap.BatterySwapManager(robots, pois_raw)
    manager.swap_plan["1"]["new"] = True
    manager.swap_plan["2"]["new"] = False
    manager.swap_plan["3"]["new"] = False
    manager.swap_plan["4"]["new"] = False
    manager.swap_plan["5"]["new"] = True
    manager.swap_plan["5"]["updated"] = True
    manager.swap_plan["6"]["new"] = False
    manager.swap_plan["7"]["new"] = False
    manager.swap_plan["8"]["new"] = False
    manager.swap_plan["9"]["new"] = True
    manager.swap_plan["10"]["new"] = False

    robot_id_swap_tasks = ["1", "5", "9"]
    new_tasks = manager.get_new_swap_tasks()

    assert len(robot_id_swap_tasks) == len(new_tasks)
    for i in robot_id_swap_tasks:
        is_task_exist = False
        for task in new_tasks:
            if task.robot_id == i:
                is_task_exist = True
                break
        assert is_task_exist


@pytest.mark.swap_manager
def test_get_tasks_to_update():
    robots_raw = [
        {"id": "1", "edge": (41, 19), "planningOn": True, "isFree": True, "timeRemaining": 0, "poiId": "1"},
        {"id": "2", "edge": (41, 19), "planningOn": True, "isFree": True, "timeRemaining": 0, "poiId": "1"},
        {"id": "3", "edge": (41, 19), "planningOn": True, "isFree": True, "timeRemaining": 0, "poiId": "1"},
        {"id": "4", "edge": (41, 19), "planningOn": True, "isFree": True, "timeRemaining": 0, "poiId": "1"},
        {"id": "5", "edge": (41, 19), "planningOn": True, "isFree": True, "timeRemaining": 0, "poiId": "1"},
        {"id": "6", "edge": (41, 19), "planningOn": True, "isFree": True, "timeRemaining": 0, "poiId": "1"},
        {"id": "7", "edge": (41, 19), "planningOn": True, "isFree": True, "timeRemaining": 0, "poiId": "1"},
        {"id": "8", "edge": (41, 19), "planningOn": True, "isFree": True, "timeRemaining": 0, "poiId": "1"},
        {"id": "9", "edge": (41, 19), "planningOn": True, "isFree": True, "timeRemaining": 0, "poiId": "1"},
        {"id": "10", "edge": (41, 19), "planningOn": True, "isFree": True, "timeRemaining": 0, "poiId": "1"}
    ]
    robots = {data["id"]: Robot(data) for data in robots_raw}
    manager = swap.BatterySwapManager(robots, pois_raw)
    manager.swap_plan["4"]["new"] = False
    manager.swap_plan["4"]["updated"] = True
    manager.swap_plan["5"]["new"] = False
    manager.swap_plan["5"]["updated"] = True
    manager.swap_plan["8"]["new"] = False
    manager.swap_plan["8"]["updated"] = True

    robot_id_updated_tasks = ["4", "5", "8"]
    updated_tasks = manager.get_tasks_to_update()

    roboty = [data.robot_id for data in updated_tasks]
    assert len(robot_id_updated_tasks) == len(updated_tasks)
    for i in robot_id_updated_tasks:
        is_task_exist = False
        for task in updated_tasks:
            if task.robot_id == i:
                is_task_exist = True
                break
        assert is_task_exist


@pytest.mark.swap_manager
def test_started_swap_task():
    robots_raw = [
        {"id": "1", "edge": (41, 19), "planningOn": True, "isFree": True, "timeRemaining": 0, "poiId": "1"},
        {"id": "2", "edge": (41, 19), "planningOn": True, "isFree": True, "timeRemaining": 0, "poiId": "1"},
        {"id": "3", "edge": (41, 19), "planningOn": True, "isFree": True, "timeRemaining": 0, "poiId": "1"},
        {"id": "4", "edge": (41, 19), "planningOn": True, "isFree": True, "timeRemaining": 0, "poiId": "1"},
        {"id": "5", "edge": (41, 19), "planningOn": True, "isFree": True, "timeRemaining": 0, "poiId": "1"}
    ]
    robots = {data["id"]: Robot(data) for data in robots_raw}
    manager = swap.BatterySwapManager(robots, pois_raw)

    manager.set_in_progress_task_status("2")
    manager.set_in_progress_task_status("5")

    robot_id_swap_tasks = ["2", "5"]

    for i in robots:
        if i in robot_id_swap_tasks and manager.swap_plan[i]["in_progress"]:
            assert True
        elif i not in robot_id_swap_tasks and not manager.swap_plan[i]["in_progress"]:
            assert True
        else:
            assert False


@pytest.mark.swap_manager
def test_finished_swap_task():
    robots_raw = [
        {"id": "1", "edge": (41, 19), "planningOn": True, "isFree": True, "timeRemaining": 0, "poiId": "1"},
        {"id": "2", "edge": (41, 19), "planningOn": True, "isFree": True, "timeRemaining": 0, "poiId": "1"},
        {"id": "3", "edge": (41, 19), "planningOn": True, "isFree": True, "timeRemaining": 0, "poiId": "1"},
        {"id": "4", "edge": (41, 19), "planningOn": True, "isFree": True, "timeRemaining": 0, "poiId": "1"},
        {"id": "5", "edge": (41, 19), "planningOn": True, "isFree": True, "timeRemaining": 0, "poiId": "1"}
    ]
    robots = {data["id"]: Robot(data) for data in robots_raw}
    manager = swap.BatterySwapManager(robots, pois_raw)

    robot_id_swap_tasks_to_remove = ["2", "5", "5"]
    count_previous_tasks = {i: len(manager.swap_plan[i]["tasks"]) for i in robot_id_swap_tasks_to_remove}
    for i in robot_id_swap_tasks_to_remove:
        manager.set_done_task_status(i)

    for i in robots:
        if i in robot_id_swap_tasks_to_remove and manager.swap_plan[i]["new"] and not manager.swap_plan[i]["updated"] \
                and not manager.swap_plan[i]["in_progress"]:
            assert True
            assert len(manager.swap_plan[i]["tasks"]) == count_previous_tasks[i] - 1
        elif i in robot_id_swap_tasks_to_remove:
            assert False


@pytest.mark.swap_manager
def test_check_if_replan_required_false():
    robots_raw = [
        {"id": "1", "edge": (41, 19), "planningOn": True, "isFree": True, "timeRemaining": 0, "poiId": "1"},
        {"id": "2", "edge": (41, 19), "planningOn": True, "isFree": True, "timeRemaining": 0, "poiId": "1"},
        {"id": "3", "edge": (41, 19), "planningOn": True, "isFree": True, "timeRemaining": 0, "poiId": "1"},
        {"id": "4", "edge": (41, 19), "planningOn": True, "isFree": True, "timeRemaining": 0, "poiId": "1"},
        {"id": "5", "edge": (41, 19), "planningOn": True, "isFree": True, "timeRemaining": 0, "poiId": "1"}
    ]
    robots = {data["id"]: Robot(data) for data in robots_raw}
    manager = swap.BatterySwapManager(robots, pois_raw)
    assert not manager._is_replan_required(robots)


@pytest.mark.swap_manager
def test_check_if_replan_required_false_close_to_replan():
    # zadanie wymiany na granicy progu replanowania, ktory nie zostal jeszcze przekroczony
    robots_raw = [
        {"id": "1", "edge": (41, 19), "planningOn": True, "isFree": True, "timeRemaining": 0, "poiId": "1"},
        {"id": "2", "edge": (41, 19), "planningOn": True, "isFree": True, "timeRemaining": 0, "poiId": "1"},
        {"id": "3", "edge": (41, 19), "planningOn": True, "isFree": True, "timeRemaining": 0, "poiId": "1"},
        {"id": "4", "edge": (41, 19), "planningOn": True, "isFree": True, "timeRemaining": 0, "poiId": "1"},
        {"id": "5", "edge": (41, 19), "planningOn": True, "isFree": True, "timeRemaining": 0, "poiId": "1"}
    ]
    robots = {data["id"]: Robot(data) for data in robots_raw}

    manager = swap.BatterySwapManager(robots, pois_raw)

    time_to_warn = robots["3"].battery.get_time_to_warn_allert()
    extend_time = time_to_warn + swap.SWAP_TIME_BEFORE_ALERT + swap.SWAP_TIME + (0.95*swap.REPLAN_THRESHOLD)
    manager.swap_plan["3"]["tasks"][0].start_time = (datetime.now() + timedelta(minutes=extend_time)).\
        strftime("%Y-%m-%d %H:%M:%S")

    assert not manager._is_replan_required(robots)


@pytest.mark.swap_manager
def test_check_if_replan_required_true_mising_robot_id():
    robots_raw = [
        {"id": "1", "edge": (41, 19), "planningOn": True, "isFree": True, "timeRemaining": 0, "poiId": "1"},
        {"id": "2", "edge": (41, 19), "planningOn": True, "isFree": True, "timeRemaining": 0, "poiId": "1"},
        {"id": "3", "edge": (41, 19), "planningOn": True, "isFree": True, "timeRemaining": 0, "poiId": "1"},
        {"id": "4", "edge": (41, 19), "planningOn": True, "isFree": True, "timeRemaining": 0, "poiId": "1"},
        {"id": "5", "edge": (41, 19), "planningOn": True, "isFree": True, "timeRemaining": 0, "poiId": "1"}
    ]
    robots = {data["id"]: Robot(data) for data in robots_raw}
    manager = swap.BatterySwapManager(robots, pois_raw)

    robots["7"] = Robot({"id": "7", "edge": (41, 19), "planningOn": True, "isFree": True, "timeRemaining": 0,
                         "poiId": "1"})
    assert manager._is_replan_required(robots)


@pytest.mark.swap_manager
def test_check_if_replan_required_true_empty_swap_tasks():
    robots_raw = [
        {"id": "1", "edge": (41, 19), "planningOn": True, "isFree": True, "timeRemaining": 0, "poiId": "1"},
        {"id": "2", "edge": (41, 19), "planningOn": True, "isFree": True, "timeRemaining": 0, "poiId": "1"},
        {"id": "3", "edge": (41, 19), "planningOn": True, "isFree": True, "timeRemaining": 0, "poiId": "1"},
        {"id": "4", "edge": (41, 19), "planningOn": True, "isFree": True, "timeRemaining": 0, "poiId": "1"},
        {"id": "5", "edge": (41, 19), "planningOn": True, "isFree": True, "timeRemaining": 0, "poiId": "1"}
    ]
    robots = {data["id"]: Robot(data) for data in robots_raw}
    manager = swap.BatterySwapManager(robots, pois_raw)
    manager.set_done_task_status("3")
    assert manager._is_replan_required(robots)


@pytest.mark.swap_manager
def test_check_if_replan_required_true_low_battery():
    # zadanie wymiany na granicy progu replanowania, ktory nie zostal jeszcze przekroczony
    robots_raw = [
        {"id": "1", "edge": (41, 19), "planningOn": True, "isFree": True, "timeRemaining": 0, "poiId": "1"},
        {"id": "2", "edge": (41, 19), "planningOn": True, "isFree": True, "timeRemaining": 0, "poiId": "1"},
        {"id": "3", "edge": (41, 19), "planningOn": True, "isFree": True, "timeRemaining": 0, "poiId": "1"},
        {"id": "4", "edge": (41, 19), "planningOn": True, "isFree": True, "timeRemaining": 0, "poiId": "1"},
        {"id": "5", "edge": (41, 19), "planningOn": True, "isFree": True, "timeRemaining": 0, "poiId": "1"}
    ]
    robots = {data["id"]: Robot(data) for data in robots_raw}

    manager = swap.BatterySwapManager(robots, pois_raw)

    time_to_warn = robots["3"].battery.get_time_to_warn_allert()
    extend_time = time_to_warn + swap.SWAP_TIME_BEFORE_ALERT + swap.SWAP_TIME + (1.2*swap.REPLAN_THRESHOLD)
    manager.swap_plan["3"]["tasks"][0].start_time = (datetime.now() + timedelta(minutes=extend_time)).\
        strftime("%Y-%m-%d %H:%M:%S")

    assert manager._is_replan_required(robots)


@pytest.mark.swap_manager
def test_create_new_plan_delete_robots():
    # zadanie wymiany na granicy progu replanowania, ktory nie zostal jeszcze przekroczony
    robots_raw1 = [
        {"id": "1", "edge": (41, 19), "planningOn": True, "isFree": True, "timeRemaining": 0, "poiId": "1"},
        {"id": "2", "edge": (41, 19), "planningOn": True, "isFree": True, "timeRemaining": 0, "poiId": "1"},
        {"id": "3", "edge": (41, 19), "planningOn": True, "isFree": True, "timeRemaining": 0, "poiId": "1"},
        {"id": "4", "edge": (41, 19), "planningOn": True, "isFree": True, "timeRemaining": 0, "poiId": "1"},
        {"id": "5", "edge": (41, 19), "planningOn": True, "isFree": True, "timeRemaining": 0, "poiId": "1"}
    ]
    robots1 = {data["id"]: Robot(data) for data in robots_raw1}
    manager = swap.BatterySwapManager(robots1, pois_raw)

    robots_raw2 = [
        {"id": "1", "edge": (41, 19), "planningOn": True, "isFree": True, "timeRemaining": 0, "poiId": "1"},
        {"id": "2", "edge": (41, 19), "planningOn": True, "isFree": True, "timeRemaining": 0, "poiId": "1"},
        {"id": "3", "edge": (41, 19), "planningOn": True, "isFree": True, "timeRemaining": 0, "poiId": "1"}
    ]
    robots2 = {data["id"]: Robot(data) for data in robots_raw2}
    manager._create_new_plan(robots2)

    assert len(manager.swap_plan) == len(robots2)
    for i in robots2:
        if i not in manager.swap_plan:
            assert False
    print(type(robots2))
    assert not manager._is_replan_required(robots2)


@pytest.mark.swap_manager
def test_create_new_plan_add_plan_missing_robots():
    # zadanie wymiany na granicy progu replanowania, ktory nie zostal jeszcze przekroczony
    robots_raw1 = [
        {"id": "1", "edge": (41, 19), "planningOn": True, "isFree": True, "timeRemaining": 0, "poiId": "1"},
        {"id": "2", "edge": (41, 19), "planningOn": True, "isFree": True, "timeRemaining": 0, "poiId": "1"},
        {"id": "3", "edge": (41, 19), "planningOn": True, "isFree": True, "timeRemaining": 0, "poiId": "1"}
    ]
    robots1 = {data["id"]: Robot(data) for data in robots_raw1}
    manager = swap.BatterySwapManager(robots1, pois_raw)
    assert len(manager.swap_plan) == len(robots1)
    for i in robots1:
        if i not in manager.swap_plan:
            assert False

    robots_raw2 = [
        {"id": "1", "edge": (41, 19), "planningOn": True, "isFree": True, "timeRemaining": 0, "poiId": "1"},
        {"id": "2", "edge": (41, 19), "planningOn": True, "isFree": True, "timeRemaining": 0, "poiId": "1"},
        {"id": "3", "edge": (41, 19), "planningOn": True, "isFree": True, "timeRemaining": 0, "poiId": "1"},
        {"id": "4", "edge": (41, 19), "planningOn": True, "isFree": True, "timeRemaining": 0, "poiId": "1"},
        {"id": "5", "edge": (41, 19), "planningOn": True, "isFree": True, "timeRemaining": 0, "poiId": "1"}
    ]
    robots2 = {data["id"]: Robot(data) for data in robots_raw2}
    manager.get_new_swap_tasks()
    assert not manager.new_task  # po pobraniu zadan flaga nie jest ustawiona
    manager._create_new_plan(robots2)

    assert len(manager.swap_plan) == len(robots2)
    for i in robots2:
        if i not in manager.swap_plan:
            assert False

    assert not manager._is_replan_required(robots2)
    assert manager.new_task
    assert not manager.updated_task


@pytest.mark.swap_manager
def test_create_new_plan_add_plan_missing_tasks():
    # zadanie wymiany na granicy progu replanowania, ktory nie zostal jeszcze przekroczony
    robots_raw = [
        {"id": "1", "edge": (41, 19), "planningOn": True, "isFree": True, "timeRemaining": 0, "poiId": "1"},
        {"id": "2", "edge": (41, 19), "planningOn": True, "isFree": True, "timeRemaining": 0, "poiId": "1"},
        {"id": "3", "edge": (41, 19), "planningOn": True, "isFree": True, "timeRemaining": 0, "poiId": "1"},
        {"id": "4", "edge": (41, 19), "planningOn": True, "isFree": True, "timeRemaining": 0, "poiId": "1"},
        {"id": "5", "edge": (41, 19), "planningOn": True, "isFree": True, "timeRemaining": 0, "poiId": "1"}
    ]
    robots = {data["id"]: Robot(data) for data in robots_raw}
    manager = swap.BatterySwapManager(robots, pois_raw)
    manager.get_new_swap_tasks()
    assert not manager.new_task  # po pobraniu zadan flaga nie jest ustawiona

    manager.set_done_task_status("1")
    manager.set_done_task_status("3")
    manager.set_done_task_status("4")

    manager._create_new_plan(robots)
    assert manager.new_task
    assert not manager.updated_task
    assert len(manager.get_new_swap_tasks()) == 3

    assert not manager._is_replan_required(robots)


@pytest.mark.swap_manager
def test_create_new_plan_update_swap_time():
    # zadanie wymiany na granicy progu replanowania, ktory nie zostal jeszcze przekroczony
    robots_raw = [
        {"id": "1", "edge": (41, 19), "planningOn": True, "isFree": True, "timeRemaining": 0, "poiId": "1"},
        {"id": "2", "edge": (41, 19), "planningOn": True, "isFree": True, "timeRemaining": 0, "poiId": "1"},
        {"id": "3", "edge": (41, 19), "planningOn": True, "isFree": True, "timeRemaining": 0, "poiId": "1"},
        {"id": "4", "edge": (41, 19), "planningOn": True, "isFree": True, "timeRemaining": 0, "poiId": "1"},
        {"id": "5", "edge": (41, 19), "planningOn": True, "isFree": True, "timeRemaining": 0, "poiId": "1"}
    ]
    robots = {data["id"]: Robot(data) for data in robots_raw}

    manager = swap.BatterySwapManager(robots, pois_raw)
    manager.get_new_swap_tasks()
    manager.get_tasks_to_update()

    time_to_warn = robots["3"].battery.get_time_to_warn_allert()
    extend_time = time_to_warn + swap.SWAP_TIME_BEFORE_ALERT + swap.SWAP_TIME + (1.2*swap.REPLAN_THRESHOLD)
    manager.swap_plan["3"]["tasks"][0].start_time = (datetime.now() + timedelta(minutes=extend_time)).\
        strftime("%Y-%m-%d %H:%M:%S")

    assert manager._is_replan_required(robots)
    assert manager._is_robot_update_required(robots["3"])

    assert not manager.new_task
    assert not manager.updated_task
    manager._create_new_plan(robots)
    assert not manager.new_task
    assert manager.updated_task

    tasks_to_update = manager.get_tasks_to_update()
    assert len(tasks_to_update) == 1
    assert tasks_to_update[0].robot_id == "3"
    assert len(manager.get_new_swap_tasks()) == 0

    assert not manager._is_replan_required(robots)
    assert not manager._is_robot_update_required(robots["3"])
