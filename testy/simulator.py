import graph_creator as gc
import networkx as nx
import matplotlib.pyplot as plt
import matplotlib
import copy
import dispatcher as disp
import testy.simulator_gui as sim_gui
from testy.test_data import pois_raw, node_dict, edge_dict
import time
from dispatcher import Task, PlanningGraph, PlaningGraphError
import os
import datetime
import csv
import numpy as np
import json
import plotly as py
import plotly.figure_factory as ff
import pandas as pd
from random import randint
import ipywidgets

SIMULATION_TIME = 5000 # w sekundach
TIME_INACTIVE = 120 # w sekundach, czas w ktorym polozenie robotow nie zmienilo sie
TIME_STEP_SUPERVISOR_SIM = 5 # w sekundach
TIME_STEP_ROBOT_SIM = 1 # w sekundach
TIME_STEP_DISPALY_UPDATE = 0 #0.05 # krok przerwy w wyswietlaniu symulacji, pozniej mozna calkowicie pominac
                                # teraz tylko do wyswietlania i pokazania animacji
TURN_ON_ANIMATION_UPDATE = True


class RobotSim(disp.Robot):
    """
    Klasa przechowujaca informacje o pojedynczym robocie do ktorego beda przypisywane zadania

    Attributes:
        id (string): id robota
        edge ((int,int)): krawedz na ktorej aktualnie znajduje sie robot
        poi_id (string): id poi w ktorym znajduje sie robot
        planning_on (bool): informuje czy robot jest w trybie planownaia
        is_free (bool): informuje czy robot aktualnie wykonuje jakies zachowanie czy nie
        time_remaining (float): czas do ukonczenia zachowania
        task (Task): zadanie przypisane do robota
        next_task_edge ((string,string)): informuje o kolejnej krawedzi przejscia ktora nalezy wyslac do robota
        end_beh_edge (bool): informuje czy zachowanie po przejsciu krawedzia zostanie ukonczone

        beh_duration (float): czas wykonywnaia zachowania
        beh_time (float): czas trwania zachowania
        task_id (int): id przypisanego zadania
        end_beh (bool): czy przejscie jest koncowe, aby wykonac zachowanie skladowae zadania
    """
    def __init__(self, robot_data):
        """
        Parameters:
            robot_data (disp.Robot): dane o wygenerowanym robocie
        """
        self.id = robot_data.id
        self.edge = robot_data.edge
        self.poi_id = robot_data.poi_id
        self.planning_on = robot_data.planning_on
        self.is_free = robot_data.is_free
        self.time_remaining = robot_data.time_remaining
        self.task = None
        self.next_task_edge = None
        self.end_beh_edge = False
        self.battery = robot_data.battery

        self.beh_duration = 0
        self.beh_time = 0
        self.task_id = None


class RobotsSimulator:
    """
    Klasa do obslugi symulacji ruchu robotow.
    Attributes:
        robots (list(RobotSim)): lista z danymi o robotach
        step_time (float): krok symulacji robotow [s]
        flag_robot_state_updated (bool): flaga informujaca o przypisaniu nowego zachowania do
                                         wykonania dla robota
    """

    def __init__(self, robots, step_time):
        """
        Parameters:
            robots (list(Robot)): lista z danymi o robotach
            step_time (float): krok symulacji robotow [s]
        """
        self.step_time = step_time
        self.robots = [RobotSim(data) for data in robots]
        self.flag_robot_state_updated = True

    def run(self):
        """
        Odpowiada za wykonanie kroku symulacji zgodnie ze "step_time"
        """
        for robot in self.robots:
            robot.beh_duration = robot.beh_duration + self.step_time
            # warunek zakonczenia wykonywania zachowania
            robot.is_free = robot.beh_duration >= robot.beh_time

            battery_usage = 0.2 * robot.battery.stand_usage + 0.8 * robot.battery.drive_usage
            robot.battery.capacity -= self.step_time/(battery_usage*60*60*self.step_time)
            if robot.battery.capacity < 0:
                robot.battery.capacity = 0

    def set_task(self, task):
        """
        Odpowiada za ustawienie kolejnej krawedzi przejscia dla robota.
        Parameters:
             task ({"robotId": int, "taskId": int, "taskDuration": int, 'nextEdge': (int, int), "endBeh": bool}):
                    fragment zadania do wykonania
        """
        for robot in self.robots:
            if robot.id == task["robotId"]:
                self.flag_robot_state_updated = True
                robot.task_id = task["taskId"]
                robot.beh_time = task["taskDuration"]
                robot.beh_duration = 0
                robot.is_free = False
                robot.edge = task["nextEdge"]
                robot.end_beh_edge = task["endBeh"]
                break

    def set_tasks(self, tasks_list):
        """
        Ustawia nowe zadania dla robotow
        Attributes:
            tasks_list ([{"robotId": int, "taskId": int, "taskDuration": int, 'nextEdge': (int, int),
                         "endBeh": bool},...]): lista kolejnych fragmentow zadan dla robotow
        """
        for task in tasks_list:
            self.set_task(task)

    def print_robot_status(self):
        """
        Funkcja wyswietla aktualny stan robotow.
        """
        print("---------------------------Robots---------------------------")
        print("{:<9} {:<8} {:<8} {:<12} {:<9} {:<7} {:<6}".format('robotId', 'taskId', 'edge', 'behDuration', 'behTime',
                                                                  'isFree', 'end_beh_edge'))
        for robot in self.robots:
            print("{:<9} {:<6} {:<15} {:<10} {:<7} {:<6} {:<6}".format(str(robot.id), str(robot.task_id),
                                                                       str(robot.edge),
                                                                       str(robot.beh_duration), str(robot.beh_time),
                                                                       str(robot.is_free),
                                                                       str(robot.end_beh_edge)))

    def get_wrong_battery_state(self):
        """
        Sprawdza stan robotow i zlicza liczbe rozladowanych.
        Returns
            (int): liczba rozladowanych robotow
        """
        n_discharged = 0
        n_critical = 0
        n_warning = 0
        for robot in self.robots:
            battery_capacity = robot.battery.capacity
            if battery_capacity == 0:
                n_discharged += 1
            elif battery_capacity < robot.battery.get_critical_capacity():
                n_critical += 1
            elif battery_capacity < robot.battery.get_warning_capacity():
                n_warning += 1
        return n_discharged, n_critical,  n_warning


class Supervisor:
    """
    Attributes:
        graph (SupervisorGraphCreator): rozbudowany graf do obslugi ruchu robotow
        tasks (list(Task)): lista zadan do wykonania przez roboty
        updated_tasks (list(Task)): lista zaktualizowanych zadan (w trakcie wykonywania, nowe zachowanie,
                                    zakonczone zadanie)
        tasks_count (int): zlicza liczbe wszystkich zadan pojawiajacych sie w systemie
        done_tasks (int): licznik wykonanych zadan
        done_swap_tasks (int): licznik wykonanych zadan wymiany baterii
        flag_task_state_updated (bool): flaga informujaca o zmianie statusu zadania, pojawieniu sie nowego zadania w
                                        systemie
        plan ({robotId: {"taskId": string, "nextEdge": (string,string)/None, "endBeh": boolean/None},...}) - plan z
            dispatchera dla robotow
    """
    def __init__(self, graph, tasks, robots_state_list):
        """
        Parameters:
            graph (SupervisorGraphCreator): rozbudowany graf do obslugi ruchu robotow
            tasks (list(Task)): lista zadan dla robotow
            robots_state_list (list(RobotSim)): aktualny stan robotow z symulacji
        """
        self.graph = graph
        self.pois_edges = PlanningGraph(graph).get_base_pois_edges()
        self.tasks = []
        self.updated_tasks = []
        self.tasks_count = 0
        self.done_tasks = 0
        self.done_swap_tasks = 0
        self.flag_task_state_updated = True
        self.add_tasks(tasks)
        self.plan = {}
        self.update_robots_on_edge(robots_state_list)
        self.next_step_set = {robot.id: False for robot in robots_state_list}

    def update_data(self, robots_state_list):
        self.update_robots_on_edge(robots_state_list)
        self.update_tasks_states(robots_state_list)

    def update_plan(self, robots_state_list):
        robots = self.convert_robots_state_to_dispatcher_format(robots_state_list)
        dispatcher = disp.Dispatcher(self.graph, robots)
        self.plan = dispatcher.get_plan_all_free_robots(self.graph, robots, self.tasks)

        for robot_id in self.plan.keys():
            self.next_step_set[robot_id] = True

    def run(self, robots_state_list):
        """
        Parameters:
            robots_state_list (list(RobotSim)): stan robotow wychodzacy z symulatora
        """
        self.update_data(robots_state_list)
        self.update_plan(robots_state_list)
        self.start_tasks()

    def print_graph(self, plot_size=(45, 45)):
        """
        Odpowiada za wyswietlenie grafu z liczba aktualnie znajdujacych sie na krawedzi robotow.
        """
        graphData = self.graph.graph
        plt.figure(figsize=plot_size)
        node_pos = nx.get_node_attributes(graphData, "pos")

        robots_on_edges_id = nx.get_edge_attributes(graphData, "robots")
        robots_on_edges = {}
        for edge in robots_on_edges_id:
            robots_on_edges[edge] = len(robots_on_edges_id[edge])
        node_col = [graphData.nodes[i]["color"] for i in graphData.nodes()]

        nx.draw_networkx(graphData, node_pos, node_color=node_col, node_size=3000, font_size=25,
                         with_labels=True, font_color="w", width=4)
        nx.draw_networkx_edge_labels(graphData, node_pos, node_color=node_col,
                                     edge_labels=robots_on_edges, font_size=30)
        plt.show()
        plt.close()

    def print_graph_weights(self, plot_size=(45, 45)):
        """
        Odpowiada za wyswietlenie grafu z wagami na krawedziach
        """
        graphData = self.graph.get_graph()
        plt.figure(figsize=plot_size)
        node_pos = nx.get_node_attributes(graphData, "pos")

        weights = nx.get_edge_attributes(graphData, "weight")
        node_col = [graphData.nodes[i]["color"] for i in graphData.nodes()]

        nx.draw_networkx(graphData, node_pos, node_color=node_col, node_size=3000, font_size=25,
                         with_labels=True, font_color="w", width=4)
        nx.draw_networkx_edge_labels(graphData, node_pos, node_color=node_col,
                                     edge_labels=weights, font_size=30)
        plt.show()
        plt.close()

    def add_task(self, task):
        """
        Parameters:
            task_raw_data (disp.Task): surowe dane o zadaniu
        """
        self.tasks.append(task)
        self.tasks_count += 1
        self.flag_task_state_updated = True

    def add_tasks(self, tasks):
        """
        Parameters:
            tasks_raw_data (list(disp.task)): dane o zadaniach
        """
        for task in tasks:
            self.add_task(task)

    def get_task_by_id(self, task_id):
        given_task = None
        for task in self.tasks:
            if task.id == task_id:
                given_task = task
        return given_task

    def update_tasks_states(self, robots_state_list):
        """
        Aktualizacja stanu zadan na podstawie danych otrzymanych z symulatora robotow, kończy aktualnie wykonywane
        zachowanie lub zadanie

        Attributes:
            robots_state_list (list(RobotSim)): stan robotow wychodzacy z symulatora
        """
        active_states = [state for state in robots_state_list if state.task_id is not None]
        for robotState in active_states:
            if robotState.planning_on and robotState.is_free and robotState.end_beh_edge \
                    and self.next_step_set[robotState.id]:
                for task in self.tasks:
                    if task.id == robotState.task_id:
                        self.flag_task_state_updated = True
                        self.next_step_set[robotState.id] = False
                        if task.current_behaviour_index == (len(task.behaviours) - 1):
                            # zakonczono zadanie
                            task.status = disp.Task.STATUS_LIST["DONE"]
                        else:
                            # zakonczono zachowanie, ale nie zadanie
                            task.current_behaviour_index = task.current_behaviour_index + 1
                        self.updated_tasks.append(copy.deepcopy(task))

        # usuwanie ukonczonych zadan
        for task in self.tasks:
            if task.status == disp.Task.STATUS_LIST["DONE"]:
                self.tasks.remove(task)
                if task.is_planned_swap():
                    self.done_swap_tasks += 1
                else:
                    self.done_tasks += 1

    def start_tasks(self):
        """
        Ustawia status in progress dla przydzielonego zadania
        """
        for robot_id in self.plan:
            plan = self.plan[robot_id]
            for task in self.tasks:
                if plan["taskId"] == task.id and task.current_behaviour_index == -1:
                    self.flag_task_state_updated = True
                    task.robot_id = robot_id
                    task.status = disp.Task.STATUS_LIST["IN_PROGRESS"]
                    task.current_behaviour_index = 0
                    self.updated_tasks.append(copy.deepcopy(task))
                    break

    def get_robots_command(self):
        """
        Zwraca liste komend przekazywanych do symulatora robotow.
        tasksList ([{'robotId': int, 'nextEdge': (int, int), 'taskId': int, 'endBeh': bool, "taskDuration": int},...])
        """
        tasksList = []
        for i in self.plan.keys():
            robotPlan = copy.deepcopy(self.plan[i])
            robot_command = {"robotId": i, "nextEdge": robotPlan["nextEdge"],
                             "taskId": robotPlan["taskId"], "endBeh": robotPlan["endBeh"],
                             "taskDuration": self.graph.graph.edges[robotPlan["nextEdge"]]["weight"]}
            # robotCommand["taskDuration"] = 1
            tasksList.append(robot_command)
        return tasksList

    def update_robots_on_edge(self, robots_state_list):
        """
        Parameters:
            robots_state_list (list(RobotSim)): stan robotow wychodzacy z symulatora
        """
        for robot in robots_state_list:
            if robot.edge is None and robot.poi_id is not None:
                robot.edge = self.pois_edges[robot.poi_id]

        for edge in self.graph.graph.edges:
            robots_on_edge = [robot.id for robot in robots_state_list if robot.edge == edge]
            self.graph.graph.edges[edge[0], edge[1]]["robots"] = robots_on_edge

    def print_data(self):
        print("\n---------------------------Stan zadan---------------------------")
        print("{:<8}{:<10}{:<20}{:<20}{:<10}{:<15}{}".format("taskId", "robotId", "WEIGHT", "start_time",
                                                             "status", "curr_beh_id", "behaviours"))
        for task in self.tasks:
            header = "{} {} {} ".format("id", "name", "goalId")
            data = []
            for behaviour in task.behaviours:
                if "to" in behaviour.parameters:
                    data.append("{:<83} {:<3} {:<6} {}".format("", str(behaviour.id),
                                                               str(behaviour.parameters["name"]),
                                                               str(behaviour.parameters["to"])))
                else:
                    data.append("{:<83} {:<3} {}".format("", str(behaviour.id),
                                                         str(behaviour.parameters["name"])))

            table = '\n'.join([header] + data)
            print("{:<11}{:<11}{:<7}{:<30}{:<15}{:<10}{}".format(str(task.id), str(task.robot_id), str(task.weight),
                                                                 str(task.start_time), str(task.status),
                                                                 str(task.current_behaviour_index), table))

        print("\n---------------------------Nowy plan---------------------------")
        print("{:<9} {:<8} {:<12} {:<7} {:<5}".format('robotId', 'taskId', 'next edge', 'endBeh', 'taskDuration'))

        for plan in self.get_robots_command():
            print("{:<12} {:<6} {:<12} {:<10} {:<7}".format(str(plan['robotId']), str(plan["taskId"]),
                                                            str(plan["nextEdge"]),
                                                            str(plan["endBeh"]), str(plan["taskDuration"])))

    def convert_robots_state_to_dispatcher_format(self, robots_state_list):
        """
        Parameters:
            robots_state_list (list(RobotSim)) - stan listy robotow z symulatora

        Returns:
            ({"id": Robot, "id": Robot, ...}): slownik robotow do ktorych beda przypisywane zadania
        """
        robots_dict = {}
        for robot in robots_state_list:
            robots_dict[robot.id] = disp.Robot({"id": robot.id, "edge": robot.edge, "planningOn": robot.planning_on,
                                              "isFree": robot.is_free, "timeRemaining":  robot.time_remaining,
                                              "poiId": robot.poi_id})

        return robots_dict


class Simulator:
    def __init__(self, pois_raw):
        self.gui = sim_gui.TestGuiPanel(pois_raw)
        self.start_inactive_sup_time = 0

    def config(self, graph):
        tasks = self.gui.task_panel.tasks
        self.robots_sim = RobotsSimulator(self.gui.robots_creator.robots, TIME_STEP_ROBOT_SIM)
        self.supervisor = Supervisor(graph, tasks, self.robots_sim.robots)
        self.log_data = DataLogger()
        self.log_data.save_graph(graph.graph)
        self.gui.export_log_config(self.log_data.file_path)

    def run(self):
        i = 0
        self.supervisor.update_data(self.robots_sim.robots)
        while True:
            time.sleep(TIME_STEP_DISPALY_UPDATE)  # czas odswiezania kroku
            if i % TIME_STEP_SUPERVISOR_SIM == 0:
                self.update_supervisor(i)

            if i % TIME_STEP_ROBOT_SIM == 0:
                self.robots_sim.run()
                if TURN_ON_ANIMATION_UPDATE:
                    discharged, crit_bat, warn_bat = self.robots_sim.get_wrong_battery_state()
                    self.gui.top_panel.set_discharged_robots(discharged)
                    self.gui.top_panel.set_battery_critical_robots(crit_bat)
                    self.gui.top_panel.set_battery_warning_robots(warn_bat)

                self.log_data.save_battery_state(i, self.robots_sim.robots)

            if i > SIMULATION_TIME:
                # przekrocozno czas symulacji
                print("przekroczono czas symulacji")
                break
            elif len(self.supervisor.tasks) == 0:
                # brak zadan do zlecenia
                print("brak zadan")
                break
            elif (i - self.start_inactive_sup_time) > TIME_INACTIVE:
                # polozenie robotow na krawedziach nie zmienilo sie w czasie TIME_INACTIVE
                print("Przekroczono czas nieaktywnosci aktualizacji symulacji")
                break

            i += 1

    def update_supervisor(self, sim_time):
        robots_state_list = self.robots_sim.robots  # aktualny stan robotow po inicjalizacji
        self.supervisor.run(robots_state_list)
        self.robots_sim.set_tasks(self.supervisor.get_robots_command())
        self.supervisor.update_robots_on_edge(self.robots_sim.robots)


        is_valid = self.is_valid_graph(sim_time)
        # Zmiana stanu robota, przypisanie go do nowej krawedzi
        if TURN_ON_ANIMATION_UPDATE:
            self.gui.top_panel.set_valid_graph_status(is_valid)
            disp_robot_format = self.supervisor.convert_robots_state_to_dispatcher_format(robots_state_list)
            self.gui.update_robots_table(disp_robot_format)  # aktualny stan robotow

        if self.robots_sim.flag_robot_state_updated:
            self.start_inactive_sup_time = sim_time
            self.log_data.save_graph_traffic(sim_time, self.supervisor.graph)
            if TURN_ON_ANIMATION_UPDATE:
                self.gui.update_graph(self.supervisor.graph)
                self.robots_sim.flag_robot_state_updated = False

        # Aktualizacja stanu zadan
        if self.supervisor.flag_task_state_updated:
            self.supervisor.flag_task_state_updated = False
            self.log_data.save_data(sim_time, self.supervisor, self.robots_sim.robots)
            self.supervisor.updated_tasks = []

            if TURN_ON_ANIMATION_UPDATE:
                self.gui.update_tasks_table(self.supervisor.tasks)
                self.gui.top_panel.set_all_tasks_number(self.supervisor.tasks_count)
                self.gui.top_panel.set_all_swap_tasks_number(self.supervisor.done_swap_tasks)

                n_to_do_tasks = 0
                n_in_progress_tasks = 0
                for task in self.supervisor.tasks:
                    if not task.is_planned_swap():
                        if task.status == Task.STATUS_LIST["TO_DO"]:
                            n_to_do_tasks += 1
                        elif task.status == Task.STATUS_LIST["IN_PROGRESS"]:
                            n_in_progress_tasks += 1

                self.gui.top_panel.set_all_tasks_to_do_number(n_to_do_tasks)
                self.gui.top_panel.set_all_tasks_in_progress_number(n_in_progress_tasks)
                self.gui.top_panel.set_all_tasks_done_number(self.supervisor.done_tasks)

    def is_valid_graph(self, sim_time):
        new_graph = PlanningGraph(self.supervisor.graph)
        for edge in new_graph.graph.edges(data=True):
            group_id = edge[2]["edgeGroupId"]
            if group_id == 0:
                if len(edge[2]["robots"]) > edge[2]["maxRobots"]:
                    return False
            else:
                try:
                    new_graph.get_robots_in_group_edge((edge[0], edge[1]))
                except PlaningGraphError as error:
                    self.log_data.save_error(sim_time, error)
                    return False
        return True


class DataLogger:
    """
    Attributes:
        tasks_start_time (dict): slownik z kluczem bedacym id zadania, a wartoscia {"sim_time": float, "task":disp.Task}
        behaviours (dict): slownik z kluczem bedacym id zadaniaa,a  wartoscia {"sim_time": float, "task":disp.Task}
    """
    def __init__(self):
        currentDT = datetime.datetime.now()
        folderName = str(currentDT.month) + "-" + str(currentDT.day) + "_" + str(currentDT.hour) + "-" + str(
            currentDT.minute) + "-" + str(currentDT.second)
        self.file_path = os.path.expanduser("~") + "/SMART_logs/dispatcher/" + folderName + "/"
        self.tasks_start_time = {}
        self.behaviours = {}
        self.init_logs_storage()

    def save_data(self, sim_time, supervisor, robots_sim):
        """
        Parameters:
            sim_time (int): czas symulacji
            supervisor (Supervisor): dane z supervisora
            tasks (list(disp.Task)): lista zadan ze zaktualizowanym stanem
            robots (list(RobotSim)): lista z danymi o robotach
        """
        for task in supervisor.updated_tasks:
            robot_edge = None
            # print("task robot id: ", str(task.robot_id))
            for robot in robots_sim:
                if robot.id == task.robot_id:
                    # print("robot edge ", str(robot.edge))
                    robot_edge = robot.edge
                    break

            is_return_go_to = None if robot_edge is None else supervisor.graph.is_return_edge(robot_edge)
            if task.status == disp.Task.STATUS_LIST["IN_PROGRESS"]:
                if task.current_behaviour_index == 0:
                    # rozpoczeto nowe zachowanie z nowego zadania
                    self.tasks_start_time[task.id] = {"sim_time": sim_time, "task": copy.deepcopy(task)}
                    self.behaviours[task.id] = {"sim_time": sim_time, "task": copy.deepcopy(task)}
                else:
                    self.save_behaviour(sim_time, self.behaviours[task.id]["task"], is_return_go_to)
                    self.behaviours[task.id] = {"sim_time": sim_time, "task": copy.deepcopy(task)}

            elif task.status == disp.Task.STATUS_LIST["DONE"]:
                with open(self.file_path + "tasks.csv", 'a') as csv_file:
                    writer = csv.writer(csv_file)
                    # ['task_id', 'robot_id', 'start_time', 'end_time', 'behaviours']
                    data = np.concatenate((task.id, task.robot_id, self.tasks_start_time[task.id]["sim_time"], sim_time,
                                           self.get_behaviours_string(task)), axis=None)
                    writer.writerow(data)
                csv_file.close()
                self.save_behaviour(sim_time, task, is_return_go_to)
                del self.tasks_start_time[task.id]
                del self.behaviours[task.id]

    def get_behaviours_string(self, task):
        """
        Dokonuje konwersji zachowan z zadania na tekst
        Parameters:
            task (disp.Task): zadanie
        """
        behaviours = ""
        n = len(task.behaviours)
        i = 1
        for behaviour in task.behaviours:
            behaviours += behaviour.get_type()
            if behaviour.check_if_go_to():
                behaviours += ": " + str(behaviour.get_poi())
            if i != n:
                behaviours += ", "
            i += 1

        return behaviours

    def init_logs_storage(self):
        """
        This function is responsible for initialize log files storage
        """

        # Create target directory & all intermediate directories if don't exists
        if not os.path.exists(self.file_path):
            os.makedirs(self.file_path)

        # ustawienie naglowkow w logu od błędów
        with open(self.file_path + "errors.csv", 'a') as csv_file:
            writer = csv.writer(csv_file)
            writer.writerow(['sim_time', 'error'])
        csv_file.close()

        # ustawienie naglowkow w logu od czasu trwania zadan
        with open(self.file_path + "tasks.csv", 'a') as csv_file:
            writer = csv.writer(csv_file)
            writer.writerow(['task_id', 'robot_id', 'start_time', 'end_time', 'behaviours'])
        csv_file.close()

        # ustawienie naglowkow w logu od czasu trwania zachowan
        with open(self.file_path + "behaviours.csv", 'a') as csv_file:
            writer = csv.writer(csv_file)
            writer.writerow(['task_id', 'robot_id', 'start_time', 'end_time', 'beh_type', 'poi', 'return_go_to'])
        csv_file.close()

        # ustawienie naglowkow w logu od monitorowania stanu naladowania baterii
        with open(self.file_path + "batteries.csv", 'a') as csv_file:
            writer = csv.writer(csv_file)
            writer.writerow(['sim_time', 'robot_id', 'battery_lvl', 'warning_lvl', 'critical_lvl', 'max_lvl'])
        csv_file.close()

        # ustawienie naglowkow w logu od monitorowania obciazenia krawedzi grafu
        with open(self.file_path + "graph_traffic.csv", 'a') as csv_file:
            writer = csv.writer(csv_file)
            writer.writerow(['sim_time', 'group_id', 'start_node_id', 'end_node_id', 'n_robots', 'max_robots', 'traffic'])
        csv_file.close()

    def save_behaviour(self, sim_time, task, is_return_go_to):
        with open(self.file_path + "behaviours.csv", 'a') as csv_file:
            writer = csv.writer(csv_file)
            # ['task_id', 'robot_id', 'start_time', 'end_time', 'beh_type', 'poi']
            data = np.concatenate((task.id, task.robot_id, self.behaviours[task.id]["sim_time"], sim_time,
                                   task.get_current_behaviour().get_type(), task.get_poi_goal(), is_return_go_to),
                                  axis=None)
            writer.writerow(data)
        csv_file.close()

    def save_error(self, sim_time, error):
        with open(self.file_path + "errors.csv", 'a') as csv_file:
            writer = csv.writer(csv_file)
            # ['sim_time', 'error']
            data = np.concatenate((sim_time, error), axis=None)
            writer.writerow(data)
        csv_file.close()

    def save_battery_state(self, sim_time, robots):
        """
        Parameters:
            sim_time (float): czas symulacji
            robots (list(RobotSim)): lista robotow ze stanem baterii
        """

        with open(self.file_path + "batteries.csv", 'a') as csv_file:
            writer = csv.writer(csv_file)
            # ['sim_time', 'robot_id', 'battery_lvl', 'warning_lvl', 'critical_lvl', 'max_lvl']
            for robot in robots:
                data = np.concatenate((sim_time, robot.id, robot.battery.capacity, robot.battery.get_warning_capacity(),
                                       robot.battery.get_critical_capacity(), robot.battery.max_capacity), axis=None)
                writer.writerow(data)
        csv_file.close()

    def save_graph_traffic(self, sim_time, graph):
        """
        Parameters:
            sim_time (float): czas symulacji
            graph (SupervisorGraphCreator): rozbudowany graf do obslugi ruchu robotow
        """
        with open(self.file_path + "graph_traffic.csv", 'a') as csv_file:
            writer = csv.writer(csv_file)
            # ['sim_time', 'group_id', 'edge_id', 'n_robots', 'max_robots', 'traffic']
            for edge in graph.graph.edges(data=True):
                n_robots = len(edge[2]["robots"])
                max_robots = edge[2]["maxRobots"] if "maxRobots" in edge[2] else 1
                traffic = n_robots/max_robots * 100
                data = np.concatenate((sim_time, edge[2]["edgeGroupId"], edge[0], edge[1], n_robots, max_robots,
                                       traffic), axis=None)
                writer.writerow(data)
        csv_file.close()

    def save_graph(self, graph):
        json.dump(dict(nodes=[[n, graph.nodes[n]] for n in graph.nodes()],
                       edges=[[u, v, graph.edges[u,v]] for u, v in graph.edges()]),
                  open(self.file_path + "graph.json", 'w'), indent=2)


class DataAnalyzer:
    def __init__(self, folder_name):
        self.file_log_path = os.path.expanduser("~") + "/SMART_logs/dispatcher/" + folder_name + "/"
        self.file_path = self.file_log_path + "result/"
        self.today = datetime.datetime.now()

        self.graph_data = pd.read_csv(self.file_log_path + "graph_traffic.csv")
        self.graph_data = self.graph_data.sort_values(by='sim_time')
        self.graph = nx.DiGraph()
        d = json.load(open(self.file_log_path + "graph.json"))
        self.graph.add_nodes_from(d['nodes'])
        self.graph.add_edges_from(d['edges'])

        # Create target directory & all intermediate directories if don't exists
        if not os.path.exists(self.file_path):
            os.makedirs(self.file_path)

        self.time_slider = ipywidgets.IntSlider()
        self._update_button = ipywidgets.ToggleButton(value=False, description='update_button', icon='check',
                                                 layout=ipywidgets.Layout(visibility = 'hidden'))

    def run(self):
        self.create_tasks_gant()
        self.create_behaviours_gant()
        self.create_pois_gant()
        self.create_pois_gant_all_robots()
        self.create_graph_edges_no_group()
        self.create_graph_edges_groups()
        self.create_battery_lvl_plot()

    def create_tasks_gant(self):
        csv_data = pd.read_csv(self.file_log_path + "tasks.csv")
        csv_data = csv_data.sort_values(by=['robot_id', 'start_time'])

        x_posed = []
        for index, data in csv_data.iterrows():
            x_pos = (data["end_time"] - data["start_time"]) / 2 + data["start_time"]
            x_posed.append(self.today + datetime.timedelta(seconds=x_pos))
        csv_data["x_poses"] = x_posed

        plot_data = []
        i = 0
        for index, data in csv_data.iterrows():
            task_color = "color1" if i % 2 == 0 else "color2"
            start_time = self.today + datetime.timedelta(seconds=data["start_time"])
            end_time = self.today + datetime.timedelta(seconds=data["end_time"])
            plot_data.append(dict(Task=str(data["robot_id"]), Start=start_time, Finish=end_time,
                                  Resource=task_color))
            i += 1

        fig = ff.create_gantt(plot_data, index_col='Resource',
                              title='Plan wykonanych zadan', show_colorbar=True,
                              group_tasks=True,
                              showgrid_x=True, showgrid_y=True)
        ## add anotations
        robots_y_value = {}
        n = len(csv_data.robot_id.unique()) - 1
        for robot in csv_data.robot_id.unique():
            robots_y_value[robot] = n
            n -= 1

        text_font = dict(size=12, color='black')
        for index, data in csv_data.iterrows():
            y = robots_y_value[data["robot_id"]]
            fig['layout']['annotations'] += tuple(
                    [dict(x=data["x_poses"], y=y, text=str(data["task_id"]), textangle=0, showarrow=False,
                          font=text_font)])

        fig['layout']['yaxis']['title'] = "ID/nazwa robotów"
        py.offline.plot(fig, filename=self.file_path + 'tasks_gant.html', auto_open=False)

    def create_behaviours_gant(self):
        csv_data = pd.read_csv(self.file_log_path + "behaviours.csv")
        csv_data = csv_data.sort_values(by='robot_id')
        colors = {'WAIT': 'rgb({},{},{})'.format(255, 0, 0),
                  'DOCK': 'rgb({},{},{})'.format(0, 0, 255),
                  'UNDOCK': 'rgb({},{},{})'.format(0, 0, 100),
                  'BAT_EX': 'rgb({},{},{})'.format(235, 0, 0)}

        x_posed = []
        for index, data in csv_data.iterrows():
            x_pos = (data["end_time"] - data["start_time"]) / 2 + data["start_time"]
            x_posed.append(self.today + datetime.timedelta(seconds=x_pos))
        csv_data["x_poses"] = x_posed

        plot_data = []
        i = 0
        for index, data in csv_data.iterrows():
            resource_name = (data["beh_type"] + "_" + str(data["poi"])) if data["beh_type"] == "GO_TO" else \
                data["beh_type"]
            start_time = self.today + datetime.timedelta(seconds=data["start_time"])
            end_time = self.today + datetime.timedelta(seconds=data["end_time"])
            plot_data.append(dict(Task=str(data["robot_id"]), Start=start_time, Finish=end_time,
                                  Resource=resource_name))
            if resource_name not in colors:
                colors[resource_name] = 'rgb({},{},{})'.format(0,randint(0,255),0)
            i += 1

        fig = ff.create_gantt(plot_data, index_col='Resource',
                              title='Plan wykonanych zachowan w zadaniach', show_colorbar=True,
                              group_tasks=True, showgrid_x=True, showgrid_y=True, colors = colors)
        ## add anotations
        robots_y_value = {}
        n = len(csv_data.robot_id.unique()) - 1
        for robot in csv_data.robot_id.unique():
            robots_y_value[robot] = n
            n -= 1

        text_font = dict(size=12, color='black')
        for index, data in csv_data.iterrows():
            y = robots_y_value[data["robot_id"]]
            fig['layout']['annotations'] += tuple(
                    [dict(x=data["x_poses"], y=y, text=str(data["task_id"]), textangle=0, showarrow=False,
                          font=text_font)])
        fig['layout']['yaxis']['title'] = "ID/nazwa robotów"
        py.offline.plot(fig, filename=self.file_path + 'behaviours_gant.html', auto_open=False)

    def create_pois_gant(self):
        csv_data = pd.read_csv(self.file_log_path + "behaviours.csv")
        csv_data = csv_data.sort_values(by='robot_id')
        colors = ['rgb({},{},{})'.format(255, 0, 0), 'rgb({},{},{})'.format(0, 0, 255)]
        df = pd.DataFrame(csv_data)
        filtered_data = df.query('beh_type != "GO_TO" | return_go_to')

        x_poses = []
        for index, data in filtered_data.iterrows():
            x_pos = (data["end_time"] - data["start_time"]) / 2 + data["start_time"]
            x_poses.append(self.today + datetime.timedelta(seconds=x_pos))
        filtered_data["x_poses"] = x_poses

        for poi in sorted(filtered_data.poi.unique()):
            filtered_csv_data = filtered_data.loc[filtered_data["poi"] == poi]
            sorted_csv_data = filtered_csv_data.sort_values(by='start_time')
            plot_data = []
            i = 0
            for index, data in sorted_csv_data.iterrows():
                start_time = self.today + datetime.timedelta(seconds=data["start_time"])
                end_time = self.today + datetime.timedelta(seconds=data["end_time"])
                plot_data.append(dict(Task="POI {}".format(poi), Start=start_time, Finish=end_time,
                                      Resource=colors[i % 2]))
                i += 1
            fig = ff.create_gantt(plot_data, index_col='Resource',
                                  title='Zadania wykonywane dla POI {}'.format(poi), show_colorbar=True,
                                  group_tasks=True, showgrid_x=True, showgrid_y=True, colors = colors)

            text_font = dict(size=12, color='black')
            for index, data in filtered_csv_data.iterrows():
                fig['layout']['annotations'] += tuple(
                        [dict(x=data["x_poses"], y=0, text=str(data["task_id"]), textangle=0, showarrow=False,
                              font=text_font)])
            fig['layout']['yaxis']['title'] = "ID/nazwa robotów"
            py.offline.plot(fig, filename=self.file_path + 'poi_{}_gant.html'.format(poi), auto_open=False)

    def create_pois_gant_all_robots(self):
        csv_data = pd.read_csv(self.file_log_path + "behaviours.csv")
        csv_data = csv_data.sort_values(by='robot_id')
        colors = {'WAIT': 'rgb({},{},{})'.format(255, 0, 0),
                  'DOCK': 'rgb({},{},{})'.format(0, 0, 255),
                  'UNDOCK': 'rgb({},{},{})'.format(0, 0, 100),
                  'BAT_EX': 'rgb({},{},{})'.format(235, 0, 0),
                  'RETURN_GO_TO': 'rgb({},{},{})'.format(0, 255, 0)}
        df = pd.DataFrame(csv_data)
        filtered_data = df.query('beh_type != "GO_TO" | return_go_to')

        x_poses = []
        for index, data in filtered_data.iterrows():
            x_pos = (data["end_time"] - data["start_time"]) / 2 + data["start_time"]
            x_poses.append(self.today + datetime.timedelta(seconds=x_pos))
        filtered_data["x_poses"] = x_poses

        for poi in sorted(filtered_data.poi.unique()):
            filtered_csv_data = filtered_data.loc[filtered_data["poi"] == poi]
            plot_data = []
            i = 0
            for index, data in filtered_csv_data.iterrows():
                beh_type = "RETURN_GO_TO" if "GO_TO" in data["beh_type"] else data["beh_type"]
                start_time = self.today + datetime.timedelta(seconds=data["start_time"])
                end_time = self.today + datetime.timedelta(seconds=data["end_time"])
                plot_data.append(dict(Task=str(data["robot_id"]), Start=start_time, Finish=end_time,
                                      Resource=beh_type))
                i += 1
            fig = ff.create_gantt(plot_data, index_col='Resource',
                                  title='Zadania wykonywane dla POI {}'.format(poi), show_colorbar=True,
                                  group_tasks=True, showgrid_x=True, showgrid_y=True, colors = colors)
            ## add anotations
            robots_y_value = {}
            n = len(filtered_csv_data.robot_id.unique()) - 1
            for robot in filtered_csv_data.robot_id.unique():
                robots_y_value[robot] = n
                n -= 1

            text_font = dict(size=12, color='black')
            for index, data in filtered_csv_data.iterrows():
                y = robots_y_value[data["robot_id"]]
                fig['layout']['annotations'] += tuple(
                        [dict(x=data["x_poses"], y=y, text=str(data["task_id"]), textangle=0, showarrow=False,
                              font=text_font)])
            fig['layout']['yaxis']['title'] = "ID/nazwa robotów"
            py.offline.plot(fig, filename=self.file_path + 'poi_{}_gant_robots.html'.format(poi), auto_open=False)

    def create_graph_edges_no_group(self):
        csv_data = pd.read_csv(self.file_log_path + "graph_traffic.csv")
        csv_data = csv_data.sort_values(by=['sim_time', 'start_node_id', 'end_node_id'])
        df = pd.DataFrame(csv_data)
        filtered_data = df.query('group_id == 0')
        time_series = sorted(filtered_data.sim_time.unique())

        plot_data = []
        i = 0
        for index, data in filtered_data.iterrows():
            step_index = time_series.index(data['sim_time']) + 1
            try:
                step_time = time_series[step_index] - data['sim_time']
            except IndexError:
                step_time = TIME_STEP_SUPERVISOR_SIM

            start_time = self.today + datetime.timedelta(seconds=data['sim_time'])
            end_time = start_time + datetime.timedelta(seconds=float(step_time))
            edge_name = str(data['start_node_id']) + ", " + str(data['end_node_id'])
            plot_data.append(dict(Task=edge_name, Start=start_time, Finish=end_time, Resource=data["traffic"]))
            i += 1
        fig = ff.create_gantt(plot_data, index_col='Resource', title='Krawędzie grafu nienależące do grup',
                              show_colorbar=True, group_tasks=True, showgrid_x=True, showgrid_y=True, colors = "Reds")

        fig['layout']['yaxis']['title'] = "ID krawędzi"
        py.offline.plot(fig, filename=self.file_path + 'graph_edges_no_group.html', auto_open=False)

    def create_graph_edges_groups(self):
        csv_data = pd.read_csv(self.file_log_path + "graph_traffic.csv")
        csv_data = csv_data.sort_values(by=['sim_time', 'group_id', 'start_node_id', 'end_node_id'])
        df = pd.DataFrame(csv_data)
        filtered_data = df.query('group_id != 0')
        time_series = sorted(filtered_data.sim_time.unique())

        plot_data = []
        i = 0
        for index, data in filtered_data.iterrows():
            step_index = time_series.index(data['sim_time']) + 1
            try:
                step_time = time_series[step_index] - data['sim_time']
            except IndexError:
                step_time = TIME_STEP_SUPERVISOR_SIM

            start_time = self.today + datetime.timedelta(seconds=data['sim_time'])
            end_time = start_time + datetime.timedelta(seconds=float(step_time))
            edge_name = str(data["group_id"]) + " | " + str(data["start_node_id"]) + ", " + str(data["end_node_id"])
            plot_data.append(dict(Task=edge_name, Start=start_time, Finish=end_time, Resource=data["traffic"]))
            i += 1
            start_time = end_time
        fig = ff.create_gantt(plot_data, index_col='Resource', title='Krawędzie grafu należące do grup',
                              show_colorbar=True, group_tasks=True, showgrid_x=True, showgrid_y=True, colors = "Reds")

        fig['layout']['yaxis']['title'] = "ID krawędzi"
        fig['layout']['height'] = 800
        py.offline.plot(fig, filename=self.file_path + 'graph_edges_groups.html', auto_open=False)

    def create_battery_lvl_plot(self):
        csv_data = pd.read_csv(self.file_log_path + "batteries.csv")
        csv_data = csv_data.sort_values(by='robot_id')

        fig, ax = plt.subplots(figsize=(20, 20))
        ax.set_title('Stan naladowania baterii w robotach')
        ax.set_xlabel('czas [s]')
        ax.set_ylabel('bateria [Ah]')

        filtered_data = csv_data.loc[csv_data["robot_id"] == csv_data.robot_id.unique()[0]]
        x = filtered_data.sim_time
        ax.plot(x, filtered_data.warning_lvl, label="warning_lvl", color='orange')
        ax.plot(x, filtered_data.critical_lvl, label="critical_lvl", color='red')

        for robot_id in sorted(csv_data.robot_id.unique()):
            filtered_data = csv_data.loc[csv_data["robot_id"] == robot_id]
            x = filtered_data.sim_time
            y = filtered_data.battery_lvl
            ax.plot(x, y, label=str(robot_id))

        ax.legend()
        plt.savefig(self.file_path + "batteries.png")

    def animate_graph(self, traffic_graph=True):
        time_series = sorted(self.graph_data.sim_time.unique())
        step = time_series[1] - time_series[0]

        play = ipywidgets.Play(value=time_series[0], min=time_series[0], max=time_series[-1], step=step,
                               description="Press play", disabled=False, interval=500)

        self.time_slider.value = time_series[0]
        self.time_slider.min = time_series[0]
        self.time_slider.max = time_series[-1]
        self.time_slider.step = step

        ipywidgets.jslink((play, 'value'), (self.time_slider, 'value'))
        timeline = ipywidgets.HBox([play, self.time_slider])
        self.time_slider.observe(self._slider_callback, 'value')
        if traffic_graph:
            ipywidgets.interact(self._update_graph_traffic, button=self._update_button)
        else:
            ipywidgets.interact(self._update_graph_robots_count, button=self._update_button)
        return timeline

    def _update_graph_traffic(self, button):
        plt.figure(figsize=(15, 15))

        df = pd.DataFrame(self.graph_data)
        filtered_data = df.query('sim_time == {}'.format(self.time_slider.value))
        for index, row in filtered_data.iterrows():
            self.graph.edges[row.start_node_id, row.end_node_id]["traffic"] = int(row["traffic"])
            red = row["traffic"]/100.0
            color = (red,0,0,1) if red > 0.0 else (0,0,0,0.25)
            self.graph.edges[row.start_node_id, row.end_node_id]["color"] = color

        node_pos = nx.get_node_attributes(self.graph, "pos")
        traffic = nx.get_edge_attributes(self.graph, "traffic")
        node_col = [self.graph.nodes[i]["color"] for i in self.graph.nodes()]
        edge_col = [self.graph.edges[i]["color"] for i in self.graph.edges()]

        nx.draw_networkx(self.graph, node_pos, node_color=node_col, edge_color=edge_col, node_size=150, font_size=9,
                         with_labels=True, font_color="w", width=3)
        #nx.draw_networkx_edge_labels(self.graph, node_pos, edge_labels=traffic, font_size=10)

    def _update_graph_robots_count(self, button):
        plt.figure(figsize=(15, 15))

        df = pd.DataFrame(self.graph_data)
        filtered_data = df.query('sim_time == {}'.format(self.time_slider.value))
        for index, row in filtered_data.iterrows():
            self.graph.edges[row.start_node_id, row.end_node_id]["maxRobots"] = row["n_robots"]

        node_pos = nx.get_node_attributes(self.graph, "pos")
        max_robots = nx.get_edge_attributes(self.graph, "maxRobots")
        node_col = [self.graph.nodes[i]["color"] for i in self.graph.nodes()]

        nx.draw_networkx(self.graph, node_pos, node_color=node_col, node_size=50, font_size=7,
                         with_labels=True, font_color="w", width=3)
        nx.draw_networkx_edge_labels(self.graph, node_pos, edge_labels=max_robots, font_size=10)

    def _slider_callback(self, widget):
        self._update_button.value = not self._update_button.value
