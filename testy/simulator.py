import graph_creator as gc
import networkx as nx
import matplotlib.pyplot as plt
import copy
import dispatcher as disp
import testy.simulator_gui as sim_gui
from testy.test_data import pois_raw, node_dict, edge_dict
import time
from dispatcher import Task, PlanningGraph

SIMULATION_TIME = 5000 # w sekundach
TIME_INACTIVE = 120 # w sekundach, czas w ktorym polozenie robotow nie zmienilo sie
TIME_STEP_SUPERVISOR_SIM = 5 # w sekundach
TIME_STEP_ROBOT_SIM = 1 # w sekundach
TIME_STEP_DISPALY_UPDATE = 0.05 # krok przerwy w wyswietlaniu symulacji, pozniej mozna calkowicie pominac
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
        self.end_beh_edge = None
        self.battery = robot_data.battery

        self.beh_duration = 0
        self.beh_time = 0
        self.task_id = None
        self.end_beh = False


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

            battery_usage = 0.2 * robot.battery.stand_usage + 0.8* robot.battery.drive_usage
            robot.battery.capacity -= self.step_time/(battery_usage*60*60)

    def set_task(self, task):
        """
        Opowiada za ustawienie kolejnej krawedzi przejscia dla robota.
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
                robot.end_beh = task["endBeh"]
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

    def get_robots_status(self):
        """
        Zwraca liste robotow wraz ze statusem czy wolny, czy wykonuje zadanie

        Returns:
            (list(RobotSim)): lista robotow z symulacji wraz z ich stanem
        """
        return self.robots

    def print_robot_status(self):
        """
        Funkcja wyswietla aktualny stan robotow.
        """
        print("---------------------------Robots---------------------------")
        print("{:<9} {:<8} {:<8} {:<12} {:<9} {:<7} {:<6}".format('robotId', 'taskId', 'edge', 'behDuration', 'behTime',
                                                                  'isFree', 'endBeh'))
        for robot in self.robots:
            print("{:<9} {:<6} {:<15} {:<10} {:<7} {:<6} {:<6}".format(str(robot.id), str(robot.task_id),
                                                                       str(robot.edge),
                                                                       str(robot.beh_duration), str(robot.beh_time),
                                                                       str(robot.is_free),
                                                                       str(robot.end_beh)))

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
        self.tasks = []
        self.tasks_count = 0
        self.done_tasks = 0
        self.done_swap_tasks = 0
        self.flag_task_state_updated = True
        self.add_tasks(tasks)
        self.plan = {}
        self.update_robots_on_edge(robots_state_list)

    def run(self, robots_state_list):
        """
        Parameters:
            robots_state_list (list(RobotSim)): stan robotow wychodzacy z symulatora
        """

        dispatcher = disp.Dispatcher(self.graph, self.convert_robots_state_to_dispatcher_format(robots_state_list))
        self.update_robots_on_edge(robots_state_list)
        self.update_tasks_states(robots_state_list)
        robots = self.convert_robots_state_to_dispatcher_format(robots_state_list)

        self.plan = dispatcher.get_plan_all_free_robots(self.graph, robots, self.tasks)
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
        Aktualizacja stanu zadan na podstawie danych otrzymanych z symulatora robotow, informuje o zakonczeniu
        zadan lub ich trwaniu

        Attributes:
            robots_state_list (list(RobotSim)): stan robotow wychodzacy z symulatora
        """
        active_states = [state for state in robots_state_list if state.task_id is not None]
        for robotState in active_states:
            if robotState.planning_on and robotState.is_free and robotState.end_beh:
                for task in self.tasks:
                    if task.id == robotState.task_id:
                        self.flag_task_state_updated = True
                        if task.current_behaviour_index == (len(task.behaviours) - 1):
                            # zakonczono zadanie
                            task.status = disp.Task.STATUS_LIST["DONE"]
                        else:
                            # zakonczono zachowanie, ale nie zadanie
                            task.current_behaviour_index = task.current_behaviour_index + 1

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

        for edge in self.graph.graph.edges:
            self.graph.graph.edges[edge[0], edge[1]]["robots"] = [robot.id for robot in robots_state_list
                                                                    if robot.edge == edge]

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

    def config(self, graph):
        tasks = self.gui.task_panel.tasks
        self.robots_sim = RobotsSimulator(self.gui.robots_creator.robots, TIME_STEP_ROBOT_SIM)
        self.supervisor = Supervisor(graph, tasks, self.robots_sim .get_robots_status())

    def run(self):
        i = 0
        start_inactive_time = 0
        while True:
            time.sleep(TIME_STEP_DISPALY_UPDATE)  # czas odswiezania kroku
            if i % TIME_STEP_SUPERVISOR_SIM == 0:
                robots_state_list = self.robots_sim.get_robots_status()  # aktualny stan robotow po inicjalizacji
                self.supervisor.run(robots_state_list)

                # Zmiana stanu robota, przypisanie go do nowej krawedzi
                if TURN_ON_ANIMATION_UPDATE:
                    self.gui.top_panel.set_valid_graph_status(self.is_valid_graph())
                    disp_robot_format = self.supervisor.convert_robots_state_to_dispatcher_format(robots_state_list)
                    self.gui.update_robots_table(disp_robot_format)  # aktualny stan robotow

                if self.robots_sim.flag_robot_state_updated:
                    start_inactive_time = i
                    if TURN_ON_ANIMATION_UPDATE:
                        self.gui.update_graph(self.supervisor.graph)
                        self.robots_sim.flag_robot_state_updated = False

                # Aktualizacja stanu zadan
                if self.supervisor.flag_task_state_updated and TURN_ON_ANIMATION_UPDATE:
                    self.supervisor.flag_task_state_updated = False

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

            if i % TIME_STEP_ROBOT_SIM == 0:
                self.robots_sim.set_tasks(self.supervisor.get_robots_command())
                self.robots_sim.run()
                if TURN_ON_ANIMATION_UPDATE:
                    discharged, crit_bat, warn_bat = self.robots_sim.get_wrong_battery_state()
                    self.gui.top_panel.set_discharged_robots(discharged)
                    self.gui.top_panel.set_battery_critical_robots(crit_bat)
                    self.gui.top_panel.set_battery_warning_robots(warn_bat)

            if i > SIMULATION_TIME:
                # przekrocozno czas symulacji
                print("przekroczono czas symulacji")
                break
            elif len(self.supervisor.tasks) == 0:
                # brak zadan do zlecenia
                print("brak zadan")
                break
            elif (i - start_inactive_time) > TIME_INACTIVE:
                # polozenie robotow na krawedziach nie zmienilo sie w czasie TIME_INACTIVE
                print("Przekroczono czas nieaktywnosci aktualizacji symulacji")
                break

            i += 1

    def is_valid_graph(self):
        new_graph = PlanningGraph(self.supervisor.graph)
        for edge in new_graph.graph.edges(data=True):
            group_id = edge[2]["edgeGroupId"]
            if group_id == 0:
                if len(edge[2]["robots"]) > edge[2]["maxRobots"]:
                    return False
            else:
                try:
                    new_graph.get_robots_in_group_edge((edge[0],edge[1]))
                except:
                    return False
        return True
