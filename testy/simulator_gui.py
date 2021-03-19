from dispatcher import Robot, Task, Behaviour
import ipywidgets as widgets
import pandas as pd
import copy
import random
import matplotlib.pyplot as plt
import networkx as nx
import json

INFO_OUTPUT = widgets.Output(layout=widgets.Layout(height='50px', width = "100%"))
HEIGHT_TABLES = "300px"

def update_info(info_data):
    with INFO_OUTPUT:
        INFO_OUTPUT.clear_output()
        display(info_data)

class RobotsCreator:
    """
    Klasa odpowiedzialna za obsluge i wyswietlanie panelu do konfiguracji robotow
    Atributes:
        robot_id (int): domyslnie zwiekszajace sie o 1 id nowego robota
        robots (list(Robot)): lista nowo utworzonych robotów

        Widgety
            tab_widget (Tab): zakladki od dodawania, usuwania robota i wyswietlania tabeli z wprowadzonymi robotami

        Widgety dla panelu dodaj robota
            add_widget (Button): przycisk do dodania nowo skonfigurowanego robota do listy
            robot_name_widget (Text): nazwa robota, domyślnie jest to id z self.robot_id
            start_poi_widget (Dropdown): lista rozwijana z id POI z grafu do wyboru
            battery_lvl_widget (FloatText): poziom naladowania baterii w %

        Widgety dla panelu usun robota
            remove_widget (Button): przycisk do usuwania robota z listy
            robot_to_remove_widget (Dropdown): lista rozwijana do wyboru 1 robota do usuniecia

        Widgety dla panelu lista robotow
            robots_table_widget (Output): tabela z lista wprowadzonych robotow (robot name, poi startowe, poziom
                naladownaia baterii w %)
    """
    def __init__(self, pois_raw):
        """
        Inicjalizacja i utworzenie interfejsu do obslugi konfiguracji robotow w systemie do testow.
        Parameters:
            pois_raw: ([{"id": string, "pose": (float,float)), "type": gc.base_node_type["..."]}, ...]) - lista
                POI w systemie
        """
        self.robot_id = 0
        self.robots = []
        self.create_tabs(pois_raw)

    def create_add_panel(self, pois_raw):
        """
        Odpowiada za utworzenie panelu do konfiguracji i wprowadzania nowych robotow
        Parameters:
            pois_raw: ([{"id": string, "pose": (float,float)), "type": gc.base_node_type["..."]}, ...]) - lista
                POI w systemie
        """
        self.add_widget = widgets.Button(
                description='Add robot',
                disabled=False,
                button_style='',  # 'success', 'info', 'warning', 'danger' or ''
                icon='check'  # (FontAwesome names without the `fa-` prefix)
        )
        self.robot_name_widget = widgets.Text(value=str(self.robot_id))

        pois = [poi["id"] for poi in pois_raw]
        self.start_poi_widget = widgets.Dropdown(options=pois, value=pois[0], description='POI:', disabled=False)
        self.battery_lvl_widget = widgets.FloatText(value=100, description='Battery lvl:', disabled=False)

        self.add_widget.on_click(self.add_robot_widget_button)
        self.battery_lvl_widget.observe(self.check_battery_range_widget_button)

    def create_remove_panel(self):
        """
        Odpowiada za usuwanie robota z listy wprowadzonych robotow.
        """
        self.remove_widget = widgets.Button(description='Remove robot', disabled=False, button_style='', icon='check')

        robots = [robot.id for robot in self.robots]
        self.robot_to_remove_widget = widgets.Dropdown(options=robots, description='Robot:', disabled=False)
        self.remove_widget.on_click(self.remove_robot_widget_button)

    def create_tabs(self, pois_raw):
        """
        Utworzenie widoku interfejsu konfiguratora robotów w systemie wraz z zakladkami.
        Parameters:
            pois_raw: ([{"id": string, "pose": (float,float)), "type": gc.base_node_type["..."]}, ...]) - lista
                POI w systemie
        """
        self.create_add_panel(pois_raw)
        self.create_remove_panel()
        self.robots_table_widget = widgets.Output(layout=widgets.Layout(height=HEIGHT_TABLES, overflow_y='auto'))
        children = [
            widgets.VBox([widgets.HBox([self.add_widget, self.robot_name_widget,
                                        self.start_poi_widget, self.battery_lvl_widget])]),
            widgets.VBox([widgets.HBox([self.remove_widget, self.robot_to_remove_widget])]),
            self.robots_table_widget
        ]
        self.tab_widget = widgets.Tab(children=children)
        self.tab_widget.set_title(0, "Dodaj robota")
        self.tab_widget.set_title(1, "Usun robota")
        self.tab_widget.set_title(2, "Lista robotow")

    def add_robot_widget_button(self, button):
        """
        Obsluguje przycisk (add_widget) i wprowadza nowego robota do systemu.
        Parameters:
            button (Button): dodanie nowego robota
        """
        update_info("Dodano robota: " + self.robot_name_widget.value)
        robot_name = self.robot_name_widget.value
        poi_id = self.start_poi_widget.value
        robot = Robot({"id": robot_name, "edge": None, "planningOn": True, "isFree": True, "timeRemaining": 0,
                       "poiId": poi_id})
        robot.battery.capacity = robot.battery.capacity * self.battery_lvl_widget.value / 100
        self.robots.append(robot)

        self.robot_id += 1
        self.robot_name_widget.value = str(self.robot_id)
        self.update_robots_list()

    def remove_robot_widget_button(self, button):
        """
        Obsluguje przycisk (remove_widget) i usuwa wybranego z listy robota.
        Parameters:
            button (Button): przycisk od usuwania robota
        """
        i = self.robot_to_remove_widget.options.index
        for i in range(len(self.robots)):
            if self.robots[i].id == self.robot_to_remove_widget.value:
                del self.robots[i]
                break
        update_info("Usunieto robota: " + str(self.robot_to_remove_widget.value))
        self.update_robots_list()

    def check_battery_range_widget_button(self, button):
        """
        Obsluguje poprawnego zakresu kontrolki (battery_lvl_widget). Ogranicza wartosc do zakresu od <0,100>
        Parameters:
            button (FloatText): kontrolka od wprowadzania stanu naladowania robota
        """
        if button["name"] == "value":
            if self.battery_lvl_widget.value > 100:
                self.battery_lvl_widget.value = 100
            elif self.battery_lvl_widget.value < 0:
                self.battery_lvl_widget.value = 0

    def update_robots_list(self):
        """
        Aktualizuje wysiwtlana tabele (robots_table_widget) z robotami oraz kontrolke do wyboru robota
        (self.robot_to_remove_widget) do usuniecia.
        """
        self.robot_to_remove_widget.options = [robot.id for robot in self.robots]
        with self.robots_table_widget:
            self.robots_table_widget.clear_output()
            robots_data = []
            for robot in self.robots:
                robots_data.append([robot.id, robot.poi_id, robot.battery.capacity/robot.battery.max_capacity*100])
            df = pd.DataFrame(robots_data,columns=["robot_name", "POI", "Battery lvl [%]"])
            df.style.set_table_styles([dict(selector='th', props=[('text-align', 'center')])])
            left_aligned_df = df.style.set_properties(**{'text-align': 'center'})
            display(left_aligned_df)

    def export_robots_config(self):
        robots_data = []
        for robot in self.robots:
            robots_data.append({"id": robot.id, "edge": robot.edge, "planningOn": robot.planning_on,
                                "isFree": robot.is_free, "timeRemaining": robot.time_remaining, "poiId": robot.poi_id})
        return robots_data

    def import_robots_config(self, robots_data):
        self.robots = []
        for data in robots_data:
            self.robots.append(Robot(data))

        self.update_robots_list()

class TasksPatternCreator:
    """
    Klasa odpowiedzialna za obsluge i wyswietlanie panelu do konfiguracji szablonow zadan
    Atributes:
        TYPES_ID (dict): zawiera informacje o stalym id dla danego zachowania robota - odniesienie do bazy
        pattern_id (int): domyslne id nowego robota zwiekszajace sie o 1 z kazdym dodanym robotem
        new_behaviours_config ([]): lista przechowujaca informacje o tymczasowych zachowaniach do dodania
        tasks_pattern ([Task, Task, ...]): lista wprowadzonych szablonow zadan

        Widgety
            tab_widget (Tab): zakladki do dodawania, usuwania i wyswietlania aktualnie skonfigurowanych szablonow
                                   zadan

        Widgety dla panelu dodaj szablon zadania
            beh_config_output_widget (Text): wyswietla kolejne zachowania z szablonu do wykonania
            pattern_name_widget (Text): nazwa szablonu zadania, domyslnie wartosc z self.pattern_id
            poi_widget (Dropdown): lista z poi do wyboru. Widoczna gdy wybrane jest zachowanie GO_TO
            beh_widget (Dropdown): lista rozwijana do wyboru jednego z zachowan GO_TO, DOCK, WAIT, BAT_EX, UNDOCK
            add_beh_widget (Button): przycisk odpowiadajacy za dodanie nowego zachowania do zadania
            clear_beh_widget (Button): przycisk od wyczyszczenia wszystkich dotychczasowo wprowadzonych zachowniach
                                       w zadaniu
            priority_widget (Dropdown): wybor priorytetu zadania
            add_task_widget (Button): przycisk od dodawania nowego szablonu zadania

        Widgety dla panelu usun szablon zadania
            remove_widget (Button): przycisk potwierdzajacy usuniecie wybranego szablonu
            pattern_to_remove_widget (Dropdown): lista rozwijana z nazwami szablonow do usuniecia

        Widgety dla panelu z lista aktualnie skonfigurowanych szablonow
            tasks_table_widget (Output): wyswietla tabele z lista wprowadzonych aktualnie szablonow zadan
                                              (pattern_id (nazwa szablonu), priorytet, zachowania w zadaniu)
    """

    TYPES_ID = {  # slownik wartosci zachowan dla robota, wartoscia jest stala nazwa dla danego typu zachowania
        "GO_TO": "1",
        "DOCK": "2",
        "WAIT": "3",
        "BAT_EX": "4",
        "UNDOCK": "5"
    }
    def __init__(self, pois_raw):
        """
        Inicjalizacja i utworzenie interfejsu do obslugi konfiguracji szablonow zadan w systemie do testow.
        Parameters:
            pois_raw: ([{"id": string, "pose": (float,float)), "type": gc.base_node_type["..."]}, ...]) - lista
                POI w systemie
        """
        self.pattern_id = 0
        self.new_behaviours_config = []
        self.tasks_pattern = []
        self.create_tabs(pois_raw)

    def create_add_panel(self, pois_raw):
        """
        Odpowiada za utworzenie panelu do wprowadzania nowych szablonow zadan.
        Parameters:
            pois_raw: ([{"id": string, "pose": (float,float)), "type": gc.base_node_type["..."]}, ...]) - lista
                POI w systemie
        """
        self.beh_config_output_widget = widgets.Text(value=str(self.pattern_id), description='Zachowania:',
                                                     layout=widgets.Layout(width='95%'))
        self.pattern_name_widget = widgets.Text(value=str(self.pattern_id), description='Nazwa szablonu:',
                                                layout=widgets.Layout(width='95%'))

        pois = [poi["id"] for poi in pois_raw]
        self.poi_widget = widgets.Dropdown(options=pois, value=pois[0], description='POI:', disabled=False,
                                           layout=widgets.Layout(visibility='hidden'))
        behaviours = sorted([beh_type for beh_type in Behaviour.TYPES.values()])
        self.beh_widget = widgets.Dropdown(options=behaviours, value=behaviours[0], description='beh_type:',
                                           disabled=False,)
        self.add_beh_widget = widgets.Button(description='Add behaviour', disabled=False, button_style='', icon='check')
        self.clear_beh_widget = widgets.Button(description='Clear behaviours', disabled=False, button_style='',
                                               icon='check')

        priorities = ["low", "normal", "high"]
        self.priority_widget = widgets.Dropdown(options=priorities, value=priorities[0], description='priority:',
                                                disabled=False)

        self.add_task_widget = widgets.Button(description='Add task', disabled=False, button_style='', icon='check')

        self.add_task_widget.on_click(self.add_task_widget_button)
        self.add_beh_widget.on_click(self.add_behaviour_widget_button)
        self.clear_beh_widget.on_click(self.clear_behaviours_widget_button)
        self.beh_widget.observe(self.observe_beh_type_widget_button)

    def create_remove_panel(self):
        """
        Utworzenie panelu do usuwania szablonow.
        """
        self.remove_widget = widgets.Button(description='Remove task pattern', disabled=False, button_style='',
                                            icon='check')
        self.pattern_to_remove_widget = widgets.Dropdown(options=[task.id for task in self.tasks_pattern],
                                                         description='Task pattern:', disabled=False)
        self.remove_widget.on_click(self.remove_task_pattern_widget_button)

    def create_tabs(self, pois_raw):
        """
        Odpowiada za utworzenie interfejsu konfiguratora szablonow zadan (dowanie, usuwanie, wyswietlanie listy
        aktualnie dostepnych szablonow).

        Parameters:
            pois_raw: ([{"id": string, "pose": (float,float)), "type": gc.base_node_type["..."]}, ...]) - lista
                POI w systemie
        """
        self.create_add_panel(pois_raw)
        self.create_remove_panel()
        self.tasks_table_widget = widgets.Output(layout=widgets.Layout(height=HEIGHT_TABLES, overflow_y='auto'))

        children = [
            widgets.VBox([self.beh_config_output_widget, self.pattern_name_widget,
                          widgets.HBox([self.poi_widget, self.beh_widget, self.add_beh_widget, self.clear_beh_widget]),
                          widgets.HBox([self.priority_widget, self.add_task_widget])]),
            widgets.VBox([widgets.HBox([self.remove_widget, self.pattern_to_remove_widget])]),
            self.tasks_table_widget
        ]
        self.tab_widget = widgets.Tab(children=children)
        self.tab_widget.set_title(0, "Dodaj szablon zadania")
        self.tab_widget.set_title(1, "Usun szablon zadania")
        self.tab_widget.set_title(2, "Lista szablonow zadan")

    def remove_task_pattern_widget_button(self, button):
        """
        Obsluguje przycisk (remove_widget) usuwajacy szablon zadania.
        Parameters:
            button (Button): przycisk usuwajacy wybrany szablon zadania
        """
        i = self.pattern_to_remove_widget.options.index
        for i in range(len(self.tasks_pattern)):
            if self.tasks_pattern[i].id == self.pattern_to_remove_widget.value:
                del self.tasks_pattern[i]
                break
        self.update_tasks_pattern_list()
        update_info("Usunieto szablon zadania: " + str(i))

    def update_tasks_pattern_list(self):
        """
        Aktualizuje wyswietlana liste szablonow (tasks_table_widget) oraz liste szablonow do usuniecia
        (pattern_to_remove_widget).
        """
        self.pattern_to_remove_widget.options = [task.id for task in self.tasks_pattern]
        with self.tasks_table_widget:
            self.tasks_table_widget.clear_output()
            pattern_tasks_data = []
            for task in self.tasks_pattern:
                behaviours = ""
                for behaviour in task.behaviours:
                    behaviours += behaviour.get_type()
                    if behaviour.check_if_go_to():
                        behaviours += ": " + str(behaviour.get_poi())
                    behaviours += ", "

                pattern_tasks_data.append([task.id, task.priority, behaviours])
            df = pd.DataFrame(pattern_tasks_data,columns=["pattern id", "priorytet", "Behaviours"])

            df.style.set_table_styles([dict(selector='th', props=[('text-align', 'center')])])
            left_aligned_df = df.style.set_properties(**{'text-align': 'center'})
            display(left_aligned_df)

    def add_task_widget_button(self, button):
        """
        Obsluguje przycisk (add_task_widget) dodajacy szablon zadania.
        Parameters:
            button (Button): przycisk dodajacy nowy szablon zadania
        """
        priorities = {"low": 1, "normal": 2, "high": 3}
        task = Task({"id": self.pattern_name_widget.value,
         "behaviours": self.new_behaviours_config,
         "current_behaviour_index": -1, #index tablicy nie zachowania
         "status": Task.STATUS_LIST["TO_DO"],
         "robot": None,
         "start_time": "2018-06-29 07:37:27",
         "weight": priorities[self.priority_widget.value],
         "priority": priorities[self.priority_widget.value]
        })
        self.tasks_pattern.append(task)
        update_info("Dodano zadanie: " + str(self.pattern_name_widget.value))

        self.new_behaviours_config = []
        self.update_behaviour_config()
        self.update_tasks_pattern_list()
        self.pattern_id += 1
        self.pattern_name_widget.value = str(self.pattern_id)

    def add_behaviour_widget_button(self, button):
        """
        Obsluguje przycisk (add_beh_widget) dodajacy zachowanie do nowego zadania.
        Parameters:
            button (Button): przycisk dodajacy nowy szablon zadania
        """
        behaviour = {}
        poi_id = self.poi_widget.value
        beh_type = self.beh_widget.value
        if beh_type != Behaviour.TYPES["goto"]:
            behaviour = {"id": self.TYPES_ID[beh_type], "parameters": {"name": beh_type}}
        else:
            behaviour = {"id": self.TYPES_ID[beh_type], "parameters": {"name": beh_type, "to": poi_id}}

        update_info("Dodano zachowanie: " + beh_type)
        self.new_behaviours_config.append(behaviour)
        self.update_behaviour_config()

    def update_behaviour_config(self):
        """
        Aktualizuje wyswietlanie (beh_config_output_widget) aktualnie skonfigurowanych zachowan w szablonie.

        """
        self.beh_config_output_widget.value = ""
        for behaviour in self.new_behaviours_config:
            beh_type = behaviour["parameters"]["name"]
            if beh_type != Behaviour.TYPES["goto"]:
                self.beh_config_output_widget.value += beh_type + ", "
            else:
                self.beh_config_output_widget.value += beh_type + ": " + behaviour["parameters"]["to"] + ", "

    def clear_behaviours_widget_button(self, button):
        """
        Obsluguje przycisk (clear_beh_widget) czyszczacy konfiguracje zachowan
        Parameters:
            button (Button): przycisk czyszczacy wszystkie dotychczas skonfigurowane zachowania
        """
        self.new_behaviours_config = []
        self.update_behaviour_config()
        update_info("Clear behaviours")

    def observe_beh_type_widget_button(self, button):
        """
        Obsluguje przycisk (beh_widget) odpowiedzialny za wybor zachowania. Dla zachowania GO_TO ustawia
        widocznosc przycisku od wyboru POI (poi_widget), a dla pozostalych jest on niewidoczny.
        Parameters:
            button (Button): przycisk (beh_widget) od wyboru zachowania
        """
        if self.beh_widget.value == "GO_TO":
            self.poi_widget.layout.visibility = "visible"
        else:
            self.poi_widget.layout.visibility = "hidden"

    def export_tasks_pattern_config(self):
        patterns_data = []
        for pattern in self.tasks_pattern:
            behaviours = []
            for behaviour in pattern.behaviours:
                behaviours.append({"id": behaviour.id, "parameters": behaviour.parameters})
            patterns_data.append({"id":pattern.id, "behaviours": behaviours,
                                 "current_behaviour_index": pattern.current_behaviour_index, "status":pattern.status,
                                 "robot": pattern.robot_id, "start_time": pattern.start_time, "weight": pattern.weight,
                                 "priority": pattern.priority})
        return patterns_data

    def import_tasks_pattern_config(self, patterns_data):
        self.tasks_pattern = []
        for data in patterns_data:
            self.tasks_pattern.append(Task(data))

        self.update_tasks_pattern_list()

class TopStatePanel:
    """
    Klasa odpowiada za obsluge panelu z podstawowymi informacjami o stanie systemu w trakcie testu.
    Attributes:
        Widgety
            panel_widget (Tab): glowne GUI panelu

            robots_on_edge_widget (Button): informuje o prawidlowym stanie liczbowym robotow na krawedziach i w
                                            grupach (1)
            discharged_robots_widget (Button): przycisk informuje o liczbie rozladowanych robotow
            warrrning_battery_widget (Button): przycisk informuje o liczbie robotow z poziomem naladowania baterii
                                               ponizej progu ostrzegawczego
            critical_battery_widget (Button): przycisk informuje o liczbie robotow z poziomem naladowania baterii
                                              ponizej progu krytycznego

            to_do_tasks_widget (Button): wyswietla liczbe zadan do wykonania
            in_progress_tasks_widget (Button): wyswietla liczbe zadan w trakcie wykonywania
            done_tasks_widget (Button): wyswietla liczbe wykonanych zadan

            all_tasks_widget (Text): informacja o liczbie wszystkich zadan (bez wymian baterii)
            all_swaps_widget (Text): informacja o wsyzstkich wykonanych zadaniach wymiany baterii
    """
    def __init__(self):
        """
        Inicjalizacja klasy od obslugi panelu z podstawowymi informacjami o stanie systemu.
        """
        button_layout = widgets.Layout(width='190px', height='30px')
        self.robots_on_edge_widget = widgets.Button(description='OK liczba robotow',
                                                    disabled=False, tooltip="Odpowiednia liczba robotow na krawedziach"
                                                                            "grafu", button_style='success', icon='',
                                                    layout=button_layout)
        self.discharged_robots_widget = widgets.Button(description='Rozladowane roboty: ', disabled=False,
                                                       button_style='success', icon='', layout=button_layout)
        self.warrrning_battery_widget = widgets.Button(description='Bateria < warrning: ', disabled=False,
                                                       button_style='success', icon='', layout=button_layout)
        self.critical_battery_widget = widgets.Button(description='Bateria < critical: ', disabled=False,
                                                       button_style='success', icon='', layout=button_layout)
        self.to_do_tasks_widget = widgets.Button(description='TO_DO: ', disabled=False, button_style='', icon='',
                                                 layout=button_layout)
        self.in_progress_tasks_widget = widgets.Button(description='IN_PROGRESS: ', disabled=False, button_style='info',
                                                       icon='', layout=button_layout)
        self.done_tasks_widget = widgets.Button(description='DONE: ', disabled=False, button_style='success', icon='',
                                                layout=button_layout)

        self.all_tasks_widget = widgets.Text(value="0")
        self.all_swaps_widget = widgets.Text(value="0")

        left_robots_column = widgets.VBox([self.robots_on_edge_widget, self.discharged_robots_widget])
        right_robots_column = widgets.VBox([self.warrrning_battery_widget, self.critical_battery_widget])
        left_task_column =  widgets.VBox([widgets.Label("Wszystkie zadania"), self.all_tasks_widget,
                                          widgets.Label("Wykonane wymiany baterii"), self.all_swaps_widget])
        right_task_column =  widgets.VBox([widgets.Label("Zadania"), self.to_do_tasks_widget,
                                           self.in_progress_tasks_widget, self.done_tasks_widget])
        robots_panel = widgets.VBox([widgets.Label("Stan robotow"), widgets.HBox([left_robots_column,
                                                                                  right_robots_column])])
        task_panel = widgets.VBox([widgets.Label("Stan zadan"), widgets.HBox([left_task_column, right_task_column])])

        self.panel_widget = widgets.HBox([robots_panel, task_panel])

    def set_valid_graph_status(self, valid_graph):
        """
        Aktualizacja kontrolki (robots_on_edge_widget) w zaleznosci od tego czy wystepuje bledna liczba robotow
        czy nie. DLa blednej zmieniony jest styl na "danger", a dla poprawnej wartosci na "success".
        Parameters:
            error (bool): informacja czy jest bledna liczba robotow na krawedziach, w grupie krawedzi
        """
        if valid_graph:
            self.robots_on_edge_widget.button_style = "success"
            self.robots_on_edge_widget.description = 'OK liczba robotow'
        else:
            self.robots_on_edge_widget.button_style = "danger"
            self.robots_on_edge_widget.description = 'Error liczba robotow'

    def set_discharged_robots(self, discharged_robots):
        """
        Aktualizacja kontrolki (discharged_robots_widget). Wyswietlenie liczby rozladowanych robotow oraz zmiana
        stylu przycisku. Jesli jakis robot jest rozladowany to styl "danger", w przeciwnym wypadku "success".
        Parameters:
            discharged_robots (int): liczba rozladowanych robotow.
        """
        self.discharged_robots_widget.description = 'Rozladowane roboty: ' + str(discharged_robots)
        if discharged_robots != 0:
            self.discharged_robots_widget.button_style = "danger"
        else:
            self.discharged_robots_widget.button_style = "success"

    def set_battery_warning_robots(self, warning_robots):
        """
        Aktualizacja kontrolki (warrrning_battery_widget). Jesli jakis robot jest ponizej tego poziomu, a przed
        wystapieniem poziomu krytycznego to ustawiany jest styl przycisku "warning", w przeciwnym wypadku "success".
        Parameters:
            warning_robots (int): liczba robotow z poziomem ostrzegawczym baterii
        """
        self.warrrning_battery_widget.description = 'Bateria < warrning: ' + str(warning_robots)
        if warning_robots != 0:
            self.warrrning_battery_widget.button_style = "warning"
        else:
            self.warrrning_battery_widget.button_style = "success"

    def set_battery_critical_robots(self, critical_robots):
        """
        Aktualizacja kontrolki (warrrning_battery_widget). Jesli jakis robot jest ponizej tego poziomu, a przed
        wystapieniem poziomu krytycznego to ustawiany jest styl przycisku "warning", w przeciwnym wypadku "success".
        Parameters:
            critical_robots (int): liczba robotow z poziomem ostrzegawczym baterii
        """
        self.critical_battery_widget.description = 'Bateria < critical: ' + str(critical_robots)
        if critical_robots != 0:
            self.critical_battery_widget.button_style = "danger"
        else:
            self.critical_battery_widget.button_style = "success"

    def set_all_tasks_number(self, tasks_number):
        """
        Aktualizacja kontrolki (all_tasks_widget) i wyswietlenie liczby wszystkich zadan.
        Parameters:
             tasks_number (int): liczba zadan
        """
        self.all_tasks_widget.value = str(tasks_number)

    def set_all_swap_tasks_number(self, tasks_number):
        """
        Aktualizacja kontrolki (all_swaps_widget) i wyswietlenie liczby wszystkich wykonanych zadan
        wymiany baterii.
        Parameters:
             tasks_number (int): liczba zadan wymiany baterii
        """
        self.all_swaps_widget.value = str(tasks_number)

    def set_all_tasks_to_do_number(self, tasks_number):
        """
        Aktualizacja kontrolki (to_do_tasks_widget) i wyswietlenie liczby wszystkich aktualnie wykonywanych zadan
        ze statusem TO_DO z pominieciem zadan wymiany baterii.
        Parameters:
             tasks_number (int): liczba zadan ze statusem TO_DO
        """
        self.to_do_tasks_widget.description = "TO_DO: " + str(tasks_number)

    def set_all_tasks_in_progress_number(self, tasks_number):
        """
        Aktualizacja kontrolki (in_progress_tasks_widget) i wyswietlenie liczby wszystkich aktualnie wykonywanych zadan
        ze statusem IN_PROGRESS z pominieciem zadan wymiany baterii.
        Parameters:
             tasks_number (int): liczba zadan ze statusem IN_PROGRESS
        """
        self.in_progress_tasks_widget.description = "IN_PROGRESS: " + str(tasks_number)

    def set_all_tasks_done_number(self, tasks_number):
        """
        Aktualizacja kontrolki (done_tasks_widget) i wyswietlenie liczby wszystkich aktualnie wykonywanych zadan
        ze statusem DONE z pominieciem zadan wymiany baterii.
        Parameters:
             tasks_number (int): liczba zadan ze statusem DONE
        """
        self.done_tasks_widget.description = "DONE: " + str(tasks_number)

class TaskPanel:
    """
    Klasa odpowiedzialna za konfiguracje i obsluge panelu do tworzenia nowych zadan na podstawie juz istniejacej
    listy robotow i szablonow.
    Attributes:
        task_id (int): id nowego zadania
        tasks (list(Task)): lista zadan do wykonania
        patterns (list(Task)): lista szablonow do tworzenia zadan
        robots_id (list(string)): lista z id robotow do wyboru przy tworzeniu zadania. Z uwzglednieniem braku
                                  przypisania robotu do zadania (None).

        Widgety
            tab_widget (Tab): GUI panelu do konfiguracji zadan

            task_name_widget (Text): nazwa zadania, domyslnie jest generowana na podstawie zwiekszajacej sie wartosci
                                     "task_id" po dodaniu nowego zadania
            patterns_widget (Dropdown): wybor z listy szablonu zadania do dodania
            robots_widget (Dropdown): wybor z listy robota, ktory ma byc przypisany do zadania
            add_task_widget (Button): dodanie nowego zadania

            task_to_remove_widget (Dropdown): lista rozwijana z wyborem zadania do usuniecia
            remove_task_widget (Button): przycisk od usuwania wybranego zadania
            remove_all_tasks_widget (Buttono): przycisk od usuwania wszystkich dotychczas wprowadzonych zadan

            tasks_to_create_widget (IntText): liczba zadan do wygenerowania
            add_auto_created_tasks_widget (Button): przycisk generujacy podana liczbe zadan

            # TODO konfigurator cyklicznych zadan
            tasks_table_widget (Output): wyswietla tabele ze skonfigurowanymi zadaniami do wykonania
    """
    def __init__(self, task_patterns, robots):
        """
        Inicjalizacja panelu do konfiguracji i obslugi zadan.
        Parameters:
            task_patterns (list(Task)): lista szablonow zadan
            robots (list(Robot)): lista robotow w systemie
        """
        self.task_id = 0
        self.tasks = []
        self.patterns = task_patterns
        self.robots_id = [None] + [robot.id for robot in robots]
        self.tasks_table_widget = widgets.Output(layout=widgets.Layout(height=HEIGHT_TABLES, width = "100%",
                                                                       overflow_y='auto'))
        self.tab_widget = widgets.Tab([self.create_new_task_tab(), self.create_remove_task_tab(),
                                       self.create_auto_creator_tasks_tab(),
                                       widgets.Output(), self.tasks_table_widget])
        self.tab_widget.set_title(0, "Nowe")
        self.tab_widget.set_title(1, "Usun zadanie")
        self.tab_widget.set_title(2, "Generator zadan")
        self.tab_widget.set_title(3, "Konfigurator cyklicnzych zadan") # TODO
        self.tab_widget.set_title(4, "Zadania do wykonania")

    def create_new_task_tab(self):
        """
        Odpowiada za utworzenie panelu do obslugi dodawania nowych zadan.
        Returns:
            (widgets.VBox): zakladka z ulozonymi kontrolkami dla panelu od dodawania nowego zadania (task_name_widget,
                            patterns_widget, robots_widget, add_task_widget)
        """
        self.task_name_widget = widgets.Text(value=str(self.task_id))
        paterns_ids = [task.id for task in self.patterns]
        self.patterns_widget = widgets.Dropdown(options=paterns_ids, description='task pattern id:', disabled=False)
        self.robots_widget = widgets.Dropdown(options=self.robots_id, value=self.robots_id[0], description='robot id:',
                                              disabled=False,)
        self.add_task_widget = widgets.Button(description='Dodaj zadanie', disabled=False, button_style='',
                                              icon='check')
        self.add_task_widget.on_click(self.add_task_widget_button)
        return widgets.VBox([widgets.HBox([self.task_name_widget, self.patterns_widget, self.robots_widget]),
                                           self.add_task_widget])

    def create_auto_creator_tasks_tab(self):
        """
        Utworzenie panelu do automatycznego generowania zadan w zaleznosci od podanej liczby (tasks_to_create_widget).
        Returns:
             (widgets.HBox): ulozone kontrolki dla panelu od generatora zadan (tasks_to_create_widget,
                             add_auto_created_tasks_widget)
        """
        self.tasks_to_create_widget = widgets.IntText(value=10, description='Zadania do wygenerowania', disabled=False)
        self.add_auto_created_tasks_widget = widgets.Button(description='Generuj zadania', disabled=False,
                                                            button_style='', icon='check')
        self.add_auto_created_tasks_widget.on_click(self.add_auto_created_tasks)
        return widgets.HBox([self.tasks_to_create_widget, self.add_auto_created_tasks_widget])

    def create_remove_task_tab(self):
        """
        Odpowiada za wygenerowanie panelu do obslugi usuwania zadan
        Returns:
            (widgets.VBox): ulozone kontrolki dla panelu do usuwania zadan (task_to_remove_widget, remove_task_widget,
                            remove_all_tasks_widget)
        """
        tasks_ids = [task.id for task in self.tasks]
        self.task_to_remove_widget = widgets.Dropdown(options=tasks_ids, description='ID zadania do usuniecia:',
                                                      disabled=False)
        self.remove_task_widget = widgets.Button(description='Usun zadanie', disabled=False, button_style='',
                                                 icon='check')
        self.remove_all_tasks_widget = widgets.Button(description='Usun wszystkie zadania', disabled=False,
                                                      button_style='', icon='check' )
        self.remove_task_widget.on_click(self.remove_task_widget_button)
        self.remove_all_tasks_widget.on_click(self.remove_all_tasks_widget_button)
        return widgets.VBox([widgets.HBox([self.task_to_remove_widget, self.remove_task_widget]),
                             self.remove_all_tasks_widget])

    def add_task_widget_button(self, button):
        """
        Obsluguje przycisk (add_task_widget) i wprowadza nowego zadanie do systemu.
        Parameters:
            button (Button): dodanie nowego zadania
        """
        update_info("Dodano zadanie: " + self.task_name_widget.value)
        for pattern in self.patterns:
            if pattern.id == self.patterns_widget.value:
                task = copy.copy(pattern)
                task.robot_id = self.robots_widget.value
                task.id = self.task_name_widget.value
                self.tasks.append(task)
                break

        self.update_tasks_list()
        self.task_id += 1
        self.task_name_widget.value = str(self.task_id)

    def remove_task_widget_button(self, button):
        """
        Obsluguje przycisk (remove_task_widget) usuwajacy zadanie z systemu.
        Parameters:
            button (Button): usuniecie zadania
        """
        for i in range(len(self.tasks)):
            if self.tasks[i].id == self.task_to_remove_widget.value:
                del self.tasks[i]
                break
        update_info("Usunieto zadanie: " + str(self.task_to_remove_widget.value))
        self.update_tasks_list()

    def remove_all_tasks_widget_button(self, button):
        """
        Obsluguje przycisk (remove_all_tasks_widget) usuwajacy wszystkie zadania z systemu.
        Parameters:
            button (Button): usuwa wszystkie zadania
        """
        self.tasks = []
        self.update_tasks_list()
        update_info("Wyczyszczenie listy zadan.")

    def set_new_panel_data(self, patterns, robots):
        """
        Ustawia nowe wartosci dla szablonow i obslugiwanych robotow do konfiguracji nowych zadan na podstawie szablonow.
        Parameters:
            patterns (list(Task)): lista szablonow
            robots(list(Robot)): lista robotow w systemie
        """
        self.patterns = patterns
        self.patterns_widget.options = [task.id for task in self.patterns]

        self.robots_id = [None] + [robot.id for robot in robots]
        self.robots_widget.options = self.robots_id

        self.update_tasks_list()

    def update_tasks_list(self):
        """
        Aktualizacja kontrolek (task_to_remove_widget, tasks_table_widget) zaleznych od liczby zadan w systemie.
        """
        # aktualizacja kontrolki z lista rozwijana z zadaniami
        self.task_to_remove_widget.options = [task.id for task in self.tasks]
        # aktualizacja wyswietlanej tablicy
        with self.tasks_table_widget:
            self.tasks_table_widget.clear_output()
            tasks_data = []
            for task in self.tasks:
                behaviours = ""
                for behaviour in task.behaviours:
                    behaviours += behaviour.get_type()
                    if behaviour.check_if_go_to():
                        behaviours += ": " + str(behaviour.get_poi())
                    behaviours += ", "

                tasks_data.append([task.id, task.robot_id, task.priority, behaviours])
            df = pd.DataFrame(tasks_data,columns=["task id", "robot", "priorytet", "zachowania"])

            df.style.set_table_styles([dict(selector='th', props=[('text-align', 'center')])])
            left_aligned_df = df.style.set_properties(**{'text-align': 'center'})
            display(left_aligned_df)

    def add_auto_created_tasks(self, button):
        """
        Obsluguje przycisk (add_auto_created_tasks_widget) generujacy losowo na podstawie szablonow okreslona liczbe
        zadan. Prawdopodobienstwo przypisania robota do zadania wynosi mniej niz 20%. Wiekszosc zadan pozostaje wolna
        do przydzielenia przez dispatchera.
        Parameters:
            button (Button): przycisk od wywolania akcji automatycznego generowania zadan
        """
        update_info("Liczba automatycznie wygenerowanych zadan: " + str(self.tasks_to_create_widget.value))
        n_patterns = len(self.patterns)
        n_robots = len(self.robots_id)

        for i in range(self.tasks_to_create_widget.value):
            task = copy.copy(self.patterns[random.randrange(0, n_patterns, 1)])
            assign_robot = 0
            if random.randrange(0, 100, 1) > 80:
                # wylosowac robota
                task.robot_id = self.robots_id[random.randrange(0, n_robots, 1)]
            else:
                # zadanie z nieprzypisanym robotem
                task.robot_id = None
            task.id = str(self.task_id)
            self.tasks.append(task)
            self.task_id += 1

        self.update_tasks_list()
        self.task_name_widget.value = str(self.task_id)

    def export_tasks_config(self):
        tasks_data = []
        for pattern in self.tasks:
            behaviours = []
            for behaviour in pattern.behaviours:
                behaviours.append({"id": behaviour.id, "parameters": behaviour.parameters})

            tasks_data.append({"id":pattern.id, "behaviours": behaviours,
                                 "current_behaviour_index": pattern.current_behaviour_index, "status":pattern.status,
                                 "robot": pattern.robot_id, "start_time": pattern.start_time, "weight": pattern.weight,
                                 "priority": pattern.priority})
        return tasks_data

    def import_tasks_config(self, tasks_data):
        self.tasks = []
        for data in tasks_data:
            self.tasks.append(Task(data))

        self.update_tasks_list()

class TestGuiPanel:
    """
    Klasa odpowiedzialna za obsluge panelu do konfigurowania i monitorowania przebiegu symulacji przydzielania zadan
    w dlugookresowym horyzoncie czasowym/ z duza liczba zadan i robotow.

    Attributes:
        top_panel (TopStatePanel): panel z ogolnym stanem symulacji
        robots_creator (RobotsCreator): panel od obslugi konfiguracji robotow
        task_pattern_creator (TasksPatternCreator): panel od obslugi szablonow zadan
        task_panel (TaskPanel): panel od obslugi zadan

        Widgety
            graph_widget (Output): wyswietlanie grafu wraz z aktualna liczba robotow na krawedzi
            robots_table_widget (Output): wyswietla tabele ze stanem robotow (kolumny: robot_id, task_id,
                                          status_is_free, end_behaviour, battery_lvl, edge)
            tasks_table_widget (Output): wyswietla tabele ze stanem zadan (kolumny: task_id, status, goal_id,
                                         zachowanie, id_robota)
            edges_table_widget (Output): wyswietla tabele z obciazeniem robotami krawedzi grafu (kolumny: group, edge,
                                         max_robots, robots_on_edge, robots_id)
            main_tab_widget (VBox): kompletne GUI do konfiguracji i monitorowania stanu systemu (bez graph_widget)
            import_config_widget (FileUpload): zaladowanie pliku z konfiguracja symulacji
            config_file_name_widget (Text): nazwa pliku .json pod jaka ma byc zapisana ustawiona konfiguracja
            export_config_widget (Button): przycisk wywolujacy akcje zapisu konfiguracji do pliku w katalogu, w ktorym
                                           zostal uzyty
    """
    def __init__(self, pois_raw):
        """
        Inicjalizacja klasy do obslugi GUI konfiguracyjnego i monitorujacego stan systemu.
        Parameters:
            pois_raw: ([{"id": string, "pose": (float,float)), "type": gc.base_node_type["..."]}, ...]) - lista
                POI w systemie
        """
        self.init_gui(pois_raw)

    def init_gui(self, pois_raw):
        """
        Inicjalizacja i utworzenie interfejsu do obslu
        gi GUI panelu konfiguracyjnego i monitorujacego symulacje.
        Parameters:
            pois_raw: ([{"id": string, "pose": (float,float)), "type": gc.base_node_type["..."]}, ...]) - lista
                POI w systemie
        """
        global INFO_OUTPUT
        self.graph_widget = widgets.Output()

        self.top_panel = TopStatePanel()
        self.robots_creator = RobotsCreator(pois_raw)
        self.task_pattern_creator = TasksPatternCreator(pois_raw)
        self.task_panel = TaskPanel(self.task_pattern_creator.tasks_pattern, self.robots_creator.robots)

        self.import_config_widget = widgets.FileUpload(accept='', multiple=False)
        self.config_file_name_widget = widgets.Text(value="config", description="nazwa pliku")
        self.export_config_widget = widgets.Button(description='Zapisz konfiguracje', disabled=False, button_style='',
                                                  icon='')

        configurator_tab = widgets.Tab([widgets.HBox([self.import_config_widget, self.config_file_name_widget,
                                                      self.export_config_widget]), self.robots_creator.tab_widget,
                                          self.task_pattern_creator.tab_widget, self.task_panel.tab_widget])
        configurator_tab.set_title(0, "Ogolne")
        configurator_tab.set_title(1, "Roboty")
        configurator_tab.set_title(2, "Szablony")
        configurator_tab.set_title(3, "Zadania")

        self.robots_table_widget = widgets.Output(layout=widgets.Layout(height=HEIGHT_TABLES, overflow_y='auto'))
        self.tasks_table_widget = widgets.Output(layout=widgets.Layout(height=HEIGHT_TABLES, overflow_y='auto'))
        robots_task = widgets.HBox([widgets.VBox([widgets.Label("Roboty"),self.robots_table_widget]),
                                    widgets.VBox([widgets.Label("Zadania"),self.tasks_table_widget])])

        self.edges_table_widget = widgets.Output(layout=widgets.Layout(height=HEIGHT_TABLES, overflow_y='auto'))

        children = [configurator_tab, robots_task, self.edges_table_widget]
        main_tab = widgets.Tab(children=children)
        main_tab.set_title(0, "Konfigurator")
        main_tab.set_title(1, "Roboty / Zadania") # tabela
        main_tab.set_title(2, "Krawedzie grafu") # tabela

        self.main_tab_widget = widgets.VBox([self.top_panel.panel_widget, INFO_OUTPUT, main_tab])

        self.task_pattern_creator.add_task_widget.on_click(self.update_created_tasks_list)
        self.task_pattern_creator.remove_widget.on_click(self.update_created_tasks_list)
        self.robots_creator.add_widget.on_click(self.update_created_tasks_list)
        self.robots_creator.remove_widget.on_click(self.update_created_tasks_list)

        self.import_config_widget.observe(self.import_config)
        self.export_config_widget.on_click(self.export_config)

    def update_created_tasks_list(self, button):
        """
        Odpowiada za aktualizacje listy zadan po dodaniu/usunieciu szablonu zadania, dodaniu/usunieciu robota.
        Parameters:
            button (Button): przycisk
        """
        self.task_panel.set_new_panel_data(self.task_pattern_creator.tasks_pattern, self.robots_creator.robots)

    def update_sim_state(self, graph, robots, tasks):
        """
        Odpowiada za aktualizację wyswietlanych danych o aktualnym stanie grafu, robotow i zadan.
        Parameters:
            graph  (SupervisorGraphCreator): graf z robotami na krawedziach
            robots ({"id": Robot, "id": Robot, ...}): slownik z aktualnym stanem robotow w systemie
            tasks (list(Task)): lista z aktualnym stanem zadan
        """
        self.update_graph(graph)
        self.update_robots_table(robots)
        self.update_tasks_table(tasks)

    def update_graph(self, graph, print_graph=False):
        """
        Aktualizacja tabeli z zajetoscia krawedzi i wyswietlenie nowego grafu.
        Parameters:
            graph (SupervisorGraphCreator): graf z robotami na krawedziach.
        """
        with self.edges_table_widget:
            self.edges_table_widget.clear_output()
            edge_data = []
            for edge in graph.graph.edges(data=True):
                group_id = edge[2]["edgeGroupId"]
                max_robots = edge[2]["maxRobots"] if "maxRobots" in edge[2] else 1
                robots = edge[2]["robots"]
                if len(robots) > 0:
                    edge_data.append([group_id, (edge[0], edge[1]), max_robots, len(robots), robots])

            df = pd.DataFrame(edge_data, columns=["group", "edge", "max_robots", "robots_on_edge", "robots_id"])
            df.style.set_table_styles([dict(selector='th', props=[('text-align', 'center')])])
            df.sort_values(by=["group", "edge", "robots_on_edge"], inplace=True, ascending=False)
            left_aligned_df = df.style.set_properties(**{'text-align': 'center'})
            display(left_aligned_df)

        if print_graph:
            with self.graph_widget:
                self.graph_widget.clear_output()
                plt.figure(figsize=(15,15))
                plt.axis('equal')
                node_pos = nx.get_node_attributes(graph.graph, "pos")

                max_robots = nx.get_edge_attributes(graph.graph, "maxRobots")
                node_col = [graph.graph.nodes[i]["color"] for i in graph.graph.nodes()]

                nx.draw_networkx(graph.graph, node_pos, node_color=node_col, node_size=200, font_size=10,
                                 with_labels=True, font_color="w", width=2)
                nx.draw_networkx_edge_labels(graph.graph, node_pos, edge_labels=max_robots, font_size=10)
                plt.show()

    def update_robots_table(self, robots):
        """
        Odpowiada za aktualizacje tabeli ze stanem robotow w systemie.
        Parameters:
            robots ({"id": Robot, "id": Robot, ...}): slownik z aktualnym stanem robotow w systemie
        """
        with self.robots_table_widget:
            self.robots_table_widget.clear_output()
            robots_data = []
            for robot_id in sorted(robots.keys()):
                robot = robots[robot_id]
                task_id = None if robot.task is None else robot.task.id
                battery_lvl = robot.battery.capacity/robot.battery.max_capacity * 100
                robots_data.append([robot.id, task_id, robot.is_free, robot.end_beh_edge, battery_lvl, robot.edge])

            df = pd.DataFrame(robots_data, columns=["robot_id", "task_id", "status_is_free", "end_behaviour",
                                                    "battery_lvl", "edge"])
            df.style.set_table_styles([dict(selector='th', props=[('text-align', 'center')])])
            df.sort_values(by=['battery_lvl', 'robot_id'], inplace=True)
            left_aligned_df = df.style.set_properties(**{'text-align': 'center'})
            display(left_aligned_df)

    def update_tasks_table(self, tasks):
        """
        Odpowiada za aktualizacje tabeli z lista zadan.
        Parameters:
            tasks (list(Task)): lista z aktualnym stanem zadan
        """
        with self.tasks_table_widget:
            self.tasks_table_widget.clear_output()
            tasks_data = []
            for task in tasks:
                if task.status != Task.STATUS_LIST["DONE"]:
                    behaviour = task.get_current_behaviour()
                    tasks_data.append([task.id, task.status, task.get_poi_goal(), behaviour.get_type(),
                                       task.robot_id])

            df = pd.DataFrame(tasks_data, columns=["task_id", "status",  "goal_id", "zachowanie", "id_robota"])
            df.style.set_table_styles([dict(selector='th', props=[('text-align', 'center')])])
            df.sort_values(by=['status', 'goal_id', "task_id"], inplace=True)
            left_aligned_df = df.style.set_properties(**{'text-align': 'center'})
            display(left_aligned_df)

    def import_config(self, widget):
        if widget["name"] == '_property_lock' and len(widget["new"]) == 0:
            data = self.import_config_widget.value[list(self.import_config_widget.value.keys())[0]]["content"]
            self.robots_creator.import_robots_config(json.loads(data.decode('ascii'))["robots"])
            self.task_pattern_creator.import_tasks_pattern_config(json.loads(data.decode('ascii'))["tasks_pattern"])
            self.task_panel.import_tasks_config(json.loads(data.decode('ascii'))["tasks"])

    def export_config(self, widget):
        file_path = 'config/' + self.config_file_name_widget.value + '.json'
        data = {}
        data["robots"] = self.robots_creator.export_robots_config()
        data["tasks_pattern"] = self.task_pattern_creator.export_tasks_pattern_config()
        data["tasks"] = self.task_panel.export_tasks_config()
        update_info("Zapisano konfiguracje: " + self.config_file_name_widget.value)
        with open(file_path, 'w') as f:
            json.dump(data, f)

