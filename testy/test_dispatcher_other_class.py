# -*- coding: utf-8 -*-
import pytest
import random
import dispatcher as disp


# Niektore testy odnosza sie do walidacji danych dla klasy Task, Robot. Moga nie przejsc, gdy integracja z supervisorem
# i reszta systemu byla sprawdzana bez tej funkcjonalnosci
# ------------------------------ Behaviour input data ------------------------------ #
@pytest.mark.behaviour_data
def test_behaviour_check_if_method_exist():
    behaviour = disp.Behaviour({"id": "1", "parameters": {"to": "5", "name": disp.Behaviour.TYPES["goto"]}})
    assert "get_type" in dir(behaviour)
    assert "check_if_go_to" in dir(behaviour)
    assert "get_poi" in dir(behaviour)
    assert "validate_data" in dir(behaviour)
    assert "get_info" in dir(behaviour)

    assert "id" in dir(behaviour)
    assert "parameters" in dir(behaviour)


@pytest.mark.behaviour_data
def test_does_not_raise_on_valid_input():
    param_name = disp.Behaviour.PARAM
    behaviour_goto = {param_name["ID"]: "fa33n52",
                      param_name["BEH_PARAM"]: {param_name["TYPE"]: disp.Behaviour.TYPES["goto"],
                                                param_name["BEH_POI"]: "53ge"}}
    behaviour_dock = {param_name["ID"]: "fa33n52",
                      param_name["BEH_PARAM"]: {param_name["TYPE"]: disp.Behaviour.TYPES["dock"]}}
    behaviour_wait = {param_name["ID"]: "fa33n52",
                      param_name["BEH_PARAM"]: {param_name["TYPE"]: disp.Behaviour.TYPES["wait"]}}
    behaviour_undock = {param_name["ID"]: "fa33n52",
                        param_name["BEH_PARAM"]: {param_name["TYPE"]: disp.Behaviour.TYPES["undock"]}}
    try:
        disp.Behaviour(behaviour_goto).validate_data(behaviour_goto)
        disp.Behaviour(behaviour_dock).validate_data(behaviour_dock)
        disp.Behaviour(behaviour_wait).validate_data(behaviour_wait)
        disp.Behaviour(behaviour_undock).validate_data(behaviour_undock)
    except disp.DispatcherError:
        assert False
    else:
        assert True


@pytest.mark.behaviour_data
def test_throws_input_data_exception_invalid_input_behaviour_type_list():
    behaviour_goto = []
    try:
        disp.Behaviour(behaviour_goto)
    except disp.WrongBehaviourInputData as error1:
        assert "Behaviour should be dict type but {} was given.".format(type([behaviour_goto])) == str(error1)
    else:
        assert False


@pytest.mark.behaviour_data
def test_throws_input_data_exception_invalid_input_behaviour_type_str():
    behaviour_goto = "test"
    try:
        disp.Behaviour(behaviour_goto)
    except disp.WrongBehaviourInputData as error:
        assert "Behaviour should be dict type but {} was given.".format(type(behaviour_goto)) == str(error)
    else:
        assert False


@pytest.mark.behaviour_data
def test_throws_input_data_exception_invalid_input_behaviour_type_none():
    behaviour_goto = None
    try:
        disp.Behaviour(behaviour_goto)
    except disp.WrongBehaviourInputData as error:
        assert "Behaviour should be dict type but {} was given.".format(type(behaviour_goto)) == str(error)
    else:
        assert False


@pytest.mark.behaviour_data
def test_throws_input_data_exception_missing_input_id_name():
    param_name = disp.Behaviour.PARAM
    behaviour_goto = {"id_nowe": "fa33n52",
                      param_name["BEH_PARAM"]: {param_name["TYPE"]: disp.Behaviour.TYPES["goto"],
                                                param_name["BEH_POI"]: "53ge"}}
    try:
        disp.Behaviour(behaviour_goto)
    except disp.WrongBehaviourInputData as error:
        assert "Behaviour param '{}' name doesn't exist.".format(disp.Behaviour.PARAM["ID"]) == str(error)
    else:
        assert False


@pytest.mark.behaviour_data
def test_throws_input_data_exception_invalid_input_id_type_int():
    param_name = disp.Behaviour.PARAM
    behaviour_goto = {param_name["ID"]: 542,
                      param_name["BEH_PARAM"]: {param_name["TYPE"]: disp.Behaviour.TYPES["goto"],
                                                param_name["BEH_POI"]: "53ge"}}
    try:
        disp.Behaviour(behaviour_goto)
    except disp.WrongBehaviourInputData as error:
        type_id = type(behaviour_goto[param_name["ID"]])
        assert "Behaviour ID should be string but '{}' was given".format(type_id) == str(error)
    else:
        assert False


@pytest.mark.behaviour_data
def test_throws_input_data_exception_invalid_input_id_type_none():
    param_name = disp.Behaviour.PARAM
    behaviour_goto = {param_name["ID"]: None,
                      param_name["BEH_PARAM"]: {param_name["TYPE"]: disp.Behaviour.TYPES["goto"],
                                                param_name["BEH_POI"]: "53ge"}}
    try:
        disp.Behaviour(behaviour_goto)
    except disp.WrongBehaviourInputData as error:
        type_id = type(behaviour_goto[param_name["ID"]])
        assert "Behaviour ID should be string but '{}' was given".format(type_id) == str(error)
    else:
        assert False


@pytest.mark.behaviour_data
def test_throws_input_data_exception_missing_input_parameter_name():
    param_name = disp.Behaviour.PARAM
    behaviour_goto = {param_name["ID"]: "fa33n52",
                      "test": {param_name["TYPE"]: disp.Behaviour.TYPES["goto"], param_name["BEH_POI"]: "53ge"}}
    try:
        disp.Behaviour(behaviour_goto)
    except disp.WrongBehaviourInputData as error:
        assert "Behaviour param '{}' name doesn't exist.".format(param_name["BEH_PARAM"]) == str(error)
    else:
        assert False


@pytest.mark.behaviour_data
def test_throws_input_data_exception_invalid_input_parameter_type_none():
    param_name = disp.Behaviour.PARAM
    behaviour_goto = {param_name["ID"]: "fa33n52", param_name["BEH_PARAM"]: None}
    try:
        disp.Behaviour(behaviour_goto)
    except disp.WrongBehaviourInputData as error:
        param_type = type(behaviour_goto[param_name["BEH_PARAM"]])
        assert "Behaviour parameters should be dict but '{}' was given".format(param_type) == str(error)
    else:
        assert False


@pytest.mark.behaviour_data
def test_throws_input_data_exception_invalid_input_parameter_type_int():
    param_name = disp.Behaviour.PARAM
    behaviour_goto = {param_name["ID"]: "fa33n52", param_name["BEH_PARAM"]: 4243}
    try:
        disp.Behaviour(behaviour_goto)
    except disp.WrongBehaviourInputData as error:
        param_type = type(behaviour_goto[param_name["BEH_PARAM"]])
        assert "Behaviour parameters should be dict but '{}' was given".format(param_type) == str(error)
    else:
        assert False


@pytest.mark.behaviour_data
def test_throws_input_data_exception_invalid_input_parameter_type_string():
    param_name = disp.Behaviour.PARAM
    behaviour_goto = {param_name["ID"]: "fa33n52", param_name["BEH_PARAM"]: "jakis tekst"}
    try:
        disp.Behaviour(behaviour_goto)
    except disp.WrongBehaviourInputData as error:
        param_type = type(behaviour_goto[param_name["BEH_PARAM"]])
        assert "Behaviour parameters should be dict but '{}' was given".format(param_type) == str(error)
    else:
        assert False


@pytest.mark.behaviour_data
def test_throws_input_data_exception_missing_behaviour_name():
    param_name = disp.Behaviour.PARAM
    behaviour_goto = {param_name["ID"]: "fa33n52",
                      param_name["BEH_PARAM"]: {param_name["BEH_POI"]: "53ge"}}
    try:
        disp.Behaviour(behaviour_goto)
    except disp.WrongBehaviourInputData as error:
        assert "In behaviours parameters '{}' name doesn't exist.".format(param_name["TYPE"]) == str(error)
    else:
        assert False


@pytest.mark.behaviour_data
def test_throws_input_data_exception_invalid_behaviour_name_type_none():
    param_name = disp.Behaviour.PARAM
    behaviour_goto = {param_name["ID"]: "fa33n52",
                      param_name["BEH_PARAM"]: {param_name["TYPE"]: None,
                                                param_name["BEH_POI"]: "53ge"}}
    try:
        disp.Behaviour(behaviour_goto)
    except disp.WrongBehaviourInputData as error:
        type_name = type(behaviour_goto[param_name["BEH_PARAM"]][param_name["TYPE"]])
        assert "Behaviour '{}' should be str.".format(type_name) == str(error)
    else:
        assert False


@pytest.mark.behaviour_data
def test_throws_input_data_exception_invalid_behaviour_name_list():
    param_name = disp.Behaviour.PARAM
    behaviour_goto = {param_name["ID"]: "fa33n52",
                      param_name["BEH_PARAM"]: {param_name["TYPE"]: [],
                                                param_name["BEH_POI"]: "53ge"}}
    try:
        disp.Behaviour(behaviour_goto)
    except disp.WrongBehaviourInputData as error:
        type_name = type(behaviour_goto[param_name["BEH_PARAM"]][param_name["TYPE"]])
        assert "Behaviour '{}' should be str.".format(type_name) == str(error)
    else:
        assert False


@pytest.mark.behaviour_data
def test_throws_input_data_exception_invalid_behaviour_name_type_int():
    param_name = disp.Behaviour.PARAM
    behaviour_goto = {param_name["ID"]: "fa33n52",
                      param_name["BEH_PARAM"]: {param_name["TYPE"]: 7,
                                                param_name["BEH_POI"]: "53ge"}}
    try:
        disp.Behaviour(behaviour_goto)
    except disp.WrongBehaviourInputData as error:
        type_name = type(behaviour_goto[param_name["BEH_PARAM"]][param_name["TYPE"]])
        assert "Behaviour '{}' should be str.".format(type_name) == str(error)
    else:
        assert False


@pytest.mark.behaviour_data
def test_throws_input_data_exception_missing_poi_in_goto_behaviour():
    param_name = disp.Behaviour.PARAM
    behaviour_goto = {param_name["ID"]: "fa33n52",
                      param_name["BEH_PARAM"]: {param_name["TYPE"]: disp.Behaviour.TYPES["goto"]}}
    try:
        disp.Behaviour(behaviour_goto)
    except disp.WrongBehaviourInputData as error:
        assert "Missing '{}' name for {} behaviour.".format(param_name["BEH_POI"], disp.Behaviour.TYPES["goto"]) \
               == str(error)
    else:
        assert False


@pytest.mark.behaviour_data
def test_throws_input_data_exception_poi_wrong_type_int():
    param_name = disp.Behaviour.PARAM
    behaviour_goto = {param_name["ID"]: "fa33n52",
                      param_name["BEH_PARAM"]: {param_name["TYPE"]: disp.Behaviour.TYPES["goto"],
                                                param_name["BEH_POI"]: 5}}
    try:
        disp.Behaviour(behaviour_goto)
    except disp.WrongBehaviourInputData as error:
        poi_type = type(behaviour_goto[param_name["BEH_PARAM"]][param_name["BEH_POI"]])
        assert "Behaviour goto poi id should be a string but {} was given.".format(poi_type) == str(error)
    else:
        assert False


# ------------------------------ Behaviours methods ------------------------------ #
@pytest.mark.behaviour_methods
def test_ok_input_data_goto():
    param_name = disp.Behaviour.PARAM
    behaviour_raw_data = {param_name["ID"]: "fa33n52",
                          param_name["BEH_PARAM"]: {param_name["TYPE"]: disp.Behaviour.TYPES["goto"],
                                                    param_name["BEH_POI"]: "53ge"}}

    behaviour_class = disp.Behaviour(behaviour_raw_data)
    assert behaviour_class.id == "fa33n52"
    assert behaviour_class.parameters ==\
           {param_name["TYPE"]: disp.Behaviour.TYPES["goto"], param_name["BEH_POI"]: "53ge"}


@pytest.mark.behaviour_methods
def test_ok_input_data_dock():
    param_name = disp.Behaviour.PARAM
    behaviour_raw_data = {param_name["ID"]: "fa33n52",
                          param_name["BEH_PARAM"]: {param_name["TYPE"]: disp.Behaviour.TYPES["dock"]}}

    behaviour_class = disp.Behaviour(behaviour_raw_data)
    assert behaviour_class.id == "fa33n52"
    assert behaviour_class.parameters == {param_name["TYPE"]: disp.Behaviour.TYPES["dock"]}


@pytest.mark.behaviour_methods
def test_ok_input_data_wait():
    param_name = disp.Behaviour.PARAM
    behaviour_raw_data = {param_name["ID"]: "fa33n52",
                          param_name["BEH_PARAM"]: {param_name["TYPE"]: disp.Behaviour.TYPES["wait"]}}

    behaviour_class = disp.Behaviour(behaviour_raw_data)
    assert behaviour_class.id == "fa33n52"
    assert behaviour_class.parameters == {param_name["TYPE"]: disp.Behaviour.TYPES["wait"]}


@pytest.mark.behaviour_methods
def test_ok_input_data_undock():
    param_name = disp.Behaviour.PARAM
    behaviour_raw_data = {param_name["ID"]: "fa33n52",
                          param_name["BEH_PARAM"]: {param_name["TYPE"]: disp.Behaviour.TYPES["undock"]}}

    behaviour_class = disp.Behaviour(behaviour_raw_data)
    assert behaviour_class.id, "fa33n52"
    assert behaviour_class.parameters == {param_name["TYPE"]: disp.Behaviour.TYPES["undock"]}


@pytest.mark.behaviour_methods
def test_check_if_type_is_goto():
    param_name = disp.Behaviour.PARAM
    behaviour_raw_data = {param_name["ID"]: "fa33n52",
                          param_name["BEH_PARAM"]: {param_name["TYPE"]: disp.Behaviour.TYPES["goto"],
                                                    param_name["BEH_POI"]: "53ge"}}

    behaviour_class = disp.Behaviour(behaviour_raw_data)
    assert behaviour_class.get_type(), disp.Behaviour.TYPES["goto"]


@pytest.mark.behaviour_methods
def test_check_if_type_is_dock():
    param_name = disp.Behaviour.PARAM
    behaviour_raw_data = {param_name["ID"]: "fa33n52",
                          param_name["BEH_PARAM"]: {param_name["TYPE"]: disp.Behaviour.TYPES["dock"]}}

    behaviour_class = disp.Behaviour(behaviour_raw_data)
    assert behaviour_class.get_type() == disp.Behaviour.TYPES["dock"]


@pytest.mark.behaviour_methods
def test_check_if_type_is_wait():
    param_name = disp.Behaviour.PARAM
    behaviour_raw_data = {param_name["ID"]: "fa33n52",
                          param_name["BEH_PARAM"]: {param_name["TYPE"]: disp.Behaviour.TYPES["wait"]}}

    behaviour_class = disp.Behaviour(behaviour_raw_data)
    assert behaviour_class.get_type() == disp.Behaviour.TYPES["wait"]


@pytest.mark.behaviour_methods
def test_check_if_type_is_undock():
    param_name = disp.Behaviour.PARAM
    behaviour_raw_data = {param_name["ID"]: "fa33n52",
                          param_name["BEH_PARAM"]: {param_name["TYPE"]: disp.Behaviour.TYPES["undock"]}}

    behaviour_class = disp.Behaviour(behaviour_raw_data)
    assert behaviour_class.get_type() == disp.Behaviour.TYPES["undock"]


@pytest.mark.behaviour_methods
def test_check_if_goto_function():
    param_name = disp.Behaviour.PARAM
    behaviour_goto = {param_name["ID"]: "fa33n52",
                      param_name["BEH_PARAM"]: {param_name["TYPE"]: disp.Behaviour.TYPES["goto"],
                                                param_name["BEH_POI"]: "53ge"}}
    behaviour_dock = {param_name["ID"]: "fa33n52",
                      param_name["BEH_PARAM"]: {param_name["TYPE"]: disp.Behaviour.TYPES["dock"]}}
    behaviour_wait = {param_name["ID"]: "fa33n52",
                      param_name["BEH_PARAM"]: {param_name["TYPE"]: disp.Behaviour.TYPES["wait"]}}
    behaviour_undock = {param_name["ID"]: "fa33n52",
                        param_name["BEH_PARAM"]: {param_name["TYPE"]: disp.Behaviour.TYPES["undock"]}}

    assert disp.Behaviour(behaviour_goto).check_if_go_to()
    assert not disp.Behaviour(behaviour_dock).check_if_go_to()
    assert not disp.Behaviour(behaviour_wait).check_if_go_to()
    assert not disp.Behaviour(behaviour_undock).check_if_go_to()


@pytest.mark.behaviour_methods
def test_get_poi_behaviour():
    param_name = disp.Behaviour.PARAM
    behaviour_goto = {param_name["ID"]: "fa33n52",
                      param_name["BEH_PARAM"]: {param_name["TYPE"]: disp.Behaviour.TYPES["goto"],
                                                param_name["BEH_POI"]: "53ge"}}
    behaviour_dock = {param_name["ID"]: "fa33n52",
                      param_name["BEH_PARAM"]: {param_name["TYPE"]: disp.Behaviour.TYPES["dock"]}}
    behaviour_wait = {param_name["ID"]: "fa33n52",
                      param_name["BEH_PARAM"]: {param_name["TYPE"]: disp.Behaviour.TYPES["wait"]}}
    behaviour_undock = {param_name["ID"]: "fa33n52",
                        param_name["BEH_PARAM"]: {param_name["TYPE"]: disp.Behaviour.TYPES["undock"]}}

    assert disp.Behaviour(behaviour_goto).get_poi() == "53ge"
    assert disp.Behaviour(behaviour_dock).get_poi() is None
    assert disp.Behaviour(behaviour_wait).get_poi() is None
    assert disp.Behaviour(behaviour_undock).get_poi() is None


# ------------------------------ Task input data ------------------------------ #
@pytest.mark.task_data
def test_task_check_if_method_exist():
    task = disp.Task({"id": "7",
                      "behaviours": [{"id": "1", "parameters": {"to": "5", "name": disp.Behaviour.TYPES["goto"]}},
                                     {"id": "2", "parameters": {"name": disp.Behaviour.TYPES["dock"]}},
                                     {"id": "3", "parameters": {"name": disp.Behaviour.TYPES["wait"]}},
                                     {"id": "4", "parameters": {"name": disp.Behaviour.TYPES["undock"]}},
                                     {"id": "5", "parameters": {"to": "1", "name": disp.Behaviour.TYPES["goto"]}}],
                      "current_behaviour_index": -1,  # index tablicy nie zachowania
                      "status": disp.Task.STATUS_LIST["TO_DO"],
                      "robot": "3",
                      "start_time": "2018-06-29 07:15:27",
                      "weight": 2,
                      "priority": 2
                      })
    assert "get_poi_goal" in dir(task)
    assert "get_current_behaviour" in dir(task)
    assert "check_if_task_started" in dir(task)
    assert "validate_input" in dir(task)
    assert "get_info" in dir(task)  # TODO testy
    assert "is_planned_swap" in dir(task)

    assert "id" in dir(task)
    assert "robot_id" in dir(task)
    assert "start_time" in dir(task)
    assert "behaviours" in dir(task)
    assert "current_behaviour_index" in dir(task)
    assert "status" in dir(task)
    assert "weight" in dir(task)
    assert "priority" in dir(task)
    assert "index" in dir(task)


@pytest.mark.task_data
def test_throws_input_data_exception_raise_on_valid_input():
    raised = False
    task_data = {"id": "1",
                 "behaviours": [{"id": "1", "parameters": {"to": "5", "name": disp.Behaviour.TYPES["goto"]}},
                                {"id": "2", "parameters": {"name": disp.Behaviour.TYPES["dock"]}},
                                {"id": "3", "parameters": {"name": disp.Behaviour.TYPES["wait"]}},
                                {"id": "4", "parameters": {"name": disp.Behaviour.TYPES["undock"]}},
                                {"id": "5", "parameters": {"to": "1", "name": disp.Behaviour.TYPES["goto"]}}],
                 "current_behaviour_index": 0,
                 "status": disp.Task.STATUS_LIST["ASSIGN"],
                 "robot": "4",
                 "start_time": "2018-06-29 07:23:27",
                 "weight": 3}
    try:
        disp.Task(task_data)
    except disp.WrongTaskInputData:
        raised = True
    assert not raised


@pytest.mark.skip("input_data_validation")
@pytest.mark.task_data
def test_throws_input_data_exception_input_data_type_list():
    task_data = []
    try:
        disp.Task(task_data)
    except disp.WrongTaskInputData as error:
        assert "Wrong task input data type." == str(error)
    else:
        assert False


@pytest.mark.skip("input_data_validation")
@pytest.mark.task_data
def test_throws_input_data_exception_input_data_type_none():
    task_data = None
    try:
        disp.Task(task_data)
    except disp.WrongTaskInputData as error:
        assert "Wrong task input data type." == str(error)
    else:
        assert False


@pytest.mark.skip("input_data_validation")
@pytest.mark.task_data
def test_throws_input_data_exception_input_data_string():
    task_data = "teaffeafwae"
    try:
        disp.Task(task_data)
    except disp.WrongTaskInputData as error:
        assert "Wrong task input data type." == str(error)
    else:
        assert False


@pytest.mark.skip("input_data_validation")
@pytest.mark.task_data
def test_throws_input_data_exception_missing_task_id():
    task_data = {"idf": "1",
                 "behaviours": [{"id": "1", "parameters": {"to": "5", "name": disp.Behaviour.TYPES["goto"]}},
                                {"id": "2", "parameters": {"name": disp.Behaviour.TYPES["dock"]}},
                                {"id": "3", "parameters": {"name": disp.Behaviour.TYPES["wait"]}},
                                {"id": "4", "parameters": {"name": disp.Behaviour.TYPES["undock"]}},
                                {"id": "5", "parameters": {"to": "1", "name": disp.Behaviour.TYPES["goto"]}}],
                 "current_behaviour_index": 0,
                 "status": disp.Task.STATUS_LIST["ASSIGN"],
                 "robot": "4",
                 "start_time": "2018-06-29 07:23:27",
                 "weight": 3}

    try:
        disp.Task(task_data)
    except disp.WrongTaskInputData as error:
        assert "Task param '{}' doesn't exist.".format(disp.Task.PARAM["ID"]) == str(error)
    else:
        assert False

    task_data = {"behaviours": [{"id": "1", "parameters": {"to": "5", "name": disp.Behaviour.TYPES["goto"]}},
                                {"id": "2", "parameters": {"name": disp.Behaviour.TYPES["dock"]}},
                                {"id": "3", "parameters": {"name": disp.Behaviour.TYPES["wait"]}},
                                {"id": "4", "parameters": {"name": disp.Behaviour.TYPES["undock"]}},
                                {"id": "5", "parameters": {"to": "1", "name": disp.Behaviour.TYPES["goto"]}}],
                 "current_behaviour_index": 0,
                 "status": disp.Task.STATUS_LIST["ASSIGN"],
                 "robot": "4",
                 "start_time": "2018-06-29 07:23:27",
                 "weight": 3}

    try:
        disp.Task(task_data)
    except disp.WrongTaskInputData as error:
        assert "Task param '{}' doesn't exist.".format(disp.Task.PARAM["ID"]) == str(error)
    else:
        assert False


@pytest.mark.skip("input_data_validation")
@pytest.mark.task_data
def test_throws_input_data_exception_wrong_task_id_type_int():
    task_data = {"id": 1,
                 "behaviours": [{"id": "1", "parameters": {"to": "5", "name": disp.Behaviour.TYPES["goto"]}},
                                {"id": "2", "parameters": {"name": disp.Behaviour.TYPES["dock"]}},
                                {"id": "3", "parameters": {"name": disp.Behaviour.TYPES["wait"]}},
                                {"id": "4", "parameters": {"name": disp.Behaviour.TYPES["undock"]}},
                                {"id": "5", "parameters": {"to": "1", "name": disp.Behaviour.TYPES["goto"]}}],
                 "current_behaviour_index": 0,
                 "status": disp.Task.STATUS_LIST["ASSIGN"],
                 "robot": "4",
                 "start_time": "2018-06-29 07:23:27",
                 "weight": 3}
    try:
        disp.Task(task_data)
    except disp.WrongTaskInputData as error:
        task_id = task_data[disp.Task.PARAM["ID"]]
        task_id_type = type(task_id)
        assert "Task '{}' should be str type but {} was given.".format(disp.Task.PARAM["ID"],
                                                                       task_id_type) == str(error)
    else:
        assert False


@pytest.mark.skip("input_data_validation")
@pytest.mark.task_data
def test_throws_input_data_exception_wrong_task_id_type_none():
    task_data = {"id": None,
                 "behaviours": [{"id": "1", "parameters": {"to": "5", "name": disp.Behaviour.TYPES["goto"]}},
                                {"id": "2", "parameters": {"name": disp.Behaviour.TYPES["dock"]}},
                                {"id": "3", "parameters": {"name": disp.Behaviour.TYPES["wait"]}},
                                {"id": "4", "parameters": {"name": disp.Behaviour.TYPES["undock"]}},
                                {"id": "5", "parameters": {"to": "1", "name": disp.Behaviour.TYPES["goto"]}}],
                 "current_behaviour_index": 0,
                 "status": disp.Task.STATUS_LIST["IN_PROGRESS"],
                 "robot": "4",
                 "start_time": "2018-06-29 07:23:27",
                 "weight": 3}
    try:
        disp.Task(task_data)
    except disp.WrongTaskInputData as error:
        task_id = task_data[disp.Task.PARAM["ID"]]
        task_id_type = type(task_id)
        assert "Task '{}' should be str type but {} was given.".format(disp.Task.PARAM["ID"],
                                                                       task_id_type) == str(error)
    else:
        assert False


@pytest.mark.skip("input_data_validation")
@pytest.mark.task_data
def test_throws_input_data_exception_wrong_task_id_type_dict():
    task_data = {"id": {},
                 "behaviours": [{"id": "1", "parameters": {"to": "5", "name": disp.Behaviour.TYPES["goto"]}},
                                {"id": "2", "parameters": {"name": disp.Behaviour.TYPES["dock"]}},
                                {"id": "3", "parameters": {"name": disp.Behaviour.TYPES["wait"]}},
                                {"id": "4", "parameters": {"name": disp.Behaviour.TYPES["undock"]}},
                                {"id": "5", "parameters": {"to": "1", "name": disp.Behaviour.TYPES["goto"]}}],
                 "current_behaviour_index": 0,
                 "status": disp.Task.STATUS_LIST["IN_PROGRESS"],
                 "robot": "4",
                 "start_time": "2018-06-29 07:23:27",
                 "weight": 3}
    try:
        disp.Task(task_data)
    except disp.WrongTaskInputData as error:
        task_id = task_data[disp.Task.PARAM["ID"]]
        task_id_type = type(task_id)
        assert "Task '{}' should be str type but {} was given.".format(disp.Task.PARAM["ID"],
                                                                       task_id_type) == str(error)
    else:
        assert False


@pytest.mark.skip("input_data_validation")
@pytest.mark.task_data
def test_throws_input_data_exception_wrong_task_id_type_list():
    task_data = {"id": [],
                 "behaviours": [{"id": "1", "parameters": {"to": "5", "name": disp.Behaviour.TYPES["goto"]}},
                                {"id": "2", "parameters": {"name": disp.Behaviour.TYPES["dock"]}},
                                {"id": "3", "parameters": {"name": disp.Behaviour.TYPES["wait"]}},
                                {"id": "4", "parameters": {"name": disp.Behaviour.TYPES["undock"]}},
                                {"id": "5", "parameters": {"to": "1", "name": disp.Behaviour.TYPES["goto"]}}],
                 "current_behaviour_index": 0,
                 "status": disp.Task.STATUS_LIST["IN_PROGRESS"],
                 "robot": "4",
                 "start_time": "2018-06-29 07:23:27",
                 "weight": 3}
    try:
        disp.Task(task_data)
    except disp.WrongTaskInputData as error:
        task_id = task_data[disp.Task.PARAM["ID"]]
        task_id_type = type(task_id)
        assert "Task '{}' should be str type but {} was given.".format(disp.Task.PARAM["ID"],
                                                                       task_id_type) == str(error)
    else:
        assert False


@pytest.mark.skip("input_data_validation")
@pytest.mark.task_data
def test_throws_input_data_exception_missing_robot_id_in_assigned_task():
    task_data = {"id": "1",
                 "behaviours": [{"id": "1", "parameters": {"to": "5", "name": disp.Behaviour.TYPES["goto"]}},
                                {"id": "2", "parameters": {"name": disp.Behaviour.TYPES["dock"]}},
                                {"id": "3", "parameters": {"name": disp.Behaviour.TYPES["wait"]}},
                                {"id": "4", "parameters": {"name": disp.Behaviour.TYPES["undock"]}},
                                {"id": "5", "parameters": {"to": "1", "name": disp.Behaviour.TYPES["goto"]}}],
                 "current_behaviour_index": 0,
                 "status": disp.Task.STATUS_LIST["ASSIGN"],
                 "robogeget": "4",
                 "start_time": "2018-06-29 07:23:27",
                 "weight": 3}

    try:
        disp.Task(task_data)
    except disp.WrongTaskInputData as error:
        task_id = task_data[disp.Task.PARAM["ID"]]
        assert "Task id: {}. Param '{}' doesn't exist.".format(task_id, disp.Task.PARAM["ROBOT_ID"]) == str(error)
    else:
        assert False

    task_data = {"id": "1",
                 "behaviours": [{"id": "1", "parameters": {"to": "5", "name": disp.Behaviour.TYPES["goto"]}},
                                {"id": "2", "parameters": {"name": disp.Behaviour.TYPES["dock"]}},
                                {"id": "3", "parameters": {"name": disp.Behaviour.TYPES["wait"]}},
                                {"id": "4", "parameters": {"name": disp.Behaviour.TYPES["undock"]}},
                                {"id": "5", "parameters": {"to": "1", "name": disp.Behaviour.TYPES["goto"]}}],
                 "current_behaviour_index": 0,
                 "status": disp.Task.STATUS_LIST["IN_PROGRESS"],
                 "start_time": "2018-06-29 07:23:27",
                 "weight": 3}

    try:
        disp.Task(task_data)
    except disp.WrongTaskInputData as error:
        task_id = task_data[disp.Task.PARAM["ID"]]
        assert "Task id: {}. Param '{}' doesn't exist.".format(task_id, disp.Task.PARAM["ROBOT_ID"]) == str(error)
    else:
        assert False


@pytest.mark.skip("input_data_validation")
@pytest.mark.task_data
def test_throws_input_data_exception_wrong_type_robot_id_int():
    task_data = {"id": "1",
                 "behaviours": [{"id": "1", "parameters": {"to": "5", "name": disp.Behaviour.TYPES["goto"]}},
                                {"id": "2", "parameters": {"name": disp.Behaviour.TYPES["dock"]}},
                                {"id": "3", "parameters": {"name": disp.Behaviour.TYPES["wait"]}},
                                {"id": "4", "parameters": {"name": disp.Behaviour.TYPES["undock"]}},
                                {"id": "5", "parameters": {"to": "1", "name": disp.Behaviour.TYPES["goto"]}}],
                 "current_behaviour_index": 0,
                 "status": disp.Task.STATUS_LIST["ASSIGN"],
                 "robot": 8,
                 "start_time": "2018-06-29 07:23:27",
                 "weight": 3}

    try:
        disp.Task(task_data)
    except disp.WrongTaskInputData as error:
        task_id = task_data[disp.Task.PARAM["ID"]]
        robot_id = task_data[disp.Task.PARAM["ROBOT_ID"]]
        robot_type = type(robot_id)
        assert "Task id: {}. Param '{}' should be str or None type but {} was given." \
               "".format(task_id, disp.Task.PARAM["ROBOT_ID"], robot_type) == str(error)
    else:
        assert False


@pytest.mark.skip("input_data_validation")
@pytest.mark.task_data
def test_throws_input_data_exception_wrong_type_robot_id_list():
    task_data = {"id": "1",
                 "behaviours": [{"id": "1", "parameters": {"to": "5", "name": disp.Behaviour.TYPES["goto"]}},
                                {"id": "2", "parameters": {"name": disp.Behaviour.TYPES["dock"]}},
                                {"id": "3", "parameters": {"name": disp.Behaviour.TYPES["wait"]}},
                                {"id": "4", "parameters": {"name": disp.Behaviour.TYPES["undock"]}},
                                {"id": "5", "parameters": {"to": "1", "name": disp.Behaviour.TYPES["goto"]}}],
                 "current_behaviour_index": 0,
                 "status": disp.Task.STATUS_LIST["ASSIGN"],
                 "robot": [],
                 "start_time": "2018-06-29 07:23:27",
                 "weight": 3}

    try:
        disp.Task(task_data)
    except disp.WrongTaskInputData as error:
        task_id = task_data[disp.Task.PARAM["ID"]]
        robot_id = task_data[disp.Task.PARAM["ROBOT_ID"]]
        robot_type = type(robot_id)
        assert "Task id: {}. Param '{}' should be str or None type but {} was given." \
               "".format(task_id, disp.Task.PARAM["ROBOT_ID"], robot_type) == str(error)
    else:
        assert False


@pytest.mark.skip("input_data_validation")
@pytest.mark.task_data
def test_throws_input_data_exception_wrong_value_robot_id():
    task_data = {"id": "1",
                 "behaviours": [{"id": "1", "parameters": {"to": "5", "name": disp.Behaviour.TYPES["goto"]}},
                                {"id": "2", "parameters": {"name": disp.Behaviour.TYPES["dock"]}},
                                {"id": "3", "parameters": {"name": disp.Behaviour.TYPES["wait"]}},
                                {"id": "4", "parameters": {"name": disp.Behaviour.TYPES["undock"]}},
                                {"id": "5", "parameters": {"to": "1", "name": disp.Behaviour.TYPES["goto"]}}],
                 "current_behaviour_index": 0,
                 "status": disp.Task.STATUS_LIST["ASSIGN"],
                 "robot": None,
                 "start_time": "2018-06-29 07:23:27",
                 "weight": 3}

    try:
        disp.Task(task_data)
    except disp.WrongTaskInputData as error:
        task_id = task_data[disp.Task.PARAM["ID"]]
        assert "Task id: {}. Param '{}' should be set when task was started. Status different than '{}'." \
               "".format(task_id, disp.Task.PARAM["ROBOT_ID"], disp.Task.STATUS_LIST["TO_DO"]) == str(error)
    else:
        assert False


@pytest.mark.task_data
def test_no_throws_input_data_exception_value_robot_id():
    task_data = {"id": "1",
                 "behaviours": [{"id": "1", "parameters": {"to": "5", "name": disp.Behaviour.TYPES["goto"]}},
                                {"id": "2", "parameters": {"name": disp.Behaviour.TYPES["dock"]}},
                                {"id": "3", "parameters": {"name": disp.Behaviour.TYPES["wait"]}},
                                {"id": "4", "parameters": {"name": disp.Behaviour.TYPES["undock"]}},
                                {"id": "5", "parameters": {"to": "1", "name": disp.Behaviour.TYPES["goto"]}}],
                 "current_behaviour_index": 0,
                 "status": disp.Task.STATUS_LIST["ASSIGN"],
                 "robot": "edd",
                 "start_time": "2018-06-29 07:23:27",
                 "weight": 3}

    try:
        disp.Task(task_data)
    except disp.WrongTaskInputData:
        assert False
    else:
        assert True

    task_data = {"id": "1",
                 "behaviours": [{"id": "1", "parameters": {"to": "5", "name": disp.Behaviour.TYPES["goto"]}},
                                {"id": "2", "parameters": {"name": disp.Behaviour.TYPES["dock"]}},
                                {"id": "3", "parameters": {"name": disp.Behaviour.TYPES["wait"]}},
                                {"id": "4", "parameters": {"name": disp.Behaviour.TYPES["undock"]}},
                                {"id": "5", "parameters": {"to": "1", "name": disp.Behaviour.TYPES["goto"]}}],
                 "current_behaviour_index": 0,
                 "status": disp.Task.STATUS_LIST["TO_DO"],
                 "robot": "edd",
                 "start_time": "2018-06-29 07:23:27",
                 "weight": 3}

    try:
        disp.Task(task_data)
    except disp.WrongTaskInputData:
        assert False
    else:
        assert True


@pytest.mark.skip("input_data_validation")
@pytest.mark.task_data
def test_throws_input_data_exception_missing_start_time():
    task_data = {"id": "1",
                 "behaviours": [{"id": "1", "parameters": {"to": "5", "name": disp.Behaviour.TYPES["goto"]}},
                                {"id": "2", "parameters": {"name": disp.Behaviour.TYPES["dock"]}},
                                {"id": "3", "parameters": {"name": disp.Behaviour.TYPES["wait"]}},
                                {"id": "4", "parameters": {"name": disp.Behaviour.TYPES["undock"]}},
                                {"id": "5", "parameters": {"to": "1", "name": disp.Behaviour.TYPES["goto"]}}],
                 "current_behaviour_index": 0,
                 "status": disp.Task.STATUS_LIST["ASSIGN"],
                 "robot": "4",
                 "weight": 3}

    try:
        disp.Task(task_data)
    except disp.WrongTaskInputData as error:
        task_id = task_data[disp.Task.PARAM["ID"]]
        assert "Task id: {}. Param '{}' doesn't exist.".format(task_id, disp.Task.PARAM["START_TIME"]) == str(error)
    else:
        assert False


@pytest.mark.skip("input_data_validation")
@pytest.mark.task_data
def test_throws_input_data_exception_wrong_type_start_time_list():
    task_data = {"id": "1",
                 "behaviours": [{"id": "1", "parameters": {"to": "5", "name": disp.Behaviour.TYPES["goto"]}},
                                {"id": "2", "parameters": {"name": disp.Behaviour.TYPES["dock"]}},
                                {"id": "3", "parameters": {"name": disp.Behaviour.TYPES["wait"]}},
                                {"id": "4", "parameters": {"name": disp.Behaviour.TYPES["undock"]}},
                                {"id": "5", "parameters": {"to": "1", "name": disp.Behaviour.TYPES["goto"]}}],
                 "current_behaviour_index": 0,
                 "status": disp.Task.STATUS_LIST["ASSIGN"],
                 "robot": "4",
                 "start_time": [],
                 "weight": 3}

    try:
        disp.Task(task_data)
    except disp.WrongTaskInputData as error:
        task_id = task_data[disp.Task.PARAM["ID"]]
        start_time_type = type(task_data[disp.Task.PARAM["START_TIME"]])
        assert "Task id: {}. Param '{}' should be str or None type but {} " \
               "was given.".format(task_id, disp.Task.PARAM["START_TIME"], start_time_type) == str(error)
    else:
        assert False


@pytest.mark.skip("input_data_validation")
@pytest.mark.task_data
def test_throws_input_data_exception_wrong_type_start_time_int():
    task_data = {"id": "1",
                 "behaviours": [{"id": "1", "parameters": {"to": "5", "name": disp.Behaviour.TYPES["goto"]}},
                                {"id": "2", "parameters": {"name": disp.Behaviour.TYPES["dock"]}},
                                {"id": "3", "parameters": {"name": disp.Behaviour.TYPES["wait"]}},
                                {"id": "4", "parameters": {"name": disp.Behaviour.TYPES["undock"]}},
                                {"id": "5", "parameters": {"to": "1", "name": disp.Behaviour.TYPES["goto"]}}],
                 "current_behaviour_index": 0,
                 "status": disp.Task.STATUS_LIST["ASSIGN"],
                 "robot": "4",
                 "start_time": 5252,
                 "weight": 3}

    try:
        disp.Task(task_data)
    except disp.WrongTaskInputData as error:
        task_id = task_data[disp.Task.PARAM["ID"]]
        start_time_type = type(task_data[disp.Task.PARAM["START_TIME"]])
        assert "Task id: {}. Param '{}' should be str or None type but {} " \
               "was given.".format(task_id, disp.Task.PARAM["START_TIME"], start_time_type) == str(error)
    else:
        assert False


@pytest.mark.skip("input_data_validation")
@pytest.mark.task_data
def test_throws_input_data_exception_wrong_format_start_time():
    task_data = {"id": "1",
                 "behaviours": [{"id": "1", "parameters": {"to": "5", "name": disp.Behaviour.TYPES["goto"]}},
                                {"id": "2", "parameters": {"name": disp.Behaviour.TYPES["dock"]}},
                                {"id": "3", "parameters": {"name": disp.Behaviour.TYPES["wait"]}},
                                {"id": "4", "parameters": {"name": disp.Behaviour.TYPES["undock"]}},
                                {"id": "5", "parameters": {"to": "1", "name": disp.Behaviour.TYPES["goto"]}}],
                 "current_behaviour_index": 0,
                 "status": disp.Task.STATUS_LIST["ASSIGN"],
                 "robot": "4",
                 "start_time": "2018-06-29 07:23:27.243860",
                 "weight": 3}

    try:
        disp.Task(task_data)
    except disp.WrongTaskInputData as error:
        task_id = task_data[disp.Task.PARAM["ID"]]
        assert "Task id: {}. Param '{}' wrong type. Required YYYY-mm-dd HH:MM:SS" \
               "".format(task_id, disp.Task.PARAM["START_TIME"]) == str(error)
    else:
        assert False

    # nieprawidlowy format danych
    task_data = {"id": "1",
                 "behaviours": [{"id": "1", "parameters": {"to": "5", "name": disp.Behaviour.TYPES["goto"]}},
                                {"id": "2", "parameters": {"name": disp.Behaviour.TYPES["dock"]}},
                                {"id": "3", "parameters": {"name": disp.Behaviour.TYPES["wait"]}},
                                {"id": "4", "parameters": {"name": disp.Behaviour.TYPES["undock"]}},
                                {"id": "5", "parameters": {"to": "1", "name": disp.Behaviour.TYPES["goto"]}}],
                 "current_behaviour_index": 0,
                 "status": disp.Task.STATUS_LIST["ASSIGN"],
                 "robot": "4",
                 "start_time": "201-06-29 07:23:27",
                 "weight": 3}

    try:
        disp.Task(task_data)
    except disp.WrongTaskInputData as error:
        task_id = task_data[disp.Task.PARAM["ID"]]
        assert "Task id: {}. Param '{}' wrong type. Required YYYY-mm-dd HH:MM:SS" \
               "".format(task_id, disp.Task.PARAM["START_TIME"]) == str(error)
    else:
        assert False

    # nieprawidlowy format danych
    task_data = {"id": "1",
                 "behaviours": [{"id": "1", "parameters": {"to": "5", "name": disp.Behaviour.TYPES["goto"]}},
                                {"id": "2", "parameters": {"name": disp.Behaviour.TYPES["dock"]}},
                                {"id": "3", "parameters": {"name": disp.Behaviour.TYPES["wait"]}},
                                {"id": "4", "parameters": {"name": disp.Behaviour.TYPES["undock"]}},
                                {"id": "5", "parameters": {"to": "1", "name": disp.Behaviour.TYPES["goto"]}}],
                 "current_behaviour_index": 0,
                 "status": disp.Task.STATUS_LIST["ASSIGN"],
                 "robot": "4",
                 "start_time": "2018-06-29 ",
                 "weight": 3}

    try:
        disp.Task(task_data)
    except disp.WrongTaskInputData as error:
        task_id = task_data[disp.Task.PARAM["ID"]]
        assert "Task id: {}. Param '{}' wrong type. Required YYYY-mm-dd HH:MM:SS" \
               "".format(task_id, disp.Task.PARAM["START_TIME"]) == str(error)
    else:
        assert False

    # nieprawidlowy format danych
    task_data = {"id": "1",
                 "behaviours": [{"id": "1", "parameters": {"to": "5", "name": disp.Behaviour.TYPES["goto"]}},
                                {"id": "2", "parameters": {"name": disp.Behaviour.TYPES["dock"]}},
                                {"id": "3", "parameters": {"name": disp.Behaviour.TYPES["wait"]}},
                                {"id": "4", "parameters": {"name": disp.Behaviour.TYPES["undock"]}},
                                {"id": "5", "parameters": {"to": "1", "name": disp.Behaviour.TYPES["goto"]}}],
                 "current_behaviour_index": 0,
                 "status": disp.Task.STATUS_LIST["ASSIGN"],
                 "robot": "4",
                 "start_time": "2018-0f6-29 07:23:27",
                 "weight": 3}

    try:
        disp.Task(task_data)
    except disp.WrongTaskInputData as error:
        task_id = task_data[disp.Task.PARAM["ID"]]
        assert "Task id: {}. Param '{}' wrong type. Required YYYY-mm-dd HH:MM:SS" \
               "".format(task_id, disp.Task.PARAM["START_TIME"]) == str(error)
    else:
        assert False

    # nieprawidlowy format danych
    task_data = {"id": "1",
                 "behaviours": [{"id": "1", "parameters": {"to": "5", "name": disp.Behaviour.TYPES["goto"]}},
                                {"id": "2", "parameters": {"name": disp.Behaviour.TYPES["dock"]}},
                                {"id": "3", "parameters": {"name": disp.Behaviour.TYPES["wait"]}},
                                {"id": "4", "parameters": {"name": disp.Behaviour.TYPES["undock"]}},
                                {"id": "5", "parameters": {"to": "1", "name": disp.Behaviour.TYPES["goto"]}}],
                 "current_behaviour_index": 0,
                 "status": disp.Task.STATUS_LIST["ASSIGN"],
                 "robot": "4",
                 "start_time": "2018-06-29 07:23:287.243860",
                 "weight": 3}

    try:
        disp.Task(task_data)
    except disp.WrongTaskInputData as error:
        task_id = task_data[disp.Task.PARAM["ID"]]
        assert "Task id: {}. Param '{}' wrong type. Required YYYY-mm-dd HH:MM:SS" \
               "".format(task_id, disp.Task.PARAM["START_TIME"]) == str(error)
    else:
        assert False


@pytest.mark.skip("input_data_validation")
@pytest.mark.task_data
def test_throws_input_data_exception_missing_current_behaviour_index():
    task_data = {"id": "1",
                 "behaviours": [{"id": "1", "parameters": {"to": "5", "name": disp.Behaviour.TYPES["goto"]}},
                                {"id": "2", "parameters": {"name": disp.Behaviour.TYPES["dock"]}},
                                {"id": "3", "parameters": {"name": disp.Behaviour.TYPES["wait"]}},
                                {"id": "4", "parameters": {"name": disp.Behaviour.TYPES["undock"]}},
                                {"id": "5", "parameters": {"to": "1", "name": disp.Behaviour.TYPES["goto"]}}],
                 "status": disp.Task.STATUS_LIST["ASSIGN"],
                 "robot": "4",
                 "start_time": "2018-06-29 07:23:27",
                 "weight": 3}

    try:
        disp.Task(task_data)
    except disp.WrongTaskInputData as error:
        task_id = task_data[disp.Task.PARAM["ID"]]
        assert "Task id: {}. Param '{}' doesn't exist.".format(task_id, disp.Task.PARAM["CURRENT_BEH_ID"]) == str(error)
    else:
        assert False


@pytest.mark.skip("input_data_validation")
@pytest.mark.task_data
def test_throws_input_data_exception_wrong_current_behaviour_index_type_float():
    task_data = {"id": "1",
                 "behaviours": [{"id": "1", "parameters": {"to": "5", "name": disp.Behaviour.TYPES["goto"]}},
                                {"id": "2", "parameters": {"name": disp.Behaviour.TYPES["dock"]}},
                                {"id": "3", "parameters": {"name": disp.Behaviour.TYPES["wait"]}},
                                {"id": "4", "parameters": {"name": disp.Behaviour.TYPES["undock"]}},
                                {"id": "5", "parameters": {"to": "1", "name": disp.Behaviour.TYPES["goto"]}}],
                 "current_behaviour_index": 0.0,
                 "status": disp.Task.STATUS_LIST["ASSIGN"],
                 "robot": "4",
                 "start_time": "2018-06-29 07:23:27",
                 "weight": 3}

    try:
        disp.Task(task_data)
    except disp.WrongTaskInputData as error:
        task_id = task_data[disp.Task.PARAM["ID"]]
        task_status_type = type(task_data[disp.Task.PARAM["CURRENT_BEH_ID"]])
        assert "Task id: {}. Param '{}' should be int type but {} " \
               "was given.".format(task_id, disp.Task.PARAM["CURRENT_BEH_ID"], task_status_type) == str(error)
    else:
        assert False


@pytest.mark.skip("input_data_validation")
@pytest.mark.task_data
def test_throws_input_data_exception_wrong_current_behaviour_index_type_string():
    task_data = {"id": "1",
                 "behaviours": [{"id": "1", "parameters": {"to": "5", "name": disp.Behaviour.TYPES["goto"]}},
                                {"id": "2", "parameters": {"name": disp.Behaviour.TYPES["dock"]}},
                                {"id": "3", "parameters": {"name": disp.Behaviour.TYPES["wait"]}},
                                {"id": "4", "parameters": {"name": disp.Behaviour.TYPES["undock"]}},
                                {"id": "5", "parameters": {"to": "1", "name": disp.Behaviour.TYPES["goto"]}}],
                 "current_behaviour_index": "0.0",
                 "status": disp.Task.STATUS_LIST["ASSIGN"],
                 "robot": "4",
                 "start_time": "2018-06-29 07:23:27",
                 "weight": 3}

    try:
        disp.Task(task_data)
    except disp.WrongTaskInputData as error:
        task_id = task_data[disp.Task.PARAM["ID"]]
        task_status_type = type(task_data[disp.Task.PARAM["STATUS"]])
        assert "Task id: {}. Param '{}' should be int type but {} " \
               "was given.".format(task_id, disp.Task.PARAM["CURRENT_BEH_ID"], task_status_type) == str(error)
    else:
        assert False


@pytest.mark.skip("input_data_validation")
@pytest.mark.task_data
def test_throws_input_data_exception_wrong_current_behaviour_index_type_none():
    task_data = {"id": "1",
                 "behaviours": [{"id": "1", "parameters": {"to": "5", "name": disp.Behaviour.TYPES["goto"]}},
                                {"id": "2", "parameters": {"name": disp.Behaviour.TYPES["dock"]}},
                                {"id": "3", "parameters": {"name": disp.Behaviour.TYPES["wait"]}},
                                {"id": "4", "parameters": {"name": disp.Behaviour.TYPES["undock"]}},
                                {"id": "5", "parameters": {"to": "1", "name": disp.Behaviour.TYPES["goto"]}}],
                 "current_behaviour_index": None,
                 "status": disp.Task.STATUS_LIST["ASSIGN"],
                 "robot": "4",
                 "start_time": "2018-06-29 07:23:27",
                 "weight": 3}

    try:
        disp.Task(task_data)
    except disp.WrongTaskInputData as error:
        task_id = task_data[disp.Task.PARAM["ID"]]
        task_status_type = type(task_data[disp.Task.PARAM["CURRENT_BEH_ID"]])
        assert "Task id: {}. Param '{}' should be int type but {} " \
               "was given.".format(task_id, disp.Task.PARAM["CURRENT_BEH_ID"], task_status_type) == str(error)
    else:
        assert False


@pytest.mark.skip("input_data_validation")
@pytest.mark.task_data
def test_throws_input_data_exception_wrong_current_behaviour_index_range():
    task_data = {"id": "1",
                 "behaviours": [{"id": "1", "parameters": {"to": "5", "name": disp.Behaviour.TYPES["goto"]}},
                                {"id": "2", "parameters": {"name": disp.Behaviour.TYPES["dock"]}},
                                {"id": "3", "parameters": {"name": disp.Behaviour.TYPES["wait"]}},
                                {"id": "4", "parameters": {"name": disp.Behaviour.TYPES["undock"]}},
                                {"id": "5", "parameters": {"to": "1", "name": disp.Behaviour.TYPES["goto"]}}],
                 "current_behaviour_index": -2,
                 "status": disp.Task.STATUS_LIST["ASSIGN"],
                 "robot": "4",
                 "start_time": "2018-06-29 07:23:27",
                 "weight": 3}

    try:
        disp.Task(task_data)
    except disp.WrongTaskInputData as error:
        task_id = task_data[disp.Task.PARAM["ID"]]
        beh_range = len(task_data[disp.Task.PARAM["BEHAVIOURS"]]) - 1
        assert "Task id: {}. Param '{}' should be int in range [-1,{}] but was '{}'"\
               .format(task_id, disp.Task.PARAM["CURRENT_BEH_ID"], beh_range,
                       task_data[disp.Task.PARAM["CURRENT_BEH_ID"]]) == str(error)
    else:
        assert False

    task_data = {"id": "1",
                 "behaviours": [{"id": "1", "parameters": {"to": 5, "name": disp.Behaviour.TYPES["goto"]}},
                                {"id": "2", "parameters": {"name": disp.Behaviour.TYPES["dock"]}},
                                {"id": "3", "parameters": {"name": disp.Behaviour.TYPES["wait"]}},
                                {"id": "4", "parameters": {"name": disp.Behaviour.TYPES["undock"]}},
                                {"id": "5", "parameters": {"to": 1, "name": disp.Behaviour.TYPES["goto"]}}],
                 "current_behaviour_index": 5,
                 "status": disp.Task.STATUS_LIST["ASSIGN"],
                 "robot": "4",
                 "start_time": "2018-06-29 07:23:27",
                 "weight": 3}

    try:
        disp.Task(task_data)
    except disp.WrongTaskInputData as error:
        task_id = task_data[disp.Task.PARAM["ID"]]
        beh_range = len(task_data[disp.Task.PARAM["BEHAVIOURS"]]) - 1
        assert "Task id: {}. Param '{}' should be int in range [-1,{}] but was '{}'"\
               .format(task_id, disp.Task.PARAM["CURRENT_BEH_ID"], beh_range,
                       task_data[disp.Task.PARAM["CURRENT_BEH_ID"]]) == str(error)
    else:
        assert False


@pytest.mark.skip("input_data_validation")
@pytest.mark.task_data
def test_throws_input_data_exception_missing_status():
    task_data = {"id": "1",
                 "behaviours": [{"id": "1", "parameters": {"to": "5", "name": disp.Behaviour.TYPES["goto"]}},
                                {"id": "2", "parameters": {"name": disp.Behaviour.TYPES["dock"]}},
                                {"id": "3", "parameters": {"name": disp.Behaviour.TYPES["wait"]}},
                                {"id": "4", "parameters": {"name": disp.Behaviour.TYPES["undock"]}},
                                {"id": "5", "parameters": {"to": "1", "name": disp.Behaviour.TYPES["goto"]}}],
                 "current_behaviour_index": 0,
                 "robot": "4",
                 "start_time": "2018-06-29 07:23:27",
                 "weight": 3}

    try:
        disp.Task(task_data)
    except disp.WrongTaskInputData as error:
        task_id = task_data[disp.Task.PARAM["ID"]]
        assert "Task id: {}. Param '{}' doesn't exist.".format(task_id, disp.Task.PARAM["STATUS"]) == str(error)
    else:
        assert False


@pytest.mark.skip("input_data_validation")
@pytest.mark.task_data
def test_throws_input_data_exception_wrong_status_type_int():
    task_data = {"id": "1",
                 "behaviours": [{"id": "1", "parameters": {"to": "5", "name": disp.Behaviour.TYPES["goto"]}},
                                {"id": "2", "parameters": {"name": disp.Behaviour.TYPES["dock"]}},
                                {"id": "3", "parameters": {"name": disp.Behaviour.TYPES["wait"]}},
                                {"id": "4", "parameters": {"name": disp.Behaviour.TYPES["undock"]}},
                                {"id": "5", "parameters": {"to": "1", "name": disp.Behaviour.TYPES["goto"]}}],
                 "current_behaviour_index": 0,
                 "status": 6,
                 "robot": "4",
                 "start_time": "2018-06-29 07:23:27",
                 "weight": 3}

    try:
        disp.Task(task_data)
    except disp.WrongTaskInputData as error:
        task_id = task_data[disp.Task.PARAM["ID"]]
        task_status_type = type(task_data[disp.Task.PARAM["STATUS"]])
        assert "Task id: {}. Param '{}' should be str or None type but {} " \
               "was given.".format(task_id, disp.Task.PARAM["STATUS"], task_status_type) == str(error)
    else:
        assert False


@pytest.mark.skip("input_data_validation")
@pytest.mark.task_data
def test_throws_input_data_exception_wrong_status_type_list():
    task_data = {"id": "1",
                 "behaviours": [{"id": "1", "parameters": {"to": "5", "name": disp.Behaviour.TYPES["goto"]}},
                                {"id": "2", "parameters": {"name": disp.Behaviour.TYPES["dock"]}},
                                {"id": "3", "parameters": {"name": disp.Behaviour.TYPES["wait"]}},
                                {"id": "4", "parameters": {"name": disp.Behaviour.TYPES["undock"]}},
                                {"id": "5", "parameters": {"to": "1", "name": disp.Behaviour.TYPES["goto"]}}],
                 "current_behaviour_index": 0,
                 "status": [],
                 "robot": "4",
                 "start_time": "2018-06-29 07:23:27",
                 "weight": 3}

    try:
        disp.Task(task_data)
    except disp.WrongTaskInputData as error:
        task_id = task_data[disp.Task.PARAM["ID"]]
        task_status_type = type(task_data[disp.Task.PARAM["STATUS"]])
        assert "Task id: {}. Param '{}' should be str or None type but {} " \
               "was given.".format(task_id, disp.Task.PARAM["STATUS"], task_status_type) == str(error)
    else:
        assert False


@pytest.mark.skip("input_data_validation")
@pytest.mark.task_data
def test_throws_input_data_exception_wrong_status_type_dict():
    task_data = {"id": "1",
                 "behaviours": [{"id": "1", "parameters": {"to": "5", "name": disp.Behaviour.TYPES["goto"]}},
                                {"id": "2", "parameters": {"name": disp.Behaviour.TYPES["dock"]}},
                                {"id": "3", "parameters": {"name": disp.Behaviour.TYPES["wait"]}},
                                {"id": "4", "parameters": {"name": disp.Behaviour.TYPES["undock"]}},
                                {"id": "5", "parameters": {"to": "1", "name": disp.Behaviour.TYPES["goto"]}}],
                 "current_behaviour_index": 0,
                 "status": {},
                 "robot": "4",
                 "start_time": "2018-06-29 07:23:27",
                 "weight": 3}

    try:
        disp.Task(task_data)
    except disp.WrongTaskInputData as error:
        task_id = task_data[disp.Task.PARAM["ID"]]
        task_status_type = type(task_data[disp.Task.PARAM["STATUS"]])
        assert "Task id: {}. Param '{}' should be str or None type but {} " \
               "was given.".format(task_id, disp.Task.PARAM["STATUS"], task_status_type) == str(error)
    else:
        assert False


@pytest.mark.skip("input_data_validation")
@pytest.mark.task_data
def test_throws_input_data_exception_wrong_status_value():
    task_data = {"id": "1",
                 "behaviours": [{"id": "1", "parameters": {"to": "5", "name": disp.Behaviour.TYPES["goto"]}},
                                {"id": "2", "parameters": {"name": disp.Behaviour.TYPES["dock"]}},
                                {"id": "3", "parameters": {"name": disp.Behaviour.TYPES["wait"]}},
                                {"id": "4", "parameters": {"name": disp.Behaviour.TYPES["undock"]}},
                                {"id": "5", "parameters": {"to": "1", "name": disp.Behaviour.TYPES["goto"]}}],
                 "current_behaviour_index": 0,
                 "status": "jfoifoeij",
                 "robot": "4",
                 "start_time": "2018-06-29 07:23:27",
                 "weight": 3}

    try:
        disp.Task(task_data)
    except disp.WrongTaskInputData as error:
        task_id = task_data[disp.Task.PARAM["ID"]]
        task_status = task_data[disp.Task.PARAM["STATUS"]]
        assert "Task id: {}. '{}' doesn't exist. {} was given.".format(task_id,
                                                                       disp.Task.PARAM["STATUS"],
                                                                       task_status) == str(error)
    else:
        assert False


@pytest.mark.skip("input_data_validation")
@pytest.mark.task_data
def test_throws_input_data_exception_missing_weight():
    task_data = {"id": "1",
                 "behaviours": [{"id": "1", "parameters": {"to": "5", "name": disp.Behaviour.TYPES["goto"]}},
                                {"id": "2", "parameters": {"name": disp.Behaviour.TYPES["dock"]}},
                                {"id": "3", "parameters": {"name": disp.Behaviour.TYPES["wait"]}},
                                {"id": "4", "parameters": {"name": disp.Behaviour.TYPES["undock"]}},
                                {"id": "5", "parameters": {"to": "1", "name": disp.Behaviour.TYPES["goto"]}}],
                 "current_behaviour_index": 0,
                 "status": disp.Task.STATUS_LIST["ASSIGN"],
                 "robot": "4",
                 "start_time": "2018-06-29 07:23:27"}

    try:
        disp.Task(task_data)
    except disp.WrongTaskInputData as error:
        task_id = task_data[disp.Task.PARAM["ID"]]
        assert "Task id: {}. Param '{}' doesn't exist.".format(task_id, disp.Task.PARAM["WEIGHT"]) == str(error)
    else:
        assert False


@pytest.mark.skip("input_data_validation")
@pytest.mark.task_data
def test_throws_input_data_exception_wrong_weight_type_string():
    task_data = {"id": "1",
                 "behaviours": [{"id": "1", "parameters": {"to": "5", "name": disp.Behaviour.TYPES["goto"]}},
                                {"id": "2", "parameters": {"name": disp.Behaviour.TYPES["dock"]}},
                                {"id": "3", "parameters": {"name": disp.Behaviour.TYPES["wait"]}},
                                {"id": "4", "parameters": {"name": disp.Behaviour.TYPES["undock"]}},
                                {"id": "5", "parameters": {"to": "1", "name": disp.Behaviour.TYPES["goto"]}}],
                 "current_behaviour_index": 0,
                 "status": disp.Task.STATUS_LIST["ASSIGN"],
                 "robot": "4",
                 "start_time": "2018-06-29 07:23:27",
                 "weight": "3"}
    try:
        disp.Task(task_data)
    except disp.WrongTaskInputData as error:
        task_id = task_data[disp.Task.PARAM["ID"]]
        task_weight_type = type(task_data[disp.Task.PARAM["WEIGHT"]])
        assert "Task id: {}. Param '{}' should be int, float, None type but {} was given." \
               "".format(task_id, disp.Task.PARAM["WEIGHT"], task_weight_type) == str(error)
    else:
        assert False


@pytest.mark.skip("input_data_validation")
@pytest.mark.task_data
def test_throws_input_data_exception_wrong_weight_type_list():
    task_data = {"id": "1",
                 "behaviours": [{"id": "1", "parameters": {"to": "5", "name": disp.Behaviour.TYPES["goto"]}},
                                {"id": "2", "parameters": {"name": disp.Behaviour.TYPES["dock"]}},
                                {"id": "3", "parameters": {"name": disp.Behaviour.TYPES["wait"]}},
                                {"id": "4", "parameters": {"name": disp.Behaviour.TYPES["undock"]}},
                                {"id": "5", "parameters": {"to": "1", "name": disp.Behaviour.TYPES["goto"]}}],
                 "current_behaviour_index": 0,
                 "status": disp.Task.STATUS_LIST["ASSIGN"],
                 "robot": "4",
                 "start_time": "2018-06-29 07:23:27",
                 "weight": []}
    try:
        disp.Task(task_data)
    except disp.WrongTaskInputData as error:
        task_id = task_data[disp.Task.PARAM["ID"]]
        task_weight_type = type(task_data[disp.Task.PARAM["WEIGHT"]])
        assert "Task id: {}. Param '{}' should be int, float, None type but {} was given." \
               "".format(task_id, disp.Task.PARAM["WEIGHT"], task_weight_type) == str(error)
    else:
        assert False


@pytest.mark.skip("input_data_validation")
@pytest.mark.task_data
def test_throws_input_data_exception_wrong_weight_type_dict():
    # nieprawidlowy format danych
    task_data = {"id": "1",
                 "behaviours": [{"id": "1", "parameters": {"to": "5", "name": disp.Behaviour.TYPES["goto"]}},
                                {"id": "2", "parameters": {"name": disp.Behaviour.TYPES["dock"]}},
                                {"id": "3", "parameters": {"name": disp.Behaviour.TYPES["wait"]}},
                                {"id": "4", "parameters": {"name": disp.Behaviour.TYPES["undock"]}},
                                {"id": "5", "parameters": {"to": "1", "name": disp.Behaviour.TYPES["goto"]}}],
                 "current_behaviour_index": 0,
                 "status": disp.Task.STATUS_LIST["ASSIGN"],
                 "robot": "4",
                 "start_time": "2018-06-29 07:23:27",
                 "weight": {}}

    try:
        disp.Task(task_data)
    except disp.WrongTaskInputData as error:
        task_id = task_data[disp.Task.PARAM["ID"]]
        task_weight_type = type(task_data[disp.Task.PARAM["WEIGHT"]])
        assert "Task id: {}. Param '{}' should be int, float, None type but {} was given." \
               "".format(task_id, disp.Task.PARAM["WEIGHT"], task_weight_type) == str(error)
    else:
        assert False


@pytest.mark.skip("input_data_validation")
@pytest.mark.task_data
def test_throws_input_data_exception_missing_behaviours():
    task_data = {"id": "1",
                 "current_behaviour_index": 0,
                 "status": disp.Task.STATUS_LIST["ASSIGN"],
                 "robot": "4",
                 "start_time": "2018-06-29 07:23:27",
                 "weight": 3}

    try:
        disp.Task(task_data)
    except disp.WrongTaskInputData as error:
        task_id = task_data[disp.Task.PARAM["ID"]]
        assert "Task id: {}. Param '{}' doesn't exist.".format(task_id, disp.Task.PARAM["BEHAVIOURS"]) == str(error)
    else:
        assert False


@pytest.mark.skip("input_data_validation")
@pytest.mark.task_data
def test_throws_input_data_exception_wrong_behaviour_type_int():
    task_data = {"id": "1",
                 "behaviours": 6,
                 "current_behaviour_index": 0,
                 "status": disp.Task.STATUS_LIST["ASSIGN"],
                 "robot": "4",
                 "start_time": "2018-06-29 07:23:27",
                 "weight": 3}

    try:
        disp.Task(task_data)
    except disp.WrongTaskInputData as error:
        task_id = task_data[disp.Task.PARAM["ID"]]
        assert "Task id: {}. Param '{}' should be list type but {} was given."\
               .format(task_id, disp.Task.PARAM["BEHAVIOURS"], type(task_data[disp.Task.PARAM["BEHAVIOURS"]])) \
               == str(error)
    else:
        assert False


@pytest.mark.skip("input_data_validation")
@pytest.mark.task_data
def test_throws_input_data_exception_wrong_behaviour_type_string():
    task_data = {"id": "1",
                 "behaviours": "dioijfewa",
                 "current_behaviour_index": 0,
                 "status": disp.Task.STATUS_LIST["ASSIGN"],
                 "robot": "4",
                 "start_time": "2018-06-29 07:23:27",
                 "weight": 3}

    try:
        disp.Task(task_data)
    except disp.WrongTaskInputData as error:
        task_id = task_data[disp.Task.PARAM["ID"]]
        assert "Task id: {}. Param '{}' should be list type but {} was given."\
               .format(task_id, disp.Task.PARAM["BEHAVIOURS"], type(task_data[disp.Task.PARAM["BEHAVIOURS"]])) \
               == str(error)
    else:
        assert False


@pytest.mark.task_data
def test_throws_input_data_exception_behaviour_error():
    task_data = {"id": "1",
                 "behaviours": [{"id": 1, "parameters": {"to": 5, "name": disp.Behaviour.TYPES["goto"]}},
                                {"id": 2, "parameters": {"name": disp.Behaviour.TYPES["dock"]}},
                                {"id": 3, "parameters": {"name": disp.Behaviour.TYPES["wait"]}},
                                {"id": 4, "parameters": {"name": disp.Behaviour.TYPES["undock"]}},
                                {"id": 5, "parameters": {"to": 1, "name": disp.Behaviour.TYPES["goto"]}}],
                 "current_behaviour_index": 0,
                 "status": disp.Task.STATUS_LIST["ASSIGN"],
                 "robot": "4",
                 "start_time": "2018-06-29 07:23:27",
                 "weight": 3}
    beh_error = ""
    try:
        [disp.Behaviour(raw_behaviour) for raw_behaviour in task_data[disp.Task.PARAM["BEHAVIOURS"]]]
    except disp.WrongBehaviourInputData as error_beh:
        beh_error = str(error_beh)

    try:
        disp.Task(task_data)
    except disp.WrongTaskInputData as error:
        task_id = task_data[disp.Task.PARAM["ID"]]
        assert "Task id: {}. Behaviour error. {}".format(task_id, beh_error) == str(error)
    else:
        assert False


# ------------------------------ Task methods ------------------------------ #
@pytest.mark.task_methods
def test_task_returned_current_behaviour():
    task_data = {"id": "1",
                 "behaviours": [{"id": "1", "parameters": {"to": "5", "name": disp.Behaviour.TYPES["goto"]}},
                                {"id": "2", "parameters": {"name": disp.Behaviour.TYPES["dock"]}},
                                {"id": "3", "parameters": {"name": disp.Behaviour.TYPES["wait"]}},
                                {"id": "4", "parameters": {"name": disp.Behaviour.TYPES["undock"]}},
                                {"id": "5", "parameters": {"to": "1", "name": disp.Behaviour.TYPES["goto"]}}],
                 "current_behaviour_index": 0,
                 "status": disp.Task.STATUS_LIST["ASSIGN"],
                 "robot": "4",
                 "start_time": "2018-06-29 07:23:27",
                 "weight": 3}
    task = disp.Task(task_data)
    behaviour = disp.Behaviour(task_data[disp.Task.PARAM["BEHAVIOURS"]][0])
    assert task.get_current_behaviour().get_info() == behaviour.get_info()

    task_data = {"id": "1",
                 "behaviours": [{"id": "1", "parameters": {"to": "5", "name": disp.Behaviour.TYPES["goto"]}},
                                {"id": "2", "parameters": {"name": disp.Behaviour.TYPES["dock"]}},
                                {"id": "3", "parameters": {"name": disp.Behaviour.TYPES["wait"]}},
                                {"id": "4", "parameters": {"name": disp.Behaviour.TYPES["undock"]}},
                                {"id": "5", "parameters": {"to": "1", "name": disp.Behaviour.TYPES["goto"]}}],
                 "current_behaviour_index": 4,
                 "status": disp.Task.STATUS_LIST["ASSIGN"],
                 "robot": "4",
                 "start_time": "2018-06-29 07:23:27",
                 "weight": 3}
    task = disp.Task(task_data)
    behaviour = disp.Behaviour(task_data[disp.Task.PARAM["BEHAVIOURS"]][4])
    assert task.get_current_behaviour().get_info() == behaviour.get_info()


@pytest.mark.task_methods
def test_task_check_if_task_started():
    task_data = {"id": "1",
                 "behaviours": [{"id": "1", "parameters": {"to": "5", "name": disp.Behaviour.TYPES["goto"]}},
                                {"id": "2", "parameters": {"name": disp.Behaviour.TYPES["dock"]}},
                                {"id": "3", "parameters": {"name": disp.Behaviour.TYPES["wait"]}},
                                {"id": "4", "parameters": {"name": disp.Behaviour.TYPES["undock"]}},
                                {"id": "5", "parameters": {"to": "1", "name": disp.Behaviour.TYPES["goto"]}}],
                 "current_behaviour_index": 0,
                 "status": disp.Task.STATUS_LIST["ASSIGN"],
                 "robot": "4",
                 "start_time": "2018-06-29 07:23:27",
                 "weight": 3}
    task = disp.Task(task_data)
    assert task.check_if_task_started()

    task_data = {"id": "1",
                 "behaviours": [{"id": "1", "parameters": {"to": "5", "name": disp.Behaviour.TYPES["goto"]}},
                                {"id": "2", "parameters": {"name": disp.Behaviour.TYPES["dock"]}},
                                {"id": "3", "parameters": {"name": disp.Behaviour.TYPES["wait"]}},
                                {"id": "4", "parameters": {"name": disp.Behaviour.TYPES["undock"]}},
                                {"id": "5", "parameters": {"to": "1", "name": disp.Behaviour.TYPES["goto"]}}],
                 "current_behaviour_index": 0,
                 "status": disp.Task.STATUS_LIST["IN_PROGRESS"],
                 "robot": "4",
                 "start_time": "2018-06-29 07:23:27",
                 "weight": 3}
    task = disp.Task(task_data)
    assert task.check_if_task_started()


@pytest.mark.task_methods
def test_task_check_if_task_not_started():
    task_data = {"id": "1",
                 "behaviours": [{"id": "1", "parameters": {"to": "5", "name": disp.Behaviour.TYPES["goto"]}},
                                {"id": "2", "parameters": {"name": disp.Behaviour.TYPES["dock"]}},
                                {"id": "3", "parameters": {"name": disp.Behaviour.TYPES["wait"]}},
                                {"id": "4", "parameters": {"name": disp.Behaviour.TYPES["undock"]}},
                                {"id": "5", "parameters": {"to": "1", "name": disp.Behaviour.TYPES["goto"]}}],
                 "current_behaviour_index": 0,
                 "status": disp.Task.STATUS_LIST["TO_DO"],
                 "robot": "4",
                 "start_time": "2018-06-29 07:23:27",
                 "weight": 3}
    task = disp.Task(task_data)
    assert not task.check_if_task_started()

    task_data = {"id": "1",
                 "behaviours": [{"id": "1", "parameters": {"to": "5", "name": disp.Behaviour.TYPES["goto"]}},
                                {"id": "2", "parameters": {"name": disp.Behaviour.TYPES["dock"]}},
                                {"id": "3", "parameters": {"name": disp.Behaviour.TYPES["wait"]}},
                                {"id": "4", "parameters": {"name": disp.Behaviour.TYPES["undock"]}},
                                {"id": "5", "parameters": {"to": "1", "name": disp.Behaviour.TYPES["goto"]}}],
                 "current_behaviour_index": 0,
                 "status": disp.Task.STATUS_LIST["TO_DO"],
                 "robot": None,
                 "start_time": "2018-06-29 07:23:27",
                 "weight": 3}
    task = disp.Task(task_data)
    assert not task.check_if_task_started()

    task_data = {"id": "1",
                 "behaviours": [{"id": "1", "parameters": {"to": "5", "name": disp.Behaviour.TYPES["goto"]}},
                                {"id": "2", "parameters": {"name": disp.Behaviour.TYPES["dock"]}},
                                {"id": "3", "parameters": {"name": disp.Behaviour.TYPES["wait"]}},
                                {"id": "4", "parameters": {"name": disp.Behaviour.TYPES["undock"]}},
                                {"id": "5", "parameters": {"to": "1", "name": disp.Behaviour.TYPES["goto"]}}],
                 "current_behaviour_index": -1,
                 "status": disp.Task.STATUS_LIST["TO_DO"],
                 "robot": None,
                 "start_time": "2018-06-29 07:23:27",
                 "weight": 3}
    task = disp.Task(task_data)
    assert not task.check_if_task_started()


@pytest.mark.task_methods
def test_task_check_get_poi_goal():
    task_data = {"id": "1",
                 "behaviours": [{"id": "1", "parameters": {"to": "5", "name": disp.Behaviour.TYPES["goto"]}},
                                {"id": "2", "parameters": {"name": disp.Behaviour.TYPES["dock"]}},
                                {"id": "3", "parameters": {"name": disp.Behaviour.TYPES["wait"]}},
                                {"id": "4", "parameters": {"name": disp.Behaviour.TYPES["undock"]}},
                                {"id": "5", "parameters": {"to": "1", "name": disp.Behaviour.TYPES["goto"]}}],
                 "current_behaviour_index": 0,
                 "status": disp.Task.STATUS_LIST["TO_DO"],
                 "robot": "4",
                 "start_time": "2018-06-29 07:23:27",
                 "weight": 3}
    task = disp.Task(task_data)
    assert task.get_poi_goal() == "5"

    task_data = {"id": "1",
                 "behaviours": [{"id": "1", "parameters": {"to": "5", "name": disp.Behaviour.TYPES["goto"]}},
                                {"id": "2", "parameters": {"name": disp.Behaviour.TYPES["dock"]}},
                                {"id": "3", "parameters": {"name": disp.Behaviour.TYPES["wait"]}},
                                {"id": "4", "parameters": {"name": disp.Behaviour.TYPES["undock"]}},
                                {"id": "5", "parameters": {"to": "1", "name": disp.Behaviour.TYPES["goto"]}}],
                 "current_behaviour_index": 3,
                 "status": disp.Task.STATUS_LIST["IN_PROGRESS"],
                 "robot": "4",
                 "start_time": "2018-06-29 07:23:27",
                 "weight": 3}
    task = disp.Task(task_data)
    assert task.get_poi_goal() == "5"

    task_data = {"id": "1",
                 "behaviours": [{"id": "1", "parameters": {"to": "5", "name": disp.Behaviour.TYPES["goto"]}},
                                {"id": "2", "parameters": {"name": disp.Behaviour.TYPES["dock"]}},
                                {"id": "3", "parameters": {"name": disp.Behaviour.TYPES["wait"]}},
                                {"id": "4", "parameters": {"name": disp.Behaviour.TYPES["undock"]}},
                                {"id": "5", "parameters": {"to": "1", "name": disp.Behaviour.TYPES["goto"]}}],
                 "current_behaviour_index": 4,
                 "status": disp.Task.STATUS_LIST["IN_PROGRESS"],
                 "robot": "4",
                 "start_time": "2018-06-29 07:23:27",
                 "weight": 3}
    task = disp.Task(task_data)
    assert task.get_poi_goal() == "1"

    task_data = {"id": "1",
                 "behaviours": [{"id": "1", "parameters": {"to": "5", "name": disp.Behaviour.TYPES["goto"]}},
                                {"id": "2", "parameters": {"name": disp.Behaviour.TYPES["dock"]}},
                                {"id": "3", "parameters": {"name": disp.Behaviour.TYPES["wait"]}},
                                {"id": "4", "parameters": {"name": disp.Behaviour.TYPES["undock"]}},
                                {"id": "5", "parameters": {"to": "1", "name": disp.Behaviour.TYPES["goto"]}}],
                 "current_behaviour_index": -1,
                 "status": disp.Task.STATUS_LIST["TO_DO"],
                 "robot": "4",
                 "start_time": "2018-06-29 07:23:27",
                 "weight": 3}
    task = disp.Task(task_data)
    assert task.get_poi_goal() == "5"

    task_data = {"id": "1",
                 "behaviours": [{"id": "2", "parameters": {"name": disp.Behaviour.TYPES["dock"]}},
                                {"id": "3", "parameters": {"name": disp.Behaviour.TYPES["wait"]}},
                                {"id": "4", "parameters": {"name": disp.Behaviour.TYPES["undock"]}},
                                {"id": "5", "parameters": {"to": "1", "name": disp.Behaviour.TYPES["goto"]}}],
                 "current_behaviour_index": -1,
                 "status": disp.Task.STATUS_LIST["TO_DO"],
                 "robot": "4",
                 "start_time": "2018-06-29 07:23:27",
                 "weight": 3}
    task = disp.Task(task_data)
    assert task.get_poi_goal() == "1"


@pytest.mark.task_methods
def test_task_is_planned_swap():
    task_data = {"id": "swap_1",
                 "behaviours": [{"id": "1", "parameters": {"to": "5", "name": disp.Behaviour.TYPES["goto"]}},
                                {"id": "2", "parameters": {"name": disp.Behaviour.TYPES["dock"]}},
                                {"id": "3", "parameters": {"name": disp.Behaviour.TYPES["bat_ex"]}},
                                {"id": "4", "parameters": {"name": disp.Behaviour.TYPES["undock"]}},
                                {"id": "5", "parameters": {"to": "1", "name": disp.Behaviour.TYPES["goto"]}}],
                 "current_behaviour_index": 0,
                 "status": disp.Task.STATUS_LIST["TO_DO"],
                 "robot": "4",
                 "start_time": "2018-06-29 07:23:27",
                 "weight": 3}
    task = disp.Task(task_data)
    assert task.is_planned_swap()


# ------------------------------ Task manager methods ------------------------------ #
@pytest.mark.task_manager_methods
def test_task_manager_check_if_method_exist():
    tasks_raw = [{"id": "1",
                  "behaviours": [{"id": "1", "parameters": {"to": "5", "name": disp.Behaviour.TYPES["goto"]}},
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
                  "behaviours": [{"id": "1", "parameters": {"to": "5", "name": disp.Behaviour.TYPES["goto"]}},
                                 {"id": "2", "parameters": {"name": disp.Behaviour.TYPES["dock"]}},
                                 {"id": "3", "parameters": {"name": disp.Behaviour.TYPES["wait"]}},
                                 {"id": "4", "parameters": {"name": disp.Behaviour.TYPES["undock"]}},
                                 {"id": "5", "parameters": {"to": "1", "name": disp.Behaviour.TYPES["goto"]}}],
                  "current_behaviour_index": 0,  # index tablicy nie zachowania
                  "status": disp.Task.STATUS_LIST["IN_PROGRESS"],
                  "robot": "2",
                  "start_time": "2018-06-29 07:27:27",
                  "weight": 2,
                  "priority": 2
                  },
                 {"id": "3",
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
                 {"id": "4",
                  "behaviours": [{"id": "1", "parameters": {"to": "5", "name": disp.Behaviour.TYPES["goto"]}},
                                 {"id": "2", "parameters": {"name": disp.Behaviour.TYPES["dock"]}},
                                 {"id": "3", "parameters": {"name": disp.Behaviour.TYPES["wait"]}},
                                 {"id": "4", "parameters": {"name": disp.Behaviour.TYPES["undock"]}},
                                 {"id": "5", "parameters": {"to": "1", "name": disp.Behaviour.TYPES["goto"]}}],
                  "current_behaviour_index": 0,  # index tablicy nie zachowania
                  "status": disp.Task.STATUS_LIST["IN_PROGRESS"],
                  "robot": "4",
                  "start_time": "2018-06-29 07:23:27",
                  "weight": 2,
                  "priority": 2
                  },
                 ]

    tasks = [disp.Task(data) for data in tasks_raw]

    manager = disp.TasksManager(tasks)
    assert "set_tasks" in dir(manager)
    assert "remove_tasks_by_id" in dir(manager)
    assert "get_all_unasigned_unstarted_tasks" in dir(manager)

    assert "tasks" in dir(manager)


@pytest.mark.task_manager_methods
def test_task_manager_set_tasks_sorted_list():
    tasks_raw = [{"id": "1",
                  "behaviours": [{"id": "1", "parameters": {"to": "5", "name": disp.Behaviour.TYPES["goto"]}},
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
                  "behaviours": [{"id": "1", "parameters": {"to": "5", "name": disp.Behaviour.TYPES["goto"]}},
                                 {"id": "2", "parameters": {"name": disp.Behaviour.TYPES["dock"]}},
                                 {"id": "3", "parameters": {"name": disp.Behaviour.TYPES["wait"]}},
                                 {"id": "4", "parameters": {"name": disp.Behaviour.TYPES["undock"]}},
                                 {"id": "5", "parameters": {"to": "1", "name": disp.Behaviour.TYPES["goto"]}}],
                  "current_behaviour_index": 0,  # index tablicy nie zachowania
                  "status": disp.Task.STATUS_LIST["IN_PROGRESS"],
                  "robot": "2",
                  "start_time": "2018-06-29 07:27:27",
                  "weight": 2,
                  "priority": 2
                  },
                 {"id": "3",
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
                 {"id": "4",
                  "behaviours": [{"id": "1", "parameters": {"to": "5", "name": disp.Behaviour.TYPES["goto"]}},
                                 {"id": "2", "parameters": {"name": disp.Behaviour.TYPES["dock"]}},
                                 {"id": "3", "parameters": {"name": disp.Behaviour.TYPES["wait"]}},
                                 {"id": "4", "parameters": {"name": disp.Behaviour.TYPES["undock"]}},
                                 {"id": "5", "parameters": {"to": "1", "name": disp.Behaviour.TYPES["goto"]}}],
                  "current_behaviour_index": 0,  # index tablicy nie zachowania
                  "status": disp.Task.STATUS_LIST["IN_PROGRESS"],
                  "robot": "4",
                  "start_time": "2018-06-29 07:23:27",
                  "weight": 2,
                  "priority": 2
                  },
                 ]

    tasks = [disp.Task(data) for data in tasks_raw]

    tasks_ordered = ["3", "1", "2", "4"]
    manager = disp.TasksManager(tasks)
    assert [task.id for task in manager.tasks] == tasks_ordered

    tasks_raw = [{"id": "1",
                  "behaviours": [{"id": "1", "parameters": {"to": "5", "name": disp.Behaviour.TYPES["goto"]}},
                                 {"id": "2", "parameters": {"name": disp.Behaviour.TYPES["dock"]}},
                                 {"id": "3", "parameters": {"name": disp.Behaviour.TYPES["wait"]}},
                                 {"id": "4", "parameters": {"name": disp.Behaviour.TYPES["undock"]}},
                                 {"id": "5", "parameters": {"to": "1", "name": disp.Behaviour.TYPES["goto"]}}],
                  "current_behaviour_index": -1,  # index tablicy nie zachowania
                  "status": disp.Task.STATUS_LIST["TO_DO"],
                  "robot": "1",
                  "start_time": "2018-06-29 07:37:27",
                  "weight": 3,
                  "priority": 3
                  },
                 {"id": "2",
                  "behaviours": [{"id": "1", "parameters": {"to": "5", "name": disp.Behaviour.TYPES["goto"]}},
                                 {"id": "2", "parameters": {"name": disp.Behaviour.TYPES["dock"]}},
                                 {"id": "3", "parameters": {"name": disp.Behaviour.TYPES["wait"]}},
                                 {"id": "4", "parameters": {"name": disp.Behaviour.TYPES["undock"]}},
                                 {"id": "5", "parameters": {"to": "1", "name": disp.Behaviour.TYPES["goto"]}}],
                  "current_behaviour_index": -1,  # index tablicy nie zachowania
                  "status": disp.Task.STATUS_LIST["TO_DO"],
                  "robot": "2",
                  "start_time": "2018-06-29 07:27:27",
                  "weight": 4,
                  "priority": 4
                  },
                 {"id": "3",
                  "behaviours": [{"id": "1", "parameters": {"to": "5", "name": disp.Behaviour.TYPES["goto"]}},
                                 {"id": "2", "parameters": {"name": disp.Behaviour.TYPES["dock"]}},
                                 {"id": "3", "parameters": {"name": disp.Behaviour.TYPES["wait"]}},
                                 {"id": "4", "parameters": {"name": disp.Behaviour.TYPES["undock"]}},
                                 {"id": "5", "parameters": {"to": "1", "name": disp.Behaviour.TYPES["goto"]}}],
                  "current_behaviour_index": -1,  # index tablicy nie zachowania
                  "status": disp.Task.STATUS_LIST["TO_DO"],
                  "robot": "3",
                  "start_time": "2018-06-29 07:15:27",
                  "weight": 3,
                  "priority": 3
                  },
                 {"id": "4",
                  "behaviours": [{"id": "1", "parameters": {"to": "5", "name": disp.Behaviour.TYPES["goto"]}},
                                 {"id": "2", "parameters": {"name": disp.Behaviour.TYPES["dock"]}},
                                 {"id": "3", "parameters": {"name": disp.Behaviour.TYPES["wait"]}},
                                 {"id": "4", "parameters": {"name": disp.Behaviour.TYPES["undock"]}},
                                 {"id": "5", "parameters": {"to": "1", "name": disp.Behaviour.TYPES["goto"]}}],
                  "current_behaviour_index": -1,  # index tablicy nie zachowania
                  "status": disp.Task.STATUS_LIST["TO_DO"],
                  "robot": "4",
                  "start_time": "2018-06-29 07:23:27",
                  "weight": 4,
                  "priority": 4
                  },
                 {"id": "5",
                  "behaviours": [{"id": "1", "parameters": {"to": "5", "name": disp.Behaviour.TYPES["goto"]}},
                                 {"id": "2", "parameters": {"name": disp.Behaviour.TYPES["dock"]}},
                                 {"id": "3", "parameters": {"name": disp.Behaviour.TYPES["wait"]}},
                                 {"id": "4", "parameters": {"name": disp.Behaviour.TYPES["undock"]}},
                                 {"id": "5", "parameters": {"to": "1", "name": disp.Behaviour.TYPES["goto"]}}],
                  "current_behaviour_index": -1,  # index tablicy nie zachowania
                  "status": disp.Task.STATUS_LIST["TO_DO"],
                  "robot": "1",
                  "start_time": "2018-06-29 07:37:27",
                  "weight": 4,
                  "priority": 4
                  },
                 {"id": "6",
                  "behaviours": [{"id": "1", "parameters": {"to": "5", "name": disp.Behaviour.TYPES["goto"]}},
                                 {"id": "2", "parameters": {"name": disp.Behaviour.TYPES["dock"]}},
                                 {"id": "3", "parameters": {"name": disp.Behaviour.TYPES["wait"]}},
                                 {"id": "4", "parameters": {"name": disp.Behaviour.TYPES["undock"]}},
                                 {"id": "5", "parameters": {"to": "1", "name": disp.Behaviour.TYPES["goto"]}}],
                  "current_behaviour_index": -1,  # index tablicy nie zachowania
                  "status": disp.Task.STATUS_LIST["TO_DO"],
                  "robot": "2",
                  "start_time": "2018-06-29 07:27:27",
                  "weight": 4,
                  "priority": 4
                  },
                 {"id": "7",
                  "behaviours": [{"id": "1", "parameters": {"to": "5", "name": disp.Behaviour.TYPES["goto"]}},
                                 {"id": "2", "parameters": {"name": disp.Behaviour.TYPES["dock"]}},
                                 {"id": "3", "parameters": {"name": disp.Behaviour.TYPES["wait"]}},
                                 {"id": "4", "parameters": {"name": disp.Behaviour.TYPES["undock"]}},
                                 {"id": "5", "parameters": {"to": "1", "name": disp.Behaviour.TYPES["goto"]}}],
                  "current_behaviour_index": -1,  # index tablicy nie zachowania
                  "status": disp.Task.STATUS_LIST["TO_DO"],
                  "robot": "3",
                  "start_time": "2018-06-29 07:15:27",
                  "weight": 2,
                  "priority": 2
                  },
                 {"id": "8",
                  "behaviours": [{"id": "1", "parameters": {"to": "5", "name": disp.Behaviour.TYPES["goto"]}},
                                 {"id": "2", "parameters": {"name": disp.Behaviour.TYPES["dock"]}},
                                 {"id": "3", "parameters": {"name": disp.Behaviour.TYPES["wait"]}},
                                 {"id": "4", "parameters": {"name": disp.Behaviour.TYPES["undock"]}},
                                 {"id": "5", "parameters": {"to": "1", "name": disp.Behaviour.TYPES["goto"]}}],
                  "current_behaviour_index": -1,  # index tablicy nie zachowania
                  "status": disp.Task.STATUS_LIST["TO_DO"],
                  "robot": "4",
                  "start_time": "2018-06-29 07:23:27",
                 "weight": 1,
                  "priority": 1
                  },
                 {"id": "9",
                  "behaviours": [{"id": "1", "parameters": {"to": "5", "name": disp.Behaviour.TYPES["goto"]}},
                                 {"id": "2", "parameters": {"name": disp.Behaviour.TYPES["dock"]}},
                                 {"id": "3", "parameters": {"name": disp.Behaviour.TYPES["wait"]}},
                                 {"id": "4", "parameters": {"name": disp.Behaviour.TYPES["undock"]}},
                                 {"id": "5", "parameters": {"to": "1", "name": disp.Behaviour.TYPES["goto"]}}],
                  "current_behaviour_index": -1,  # index tablicy nie zachowania
                  "status": disp.Task.STATUS_LIST["TO_DO"],
                  "robot": "1",
                  "start_time": "2018-06-29 07:37:27",
                  "weight": 4,
                  "priority": 4
                  },
                 {"id": "10",
                  "behaviours": [{"id": "1", "parameters": {"to": "5", "name": disp.Behaviour.TYPES["goto"]}},
                                 {"id": "2", "parameters": {"name": disp.Behaviour.TYPES["dock"]}},
                                 {"id": "3", "parameters": {"name": disp.Behaviour.TYPES["wait"]}},
                                 {"id": "4", "parameters": {"name": disp.Behaviour.TYPES["undock"]}},
                                 {"id": "5", "parameters": {"to": "1", "name": disp.Behaviour.TYPES["goto"]}}],
                  "current_behaviour_index": -1,  # index tablicy nie zachowania
                  "status": disp.Task.STATUS_LIST["TO_DO"],
                  "robot": "2",
                  "start_time": "2018-06-29 07:27:27",
                  "weight": 3,
                  "priority": 3
                  },
                 {"id": "11",
                  "behaviours": [{"id": "1", "parameters": {"to": "5", "name": disp.Behaviour.TYPES["goto"]}},
                                 {"id": "2", "parameters": {"name": disp.Behaviour.TYPES["dock"]}},
                                 {"id": "3", "parameters": {"name": disp.Behaviour.TYPES["wait"]}},
                                 {"id": "4", "parameters": {"name": disp.Behaviour.TYPES["undock"]}},
                                 {"id": "5", "parameters": {"to": "1", "name": disp.Behaviour.TYPES["goto"]}}],
                  "current_behaviour_index": -1,  # index tablicy nie zachowania
                  "status": disp.Task.STATUS_LIST["TO_DO"],
                  "robot": "3",
                  "start_time": "2018-06-29 07:15:27",
                  "weight": 1,
                  "priority": 1
                  },
                 {"id": "12",
                  "behaviours": [{"id": "1", "parameters": {"to": "5", "name": disp.Behaviour.TYPES["goto"]}},
                                 {"id": "2", "parameters": {"name": disp.Behaviour.TYPES["dock"]}},
                                 {"id": "3", "parameters": {"name": disp.Behaviour.TYPES["wait"]}},
                                 {"id": "4", "parameters": {"name": disp.Behaviour.TYPES["undock"]}},
                                 {"id": "5", "parameters": {"to": "1", "name": disp.Behaviour.TYPES["goto"]}}],
                  "current_behaviour_index": -1,  # index tablicy nie zachowania
                  "status": disp.Task.STATUS_LIST["TO_DO"],
                  "robot": "4",
                  "start_time": "2018-06-29 07:23:27",
                  "weight": 1,
                  "priority": 1
                  },
                 {"id": "13",
                  "behaviours": [{"id": "1", "parameters": {"to": "5", "name": disp.Behaviour.TYPES["goto"]}},
                                 {"id": "2", "parameters": {"name": disp.Behaviour.TYPES["dock"]}},
                                 {"id": "3", "parameters": {"name": disp.Behaviour.TYPES["wait"]}},
                                 {"id": "4", "parameters": {"name": disp.Behaviour.TYPES["undock"]}},
                                 {"id": "5", "parameters": {"to": "1", "name": disp.Behaviour.TYPES["goto"]}}],
                  "current_behaviour_index": -1,  # index tablicy nie zachowania
                  "status": disp.Task.STATUS_LIST["TO_DO"],
                  "robot": "1",
                  "start_time": "2018-06-29 07:37:27",
                  "weight": 3,
                  "priority": 3
                  },
                 {"id": "14",
                  "behaviours": [{"id": "1", "parameters": {"to": "5", "name": disp.Behaviour.TYPES["goto"]}},
                                 {"id": "2", "parameters": {"name": disp.Behaviour.TYPES["dock"]}},
                                 {"id": "3", "parameters": {"name": disp.Behaviour.TYPES["wait"]}},
                                 {"id": "4", "parameters": {"name": disp.Behaviour.TYPES["undock"]}},
                                 {"id": "5", "parameters": {"to": "1", "name": disp.Behaviour.TYPES["goto"]}}],
                  "current_behaviour_index": -1,  # index tablicy nie zachowania
                  "status": disp.Task.STATUS_LIST["TO_DO"],
                  "robot": "2",
                  "start_time": "2018-06-29 07:27:27",
                  "weight": 3,
                  "priority": 3
                  },
                 {"id": "15",
                  "behaviours": [{"id": "1", "parameters": {"to": "5", "name": disp.Behaviour.TYPES["goto"]}},
                                 {"id": "2", "parameters": {"name": disp.Behaviour.TYPES["dock"]}},
                                 {"id": "3", "parameters": {"name": disp.Behaviour.TYPES["wait"]}},
                                 {"id": "4", "parameters": {"name": disp.Behaviour.TYPES["undock"]}},
                                 {"id": "5", "parameters": {"to": "1", "name": disp.Behaviour.TYPES["goto"]}}],
                  "current_behaviour_index": -1,  # index tablicy nie zachowania
                  "status": disp.Task.STATUS_LIST["TO_DO"],
                  "robot": "3",
                  "start_time": "2018-06-29 07:15:27",
                  "weight": 3,
                  "priority": 3
                  },
                 {"id": "16",
                  "behaviours": [{"id": "1", "parameters": {"to": "5", "name": disp.Behaviour.TYPES["goto"]}},
                                 {"id": "2", "parameters": {"name": disp.Behaviour.TYPES["dock"]}},
                                 {"id": "3", "parameters": {"name": disp.Behaviour.TYPES["wait"]}},
                                 {"id": "4", "parameters": {"name": disp.Behaviour.TYPES["undock"]}},
                                 {"id": "5", "parameters": {"to": "1", "name": disp.Behaviour.TYPES["goto"]}}],
                  "current_behaviour_index": -1,  # index tablicy nie zachowania
                  "status": disp.Task.STATUS_LIST["TO_DO"],
                  "robot": "4",
                  "start_time": "2018-06-29 07:23:27",
                  "weight": 1,
                  "priority": 1
                  },
                 {"id": "17",
                  "behaviours": [{"id": "1", "parameters": {"to": "5", "name": disp.Behaviour.TYPES["goto"]}},
                                 {"id": "2", "parameters": {"name": disp.Behaviour.TYPES["dock"]}},
                                 {"id": "3", "parameters": {"name": disp.Behaviour.TYPES["wait"]}},
                                 {"id": "4", "parameters": {"name": disp.Behaviour.TYPES["undock"]}},
                                 {"id": "5", "parameters": {"to": "1", "name": disp.Behaviour.TYPES["goto"]}}],
                  "current_behaviour_index": -1,  # index tablicy nie zachowania
                  "status": disp.Task.STATUS_LIST["TO_DO"],
                  "robot": "1",
                  "start_time": "2018-06-29 07:37:27",
                  "weight": 3,
                  "priority": 3
                  },
                 {"id": "18",
                  "behaviours": [{"id": "1", "parameters": {"to": "5", "name": disp.Behaviour.TYPES["goto"]}},
                                 {"id": "2", "parameters": {"name": disp.Behaviour.TYPES["dock"]}},
                                 {"id": "3", "parameters": {"name": disp.Behaviour.TYPES["wait"]}},
                                 {"id": "4", "parameters": {"name": disp.Behaviour.TYPES["undock"]}},
                                 {"id": "5", "parameters": {"to": "1", "name": disp.Behaviour.TYPES["goto"]}}],
                  "current_behaviour_index": -1,  # index tablicy nie zachowania
                  "status": disp.Task.STATUS_LIST["TO_DO"],
                  "robot": "2",
                  "start_time": "2018-06-29 07:27:27",
                  "weight": 2,
                  "priority": 2
                  },
                 {"id": "19",
                  "behaviours": [{"id": "1", "parameters": {"to": "5", "name": disp.Behaviour.TYPES["goto"]}},
                                 {"id": "2", "parameters": {"name": disp.Behaviour.TYPES["dock"]}},
                                 {"id": "3", "parameters": {"name": disp.Behaviour.TYPES["wait"]}},
                                 {"id": "4", "parameters": {"name": disp.Behaviour.TYPES["undock"]}},
                                 {"id": "5", "parameters": {"to": "1", "name": disp.Behaviour.TYPES["goto"]}}],
                  "current_behaviour_index": -1,  # index tablicy nie zachowania
                  "status": disp.Task.STATUS_LIST["TO_DO"],
                  "robot": "3",
                  "start_time": "2018-06-29 07:15:27",
                  "weight": 2,
                  "priority": 2
                  },
                 {"id": "20",
                  "behaviours": [{"id": "1", "parameters": {"to": "5", "name": disp.Behaviour.TYPES["goto"]}},
                                 {"id": "2", "parameters": {"name": disp.Behaviour.TYPES["dock"]}},
                                 {"id": "3", "parameters": {"name": disp.Behaviour.TYPES["wait"]}},
                                 {"id": "4", "parameters": {"name": disp.Behaviour.TYPES["undock"]}},
                                 {"id": "5", "parameters": {"to": "1", "name": disp.Behaviour.TYPES["goto"]}}],
                  "current_behaviour_index": -1,  # index tablicy nie zachowania
                  "status": disp.Task.STATUS_LIST["TO_DO"],
                  "robot": "4",
                  "start_time": "2018-06-29 07:23:27",
                  "weight": 2,
                  "priority": 2
                  },
                 ]

    # task id  [1  2  3  4  5  6  7  8  9 10  11 12 13 14 15 16 17 18 19 20]
    # weight   [3, 4, 3, 4, 4, 4, 2, 1, 4, 3, 1, 1, 3, 3, 3, 1, 3, 2, 2, 2]
    tasks = [disp.Task(data) for data in tasks_raw]
    tasks_ordered = ["2", "4", "5", "6", "9", "1", "3", "10", "13", "14", "15", "17", "7", "18", "19", "20",
                     "8", "11", "12", "16"]
    manager = disp.TasksManager(tasks)
    assert [task.id for task in manager.tasks] == tasks_ordered


@pytest.mark.task_manager_methods
def test_task_manager_set_tasks_throws_input_input_data_type_exception():
    tasks = {1: {"id": "1",
                 "behaviours": [{"id": "1", "parameters": {"to": "5", "name": disp.Behaviour.TYPES["goto"]}},
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
             2: {"id": "2",
                 "behaviours": [{"id": "1", "parameters": {"to": "5", "name": disp.Behaviour.TYPES["goto"]}},
                                {"id": "2", "parameters": {"name": disp.Behaviour.TYPES["dock"]}},
                                {"id": "3", "parameters": {"name": disp.Behaviour.TYPES["wait"]}},
                                {"id": "4", "parameters": {"name": disp.Behaviour.TYPES["undock"]}},
                                {"id": "5", "parameters": {"to": "1", "name": disp.Behaviour.TYPES["goto"]}}],
                 "current_behaviour_index": 0,  # index tablicy nie zachowania
                 "status": disp.Task.STATUS_LIST["IN_PROGRESS"],
                 "robot": "2",
                 "start_time": "2018-06-29 07:27:27",
                 "weight": 2,
                 "priority": 2
                 },
             3: {"id": "3",
                 "behaviours": [{"id": "1", "parameters": {"to": "5", "name": disp.Behaviour.TYPES["goto"]}},
                                {"id": "2", "parameters": {"name": disp.Behaviour.TYPES["dock"]}},
                                {"id": "3", "parameters": {"name": disp.Behaviour.TYPES["wait"]}},
                                {"id": "4", "parameters": {"name": disp.Behaviour.TYPES["undock"]}},
                                {"id": "5", "parameters": {"to": "1", "name": disp.Behaviour.TYPES["goto"]}}],
                 "current_behaviour_index": 0,  # index tablicy nie zachowania
                 "status": disp.Task.STATUS_LIST["IN_PROGRESS"],
                 "robot": "7",
                 "start_time": "2018-06-29 07:15:27",
                 "weight": 3,
                 "priority": 3
                 },
             4: {"id": "4",
                 "behaviours": [{"id": "1", "parameters": {"to": "5", "name": disp.Behaviour.TYPES["goto"]}},
                                {"id": "2", "parameters": {"name": disp.Behaviour.TYPES["dock"]}},
                                {"id": "3", "parameters": {"name": disp.Behaviour.TYPES["wait"]}},
                                {"id": "4", "parameters": {"name": disp.Behaviour.TYPES["undock"]}},
                                {"id": "5", "parameters": {"to": "1", "name": disp.Behaviour.TYPES["goto"]}}],
                 "current_behaviour_index": 0,  # index tablicy nie zachowania
                 "status": disp.Task.STATUS_LIST["IN_PROGRESS"],
                 "robot": "4",
                 "start_time": "2018-06-29 07:23:27",
                 "weight": 2,
                 "priority": 2
                 },
             }
    try:
        disp.TasksManager(tasks)
    except disp.WrongTaskInputData as error:
        assert "Input tasks list should be list but '{}' was given.".format(type(tasks)) == str(error)
    else:
        assert False


@pytest.mark.task_manager_methods
def test_task_manager_set_tasks_proper_weight():
    tasks_raw = [{"id": "1",
                  "behaviours": [{"id": "1", "parameters": {"to": "5", "name": disp.Behaviour.TYPES["goto"]}},
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
                  "behaviours": [{"id": "1", "parameters": {"to": "5", "name": disp.Behaviour.TYPES["goto"]}},
                                 {"id": "2", "parameters": {"name": disp.Behaviour.TYPES["dock"]}},
                                 {"id": "3", "parameters": {"name": disp.Behaviour.TYPES["wait"]}},
                                 {"id": "4", "parameters": {"name": disp.Behaviour.TYPES["undock"]}},
                                 {"id": "5", "parameters": {"to": "1", "name": disp.Behaviour.TYPES["goto"]}}],
                  "current_behaviour_index": 0,  # index tablicy nie zachowania
                  "status": disp.Task.STATUS_LIST["IN_PROGRESS"],
                  "robot": "2",
                  "start_time": "2018-06-29 07:27:27",
                  "weight": 2,
                  "priority": 2
                  },
                 {"id": "3",
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
                 {"id": "4",
                  "behaviours": [{"id": "1", "parameters": {"to": "5", "name": disp.Behaviour.TYPES["goto"]}},
                                 {"id": "2", "parameters": {"name": disp.Behaviour.TYPES["dock"]}},
                                 {"id": "3", "parameters": {"name": disp.Behaviour.TYPES["wait"]}},
                                 {"id": "4", "parameters": {"name": disp.Behaviour.TYPES["undock"]}},
                                 {"id": "5", "parameters": {"to": "1", "name": disp.Behaviour.TYPES["goto"]}}],
                  "current_behaviour_index": 0,  # index tablicy nie zachowania
                  "status": disp.Task.STATUS_LIST["IN_PROGRESS"],
                  "robot": "4",
                  "start_time": "2018-06-29 07:23:27",
                  "weight": 2,
                  "priority": 2
                  },
                 ]
    tasks = [disp.Task(data) for data in tasks_raw]
    # tasks_ordered = ["3", "1", "2", "4"]
    weight_list = [3, 2, 2, 2]
    manager = disp.TasksManager(tasks)
    manager_weight = [task.weight for task in manager.tasks]
    assert weight_list == manager_weight


@pytest.mark.task_manager_methods
def test_task_manager_remove_tasks_by_id():
    # task id  [1  2  3  4  5  6  7  8  9 10  11 12 13 14 15 16 17 18 19 20]
    # weight   [3, 4, 3, 4, 4, 4, 2, 1, 4, 3, 1, 1, 3, 3, 3, 1, 3, 2, 2, 2]
    # tasks_ordered = ["2", "4", "5", "6", "9", "1", "3", "10", "13", "14", "15", "17", "7", "18", "19", "20",
    #                  "8", "11", "12", "16"]
    tasks_raw = [{"id": "1",
                  "behaviours": [{"id": "1", "parameters": {"to": "5", "name": disp.Behaviour.TYPES["goto"]}},
                                 {"id": "2", "parameters": {"name": disp.Behaviour.TYPES["dock"]}},
                                 {"id": "3", "parameters": {"name": disp.Behaviour.TYPES["wait"]}},
                                 {"id": "4", "parameters": {"name": disp.Behaviour.TYPES["undock"]}},
                                 {"id": "5", "parameters": {"to": "1", "name": disp.Behaviour.TYPES["goto"]}}],
                  "current_behaviour_index": -1,  # index tablicy nie zachowania
                  "status": disp.Task.STATUS_LIST["TO_DO"],
                  "robot": "1",
                  "start_time": "2018-06-29 07:37:27",
                  "weight": 3,
                  "priority": 3
                  },
                 {"id": "2",
                  "behaviours": [{"id": "1", "parameters": {"to": "5", "name": disp.Behaviour.TYPES["goto"]}},
                                 {"id": "2", "parameters": {"name": disp.Behaviour.TYPES["dock"]}},
                                 {"id": "3", "parameters": {"name": disp.Behaviour.TYPES["wait"]}},
                                 {"id": "4", "parameters": {"name": disp.Behaviour.TYPES["undock"]}},
                                 {"id": "5", "parameters": {"to": "1", "name": disp.Behaviour.TYPES["goto"]}}],
                  "current_behaviour_index": -1,  # index tablicy nie zachowania
                  "status": disp.Task.STATUS_LIST["TO_DO"],
                  "robot": "2",
                  "start_time": "2018-06-29 07:27:27",
                 "weight": 4,
                  "priority": 4
                  },
                 {"id": "3",
                  "behaviours": [{"id": "1", "parameters": {"to": "5", "name": disp.Behaviour.TYPES["goto"]}},
                                 {"id": "2", "parameters": {"name": disp.Behaviour.TYPES["dock"]}},
                                 {"id": "3", "parameters": {"name": disp.Behaviour.TYPES["wait"]}},
                                 {"id": "4", "parameters": {"name": disp.Behaviour.TYPES["undock"]}},
                                 {"id": "5", "parameters": {"to": "1", "name": disp.Behaviour.TYPES["goto"]}}],
                  "current_behaviour_index": -1,  # index tablicy nie zachowania
                  "status": disp.Task.STATUS_LIST["TO_DO"],
                  "robot": "3",
                  "start_time": "2018-06-29 07:15:27",
                  "weight": 3,
                  "priority": 3
                  },
                 {"id": "4",
                  "behaviours": [{"id": "1", "parameters": {"to": "5", "name": disp.Behaviour.TYPES["goto"]}},
                                 {"id": "2", "parameters": {"name": disp.Behaviour.TYPES["dock"]}},
                                 {"id": "3", "parameters": {"name": disp.Behaviour.TYPES["wait"]}},
                                 {"id": "4", "parameters": {"name": disp.Behaviour.TYPES["undock"]}},
                                 {"id": "5", "parameters": {"to": "1", "name": disp.Behaviour.TYPES["goto"]}}],
                  "current_behaviour_index": -1,  # index tablicy nie zachowania
                  "status": disp.Task.STATUS_LIST["TO_DO"],
                  "robot": "4",
                  "start_time": "2018-06-29 07:23:27",
                  "weight": 4,
                  "priority": 4
                  },
                 {"id": "5",
                  "behaviours": [{"id": "1", "parameters": {"to": "5", "name": disp.Behaviour.TYPES["goto"]}},
                                 {"id": "2", "parameters": {"name": disp.Behaviour.TYPES["dock"]}},
                                 {"id": "3", "parameters": {"name": disp.Behaviour.TYPES["wait"]}},
                                 {"id": "4", "parameters": {"name": disp.Behaviour.TYPES["undock"]}},
                                 {"id": "5", "parameters": {"to": "1", "name": disp.Behaviour.TYPES["goto"]}}],
                  "current_behaviour_index": -1,  # index tablicy nie zachowania
                  "status": disp.Task.STATUS_LIST["TO_DO"],
                  "robot": "1",
                  "start_time": "2018-06-29 07:37:27",
                  "weight": 4,
                  "priority": 4
                  },
                 {"id": "6",
                  "behaviours": [{"id": "1", "parameters": {"to": "5", "name": disp.Behaviour.TYPES["goto"]}},
                                 {"id": "2", "parameters": {"name": disp.Behaviour.TYPES["dock"]}},
                                 {"id": "3", "parameters": {"name": disp.Behaviour.TYPES["wait"]}},
                                 {"id": "4", "parameters": {"name": disp.Behaviour.TYPES["undock"]}},
                                 {"id": "5", "parameters": {"to": "1", "name": disp.Behaviour.TYPES["goto"]}}],
                  "current_behaviour_index": -1,  # index tablicy nie zachowania
                  "status": disp.Task.STATUS_LIST["TO_DO"],
                  "robot": "2",
                  "start_time": "2018-06-29 07:27:27",
                  "weight": 4,
                  "priority": 4
                  },
                 {"id": "7",
                  "behaviours": [{"id": "1", "parameters": {"to": "5", "name": disp.Behaviour.TYPES["goto"]}},
                                 {"id": "2", "parameters": {"name": disp.Behaviour.TYPES["dock"]}},
                                 {"id": "3", "parameters": {"name": disp.Behaviour.TYPES["wait"]}},
                                 {"id": "4", "parameters": {"name": disp.Behaviour.TYPES["undock"]}},
                                 {"id": "5", "parameters": {"to": "1", "name": disp.Behaviour.TYPES["goto"]}}],
                  "current_behaviour_index": -1,  # index tablicy nie zachowania
                  "status": disp.Task.STATUS_LIST["TO_DO"],
                  "robot": "3",
                  "start_time": "2018-06-29 07:15:27",
                  "weight": 2,
                  "priority": 2
                  },
                 {"id": "8",
                  "behaviours": [{"id": "1", "parameters": {"to": "5", "name": disp.Behaviour.TYPES["goto"]}},
                                 {"id": "2", "parameters": {"name": disp.Behaviour.TYPES["dock"]}},
                                 {"id": "3", "parameters": {"name": disp.Behaviour.TYPES["wait"]}},
                                 {"id": "4", "parameters": {"name": disp.Behaviour.TYPES["undock"]}},
                                 {"id": "5", "parameters": {"to": "1", "name": disp.Behaviour.TYPES["goto"]}}],
                  "current_behaviour_index": -1,  # index tablicy nie zachowania
                  "status": disp.Task.STATUS_LIST["TO_DO"],
                  "robot": "4",
                  "start_time": "2018-06-29 07:23:27",
                  "weight": 1,
                  "priority": 1
                  },
                 {"id": "9",
                  "behaviours": [{"id": "1", "parameters": {"to": "5", "name": disp.Behaviour.TYPES["goto"]}},
                                 {"id": "2", "parameters": {"name": disp.Behaviour.TYPES["dock"]}},
                                 {"id": "3", "parameters": {"name": disp.Behaviour.TYPES["wait"]}},
                                 {"id": "4", "parameters": {"name": disp.Behaviour.TYPES["undock"]}},
                                 {"id": "5", "parameters": {"to": "1", "name": disp.Behaviour.TYPES["goto"]}}],
                  "current_behaviour_index": -1,  # index tablicy nie zachowania
                  "status": disp.Task.STATUS_LIST["TO_DO"],
                  "robot": "1",
                  "start_time": "2018-06-29 07:37:27",
                  "weight": 4,
                  "priority": 4
                  },
                 {"id": "10",
                  "behaviours": [{"id": "1", "parameters": {"to": "5", "name": disp.Behaviour.TYPES["goto"]}},
                                 {"id": "2", "parameters": {"name": disp.Behaviour.TYPES["dock"]}},
                                 {"id": "3", "parameters": {"name": disp.Behaviour.TYPES["wait"]}},
                                 {"id": "4", "parameters": {"name": disp.Behaviour.TYPES["undock"]}},
                                 {"id": "5", "parameters": {"to": "1", "name": disp.Behaviour.TYPES["goto"]}}],
                  "current_behaviour_index": -1,  # index tablicy nie zachowania
                  "status": disp.Task.STATUS_LIST["TO_DO"],
                  "robot": "2",
                  "start_time": "2018-06-29 07:27:27",
                  "weight": 3,
                  "priority": 3
                  },
                 {"id": "11",
                  "behaviours": [{"id": "1", "parameters": {"to": "5", "name": disp.Behaviour.TYPES["goto"]}},
                                 {"id": "2", "parameters": {"name": disp.Behaviour.TYPES["dock"]}},
                                 {"id": "3", "parameters": {"name": disp.Behaviour.TYPES["wait"]}},
                                 {"id": "4", "parameters": {"name": disp.Behaviour.TYPES["undock"]}},
                                 {"id": "5", "parameters": {"to": "1", "name": disp.Behaviour.TYPES["goto"]}}],
                  "current_behaviour_index": -1,  # index tablicy nie zachowania
                  "status": disp.Task.STATUS_LIST["TO_DO"],
                  "robot": "3",
                  "start_time": "2018-06-29 07:15:27",
                  "weight": 1,
                  "priority": 1
                  },
                 {"id": "12",
                  "behaviours": [{"id": "1", "parameters": {"to": "5", "name": disp.Behaviour.TYPES["goto"]}},
                                 {"id": "2", "parameters": {"name": disp.Behaviour.TYPES["dock"]}},
                                 {"id": "3", "parameters": {"name": disp.Behaviour.TYPES["wait"]}},
                                 {"id": "4", "parameters": {"name": disp.Behaviour.TYPES["undock"]}},
                                 {"id": "5", "parameters": {"to": "1", "name": disp.Behaviour.TYPES["goto"]}}],
                  "current_behaviour_index": -1,  # index tablicy nie zachowania
                  "status": disp.Task.STATUS_LIST["TO_DO"],
                  "robot": "4",
                  "start_time": "2018-06-29 07:23:27",
                  "weight": 1,
                  "priority": 1
                  },
                 {"id": "13",
                  "behaviours": [{"id": "1", "parameters": {"to": "5", "name": disp.Behaviour.TYPES["goto"]}},
                                 {"id": "2", "parameters": {"name": disp.Behaviour.TYPES["dock"]}},
                                 {"id": "3", "parameters": {"name": disp.Behaviour.TYPES["wait"]}},
                                 {"id": "4", "parameters": {"name": disp.Behaviour.TYPES["undock"]}},
                                 {"id": "5", "parameters": {"to": "1", "name": disp.Behaviour.TYPES["goto"]}}],
                  "current_behaviour_index": -1,  # index tablicy nie zachowania
                  "status": disp.Task.STATUS_LIST["TO_DO"],
                  "robot": "1",
                  "start_time": "2018-06-29 07:37:27",
                  "weight": 3,
                  "priority": 3
                  },
                 {"id": "14",
                  "behaviours": [{"id": "1", "parameters": {"to": "5", "name": disp.Behaviour.TYPES["goto"]}},
                                 {"id": "2", "parameters": {"name": disp.Behaviour.TYPES["dock"]}},
                                 {"id": "3", "parameters": {"name": disp.Behaviour.TYPES["wait"]}},
                                 {"id": "4", "parameters": {"name": disp.Behaviour.TYPES["undock"]}},
                                 {"id": "5", "parameters": {"to": "1", "name": disp.Behaviour.TYPES["goto"]}}],
                  "current_behaviour_index": -1,  # index tablicy nie zachowania
                  "status": disp.Task.STATUS_LIST["TO_DO"],
                  "robot": "2",
                  "start_time": "2018-06-29 07:27:27",
                  "weight": 3,
                  "priority": 3
                  },
                 {"id": "15",
                  "behaviours": [{"id": "1", "parameters": {"to": "5", "name": disp.Behaviour.TYPES["goto"]}},
                                 {"id": "2", "parameters": {"name": disp.Behaviour.TYPES["dock"]}},
                                 {"id": "3", "parameters": {"name": disp.Behaviour.TYPES["wait"]}},
                                 {"id": "4", "parameters": {"name": disp.Behaviour.TYPES["undock"]}},
                                 {"id": "5", "parameters": {"to": "1", "name": disp.Behaviour.TYPES["goto"]}}],
                  "current_behaviour_index": -1,  # index tablicy nie zachowania
                  "status": disp.Task.STATUS_LIST["TO_DO"],
                  "robot": "3",
                  "start_time": "2018-06-29 07:15:27",
                  "weight": 3,
                  "priority": 3
                  },
                 {"id": "16",
                  "behaviours": [{"id": "1", "parameters": {"to": "5", "name": disp.Behaviour.TYPES["goto"]}},
                                 {"id": "2", "parameters": {"name": disp.Behaviour.TYPES["dock"]}},
                                 {"id": "3", "parameters": {"name": disp.Behaviour.TYPES["wait"]}},
                                 {"id": "4", "parameters": {"name": disp.Behaviour.TYPES["undock"]}},
                                 {"id": "5", "parameters": {"to": "1", "name": disp.Behaviour.TYPES["goto"]}}],
                  "current_behaviour_index": -1,  # index tablicy nie zachowania
                  "status": disp.Task.STATUS_LIST["TO_DO"],
                  "robot": "4",
                  "start_time": "2018-06-29 07:23:27",
                  "weight": 1,
                  "priority": 1
                  },
                 {"id": "17",
                  "behaviours": [{"id": "1", "parameters": {"to": "5", "name": disp.Behaviour.TYPES["goto"]}},
                                 {"id": "2", "parameters": {"name": disp.Behaviour.TYPES["dock"]}},
                                 {"id": "3", "parameters": {"name": disp.Behaviour.TYPES["wait"]}},
                                 {"id": "4", "parameters": {"name": disp.Behaviour.TYPES["undock"]}},
                                 {"id": "5", "parameters": {"to": "1", "name": disp.Behaviour.TYPES["goto"]}}],
                  "current_behaviour_index": -1,  # index tablicy nie zachowania
                  "status": disp.Task.STATUS_LIST["TO_DO"],
                  "robot": "1",
                  "start_time": "2018-06-29 07:37:27",
                  "weight": 3,
                  "priority": 3
                  },
                 {"id": "18",
                  "behaviours": [{"id": "1", "parameters": {"to": "5", "name": disp.Behaviour.TYPES["goto"]}},
                                 {"id": "2", "parameters": {"name": disp.Behaviour.TYPES["dock"]}},
                                 {"id": "3", "parameters": {"name": disp.Behaviour.TYPES["wait"]}},
                                 {"id": "4", "parameters": {"name": disp.Behaviour.TYPES["undock"]}},
                                 {"id": "5", "parameters": {"to": "1", "name": disp.Behaviour.TYPES["goto"]}}],
                  "current_behaviour_index": -1,  # index tablicy nie zachowania
                  "status": disp.Task.STATUS_LIST["TO_DO"],
                  "robot": "2",
                  "start_time": "2018-06-29 07:27:27",
                  "weight": 2,
                  "priority": 2
                  },
                 {"id": "19",
                  "behaviours": [{"id": "1", "parameters": {"to": "5", "name": disp.Behaviour.TYPES["goto"]}},
                                 {"id": "2", "parameters": {"name": disp.Behaviour.TYPES["dock"]}},
                                 {"id": "3", "parameters": {"name": disp.Behaviour.TYPES["wait"]}},
                                 {"id": "4", "parameters": {"name": disp.Behaviour.TYPES["undock"]}},
                                 {"id": "5", "parameters": {"to": "1", "name": disp.Behaviour.TYPES["goto"]}}],
                  "current_behaviour_index": -1,  # index tablicy nie zachowania
                  "status": disp.Task.STATUS_LIST["TO_DO"],
                  "robot": "3",
                  "start_time": "2018-06-29 07:15:27",
                  "weight": 2,
                  "priority": 2
                  },
                 {"id": "20",
                  "behaviours": [{"id": "1", "parameters": {"to": "5", "name": disp.Behaviour.TYPES["goto"]}},
                                 {"id": "2", "parameters": {"name": disp.Behaviour.TYPES["dock"]}},
                                 {"id": "3", "parameters": {"name": disp.Behaviour.TYPES["wait"]}},
                                 {"id": "4", "parameters": {"name": disp.Behaviour.TYPES["undock"]}},
                                 {"id": "5", "parameters": {"to": "1", "name": disp.Behaviour.TYPES["goto"]}}],
                  "current_behaviour_index": -1,  # index tablicy nie zachowania
                  "status": disp.Task.STATUS_LIST["TO_DO"],
                  "robot": "4",
                  "start_time": "2018-06-29 07:23:27",
                  "weight": 2,
                  "priority": 2
                  },
                 ]
    tasks = [disp.Task(data) for data in tasks_raw]
    n_tasks = len(tasks)
    id_tasks_to_remove = ["5", "3", "16"]

    manager = disp.TasksManager(tasks)
    manager.remove_tasks_by_id(id_tasks_to_remove)
    n_manager_tasks = len(manager.tasks)
    assert n_manager_tasks == (n_tasks-len(id_tasks_to_remove))
    # sprawdzenie czy zadania o podanych id do usuniecia nie istnieja na liscie
    for id_remove in id_tasks_to_remove:
        for task in manager.tasks:
            assert task.id != id_remove


@pytest.mark.task_manager_methods
def test_task_manager_remove_tasks_by_id_task_doesnt_exist():
    # task id  [1  2  3  4  5  6  7  8  9 10  11 12 13 14 15 16 17 18 19 20]
    # weight   [3, 4, 3, 4, 4, 4, 2, 1, 4, 3, 1, 1, 3, 3, 3, 1, 3, 2, 2, 2]
    # tasks_ordered = ["2", "4", "5", "6", "9", "1", "3", "10", "13", "14", "15", "17", "7", "18", "19", "20",
    #                  "8", "11", "12", "16"]
    tasks_raw = [{"id": "1",
                  "behaviours": [{"id": "1", "parameters": {"to": "5", "name": disp.Behaviour.TYPES["goto"]}},
                                 {"id": "2", "parameters": {"name": disp.Behaviour.TYPES["dock"]}},
                                 {"id": "3", "parameters": {"name": disp.Behaviour.TYPES["wait"]}},
                                 {"id": "4", "parameters": {"name": disp.Behaviour.TYPES["undock"]}},
                                 {"id": "5", "parameters": {"to": "1", "name": disp.Behaviour.TYPES["goto"]}}],
                  "current_behaviour_index": -1,  # index tablicy nie zachowania
                  "status": disp.Task.STATUS_LIST["TO_DO"],
                  "robot": "1",
                  "start_time": "2018-06-29 07:37:27",
                  "weight": 3,
                  "priority": 3
                  },
                 {"id": "2",
                  "behaviours": [{"id": "1", "parameters": {"to": "5", "name": disp.Behaviour.TYPES["goto"]}},
                                 {"id": "2", "parameters": {"name": disp.Behaviour.TYPES["dock"]}},
                                 {"id": "3", "parameters": {"name": disp.Behaviour.TYPES["wait"]}},
                                 {"id": "4", "parameters": {"name": disp.Behaviour.TYPES["undock"]}},
                                 {"id": "5", "parameters": {"to": "1", "name": disp.Behaviour.TYPES["goto"]}}],
                  "current_behaviour_index": -1,  # index tablicy nie zachowania
                  "status": disp.Task.STATUS_LIST["TO_DO"],
                  "robot": "2",
                  "start_time": "2018-06-29 07:27:27",
                  "weight": 4,
                  "priority": 4
                  },
                 {"id": "3",
                  "behaviours": [{"id": "1", "parameters": {"to": "5", "name": disp.Behaviour.TYPES["goto"]}},
                                 {"id": "2", "parameters": {"name": disp.Behaviour.TYPES["dock"]}},
                                 {"id": "3", "parameters": {"name": disp.Behaviour.TYPES["wait"]}},
                                 {"id": "4", "parameters": {"name": disp.Behaviour.TYPES["undock"]}},
                                 {"id": "5", "parameters": {"to": "1", "name": disp.Behaviour.TYPES["goto"]}}],
                  "current_behaviour_index": -1,  # index tablicy nie zachowania
                  "status": disp.Task.STATUS_LIST["TO_DO"],
                  "robot": "3",
                  "start_time": "2018-06-29 07:15:27",
                  "weight": 3,
                  "priority": 3
                  },
                 {"id": "4",
                  "behaviours": [{"id": "1", "parameters": {"to": "5", "name": disp.Behaviour.TYPES["goto"]}},
                                 {"id": "2", "parameters": {"name": disp.Behaviour.TYPES["dock"]}},
                                 {"id": "3", "parameters": {"name": disp.Behaviour.TYPES["wait"]}},
                                 {"id": "4", "parameters": {"name": disp.Behaviour.TYPES["undock"]}},
                                 {"id": "5", "parameters": {"to": "1", "name": disp.Behaviour.TYPES["goto"]}}],
                  "current_behaviour_index": -1,  # index tablicy nie zachowania
                  "status": disp.Task.STATUS_LIST["TO_DO"],
                  "robot": "4",
                  "start_time": "2018-06-29 07:23:27",
                  "weight": 4,
                  "priority": 4
                  },
                 {"id": "5",
                  "behaviours": [{"id": "1", "parameters": {"to": "5", "name": disp.Behaviour.TYPES["goto"]}},
                                 {"id": "2", "parameters": {"name": disp.Behaviour.TYPES["dock"]}},
                                 {"id": "3", "parameters": {"name": disp.Behaviour.TYPES["wait"]}},
                                 {"id": "4", "parameters": {"name": disp.Behaviour.TYPES["undock"]}},
                                 {"id": "5", "parameters": {"to": "1", "name": disp.Behaviour.TYPES["goto"]}}],
                  "current_behaviour_index": -1,  # index tablicy nie zachowania
                  "status": disp.Task.STATUS_LIST["TO_DO"],
                  "robot": "1",
                  "start_time": "2018-06-29 07:37:27",
                  "weight": 4,
                  "priority": 4
                  },
                 {"id": "6",
                  "behaviours": [{"id": "1", "parameters": {"to": "5", "name": disp.Behaviour.TYPES["goto"]}},
                                 {"id": "2", "parameters": {"name": disp.Behaviour.TYPES["dock"]}},
                                 {"id": "3", "parameters": {"name": disp.Behaviour.TYPES["wait"]}},
                                 {"id": "4", "parameters": {"name": disp.Behaviour.TYPES["undock"]}},
                                 {"id": "5", "parameters": {"to": "1", "name": disp.Behaviour.TYPES["goto"]}}],
                  "current_behaviour_index": -1,  # index tablicy nie zachowania
                  "status": disp.Task.STATUS_LIST["TO_DO"],
                  "robot": "2",
                  "start_time": "2018-06-29 07:27:27",
                  "weight": 4,
                  "priority": 4
                  },
                 {"id": "7",
                  "behaviours": [{"id": "1", "parameters": {"to": "5", "name": disp.Behaviour.TYPES["goto"]}},
                                 {"id": "2", "parameters": {"name": disp.Behaviour.TYPES["dock"]}},
                                 {"id": "3", "parameters": {"name": disp.Behaviour.TYPES["wait"]}},
                                 {"id": "4", "parameters": {"name": disp.Behaviour.TYPES["undock"]}},
                                 {"id": "5", "parameters": {"to": "1", "name": disp.Behaviour.TYPES["goto"]}}],
                  "current_behaviour_index": -1,  # index tablicy nie zachowania
                  "status": disp.Task.STATUS_LIST["TO_DO"],
                  "robot": "3",
                  "start_time": "2018-06-29 07:15:27",
                  "weight": 2,
                  "priority": 2
                  },
                 {"id": "8",
                  "behaviours": [{"id": "1", "parameters": {"to": "5", "name": disp.Behaviour.TYPES["goto"]}},
                                 {"id": "2", "parameters": {"name": disp.Behaviour.TYPES["dock"]}},
                                 {"id": "3", "parameters": {"name": disp.Behaviour.TYPES["wait"]}},
                                 {"id": "4", "parameters": {"name": disp.Behaviour.TYPES["undock"]}},
                                 {"id": "5", "parameters": {"to": "1", "name": disp.Behaviour.TYPES["goto"]}}],
                  "current_behaviour_index": -1,  # index tablicy nie zachowania
                  "status": disp.Task.STATUS_LIST["TO_DO"],
                  "robot": "4",
                  "start_time": "2018-06-29 07:23:27",
                  "weight": 1,
                  "priority": 1
                  },
                 {"id": "9",
                  "behaviours": [{"id": "1", "parameters": {"to": "5", "name": disp.Behaviour.TYPES["goto"]}},
                                 {"id": "2", "parameters": {"name": disp.Behaviour.TYPES["dock"]}},
                                 {"id": "3", "parameters": {"name": disp.Behaviour.TYPES["wait"]}},
                                 {"id": "4", "parameters": {"name": disp.Behaviour.TYPES["undock"]}},
                                 {"id": "5", "parameters": {"to": "1", "name": disp.Behaviour.TYPES["goto"]}}],
                  "current_behaviour_index": -1,  # index tablicy nie zachowania
                  "status": disp.Task.STATUS_LIST["TO_DO"],
                  "robot": "1",
                  "start_time": "2018-06-29 07:37:27",
                  "weight": 4,
                  "priority": 4
                  },
                 {"id": "10",
                  "behaviours": [{"id": "1", "parameters": {"to": "5", "name": disp.Behaviour.TYPES["goto"]}},
                                 {"id": "2", "parameters": {"name": disp.Behaviour.TYPES["dock"]}},
                                 {"id": "3", "parameters": {"name": disp.Behaviour.TYPES["wait"]}},
                                 {"id": "4", "parameters": {"name": disp.Behaviour.TYPES["undock"]}},
                                 {"id": "5", "parameters": {"to": "1", "name": disp.Behaviour.TYPES["goto"]}}],
                  "current_behaviour_index": -1,  # index tablicy nie zachowania
                  "status": disp.Task.STATUS_LIST["TO_DO"],
                  "robot": "2",
                  "start_time": "2018-06-29 07:27:27",
                  "weight": 3,
                  "priority": 3
                  },
                 {"id": "11",
                  "behaviours": [{"id": "1", "parameters": {"to": "5", "name": disp.Behaviour.TYPES["goto"]}},
                                 {"id": "2", "parameters": {"name": disp.Behaviour.TYPES["dock"]}},
                                 {"id": "3", "parameters": {"name": disp.Behaviour.TYPES["wait"]}},
                                 {"id": "4", "parameters": {"name": disp.Behaviour.TYPES["undock"]}},
                                 {"id": "5", "parameters": {"to": "1", "name": disp.Behaviour.TYPES["goto"]}}],
                  "current_behaviour_index": -1,  # index tablicy nie zachowania
                  "status": disp.Task.STATUS_LIST["TO_DO"],
                  "robot": "3",
                  "start_time": "2018-06-29 07:15:27",
                  "weight": 1,
                  "priority": 1
                  },
                 {"id": "12",
                  "behaviours": [{"id": "1", "parameters": {"to": "5", "name": disp.Behaviour.TYPES["goto"]}},
                                 {"id": "2", "parameters": {"name": disp.Behaviour.TYPES["dock"]}},
                                 {"id": "3", "parameters": {"name": disp.Behaviour.TYPES["wait"]}},
                                 {"id": "4", "parameters": {"name": disp.Behaviour.TYPES["undock"]}},
                                 {"id": "5", "parameters": {"to": "1", "name": disp.Behaviour.TYPES["goto"]}}],
                  "current_behaviour_index": -1,  # index tablicy nie zachowania
                  "status": disp.Task.STATUS_LIST["TO_DO"],
                  "robot": "4",
                  "start_time": "2018-06-29 07:23:27",
                  "weight": 1,
                  "priority": 1
                  },
                 {"id": "13",
                  "behaviours": [{"id": "1", "parameters": {"to": "5", "name": disp.Behaviour.TYPES["goto"]}},
                                 {"id": "2", "parameters": {"name": disp.Behaviour.TYPES["dock"]}},
                                 {"id": "3", "parameters": {"name": disp.Behaviour.TYPES["wait"]}},
                                 {"id": "4", "parameters": {"name": disp.Behaviour.TYPES["undock"]}},
                                 {"id": "5", "parameters": {"to": "1", "name": disp.Behaviour.TYPES["goto"]}}],
                  "current_behaviour_index": -1,  # index tablicy nie zachowania
                  "status": disp.Task.STATUS_LIST["TO_DO"],
                  "robot": "1",
                  "start_time": "2018-06-29 07:37:27",
                  "weight": 3,
                  "priority": 3
                  },
                 {"id": "14",
                  "behaviours": [{"id": "1", "parameters": {"to": "5", "name": disp.Behaviour.TYPES["goto"]}},
                                 {"id": "2", "parameters": {"name": disp.Behaviour.TYPES["dock"]}},
                                 {"id": "3", "parameters": {"name": disp.Behaviour.TYPES["wait"]}},
                                 {"id": "4", "parameters": {"name": disp.Behaviour.TYPES["undock"]}},
                                 {"id": "5", "parameters": {"to": "1", "name": disp.Behaviour.TYPES["goto"]}}],
                  "current_behaviour_index": -1,  # index tablicy nie zachowania
                  "status": disp.Task.STATUS_LIST["TO_DO"],
                  "robot": "2",
                  "start_time": "2018-06-29 07:27:27",
                  "weight": 3,
                  "priority": 3
                  },
                 {"id": "15",
                  "behaviours": [{"id": "1", "parameters": {"to": "5", "name": disp.Behaviour.TYPES["goto"]}},
                                 {"id": "2", "parameters": {"name": disp.Behaviour.TYPES["dock"]}},
                                 {"id": "3", "parameters": {"name": disp.Behaviour.TYPES["wait"]}},
                                 {"id": "4", "parameters": {"name": disp.Behaviour.TYPES["undock"]}},
                                 {"id": "5", "parameters": {"to": "1", "name": disp.Behaviour.TYPES["goto"]}}],
                  "current_behaviour_index": -1,  # index tablicy nie zachowania
                  "status": disp.Task.STATUS_LIST["TO_DO"],
                  "robot": "3",
                  "start_time": "2018-06-29 07:15:27",
                  "weight": 3,
                  "priority": 3
                  },
                 {"id": "16",
                  "behaviours": [{"id": "1", "parameters": {"to": "5", "name": disp.Behaviour.TYPES["goto"]}},
                                 {"id": "2", "parameters": {"name": disp.Behaviour.TYPES["dock"]}},
                                 {"id": "3", "parameters": {"name": disp.Behaviour.TYPES["wait"]}},
                                 {"id": "4", "parameters": {"name": disp.Behaviour.TYPES["undock"]}},
                                 {"id": "5", "parameters": {"to": "1", "name": disp.Behaviour.TYPES["goto"]}}],
                  "current_behaviour_index": -1,  # index tablicy nie zachowania
                  "status": disp.Task.STATUS_LIST["TO_DO"],
                  "robot": "4",
                  "start_time": "2018-06-29 07:23:27",
                  "weight": 1,
                  "priority": 1
                  },
                 {"id": "17",
                  "behaviours": [{"id": "1", "parameters": {"to": "5", "name": disp.Behaviour.TYPES["goto"]}},
                                 {"id": "2", "parameters": {"name": disp.Behaviour.TYPES["dock"]}},
                                 {"id": "3", "parameters": {"name": disp.Behaviour.TYPES["wait"]}},
                                 {"id": "4", "parameters": {"name": disp.Behaviour.TYPES["undock"]}},
                                 {"id": "5", "parameters": {"to": "1", "name": disp.Behaviour.TYPES["goto"]}}],
                  "current_behaviour_index": -1,  # index tablicy nie zachowania
                  "status": disp.Task.STATUS_LIST["TO_DO"],
                  "robot": "1",
                  "start_time": "2018-06-29 07:37:27",
                  "weight": 3,
                  "priority": 3
                  },
                 {"id": "18",
                  "behaviours": [{"id": "1", "parameters": {"to": "5", "name": disp.Behaviour.TYPES["goto"]}},
                                 {"id": "2", "parameters": {"name": disp.Behaviour.TYPES["dock"]}},
                                 {"id": "3", "parameters": {"name": disp.Behaviour.TYPES["wait"]}},
                                 {"id": "4", "parameters": {"name": disp.Behaviour.TYPES["undock"]}},
                                 {"id": "5", "parameters": {"to": "1", "name": disp.Behaviour.TYPES["goto"]}}],
                  "current_behaviour_index": -1,  # index tablicy nie zachowania
                  "status": disp.Task.STATUS_LIST["TO_DO"],
                  "robot": "2",
                  "start_time": "2018-06-29 07:27:27",
                  "weight": 2,
                  "priority": 2
                  },
                 {"id": "19",
                  "behaviours": [{"id": "1", "parameters": {"to": "5", "name": disp.Behaviour.TYPES["goto"]}},
                                 {"id": "2", "parameters": {"name": disp.Behaviour.TYPES["dock"]}},
                                 {"id": "3", "parameters": {"name": disp.Behaviour.TYPES["wait"]}},
                                 {"id": "4", "parameters": {"name": disp.Behaviour.TYPES["undock"]}},
                                 {"id": "5", "parameters": {"to": "1", "name": disp.Behaviour.TYPES["goto"]}}],
                  "current_behaviour_index": -1,  # index tablicy nie zachowania
                  "status": disp.Task.STATUS_LIST["TO_DO"],
                  "robot": "3",
                  "start_time": "2018-06-29 07:15:27",
                  "weight": 2,
                  "priority": 2
                  },
                 {"id": "20",
                  "behaviours": [{"id": "1", "parameters": {"to": "5", "name": disp.Behaviour.TYPES["goto"]}},
                                 {"id": "2", "parameters": {"name": disp.Behaviour.TYPES["dock"]}},
                                 {"id": "3", "parameters": {"name": disp.Behaviour.TYPES["wait"]}},
                                 {"id": "4", "parameters": {"name": disp.Behaviour.TYPES["undock"]}},
                                 {"id": "5", "parameters": {"to": "1", "name": disp.Behaviour.TYPES["goto"]}}],
                  "current_behaviour_index": -1,  # index tablicy nie zachowania
                  "status": disp.Task.STATUS_LIST["TO_DO"],
                  "robot": "4",
                  "start_time": "2018-06-29 07:23:27",
                  "weight": 2,
                  "priority": 2
                  },
                 ]
    tasks = [disp.Task(data) for data in tasks_raw]
    tasks_id = [task["id"] for task in tasks_raw]
    n_tasks = len(tasks)
    id_tasks_to_remove = ["35", "3"]
    count_tasks_to_remove = 0
    for i in id_tasks_to_remove:
        if i in tasks_id:
            count_tasks_to_remove += 1

    manager = disp.TasksManager(tasks)
    manager.remove_tasks_by_id(id_tasks_to_remove)
    n_manager_tasks = len(manager.tasks)
    assert n_manager_tasks == (n_tasks-count_tasks_to_remove)
    # sprawdzenie czy zadania o podanych id do usuniecia nie istnieja na liscie
    for id_remove in id_tasks_to_remove:
        for task in manager.tasks:
            assert task.id != id_remove


@pytest.mark.task_manager_methods
def test_task_manager_get_free_tasks():
    # task id  [1  2  3  4  5  6  7  8  9 10  11 12 13 14 15 16 17 18 19 20]
    # weight   [3, 4, 3, 4, 4, 4, 2, 1, 4, 3, 1, 1, 3, 3, 3, 1, 3, 2, 2, 2]
    # tasks_ordered = ["2", "4", "5", "6", "9", "1", "3", "10", "13", "14", "15", "17", "7", "18", "19", "20",
    #                  "8", "11", "12", "16"]
    # nieprzypisane i nierozpoczete zadania id [4, 9, 3]
    tasks_raw = [{"id": "1",
                  "behaviours": [{"id": "1", "parameters": {"to": "5", "name": disp.Behaviour.TYPES["goto"]}},
                                 {"id": "2", "parameters": {"name": disp.Behaviour.TYPES["dock"]}},
                                 {"id": "3", "parameters": {"name": disp.Behaviour.TYPES["wait"]}},
                                 {"id": "4", "parameters": {"name": disp.Behaviour.TYPES["undock"]}},
                                 {"id": "5", "parameters": {"to": "1", "name": disp.Behaviour.TYPES["goto"]}}],
                  "current_behaviour_index": -1,  # index tablicy nie zachowania
                  "status": disp.Task.STATUS_LIST["TO_DO"],
                  "robot": "1",
                  "start_time": "2018-06-29 07:37:27",
                  "weight": 3,
                  "priority": 3
                  },
                 {"id": "2",
                  "behaviours": [{"id": "1", "parameters": {"to": "5", "name": disp.Behaviour.TYPES["goto"]}},
                                 {"id": "2", "parameters": {"name": disp.Behaviour.TYPES["dock"]}},
                                 {"id": "3", "parameters": {"name": disp.Behaviour.TYPES["wait"]}},
                                 {"id": "4", "parameters": {"name": disp.Behaviour.TYPES["undock"]}},
                                 {"id": "5", "parameters": {"to": "1", "name": disp.Behaviour.TYPES["goto"]}}],
                  "current_behaviour_index": -1,  # index tablicy nie zachowania
                  "status": disp.Task.STATUS_LIST["TO_DO"],
                  "robot": "2",
                  "start_time": "2018-06-29 07:27:27",
                  "weight": 4,
                  "priority": 4
                  },
                 {"id": "3",
                  "behaviours": [{"id": "1", "parameters": {"to": "5", "name": disp.Behaviour.TYPES["goto"]}},
                                 {"id": "2", "parameters": {"name": disp.Behaviour.TYPES["dock"]}},
                                 {"id": "3", "parameters": {"name": disp.Behaviour.TYPES["wait"]}},
                                 {"id": "4", "parameters": {"name": disp.Behaviour.TYPES["undock"]}},
                                 {"id": "5", "parameters": {"to": "1", "name": disp.Behaviour.TYPES["goto"]}}],
                  "current_behaviour_index": -1,  # index tablicy nie zachowania
                  "status": disp.Task.STATUS_LIST["TO_DO"],
                  "robot": None,
                  "start_time": "2018-06-29 07:15:27",
                  "weight": 3,
                  "priority": 3
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
                  "start_time": "2018-06-29 07:23:27",
                  "weight": 4,
                  "priority": 4
                  },
                 {"id": "5",
                  "behaviours": [{"id": "1", "parameters": {"to": "5", "name": disp.Behaviour.TYPES["goto"]}},
                                 {"id": "2", "parameters": {"name": disp.Behaviour.TYPES["dock"]}},
                                 {"id": "3", "parameters": {"name": disp.Behaviour.TYPES["wait"]}},
                                 {"id": "4", "parameters": {"name": disp.Behaviour.TYPES["undock"]}},
                                 {"id": "5", "parameters": {"to": "1", "name": disp.Behaviour.TYPES["goto"]}}],
                  "current_behaviour_index": -1,  # index tablicy nie zachowania
                  "status": disp.Task.STATUS_LIST["TO_DO"],
                  "robot": "1",
                  "start_time": "2018-06-29 07:37:27",
                  "weight": 4,
                  "priority": 4
                  },
                 {"id": "6",
                  "behaviours": [{"id": "1", "parameters": {"to": "5", "name": disp.Behaviour.TYPES["goto"]}},
                                 {"id": "2", "parameters": {"name": disp.Behaviour.TYPES["dock"]}},
                                 {"id": "3", "parameters": {"name": disp.Behaviour.TYPES["wait"]}},
                                 {"id": "4", "parameters": {"name": disp.Behaviour.TYPES["undock"]}},
                                 {"id": "5", "parameters": {"to": "1", "name": disp.Behaviour.TYPES["goto"]}}],
                  "current_behaviour_index": -1,  # index tablicy nie zachowania
                  "status": disp.Task.STATUS_LIST["TO_DO"],
                  "robot": "2",
                  "start_time": "2018-06-29 07:27:27",
                  "weight": 4,
                  "priority": 4
                  },
                 {"id": "7",
                  "behaviours": [{"id": "1", "parameters": {"to": "5", "name": disp.Behaviour.TYPES["goto"]}},
                                 {"id": "2", "parameters": {"name": disp.Behaviour.TYPES["dock"]}},
                                 {"id": "3", "parameters": {"name": disp.Behaviour.TYPES["wait"]}},
                                 {"id": "4", "parameters": {"name": disp.Behaviour.TYPES["undock"]}},
                                 {"id": "5", "parameters": {"to": "1", "name": disp.Behaviour.TYPES["goto"]}}],
                  "current_behaviour_index": -1,  # index tablicy nie zachowania
                  "status": disp.Task.STATUS_LIST["TO_DO"],
                  "robot": "3",
                  "start_time": "2018-06-29 07:15:27",
                  "weight": 2,
                  "priority": 2
                  },
                 {"id": "8",
                  "behaviours": [{"id": "1", "parameters": {"to": "5", "name": disp.Behaviour.TYPES["goto"]}},
                                 {"id": "2", "parameters": {"name": disp.Behaviour.TYPES["dock"]}},
                                 {"id": "3", "parameters": {"name": disp.Behaviour.TYPES["wait"]}},
                                 {"id": "4", "parameters": {"name": disp.Behaviour.TYPES["undock"]}},
                                 {"id": "5", "parameters": {"to": "1", "name": disp.Behaviour.TYPES["goto"]}}],
                  "current_behaviour_index": -1,  # index tablicy nie zachowania
                  "status": disp.Task.STATUS_LIST["TO_DO"],
                  "robot": "4",
                  "start_time": "2018-06-29 07:23:27",
                  "weight": 1,
                  "priority": 1
                  },
                 {"id": "9",
                  "behaviours": [{"id": "1", "parameters": {"to": "5", "name": disp.Behaviour.TYPES["goto"]}},
                                 {"id": "2", "parameters": {"name": disp.Behaviour.TYPES["dock"]}},
                                 {"id": "3", "parameters": {"name": disp.Behaviour.TYPES["wait"]}},
                                 {"id": "4", "parameters": {"name": disp.Behaviour.TYPES["undock"]}},
                                 {"id": "5", "parameters": {"to": "1", "name": disp.Behaviour.TYPES["goto"]}}],
                  "current_behaviour_index": -1,  # index tablicy nie zachowania
                  "status": disp.Task.STATUS_LIST["TO_DO"],
                  "robot": None,
                  "start_time": "2018-06-29 07:37:27",
                  "weight": 4,
                  "priority": 4
                  },
                 {"id": "10",
                  "behaviours": [{"id": "1", "parameters": {"to": "5", "name": disp.Behaviour.TYPES["goto"]}},
                                 {"id": "2", "parameters": {"name": disp.Behaviour.TYPES["dock"]}},
                                 {"id": "3", "parameters": {"name": disp.Behaviour.TYPES["wait"]}},
                                 {"id": "4", "parameters": {"name": disp.Behaviour.TYPES["undock"]}},
                                 {"id": "5", "parameters": {"to": "1", "name": disp.Behaviour.TYPES["goto"]}}],
                  "current_behaviour_index": -1,  # index tablicy nie zachowania
                  "status": disp.Task.STATUS_LIST["TO_DO"],
                  "robot": "2",
                  "start_time": "2018-06-29 07:27:27",
                  "weight": 3,
                  "priority": 3
                  },
                 {"id": "11",
                  "behaviours": [{"id": "1", "parameters": {"to": "5", "name": disp.Behaviour.TYPES["goto"]}},
                                 {"id": "2", "parameters": {"name": disp.Behaviour.TYPES["dock"]}},
                                 {"id": "3", "parameters": {"name": disp.Behaviour.TYPES["wait"]}},
                                 {"id": "4", "parameters": {"name": disp.Behaviour.TYPES["undock"]}},
                                 {"id": "5", "parameters": {"to": "1", "name": disp.Behaviour.TYPES["goto"]}}],
                  "current_behaviour_index": -1,  # index tablicy nie zachowania
                  "status": disp.Task.STATUS_LIST["TO_DO"],
                  "robot": "3",
                  "start_time": "2018-06-29 07:15:27",
                  "weight": 1,
                  "priority": 1
                  },
                 {"id": "12",
                  "behaviours": [{"id": "1", "parameters": {"to": "5", "name": disp.Behaviour.TYPES["goto"]}},
                                 {"id": "2", "parameters": {"name": disp.Behaviour.TYPES["dock"]}},
                                 {"id": "3", "parameters": {"name": disp.Behaviour.TYPES["wait"]}},
                                 {"id": "4", "parameters": {"name": disp.Behaviour.TYPES["undock"]}},
                                 {"id": "5", "parameters": {"to": "1", "name": disp.Behaviour.TYPES["goto"]}}],
                  "current_behaviour_index": -1,  # index tablicy nie zachowania
                  "status": disp.Task.STATUS_LIST["TO_DO"],
                  "robot": "4",
                  "start_time": "2018-06-29 07:23:27",
                  "weight": 1,
                  "priority": 1
                  },
                 {"id": "13",
                  "behaviours": [{"id": "1", "parameters": {"to": "5", "name": disp.Behaviour.TYPES["goto"]}},
                                 {"id": "2", "parameters": {"name": disp.Behaviour.TYPES["dock"]}},
                                 {"id": "3", "parameters": {"name": disp.Behaviour.TYPES["wait"]}},
                                 {"id": "4", "parameters": {"name": disp.Behaviour.TYPES["undock"]}},
                                 {"id": "5", "parameters": {"to": "1", "name": disp.Behaviour.TYPES["goto"]}}],
                  "current_behaviour_index": -1,  # index tablicy nie zachowania
                  "status": disp.Task.STATUS_LIST["TO_DO"],
                  "robot": "1",
                  "start_time": "2018-06-29 07:37:27",
                  "weight": 3,
                  "priority": 3
                  },
                 {"id": "14",
                  "behaviours": [{"id": "1", "parameters": {"to": "5", "name": disp.Behaviour.TYPES["goto"]}},
                                 {"id": "2", "parameters": {"name": disp.Behaviour.TYPES["dock"]}},
                                 {"id": "3", "parameters": {"name": disp.Behaviour.TYPES["wait"]}},
                                 {"id": "4", "parameters": {"name": disp.Behaviour.TYPES["undock"]}},
                                 {"id": "5", "parameters": {"to": "1", "name": disp.Behaviour.TYPES["goto"]}}],
                  "current_behaviour_index": -1,  # index tablicy nie zachowania
                  "status": disp.Task.STATUS_LIST["TO_DO"],
                  "robot": "2",
                  "start_time": "2018-06-29 07:27:27",
                  "weight": 3,
                  "priority": 3
                  },
                 {"id": "15",
                  "behaviours": [{"id": "1", "parameters": {"to": "5", "name": disp.Behaviour.TYPES["goto"]}},
                                 {"id": "2", "parameters": {"name": disp.Behaviour.TYPES["dock"]}},
                                 {"id": "3", "parameters": {"name": disp.Behaviour.TYPES["wait"]}},
                                 {"id": "4", "parameters": {"name": disp.Behaviour.TYPES["undock"]}},
                                 {"id": "5", "parameters": {"to": "1", "name": disp.Behaviour.TYPES["goto"]}}],
                  "current_behaviour_index": -1,  # index tablicy nie zachowania
                  "status": disp.Task.STATUS_LIST["TO_DO"],
                  "robot": "7",
                  "start_time": "2018-06-29 07:15:27",
                  "weight": 3,
                  "priority": 3
                  },
                 {"id": "16",
                  "behaviours": [{"id": "1", "parameters": {"to": "5", "name": disp.Behaviour.TYPES["goto"]}},
                                 {"id": "2", "parameters": {"name": disp.Behaviour.TYPES["dock"]}},
                                 {"id": "3", "parameters": {"name": disp.Behaviour.TYPES["wait"]}},
                                 {"id": "4", "parameters": {"name": disp.Behaviour.TYPES["undock"]}},
                                 {"id": "5", "parameters": {"to": "1", "name": disp.Behaviour.TYPES["goto"]}}],
                  "current_behaviour_index": -1,  # index tablicy nie zachowania
                  "status": disp.Task.STATUS_LIST["TO_DO"],
                  "robot": "4",
                  "start_time": "2018-06-29 07:23:27",
                  "weight": 1,
                  "priority": 1
                  },
                 {"id": "17",
                  "behaviours": [{"id": "1", "parameters": {"to": "5", "name": disp.Behaviour.TYPES["goto"]}},
                                 {"id": "2", "parameters": {"name": disp.Behaviour.TYPES["dock"]}},
                                 {"id": "3", "parameters": {"name": disp.Behaviour.TYPES["wait"]}},
                                 {"id": "4", "parameters": {"name": disp.Behaviour.TYPES["undock"]}},
                                 {"id": "5", "parameters": {"to": "1", "name": disp.Behaviour.TYPES["goto"]}}],
                  "current_behaviour_index": -1,  # index tablicy nie zachowania
                  "status": disp.Task.STATUS_LIST["TO_DO"],
                  "robot": "1",
                  "start_time": "2018-06-29 07:37:27",
                  "weight": 3,
                  "priority": 3
                  },
                 {"id": "18",
                  "behaviours": [{"id": "1", "parameters": {"to": "5", "name": disp.Behaviour.TYPES["goto"]}},
                                 {"id": "2", "parameters": {"name": disp.Behaviour.TYPES["dock"]}},
                                 {"id": "3", "parameters": {"name": disp.Behaviour.TYPES["wait"]}},
                                 {"id": "4", "parameters": {"name": disp.Behaviour.TYPES["undock"]}},
                                 {"id": "5", "parameters": {"to": "1", "name": disp.Behaviour.TYPES["goto"]}}],
                  "current_behaviour_index": -1,  # index tablicy nie zachowania
                  "status": disp.Task.STATUS_LIST["TO_DO"],
                  "robot": "2",
                  "start_time": "2018-06-29 07:27:27",
                  "weight": 2,
                  "priority": 2
                  },
                 {"id": "19",
                  "behaviours": [{"id": "1", "parameters": {"to": "5", "name": disp.Behaviour.TYPES["goto"]}},
                                 {"id": "2", "parameters": {"name": disp.Behaviour.TYPES["dock"]}},
                                 {"id": "3", "parameters": {"name": disp.Behaviour.TYPES["wait"]}},
                                 {"id": "4", "parameters": {"name": disp.Behaviour.TYPES["undock"]}},
                                 {"id": "5", "parameters": {"to": "1", "name": disp.Behaviour.TYPES["goto"]}}],
                  "current_behaviour_index": -1,  # index tablicy nie zachowania
                  "status": disp.Task.STATUS_LIST["TO_DO"],
                  "robot": "3",
                  "start_time": "2018-06-29 07:15:27",
                  "weight": 2,
                  "priority": 2
                  },
                 {"id": "20",
                  "behaviours": [{"id": "1", "parameters": {"to": "5", "name": disp.Behaviour.TYPES["goto"]}},
                                 {"id": "2", "parameters": {"name": disp.Behaviour.TYPES["dock"]}},
                                 {"id": "3", "parameters": {"name": disp.Behaviour.TYPES["wait"]}},
                                 {"id": "4", "parameters": {"name": disp.Behaviour.TYPES["undock"]}},
                                 {"id": "5", "parameters": {"to": "1", "name": disp.Behaviour.TYPES["goto"]}}],
                  "current_behaviour_index": -1,  # index tablicy nie zachowania
                  "status": disp.Task.STATUS_LIST["TO_DO"],
                  "robot": "4",
                  "start_time": "2018-06-29 07:23:27",
                  "weight": 2,
                  "priority": 2
                  },
                 ]
    tasks = [disp.Task(data) for data in tasks_raw]
    manager = disp.TasksManager(tasks)
    expected_result = [tasks[3], tasks[8], tasks[2]]
    free_tasks = manager.get_all_unasigned_unstarted_tasks()
    for i in range(len(free_tasks)):
        assert expected_result[i].get_info() == free_tasks[i].get_info()


# ------------------------------ Battery input data ------------------------------ #
@pytest.mark.battery
def test_task_manager_check_if_method_exist():
    battery = disp.Battery()
    assert "get_warning_capacity" in dir(battery)
    assert "get_critical_capacity" in dir(battery)
    assert "get_time_to_warn_allert" in dir(battery)
    assert "get_time_to_critical_allert" in dir(battery)
    assert "is_enough_capacity_before_critical_alert" in dir(battery)

    assert "max_capacity" in dir(battery)
    assert "capacity" in dir(battery)
    assert "drive_usage" in dir(battery)
    assert "stand_usage" in dir(battery)
    assert "remaining_working_time" in dir(battery)


@pytest.mark.battery
def test_get_warning_capacity():
    battery = disp.Battery()
    battery.max_capacity = 40
    battery.drive_usage = 10
    battery.remaining_working_time = 60  # [min]
    assert battery.get_warning_capacity() == 10


@pytest.mark.battery
def test_get_critical_capacity():
    battery = disp.Battery()
    battery.max_capacity = 40
    battery.drive_usage = 10
    battery.remaining_working_time = 60  # [min]
    assert battery.get_critical_capacity() == 5


@pytest.mark.battery
def test_get_time_to_warn_allert():
    battery = disp.Battery()
    battery.max_capacity = 40
    battery.capacity = 40
    battery.drive_usage = 10
    battery.remaining_working_time = 60  # [min]
    assert battery.get_time_to_warn_allert() == 180  # [min]


@pytest.mark.battery
def test_get_time_to_critical_allert():
    battery = disp.Battery()
    battery.max_capacity = 40
    battery.capacity = 40
    battery.drive_usage = 10
    battery.remaining_working_time = 60  # [min]
    assert battery.get_time_to_critical_allert() == 210  # [min]


@pytest.mark.battery
def test_is_enough_capacity_before_critical_alert_true():
    battery = disp.Battery()
    battery.max_capacity = 40
    battery.capacity = 40
    battery.drive_usage = 10
    battery.stand_usage = 5
    battery.remaining_working_time = 60  # [min]
    assert battery.is_enough_capacity_before_critical_alert(180, 20)


@pytest.mark.battery
def test_is_enough_capacity_before_critical_alert_false():
    battery = disp.Battery()
    battery.max_capacity = 40
    battery.capacity = 40
    battery.drive_usage = 10
    battery.stand_usage = 5
    battery.remaining_working_time = 60  # [min]
    assert battery.is_enough_capacity_before_critical_alert(180, 60) is False


# ------------------------------ Robot input data ------------------------------ #
@pytest.mark.robot
def test_robot_check_if_method_exist():
    robot = {"id": "1", "edge": (1, 4), "planningOn": True, "isFree": True, "timeRemaining": 9, "poiId": 1}
    new_robot = disp.Robot(robot)
    assert "validate_input" in dir(new_robot)
    assert "get_current_node" in dir(new_robot)
    assert "check_planning_status" in dir(new_robot)  # TODO testy
    assert "get_current_destination_goal" in dir(new_robot)
    assert "get_info" in dir(new_robot)  # TODO testy

    # atrybuty
    assert "id" in dir(new_robot)
    assert "edge" in dir(new_robot)
    assert "poi_id" in dir(new_robot)
    assert "planning_on" in dir(new_robot)
    assert "is_free" in dir(new_robot)
    assert "time_remaining" in dir(new_robot)
    assert "task" in dir(new_robot)
    assert "next_task_edges" in dir(new_robot)
    assert "end_beh_edge" in dir(new_robot)
    assert "battery" in dir(new_robot)
    assert "swap_time" in dir(new_robot)


@pytest.mark.skip("input_data_validation")
@pytest.mark.robot_input_data
def test_robot_validate_input_throws_exceptions_wrong_data_type():
    robot = "nazwa"
    try:
        disp.Robot(robot)
    except disp.WrongRobotInputData as error:
        assert "Robot input data should be dict but {} was given.".format(type(robot)) == str(error)
    else:
        assert False

    robot = []
    try:
        disp.Robot(robot)
    except disp.WrongRobotInputData as error:
        assert "Robot input data should be dict but {} was given.".format(type(robot)) == str(error)
    else:
        assert False

    robot = 6
    try:
        disp.Robot(robot)
    except disp.WrongRobotInputData as error:
        assert "Robot input data should be dict but {} was given.".format(type(robot)) == str(error)
    else:
        assert False


@pytest.mark.skip("input_data_validation")
@pytest.mark.robot_input_data
def test_robot_validate_input_throws_exceptions_missing_id_param():
    robot = {"edge": (1, 2), "planningOn": True, "isFree": True, "timeRemaining": 0}
    try:
        disp.Robot(robot)
    except disp.WrongRobotInputData as error:
        assert "Robot 'id' param doesn't exist." == str(error)
    else:
        assert False


@pytest.mark.skip("input_data_validation")
@pytest.mark.robot_input_data
def test_robot_validate_input_throws_exceptions_missing_edge_param():
    robot = {"id": "4", "planningOn": True, "isFree": True, "timeRemaining": 0}
    try:
        disp.Robot(robot)
    except disp.WrongRobotInputData as error:
        assert "Robot id: {}. Param 'edge' doesn't exist.".format(robot["id"]) == str(error)
    else:
        assert False


@pytest.mark.skip("input_data_validation")
@pytest.mark.robot_input_data
def test_robot_validate_input_throws_exceptions_missing_planning_on_param():
    robot = {"id": "4", "edge": (1, 2), "isFree": True, "timeRemaining": 0}
    try:
        disp.Robot(robot)
    except disp.WrongRobotInputData as error:
        assert "Robot id: {}. Param 'planningOn' doesn't exist.".format(robot["id"]) == str(error)
    else:
        assert False


@pytest.mark.skip("input_data_validation")
@pytest.mark.robot_input_data
def test_robot_validate_input_throws_exceptions_missing_is_free_param():
    robot = {"id": "4", "edge": (1, 2), "planningOn": True, "timeRemaining": 0}
    try:
        disp.Robot(robot)
    except disp.WrongRobotInputData as error:
        assert "Robot id: {}. Param 'isFree' doesn't exist.".format(robot["id"]) == str(error)
    else:
        assert False


@pytest.mark.skip("input_data_validation")
@pytest.mark.robot_input_data
def test_robot_validate_input_throws_exceptions_missing_time_remaining_param():
    robot = {"id": "4", "edge": (1, 2), "planningOn": True, "isFree": True}
    try:
        disp.Robot(robot)
    except disp.WrongRobotInputData as error:
        assert "Robot id: {}. Param 'timeRemaining' doesn't exist.".format(robot["id"]) == str(error)
    else:
        assert False


@pytest.mark.skip("input_data_validation")
@pytest.mark.robot_input_data
def test_robot_validate_input_throws_exceptions_wrong_id_type():
    robot = {"id": 6, "edge": (1, 2), "planningOn": True, "isFree": True, "timeRemaining": 0}
    type_id = type(robot["id"])
    try:
        disp.Robot(robot)
    except disp.WrongRobotInputData as error:
        assert "Robot id: {}. Param 'id' should be str type but {} was given." \
               "".format(robot["id"], type_id) == str(error)
    else:
        assert False

    robot = {"id": None, "edge": (1, 2), "planningOn": True, "isFree": True, "timeRemaining": 0}
    type_id = type(robot["id"])
    try:
        disp.Robot(robot)
    except disp.WrongRobotInputData as error:
        assert "Robot id: {}. Param 'id' should be str type but {} was given." \
               "".format(robot["id"], type_id) == str(error)
    else:
        assert False


@pytest.mark.skip("input_data_validation")
@pytest.mark.robot_input_data
def test_robot_validate_input_throws_exceptions_wrong_edge_type():
    robot = {"id": "6", "edge": "1", "planningOn": True, "isFree": True, "timeRemaining": 0}
    type_edge = type(robot["edge"])
    try:
        disp.Robot(robot)
    except disp.WrongRobotInputData as error:
        assert "Robot id: {}. Param 'edge' should be tuple or None type but {} was given." \
               "".format(robot["id"], type_edge) == str(error)
    else:
        assert False

    robot = {"id": "6", "edge": 7, "planningOn": True, "isFree": True, "timeRemaining": 0}
    type_edge = type(robot["edge"])
    try:
        disp.Robot(robot)
    except disp.WrongRobotInputData as error:
        assert "Robot id: {}. Param 'edge' should be tuple or None type but {} was given." \
               "".format(robot["id"], type_edge) == str(error)
    else:
        assert False


@pytest.mark.skip("input_data_validation")
@pytest.mark.robot_input_data
def test_robot_validate_input_throws_exceptions_wrong_planning_on_type():
    robot = {"id": "6", "edge": (1, 2), "planningOn": 6, "isFree": True, "timeRemaining": 0}
    type_planning = type(robot["planningOn"])
    try:
        disp.Robot(robot)
    except disp.WrongRobotInputData as error:
        assert "Robot id: {}. Param 'planningOn' should be bool type but {} was given." \
               "".format(robot["id"], type_planning) == str(error)
    else:
        assert False

    robot = {"id": "6", "edge": (1, 2), "planningOn": None, "isFree": True, "timeRemaining": 0}
    type_planning = type(robot["planningOn"])
    try:
        disp.Robot(robot)
    except disp.WrongRobotInputData as error:
        assert "Robot id: {}. Param 'planningOn' should be bool type but {} was given." \
               "".format(robot["id"], type_planning) == str(error)
    else:
        assert False


@pytest.mark.skip("input_data_validation")
@pytest.mark.robot_input_data
def test_robot_validate_input_throws_exceptions_wrong_is_free_type():
    robot = {"id": "6", "edge": (1, 2), "planningOn": True, "isFree": "True", "timeRemaining": 0}
    type_is_free = type(robot["isFree"])
    try:
        disp.Robot(robot)
    except disp.WrongRobotInputData as error:
        assert "Robot id: {}. Param 'isFree' should be bool type but {} was given." \
               "".format(robot["id"], type_is_free) == str(error)
    else:
        assert False

    robot = {"id": "6", "edge": (1, 2), "planningOn": True, "isFree": None, "timeRemaining": 0}
    type_is_free = type(robot["isFree"])
    try:
        disp.Robot(robot)
    except disp.WrongRobotInputData as error:
        assert "Robot id: {}. Param 'isFree' should be bool type but {} was given." \
               "".format(robot["id"], type_is_free) == str(error)
    else:
        assert False


@pytest.mark.skip("input_data_validation")
@pytest.mark.robot_input_data
def test_robot_validate_input_throws_exceptions_wrong_time_remaining_type():
    robot = {"id": "6", "edge": (1, 4), "planningOn": True, "isFree": True, "timeRemaining": "0"}
    type_time = type(robot["timeRemaining"])
    try:
        disp.Robot(robot)
    except disp.WrongRobotInputData as error:
        assert "Robot id: {}. Param 'timeRemaining' should be int or float type but {} was given." \
               "".format(robot["id"], type_time) == str(error)
    else:
        assert False

    robot = {"id": "6", "edge": (1, 4), "planningOn": True, "isFree": True, "timeRemaining": None}
    type_time = type(robot["timeRemaining"])
    try:
        disp.Robot(robot)
    except disp.WrongRobotInputData as error:
        assert "Robot id: {}. Param 'timeRemaining' should be int or float type but {} was given." \
               "".format(robot["id"], type_time) == str(error)
    else:
        assert False


@pytest.mark.robot_input_data
def test_robot_validate_input_valid_data():
    robot = {"id": "1", "edge": (1, 4), "planningOn": True, "isFree": True, "timeRemaining": 9, "poiId": "1"}
    try:
        disp.Robot(robot)
    except disp.WrongRobotInputData as error:
        print(error)
        assert False
    else:
        assert True


# ------------------------------ Robot methods ------------------------------ #
@pytest.mark.robot_input_data
def test_robot_get_current_destination_goal():
    task = {"id": "2",
            "behaviours": [{"id": "1", "parameters": {"to": "7", "name": disp.Behaviour.TYPES["goto"]}},
                           {"id": "2", "parameters": {"name": disp.Behaviour.TYPES["dock"]}},
                           {"id": "3", "parameters": {"name": disp.Behaviour.TYPES["wait"]}},
                           {"id": "4", "parameters": {"name": disp.Behaviour.TYPES["undock"]}}],
            "current_behaviour_index": -1,
            "status": disp.Task.STATUS_LIST["TO_DO"],
            "robot": "1",
            "start_time": "2018-06-29 07:45:27",
            "weight": 2,
            "priority": 2
            }
    robot = {"id": "1", "edge": (1, 4), "planningOn": True, "isFree": True, "timeRemaining": 9, "poiId": 1}

    new_robot = disp.Robot(robot)
    # robot nie ma przypisanego zadania
    assert new_robot.get_current_destination_goal() is None

    # robot ma przypisane zadanie
    new_robot.task = disp.Task(task)
    assert new_robot.task.get_info() == disp.Task(task).get_info()

    # aktualny cel do ktorego jedzie robot lub bedzie jechal to poi id "7"
    assert new_robot.get_current_destination_goal() == "7"

    task = {"id": "5",
            "behaviours": [{"id": "1", "parameters": {"to": "7", "name": disp.Behaviour.TYPES["goto"]}},
                           {"id": "2", "parameters": {"name": disp.Behaviour.TYPES["dock"]}},
                           {"id": "3", "parameters": {"name": disp.Behaviour.TYPES["wait"]}},
                           {"id": "4", "parameters": {"name": disp.Behaviour.TYPES["undock"]}},
                           {"id": "5", "parameters": {"to": "6", "name": disp.Behaviour.TYPES["goto"]}},
                           {"id": "6", "parameters": {"name": disp.Behaviour.TYPES["wait"]}}],
            "current_behaviour_index": 4,
            "status": disp.Task.STATUS_LIST["IN_PROGRESS"],
            "robot": "1",
            "start_time": "2018-06-29 07:45:27",
            "weight": 2,
            "priority": 2
            }
    new_robot.task = disp.Task(task)
    assert new_robot.task.get_info() == disp.Task(task).get_info()
    assert new_robot.get_current_destination_goal() == "6"


@pytest.mark.robot_input_data
def test_robot_get_current_node():
    robot = {"id": "1", "edge": (1, 4), "planningOn": True, "isFree": True, "timeRemaining": 9, "poiId": "1"}
    new_robot = disp.Robot(robot)
    assert robot["edge"][1] == new_robot.get_current_node()

    robot = {"id": "1", "edge": None, "planningOn": True, "isFree": True, "timeRemaining": 9, "poiId": "1"}
    new_robot = disp.Robot(robot)
    assert new_robot.get_current_node() is None


# ------------------------------ RobotsPlanManager ------------------------------ #
@pytest.mark.robots_plan_manager
def test_robots_plan_manager_check_if_method_exist():
    robots_raw = [
        {"id": "1", "edge": (67, 68), "planningOn": True, "isFree": True, "timeRemaining": 0, "poiId": "1"},
        {"id": "2", "edge": (33, 34), "planningOn": True, "isFree": True, "timeRemaining": 0, "poiId": "1"},
        {"id": "3", "edge": (89, 90), "planningOn": False, "isFree": True, "timeRemaining": 0, "poiId": "1"},
        {"id": "4", "edge": (85, 86), "planningOn": True, "isFree": True, "timeRemaining": 0, "poiId": "1"}
    ]
    robots = {robot["id"]: disp.Robot(robot) for robot in robots_raw}
    base_poi_edges = {
        "1": (1, 2),
        "2": (89, 90),
        "3": (20, 30)
    }
    plan_manager = disp.RobotsPlanManager(robots, base_poi_edges)
    assert "set_robots" in dir(plan_manager)
    assert "get_robot_by_id" in dir(plan_manager)
    assert "set_task" in dir(plan_manager)
    assert "check_if_robot_id_exist" in dir(plan_manager)
    assert "set_next_edges" in dir(plan_manager)
    assert "set_end_beh_edge" in dir(plan_manager)
    assert "get_free_robots" in dir(plan_manager)
    assert "get_busy_robots" in dir(plan_manager)
    assert "get_robots_id_on_edge" in dir(plan_manager)
    assert "get_current_robots_goals" in dir(plan_manager)

    assert "robots" in dir(plan_manager)


@pytest.mark.robots_plan_manager
def test_plan_manager_set_robots_only_planning_on():
    robots_raw = [
        {"id": "1", "edge": (67, 68), "planningOn": True, "isFree": True, "timeRemaining": 0, "poiId": "1"},
        {"id": "2", "edge": (33, 34), "planningOn": True, "isFree": True, "timeRemaining": 0, "poiId": "1"},
        {"id": "3", "edge": (89, 90), "planningOn": False, "isFree": True, "timeRemaining": 0, "poiId": "1"},
        {"id": "4", "edge": (85, 86), "planningOn": True, "isFree": True, "timeRemaining": 0, "poiId": "1"}
    ]
    robots = {robot["id"]: disp.Robot(robot) for robot in robots_raw}
    base_poi_edges = {
        "1": (1, 2),
        "2": (89, 90),
        "3": (20, 30)
    }
    plan_manager = disp.RobotsPlanManager(robots, base_poi_edges)
    assert len(plan_manager.robots) == 3  # w trybie planowania tylko 3

    robots = []
    plan_manager = disp.RobotsPlanManager(robots, base_poi_edges)
    assert len(plan_manager.robots) == 0  # w trybie planowania tylko 0


@pytest.mark.robots_plan_manager
def test_plan_manager_set_robots_check_if_edge_is_set():
    # TODO przerobic klase robota, aby mial POI i jesli nie ma krawedzi to na podstawie
    # poi ja okreslic
    pass


@pytest.mark.robots_plan_manager
def test_plan_manager_get_robot_by_id():
    robots_raw = [
        {"id": "1", "edge": (67, 68), "planningOn": True, "isFree": True, "timeRemaining": 0, "poiId": "1"},
        {"id": "2", "edge": (33, 34), "planningOn": True, "isFree": True, "timeRemaining": 0, "poiId": "1"},
        {"id": "3", "edge": (89, 90), "planningOn": True, "isFree": True, "timeRemaining": 0, "poiId": "1"},
        {"id": "4", "edge": (85, 86), "planningOn": True, "isFree": True, "timeRemaining": 0, "poiId": "1"}
    ]
    robots = {robot["id"]: disp.Robot(robot) for robot in robots_raw}
    base_poi_edges = {
        "1": (1, 2),
        "2": (89, 90),
        "3": (20, 30)
    }
    plan_manager = disp.RobotsPlanManager(robots, base_poi_edges)
    assert plan_manager.get_robot_by_id("3").get_info() == disp.Robot(robots_raw[2]).get_info()


@pytest.mark.robots_plan_manager
def test_plan_manager_get_robot_by_id_robot_no_exist():
    robots_raw = [
        {"id": "1", "edge": (67, 68), "planningOn": True, "isFree": True, "timeRemaining": 0, "poiId": "1"},
        {"id": "2", "edge": (33, 34), "planningOn": True, "isFree": True, "timeRemaining": 0, "poiId": "1"},
        {"id": "3", "edge": (89, 90), "planningOn": True, "isFree": True, "timeRemaining": 0, "poiId": "1"},
        {"id": "4", "edge": (85, 86), "planningOn": True, "isFree": True, "timeRemaining": 0, "poiId": "1"}
    ]
    robots = {robot["id"]: disp.Robot(robot) for robot in robots_raw}
    base_poi_edges = {
        "1": (1, 2),
        "2": (89, 90),
        "3": (20, 30)
    }
    plan_manager = disp.RobotsPlanManager(robots, base_poi_edges)
    assert plan_manager.get_robot_by_id("7") is None


@pytest.mark.robots_plan_manager
def test_plan_manager_set_tasks_ok_data():
    robots_raw = [
        {"id": "1", "edge": (67, 68), "planningOn": True, "isFree": True, "timeRemaining": 0, "poiId": "1"},
        {"id": "2", "edge": (33, 34), "planningOn": True, "isFree": True, "timeRemaining": 0, "poiId": "1"},
        {"id": "3", "edge": (89, 90), "planningOn": True, "isFree": True, "timeRemaining": 0, "poiId": "1"},
        {"id": "4", "edge": (85, 86), "planningOn": True, "isFree": True, "timeRemaining": 0, "poiId": "1"}
    ]
    robots = {robot["id"]: disp.Robot(robot) for robot in robots_raw}
    task = {"id": "1",
            "behaviours": [{"id": "1", "parameters": {"to": "7", "name": disp.Behaviour.TYPES["goto"]}},
                           {"id": "2", "parameters": {"name": disp.Behaviour.TYPES["dock"]}},
                           {"id": "3", "parameters": {"name": disp.Behaviour.TYPES["wait"]}},
                           {"id": "4", "parameters": {"name": disp.Behaviour.TYPES["undock"]}}],
            "current_behaviour_index": -1,
            "status": disp.Task.STATUS_LIST["TO_DO"],
            "robot": None,
            "start_time": "2018-06-29 07:15:27",
            "weight": 5
            }
    base_poi_edges = {
        "1": (1, 2),
        "2": (89, 90),
        "3": (20, 30)
    }
    plan_manager = disp.RobotsPlanManager(robots, base_poi_edges)
    plan_manager.set_task("2", disp.Task(task))
    valid_task = disp.Task(task)
    valid_task.robot_id = "2"
    assert valid_task.get_info() == plan_manager.get_robot_by_id("2").task.get_info()


@pytest.mark.robots_plan_manager
def test_plan_manager_set_tasks_ok_data():
    robots_raw = [
        {"id": "1", "edge": (67, 68), "planningOn": True, "isFree": True, "timeRemaining": 0, "poiId": "1"},
        {"id": "2", "edge": (33, 34), "planningOn": True, "isFree": True, "timeRemaining": 0, "poiId": "1"},
        {"id": "3", "edge": (89, 90), "planningOn": True, "isFree": True, "timeRemaining": 0, "poiId": "1"},
        {"id": "4", "edge": (85, 86), "planningOn": True, "isFree": True, "timeRemaining": 0, "poiId": "1"}
    ]
    robots = {robot["id"]: disp.Robot(robot) for robot in robots_raw}
    task = {"id": "1",
            "behaviours": [{"id": "1", "parameters": {"to": "7", "name": disp.Behaviour.TYPES["goto"]}},
                           {"id": "2", "parameters": {"name": disp.Behaviour.TYPES["dock"]}},
                           {"id": "3", "parameters": {"name": disp.Behaviour.TYPES["wait"]}},
                           {"id": "4", "parameters": {"name": disp.Behaviour.TYPES["undock"]}}],
            "current_behaviour_index": -1,
            "status": disp.Task.STATUS_LIST["TO_DO"],
            "robot": None,
            "start_time": "2018-06-29 07:15:27",
            "weight": 5,
            "priority": 5
            }
    base_poi_edges = {
        "1": (1, 2),
        "2": (89, 90),
        "3": (20, 30)
    }
    plan_manager = disp.RobotsPlanManager(robots, base_poi_edges)
    plan_manager.set_task("2", disp.Task(task))
    valid_task = disp.Task(task)
    valid_task.robot_id = "2"
    assert valid_task.get_info() == plan_manager.get_robot_by_id("2").task.get_info()


@pytest.mark.robots_plan_manager
def test_plan_manager_set_tasks_throws_error_when_dispatcher_assigned_tasks_set_to_different_robot():
    robots_raw = [
        {"id": "1", "edge": (67, 68), "planningOn": True, "isFree": True, "timeRemaining": 0, "poiId": "1"},
        {"id": "2", "edge": (33, 34), "planningOn": True, "isFree": True, "timeRemaining": 0, "poiId": "1"},
        {"id": "3", "edge": (89, 90), "planningOn": True, "isFree": True, "timeRemaining": 0, "poiId": "1"},
        {"id": "4", "edge": (85, 86), "planningOn": True, "isFree": True, "timeRemaining": 0, "poiId": "1"}
    ]
    robots = {robot["id"]: disp.Robot(robot) for robot in robots_raw}
    task_data = {"id": "1",
                 "behaviours": [{"id": "1", "parameters": {"to": "7", "name": disp.Behaviour.TYPES["goto"]}},
                                {"id": "2", "parameters": {"name": disp.Behaviour.TYPES["dock"]}},
                                {"id": "3", "parameters": {"name": disp.Behaviour.TYPES["wait"]}},
                                {"id": "4", "parameters": {"name": disp.Behaviour.TYPES["undock"]}}],
                 "current_behaviour_index": -1,
                 "status": disp.Task.STATUS_LIST["TO_DO"],
                 "robot": "1",
                 "start_time": "2018-06-29 07:15:27",
                 "weight": 5,
                 "priority": 5
                 }
    base_poi_edges = {
        "1": (1, 2),
        "2": (89, 90),
        "3": (20, 30)
    }
    plan_manager = disp.RobotsPlanManager(robots, base_poi_edges)
    task = disp.Task(task_data)
    robot_id = "2"
    try:
        plan_manager.set_task(robot_id, disp.Task(task_data))
    except disp.TaskManagerError as error:
        assert "Task is assigned to different robot. Task {} required robot with " \
               "id {} but {} was given.".format(task.id, task.robot_id, robot_id) == str(error)
    else:
        assert False


@pytest.mark.robots_plan_manager
def test_plan_manager_set_tasks_set_root_id_in_task():
    robots_raw = [
        {"id": "1", "edge": (67, 68), "planningOn": True, "isFree": True, "timeRemaining": 0, "poiId": "1"},
        {"id": "2", "edge": (33, 34), "planningOn": True, "isFree": True, "timeRemaining": 0, "poiId": "1"},
        {"id": "3", "edge": (89, 90), "planningOn": True, "isFree": True, "timeRemaining": 0, "poiId": "1"},
        {"id": "4", "edge": (85, 86), "planningOn": True, "isFree": True, "timeRemaining": 0, "poiId": "1"}
    ]
    robots = {robot["id"]: disp.Robot(robot) for robot in robots_raw}
    task = {"id": "1",
            "behaviours": [{"id": "1", "parameters": {"to": "7", "name": disp.Behaviour.TYPES["goto"]}},
                           {"id": "2", "parameters": {"name": disp.Behaviour.TYPES["dock"]}},
                           {"id": "3", "parameters": {"name": disp.Behaviour.TYPES["wait"]}},
                           {"id": "4", "parameters": {"name": disp.Behaviour.TYPES["undock"]}}],
            "current_behaviour_index": -1,
            "status": disp.Task.STATUS_LIST["TO_DO"],
            "robot": None,
            "start_time": "2018-06-29 07:15:27",
            "weight": 5,
            "priority": 5
            }
    base_poi_edges = {
        "1": (1, 2),
        "2": (89, 90),
        "3": (20, 30)
    }
    robot_id = "2"
    plan_manager = disp.RobotsPlanManager(robots, base_poi_edges)
    plan_manager.set_task(robot_id, disp.Task(task))

    assert plan_manager.get_robot_by_id(robot_id).task.robot_id == robot_id


@pytest.mark.robots_plan_manager
def test_plan_manager_set_tasks_invalid_robot_id():
    robots_raw = [
        {"id": "1", "edge": (67, 68), "planningOn": True, "isFree": True, "timeRemaining": 0, "poiId": "1"},
        {"id": "2", "edge": (33, 34), "planningOn": True, "isFree": True, "timeRemaining": 0, "poiId": "1"},
        {"id": "3", "edge": (89, 90), "planningOn": True, "isFree": True, "timeRemaining": 0, "poiId": "1"},
        {"id": "4", "edge": (85, 86), "planningOn": True, "isFree": True, "timeRemaining": 0, "poiId": "1"}
    ]
    robots = {robot["id"]: disp.Robot(robot) for robot in robots_raw}
    task = {"id": "1",
            "behaviours": [{"id": "1", "parameters": {"to": "7", "name": disp.Behaviour.TYPES["goto"]}},
                           {"id": "2", "parameters": {"name": disp.Behaviour.TYPES["dock"]}},
                           {"id": "3", "parameters": {"name": disp.Behaviour.TYPES["wait"]}},
                           {"id": "4", "parameters": {"name": disp.Behaviour.TYPES["undock"]}}],
            "current_behaviour_index": -1,
            "status": disp.Task.STATUS_LIST["TO_DO"],
            "robot": None,
            "start_time": "2018-06-29 07:15:27",
            "weight": 5,
            "priority": 5
            }
    base_poi_edges = {
        "1": (1, 2),
        "2": (89, 90),
        "3": (20, 30)
    }
    robot_id = "7"
    plan_manager = disp.RobotsPlanManager(robots, base_poi_edges)
    try:
        plan_manager.set_task(robot_id, disp.Task(task))
    except disp.TaskManagerError as error:
        assert "Robot on id '{}' doesn't exist".format(robot_id) == str(error)
    else:
        assert False


@pytest.mark.robots_plan_manager
def test_plan_manager_check_if_robot_exist():
    robots_raw = [
        {"id": "1", "edge": (67, 68), "planningOn": True, "isFree": True, "timeRemaining": 0, "poiId": "1"},
        {"id": "2", "edge": (33, 34), "planningOn": True, "isFree": True, "timeRemaining": 0, "poiId": "1"},
        {"id": "3", "edge": (89, 90), "planningOn": True, "isFree": True, "timeRemaining": 0, "poiId": "1"},
        {"id": "4", "edge": (85, 86), "planningOn": True, "isFree": True, "timeRemaining": 0, "poiId": "1"}
    ]
    robots = {robot["id"]: disp.Robot(robot) for robot in robots_raw}
    base_poi_edges = {
        "1": (1, 2),
        "2": (89, 90),
        "3": (20, 30)
    }
    plan_manager = disp.RobotsPlanManager(robots, base_poi_edges)
    assert plan_manager.check_if_robot_id_exist("1")
    assert not plan_manager.check_if_robot_id_exist("7")


@pytest.mark.robots_plan_manager
def test_plan_manager_set_next_edges():
    robots_raw = [
        {"id": "1", "edge": (67, 68), "planningOn": True, "isFree": True, "timeRemaining": 0, "poiId": "1"},
        {"id": "2", "edge": (33, 34), "planningOn": True, "isFree": True, "timeRemaining": 0, "poiId": "1"},
        {"id": "3", "edge": (89, 90), "planningOn": True, "isFree": True, "timeRemaining": 0, "poiId": "1"},
        {"id": "4", "edge": (85, 86), "planningOn": True, "isFree": True, "timeRemaining": 0, "poiId": "1"}
    ]
    robots = {robot["id"]: disp.Robot(robot) for robot in robots_raw}
    task = {"id": "1",
            "behaviours": [{"id": "1", "parameters": {"to": "7", "name": disp.Behaviour.TYPES["goto"]}},
                           {"id": "2", "parameters": {"name": disp.Behaviour.TYPES["dock"]}},
                           {"id": "3", "parameters": {"name": disp.Behaviour.TYPES["wait"]}},
                           {"id": "4", "parameters": {"name": disp.Behaviour.TYPES["undock"]}}],
            "current_behaviour_index": -1,
            "status": disp.Task.STATUS_LIST["TO_DO"],
            "robot": None,
            "start_time": "2018-06-29 07:15:27",
            "weight": 5,
            "priority": 5
            }
    base_poi_edges = {
        "1": (1, 2),
        "2": (89, 90),
        "3": (20, 30)
    }
    robot_id = "2"
    set_edges = [(3, 4)]
    plan_manager = disp.RobotsPlanManager(robots, base_poi_edges)
    plan_manager.set_task(robot_id, disp.Task(task))
    plan_manager.set_next_edges(robot_id, [set_edges])
    assert plan_manager.get_robot_by_id(robot_id).next_task_edges == [set_edges]


@pytest.mark.robots_plan_manager
def test_plan_manager_set_next_edge_invalid_robot_id():
    robots_raw = [
        {"id": "1", "edge": (67, 68), "planningOn": True, "isFree": True, "timeRemaining": 0, "poiId": "1"},
        {"id": "2", "edge": (33, 34), "planningOn": True, "isFree": True, "timeRemaining": 0, "poiId": "1"},
        {"id": "3", "edge": (89, 90), "planningOn": True, "isFree": True, "timeRemaining": 0, "poiId": "1"},
        {"id": "4", "edge": (85, 86), "planningOn": True, "isFree": True, "timeRemaining": 0, "poiId": "1"}
    ]
    robots = {robot["id"]: disp.Robot(robot) for robot in robots_raw}
    task = {"id": "1",
            "behaviours": [{"id": "1", "parameters": {"to": "7", "name": disp.Behaviour.TYPES["goto"]}},
                           {"id": "2", "parameters": {"name": disp.Behaviour.TYPES["dock"]}},
                           {"id": "3", "parameters": {"name": disp.Behaviour.TYPES["wait"]}},
                           {"id": "4", "parameters": {"name": disp.Behaviour.TYPES["undock"]}}],
            "current_behaviour_index": -1,
            "status": disp.Task.STATUS_LIST["TO_DO"],
            "robot": None,
            "start_time": "2018-06-29 07:15:27",
            "weight": 5,
            "priority": 5
            }
    base_poi_edges = {
        "1": (1, 2),
        "2": (89, 90),
        "3": (20, 30)
    }
    robot_id = "2"
    set_edge = [(3, 4)]
    plan_manager = disp.RobotsPlanManager(robots, base_poi_edges)
    plan_manager.set_task(robot_id, disp.Task(task))
    try:
        plan_manager.set_next_edges("7", [set_edge])
    except disp.TaskManagerError as error:
        assert "Robot on id '{}' doesn't exist".format("7") == str(error)
    else:
        assert False


@pytest.mark.robots_plan_manager
def test_plan_manager_set_next_edge_throws_except_when_robot_get_next_edge_but_dosent_have_task():
    robots_raw = [
        {"id": "1", "edge": (67, 68), "planningOn": True, "isFree": True, "timeRemaining": 0, "poiId": "1"},
        {"id": "2", "edge": (33, 34), "planningOn": True, "isFree": True, "timeRemaining": 0, "poiId": "1"},
        {"id": "3", "edge": (89, 90), "planningOn": True, "isFree": True, "timeRemaining": 0, "poiId": "1"},
        {"id": "4", "edge": (85, 86), "planningOn": True, "isFree": True, "timeRemaining": 0, "poiId": "1"}
    ]
    robots = {robot["id"]: disp.Robot(robot) for robot in robots_raw}
    base_poi_edges = {
        "1": (1, 2),
        "2": (89, 90),
        "3": (20, 30)
    }
    robot_id = "2"
    set_edge = [(3, 4)]
    plan_manager = disp.RobotsPlanManager(robots, base_poi_edges)
    try:
        plan_manager.set_next_edges(robot_id, [set_edge])
    except disp.TaskManagerError as error:
        assert "Can not assign next edge when robot {} doesn't have task.".format(robot_id) == str(error)
    else:
        assert False


@pytest.mark.robots_plan_manager
def test_plan_manager_set_end_beh_edge():
    robots_raw = [
        {"id": "1", "edge": (67, 68), "planningOn": True, "isFree": True, "timeRemaining": 0, "poiId": "1"},
        {"id": "2", "edge": (33, 34), "planningOn": True, "isFree": True, "timeRemaining": 0, "poiId": "1"},
        {"id": "3", "edge": (89, 90), "planningOn": True, "isFree": True, "timeRemaining": 0, "poiId": "1"},
        {"id": "4", "edge": (85, 86), "planningOn": True, "isFree": True, "timeRemaining": 0, "poiId": "1"}
    ]
    robots = {robot["id"]: disp.Robot(robot) for robot in robots_raw}
    task = {"id": "1",
            "behaviours": [{"id": "1", "parameters": {"to": "7", "name": disp.Behaviour.TYPES["goto"]}},
                           {"id": "2", "parameters": {"name": disp.Behaviour.TYPES["dock"]}},
                           {"id": "3", "parameters": {"name": disp.Behaviour.TYPES["wait"]}},
                           {"id": "4", "parameters": {"name": disp.Behaviour.TYPES["undock"]}}],
            "current_behaviour_index": -1,
            "status": disp.Task.STATUS_LIST["TO_DO"],
            "robot": None,
            "start_time": "2018-06-29 07:15:27",
            "weight": 5,
            "priority": 2
            }
    base_poi_edges = {
        "1": (1, 2),
        "2": (89, 90),
        "3": (20, 30)
    }
    robot_id = "2"
    set_edge = [(3, 4)]
    plan_manager = disp.RobotsPlanManager(robots, base_poi_edges)
    plan_manager.set_task(robot_id, disp.Task(task))
    plan_manager.set_next_edges(robot_id, set_edge)
    plan_manager.set_end_beh_edge(robot_id, True)
    assert plan_manager.get_robot_by_id(robot_id).end_beh_edge


@pytest.mark.robots_plan_manager
def test_plan_manager_set_end_beh_edge_invalid_robot_id():
    robots_raw = [
        {"id": "1", "edge": (67, 68), "planningOn": True, "isFree": True, "timeRemaining": 0, "poiId": "1"},
        {"id": "2", "edge": (33, 34), "planningOn": True, "isFree": True, "timeRemaining": 0, "poiId": "1"},
        {"id": "3", "edge": (89, 90), "planningOn": True, "isFree": True, "timeRemaining": 0, "poiId": "1"},
        {"id": "4", "edge": (85, 86), "planningOn": True, "isFree": True, "timeRemaining": 0, "poiId": "1"}
    ]
    robots = {robot["id"]: disp.Robot(robot) for robot in robots_raw}
    task = {"id": "1",
            "behaviours": [{"id": "1", "parameters": {"to": "7", "name": disp.Behaviour.TYPES["goto"]}},
                           {"id": "2", "parameters": {"name": disp.Behaviour.TYPES["dock"]}},
                           {"id": "3", "parameters": {"name": disp.Behaviour.TYPES["wait"]}},
                           {"id": "4", "parameters": {"name": disp.Behaviour.TYPES["undock"]}}],
            "current_behaviour_index": -1,
            "status": disp.Task.STATUS_LIST["TO_DO"],
            "robot": None,
            "start_time": "2018-06-29 07:15:27",
            "weight": 5,
            "priority": 5
            }
    base_poi_edges = {
        "1": (1, 2),
        "2": (89, 90),
        "3": (20, 30)
    }
    robot_id = "2"
    set_end_beh_edge = False
    plan_manager = disp.RobotsPlanManager(robots, base_poi_edges)
    plan_manager.set_task(robot_id, disp.Task(task))
    try:
        plan_manager.set_end_beh_edge("7", set_end_beh_edge)
    except disp.TaskManagerError as error:
        assert "Robot on id '{}' doesn't exist".format("7") == str(error)
    else:
        assert False


@pytest.mark.robots_plan_manager
def test_plan_manager_set_end_beh_edge_throws_except_when_robot_get_next_edge_but_dosent_have_task():
    robots_raw = [
        {"id": "1", "edge": (67, 68), "planningOn": True, "isFree": True, "timeRemaining": 0, "poiId": "1"},
        {"id": "2", "edge": (33, 34), "planningOn": True, "isFree": True, "timeRemaining": 0, "poiId": "1"},
        {"id": "3", "edge": (89, 90), "planningOn": True, "isFree": True, "timeRemaining": 0, "poiId": "1"},
        {"id": "4", "edge": (85, 86), "planningOn": True, "isFree": True, "timeRemaining": 0, "poiId": "1"}
    ]
    robots = {robot["id"]: disp.Robot(robot) for robot in robots_raw}
    base_poi_edges = {
        "1": (1, 2),
        "2": (89, 90),
        "3": (20, 30)
    }
    robot_id = "2"
    plan_manager = disp.RobotsPlanManager(robots, base_poi_edges)
    try:
        plan_manager.set_end_beh_edge(robot_id, True)
    except disp.TaskManagerError as error:
        assert "Can not set end behaviour edge when robot {} doesn't have task.".format(robot_id) == str(error)
    else:
        assert False


@pytest.mark.robots_plan_manager
def test_plan_manager_set_end_beh_edge_throws_except_when_robot_get_next_edge_but_dosent_have_task():
    robots_raw = [
        {"id": "1", "edge": (67, 68), "planningOn": True, "isFree": True, "timeRemaining": 0, "poiId": "1"},
        {"id": "2", "edge": (33, 34), "planningOn": True, "isFree": True, "timeRemaining": 0, "poiId": "1"},
        {"id": "3", "edge": (89, 90), "planningOn": True, "isFree": True, "timeRemaining": 0, "poiId": "1"},
        {"id": "4", "edge": (85, 86), "planningOn": True, "isFree": True, "timeRemaining": 0, "poiId": "1"}
    ]
    robots = {robot["id"]: disp.Robot(robot) for robot in robots_raw}
    task = {"id": "1",
            "behaviours": [{"id": "1", "parameters": {"to": "7", "name": disp.Behaviour.TYPES["goto"]}},
                           {"id": "2", "parameters": {"name": disp.Behaviour.TYPES["dock"]}},
                           {"id": "3", "parameters": {"name": disp.Behaviour.TYPES["wait"]}},
                           {"id": "4", "parameters": {"name": disp.Behaviour.TYPES["undock"]}}],
            "current_behaviour_index": -1,
            "status": disp.Task.STATUS_LIST["TO_DO"],
            "robot": None,
            "start_time": "2018-06-29 07:15:27",
            "weight": 5,
            "priority": 5
            }
    base_poi_edges = {
        "1": (1, 2),
        "2": (89, 90),
        "3": (20, 30)
    }
    robot_id = "2"
    plan_manager = disp.RobotsPlanManager(robots, base_poi_edges)
    plan_manager.set_task(robot_id, disp.Task(task))
    try:
        plan_manager.set_end_beh_edge(robot_id, True)
    except disp.TaskManagerError as error:
        assert "Can not set end behaviour edge when robot {} doesn't have next_task_edge." \
               "".format(robot_id) == str(error)
    else:
        assert False


@pytest.mark.robots_plan_manager
def test_plan_manager_get_free_robots():
    # zestaw 1
    robots_raw = [
        {"id": "1", "edge": (67, 68), "planningOn": True, "isFree": True, "timeRemaining": 0, "poiId": "1"},
        {"id": "2", "edge": (33, 34), "planningOn": False, "isFree": True, "timeRemaining": 0, "poiId": "1"},
        {"id": "3", "edge": (89, 90), "planningOn": True, "isFree": True, "timeRemaining": 0, "poiId": "1"},
        {"id": "4", "edge": (85, 86), "planningOn": True, "isFree": True, "timeRemaining": 0, "poiId": "1"}
    ]
    robots = {robot["id"]: disp.Robot(robot) for robot in robots_raw}
    free_input_robots = ["1", "3", "4"]
    base_poi_edges = {
        "1": (1, 2),
        "2": (89, 90),
        "3": (20, 30)
    }
    plan_manager = disp.RobotsPlanManager(robots, base_poi_edges)
    free_robots = plan_manager.get_free_robots()
    assert len(free_robots) == 3
    for robot in free_robots:
        assert robot.id in free_input_robots

    # zestaw 2
    robots_raw = [
        {"id": "1", "edge": (67, 68), "planningOn": True, "isFree": True, "timeRemaining": 0, "poiId": "1"},
        {"id": "2", "edge": (33, 34), "planningOn": True, "isFree": True, "timeRemaining": 0, "poiId": "1"},
        {"id": "3", "edge": (89, 90), "planningOn": True, "isFree": True, "timeRemaining": 0, "poiId": "1"},
        {"id": "4", "edge": (85, 86), "planningOn": True, "isFree": True, "timeRemaining": 0, "poiId": "1"}
    ]
    robots = {robot["id"]: disp.Robot(robot) for robot in robots_raw}
    free_input_robots = ["1", "2", "3", "4"]
    base_poi_edges = {
        "1": (1, 2),
        "2": (89, 90),
        "3": (20, 30)
    }
    plan_manager = disp.RobotsPlanManager(robots, base_poi_edges)
    free_robots = plan_manager.get_free_robots()
    assert len(free_robots) == 4
    for robot in free_robots:
        assert robot.id in free_input_robots

    # zestaw 3
    robots_raw = [
        {"id": "1", "edge": (67, 68), "planningOn": True, "isFree": True, "timeRemaining": 0, "poiId": "1"},
        {"id": "2", "edge": (33, 34), "planningOn": True, "isFree": True, "timeRemaining": 0, "poiId": "1"},
        {"id": "3", "edge": (89, 90), "planningOn": True, "isFree": True, "timeRemaining": 0, "poiId": "1"},
        {"id": "4", "edge": (85, 86), "planningOn": True, "isFree": True, "timeRemaining": 0, "poiId": "1"}
    ]
    robots = {robot["id"]: disp.Robot(robot) for robot in robots_raw}
    task1 = disp.Task({"id": "1",
                       "behaviours": [{"id": "1", "parameters": {"to": "7", "name": disp.Behaviour.TYPES["goto"]}},
                                      {"id": "2", "parameters": {"name": disp.Behaviour.TYPES["dock"]}},
                                      {"id": "3", "parameters": {"name": disp.Behaviour.TYPES["wait"]}},
                                      {"id": "4", "parameters": {"name": disp.Behaviour.TYPES["undock"]}}],
                       "current_behaviour_index": -1,
                       "status": disp.Task.STATUS_LIST["TO_DO"],
                       "robot": None,
                       "start_time": "2018-06-29 07:15:27",
                       "weight": 5,
                       "priority": 5
                       })
    task2 = disp.Task({"id": "2",
                       "behaviours": [{"id": "1", "parameters": {"to": "7", "name": disp.Behaviour.TYPES["goto"]}},
                                      {"id": "2", "parameters": {"name": disp.Behaviour.TYPES["dock"]}},
                                      {"id": "3", "parameters": {"name": disp.Behaviour.TYPES["wait"]}},
                                      {"id": "4", "parameters": {"name": disp.Behaviour.TYPES["undock"]}}],
                       "current_behaviour_index": -1,
                       "status": disp.Task.STATUS_LIST["TO_DO"],
                       "robot": None,
                       "start_time": "2018-06-29 07:15:27",
                       "weight": 5,
                       "priority": 5
                       })
    free_input_robots = ["1", "3"]
    base_poi_edges = {
        "1": (1, 2),
        "2": (89, 90),
        "3": (20, 30)
    }
    plan_manager = disp.RobotsPlanManager(robots, base_poi_edges)
    plan_manager.set_task("4", task1)
    plan_manager.set_task("2", task2)
    free_robots = plan_manager.get_free_robots()
    assert len(free_robots) == 2
    for robot in free_robots:
        assert robot.id in free_input_robots


@pytest.mark.robots_plan_manager
def test_plan_manager_get_busy_robots():
    robots_raw = [
        {"id": "1", "edge": (67, 68), "planningOn": True, "isFree": True, "timeRemaining": 0, "poiId": "1"},
        {"id": "2", "edge": (33, 34), "planningOn": True, "isFree": True, "timeRemaining": 0, "poiId": "1"},
        {"id": "3", "edge": (89, 90), "planningOn": True, "isFree": True, "timeRemaining": 0, "poiId": "1"},
        {"id": "4", "edge": (85, 86), "planningOn": True, "isFree": True, "timeRemaining": 0, "poiId": "1"}
    ]
    robots = {robot["id"]: disp.Robot(robot) for robot in robots_raw}
    task1 = disp.Task({"id": "1",
                       "behaviours": [{"id": "1", "parameters": {"to": "7", "name": disp.Behaviour.TYPES["goto"]}},
                                      {"id": "2", "parameters": {"name": disp.Behaviour.TYPES["dock"]}},
                                      {"id": "3", "parameters": {"name": disp.Behaviour.TYPES["wait"]}},
                                      {"id": "4", "parameters": {"name": disp.Behaviour.TYPES["undock"]}}],
                       "current_behaviour_index": -1,
                       "status": disp.Task.STATUS_LIST["TO_DO"],
                       "robot": None,
                       "start_time": "2018-06-29 07:15:27",
                       "weight": 5,
                       "priority": 5
                       })
    task2 = disp.Task({"id": "2",
                       "behaviours": [{"id": "1", "parameters": {"to": "7", "name": disp.Behaviour.TYPES["goto"]}},
                                      {"id": "2", "parameters": {"name": disp.Behaviour.TYPES["dock"]}},
                                      {"id": "3", "parameters": {"name": disp.Behaviour.TYPES["wait"]}},
                                      {"id": "4", "parameters": {"name": disp.Behaviour.TYPES["undock"]}}],
                       "current_behaviour_index": -1,
                       "status": disp.Task.STATUS_LIST["TO_DO"],
                       "robot": None,
                       "start_time": "2018-06-29 07:15:27",
                       "weight": 5,
                       "priority": 5
                       })
    busy_robots = ["2", "4"]
    base_poi_edges = {
        "1": (1, 2),
        "2": (89, 90),
        "3": (20, 30)
    }
    plan_manager = disp.RobotsPlanManager(robots, base_poi_edges)
    plan_manager.set_task("4", task1)
    plan_manager.set_task("2", task2)
    for robot in plan_manager.get_busy_robots():
        assert robot.id in busy_robots


@pytest.mark.robots_plan_manager
def test_plan_manager_get_robots_id_on_edge():
    robots_raw = [
        {"id": "1", "edge": (1, 2), "planningOn": True, "isFree": True, "timeRemaining": 0, "poiId": "1"},
        {"id": "2", "edge": (3, 4), "planningOn": True, "isFree": True, "timeRemaining": 0, "poiId": "1"},
        {"id": "3", "edge": (8, 9), "planningOn": True, "isFree": True, "timeRemaining": 0, "poiId": "1"},
        {"id": "4", "edge": (1, 2), "planningOn": True, "isFree": True, "timeRemaining": 0, "poiId": "1"},
        {"id": "5", "edge": (8, 9), "planningOn": True, "isFree": True, "timeRemaining": 0, "poiId": "1"},
        {"id": "6", "edge": (33, 34), "planningOn": True, "isFree": True, "timeRemaining": 0, "poiId": "1"},
        {"id": "7", "edge": (5, 6), "planningOn": True, "isFree": True, "timeRemaining": 0, "poiId": "1"},
        {"id": "8", "edge": (67, 68), "planningOn": True, "isFree": True, "timeRemaining": 0, "poiId": "1"},
        {"id": "9", "edge": (33, 34), "planningOn": True, "isFree": True, "timeRemaining": 0, "poiId": "1"},
        {"id": "10", "edge": (1, 2), "planningOn": True, "isFree": True, "timeRemaining": 0, "poiId": "1"},
        {"id": "11", "edge": (15, 16), "planningOn": True, "isFree": True, "timeRemaining": 0, "poiId": "1"},
        {"id": "12", "edge": (33, 34), "planningOn": True, "isFree": True, "timeRemaining": 0, "poiId": "1"},
        {"id": "13", "edge": (13, 14), "planningOn": True, "isFree": True, "timeRemaining": 0, "poiId": "1"}
    ]
    robots = {robot["id"]: disp.Robot(robot) for robot in robots_raw}
    base_poi_edges = {
        "1": (1, 2),
        "2": (89, 90),
        "3": (20, 30)
    }
    plan_manager = disp.RobotsPlanManager(robots, base_poi_edges)
    given_edge = (8, 9)
    robots_id = [robot["id"] for robot in robots_raw if robot["edge"] == given_edge]
    given_robots = plan_manager.get_robots_id_on_edge(given_edge)
    assert len(robots_id) == len(given_robots)
    for robot in given_robots:
        assert robot in robots_id


@pytest.mark.robots_plan_manager
def test_plan_manager_get_current_robots_goals():
    robots_raw = [
        {"id": "1", "edge": (1, 2), "planningOn": True, "isFree": True, "timeRemaining": 0, "poiId": "1"},
        {"id": "2", "edge": (3, 4), "planningOn": True, "isFree": True, "timeRemaining": 0, "poiId": "1"},
        {"id": "3", "edge": (8, 9), "planningOn": True, "isFree": True, "timeRemaining": 0, "poiId": "1"},
        {"id": "4", "edge": (1, 2), "planningOn": True, "isFree": True, "timeRemaining": 0, "poiId": "1"},
        {"id": "5", "edge": (8, 9), "planningOn": True, "isFree": True, "timeRemaining": 0, "poiId": "1"},
        {"id": "6", "edge": (33, 34), "planningOn": True, "isFree": True, "timeRemaining": 0, "poiId": "1"},
        {"id": "7", "edge": (5, 6), "planningOn": True, "isFree": True, "timeRemaining": 0, "poiId": "1"},
        {"id": "8", "edge": (67, 68), "planningOn": True, "isFree": True, "timeRemaining": 0, "poiId": "1"},
        {"id": "9", "edge": (33, 34), "planningOn": True, "isFree": True, "timeRemaining": 0, "poiId": "1"},
        {"id": "10", "edge": (1, 2), "planningOn": True, "isFree": True, "timeRemaining": 0, "poiId": "1"},
        {"id": "11", "edge": (15, 16), "planningOn": True, "isFree": True, "timeRemaining": 0, "poiId": "1"},
        {"id": "12", "edge": (33, 34), "planningOn": True, "isFree": True, "timeRemaining": 0, "poiId": "1"},
        {"id": "13", "edge": (13, 14), "planningOn": True, "isFree": True, "timeRemaining": 0, "poiId": "1"}
    ]
    robots = {robot["id"]: disp.Robot(robot) for robot in robots_raw}
    pois = ["4", "6", "8", "10"]
    pois_id = []
    for a in range(len(robots_raw)):
        pois_id.append(pois[random.randint(0, 3)])
    tasks = []
    for i in range(len(robots_raw)):
        tasks.append(disp.Task({"id": str(i),
                                "behaviours": [{"id": "1", "parameters": {"to": pois_id[i],
                                                                          "name": disp.Behaviour.TYPES["goto"]}},
                                               {"id": "2", "parameters": {"name": disp.Behaviour.TYPES["dock"]}},
                                               {"id": "3", "parameters": {"name": disp.Behaviour.TYPES["wait"]}},
                                               {"id": "4", "parameters": {"name": disp.Behaviour.TYPES["undock"]}}],
                                "current_behaviour_index": -1,
                                "status": disp.Task.STATUS_LIST["TO_DO"],
                                "robot": None,
                                "start_time": "2018-06-29 07:15:27",
                                "weight": 5,
                                "priority": 5}))

    base_poi_edges = {
        "1": (1, 2),
        "2": (89, 90),
        "3": (20, 30)
    }
    plan_manager = disp.RobotsPlanManager(robots, base_poi_edges)
    for i, robot in enumerate(robots_raw):
        plan_manager.set_task(robot["id"], tasks[i])

    expected_result = {}
    for i in range(len(robots_raw)):
        expected_result[robots_raw[i]["id"]] = pois_id[i]

    assert expected_result == plan_manager.get_current_robots_goals()

    # Niektore roboty nie maja zadan
    robots_raw = [
        {"id": "1", "edge": (1, 2), "planningOn": True, "isFree": True, "timeRemaining": 0, "poiId": "1"},
        {"id": "2", "edge": (3, 4), "planningOn": True, "isFree": True, "timeRemaining": 0, "poiId": "1"},
        {"id": "3", "edge": (8, 9), "planningOn": True, "isFree": True, "timeRemaining": 0, "poiId": "1"},
        {"id": "4", "edge": (1, 2), "planningOn": True, "isFree": True, "timeRemaining": 0, "poiId": "1"},
        {"id": "5", "edge": (8, 9), "planningOn": True, "isFree": True, "timeRemaining": 0, "poiId": "1"},
        {"id": "6", "edge": (33, 34), "planningOn": True, "isFree": True, "timeRemaining": 0, "poiId": "1"},
        {"id": "7", "edge": (5, 6), "planningOn": True, "isFree": True, "timeRemaining": 0, "poiId": "1"},
        {"id": "8", "edge": (67, 68), "planningOn": True, "isFree": True, "timeRemaining": 0, "poiId": "1"},
        {"id": "9", "edge": (33, 34), "planningOn": True, "isFree": True, "timeRemaining": 0, "poiId": "1"},
        {"id": "10", "edge": (1, 2), "planningOn": True, "isFree": True, "timeRemaining": 0, "poiId": "1"},
        {"id": "11", "edge": (15, 16), "planningOn": True, "isFree": True, "timeRemaining": 0, "poiId": "1"},
        {"id": "12", "edge": (33, 34), "planningOn": True, "isFree": True, "timeRemaining": 0, "poiId": "1"},
        {"id": "13", "edge": (13, 14), "planningOn": True, "isFree": True, "timeRemaining": 0, "poiId": "1"}
    ]
    robots = {robot["id"]: disp.Robot(robot) for robot in robots_raw}
    pois = ["4", "6", "8", None]
    pois_id = []
    for a in range(len(robots_raw)):
        pois_id.append(pois[random.randint(0, 3)])
    base_poi_edges = {
        "1": (1, 2),
        "2": (89, 90),
        "3": (20, 30)
    }
    plan_manager = disp.RobotsPlanManager(robots, base_poi_edges)
    for i in range(len(robots_raw)):
        poi_id = pois_id[i]
        if poi_id is not None:
            task = disp.Task({"id": str(i),
                              "behaviours": [{"id": "1", "parameters": {"to": poi_id,
                                                                        "name": disp.Behaviour.TYPES["goto"]}},
                                             {"id": "2", "parameters": {"name": disp.Behaviour.TYPES["dock"]}},
                                             {"id": "3", "parameters": {"name": disp.Behaviour.TYPES["wait"]}},
                                             {"id": "4", "parameters": {"name": disp.Behaviour.TYPES["undock"]}}],
                              "current_behaviour_index": -1,
                              "status": disp.Task.STATUS_LIST["TO_DO"],
                              "robot": None,
                              "start_time": "2018-06-29 07:15:27",
                              "weight": 5,
                              "priority": 5})
            plan_manager.set_task(robots_raw[i]["id"], task)

    expected_result = {}
    for i in range(len(robots_raw)):
        if pois_id[i] is not None:
            expected_result[robots_raw[i]["id"]] = pois_id[i]

    assert expected_result == plan_manager.get_current_robots_goals()
