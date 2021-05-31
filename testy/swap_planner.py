import os
from operator import itemgetter
from datetime import datetime, timedelta
import plotly.figure_factory as ff
import plotly as py
import matplotlib.pyplot as plt
import copy

FULL_BATTERY_WORKING_TIME = 4*60  # [min]
SWAP_TIME = 3  # [min]
STANDARD_CYCLE_TIME = FULL_BATTERY_WORKING_TIME - 10  # [min] standardowy czas na jaki planowane są wymiany
ALLOWED_CYCLE_TIME = FULL_BATTERY_WORKING_TIME - 5  # [min] pozwala na dłuższą pracę na baterii i wykonanie
# późniejszej wymiany, aby ustabilizować wymiany w równych odstępach czasowych


def create_regular_plan(robots):
    """
    Zwraca plan dla regularnego cyklu wymian.
    Parameters:
        robots (list({"id": string, "time_to_discharged": float})) - dane o robotach, id robota i czas do
            rozładowania baterii w minutach

    Returns:
        (list({"swap_time": float, "time_to_swap": float, "robot_id": string, "active_swap": boolean)) - lista robotów
         z ułożonym planem kolejnych wymian, "time_to_swap" liczony jest względem updated_time.
    """
    sorted_robots = sorted(copy.deepcopy(robots), key=itemgetter('time_to_discharged'))
    plan = []
    n = len(sorted_robots)
    cycle_horizon_time = STANDARD_CYCLE_TIME / n

    for j in range(n):
        plan.append({"robot_id": sorted_robots[j]["id"], "time_to_swap": j * cycle_horizon_time,
                     "swap_time": SWAP_TIME, "active_swap": False})

    return plan


def get_log_path(folder_name):
    log_path = os.path.expanduser("~") + "/SMART_logs/dispatcher/" + folder_name + "/"
    if not os.path.exists(log_path):
        os.makedirs(log_path)
    return log_path


def shifted_plan_if_required(plan):
    """
    Parameters:
        plan (list({"swap_time": float, "time_to_swap": float, "robot_id": string, "active_swap": boolean})) - lista
            robotów z ułożonym planem kolejnych wymian, "time_to_swap" liczony jest względem updated_time.

    Returns:
        (list({"start_swap": string(%Y-%m-%d %H:%M:%S), "swap_time": float, "time_to_swap": float,
            "robot_id": string})): zwraca posortowany plan po czasie pozostałym do wymiany od najwcześniejszej do
            najpóźniejszej
    """
    sorted_plan = sorted(copy.deepcopy(plan), key=itemgetter('time_to_swap'))
    n = len(sorted_plan)
    for i in range(n - 1):
        diff = sorted_plan[-i-1]["time_to_swap"] - sorted_plan[-i-2]["time_to_swap"]
        if diff < SWAP_TIME and not sorted_plan[-i - 2]["active_swap"]:
            # wymiany pokrywają się, przesunąć poprzednią wymianę
            sorted_plan[-i - 2]["time_to_swap"] = sorted_plan[-i-1]["time_to_swap"] - SWAP_TIME
    return sorted_plan


class SwapPlanner:
    """
    Attributes:
        start_swaps_time (datetime): data i godzina w której generowany był długookresowy plan. Wykorzystywany również do
            wygenerowania wykresów ganta na podstawie przesunięć czasowych i czasu trwania wymian.
        plan (list({"swap_time": float, "time_to_swap": float, "robot_id": string)) - lista robotów z ułożonym planem
            kolejnych wymian, "time_to_swap" liczony jest względem updated_time.
        active_swaps (list) - lista aktywnych wymian wykonywanych przez roboty o podanym id
            ({"id": string, "start_swap": string(%Y-%m-%d %H:%M:%S), "swap_time": float})
        robots (list({"id": string, "time_to_discharged": float, "swap": dict/None})) - dane o robotach, lista
            posortowanych robotów w kolejności od tego, który najszybciej się rozładuje.
        start_cycles (list(dict("Task": string, "Start": datetime, "Finish": datetime, "Resource": int))): lista z
            kolejnymi czasami rozpoczęcia cyklów. Do wyświetlania na wykresie.
    """
    def __init__(self):
        self.start_swaps_time = datetime.now() # docelowo datetime.now, ale przy korzystaniu z symulatora podmienić czas
        self.plan = []
        self.robots = []
        self.active_swaps = []
        start = self.start_swaps_time - timedelta(seconds=10)
        self.start_cycles = [dict(Task="swap tasks", Start=start, Finish=self.start_swaps_time, Resource=2)]

    def create_plan(self, time_horizon, robots):
        """
        Parameters:
            time_horizon (float): horyzont czasowy w minutach w jakim ma być ułożony plan wymian.
            robots (list({"id": string, "time_to_discharged": float, "swap": dict/None})) - dane o robotach, jeśli
               wykonywane jest zadanie wymiany to przekazywana jest informacja {"start_swap": string(%Y-%m-%d %H:%M:%S),
               "swap_time": float}, a jeśli robot nie wykonuje zadania wymiany to None.
        """
        # self.updated_time = datetime.now()  # docelowo datetime.now, ale przy korzystaniu z symulatora podmienić czas
        # przed wywołaniem funkcji
        self.robots = []
        for robot in sorted(robots, key=itemgetter('time_to_discharged')):
            self.robots.append(robot)
            if robot["swap"] is not None:
                swap_time = datetime.strptime(robot["swap"]["start_swap"], "%Y-%m-%d %H:%M:%S")
                self.active_swaps.append(dict(id=robot["id"], start_swap=swap_time,
                                              swap_time=robot["swap"]["swap_time"]))

        self.active_swaps = sorted(self.active_swaps, key=itemgetter('start_swap'))
        self.create_plan_v4(time_horizon)

    def create_plan_v3(self, time_horizon):
        """
        Zwraca plan dla regularnego cyklu wymian z uwzględnieniem aktualnego poziomu naładowania baterii. Generuje plan
        z cyklami przygotowawczymi do wejścia w regularne cykle podane jako parametr. Początek wejścia w regularny
        cykl wymian. Początek wejścia w regularny tryb wymian w chwili, w której nastąpiłaby wymiana w pełni
        naładowanej baterii. wygenerowany plan. Ustawienie planowania względem czasów z planu.
        Przesuwanie wymian w celu uniknięcia konfliktów wymian.

        Parameters:
            time_horizon (int) - horyzont czasowy planowania w minutach
        """
        self.plan = []

        regular_plan = {}
        # wyznaczenie czasu początkowego wynikającego z chwili, w której dla najbardziej rozładowanego robota poziom
        # naładowania baterii spada poniżej ostrzegawczego.
        first_swap_time = FULL_BATTERY_WORKING_TIME - STANDARD_CYCLE_TIME
        for plan_data in create_regular_plan(self.robots):
            plan_data["time_to_swap"] = first_swap_time + plan_data["time_to_swap"]
            #         print(plan_data)
            regular_plan[plan_data["robot_id"]] = plan_data

        swap_t = 0
        while True:
            temp_plan = []
            for robot in self.robots:
                planned_swap_time = regular_plan[robot["id"]]["time_to_swap"]
                if planned_swap_time <= robot["time_to_discharged"]:
                    swap_t = planned_swap_time
                else:
                    new_swap_time = robot["time_to_discharged"] + (ALLOWED_CYCLE_TIME - STANDARD_CYCLE_TIME)
                    if planned_swap_time < new_swap_time:
                        swap_t = planned_swap_time
                    else:
                        swap_t = new_swap_time
                temp_plan.append({"robot_id": robot["id"], "time_to_swap": swap_t, "swap_time": SWAP_TIME})
                robot["time_to_discharged"] = swap_t + FULL_BATTERY_WORKING_TIME  # po wymianie robot dostaje w pełni
                # naładowaną baterię

            for new_shifted_swap in shifted_plan_if_required(temp_plan):
                for robot in self.robots:
                    if robot["id"] == new_shifted_swap["robot_id"]:
                        robot["time_to_swap"] = new_shifted_swap["time_to_swap"]
                self.plan.append(new_shifted_swap)
            self.robots = sorted(self.robots, key=itemgetter('time_to_discharged'))

            if swap_t > time_horizon:
                break
            else:
                # konfiguracja inicjalizacji nowego kroku
                start_time_regular_cycle = self.robots[0]["time_to_swap"] + STANDARD_CYCLE_TIME  # wyznaczenie początku
                # nowego kroku cyklu
                end = self.start_swaps_time + timedelta(minutes=start_time_regular_cycle)
                start = end - timedelta(seconds=10)
                self.start_cycles.append(dict(Task="swap tasks", Start=start, Finish=end, Resource=2))

                regular_plan = {}
                received_cycle_plan = sorted(create_regular_plan(self.robots), key=itemgetter('time_to_swap'))
                for plan_data in received_cycle_plan:
                    plan_data["time_to_swap"] = start_time_regular_cycle + plan_data["time_to_swap"]
                    # print(plan_data)
                    regular_plan[plan_data["robot_id"]] = plan_data

    def create_plan_v4(self, time_horizon):
        """
        Zwraca plan dla regularnego cyklu wymian z uwzględnieniem aktualnego poziomu naładowania baterii. Generuje plan
        z cyklami przygotowawczymi do wejścia w regularne cykle podane jako parametr. Początek wejścia w regularny
        cykl wymian. Początek wejścia w regularny tryb wymian w chwili, w której nastąpiłaby wymiana w pełni
        naładowanej baterii. wygenerowany plan. Ustawienie planowania względem czasów z planu.
        Przesuwanie wymian w celu uniknięcia konfliktów wymian. Generowanie planu z uwzględnieniem aktualnie
        wykonywanych wymian.

        Parameters:
            time_horizon (int) - horyzont czasowy planowania w minutach
        """
        self.plan = []

        regular_plan = self.init_swap_tasks()
        swap_t = 0
        while True:
            temp_plan = []
            for robot in self.robots:
                planned_swap_time = regular_plan[robot["id"]]["time_to_swap"]
                if planned_swap_time <= robot["time_to_discharged"]:
                    swap_t = planned_swap_time
                else:
                    new_swap_time = robot["time_to_discharged"] + (ALLOWED_CYCLE_TIME - STANDARD_CYCLE_TIME)
                    if planned_swap_time < new_swap_time:
                        swap_t = planned_swap_time
                    else:
                        swap_t = new_swap_time

                temp_plan.append({"robot_id": robot["id"], "time_to_swap": swap_t, "swap_time": SWAP_TIME,
                                  "active_swap": regular_plan[robot["id"]]["active_swap"]})
                robot["time_to_discharged"] = swap_t + FULL_BATTERY_WORKING_TIME  # po wymianie robot dostaje w pełni
                # naładowaną baterię
            for new_shifted_swap in shifted_plan_if_required(temp_plan):
                for robot in self.robots:
                    if robot["id"] == new_shifted_swap["robot_id"]:
                        robot["time_to_swap"] = new_shifted_swap["time_to_swap"]
                self.plan.append(new_shifted_swap)
            self.robots = sorted(self.robots, key=itemgetter('time_to_discharged'))

            if swap_t > time_horizon:
                break
            else:
                # konfiguracja inicjalizacji nowego kroku
                start_time_regular_cycle = self.robots[0]["time_to_swap"] + STANDARD_CYCLE_TIME  # wyznaczenie początku
                # nowego kroku cyklu
                end = self.start_swaps_time + timedelta(minutes=start_time_regular_cycle)
                start = end - timedelta(seconds=10)
                self.start_cycles.append(dict(Task="swap tasks", Start=start, Finish=end, Resource=2))

                regular_plan = {}
                received_cycle_plan = sorted(create_regular_plan(self.robots), key=itemgetter('time_to_swap'))
                for plan_data in received_cycle_plan:
                    plan_data["time_to_swap"] = start_time_regular_cycle + plan_data["time_to_swap"]
                    regular_plan[plan_data["robot_id"]] = plan_data

    def init_swap_tasks(self):
        first_cycle_plan = {}
        n_swaps = len(self.active_swaps)
        allowed_working_time = FULL_BATTERY_WORKING_TIME - STANDARD_CYCLE_TIME
        if n_swaps == 0:
            # w trakcie przeplanowania zadania wymiany nie są wykonywane
            for plan_data in create_regular_plan(self.robots):
                plan_data["time_to_swap"] = allowed_working_time + plan_data["time_to_swap"]
                first_cycle_plan[plan_data["robot_id"]] = plan_data
            start = self.start_swaps_time - timedelta(seconds=10)
            self.start_cycles = [dict(Task="swap tasks", Start=start, Finish=self.start_swaps_time, Resource=2)]
        else:
            # co najmniej 1 z robotów jest w trakcie wykonywania zadania wymiany baterii
            # Wyznaczenie czasu początku cyklu wymian. Czas początku najwcześniej rozpoczętej wymiany jest początkiem
            # cyklu wymian.
            self.start_swaps_time = self.active_swaps[0]["start_swap"]
            start = self.start_swaps_time - timedelta(seconds=10)
            self.start_cycles.append(dict(Task="swap tasks", Start=start, Finish=self.start_swaps_time, Resource=2))
            regular_plan = create_regular_plan(self.robots)

            n = len(self.robots)
            swap_slots = []
            cycle_horizon_time = STANDARD_CYCLE_TIME / n
            for i in range(n):
                end_time_slot = i*cycle_horizon_time
                swap_slots.append({"robot_id": None, "end_time_slot": end_time_slot,
                                   "default_start_time": regular_plan[i]["time_to_swap"], "swap_start_time": None,
                                   "active_swap": False})

            robots_to_cycle_assign = self.get_robots_id()
            unassigned_active_swaps = copy.deepcopy(self.active_swaps)
            for active_swap in self.active_swaps:
                robot_id = active_swap["id"]
                # przeliczenie do czasu przesunięcia w minutach od startu
                start_swap = (active_swap["start_swap"].timestamp() - self.start_swaps_time.timestamp())/60
                for swap_slot in swap_slots:
                    start_time_slot = swap_slot["end_time_slot"] - cycle_horizon_time
                    if swap_slot["robot_id"] is None and (start_time_slot <= start_swap < swap_slot["end_time_slot"]):
                        swap_slot["robot_id"] = robot_id
                        swap_slot["active_swap"] = True
                        swap_slot["swap_start_time"] = start_swap
                        robots_to_cycle_assign.remove(robot_id)
                        for i in range(len(unassigned_active_swaps)):
                            swap_to_remove = unassigned_active_swaps[i]
                            if swap_to_remove["id"] == active_swap["id"]:
                                unassigned_active_swaps.pop(i)
                                break
            # jeśli niektóre roboty nie zostały przydzielone do slotów to przydzielane im są kolejne wolne od
            # początkowego slotu
            if len(unassigned_active_swaps) > 0:
                for active_swap in self.active_swaps:
                    robot_id = active_swap["id"]
                    start_swap = (active_swap["start_swap"].timestamp() - self.start_swaps_time.timestamp())/60
                    for swap_slot in swap_slots:
                        if swap_slot["robot_id"] is None and robot_id in robots_to_cycle_assign:
                            swap_slot["robot_id"] = robot_id
                            swap_slot["active_swap"] = True
                            swap_slot["swap_start_time"] = start_swap
                            robots_to_cycle_assign.remove(robot_id)

            # do pozostałych slotów przydzielane sa kolejno roboty od najbardziej do najmniej rozładowanego
            for robot in self.robots:
                if robot["swap"] is None:
                    # przypisać robota do pierwszego wolnego slotu
                    for swap_slot in swap_slots:
                        if swap_slot["robot_id"] is None and robot["id"] in robots_to_cycle_assign:

                            swap_slot["robot_id"] = robot["id"]
                            diff = swap_slot["default_start_time"] - (robot["time_to_discharged"] - allowed_working_time)
                            if diff > 0:
                                # do czasu domyślnie zaplanowanej wymiany potrzeba bardziej naładowanej baterii niż
                                # aktualna w robocie
                                swap_slot["swap_start_time"] = robot["time_to_discharged"] - allowed_working_time
                            else:
                                swap_slot["swap_start_time"] = swap_slot["default_start_time"]
                            robots_to_cycle_assign.remove(robot["id"])

            for robot in self.robots:
                for i in range(len(swap_slots)):
                    if swap_slots[i]["robot_id"] == robot["id"]:
                        swap_time = SWAP_TIME if robot["swap"] is None else robot["swap"]["swap_time"]
                        plan_data = {"swap_time": swap_time,
                                     "time_to_swap": swap_slots[i]["swap_start_time"],
                                     "robot_id": robot["id"],
                                     "active_swap": swap_slots[i]["active_swap"]}
                        first_cycle_plan[robot["id"]] = plan_data
                        break

            # dodanie do poczatku wyswietlanych cykli chwili najwcześniejszego rozpoczęcia zadania wymiany baterii
            start = self.start_swaps_time - timedelta(seconds=10)
            self.start_cycles = [dict(Task="swap tasks", Start=start, Finish=self.start_swaps_time, Resource=2)]
        return first_cycle_plan

    def get_robots_id(self):
        """
        Returns:
            (list(string)): lista z unikalnymi id robotów
        """
        unique_rid = [data["id"] for data in self.robots]
        unique_rid = sorted(unique_rid)
        return unique_rid

    def is_possible_create_init_cycle(self):
        time_to_swap = 0
        for robot in self.robots:
            if robot["time_to_discharged"] < time_to_swap:
                print("Roboty nie zdążą wymienić baterii w trakcie rozruchu wymian przed wejściem w regularny cykl.")
                return False
            time_to_swap += SWAP_TIME

        swap_times = len(self.robots) * SWAP_TIME
        if swap_times > STANDARD_CYCLE_TIME:
            print("Wymiany trwają dłużej niż standardowy czas cyklu. Czas wymian: {},"
                  " czas cyklu: {}".format(swap_times, STANDARD_CYCLE_TIME))
            return False
        return True

    def is_valid_plan(self):
        """
        Weryfikuje czy podany plan jest prawidłowy:
            1. czasy wymian nie pokrywają się ze sobą
            2. Dla danego robota od jednej do druiej wymiany wystarczy w pełni naładowanej baterii
            3. czas do pierwszej wymiany jest mniejszy niż czas do rozładowania robota
        Returns:
            (boolean): True - plan prawidłowy, False - plan nieprawidłowy
        """
        sorted_plan = sorted(copy.deepcopy(self.plan), key=itemgetter('time_to_swap'))
        unique_rid = self.get_robots_id()

        first_swaps = {}
        for rid in unique_rid:
            for swap_task in sorted_plan:
                if swap_task["robot_id"] == rid:
                    first_swaps[swap_task["robot_id"]] = swap_task["time_to_swap"]
                    break

        # 1. weryfikacja czy wymiany nie pokrywają się ze sobą
        for i in range(len(sorted_plan) - 1):
            if sorted_plan[i + 1]["time_to_swap"] - sorted_plan[i]["time_to_swap"] < SWAP_TIME:
                print("1. Wymiany pokrywają się")
                print(sorted_plan[i + 1])
                print(sorted_plan[i])
                return False

        # 2. Weyfikacja czy dla danego robota dla kolejnych zaplanowanych wymian wystarczy w pełni naładowanej
        # baterii
        for rid in unique_rid:
            robots_swaps = [swap_task for swap_task in sorted_plan if swap_task["robot_id"] == rid]
            for i in range(len(robots_swaps) - 1):
                swap_diff = robots_swaps[i + 1]["time_to_swap"] - robots_swaps[i]["time_to_swap"]
                if swap_diff > FULL_BATTERY_WORKING_TIME:
                    print("2. Kolejna wymiana baterii nie odbywa się przed końcem czasu pracy na pełnej baterii.")
                    return False

        # 3. weryfikacja pierwszych wymian
        for robot in self.robots:
            if robot["time_to_discharged"] < first_swaps[robot["id"]]:
                print("3. Przed pierwszą wymianą bateria jest rozładowana.")
                return False
        return True

    def create_swap_gant(self, folder_name):
        """
        Tworzy wykres ganta z wszystkimi wymianami baterii dla stacji.
        Parameters:
            folder_name (string): nazwa folderu do zapisu loga
        """
        sorted_plan = sorted(self.plan, key=itemgetter('time_to_swap'))
        colors = {0: 'rgb({},{},{})'.format(255, 0, 0),
                  1: 'rgb({},{},{})'.format(0, 0, 255),
                  2: 'rgb({},{},{})'.format(0, 0, 0)}

        plot_data = []
        i = 0

        for data in sorted_plan:
            start_time = self.start_swaps_time + timedelta(minutes=data["time_to_swap"])
            end_time = start_time + timedelta(minutes=data["swap_time"])
            plot_data.append(dict(Task="swap tasks", Start=start_time, Finish=end_time, Resource=int(i % 2)))
            i += 1
        for cycle in self.start_cycles:
            plot_data.append(cycle)
        fig = ff.create_gantt(plot_data, index_col='Resource', title='Zadania zaplanowanej wymiany baterii',
                              show_colorbar=True, group_tasks=True, showgrid_x=True, showgrid_y=True,
                              colors=colors)

        text_font = dict(size=12, color='black')
        for data in sorted_plan:
            start_time = self.start_swaps_time + timedelta(minutes=data["time_to_swap"])
            end_time = start_time + timedelta(minutes=data["swap_time"])
            robot_annotation_pose = (end_time - start_time) / 2 + start_time
            fig['layout']['annotations'] += tuple([dict(x=robot_annotation_pose, y=0, text=str(data["robot_id"]),
                                                        textangle=0, showarrow=False, font=text_font)])

        fig['layout']['yaxis']['title'] = "Wymiany baterii w stacji"
        py.offline.plot(fig, filename=get_log_path(folder_name) + 'swap_gant.html', auto_open=False)

    def create_robots_swap_gant(self, folder_name):
        """
        Tworzy wykres ganta z wymianami baterii oddzielnie dla każdego z robotów.
        Parameters:
            folder_name (string): nazwa folderu do zapisu loga
        """
        sorted_plan = sorted(self.plan, key=itemgetter('robot_id'))
        colors = {0: 'rgb({},{},{})'.format(255, 0, 0),
                  1: 'rgb({},{},{})'.format(0, 0, 0)}

        unique_rid = self.get_robots_id()

        plot_data = []

        for data in sorted_plan:
            start_time = self.start_swaps_time + timedelta(minutes=data["time_to_swap"])
            end_time = start_time + timedelta(minutes=data["swap_time"])
            plot_data.append(dict(Task=str(data["robot_id"]), Start=start_time, Finish=end_time,
                                  Resource=0))
        for cycle in self.start_cycles:
            for rid in unique_rid:
                plot_data.append(dict(Task=rid, Start=cycle["Start"], Finish=cycle["Finish"], Resource=1))
        fig = ff.create_gantt(plot_data, index_col='Resource',
                              title='Zadania zaplanowanej wymiany', show_colorbar=True,
                              group_tasks=True, showgrid_x=True, showgrid_y=True, colors=colors)
        fig['layout']['yaxis']['title'] = "Wymiana baterii w stacji dla robotów"
        py.offline.plot(fig, filename=get_log_path(folder_name) + 'swap_robots_gant.html', auto_open=False)

    def create_next_swaps_diff(self, folder_name):
        """
        Generuje wykres z naniesionymi różnicami czasowymi pomiędzy kolejnymi wymianami i zakładanym czasem wymiany
        baterii.
        Parameters:
            folder_name (string): nazwa folderu do zapisu loga
        Returns:
            (png file): wykres wynikowy
        """
        sorted_plan = sorted(self.plan, key=itemgetter('time_to_swap'))
        swap_diff = []
        for i in range(len(sorted_plan) - 1):
            diff = abs(sorted_plan[i + 1]['time_to_swap'] - sorted_plan[i]['time_to_swap'])
            swap_diff.append(diff)

        fig, ax = plt.subplots(figsize=(20, 20))
        ax.set_title('Stan naladowania baterii w robotach')
        ax.set_xlabel('kolejne wymiany (i+1) - i')
        ax.set_ylabel('diff time [min]')

        ax.plot(swap_diff, label="swap_diff", color="blue")
        ax.plot([SWAP_TIME]*len(swap_diff), label="swap_time", color="red")
        ax.legend()
        plt.savefig(get_log_path(folder_name) + "swap_times.png")
