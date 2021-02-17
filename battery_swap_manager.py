from dispatcher import Battery, Robot, Task
from datetime import datetime, timedelta
from graph_creator import base_node_type


SWAP_TIME = 3.0  # czas w [min] przed ktorym powinna nastapic wymiana baterii zanim przekroczony
                 # zostanie prog ostrzegawczy
SWAP_TIME_BEFORE_ALERT = 5.0  # czas w [min] przed ktorym powinna nastapic wymiana baterii zanim przekroczony
                              # zostanie prog ostrzegawczy
REPLAN_THRESHOLD = 1  # czas w [min], jesli zaplanowana wymiana odbedzie sie pozniej niz podana wartosc
                      # to nalezy przeplanowac zadania

class BatterySwapManager:
    """
    Klasa odpowiedzialna za planowanie wymian w robotach. Dla kazdego robota przechowuje w pamieci jedna wymiane
    (zaplanowana lub aktualnie zlecona do wykonania).
    Attributes:
        swap_plan (dict(robot_id: {"new": False, "updated": False, "in_progress": False, "tasks": []})): plan wymian z
            lista zadan (tasks), new - informuje o tym czy jest to nowe zadanie do przekazania, updated - nastapila
            aktualizacja planu dla pierwszego zadania; "in_progress" - informuje czy zadanie zostalo przydzielone
            i jest aktualnie wykonywane, przy aktualizacji planu jest ono uwzględniane i nie mozna w nim zmienic
            start_time
        swap_stations (list): lista id POI, ktore sa stacja wymiany baterii
        last_id (int): id ostatnio przydzielonego zadania, wykorzystywane do wygenerowania unikalnego id zadania wymiany
            baterii
    """
    def __init__(self, robots, pois_raw_data):
        """
        Parameters:
            robots (list(Robot)): Lista robotow dla ktorych nalezy ulozyc plan wymian
            pois_raw_data: ([{"id": string, "pose": (float,float)), "type": gc.base_node_type["..."]}, ...]) - lista
                POI w systemie
        """
        self.swap_plan = {robot.id: {"new": False, "updated": False, "in_progress": False, "tasks": []}
                          for robot in robots}
        self.swap_stations = self.get_swap_stations()
        self.last_id = 0
        self.new_task = True
        self.updated_task = False
        self.init_plan(robots)
    # OK
    def run(self, robots):
        if self.check_if_replan_required(robots):
            self.create_new_plan(robots)
    # OK
    def init_plan(self, robots):
        """
        Tworzy plan wymian dla robotow w systemie
        Parameters:
            robots (list(Robot)): Lista robotow dla ktorych nalezy ulozyc plan wymian
        """
        now = datetime.now()
        n = len(self.swap_stations)
        i = 0
        for robot in robots:
            swap_station_poi = self.swap_stations[i]
            time_to_allert = robot.battery.get_time_to_critical_allert()
            SWAP_TIME = (now + timedelta(minutes=time_to_allert) - timedelta(minutes=self.SWAP_TIME) -
                         timedelta(minutes=self.SWAP_TIME_BEFORE_ALERT)).strftime("%Y-%m-%d %H:%M:%S")
            self.add_task(SWAP_TIME, swap_station_poi, robot.id)
            i += 1
            if i >= n:
                i = 0

    def create_new_plan(self, robots):
        """
        Parameters:
            robots (list(Robot)): Lista robotow dla ktorych nalezy ulozyc plan wymian
        """
        now = datetime.now()
        n = len(self.swap_stations)
        i = 0
        robot_ids = [robot.id for robot in robots]
        planned_robot_id = self.swap_plan.keys()

        # usuwanie z planu robotow, ktorych nie ma w systemie
        untracked_robots = [rid for rid in planned_robot_id if rid not in robot_ids]
        for robot_id in untracked_robots:
            del self.swap_plan[robot_id]

        for robot in robots:
            swap_station_poi = self.swap_stations[i]
            if robot.id not in self.swap_plan:
                # brak zaplanowanej wymiany, moze wynikac z pojawienia sie nowego robota w systemie
                self.swap_plan[robot.id] = {"new": False, "updated": False, "in_progress": False, "tasks": []}
                time_to_allert = robot.battery.get_time_to_critical_allert()
                SWAP_TIME = (now + timedelta(minutes=time_to_allert) - timedelta(minutes=self.SWAP_TIME) -
                             timedelta(minutes=self.SWAP_TIME_BEFORE_ALERT)).strftime("%Y-%m-%d %H:%M:%S")
                self.add_task(SWAP_TIME, swap_station_poi, robot.id)
                i += 1
                if i >= n:
                    i = 0
            elif len(self.swap_plan[robot.id]["tasks"]) == 0:
                # brak zadan wymiany dla robota, nalezy wprowadzic nowe
                time_to_allert = robot.battery.get_time_to_critical_allert()
                SWAP_TIME = (now + timedelta(minutes=time_to_allert) - timedelta(minutes=self.SWAP_TIME) -
                             timedelta(minutes=self.SWAP_TIME_BEFORE_ALERT)).strftime("%Y-%m-%d %H:%M:%S")
                self.add_task(SWAP_TIME, swap_station_poi, robot.id)
                i += 1
                if i >= n:
                    i = 0





                if self.swap_plan[robot.id][0].status == Task.STATUS_LIST["TO_DO"]:
                    swap_station_poi = self.swap_stations[i]
                    time_to_warn = robot.battery.get_time_to_critical_allert()
                    SWAP_TIME = (now + timedelta(minutes=time_to_warn) - timedelta(minutes=self.SWAP_TIME)).strftime("%Y-%m-%d %H:%M:%S")
                    self.swap_plan[robot.id] = []
                    self.add_task(SWAP_TIME, swap_station_poi, robot.id)
                    i += 1
                    if i >= n:
                        i = 0


    # OK
    def add_task(self, planned_swap_time, swap_station_poi, robot_id):
        """
        Dodaje zadanie do planu wymian
        """
        data = {"id": "swap_" + str(self.last_id),
                "behaviours": [{"id": "1", "parameters": {"to": swap_station_poi, "name": disp.Behaviour.TYPES["goto"]}},
                               {"id": "2", "parameters": {"name": disp.Behaviour.TYPES["dock"]}},
                               {"id": "3", "parameters": {"name": disp.Behaviour.TYPES["bat_ex"]}},
                               {"id": "4", "parameters": {"name": disp.Behaviour.TYPES["undock"]}}],
                "current_behaviour_index": -1,  # index tablicy nie zachowania
                "status": Task.STATUS_LIST["TO_DO"],
                "robot": robot_id,
                "start_time": planned_swap_time,  # 2018-06-29 07:37:27
                "weight": 3, # TODO  ustalic wartosc z jaka wchodza inne zadania
                "priority": 3} # TODO ustalic wartosc z jaka wchodza inne zadania
        self.swap_plan[robot_id]["tasks"].append(Task(data))
        self.last_id += 1
    # OK
    def get_swap_stations(self, pois_raw_data):
        """
        Parameters:
            pois_raw_data: ([{"id": string, "pose": (float,float)), "type": gc.base_node_type["..."]}, ...]) - lista
                POI w systemie
        """
        stations_ids = []
        for poi in pois_raw_data:
            if poi["type"] == base_node_type["charger"]:
                stattions_ids.append(poi["id"])
        return stations_ids
    # OK
    def get_new_swap_tasks(self):
        """
        Zwraca liste nowych zadan do wprowadzenia do listy zadan.

        Returns:
             (list(Task)): lista zadan z wymiana baterii
        """
        new_tasks = []
        for robot_data in self.swap_plan.values():
            for tasks in robot_data["tasks"]:
                if len(tasks) > 0 and robot_data["new"]:
                    robot_data["new"] = False
                    new_tasks.append(tasks[0])

        self.new_task = False
        return new_tasks
    # OK
    def get_tasks_to_update(self):
        """
        Zwraca liste zadan wymiany baterii do zaktualizowania.

        Returns:
             (list(Task)): lista zadan z wymiana baterii do zaktualizowania
        """
        update_tasks = []
        for robot_data in self.swap_plan.values():
            for tasks in robot_data["tasks"]:
                if len(tasks) > 0 and robot_data["update"] and not robot_data["new"]:
                    robot_data["update"] = False
                    update_tasks.append(tasks[0])

        self.updated_task = False
        return update_tasks
    # OK
    def started_swap_task(self, robot_id):
        """
        Ustawienie potwierdzenia, ze zadanie wymiany zostalo rozpoczete.
        """
        if len(self.swap_plan[robot_id]["tasks"]) > 0:
            self.swap_plan[robot_id]["in_progress"] = True
    # OK
    def finished_swap_task(self, robot_id):
        """
        Usuwanie zakonczonego zadania o podanym id z planu i ustawienie, ze pojawilo sie nowe zadanie do zlecenia.
        """
        if len(self.swap_plan[robot_id]["tasks"]) > 0:
            self.new_task = True
            self.swap_plan[robot_id]["new"] = True
            self.swap_plan[robot_id]["updated"] = False
            self.swap_plan[robot_id]["in_progress"] = False
            del self.swap_plan[robot_id][0]
    # OK
    def check_if_replan_required(self, robots):
        """
        Parameters:
            robots (list(Robot)): Lista robotow dla ktorych nalezy ulozyc plan wymian
        """
        now = datetime.strptime(datetime.now().strftime("%Y-%m-%d %H:%M:%S"), ("%Y-%m-%d %H:%M:%S"))
        for robot in robots:
            if robot.id not in self.swap_plan:
                return True

            robot_plan = self.swap_plan[robot.id]["tasks"]
            if len(robot_plan) > 0:
                time_to_warn = robot.battery.get_time_to_critical_allert()
                planned_diff = (datetime.strptime(robot_plan[0].start_time,
                                                  ("%Y-%m-%d %H:%M:%S")) - now)/timedelta(minutes=1)
                if planned_diff > 0 and time_to_warn > 0:
                    if (planned_diff - time_to_warn) < self.REPLAN_THRESHOLD:
                        return True

        return False


