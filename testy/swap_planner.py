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


def get_robots_id(robots):
    """
    Parameters:
        robots (list({"id": string, "start_swap": float, "swap_time": float})) - lista robotów z chwilą rozpoczęcia
                        zadania w minutach od aktualnej chwili i czasem trwania wymiany w minutach
    Returns:
        (list(string)): lista z unikalnymi id robotów
    """
    unique_rid = []
    for data in robots:
        if data["id"] not in unique_rid:
            unique_rid.append(data["id"])
    unique_rid = sorted(unique_rid)
    return unique_rid


def create_regular_plan(robots):
    """
    Zwraca plan dla regularnego cyklu wymian.
    Parameters:
        robots (list({"id": string, "time_to_discharged": float})) - dane o robotach, id robota i czas do
            rozładowania baterii w minutach

    Returns:
        (list({"id": string, "start_swap": float, "swap_time": float})) - lista robotów z chwilą rozpoczęcia
            zadania w minutach od aktualnej chwili i czasem trwania wymiany w minutach
    """
    sorted_robots = sorted(copy.deepcopy(robots), key=itemgetter('time_to_discharged'))
    plan = []
    n = len(sorted_robots)
    cycle_horizon_time = STANDARD_CYCLE_TIME / n

    for j in range(n):
        plan.append({"id": sorted_robots[j]["id"], "start_swap": j * cycle_horizon_time, "swap_time": SWAP_TIME})

    return plan


def get_log_path(folder_name):
    log_path = os.path.expanduser("~") + "/SMART_logs/dispatcher/" + folder_name + "/"
    if not os.path.exists(log_path):
        os.makedirs(log_path)
    return log_path


def shifted_plan_if_required(plan):
    """
    Parameters
        plan (list({"id": string, "start_swap": float, "swap_time": float})) - lista robotów z chwilą rozpoczęcia
            zadania w minutach od aktualnej chwili i czasem trwania wymiany w minutach
    """
    sorted_plan = sorted(copy.deepcopy(plan), key=itemgetter('start_swap'))
    n = len(sorted_plan)
    for i in range(n - 1):
        diff = sorted_plan[-i-1]["start_swap"] - sorted_plan[-i-2]["start_swap"]
        if diff < SWAP_TIME:
            # wymiany pokrywają się, przesunąć poprzednią wymianę
            sorted_plan[-i - 2]["start_swap"] = sorted_plan[-i-1]["start_swap"] - SWAP_TIME
    return sorted_plan


class SwapPlanner:
    """
    Attributes:
        today (datetime): aktualna data od której generowane są wykresy ganta na podstawie przesunięć czasowych i czasu
                          trwania wymian
        plan (list({"id": string, "start_swap": float, "swap_time": float, "robot_id": string)) - lista robotów z chwilą
                rozpoczęcia zadania w minutach od aktualnej chwili i czasem trwania wymiany w minutach
        robots (list({"id": string, "time_to_discharged": float})) - dane o robotach, lista posortowanych robotów
                w kolejności od tego, który najszybciej się rozładuje.
    """
    def __init__(self, robots):
        """
        Parameters:
            robots (list({"id": string, "time_to_discharged": float})) - dane o robotach
        """
        self.today = datetime.now()  # docelowo datetime.now, ale przy korzystaniu z symulatora podmienić czas
        self.plan = []
        self.robots = sorted(robots, key=itemgetter('time_to_discharged'))

        start = self.today - timedelta(seconds=10)
        self.start_cycles = [dict(Task="swap tasks", Start=start, Finish=self.today, Resource=2)]

    def create_plan(self, time_horizon):
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

        Returns:
            (list({"id": string, "start_swap": float, "swap_time": float})) - lista robotów z chwilą rozpoczęcia
                zadania w minutach od aktualnej chwili i czasem trwania wymiany w minutach
        """
        self.plan = []

        regular_plan = {}
        # wyznaczenie czasu początkowego wynikającego z chwili, w której dla najbardziej rozładowanego robota poziom
        # naładowania baterii spada poniżej ostrzegawczego.
        first_swap_time = FULL_BATTERY_WORKING_TIME - STANDARD_CYCLE_TIME
        for plan_data in create_regular_plan(self.robots):
            plan_data["start_swap"] = first_swap_time + plan_data["start_swap"]
            #         print(plan_data)
            regular_plan[plan_data["id"]] = plan_data

        swap_t = 0
        while True:
            temp_plan = []
            for robot in self.robots:
                planned_swap_time = regular_plan[robot["id"]]["start_swap"]
                if planned_swap_time <= robot["time_to_discharged"]:
                    swap_t = planned_swap_time
                else:
                    new_swap_time = robot["time_to_discharged"] + (ALLOWED_CYCLE_TIME - STANDARD_CYCLE_TIME)
                    if planned_swap_time < new_swap_time:
                        swap_t = planned_swap_time
                    else:
                        swap_t = new_swap_time
                temp_plan.append({"id": robot["id"], "start_swap": swap_t, "swap_time": SWAP_TIME})
                robot["time_to_discharged"] = swap_t + FULL_BATTERY_WORKING_TIME  # po wymianie robot dostaje w pełni
                # naładowaną baterię

            for new_shifted_swap in shifted_plan_if_required(temp_plan):
                for robot in self.robots:
                    if robot["id"] == new_shifted_swap["id"]:
                        robot["start_swap"] = new_shifted_swap["start_swap"]
                self.plan.append(new_shifted_swap)
            self.robots = sorted(self.robots, key=itemgetter('time_to_discharged'))

            if swap_t > time_horizon:
                break
            else:
                # konfiguracja inicjalizacji nowego kroku
                start_time_regular_cycle = self.robots[0]["start_swap"] + STANDARD_CYCLE_TIME  # wyznaczenie początku
                # nowego kroku cyklu
                end = self.today + timedelta(minutes=start_time_regular_cycle)
                start = end - timedelta(seconds=10)
                self.start_cycles.append(dict(Task="swap tasks", Start=start, Finish=end, Resource=2))

                regular_plan = {}
                received_cycle_plan = sorted(create_regular_plan(self.robots), key=itemgetter('start_swap'))
                for plan_data in received_cycle_plan:
                    plan_data["start_swap"] = start_time_regular_cycle + plan_data["start_swap"]
                    # print(plan_data)
                    regular_plan[plan_data["id"]] = plan_data

    def create_plan_v4(self, time_horizon):
        """
        Zwraca plan dla regularnego cyklu wymian z uwzględnieniem aktualnego poziomu naładowania baterii. Generuje plan
        z cyklami przygotowawczymi do wejścia w regularne cykle podane jako parametr. Początek wejścia w regularny
        cykl wymian. Początek wejścia w regularny tryb wymian w chwili, w której nastąpiłaby wymiana w pełni
        naładowanej baterii. wygenerowany plan. Ustawienie planowania względem czasów z planu.
        Przesuwanie wymian w celu uniknięcia konfliktów wymian.

        Parameters:
            time_horizon (int) - horyzont czasowy planowania w minutach

        Returns:
            (list({"id": string, "start_swap": float, "swap_time": float})) - lista robotów z chwilą rozpoczęcia
                zadania w minutach od aktualnej chwili i czasem trwania wymiany w minutach
        """
        self.plan = []

        regular_plan = {}
        # wyznaczenie czasu początkowego wynikającego z chwili, w której dla najbardziej rozładowanego robota poziom
        # naładowania baterii spada poniżej ostrzegawczego.
        first_swap_time = FULL_BATTERY_WORKING_TIME - STANDARD_CYCLE_TIME
        for plan_data in create_regular_plan(self.robots):
            plan_data["start_swap"] = first_swap_time + plan_data["start_swap"]
            #         print(plan_data)
            regular_plan[plan_data["id"]] = plan_data

        swap_t = 0
        while True:
            temp_plan = []
            for robot in self.robots:
                planned_swap_time = regular_plan[robot["id"]]["start_swap"]
                if planned_swap_time <= robot["time_to_discharged"]:
                    swap_t = planned_swap_time
                else:
                    new_swap_time = robot["time_to_discharged"] + (ALLOWED_CYCLE_TIME - STANDARD_CYCLE_TIME)
                    if planned_swap_time < new_swap_time:
                        swap_t = planned_swap_time
                    else:
                        swap_t = new_swap_time
                temp_plan.append({"id": robot["id"], "start_swap": swap_t, "swap_time": SWAP_TIME})
                robot["time_to_discharged"] = swap_t + FULL_BATTERY_WORKING_TIME  # po wymianie robot dostaje w pełni
                # naładowaną baterię

            for new_shifted_swap in shifted_plan_if_required(temp_plan):
                for robot in self.robots:
                    if robot["id"] == new_shifted_swap["id"]:
                        robot["start_swap"] = new_shifted_swap["start_swap"]
                self.plan.append(new_shifted_swap)
            self.robots = sorted(self.robots, key=itemgetter('time_to_discharged'))

            if swap_t > time_horizon:
                break
            else:
                # konfiguracja inicjalizacji nowego kroku
                start_time_regular_cycle = self.robots[0]["start_swap"] + STANDARD_CYCLE_TIME  # wyznaczenie początku
                # nowego kroku cyklu
                end = self.today + timedelta(minutes=start_time_regular_cycle)
                start = end - timedelta(seconds=10)
                self.start_cycles.append(dict(Task="swap tasks", Start=start, Finish=end, Resource=2))

                regular_plan = {}
                received_cycle_plan = sorted(create_regular_plan(self.robots), key=itemgetter('start_swap'))
                for plan_data in received_cycle_plan:
                    plan_data["start_swap"] = start_time_regular_cycle + plan_data["start_swap"]
                    # print(plan_data)
                    regular_plan[plan_data["id"]] = plan_data

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
        sorted_plan = sorted(copy.deepcopy(self.plan), key=itemgetter('start_swap'))
        unique_rid = get_robots_id(self.robots)

        first_swaps = {}
        for rid in unique_rid:
            for swap_task in sorted_plan:
                if swap_task["id"] == rid:
                    first_swaps[swap_task["id"]] = swap_task["start_swap"]
                    break

        # 1. weryfikacja czy wymiany nie pokrywają się ze sobą
        for i in range(len(sorted_plan) - 1):
            if sorted_plan[i + 1]["start_swap"] - sorted_plan[i]["start_swap"] < SWAP_TIME:
                print("1. Wymiany pokrywają się")
                print(sorted_plan[i + 1])
                print(sorted_plan[i])
                return False

        # 2. Weyfikacja czy dla danego robota dla kolejnych zaplanowanych wymian wystarczy w pełni naładowanej
        # baterii
        for rid in unique_rid:
            robots_swaps = [swap_task for swap_task in sorted_plan if swap_task["id"] == rid]
            for i in range(len(robots_swaps) - 1):
                swap_diff = robots_swaps[i + 1]["start_swap"] - robots_swaps[i]["start_swap"]
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
        sorted_plan = sorted(self.plan, key=itemgetter('start_swap'))
        colors = {0: 'rgb({},{},{})'.format(255, 0, 0),
                  1: 'rgb({},{},{})'.format(0, 0, 255),
                  2: 'rgb({},{},{})'.format(0, 0, 0)}

        plot_data = []
        i = 0

        for data in sorted_plan:
            start_time = self.today + timedelta(minutes=data["start_swap"])
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
            start_time = self.today + timedelta(minutes=data["start_swap"])
            end_time = start_time + timedelta(minutes=data["swap_time"])
            robot_annotation_pose = (end_time - start_time) / 2 + start_time
            fig['layout']['annotations'] += tuple([dict(x=robot_annotation_pose, y=0, text=str(data["id"]),
                                                        textangle=0, showarrow=False, font=text_font)])

        fig['layout']['yaxis']['title'] = "Wymiany baterii w stacji"
        py.offline.plot(fig, filename=get_log_path(folder_name) + 'swap_gant.html', auto_open=False)

    def create_robots_swap_gant(self, folder_name):
        """
        Tworzy wykres ganta z wymianami baterii oddzielnie dla każdego z robotów.
        Parameters:
            folder_name (string): nazwa folderu do zapisu loga
        """
        sorted_plan = sorted(self.plan, key=itemgetter('id'))
        colors = {0: 'rgb({},{},{})'.format(255, 0, 0),
                  1: 'rgb({},{},{})'.format(0, 0, 0)}

        unique_rid = get_robots_id(sorted_plan)

        plot_data = []

        for data in sorted_plan:
            start_time = self.today + timedelta(minutes=data["start_swap"])
            end_time = start_time + timedelta(minutes=data["swap_time"])
            plot_data.append(dict(Task=str(data["id"]), Start=start_time, Finish=end_time,
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
        sorted_plan = sorted(self.plan, key=itemgetter('start_swap'))
        swap_diff = []
        for i in range(len(sorted_plan) - 1):
            diff = abs(sorted_plan[i + 1]['start_swap'] - sorted_plan[i]['start_swap'])
            swap_diff.append(diff)

        fig, ax = plt.subplots(figsize=(20, 20))
        ax.set_title('Stan naladowania baterii w robotach')
        ax.set_xlabel('kolejne wymiany (i+1) - i')
        ax.set_ylabel('diff time [min]')

        ax.plot(swap_diff, label="swap_diff", color="blue")
        ax.plot([SWAP_TIME]*len(swap_diff), label="swap_time", color="red")
        ax.legend()
        plt.savefig(get_log_path(folder_name) + "swap_times.png")
