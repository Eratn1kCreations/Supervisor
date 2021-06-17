# -*- coding: utf-8 -*-
import copy
import networkx as nx
import graph_creator as gc
import numpy as np
import time
from datetime import datetime, timedelta


class DispatcherError(Exception):
    """Base class for exceptions in this module."""
    pass


class TimeoutPlanning(DispatcherError):
    """Planning timeout passed."""
    pass


class WrongData(DispatcherError):
    """Wrong data"""


class WrongBehaviourInputData(WrongData):
    """Wrong behaviour input data"""


class WrongTaskInputData(WrongData):
    """Wrong task input data"""


class WrongRobotInputData(WrongData):
    """Wrong robot input data"""


class TaskManagerError(DispatcherError):
    """Task manager error"""


class PoisManagerError(DispatcherError):
    """Pois manager error"""


class PlaningGraphError(DispatcherError):
    """Planing graph error"""


class Behaviour:
    """
    Klasa zawierajaca informacje o pojedynczym zachowaniu dla robota

    Attributes:
        id (string): id zachowania dla robota w ramach zadania
        parameters (dict): slownik z parametrami dla robota, moze sie roznic w zaleznosci od typu zachowania
    """
    PARAM = {
        "ID": "id",  # nazwa id zachowania w bazie
        "BEH_PARAM": "parameters",  # nazwa pola zawierajacego liste parametrow
        "TYPE": "name",  # nazwa typu zachowania
        "BEH_POI": "to"  # nazwa pola, ktore odnosi sie do celu (POI)
    }
    TYPES = {  # slownik wartosci zachowan dla robota, wartoscia jest stala nazwa dla danego typu zachowania
        "goto": "GO_TO",
        "dock": "DOCK",
        "wait": "WAIT",
        "bat_ex": "BAT_EX",
        "undock": "UNDOCK",
        "msg": "MSG"
    }

    def __init__(self, behaviour_data):
        """
        Parameters:
            behaviour_data (dict): slownik z parametrami zachowania
                dict {"id" string: , "parameters": {"name": Behaviour.TYPES[nazwa_typu], "to": "id_poi"})
        """
        self.validate_data(behaviour_data)
        self.id = behaviour_data[self.PARAM["ID"]]
        self.parameters = behaviour_data[self.PARAM["BEH_PARAM"]]

    def __getitem__(self, key):
        return self.parameters[key]

    def __contains__(self, key):
        return key in self.parameters

    def get_type(self):
        """
        Returns:
            (string): typ zachowania
        """
        return self.parameters[self.PARAM["TYPE"]]

    def check_if_go_to(self):
        """
        Returns:
            (bool): informacja o tym czy zachowanie jest typu GO TO
        """
        return self.parameters[self.PARAM["TYPE"]] == self.TYPES["goto"]

    def get_poi(self):
        """
        Returns:
             (string): zawiera informacje z id POI dla zachowania GO TO, a dla pozostalych wartosc None
        """
        if self.check_if_go_to():
            return self.parameters[self.PARAM["BEH_POI"]]
        else:
            return None

    def validate_data(self, behaviour_data):
        """
        Parameters:
            behaviour_data (dict): slownik z parametrami zachowania
                dict {"id" string: , "parameters": {"name": Behaviour.TYPES[nazwa_typu], "to": "id_poi"})
        """
        beh_type = type(behaviour_data)
        if beh_type is not dict:
            raise WrongBehaviourInputData("Behaviour should be dict type but {} was given.".format(beh_type))
        base_beh_info_keys = list(behaviour_data.keys())
        if self.PARAM["ID"] not in base_beh_info_keys:
            raise WrongBehaviourInputData("Behaviour param '{}' name doesn't exist.".format(self.PARAM["ID"]))
        if self.PARAM["BEH_PARAM"] not in base_beh_info_keys:
            raise WrongBehaviourInputData("Behaviour param '{}' name doesn't exist.".format(self.PARAM["BEH_PARAM"]))

        beh_id_type = type(behaviour_data[self.PARAM["ID"]])
        if beh_id_type is not str:
            raise WrongBehaviourInputData("Behaviour ID should be string but '{}' was given".format(beh_id_type))
        beh_param_type = type(behaviour_data[self.PARAM["BEH_PARAM"]])
        if beh_param_type is not dict:
            raise WrongBehaviourInputData("Behaviour parameters should be dict but '{}' "
                                          "was given".format(beh_param_type))

        param_keys = list(behaviour_data[self.PARAM["BEH_PARAM"]].keys())
        if self.PARAM["TYPE"] not in param_keys:
            raise WrongBehaviourInputData("In behaviours parameters '{}' name doesn't "
                                          "exist.".format(self.PARAM["TYPE"]))
        beh_name = behaviour_data[self.PARAM["BEH_PARAM"]][self.PARAM["TYPE"]]
        if type(beh_name) is not str:
            raise WrongBehaviourInputData("Behaviour '{}' should be str.".format(type(beh_name)))
        if beh_name not in self.TYPES.values():
            raise WrongBehaviourInputData("Behaviour '{}' doesn't exist.".format(beh_name))

        if beh_name == self.TYPES["goto"]:
            if self.PARAM["BEH_POI"] not in param_keys:
                raise WrongBehaviourInputData("Missing '{}' name for {} behaviour.".format(self.PARAM["BEH_POI"],
                                                                                           self.TYPES["goto"]))
            beh_type = type(behaviour_data[self.PARAM["BEH_PARAM"]][self.PARAM["BEH_POI"]])
            if beh_type is not str:
                raise WrongBehaviourInputData("Behaviour goto poi id should be a string "
                                              "but {} was given.".format(beh_type))

    def get_info(self):
        """
        Wyswietla informacje o zachownaiu
        """
        param = "{"
        n = len(self.parameters)
        i = 0
        for key in sorted(self.parameters):
            i += 1
            param += "'" + key + "': '" + str(self.parameters) + "'"
            if i != n:
                param += ","
        param += "}"
        return "id: " + str(self.id) + ", parameters: " + str(self.parameters) + "\n"


class Task:
    """
    Klasa przechowuje informacje o pojedymczym zadaniu w systemie

    Attributes:
        id (string): id zadania
        robot_id (string): id robota
        start_time (time_string YYYY-mm-dd HH:MM:SS or None): czas dodania zadania do bazy
        behaviours ([Behaviour, Behaviour, ...]): lista kolejnych zachowan dla robota
        current_behaviour_index (int): id aktualnie wykonywanego zachowania, jesli zadanie jest w trakcie wykonywania
        status (string): nazwa statusu z listy STATUS_LIST
        weight (float): waga z jaka powinno zostac wykonane zadanie, im wyzsza tym wyzszy priorytet
        priority (float) priorytet na wykonanie zadania. Im wyższy tym wyższy priorytet wykonania
    """
    PARAM = {
        "ID": "id",  # nazwa pola zawierajacego id zadania
        "ROBOT_ID": "robot",  # nazwa pola zawierajacego id robota
        "START_TIME": "start_time",  # nazwa pola zawierajaca czas pojawienia sie zadania w systemie
        "CURRENT_BEH_ID": "current_behaviour_index",  # nazwa pola odnoszacego sie do aktualnie wykonywanego
        # zachowania po id
        "STATUS": "status",  # nazwa pola zawierajacego status zadania
        "WEIGHT": "weight",  # nazwa pola odnoszacego sie do wagi zadania
        "BEHAVIOURS": "behaviours",  # nazwa pola odnoszaca sie do listy zachowan w zadaniu
        "PRIORITY": "priority"  # priorytet zadania
    }

    STATUS_LIST = {  # slownik wartosci nazw statusow zadania
        "TO_DO": 'To Do',  # nowe zadanie, nie przypisane do robota
        "IN_PROGRESS": "IN_PROGRESS",  # zadanie w trakcie wykonywania
        "ASSIGN": "ASSIGN",  # zadanie przypisane, ale nie wykonywane. Oczekiwanie na potwierdzenie od robota
        "DONE": "COMPLETED"  # zadanie zakonczone
    }

    def __init__(self, task_data):
        """
        Parameters:
            task_data ({"id": string, "behaviours": [Behaviour, Behaviour, ...],
                  "robotId": string, "start_time": time, "priority": int, "status": STATUS_LIST[status},
                  "weight": int): zadanie dla robota
        """
        # self.validate_input(task_data)
        self.id = task_data[self.PARAM["ID"]]
        self.robot_id = task_data[self.PARAM["ROBOT_ID"]]
        self.start_time = task_data[self.PARAM["START_TIME"]]
        self.status = task_data[self.PARAM["STATUS"]]
        self.weight = task_data[self.PARAM["WEIGHT"]]
        self.priority = 3 if self.PARAM["PRIORITY"] not in task_data else task_data[self.PARAM["PRIORITY"]]
        self.index = 0
        self.current_behaviour_index = task_data[self.PARAM["CURRENT_BEH_ID"]]  # dla statusu done kolejne zachowania
        # jesli zadanie ma inny status to wartosc tyczy sie aktualnie wykonywanego zachowania
        try:
            self.behaviours = [Behaviour(raw_behaviour) for raw_behaviour in task_data[self.PARAM["BEHAVIOURS"]]]
        except WrongBehaviourInputData as error:
            raise WrongTaskInputData("Task id: {}. Behaviour error. {}".format(task_data[self.PARAM["ID"]], error))

    def get_poi_goal(self):
        """
        Returns:
            (string): id POI w kierunku, ktorego porusza sie robot lub id POI, w ktorym wykonuje zachowanie
        """
        goal_poi = None
        previous_behaviour = None
        i = 0
        beh_id = 0 if self.current_behaviour_index == -1 else self.current_behaviour_index
        for behaviour in self.behaviours:
            if beh_id == i:
                if behaviour.check_if_go_to():
                    goal_poi = behaviour.get_poi()
                else:
                    if previous_behaviour is not None:
                        goal_poi = previous_behaviour.get_poi()
                        break

            if behaviour.check_if_go_to():
                previous_behaviour = behaviour
            i += 1

        return goal_poi if goal_poi is not None else previous_behaviour.get_poi()

    def get_current_behaviour(self):
        """
        Zwraca aktualne zachowanie wykonywane przez robota lub takie ktore ma byc kolejno wykonane, bo poprzednie
        zostalo zakonczone.

        Returns:
            (Behaviour): aktualnie wykonywane zachowanie w ramach zadania
        """
        return self.behaviours[0] if self.current_behaviour_index == -1 else \
            self.behaviours[self.current_behaviour_index]

    def check_if_task_started(self):
        """
        Sprawdza czy dane zadanie zostalo rozpoczete.

        Returns:
            (bool): wartosc True jesli zadanie zostalo rozpoczete w przeciwnym wypadku False
        """
        return self.status != self.STATUS_LIST["TO_DO"]

    def validate_input(self, task_data):
        """
        Parameters:
            task_data ({"id": string, "behaviours": [Behaviour, Behaviour, ...],
                  "robotId": string, "timeAdded": time, "PRIORITY": Task.PRIORITY["..."]}): zadanie dla robota
        """
        if type(task_data) != dict:
            raise WrongTaskInputData("Wrong task input data type.")
        task_keys = task_data.keys()
        # sprawdzenie czy zadanie zawiera wszystkie niezbedne parametry
        if self.PARAM["ID"] not in task_keys:
            raise WrongTaskInputData("Task param '{}' doesn't exist.".format(self.PARAM["ID"]))
        task_id = task_data[self.PARAM["ID"]]
        if self.PARAM["ROBOT_ID"] not in task_keys:
            raise WrongTaskInputData("Task id: {}. Param '{}' doesn't exist.".format(task_id, self.PARAM["ROBOT_ID"]))
        if self.PARAM["START_TIME"] not in task_keys:
            raise WrongTaskInputData("Task id: {}. Param '{}' doesn't exist.".format(task_id, self.PARAM["START_TIME"]))
        if self.PARAM["BEHAVIOURS"] not in task_keys:
            raise WrongTaskInputData("Task id: {}. Param '{}' doesn't exist.".format(task_id, self.PARAM["BEHAVIOURS"]))
        if self.PARAM["CURRENT_BEH_ID"] not in task_keys:
            raise WrongTaskInputData("Task id: {}. Param '{}' doesn't exist.".format(task_id,
                                                                                     self.PARAM["CURRENT_BEH_ID"]))
        if self.PARAM["STATUS"] not in task_keys:
            raise WrongTaskInputData("Task id: {}. Param '{}' doesn't exist.".format(task_id, self.PARAM["STATUS"]))
        if self.PARAM["WEIGHT"] not in task_keys:
            raise WrongTaskInputData("Task id: {}. Param '{}' doesn't exist.".format(task_id, self.PARAM["WEIGHT"]))

        # sprawdzenie czy parametry sa wlasciwego typu
        task_id_type = type(task_id)
        if task_id_type is not str:
            raise WrongTaskInputData("Task '{}' should be str type but {} was given.".format(self.PARAM["ID"],
                                                                                             task_id_type))

        robot_id = task_data[self.PARAM["ROBOT_ID"]]
        task_robot_type = type(robot_id)
        if task_robot_type != str and robot_id is not None:
            raise WrongTaskInputData("Task id: {}. Param '{}' should be str or None type but {} "
                                     "was given.".format(task_id, self.PARAM["ROBOT_ID"], task_robot_type))

        task_time = task_data[self.PARAM["START_TIME"]]
        task_time_type = type(task_time)
        if task_time_type != str and task_time is not None:
            raise WrongTaskInputData("Task id: {}. Param '{}' should be str or None type but {} "
                                     "was given.".format(task_id, self.PARAM["START_TIME"], task_time_type))

        task_beh_index_type = type(task_data[self.PARAM["CURRENT_BEH_ID"]])
        if task_beh_index_type != int:
            raise WrongTaskInputData("Task id: {}. Param '{}' should be int type but {} "
                                     "was given.".format(task_id, self.PARAM["CURRENT_BEH_ID"], task_beh_index_type))

        task_status = task_data[self.PARAM["STATUS"]]
        task_status_type = type(task_data[self.PARAM["STATUS"]])
        if task_status_type != str and task_status is not None:
            raise WrongTaskInputData("Task id: {}. Param '{}' should be str or None type but {} "
                                     "was given.".format(task_id, self.PARAM["STATUS"], task_status_type))

        weight_id_type = type(task_data[self.PARAM["WEIGHT"]])
        if weight_id_type not in [int, float]:
            raise WrongTaskInputData("Task id: {}. Param '{}' should be int, float, None type but {} was given."
                                     .format(task_id, self.PARAM["WEIGHT"], weight_id_type))

        behaviour_type = type(task_data[self.PARAM["BEHAVIOURS"]])
        if behaviour_type != list:
            raise WrongTaskInputData("Task id: {}. Param '{}' should be list type but {} was given."
                                     .format(task_id, self.PARAM["BEHAVIOURS"], behaviour_type))

        # sprawdzenie poprawnosci danych
        if task_status not in self.STATUS_LIST.values():
            raise WrongTaskInputData("Task id: {}. '{}' doesn't exist. {} "
                                     "was given.".format(task_id, self.PARAM["STATUS"], task_status))
        if robot_id is None and task_data[self.PARAM["STATUS"]] != self.STATUS_LIST["TO_DO"]:
            raise WrongTaskInputData("Task id: {}. Param '{}' should be set when task was started. Status different"
                                     " than '{}'.".format(task_id, self.PARAM["ROBOT_ID"],
                                                          self.STATUS_LIST["TO_DO"]))

        max_n_beh = len(task_data[self.PARAM["BEHAVIOURS"]]) - 1
        if (task_data[self.PARAM["CURRENT_BEH_ID"]] < -1) or (task_data[self.PARAM["CURRENT_BEH_ID"]] > max_n_beh):
            raise WrongTaskInputData("Task id: {}. Param '{}' should be int in range [-1,{}] but was '{}'"
                                     "".format(task_id, self.PARAM["CURRENT_BEH_ID"], max_n_beh,
                                               task_data[self.PARAM["CURRENT_BEH_ID"]]))

        try:
            datetime.strptime(task_time, "%Y-%m-%d %H:%M:%S")
        except:
            raise WrongTaskInputData("Task id: {}. Param '{}' wrong type. Required YYYY-mm-dd HH:MM:SS".
                                     format(task_id, self.PARAM["START_TIME"], task_time_type))

    # TODO
    # sprawdzenie kolejnosci zachowan w zadaniu
    # sprawdzenie czy pierwszym zachowaniem jest goto
    # dla innych typow zadan odpowiedzialnych za wysylanie MSG do robota current beh index odnosi
    # sie do wykonywalnego przez robota zachowania uwzglednianego w planie. Takie zachowania
    # powinny być pominięte na etapie planowania. Kolejnym zachowaniem nie może być zachowanie nieuwzględniane
    # na etapie planowania.

    def get_info(self):
        """
        Wyswietla informacje o zadaniu.
        """
        data = "id: " + str(self.id) + ", robot_id: " + str(self.robot_id) + ",start_tme: " + str(
            self.start_time) + "\n"
        data += "current beh id: " + str(self.current_behaviour_index) + ", status: " + str(self.status) + \
                ", weight: " + str(self.weight) + "\n"
        for behaviour in self.behaviours:
            data += behaviour.get_info()
        return data

    def is_planned_swap(self):
        """
        Sprawdza czy zadanie wymiany jest zadaniem pochodzącym z planu.
        Returns:
             (bool): True - zadanie z planu wymian, False - inne zadanie lub wymiana utworzona w inny sposob
        """
        for behaviour in self.behaviours:
            if "swap" in self.id:
                if behaviour.get_type() == Behaviour.TYPES["bat_ex"]:
                    return True

        return False


class TasksManager:
    """
    Klasa odpowiadajaca za analize kolejnych zadan wykonywanych i przydzielonych do robotow. Zawiera liste
    posortowanych zadan po priorytecie wykonania, a nastepnie po czasie.

    Attributes:
        tasks ([Task, Task, ...]): lista posortowanych zadan dla robotow
    """

    #
    # TODO 1. Oddzielić zadania wymiany baterii od reszty
    # slownik id robota: zadanie wymiany baterii
    def __init__(self, tasks):
        """
        Parameters:
          tasks ([Task, Task, ...) - lista zadan dla robotow
        """
        self.tasks = []
        self.set_tasks(tasks)

    def set_tasks(self, tasks):
        """
        Odpowiada za przekonwertowanie danych wejsciowych i ustawienie zadan dla atrybutu tasks.

        Parameters:
            tasks ([Task, Task, ...) - lista zadan dla robotow
        """
        type_input_data = type(tasks)
        if type_input_data != list:
            raise WrongTaskInputData("Input tasks list should be list but '{}' was given.".format(type_input_data))

        max_priority_value = 0
        all_tasks = copy.deepcopy(tasks)
        for i, task in enumerate(all_tasks):
            task.weight = task.priority
            max_priority_value = task.weight if task.weight > max_priority_value else max_priority_value
            task.index = i + 1

        # odwrocenie wynika pozniej z funkcji sortujacej, zadanie o najwyzszym priorytecie powinno miec
        # najnizsza wartosc liczbowa
        for task in all_tasks:
            task.weight = max_priority_value - task.weight

        # sortowanie zadan po priorytetach i czasie zgłoszenia
        tasks_id = [data.id for data in sorted(all_tasks, key=lambda task_data: (task_data.weight, task_data.index),
                                               reverse=False)]

        self.tasks = []
        for i in tasks_id:
            updated_task = [task for task in all_tasks if task.id == i][0]
            # przepisanie wartosci wejsciowej priorytetu dla zachowania kolejnosci
            updated_task.weight = [task.weight for task in tasks if task.id == i][0]

            self.tasks.append(updated_task)

    def remove_tasks_by_id(self, tasks_id):
        """
        Usuwa z listy zadania na podstawie przekazanej listy id zadan, ktore trzeba usunac.

        Parameters:
             tasks_id ([string, string, ...]): lista z kolejnymi id zadan
        """

        for i in tasks_id:
            for task in self.tasks:
                if task.id == i:
                    self.tasks.remove(task)
                    break

    def get_all_unasigned_unstarted_tasks(self):
        """
        Zwraca liste wszystkich nieprzypisanych i nierozpoczetych zadan.

        Returns:
             (list(Task)): lista zadan
        """
        return [task for task in self.tasks if task.robot_id is None and not task.check_if_task_started()]


class Battery:
    """
    Klasa przechowująca informacje o baterii
    Attributes:
        max_capacity (float): maksymalna pojemnosc baterii w [Ah]
        capacity (float): pojemnosc baterii w [Ah]
        drive_usage (float): zuzycie baterii w trakcie jazdy w [A/h]
        stand_usage (float): zuzycie baterii w trakcie postoju w [A/h]
        remaining_working_time (float): pozostaly czas pracy na baterii przy ktorym pojawia sie
                                        poziom ostrzegawczy [min]
    """

    def __init__(self):
        self.max_capacity = 40.0
        self.capacity = 40.0
        self.drive_usage = 5.0
        self.stand_usage = 3.5
        self.remaining_working_time = 20.0  # [min]

    def __str__(self):
        return "Battery info: max_cappacity={max_capacity:.2f}   cappacity={capacity:.2f}" \
               "warning_capacity={warning_lvl:.2f}   critical_capacity={critical_lvl:.2f}   " \
               "drive_usage={drive_use:.2f}  " \
               "stand_usage={stand_use:.2f}  " \
               "remaining_working_time={rem_time:.2f}".format(max_capacity=self.max_capacity,
                                                              capacity=self.capacity,
                                                              warning_lvl=self.get_warning_capacity(),
                                                              critical_lvl=self.get_critical_capacity(),
                                                              drive_use=self.drive_usage,
                                                              stand_use=self.stand_usage,
                                                              rem_time=self.remaining_working_time)

    def get_warning_capacity(self):
        """
        Zwraca pojemnosc baterii przy ktorej przekroczony zostaje poziom ostrzegawczy.

        Returns:
            (float): pojemnosc baterii w Ah
        """
        return self.remaining_working_time / 60 * self.drive_usage

    def get_critical_capacity(self):
        """
        Zwraca pojemnosc baterii przy ktorej przekroczony zostaje poziom krytyczny. Przy tym poziomie powinien zostac
        zalogowany blad, gdyz grozi on wylaczeniem robota.

        Returns:
            (float): pojemnosc baterii w Ah
        """
        return (self.remaining_working_time / 2) / 60 * self.drive_usage

    def get_time_to_warn_allert(self):
        """
        Returns:
             (float): Zwraca czas w minutach do osiągnięcia poziomu ostrzegawczego. Dla przekroczenia progu
                      ostrzegawczego zwracana jest wartosc -1.
        """
        warn_capacity = self.get_warning_capacity()
        if warn_capacity <= self.capacity:
            return (self.capacity - warn_capacity) / self.drive_usage * 60
        else:
            return -1

    def get_time_to_critical_allert(self):
        """
        Returns:
             (float): Zwraca czas w minutach do osiągnięcia poziomu krytycznego. Dla przekroczenia progu
                      krytycznego zwracana jest wartosc -1.
        """
        critical_capacity = self.get_critical_capacity()
        if critical_capacity <= self.capacity:
            return (self.capacity - critical_capacity) / self.drive_usage * 60
        else:
            return -1

    def get_time_to_discharged(self):
        """
        Returns:
             (float): Zwraca czas w minutach do rozładowania baterii.
        """
        return self.capacity / self.drive_usage * 60

    def is_enough_capacity_before_critical_alert(self, drive_time_min, stand_time_min):
        """
        Sprawdza czy robot posiada wystarczajaca liczbe energii zanim pojawi sie ostrzezenie krytyczne. Pod uwage
        brane jest zuzycie energii w trakcie jazdy i postoju zgodnie z planowanym czasem jazdy i postoju.

        Parameters:
            drive_time_min (float): czas jazdy w minutach
            stand_time_min (float): czas postoju w minutach

        Returns:
            (bool): zwraca informacje o wystarczajacej liczbie energii
        """
        used_capacity = drive_time_min / 60 * self.drive_usage + stand_time_min / 60 * self.stand_usage  # z min na h
        predicted_capacity_lvl = self.capacity - used_capacity
        return predicted_capacity_lvl > self.get_critical_capacity()


class Robot:
    """
    Klasa przechowujaca informacje o pojedynczym robocie do ktorego beda przypisywane zadania

    Attributes:
        id (string): id robota
        edge ((int,int)): krawedz na ktorej aktualnie znajduje sie robot
        poi_id (string): id poi w ktorym znajduje sie robot
        planning_on (bool): informuje czy robot jest w trybie planownaia
        is_free (bool): informuje czy robot aktualnie wykonuje jakies zachowanie czy nie
        time_remaining (float/None): czas do ukonczenia zachowania
        task (Task): zadanie przypisane do robota
        next_task_edges ([(int,int), ... ]): informuje o kolejnych krawedziach przejscia ktore nalezy wyslac do robota
        end_beh_edge (bool): informuje czy zachowanie po przejsciu krawedzia zostanie ukonczone
        battery (Battery): bateria w robocie
        swap_time (float): czas wymiany/ładowania baterii w stacji. Dla ładowania -> narastanie poziomu naładowania
                           baterii w robocie. Dla wymiany -> poziom naładowania w robocie zmienia się skokowo. Dla
                           kilku baterii będzie to kilka skoków poziomów naładowania. [s]
    """

    def __init__(self, robot_data):
        """
        Parameters:
            robot_data ({"id": string, "edge": (int, int), "poiId" (string), "planningOn": bool, "isFree": bool,
                         "timeRemaining": float/None}): slownik z danymi o robocie
        """
        # self.validate_input(robot_data)
        self.id = robot_data["id"]
        self.edge = robot_data["edge"]
        self.poi_id = robot_data["poiId"]
        self.planning_on = robot_data["planningOn"]
        self.is_free = robot_data["isFree"]
        self.time_remaining = robot_data["timeRemaining"]
        self.task = None
        self.next_task_edges = None
        self.end_beh_edge = None
        self.swap_time = 3 * 60
        self.battery = Battery()
        self.check_planning_status()

    def validate_input(self, data):
        """
        Parameters:
            data ({"id": string, "edge": (int, int), "planningOn": bool, "isFree": bool,
                         "timeRemaining": float/None}): slownik z danymi o robocie
        """
        # sprawdzenie czy dane wejsciowe sa dobrego typu
        type_data = type(data)
        if type_data != dict:
            raise WrongRobotInputData("Robot input data should be dict but {} was given.".format(type_data))

        # sprawdzenie czy kazdy parametr istnieje
        if "id" not in data:
            raise WrongRobotInputData("Robot 'id' param doesn't exist.")
        robot_id = data["id"]
        if "edge" not in data:
            raise WrongRobotInputData("Robot id: {}. Param 'edge' doesn't exist.".format(robot_id))
        if "planningOn" not in data:
            raise WrongRobotInputData("Robot id: {}. Param 'planningOn' doesn't exist.".format(robot_id))
        if "isFree" not in data:
            raise WrongRobotInputData("Robot id: {}. Param 'isFree' doesn't exist.".format(robot_id))
        if "timeRemaining" not in data:
            raise WrongRobotInputData("Robot id: {}. Param 'timeRemaining' doesn't exist.".format(robot_id))

        # sprawdzenie czy kazdy parametr wejsciowy jest dobrego typu
        type_id = type(data["id"])
        if type_id != str:
            raise WrongRobotInputData("Robot id: {}. Param 'id' should be str type but {} was given."
                                      "".format(robot_id, type_id))
        type_id = type(data["edge"])
        if type_id != tuple and data["edge"] is not None:
            raise WrongRobotInputData("Robot id: {}. Param 'edge' should be tuple or None type but {} was given."
                                      "".format(robot_id, type_id))
        type_id = type(data["planningOn"])
        if type_id != bool:
            raise WrongRobotInputData("Robot id: {}. Param 'planningOn' should be bool type but {} was given."
                                      "".format(robot_id, type_id))
        type_id = type(data["isFree"])
        if type_id != bool:
            raise WrongRobotInputData("Robot id: {}. Param 'isFree' should be bool type but {} was given."
                                      .format(robot_id, type_id))
        type_id = type(data["timeRemaining"])
        if type_id not in [int, float]:
            raise WrongRobotInputData("Robot id: {}. Param 'timeRemaining' should be int or float type but {} "
                                      "was given.".format(robot_id, type_id))

    def get_current_node(self):
        """
        Returns:
             (int): wezel w ktorym znajduje sie robot lub znajdzie po zakonczeniu zachowania
        """
        return None if self.edge is None else self.edge[1]

    def check_planning_status(self):
        """
        TODO
            - przekonwertowac status z robota i okreslic na jego podstawie czy robot jest w trybie planowania czy nie
            - dopisac testy po wprowadzeniu dodatkowych statusow robota na podstawie, ktorych
                podjeta jest decyzja o planowaniu
        Returns:
            (bool): True - robot zajety, False - robot wolny
        """
        return self.planning_on

    def get_current_destination_goal(self):
        """
        Zwraca Id POI do ktorego aktualnie jedzie robot lub wykonuje w nim jakas operacje (dokowanie,
        wait, oddokowanie). Dla nowo przydzielonych zadan pozwala na sprawdzenie do ktorego POI bedzie jechal
        robot.

        Returns:
            (string): id POI z bazy do ktorego aktualnie jedzie lub bedzie jechal robot, jesli nie jest on skierowany do
                      zadnego POI to zwracana jest wartosc None
        """
        return self.task.get_poi_goal() if self.task is not None else None

    def get_info(self):
        """
        Zwraca informacje o robocie.

        Returns:
            data (string): informacje o robocie
        """
        data = "id: " + str(self.id) + ", edge: " + str(self.edge) + ", planning_on: " + str(self.planning_on) + "\n"
        data += "is free: " + str(self.is_free) + ", time remaining: " + str(self.time_remaining) + "\n"
        task_info = self.task.get_info if self.task is not None else None
        data += "task: " + str(task_info) + "\n"
        data += "next edge " + str(self.next_task_edges) + ", end beh: " + str(self.end_beh_edge)
        return data


class RobotsPlanManager:
    """
    Klasa obslugujaca przypisywanie zadan do robotow i wyciaganie informacji o robotach niezbednych do planowania zadan.

    Attributes:
        robots ({"id": Robot, "id": Robot, ...}): slownik z robotami do ktorych beda przypisywane zadania

    """

    def __init__(self, robots, base_poi_edges):
        """
        Parameters:
             robots ({ "id":Robot, "id": Robot, ...]): slownik robotow do planowania zadan
             base_poi_edges ({poi_id: graph_edge(tuple), ...}) : slownik z krawedziami bazowymi do ktorych nalezy
                przypisac robota, jesli jest on w POI
        """
        self.robots = {}
        self.set_robots(robots, base_poi_edges)

    def set_robots(self, robots, base_poi_edges):
        """
        Parameters:
             robots ({"id":Robot, "id": Robot, ...]): slownik robotow do planowania zadan
            base_poi_edges ({poi_id: graph_edge(tuple), ...}) : slownik z krawedziami bazowymi do ktorych nalezy
                przypisac robota, jesli jest on w POI
        """
        self.robots = {}
        robots_copy = copy.deepcopy(robots)
        for i in robots_copy:
            robot = robots_copy[i]
            if robot.planning_on:
                if type(robot.edge) is not tuple:
                    # zamiast krawedzi jest POI TODO pobrania POI z innego miejsca i wpisanie odpowiedniej
                    # krawedzi, jesli nie jest ona znana dla danego robota.
                    # TODO weryfikacja czy dla danego poi istnieje krawedz na grafie, istnieje w podanym slowniku
                    # wejsciowym
                    if robot.poi_id is not None:
                        robot.edge = base_poi_edges[robot.poi_id]
                        self.robots[robot.id] = robot
                else:
                    self.robots[robot.id] = robot

    def get_robot_by_id(self, robot_id):
        """
        Dla podanego id zwraca obiekt Robot.

        Parameters:
            robot_id (string): id robota

        Returns:
            (Robot): informacje o robocie, jeśli nie ma go na liście to None
        """
        if self.check_if_robot_id_exist(robot_id):
            return self.robots[robot_id]
        else:
            return None

    def set_task(self, robot_id, task):
        """
        Przypisuje zadanie dla robota o podanym id. Jeśli go nie ma to blad.

        Parameters:
            robot_id (string): id robota
            task (Task): zadanie dla robota
        """

        if not self.check_if_robot_id_exist(robot_id):
            raise TaskManagerError("Robot on id '{}' doesn't exist".format(robot_id))

        if robot_id != task.robot_id and task.robot_id is not None:
            raise TaskManagerError("Task is assigned to different robot. Task {} required robot with "
                                   "id {} but {} was given.".format(task.id, task.robot_id, robot_id))
        task.robot_id = robot_id
        self.robots[robot_id].task = task

    def check_if_robot_id_exist(self, robot_id):
        """
        Sprawdza czy robot o podanym id istnieje na liscie do planownaia.
        Parameters:
            robot_id (string): id robota
        Returns:
            (bool): Jesli robot istnieje to True inaczej False.
        """
        return robot_id in self.robots

    def set_next_edges(self, robot_id, next_edges):
        """
        Ustawia kolejna krawedz przejscia dla robota.

        Parameters:
            robot_id (string): id robota
            next_edges ([(int,int), ...]): nastepna krawedz jaka ma sie poruszac robot
        """
        if not self.check_if_robot_id_exist(robot_id):
            raise TaskManagerError("Robot on id '{}' doesn't exist".format(robot_id))
        if self.robots[robot_id].task is None:
            raise TaskManagerError("Can not assign next edge when robot {} doesn't have task.".format(robot_id))
        self.robots[robot_id].next_task_edges = next_edges

    def set_end_beh_edge(self, robot_id, end_beh_edge):
        """
        Ustawia informacje o tym czy dane przejscie krawedzia bedzie konczylo zachowanie w zadaniu czy nie.

        Parameters:
            robot_id (string): id robota
            end_beh_edge (bool): informacja o tym czy jest to koniec zachowania czy nie
        """
        if not self.check_if_robot_id_exist(robot_id):
            raise TaskManagerError("Robot on id '{}' doesn't exist".format(robot_id))
        if self.robots[robot_id].task is None:
            raise TaskManagerError("Can not set end behaviour edge when robot {} doesn't have task.".format(robot_id))
        if self.robots[robot_id].next_task_edges is None:
            raise TaskManagerError("Can not set end behaviour edge when robot {} doesn't have next_task_edge."
                                   "".format(robot_id))
        self.robots[robot_id].end_beh_edge = end_beh_edge

    def get_free_robots(self):
        """
        Zwraca liste robotow do ktorych zadania nie zostaly przypisane. Atrybut robota 'task' jest None.

        Returns:
            ([Robot, Robot, ... ]): lista robotow, ktore nie posiadaja przypisanych zadan.
        """
        return [robot for robot in self.robots.values() if robot.task is None]

    def get_busy_robots(self):
        """
        Zwraca liste robotow do ktorych zadania zostaly przypisane.

        Returns:
            ([Robot, Robot, ... ]): lista robotow, wykonujacych zadania
        """
        return [robot for robot in self.robots.values() if robot.task is not None]

    def get_robots_id_on_edge(self, edge):
        """
        Zwraca liste z id robotow, ktore znajduja sie na podanych krawedziach

        Parameters:
            edge ((int,int)): lista krawedzi na ktorych maja byc znalezione wszystkie
                roboty

        Returns:
            ([string,string, ...]): lista z id robotow znajdujacych sie na wszystkich wskazanych krawedziach
        """
        return [robot.id for robot in self.robots.values() if robot.edge == edge]

    def get_current_robots_goals(self):
        """
        Zwraca slownik robotow wraz z POI do ktorych aktualnie jada roboty

        Returns:
            ({robot_id: poi_id, ...}): slownik robotow z POI aktualnego celu
        """
        busy_robots = {}
        for robot in self.robots.values():
            if robot.task is not None:
                busy_robots[robot.id] = robot.task.get_poi_goal()
        return busy_robots


class PoisManager:
    """
    Zawiera informacje o POI przypisanych do grafu.

    Attributes:
        pois ({poi_id: {"type": typ_poi}, ... ): slownik poi wraz z ich typem
    """

    def __init__(self, graph_data):
        """
        Parameters:
             graph_data (SupervisorGraphCreator): rozszerzony graf do planowania
        """
        self.pois = {}
        self.set_pois(graph_data)

    def set_pois(self, graph):
        """
        Na podstawie danych z grafu tworzy slownik POI przypisanych do wezlow grafu.

        Parameters:
             graph (SupervisorGraphCreator): rozszerzony graf do planowania
        """
        for i in graph.source_nodes:
            node = graph.source_nodes[i]
            if node["poiId"] != "0":
                self.pois[node["poiId"]] = node["type"]

    def check_if_queue(self, poi_id):
        """
        Sprawdza czy podane POI jest POI kolejkowania.

        Parameters:
            poi_id (string): id poi z bazy

        Returns:
            (bool): informacja czy poi jest typu kolejkownaia (queue)
        """
        if poi_id not in self.pois:
            raise PoisManagerError("Poi id '{}' doesn't exist".format(poi_id))
        return self.pois[poi_id] == gc.base_node_type["queue"]

    def get_raw_pois_dict(self):
        """
        Zwraca pusta slownik z id poi

        Returns:
            ({poi_id: None, poi_id: None, ...}): pusty slownik z POI
        """
        poi_list = {}
        for poi_id in self.pois:
            poi_list[poi_id] = None
        return poi_list

    def get_type(self, poi_id):
        """
        Zwraca typ POI na podstawie id.

        Parameters:
            poi_id (string): id poi z bazy

        Returns:
            (gc.base_node_type[]): typ POI
        """
        if poi_id not in self.pois:
            raise PoisManagerError("Poi id '{}' doesn't exist".format(poi_id))
        return self.pois[poi_id]


class PlanningGraph:
    """
    Klasa do obslugi grafu planujacego.

    Attributes:
        graph (SupervisorGraphCreator): dane o grafie z klasy SupervisorGraphCreator
        pois (PoisManager): manager punktów POI
        future_blocked_edges (dict): słownik zawierający informację o krawędziach zablokowanych w przyszłości w wyniku
            planowania
    """

    def __init__(self, graph):
        """
        Parameters:
            graph (SupervisorGraphCreator):
        """
        self.graph = copy.deepcopy(graph)
        self.pois = PoisManager(graph).pois
        self.future_blocked_edges = {}
        for edge in self.graph.graph.edges.keys():
            self.future_blocked_edges[edge] = []

    def block_other_pois(self, robot_node, target_node):
        """
        Funkcja odpowiada za zablokowanie krawedzi grafu zwiazanych z innymi POI niz aktualnym (jesli jest w POI) i
        docelowym.

        Parameters:
            robot_node (int): wezel grafu z supervisora w ktorym aktualnie jest robot
            target_node (int): wezel grafu z supervisora do ktorego zmierza robot
        """
        no_block_poi_ids = ["0", self.graph.graph.nodes[robot_node]["poiId"],
                            self.graph.graph.nodes[target_node]["poiId"]]
        for edge in self.graph.graph.edges(data=True):
            start_node_poi_id = self.graph.graph.nodes[edge[0]]["poiId"]
            end_node_poi_id = self.graph.graph.nodes[edge[1]]["poiId"]
            if start_node_poi_id not in no_block_poi_ids or end_node_poi_id not in no_block_poi_ids:
                self.graph.graph.edges[edge[0], edge[1]]["planWeight"] = None
            else:
                self.graph.graph.edges[edge[0], edge[1]]["planWeight"] = self.graph.graph.edges[edge[0], edge[1]][
                    "weight"]

    def set_robot_on_future_edge(self, edge, robot_id):
        self.future_blocked_edges[edge].append(robot_id)

    def get_robots_on_future_edge(self, edge):
        return self.future_blocked_edges[edge]

    def get_robots_on_edge(self, edge):
        return self.graph.graph.edges[edge]["robots"]

    def get_end_go_to_node(self, poi_id, poi_type):
        """
        Zwraca węzeł końcowy krawędzi dla zadania typu GOTO POI.

        Parameters:
            poi_id (string): id POI z bazy
            poi_type (gc.base_node_type["nazwa_typu"]): typ poi

        Returns:
            (int): koncowy wezel krawedzi dojazdu do wlasciwego stanowiska
        """
        if poi_id not in self.pois:
            raise PlaningGraphError("POI {} doesn't exist on graph.".format(poi_id))
        if poi_type["nodeSection"] == gc.base_node_section_type["dockWaitUndock"]:
            return [node[0] for node in self.graph.graph.nodes(data=True) if node[1]["poiId"] == poi_id
                    and node[1]["nodeType"] == gc.new_node_type["dock"]][0]
        elif poi_type["nodeSection"] == gc.base_node_section_type["waitPOI"]:
            return [node[0] for node in self.graph.graph.nodes(data=True) if node[1]["poiId"] == poi_id
                    and node[1]["nodeType"] == gc.new_node_type["wait"]][0]
        else:
            return [node[0] for node in self.graph.graph.nodes(data=True) if node[1]["poiId"] == poi_id][0]

    def get_end_docking_node(self, poi_id):
        """
        Zwraca węzeł końcowy krawędzi dla zadania typu DOCK POI.

        Parameters:
            poi_id (string): id POI z bazy

        Returns:
            (int): koncowy wezel krawedzi zwiazanej z zachowaniem dokowania
        """
        if poi_id not in self.pois:
            raise PlaningGraphError("POI {} doesn't exist on graph.".format(poi_id))
        if self.pois[poi_id]["nodeSection"] != gc.base_node_section_type["dockWaitUndock"]:
            raise PlaningGraphError("POI {} should be one of docking type.".format(poi_id))
        poi_node = [node for node in self.graph.graph.nodes(data=True) if node[1]["poiId"] == poi_id
                    and node[1]["nodeType"] == gc.new_node_type["wait"]]
        return poi_node[0][0]

    def get_end_wait_node(self, poi_id, poi_type):
        """
        Zwraca węzeł końcowy krawędzi dla zadania typu WAIT POI.

        Parameters:
            poi_id (string): id POI z bazy
            poi_type (gc.base_node_type["nazwa_typu"]): typ POI

        Returns:
            (int): koncowy wezel krawedzi zwiazanej z zachowaniem WAIT
        """
        if poi_id not in self.pois:
            raise PlaningGraphError("POI {} doesn't exist on graph.".format(poi_id))
        if self.pois[poi_id]["nodeSection"] not in [gc.base_node_section_type["dockWaitUndock"],
                                                    gc.base_node_section_type["waitPOI"]]:
            raise PlaningGraphError("POI {} should be one of docking/wait POI.".format(poi_id))
        poi_node = None
        if poi_type["nodeSection"] == gc.base_node_section_type["dockWaitUndock"]:
            poi_node = [node for node in self.graph.graph.nodes(data=True) if node[1]["poiId"] == poi_id
                        and node[1]["nodeType"] == gc.new_node_type["undock"]]
        elif poi_type["nodeSection"] == gc.base_node_section_type["waitPOI"]:
            poi_node = [node for node in self.graph.graph.nodes(data=True) if node[1]["poiId"] == poi_id
                        and node[1]["nodeType"] == gc.new_node_type["end"]]
        return poi_node[0][0]

    def get_end_undocking_node(self, poi_id):
        """
        Zwraca węzeł końcowy krawędzi dla zadania typu UNDOCK POI.

        Parameters:
            poi_id (string): id POI z bazy

        Returns:
            (int): koncowy wezel krawedzi zwiazanej z zachowaniem UNDOCK
        """
        if poi_id not in self.pois:
            raise PlaningGraphError("POI {} doesn't exist on graph.".format(poi_id))
        if self.pois[poi_id]["nodeSection"] != gc.base_node_section_type["dockWaitUndock"]:
            raise PlaningGraphError("POI {} should be one of docking/wait POI.".format(poi_id))
        poi_node = [node for node in self.graph.graph.nodes(data=True) if node[1]["poiId"] == poi_id
                    and node[1]["nodeType"] == gc.new_node_type["end"]]

        return poi_node[0][0]

    def get_max_allowed_robots_using_pois(self):
        """
        Zwraca slownik zawierajacy maksymalna liczbe robotow, ktora moze byc przypisana do POI.
        Przekroczenie tej liczby oznacza, ze roboty moga zaczac sie kolejkowac na glownym szlaku komunikacyjnym.

        Returns:
            ({poiId: int, poiId2: int,...}): Slownik z liczba robotow dla ktorego kluczem jest ID POI z bazy, a
            wartoscia maksymalna liczba robotow jaka moze oczekiwac i byc obslugiwana przy stanowisku.
        """
        max_robot_pois = {i: 0 for i in self.pois}
        for i in self.pois:
            poi_edges = [edge for edge in self.graph.graph.edges(data=True) if "connectedPoi" in edge[2]]
            connected_edges = [edge for edge in poi_edges if edge[2]["connectedPoi"] == i]
            no_intersection_direct_connection = False
            for edge in connected_edges:
                if edge[2]["edgeGroupId"] == 0:
                    no_intersection_direct_connection = True
                    break
            max_robot_pois[connected_edges[0][2]["connectedPoi"]] = 1  # dla parkingów i stanowisk bezpośrednio
            # połączonych ze skrzyżowaniem
            for edge in connected_edges:
                poi_id = edge[2]["connectedPoi"]
                poi_type = self.pois[poi_id]
                if poi_type == gc.base_node_type["queue"] and \
                        self.graph.graph.nodes[edge[0]]["nodeType"] == gc.new_node_type["intersection_out"]:
                    # dla POI z kolejkowaniem tylko tyle robotów ile wynika z krawędzi oczekiwania
                    max_robot_pois[poi_id] = max(edge[2]["maxRobots"], 1)
                    break
                elif poi_type["nodeSection"] in [gc.base_node_section_type["waitPOI"],
                                                 gc.base_node_section_type["dockWaitUndock"]]:
                    if no_intersection_direct_connection and edge[2]["edgeGroupId"] == 0:
                        # 1 dla obsługi samego stanowiska + maksymalna liczba robotów na krawędzi związana z danym POI
                        max_robot_pois[poi_id] = edge[2]["maxRobots"] + 1
                        break
        return max_robot_pois

    def get_group_id(self, edge):
        """
        Zwraca id grupy do ktorej przypisana jest krawedz. Numer grupy 0 odnosi sie do krawedzi, ktore nie sa od
        siebie wzajemnie zalezne.

        Parameters:
            edge((int,int)): krawedz grafu

        Returns:
            (int): id grupy krawedzi, 0 dla krawedzi nie wchodzacych w sklad grupy
        """
        return self.graph.graph.edges[edge]["edgeGroupId"]

    def get_edges_by_group(self, group_id):
        """
        Zwraca liste krawedzi dla grupy o danym id.

        Parameters:
            group_id (int): id grupy krawedzi

        Returns:
            ([(int, int), (int,int), ... ]): lista krawedzi nalezaca do podanej grupy
        """
        return [(edge[0], edge[1]) for edge in self.graph.graph.edges(data=True) if edge[2]["edgeGroupId"] == group_id]

    def get_max_allowed_robots(self, edge):
        """
        Zwraca maksymalna dozwolona liczbe robotow dla danej krawedzi. Jesli krawedz nalezy do grupy to 1 robot.

        Attributes:
            edge ((int,int)): dana krawedz

        Returns:
              (int): maksymalna liczba robotow jaka moze znajdowac sie na danej krawedzi
        """
        return 1 if self.get_group_id(edge) != 0 else self.graph.graph.edges[edge]["maxRobots"]

    def get_poi(self, edge):
        """
        Dla podanej krawedzi zwraca zwiazane z nia POI, jesli takie istnieje.

        Parameters:
            edge (int, int): krawedz grafu

        Returns:
            (string): zwraca id poi, jesli krawedz zwiazana jest z POI, jesli nie to None
        """
        poi_node = self.graph.graph.nodes[edge[1]]['poiId']
        if poi_node != "0":
            return poi_node
        else:
            return None

    def get_path(self, start_node, end_node):
        """
        Zwraca sciezke od aktualnego polozenia robota do celu.
        TODO - obsluga gdy wezel poczatkowy jest tym samym co koncowy np. ponowne zlecenie dojazdu tego samego
        robota do parkingu
        Parameters:
            start_node (int): wezel od ktorego ma byc rozpoczete planowanie
            end_node (int): wezel celu

        Returns:
            (list): kolejne krawedzie grafu, ktorymi ma sie poruszac robot, aby dotrzec do celu
        """
        self.block_other_pois(start_node, end_node)
        # if start_node == end_node:
        #     raise PlaningGraphError("Wrong plan. Start node '{}' should be different than end node '{}'."
        #                             .format(start_node, end_node))
        return nx.shortest_path(self.graph.graph, source=start_node, target=end_node, weight='planWeight')

    def get_path_length(self, start_node, end_node):
        """
        Zwraca wage dojazdu do punktu.

        Parameters:
            start_node (int): wezel od ktorego ma byc rozpoczete planowanie
            end_node (int): wezel celu

        Returns:
            (float): czas dojazdu od start_node do end_node
        """
        self.block_other_pois(start_node, end_node)
        if start_node == end_node:
            return 0
        else:
            return nx.shortest_path_length(self.graph.graph, source=start_node, target=end_node, weight='planWeight')

    def get_base_pois_edges(self):
        """
        Returns:
            ({poi_id: graph_edge(tuple), ...}) : slownik z krawedziami bazowymi do ktorych nalezy
             przypisac robota, jesli jest on w POI
        """
        base_poi_edges = {}
        for poi_id in self.pois:
            poi_nodes = [node[0] for node in self.graph.graph.nodes(data=True) if node[1]["poiId"] == poi_id]
            if len(poi_nodes) == 1:
                # poi jest typu parking lub queue
                edges = [edge for edge in self.graph.graph.edges(data=True) if edge[1] in poi_nodes][0]
                base_poi_edges[poi_id] = (edges[0], edges[1])
            elif len(poi_nodes) == 4:
                # poi z dokowaniem
                start_node = [node for node in poi_nodes
                              if self.graph.graph.nodes[node]["nodeType"] == gc.new_node_type["undock"]]
                end_node = [node for node in poi_nodes if
                            self.graph.graph.nodes[node]["nodeType"] == gc.new_node_type["end"]]
                base_poi_edges[poi_id] = (start_node[0], end_node[0])
            elif len(poi_nodes) == 2:
                # poi bez dokowania
                start_node = [node for node in poi_nodes
                              if self.graph.graph.nodes[node]["nodeType"] == gc.new_node_type["wait"]]
                end_node = [node for node in poi_nodes if
                            self.graph.graph.nodes[node]["nodeType"] == gc.new_node_type["end"]]
                base_poi_edges[poi_id] = (start_node[0], end_node[0])
            else:
                raise PlaningGraphError("Input graph wrong structure.")
        return base_poi_edges

    def is_intersection_edge(self, edge):
        """
        Weryfikuje czy podana krawędź jest krawędzią skrzyżowania.
        Args:
            edge ((int,int)): krawędź grafu

        Returns:
            (boolean): True - krawędź należy do skrzyżowania, False - nie należy do skrzyżowania
        """
        edge_behaviour = self.graph.graph.edges[edge]["behaviour"]
        source_nodes = self.graph.graph.edges[edge]["sourceNodes"]
        source_node_type = self.graph.source_nodes[source_nodes[0]]["type"]
        return source_node_type in [gc.base_node_type["intersection"], gc.base_node_type["waiting-departure"]] and \
               edge_behaviour == Behaviour.TYPES["goto"] and len(source_nodes) == 1

    def select_next_task(self, task, swap_task, robot, test_sim_time):
        """
        Wybiera zadanie dla robota. Jesli robotowi wystarczy energii i nie minal planowany czas wymiany na wykonanie
        zadania to jest mu ono przydzielane, a jesli nie to przydzielane jest zadanie wymiany baterii.

        Parameters:
            task (Task): zadanie dla robota, dojazdy do stanowisk
            swap_task (Task): zadanie wymiany baterii
            robot (Robot): robot dla, ktorego ma byc przydzielone zadanie
            test_sim_time (datetime.now()): TODO czas na potrzeby testów symulacyjnych, domyślnie do usunięcia
        Returns:
            (Task): wybrane zadanie dla robota
        """
        task_travel_time = self._get_task_travel_stands_time(robot.edge[1], task)
        swap_task_time = self._get_task_travel_stands_time(task_travel_time["end_node"], swap_task)
        drive_time = (task_travel_time["drive_time"] + swap_task_time["drive_time"]) / 60  # zamiana na minuty
        stand_time = (task_travel_time["stand_time"] + swap_task_time["stand_time"]) / 60  # zamiana na minuty
        total_time = drive_time + stand_time
        is_no_battery_critical_allert = robot.battery.is_enough_capacity_before_critical_alert(drive_time, stand_time)

        # now = datetime.strptime(datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "%Y-%m-%d %H:%M:%S") TODO do przywrócenia po testach
        now = datetime.strptime(test_sim_time.strftime("%Y-%m-%d %H:%M:%S"), "%Y-%m-%d %H:%M:%S")
        swap_time = datetime.strptime(swap_task.start_time, "%Y-%m-%d %H:%M:%S")

        time_to_swap = (swap_time - now) / timedelta(minutes=1)
        if time_to_swap < total_time:
            # zadanie wymiany powinno zostac zlecone i przypisane do robota:
            return swap_task
        elif not is_no_battery_critical_allert:
            # zadanie wymiany musi zostac zlecone nawet, jesli czas planowanej wymiany nie zostal przekroczony
            # robot ma znalezc sie jak najblizej stacji wymiany, aby na wypadek calkowitego rozladowania baterii
            # mozna bylo wziac naladowana ze stacji
            return swap_task
        else:
            return task

    def _get_task_travel_stands_time(self, node_id, task):
        """
        Parameters:
            node_id (int): id wezla grafu rozszerzonego od ktorego wyliczane bedzie pierwsze zachowanie goto
            task (Task): zadanie dla robota

        Returns:
            ({"drive_time": float, "stand_time": float, "end_node": int}): czasy postoju, aktywnej jazdy oraz wezel,
                w ktorym znajdzie sie robot po ukonczeniu zadania
        """

        drive_time = 0.0
        stand_time = 0.0
        last_node = node_id
        last_poi_id = task.get_poi_goal()

        for behaviour in task.behaviours:
            if behaviour.get_type() == Behaviour.TYPES["goto"]:
                last_poi_id = behaviour.get_poi()
                new_node_id = self.get_end_go_to_node(last_poi_id, self.pois[last_poi_id])
                self.block_other_pois(last_node, new_node_id)
                drive_time += self.get_path_length(last_node, new_node_id)
                last_node = new_node_id
            elif behaviour.get_type() == Behaviour.TYPES["dock"]:
                new_node_id = self.get_end_docking_node(last_poi_id)
                drive_time += self.get_path_length(last_node, new_node_id)
                last_node = new_node_id
            elif behaviour.get_type() == Behaviour.TYPES["wait"] or behaviour.get_type() == Behaviour.TYPES["bat_ex"]:
                new_node_id = self.get_end_wait_node(last_poi_id, self.pois[last_poi_id])
                stand_time += self.get_path_length(last_node, new_node_id)
                last_node = new_node_id
            elif behaviour.get_type() == Behaviour.TYPES["undock"]:
                new_node_id = self.get_end_undocking_node(last_poi_id)
                drive_time += self.get_path_length(last_node, new_node_id)
                last_node = new_node_id

        return {"drive_time": drive_time, "stand_time": stand_time, "end_node": last_node}  # zwracane czasy w [s]


class Dispatcher:
    """
    Klasa dispatchera odpowiadajaca za tworzenie planu, przydzielanie zadan do robotow i unikanie drog
    kolizyjnych na grafie. Wolne roboty blokujace stanowiska kierowane sa odpowiednio na miejsca oczekiwan
    queue/parking.

    Attributes:
        planning_graph (PlanningGraph): graf do planowania zadan
        pois (PoisManager): manager poi, zawiera m.in. informacje o ich typach
        robots_plan (RobotsPlanManager): zawiera informacje o robotach, zadaniach i kolejnych akcjach wynikajacych z
            planownaia
        unanalyzed_tasks_handler (TasksManager): zawiera informacje o zadaniach, ktore nalezy przeanalizowac
            i przypisac do robotow
        swap_tasks ({robot_id: Task, ...}): slownik zadan z zaplanowanymi wymianami baterii
    """

    def __init__(self, graph_data, robots):
        """
        Utworzenie klasy Dispatcher'a i ustawienie wartosci atrybutow planning_graph, pois, robots_plan.

        Parameters:
            graph_data (SupervisorGraphCreator): wygenerwany rozszerzony graf do planowania kolejnych zachowan robotow
            robots ({"id": Robot, "id": Robot, ...}): slownik robotow do ktorych beda przypisywane zadania
        """
        self.planning_graph = PlanningGraph(graph_data)
        self.pois = PoisManager(graph_data)

        self.robots_plan = RobotsPlanManager(robots, self.planning_graph.get_base_pois_edges())
        self.init_robots_plan(robots)

        self.unanalyzed_tasks_handler = None
        self.swap_tasks = {robot.id: None for robot in self.robots_plan.get_free_robots()}

        self.test_sim_time = None  # TODO usunąć, czas dodany na potrzeby testów symulacyjnych

    def get_plan_all_free_robots(self, graph_data, robots, tasks):
        """
        Zwraca liste robotow wraz z zaplanowanymi krawedziami przejscia na grafie, ktore aktualnie moga zostac wykonane

        Parameters:
            graph_data (SupervisorGraphCreator): wygenerwany rozszerzony graf do planowania kolejnych zachowan robotow
            robots ({"id": Robot, "id": Robot, ...}): slownik robotow do ktorych beda przypisywane zadania
            tasks ([Task, Task, ...]): lista posortowanych zadan dla robotow

        Returns:
             ({robotId: {"taskId": string, "nextEdges": [(int,int), ...]/None, "endBeh": boolean/None},...})
              - plan dla robotow, ktory moze zostac od razu zrealizowany, gdyz nie ma kolizji; jesli niemożliwe jest
                zlecenie kolejnej krawedzi, bo jest zablokowana to None. Lista krawędzi związana jest z krawędzią
                przejazdu przez skrzyżowanie i krawędzią znajdującą się bezpośrednio za nim. Dla pozostałych przypadków
                jest to 1 krawędź przejścia.
        """
        self.planning_graph = PlanningGraph(graph_data)
        self.set_plan(robots, tasks)

        plan = {}  # kluczem jest id robota
        for robot_plan in self.robots_plan.get_busy_robots():
            if robot_plan.next_task_edges is not None:
                plan[robot_plan.id] = {"taskId": robot_plan.task.id, "nextEdges": robot_plan.next_task_edges,
                                       "endBeh": robot_plan.end_beh_edge}
        return plan

    def get_plan_selected_robot(self, graph_data, robots, tasks, robot_id):
        """
        Zwraca liste robotow wraz z zaplanowanymi krawedziami przejscia na grafie, ktore aktualnie moga zostac
        wykonane
        Parameters:
            graph_data (SupervisorGraphCreator): wygenerwany rozszerzony graf do planowania kolejnych zachowan robotow
            robots ({"id": Robot, "id": Robot, ...}): slownik robotow do ktorych beda przypisywane zadania
            tasks ([Task, Task, ...]): lista posortowanych zadan dla robotow
            robot_id (string): id robota dla ktorego ma byc zwrocony plan

        Returns:
             ({"taskId": string, "nextEdges": [(int,int), ...]/None, "endBeh": boolean/None},...}): plan dla robotow,
             ktory moze zostac od razu zrealizowany, gdyz nie ma kolizji, w przeciwnym wypadku None. Lista krawędzi
             związana jest z krawędzią przejazdu przez skrzyżowanie i krawędzią znajdującą się bezpośrednio za nim.
             Dla pozostałych przypadków jest to 1 krawędź przejścia.
        """
        self.planning_graph = PlanningGraph(graph_data)
        self.set_plan(robots, tasks)

        given_robot = self.robots_plan.get_robot_by_id(robot_id)
        if given_robot.next_task_edges is None:
            return None
        else:
            return {"taskId": given_robot.task.id, "nextEdges": given_robot.next_task_edges,
                    "endBeh": given_robot.end_beh_edge}

    def set_plan(self, robots, tasks):
        """
        Ustawia plan dla robotow.

        Parameters:
            robots ({"id": Robot, "id": Robot, ...}): slownik robotow do ktorych beda przypisywane zadania
            tasks ([Task, Task, ...]): lista posortowanych zadan dla robotow
        """
        self.set_tasks(tasks)
        self.init_robots_plan(robots)
        self.set_tasks_doing_by_robots()
        self.separate_swap_tasks()
        self.set_task_assigned_to_robots()
        self.set_other_tasks()

    def init_robots_plan(self, robots):
        """Ustawia roboty aktywnie dzialajace w systemie tzn. podlegajace planowaniu i przydzielaniu zadan.

        Parameters:
            robots ({"id": Robot, "id": Robot, ...}): slownik robotow do ktorych beda przypisywane zadania
        """
        self.robots_plan = RobotsPlanManager(robots, self.planning_graph.get_base_pois_edges())
        self.swap_tasks = {robot.id: None for robot in self.robots_plan.get_free_robots()}

    def set_tasks(self, tasks):
        """
        Ustawia menadzera nieprzeanalizowanych zadan w ramach planowania.

        Parameters:
            tasks ([Task, Task, ...]): lista posortowanych zadan dla robotow
        """

        self.unanalyzed_tasks_handler = TasksManager(tasks)

    def separate_swap_tasks(self):
        """
        Oddziela zadania do wykonania w POI od zadan wymiany baterii.
        """
        tasks_to_remove = []
        for task in self.unanalyzed_tasks_handler.tasks:
            if task.is_planned_swap():
                self.swap_tasks[task.robot_id] = task
                tasks_to_remove.append(task.id)

        self.unanalyzed_tasks_handler.remove_tasks_by_id(tasks_to_remove)

    def set_tasks_doing_by_robots(self):
        """
        Przypisanie zadan do robotow, ktore aktualnie pracuja i usuniecie ich z listy zadan do przeanalizowania.
        """

        # przypisanie zadan z POI w których aktualnie jest robot
        tasks_id_to_remove = []
        for unanalyzed_task in self.unanalyzed_tasks_handler.tasks:
            current_behaviour_is_goto = unanalyzed_task.get_current_behaviour().check_if_go_to()
            task_started = unanalyzed_task.check_if_task_started()
            for robot in self.robots_plan.get_free_robots():
                if robot.id == unanalyzed_task.robot_id and task_started and not current_behaviour_is_goto:
                    self.robots_plan.set_task(robot.id, unanalyzed_task)
                    self.set_task_edge(robot.id)
                    tasks_id_to_remove.append(unanalyzed_task.id)
        self.unanalyzed_tasks_handler.remove_tasks_by_id(tasks_id_to_remove)

        # przypisanie zadan z POI do ktorych aktualnie jedzie robot
        tasks_id_to_remove = []
        for unanalyzed_task in self.unanalyzed_tasks_handler.tasks:
            current_behaviour_is_goto = unanalyzed_task.get_current_behaviour().check_if_go_to()
            task_poi_goal = unanalyzed_task.get_poi_goal()
            task_started = unanalyzed_task.check_if_task_started()
            for robot in self.robots_plan.get_free_robots():
                robot_poi = self.planning_graph.get_poi(robot.edge)
                if (robot.id == unanalyzed_task.robot_id and task_started and current_behaviour_is_goto) \
                        and (robot_poi == task_poi_goal or robot_poi is None):
                    self.robots_plan.set_task(robot.id, unanalyzed_task)
                    self.set_task_edge(robot.id)
                    tasks_id_to_remove.append(unanalyzed_task.id)
        self.unanalyzed_tasks_handler.remove_tasks_by_id(tasks_id_to_remove)

        # przypisanie pozostalych zadan rowniez wykonywanych przez agv bedace w POI i majace jechac do innego
        # jesli kolejne POI docelowe ma wolna przestrzen do obslugi to robot wysylany jest do tego POI
        free_slots_in_poi = self.get_free_slots_in_pois()
        tasks_id_to_remove = []
        for unanalyzed_task in self.unanalyzed_tasks_handler.tasks:
            task_poi_goal = unanalyzed_task.get_poi_goal()
            task_started = unanalyzed_task.check_if_task_started()
            for robot in self.robots_plan.get_free_robots():
                robot_poi = self.planning_graph.get_poi(robot.edge)
                if robot.id == unanalyzed_task.robot_id and task_started and robot_poi != task_poi_goal:
                    self.robots_plan.set_task(robot.id, unanalyzed_task)
                    if free_slots_in_poi[task_poi_goal] > 0:
                        free_slots_in_poi[task_poi_goal] = free_slots_in_poi[task_poi_goal] - 1
                        self.set_task_edge(robot.id)
                    tasks_id_to_remove.append(unanalyzed_task.id)

        self.unanalyzed_tasks_handler.remove_tasks_by_id(tasks_id_to_remove)

    def set_task_assigned_to_robots(self):
        """
        Przypisanie do wolnych robotow zadan, ktore sa do nich przypisane. Po przypisaniu zadania
        usuwane jest ono z menadzera nieprzeanalizowanych zadan (unanalyzed_tasks_handler).
        """
        tasks_id_to_remove = []
        for unanalyzed_task in self.unanalyzed_tasks_handler.tasks:
            for robot in self.robots_plan.get_free_robots():
                if robot.task is None:
                    if unanalyzed_task.robot_id == robot.id and not unanalyzed_task.check_if_task_started():
                        task = unanalyzed_task
                        if robot.id in self.swap_tasks:
                            swap_task = self.swap_tasks[robot.id]
                            if type(swap_task) == Task:
                                task = self.planning_graph.select_next_task(unanalyzed_task, swap_task, robot, self.test_sim_time)  # TODO do usunięcia self.test_sim_time, tylko do testow symulacyjnych
                        self.robots_plan.set_task(robot.id, task)
                        self.set_task_edge(robot.id)
                        tasks_id_to_remove.append(task.id)

        self.unanalyzed_tasks_handler.remove_tasks_by_id(tasks_id_to_remove)

    def set_other_tasks(self):
        """
        Przypisanie zadan do pozostalych robotow z uwzglednieniem pierwszenstwa przydzialu zadan do robotow
        blokujacych POI.
        """
        init_time = time.time()
        free_robots_in_poi_task_assigned = True
        while True:

            free_robots_id = [robot.id for robot in self.robots_plan.get_free_robots()]
            blocking_robots_id = self.get_robots_id_blocking_used_poi()

            n_free_robots = len(free_robots_id)
            n_blocking_robots = len(blocking_robots_id)

            all_robots_tasks = self.get_free_task_to_assign(n_free_robots)
            blocking_robots_tasks = self.get_free_task_to_assign(n_blocking_robots)

            n_all_tasks = len(all_robots_tasks)
            n_blocking_robots_tasks = len(blocking_robots_tasks)

            all_free_tasks = self.unanalyzed_tasks_handler.get_all_unasigned_unstarted_tasks()
            if n_all_tasks == n_free_robots and n_all_tasks != 0:
                self.assign_tasks_to_robots(all_robots_tasks, free_robots_id)
                # przypisywanie zadań zakończone, bo każdy aktywny w systemie robot powinien już mieć zadanie
                break
            elif n_blocking_robots > 0 and n_blocking_robots_tasks != 0:
                # przypisanie zadan do robotow blokujacych POI
                self.assign_tasks_to_robots(blocking_robots_tasks, blocking_robots_id)
            elif n_free_robots > 0 and n_all_tasks != 0:
                # do wolnych robotow przypisanie zadan, jesli robot byl wolny i blokowal POI to traktowany jest jako
                # blokujacy slot do wyslania robota do POI
                self.assign_tasks_to_robots(all_robots_tasks, free_robots_id)
            elif n_free_robots > 0 and len(all_free_tasks) > 0 and free_robots_in_poi_task_assigned:
                # jesli sa dalej wolne roboty w POI to poszukiwane jest pierwsze mozliwe do wykonania zadanie dojazdu
                # do tego samego POI
                for robot_id in free_robots_id:
                    for task in all_free_tasks:
                        goal_id = task.get_poi_goal()
                        robot = self.robots_plan.robots[robot_id]
                        poi = None
                        if robot.edge is not None:
                            poi = self.planning_graph.get_poi(robot.edge)
                        elif robot.edge is None and robot.poi_id is not None:
                            poi = robot.poi_id
                        if goal_id == poi:
                            if robot.id in self.swap_tasks:
                                swap_task = self.swap_tasks[robot.id]
                                if type(swap_task) == Task:
                                    task = self.planning_graph.select_next_task(task, swap_task, robot,
                                                                                self.test_sim_time)
                            self.robots_plan.set_task(robot_id, task)
                            self.set_task_edge(robot_id)
                            self.unanalyzed_tasks_handler.remove_tasks_by_id([task.id])
                            break
                free_robots_in_poi_task_assigned = False
            else:
                # wysłanie pozostałych blokujących robotów na parkingi
                if n_blocking_robots != 0:
                    # jeśli jakieś roboty dalej blokują POI po przypisaniu zadań to wysyłane są do
                    # najbliższych prakingów/kolejek.
                    # weryfikacja czy nie ma robotów blokujących -> jeśli są to wysłać je do kolejki (roboty bez zadań)
                    # na parkingach raczej powinny być roboty wykonujące zadania, które nie mogą podjechać do stanowiska
                    self.send_free_robots_to_parking(blocking_robots_id)
                break

            current_time = time.time()
            if (current_time - init_time) > 5:
                raise TimeoutPlanning("Set other tasks loop is too long.")

    def set_task_edge(self, robot_id):
        """
        Ustawia kolejna krawedz przejscia dla robota o danym id.

        Parameters:
            robot_id (string): id robota dla ktorego ma zostac dokonana aktualizacja przejscia po krawedzi
        """
        robot = self.robots_plan.get_robot_by_id(robot_id)
        if robot.planning_on and robot.is_free:
            # robot wykonal fragment zachowania lub ma przydzielone zupelnie nowe zadanie
            # weryfikacja czy kolejna akcja jazdy krawedzia moze zostac wykonana
            start_node = robot.get_current_node()
            end_node = self.get_undone_behaviour_node(robot.task)
            path_nodes = self.planning_graph.get_path(start_node, end_node)
            next_edge = (path_nodes[0], path_nodes[1]) if len(path_nodes) >= 2 else robot.edge

            base_poi_edges = self.planning_graph.get_base_pois_edges()
            poi_id = robot.task.get_poi_goal()
            poi_group_id = self.planning_graph.get_group_id(base_poi_edges[poi_id])
            robot_current_group_id = self.planning_graph.get_group_id(robot.edge)
            poi_group_ids = [self.planning_graph.get_group_id(poi_edge) for poi_edge in base_poi_edges.values()]
            # dostepnosc kolejnego POI
            free_robots_in_poi = []
            for free_robot in self.robots_plan.get_free_robots():
                poi = self.planning_graph.get_poi(free_robot.edge)
                if poi is not None:
                    if not self.pois.check_if_queue(poi) and poi == poi_id:
                        free_robots_in_poi.append(free_robot.id)

            robots_using_poi = free_robots_in_poi
            current_goals = self.robots_plan.get_current_robots_goals()
            max_robots = self.planning_graph.get_max_allowed_robots_using_pois()[poi_id]
            for r_id in current_goals:
                if poi_id == current_goals[r_id]:
                    robots_using_poi.append(r_id)
            robots_using_poi = np.unique(robots_using_poi)
            free_slots = self.get_free_slots_in_pois()[poi_id]
            poi_availability = free_slots > 0 or poi_group_id == robot_current_group_id \
                               or robot_current_group_id not in poi_group_ids \
                               or (len(robots_using_poi) <= max_robots and robot_id in robots_using_poi)

            if self.is_edge_available(next_edge, robot_id) and poi_availability:
                # krawędź i POI są dostępne
                if self.planning_graph.is_intersection_edge(next_edge):
                    # 2. Weryfikacja czy dostępne są kolejne krawędzie przejścia
                    if len(path_nodes) >= 3:
                        edge_after_intersection = (path_nodes[1], path_nodes[2])
                        if self.is_edge_available(edge_after_intersection, robot_id):
                            # jeśli krawędź za skrzyżowaniem jest dostępna to możliwy jest wjazd i zjazd ze skrzyżowania
                            self.set_robot_next_step(robot, [next_edge, edge_after_intersection], len(path_nodes))
                else:
                    self.set_robot_next_step(robot, [next_edge], len(path_nodes))

    def is_edge_available(self, edge, robot_id):
        """
        Sprawdza czy możliwe jest wysłanie robota na daną krawędź. Jeśli krawędź należy do grupy to sprawdza czy ten
        sam robot jest w tej grupie, jeśli tak to kolejna krawędź z grupy jest dostępna dla takiego robota. Jeśli
        krawędź nie należy do grupy to weryfikuje czy dopisanie kolejnego robota nie spowoduje przekroczenia maksymalnej
        liczby robotów jaka może znajdować się na danej krawędzi.
        Parameters:
            edge ((int,int)): krawędź grafu
            robot_id (string): id robota, który ma być przypisany do krawędzi

        Returns:
            (boolean): True - krawędź dostępna dla robota, False gdy niedostępna
        """
        group_id = self.planning_graph.get_group_id(edge)
        robots_on_edge = []

        if group_id == 0:
            robots_on_edge += self.robots_plan.get_robots_id_on_edge(edge)
            robots_on_edge += self.planning_graph.get_robots_on_future_edge(edge)
            robots_on_edge += self.planning_graph.get_robots_on_edge(edge)
        else:
            group_edges = self.planning_graph.get_edges_by_group(group_id)
            for next_edge in group_edges:
                robots_on_edge += self.robots_plan.get_robots_id_on_edge(next_edge)
                robots_on_edge += self.planning_graph.get_robots_on_future_edge(next_edge)
                robots_on_edge += self.planning_graph.get_robots_on_edge(next_edge)

        robots_on_edge = list(np.unique(robots_on_edge))
        if robot_id in robots_on_edge:
            robots_on_edge.remove(robot_id)
        return self.planning_graph.get_max_allowed_robots(edge) > len(robots_on_edge)

    def set_robot_next_step(self, robot, execute_path, n_path_nodes):
        """
        Ustawia dozwolone krawędzie ruch dla robota oraz parametr odpowiedzialny za określenie czy po wykonaniu
        przejść podanymi krawędziami kończą one zachowanie.
        Parameters:
            robot (Robot): robot dla którego ma być przypisane zadania przejścia po kolejnych krawędziach grafu
            execute_path (list(tuple)/None): lista z kolejnymi krawędziami przejścia
            n_path_nodes (int) informuje o liczbie wygenerowanych węzłów w planie
        """
        # jesli krawedz konczy dane zachowanie to ustawiany jest parametr endBehEdge na True
        undone_behaviour = robot.task.get_current_behaviour()
        self.robots_plan.set_next_edges(robot.id, execute_path)
        for edge in execute_path:
            self.planning_graph.set_robot_on_future_edge(edge, robot.id)
        if undone_behaviour.get_type() != Behaviour.TYPES["goto"]:  # dock,wait,undock -> pojedyncze przejscie
            # na grafie
            self.robots_plan.set_end_beh_edge(robot.id, True)
        elif n_path_nodes <= 2:
            self.robots_plan.set_end_beh_edge(robot.id, True)
        else:
            self.robots_plan.set_end_beh_edge(robot.id, False)

    def get_robots_id_blocking_used_poi(self):
        """
        Zwraca liste robotow blokujacych POI do ktorego aktualnie jada roboty.

        Returns:
            ([robotId,...]): lista zawierajaca ID robotow, ktore blokuja POI.
        """
        temp_blocked_pois = self.pois.get_raw_pois_dict()
        for robot in self.robots_plan.get_free_robots():
            poi_id = self.planning_graph.get_poi(robot.edge)
            if poi_id is not None:
                if not self.pois.check_if_queue(poi_id):
                    if temp_blocked_pois[poi_id] is None:
                        temp_blocked_pois[poi_id] = []
                    temp_blocked_pois[poi_id] = temp_blocked_pois[poi_id] + [robot.id]

        robots_goals = self.robots_plan.get_current_robots_goals()
        blocking_robots = []
        for robot_id in robots_goals:
            poi_id = robots_goals[robot_id]
            if temp_blocked_pois[poi_id] is not None:
                blocking_robots = blocking_robots + temp_blocked_pois[poi_id]
        # zwracana jest lista robotów, które blokują POI do których aktualnie jadą roboty
        return blocking_robots

    def get_robots_using_pois(self):
        """
        Zwraca liczbe robotow, ktore aktualnie uzywaja danego POI. Przez uzywanie POI rozumie sie
        dojazd do POI, dokowanie, obsluge w POI lub oddokowanie. Jesli przydzielona krawedz przejscia dotyczy uzycia
        POI to rowniez jest uwzgledniana.

        Returns:
            ({poiId: string, ...}): Slownik z liczba robotow dla ktorego kluczem jest ID POI z bazy
                a wartoscia liczba robotow zmierzajaca/bedaca do danego POI
        """
        robots_to_poi = self.pois.get_raw_pois_dict()
        for i in robots_to_poi:
            robots_to_poi[i] = 0
        all_robots = self.robots_plan.robots.values()
        for robot in all_robots:
            goal_id = robot.get_current_destination_goal()
            if goal_id is not None:
                robots_to_poi[goal_id] = robots_to_poi[goal_id] + 1
        return robots_to_poi

    def get_free_slots_in_pois(self):
        """
            Funkcja zwraca liste dostepnych slotow dla kazdego z POI.
        Returns:
             ({poi_id: int, ...}) : liczba wolnych slotow dla kazdego poi.
        """
        robots_using_poi = self.get_robots_using_pois()
        free_robots_in_poi = {poi: 0 for poi in self.pois.pois}
        for robot in self.robots_plan.get_free_robots():
            poi_id = self.planning_graph.get_poi(robot.edge)
            if poi_id and poi_id != "0":
                free_robots_in_poi[poi_id] += 1

        max_robots_in_poi = self.planning_graph.get_max_allowed_robots_using_pois()
        free_slots_in_poi = {}
        for poi_id in robots_using_poi:
            diff = max_robots_in_poi[poi_id] - robots_using_poi[poi_id] - free_robots_in_poi[poi_id]
            free_slots_in_poi[poi_id] = 0 if diff < 0 else diff
        return free_slots_in_poi

    def get_free_task_to_assign(self, robots_numbers):
        """
        Zwraca liste zadan, ktore nalezy przypisac do robotow. Jako argument podawana jest liczba robotow
        ktore maja otrzymac zadania. Nie moze byc ona wieksza niz liczba robotow, ktore nie maja zadan i pracuja
        w trybie autonomicznym.

        Parameters:
            robots_numbers (int): liczba robotow dla ktorych powinny byc wygenerowane zadania

        Returns:
            ([Task,Task,...]): lista zadan, ktore nalezy przydzielic do robotow. Liczba zadan moze
                byc mniejsza niz liczba robotow co wynika z: mniejszej liczby zadan niz robotow; nie istnieja
                zadania w systemie, ktorych przypisanie powoduje spelnienie warunku, ze dla danego POI liczba
                przypisanych robotow jest mniejsza od maksymalnej liczby obslugiwanej w danym POI.
        """

        free_slots_in_poi = self.get_free_slots_in_pois()
        # Lista zadań, które nie są przypisane do robotów
        free_tasks = []
        all_free_tasks = self.unanalyzed_tasks_handler.get_all_unasigned_unstarted_tasks()
        for task in all_free_tasks:
            goal_id = task.get_poi_goal()
            if free_slots_in_poi[goal_id] > 0:
                free_slots_in_poi[goal_id] = free_slots_in_poi[goal_id] - 1
                free_tasks.append(task)
                if len(free_tasks) == robots_numbers:
                    break
        return free_tasks

    def assign_tasks_to_robots(self, tasks, robots_id):
        """
        Optymalne przypisanie zadan do robotow pod katem wykonania. W pierwszej kolejnosci zadanie o najwyzszym
        priorytecie dostaje robot, ktory wykona je najszybciej. Po przypisaniu zadania usuwane jest ono z listy
        all_tasks.

        Parameters:
            tasks ([Task, Task, ...]): lista posortowanych zadan ktore maja byc przypisane do robotow
            robots_id ([string, string, ...]): lista id robotow do ktorych maja zostac przypisane zadania
        """
        for task in tasks:
            fastest_robot_id = None
            min_task_time = None
            for r_id in robots_id:
                robot_node = self.robots_plan.get_robot_by_id(r_id).get_current_node()
                target_node = self.get_undone_behaviour_node(task)
                task_time = self.planning_graph.get_path_length(robot_node, target_node)
                if min_task_time is None or min_task_time > task_time:
                    fastest_robot_id = r_id
                    min_task_time = task_time

            # Przypisanie robota do zadania
            if fastest_robot_id in self.swap_tasks:
                swap_task = self.swap_tasks[fastest_robot_id]
                if type(swap_task) == Task:
                    robot = self.robots_plan.get_robot_by_id(fastest_robot_id)
                    task = self.planning_graph.select_next_task(task, swap_task, robot, self.test_sim_time)
            self.robots_plan.set_task(fastest_robot_id, task)
            self.set_task_edge(fastest_robot_id)
            robots_id.remove(fastest_robot_id)

        self.unanalyzed_tasks_handler.remove_tasks_by_id([task.id for task in tasks])

    def send_free_robots_to_parking(self, blocking_robots_id):
        """
        Tworzy i przypisuje do robotow blokujacych POI zadanie jazdy do Parkingu/Queue w celu odblokowania POI.

        Parameters:
            blocking_robots_id ([string, string,...]): lista id robotow, ktore blokuja POI

        TODO
            - utworzenie zadan dojazdu w wolne miejsce dla robotow blokujacych POI
            - przypisanie zadan do robotow
        """
        pass

    def send_busy_robots_to_parking(self, blocking_robots_id):
        """
        Tworzy i przypisuje do robotow blokujacych POI zadanie jazdy do Parkingu/Queue w celu odblokowania POI.

        Parameters:
            blocking_robots_id ([string,string,...]): lista id robotow, ktore blokuja POI

        TODO
            - przypisanie zadan do robotow
            - obsluga robotow ktore wykonuja inne zadanie i musza zjechac na parking
        """
        pass

    def get_undone_behaviour_node(self, task):
        """
        Wybiera z zadania pierwsze zachowanie, ktore nie zostalo jeszcze ukonczone, dla zadan nie rozpoczetych
        jest to pierwsze zachowanie jakie wystepuje w zadaniu.

        Parameters:
            task (Task): zadanie dla ktorego okreslany jest wezel do ktorego ma dotrzec robot w zaleznosci
                od kolejnego zadania do wykonania

        Returns:
            (int): id wezla z grafu rozszerzonego na ktorym opiera sie tworzenie zadan
        """
        poi_id = task.get_poi_goal()
        behaviour = task.get_current_behaviour()
        goal_node = None
        if behaviour.get_type() == Behaviour.TYPES["goto"]:
            goal_node = self.planning_graph.get_end_go_to_node(poi_id, self.pois.get_type(poi_id))
        elif behaviour.get_type() == Behaviour.TYPES["dock"]:
            goal_node = self.planning_graph.get_end_docking_node(poi_id)
        elif behaviour.get_type() == Behaviour.TYPES["wait"] or behaviour.get_type() == Behaviour.TYPES["bat_ex"]:
            goal_node = self.planning_graph.get_end_wait_node(poi_id, self.pois.get_type(poi_id))
        elif behaviour.get_type() == Behaviour.TYPES["undock"]:
            goal_node = self.planning_graph.get_end_undocking_node(poi_id)
        return goal_node
