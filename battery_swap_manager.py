from dispatcher import Battery, Robot, Task, Behaviour
from datetime import datetime, timedelta
from graph_creator import base_node_type


SWAP_TIME = 3.0  # czas [min] wymiany baterii w stacji
SWAP_TIME_BEFORE_ALERT = 5.0  # czas w [min] przed ktorym powinna rozpoczac sie wymiana baterii zanim przekroczony
                              # zostanie prog ostrzegawczy
REPLAN_THRESHOLD = 1  # czas w [min], jesli zaplanowana wymiana odbedzie sie pozniej niz podana wartosc
                      # to nalezy przeplanowac zadania

class BatterySwapManager:
    """
    Klasa odpowiedzialna za planowanie wymian w robotach. Dla kazdego robota przechowuje w pamieci jedna wymiane
    (zaplanowana lub aktualnie zlecona do wykonania).
    Attributes:
        swap_plan (dict(robot_id: {"new": False, "updated": False, "in_progress": False, "tasks": list(Task})): plan
            wymian z lista zadan (tasks).
            - new - informuje o tym czy jest to nowe zadanie do przekazania
            - updated - nastapila aktualizacja planu dla pierwszego zadania
            - in_progress - informuje czy zadanie zostalo przydzielone i jest aktualnie wykonywane, przy aktualizacji
              planu jest ono uwzględniane i nie mozna w nim zmienic start_time
            - tasks - plan kolejnych wymian
        swap_stations (list): lista id POI, ktore sa stacja wymiany baterii
        last_id (int): id ostatnio przydzielonego zadania, wykorzystywane do wygenerowania unikalnego id zadania wymiany
            baterii
        swap_station_id (string): id ostatnio przydzielonej stacji
        new_task (bool): flaga informujaca o nowym zadaniu do pobrania z planu
        updated_task (bool): flaga informujaca o aktualizacji zadan w planie
    """

    def __init__(self, robots, pois_raw_data):
        """
        Parameters:
            robots ({"id": Robot, "id": Robot, ...}): slownik robotow do ktorych nalezy przypisac zadania wymiany
            pois_raw_data: ([{"id": string, "pose": (float,float)), "type": gc.base_node_type["..."]}, ...]) - lista
                POI w systemie
        """
        self.swap_plan = {i: {"new": False, "updated": False, "in_progress": False, "tasks": []} for i in robots}
        self.swap_stations = self._get_swap_stations(pois_raw_data)
        self.last_id = 0
        self.swap_station_id = 0
        self.new_task = True
        self.updated_task = False

        self._init_plan(robots)

    def run(self, robots):
        """
        Parameters:
            robots ({"id": Robot, "id": Robot, ...}): slownik robotow do ktorych nalezy przypisac zadania wymiany
        """
        if self._is_replan_required(robots):
            self._create_new_plan(robots)

    def get_new_swap_tasks(self):
        """
        Zwraca liste nowych zadan do wprowadzenia do listy zadan.

        Returns:
             (list(Task)): lista zadan z wymiana baterii
        """
        new_tasks = []
        for robot_data in self.swap_plan.values():
            tasks = robot_data["tasks"]
            if len(tasks) > 0 and robot_data["new"]:
                robot_data["new"] = False
                new_tasks.append(tasks[0])

        self.new_task = False
        return new_tasks

    def get_tasks_to_update(self):
        """
        Zwraca liste zadan, ktore zostaly zaktualizowane w wyniku przeplanowania.

        Returns:
             (list(Task)): lista zadan z wymiana baterii do zaktualizowania
        """
        update_tasks = []
        for robot_data in self.swap_plan.values():
            tasks = robot_data["tasks"]
            if len(tasks) > 0 and robot_data["updated"] and not robot_data["new"]:
                robot_data["update"] = False
                update_tasks.append(tasks[0])

        self.updated_task = False
        return update_tasks

    def set_in_progress_task_status(self, robot_id):
        """
        Ustawienie potwierdzenia, ze zadanie wymiany zostalo rozpoczete.
        Parameters:
            robot_id (string): id robota, ktory rozpoczal wykonywanie zadania wymiany baterii
        """
        if robot_id in self.swap_plan.keys():
            if len(self.swap_plan[robot_id]["tasks"]) > 0:
                self.swap_plan[robot_id]["in_progress"] = True

    def set_done_task_status(self, robot_id):
        """
        Usuwanie zakonczonego zadania o podanym id z planu i ustawienie, ze pojawilo sie nowe zadanie do zlecenia.
        Parameters:
            robot_id (string): id robota, ktory rozpoczal wykonywanie zadania wymiany baterii
        """
        if robot_id in self.swap_plan.keys():
            if len(self.swap_plan[robot_id]["tasks"]) > 0:
                self.new_task = True
                self.swap_plan[robot_id]["new"] = True
                self.swap_plan[robot_id]["updated"] = False
                self.swap_plan[robot_id]["in_progress"] = False
                del self.swap_plan[robot_id]["tasks"][0]

    def _init_plan(self, robots):
        """
        Inicjalizuje plan wymian dla robotow w systemie
        Parameters:
            robots ({"id": Robot, "id": Robot, ...}): slownik robotow do ktorych nalezy przypisac zadania wymiany
        """
        now = datetime.now()
        n = len(self.swap_stations)
        for robot in robots.values():
            swap_station_poi = self.swap_stations[self.swap_station_id]
            time_to_allert = robot.battery.get_time_to_warn_allert()
            start_swap_time = (now + timedelta(minutes=time_to_allert) - timedelta(minutes=SWAP_TIME) -
                               timedelta(minutes=SWAP_TIME_BEFORE_ALERT)).strftime("%Y-%m-%d %H:%M:%S")
            self._add_task(start_swap_time, swap_station_poi, robot.id)
            self.swap_station_id += 1
            if self.swap_station_id >= n:
                self.swap_station_id = 0

    def _create_new_plan(self, robots):
        """
        Aktualizacja planu wymian. Jesli niektore zadania wymiany zostaly juz rozpoczete to sa uwzgledniane jako
        wykonywane teraz, a ich czas rozpoczecia nie jest zmieniany.
        Parameters:
            robots ({"id": Robot, "id": Robot, ...}): slownik robotow do ktorych nalezy przypisac zadania wymiany
        """
        now = datetime.now()
        n = len(self.swap_stations)
        robot_ids = [robot.id for robot in robots.values()]
        planned_robot_id = self.swap_plan.keys()

        # usuwanie z planu robotow, ktorych nie ma w systemie
        untracked_robots = [rid for rid in planned_robot_id if rid not in robot_ids]
        for robot_id in untracked_robots:
            del self.swap_plan[robot_id]

        for robot in robots.values():
            swap_station_poi = self.swap_stations[self.swap_station_id]
            if self._is_robot_add_task_required(robot):
                # brak zaplanowanej wymiany, moze wynikac z pojawienia sie nowego robota w systemie
                self.swap_plan[robot.id] = {"new": True, "updated": False, "in_progress": False, "tasks": []}
                time_to_warn = robot.battery.get_time_to_warn_allert()
                start_swap_time = (now + timedelta(minutes=time_to_warn) - timedelta(minutes=SWAP_TIME) -
                                   timedelta(minutes=SWAP_TIME_BEFORE_ALERT)).strftime("%Y-%m-%d %H:%M:%S")
                self._add_task(start_swap_time, swap_station_poi, robot.id)
                self.swap_station_id += 1
                if self.swap_station_id >= n:
                    self.swap_station_id = 0
                self.new_task = True
            elif len(self.swap_plan[robot.id]["tasks"]) > 0 and self._is_robot_update_required(robot):
                # weryfikacja czy konieczne jest przeplanowanie
                time_to_warn = robot.battery.get_time_to_warn_allert()
                start_swap_time = (now + timedelta(minutes=time_to_warn) - timedelta(minutes=SWAP_TIME) -
                                    timedelta(minutes=SWAP_TIME_BEFORE_ALERT)).strftime("%Y-%m-%d %H:%M:%S")
                self.swap_plan[robot.id]["tasks"][0].start_time = start_swap_time
                self.swap_plan[robot.id]["updated"] = True
                self.updated_task = True

    def _add_task(self, planned_swap_time, swap_station_poi, robot_id):
        """
        Dodaje zadanie do planu wymian
        Parameters:
            planned_swap_time (string): planowany czas rozpoczecia zadania w formacie "%Y-%m-%d %H:%M:%S"
            swap_station_poi (string): id poi z bazy typu charger
            robot_id (string): id robota z bazy
        """
        data = {"id": "swap_" + str(self.last_id),
                "behaviours": [{"id": "1", "parameters": {"to": swap_station_poi, "name": Behaviour.TYPES["goto"]}},
                               {"id": "2", "parameters": {"name": Behaviour.TYPES["dock"]}},
                               {"id": "3", "parameters": {"name": Behaviour.TYPES["bat_ex"]}},
                               {"id": "4", "parameters": {"name": Behaviour.TYPES["undock"]}}],
                "current_behaviour_index": -1,  # index tablicy nie zachowania
                "status": Task.STATUS_LIST["TO_DO"],
                "robot": robot_id,
                "start_time": planned_swap_time,
                "weight": 3,
                "priority": 3}
        self.swap_plan[robot_id]["tasks"].append(Task(data))
        self.last_id += 1

    def _get_swap_stations(self, pois_raw_data):
        """
        Dla listy POI zwraca tylko te, ktore sa typu charger.
        Parameters:
            pois_raw_data: ([{"id": string, "pose": (float,float)), "type": gc.base_node_type["..."]}, ...]) - lista
                POI w systemie

        Returns:
            (list): lista z id POI z bazy, ktore sa typu charger
        """
        stations_ids = []
        for poi in pois_raw_data:
            if poi["type"] == base_node_type["charger"]:
                stations_ids.append(poi["id"])
        return stations_ids

    def _is_replan_required(self, robots):
        """
        Sprawdza czy konieczne jest przeplanowanie wymian dla robotow. Nastepuje ono, gdy dla danego robota nie ma
        utworzonego kolejnego zadania wymiany lub gdy bateria przekroczy poziom ostrzegawczy zanim ma nastapic planowana
        wymiana.

        Parameters:
            robots ({"id": Robot, "id": Robot, ...}): slownik robotow do ktorych nalezy przypisac zadania wymiany

        Returns:
            (bool): informacja o koniecznosci przeplanowania wymian
        """
        now = datetime.now()
        for robot in robots.values():
            if self._is_robot_add_task_required(robot):
                return True
            if self._is_robot_update_required(robot):
                return True
        return False

    def _is_robot_update_required(self, robot):
        """
        Weryfikuje czy zaplanowana wymiana nastapi wczesniej niz wynika to z chwili czasowej, w ktorej wystapi
        ostrzezenie o niskim poziomie naladowania.

        Parameters:
            robots ({"id": Robot, "id": Robot, ...}): slownik robotow do ktorych nalezy przypisac zadania wymiany

        Returns:
            (bool): informacja o koniecznosci wykonania aktualizacji planu
        """
        now = datetime.now()
        robot_plan = self.swap_plan[robot.id]["tasks"]
        if len(robot_plan) > 0 and not self.swap_plan[robot.id]["in_progress"]:
            time_to_warn = robot.battery.get_time_to_warn_allert()
            planned_diff = (datetime.strptime(robot_plan[0].start_time,
                                                  ("%Y-%m-%d %H:%M:%S")) - now)/timedelta(minutes=1)

            min_diff_time = planned_diff - SWAP_TIME_BEFORE_ALERT - SWAP_TIME - REPLAN_THRESHOLD
            if planned_diff > 0 and time_to_warn > 0 and time_to_warn < min_diff_time:
                    return True

    def _is_robot_add_task_required(self, robot):
        """
        Weryfikuje czy istnieje plan wymian dla robota o podanym id oraz czy dla danego robota zaplanowana jest jakas
        wymiana baterii.

        Parameters:
            robots ({"id": Robot, "id": Robot, ...}): slownik robotow do ktorych nalezy przypisac zadania wymiany

        Returns:
            (bool): informacja o koniecznosci wykonania aktualizacji planu
        """
        if robot.id not in self.swap_plan:
            return True
        elif len(self.swap_plan[robot.id]["tasks"]) == 0:
            return True

