# -*- coding: utf-8 -*-
import networkx as nx
import numpy as np
import copy
import itertools
import math
import matplotlib.pyplot as plt  # do wizualizaccji i rysowania grafu
import json
from shapely.geometry import LineString
from shapely.ops import unary_union
from dispatcher import *

ROBOT_LENGTH = 0.7
ROBOT_CORRIDOR_WIDTH = 0.9  # 0.9 szerokosc korytarza ruchu dla pojedynczego robota
MAIN_CORRIDOR_WIDTH = 0.001  # odleglosc pomiedzy glownymi drogami w korytarzu dla krawedzi dwukierunkowych szerokich
# wartosc powinna byc wieksza od 0
WAITING_STOP_DIST_TO_INTERSECTION = ROBOT_LENGTH/2 + MAIN_CORRIDOR_WIDTH  # odleglosc od srodka skrzyzowania do miejsca
# w ktorym zatrzymuje sie srodek robota. Ustawiona wartosc powinna powodowac zatrzymanie robota przed wjazdem na
# skrzyzowanie
DOCKING_TIME_WEIGHT = 20
UNDOCKING_TIME_WEIGHT = 20
WAIT_WEIGHT = 10
OFFLINE_TEST = False

way_type = {
    "twoWay": 1,
    "narrowTwoWay": 2,
    "oneWay": 3
}
base_node_section_type = {
    "dockWaitUndock": 1,  # rozbicie na dock, wait, undock, end
    "waitPOI": 2,  # rozbicie na wait, end
    "noChanges": 3,  # brak zmian, przepisać
    "normal": 4,  # pomijane przy rozbijaniu węzłów, ale uwzględniane przy kształcie korytarza
    "intersection": 5   # rozbicie na in, out; liczba zależy od krawędzi związanych z węzłem; konieczność wygenerowania
    # prawidłowych współrzędnych przesunięcia
}
base_node_type = {
    # Typy POI
    "charger": {"id": 1, "nodeSection": base_node_section_type["dockWaitUndock"]},  # charger
    "load": {"id": 2, "nodeSection": base_node_section_type["waitPOI"]},  # loading
    "unload": {"id": 3, "nodeSection": base_node_section_type["waitPOI"]},  # unloading
    "load-unload": {"id": 4, "nodeSection": base_node_section_type["waitPOI"]},  # loading-unloading
    "load-dock": {"id": 5, "nodeSection": base_node_section_type["dockWaitUndock"]},  # loading-docking
    "unload-dock": {"id": 6, "nodeSection": base_node_section_type["dockWaitUndock"]},  # unloading-docking
    "load-unload-dock": {"id": 7, "nodeSection": base_node_section_type["dockWaitUndock"]}, # loading-unloading-docking
    "waiting": {"id": 8, "nodeSection": base_node_section_type["noChanges"]},  # waiting
    "departure": {"id": 9, "nodeSection": base_node_section_type["noChanges"]},  # departue
    "waiting-departure": {"id": 10, "nodeSection": base_node_section_type["intersection"]},  # waiting-departure
    "parking": {"id": 11, "nodeSection": base_node_section_type["noChanges"]},  # parking
    "queue": {"id": 12, "nodeSection": base_node_section_type["noChanges"]},  # queue
    "normal": {"id": 13, "nodeSection": base_node_section_type["normal"]},  # normal
    "intersection": {"id": 14, "nodeSection": base_node_section_type["intersection"]},  # intersection
}
new_node_type = {
    # type - służy do przyszłego złączenia krawędzi grafu w odpowiedniej kolejności
    # znaczenie typow wezlow
    "dock": 1,  # rozpoczecie dokowania
    "wait": 2,  # rozpoczecie wlaciwej operacji na stanowisku
    "undock": 3,  # rozpoczecie procedury oddokowania
    "end": 4,  # zakonczenie zadania, mozliwosc przekierowania robota do innego zadania (wolny) lub kolejnego zachowania
    "noChanges": 5,  # wezel nie ulega zmianom wzgledem tego od ktorego jest tworzony
    "intersection_in": 6,  # wjazd na skrzyzowanie
    "intersection_out": 7  # zjazd ze skrzyzowania
}
node_color = {  # do celow wizualizacji i podgladu
    "dockWaitUndock": "yellow",  # L
    "dock": "#00fc00",  # jasna zielen
    "wait": "red",
    "undock": "#00a800",  # ciemna zielen
    "end": "#8c0000",  # ciemny czerwony
    "noChanges": "orange",  # S
    "intersection_base": "blue",  # D
    "in": "black",  # P
    "out": "magenta",  # WP
    "skipped": "#72fdfe"  # blękit - wezly ktore powinny byc pominiete, ale chyba beda rysowane
}


class GraphError(Exception):
    """Base class for exceptions in this module."""
    pass


def create_edges(source_edges):
    """
    Zduplikowanie krawędzi dla dróg dwukierunkowych. Zduplikowane krawedzie maja zamieniony wezel startowy z koncowym.
    Parameters:
        source_edges ({"edge_id": {"startNode": string, "endNode": string, "type": way_type[""], "isActive": boolen},
            ...}): slownik z krawedziami bazowymi grafu
    Returns:
        {"edge_id": {"startNode": string, "endNode": string, "type": way_type[""], "isActive": boolen}, ...} - slownik
            ze zduplikowanymi krawedziami
    """
    i = 1
    extended_edges = {}
    for k in sorted(source_edges):
        edge = source_edges[k]
        if edge["type"] == way_type["twoWay"] or \
                edge["type"] == way_type["narrowTwoWay"]:

            a = edge["startNode"]
            b = edge["endNode"]
            extended_edges[i] = edge.copy()
            extended_edges[i]["startNode"] = a
            extended_edges[i]["endNode"] = b
            extended_edges[i]["edgeSource"] = k
            i = i + 1
            extended_edges[i] = edge.copy()
            extended_edges[i]["startNode"] = b
            extended_edges[i]["endNode"] = a
            extended_edges[i]["edgeSource"] = k
            i = i + 1
            pass
        else:
            extended_edges[i] = edge.copy()
            extended_edges[i]["edgeSource"] = k
            i = i + 1
    return extended_edges


class DataValidator:
    """
    Klasa odpowiada za weryfikacje danych wejsciowych grafu.
    Attributes
        source_nodes ({"node_id": {"name": string, "pos": (float,float) "type": base_node_type[""], "poiId": string}},
            ...}) - slownik z krawedziami grafu
        sorted_source_nodes_list (list) - lista posortowanych wierzcholkow grafu
        source_edges ({"edge_id": {"startNode": string, "endNode": string, "type": way_type[""], "isActive": boolen},
            ...}) - slownik z krawedziami grafu
        reduced_edges ({"edgeId": {"sourceEdges": list, "sourceNodes": list, "wayType": way_type[""],
                                   "edgeGroupId": int}, ...}) - slownik ze zredukowna liczba krawedzi wraz z ich typem
    """
    def __init__(self, source_nodes, source_edges):
        """
        Parameters:
            source_nodes ({"node_id": {"name": string, "pos": (float,float) "type": base_node_type[""],
                                       "poiId": string}}, ...}) - slownik z krawedziami grafu
            source_edges ({"edge_id": {"startNode": string, "endNode": string, "type": way_type[""],
                                       "isActive": boolen}, ...}) - slownik z krawedziami grafu
        """
        self.source_nodes = source_nodes
        self.sorted_source_nodes_list = sorted(source_nodes)
        self.source_edges = source_edges
        edges = create_edges(copy.deepcopy(source_edges))
        self.reduced_edges = self.combined_normal_nodes(edges)
        self.validate_data()

    def validate_data(self):
        """
        Walidacja danych wejsciowych grafu podstawowego.
        """
        self.validate_poi_connection_nodes()
        self.validate_parking_connection_nodes()
        self.validate_queue_connection_nodes()
        self.validate_waiting_connection_nodes()
        self.validate_departure_connection_nodes()
        self.validate_wait_dep_connection_nodes()

    def combined_normal_nodes(self, edges):
        """
        Funkcja redukuje liczbe krawedzi wejsciowych. Zwraca nowe krawedzie grafu po zredukowaniu krawedzi z wezlami
        normlanymi.
        Parameters:
            edges ({"edge_id": {"startNode": string, "endNode": string, "type": way_type[""],
                                "isActive": boolen}, ...}) - slownik z krawedziami grafu bazowego
        Returns:
            ({"edgeId": {"sourceEdges": list, "sourceNodes": list, "wayType": way_type[""], "edgeGroupId": int}, ...})
                - slownik ze zredukowna liczba krawedzi wraz z ich typem
        """
        normal_nodes_id = {i for i in self.sorted_source_nodes_list
                           if self.source_nodes[i]["type"] == base_node_type["normal"]}
        combined_path = {edgeId: {"edgeSourceId": [edges[edgeId]["edgeSource"]],
                                  "connectedNodes": [edges[edgeId]["startNode"], edges[edgeId]["endNode"]]}
                         for edgeId in edges if edges[edgeId]["startNode"] not in normal_nodes_id
                         and edges[edgeId]["endNode"] in normal_nodes_id}
        edges_normal_nodes = [i for i in sorted(edges) if edges[i]["startNode"] in normal_nodes_id]
        previos_edge_len = len(edges_normal_nodes)
        while True:
            for i in edges_normal_nodes:
                edge = edges[i]
                for j in sorted(combined_path):
                    node = combined_path[j]
                    if node["connectedNodes"][-1] == edge["startNode"] and \
                            edge["edgeSource"] not in node["edgeSourceId"]:
                        combined_path[j]["connectedNodes"].append(edge["endNode"])
                        combined_path[j]["edgeSourceId"].append(edge["edgeSource"])
                        edges_normal_nodes.remove(i)
                        break

            if previos_edge_len == len(edges_normal_nodes):
                if len(edges_normal_nodes) != 0:
                    raise GraphError("Normal nodes error. Path contains normal nodes should start and end "
                                     "from different type of node.")
                break
            else:
                previos_edge_len = len(edges_normal_nodes)
        self._validate_direction_combined_path(combined_path)
        return self._combined_normal_nodes_edges(edges, combined_path)

    def _validate_direction_combined_path(self, connected_normal_nodes_paths):
        """
        Sprawdza czy kazdy z odcinkow zlozonej krawedzi jest tego samego typu oraz czy poczatkowy i koncowy wezel
        jest innego typu niz normal. W przeciwnym wypadku pojawia sie wyjatek GraphError.
        Parameters:
            connected_normal_nodes_paths ({"edgeId": {"edgeSourceId": [], "connectedNodes": []}, ... }):
                slownik z krawedziami ze zlaczonymi wezlami normalnymi; edgeId - id krawedzi wejsciowej
        """
        combined_path = copy.deepcopy(connected_normal_nodes_paths)
        for i in sorted(combined_path):
            edges_id = combined_path[i]["edgeSourceId"]
            previous_path_type = self.source_edges[edges_id[0]]["type"]
            for j in range(len(edges_id) - 1):
                current_path_type = self.source_edges[edges_id[j + 1]]["type"]
                if previous_path_type != current_path_type:
                    raise GraphError("Different path type connected to normal nodes.")
            end_node_id = combined_path[i]["connectedNodes"][-1]
            end_node_type = self.source_nodes[end_node_id]["type"]
            if end_node_type == base_node_type["normal"]:
                raise GraphError("Path contains normal nodes should be end different type of nodes.")

    def _combined_normal_nodes_edges(self, edges, combined_path):
        """
        Tworzy slownik ze zredukowanymi krawedziami z uzupelnionymi wlasciwosciami krawedzi.
        Parameters:
            edges ({"edge_id": {"startNode": string, "endNode": string, "type": way_type[""],
                                "isActive": boolen}, ...}) - slownik z krawedziami grafu bazowego
            combined_path ({"edgeId": {"edgeSourceId": [], "connectedNodes": []}, ... }): slownik z krawedziami ze
                zlaczonymi wezlami normalnymi; edgeId - id krawedzi wejsciowej
        Returns:
            ({"edgeId": {"sourceEdges": list, "sourceNodes": list, "wayType": way_type[""], "edgeGroupId": int}, ...})
                - slownik ze zredukowna liczba krawedzi wraz z ich typem
        """
        reduced_edges = {}
        j = 1
        for i in sorted(edges):
            edge = edges[i]
            if self.source_nodes[edge["startNode"]]["type"] != base_node_type["normal"] \
                    and self.source_nodes[edge["endNode"]]["type"] != base_node_type["normal"]:
                if j not in reduced_edges:
                    reduced_edges[j] = {"sourceEdges": [], "sourceNodes": [], "wayType": 0, "edgeGroupId": 0}
                reduced_edges[j]["sourceEdges"] = [edge["edgeSource"]]
                reduced_edges[j]["sourceNodes"] = [edge["startNode"], edge["endNode"]]
                reduced_edges[j]["wayType"] = edge["type"]
                j = j + 1
            elif self.source_nodes[edge["startNode"]]["type"] != base_node_type["normal"] \
                    and self.source_nodes[edge["endNode"]]["type"] == base_node_type["normal"]:
                last_node_id = [pathId for pathId in combined_path
                                if combined_path[pathId]["connectedNodes"][0] == edge["startNode"]
                                and combined_path[pathId]["connectedNodes"][1] == edge["endNode"]]
                if j not in reduced_edges:
                    reduced_edges[j] = {"sourceEdges": [], "sourceNodes": [], "wayType": 0, "edgeGroupId": 0}
                reduced_edges[j]["sourceEdges"] = combined_path[last_node_id[0]]["edgeSourceId"]
                reduced_edges[j]["sourceNodes"] = combined_path[last_node_id[0]]["connectedNodes"]
                reduced_edges[j]["wayType"] = edge["type"]
                del combined_path[last_node_id[0]]
                j = j + 1
        return reduced_edges

    def validate_poi_connection_nodes(self):
        """
        Analizuje POI z dokowaniem i bez dokowania. Sprawdza czy kazde POI laczy sie z dwoma innymi wezlami.
        - konfiguracja 1 wezly: waiting, POI, departure
        - sprawdzenie czy krawedzi w konfiguracji 1 zgodnie z podana kolejnoscia sa jednokierunkowe
        - konfiguracja 2 wezly: waiting-departure, poi, waiting-departure
        - sprawdzenie czy POI laczy sie z wezlem waiting-departure krawedzia waska jednokierunkowa
        - dla pozostalych konfiguracji krawedzi -> blad polaczenia
        - konfiguracja 3 wezly: intersection 1 -> poi -> intersection 1
        """
        poi_nodes_id = [i for i in self.sorted_source_nodes_list
                        if self.source_nodes[i]["type"]["nodeSection"] == base_node_section_type["dockWaitUndock"]
                        or self.source_nodes[i]["type"]["nodeSection"] == base_node_section_type["waitPOI"]]
        for i in poi_nodes_id:
            in_nodes = [self.reduced_edges[j]["sourceNodes"][0] for j in sorted(self.reduced_edges)
                        if self.reduced_edges[j]["sourceNodes"][-1] == i]
            out_nodes = [self.reduced_edges[j]["sourceNodes"][-1] for j in sorted(self.reduced_edges)
                         if self.reduced_edges[j]["sourceNodes"][0] == i]

            if len(in_nodes) < 1:
                raise GraphError("Missing before POI's node.")
            if len(out_nodes) < 1:
                raise GraphError("Missing after POI's node.")

            in_node_type = self.source_nodes[in_nodes[0]]["type"]
            out_node_type = self.source_nodes[out_nodes[0]]["type"]

            if len(in_nodes) != 1:
                raise GraphError("Only one waiting/waiting-departure/intersection node is allowed as before "
                                 "POI's node.")
            if len(out_nodes) != 1:
                raise GraphError("Only one departure/waiting-departure/intersection node is allowed as after "
                                 "POI's node.")

            in_node_type = self.source_nodes[in_nodes[0]]["type"]
            out_node_type = self.source_nodes[out_nodes[0]]["type"]
            if not ((in_node_type == base_node_type["waiting"] and out_node_type == base_node_type["departure"])
                    or (in_node_type == base_node_type["waiting-departure"] and
                    out_node_type == base_node_type["waiting-departure"])
                    or (in_node_type == base_node_type["intersection"] and in_node_type == out_node_type)):
                raise GraphError("Connected POI with given nodes not allowed. Available connection: "
                                 "waiting->POI->departure or waiting-departure->POI-> waiting-departure "
                                 "or intersection1->POI->intersection1")

            in_edge_type = [self.reduced_edges[j]["wayType"] for j in sorted(self.reduced_edges)
                            if self.reduced_edges[j]["sourceNodes"][0] == in_nodes[0]
                            and self.reduced_edges[j]["sourceNodes"][-1] == i]

            out_edge_type = [self.reduced_edges[j]["wayType"] for j in sorted(self.reduced_edges)
                             if self.reduced_edges[j]["sourceNodes"][0] == i
                             and self.reduced_edges[j]["sourceNodes"][-1] == out_nodes[0]]
            if in_node_type == base_node_type["waiting"]:
                if not (in_edge_type[0] == way_type["oneWay"] and out_edge_type[0] == way_type["oneWay"]):
                    raise GraphError("Edges should be one way in connection waiting->POI->departure")
            elif in_node_type == base_node_type["waiting-departure"]:
                if not (in_edge_type[0] == way_type["narrowTwoWay"] and out_edge_type[0] == way_type["narrowTwoWay"]):
                    raise GraphError("Edges should be narrow two way in connection "
                                     "waiting-departure->POI->waiting-departure")
            elif in_node_type == base_node_type["intersection"]:
                if not (in_edge_type[0] == way_type["narrowTwoWay"] and out_edge_type[0] == way_type["narrowTwoWay"]):
                    raise GraphError("Edges should be narrow two way in connection intersection->POI->intersection")


    def validate_parking_connection_nodes(self):
        """
        Analiza polaczen z wezlami typu Parking. Dla wszystich parkingow nastepuje sprawdzenie czy lacza sie
        bezposrednio ze skrzyzowaniem oraz czy krawedz laczaca jest typu waskiego dwukierunkowego.
        """
        parking_nodes_id = [i for i in self.sorted_source_nodes_list
                            if self.source_nodes[i]["type"] == base_node_type["parking"]]
        for i in parking_nodes_id:
            in_nodes = [self.reduced_edges[j]["sourceNodes"][0] for j in sorted(self.reduced_edges)
                        if self.reduced_edges[j]["sourceNodes"][-1] == i]
            out_nodes = [self.reduced_edges[j]["sourceNodes"][-1] for j in sorted(self.reduced_edges)
                         if self.reduced_edges[j]["sourceNodes"][0] == i]
            if len(in_nodes) != 1:
                raise GraphError("Only one intersection node should be connected as input with parking.")
            if len(out_nodes) != 1:
                raise GraphError("Only one intersection node should be connected as output with parking.")

            in_node_type = self.source_nodes[in_nodes[0]]["type"]
            out_node_type = self.source_nodes[out_nodes[0]]["type"]
            if not (in_node_type == base_node_type["intersection"] and out_node_type == base_node_type["intersection"]):
                raise GraphError("Connected Parking with given nodes not allowed. Available connection: "
                                 "intersection->POI->intersection.")

            in_edge_type = [self.reduced_edges[j]["wayType"] for j in sorted(self.reduced_edges)
                            if self.reduced_edges[j]["sourceNodes"][0] == in_nodes[0]
                            and self.reduced_edges[j]["sourceNodes"][-1] == i]

            out_edge_type = [self.reduced_edges[j]["wayType"] for j in sorted(self.reduced_edges)
                             if self.reduced_edges[j]["sourceNodes"][0] == i
                             and self.reduced_edges[j]["sourceNodes"][-1] == out_nodes[0]]
            if not (in_edge_type[0] == way_type["narrowTwoWay"] and out_edge_type[0] == way_type["narrowTwoWay"]):
                raise GraphError("Edges should be narrow two way in connection intersection->parking->intersection.")

    def validate_queue_connection_nodes(self):
        """
        Analiza polaczen z wezlami typu Queue. Dla wszystich miejsc kolejkowania robotow nastepuje sprawdzenie czy
        wezel poprzedzajacy i nastepujacy jest skrzyzowaniem oraz wystepuje polaczenie jednokierunkowe z Queue.
        intersection1->queue, queue->intersection2
        """
        queue_nodes_id = [i for i in self.sorted_source_nodes_list
                          if self.source_nodes[i]["type"] == base_node_type["queue"]]
        for i in queue_nodes_id:
            in_nodes = [self.reduced_edges[j]["sourceNodes"][0] for j in sorted(self.reduced_edges)
                        if self.reduced_edges[j]["sourceNodes"][-1] == i]
            out_nodes = [self.reduced_edges[j]["sourceNodes"][-1] for j in sorted(self.reduced_edges)
                         if self.reduced_edges[j]["sourceNodes"][0] == i]
            if len(in_nodes) != 1:
                raise GraphError("Only one intersection node should be connected as input with queue.")
            if len(out_nodes) != 1:
                raise GraphError("Only one intersection node should be connected as output with queue.")

            in_node_type = self.source_nodes[in_nodes[0]]["type"]
            out_node_type = self.source_nodes[out_nodes[0]]["type"]
            if not (in_node_type == base_node_type["intersection"] and out_node_type == base_node_type["intersection"]):
                raise GraphError("Connected Queue with given nodes not allowed. Available connection: "
                                 "intersection->queue->intersection.")

            in_edge_type = [self.reduced_edges[j]["wayType"] for j in sorted(self.reduced_edges)
                            if self.reduced_edges[j]["sourceNodes"][0] == in_nodes[0]
                            and self.reduced_edges[j]["sourceNodes"][-1] == i]

            out_edge_type = [self.reduced_edges[j]["wayType"] for j in sorted(self.reduced_edges)
                             if self.reduced_edges[j]["sourceNodes"][0] == i
                             and self.reduced_edges[j]["sourceNodes"][-1] == out_nodes[0]]
            if not (in_edge_type[0] == way_type["oneWay"] and out_edge_type[0] == way_type["oneWay"]):
                raise GraphError("Edges should be one way in connection intersection->queue->intersection.")

    def validate_waiting_connection_nodes(self):
        """
        Pobiera wszystkie wezly typu waiting. Sa to wezly przed ktorymi kolejkuja sie roboty w oczekiwaniu na dojazd do
        stanowiska. Nastepuje sprawdzenie czy wezel poprzedzajacy jest skrzyzowaniem, a nastepny stanowiskiem.
        Polaczenie miedzy odpowiednimi wezlami powinny byc jednokierunkowe intersection->waiting->POI
        """
        queue_nodes_id = [i for i in self.sorted_source_nodes_list
                          if self.source_nodes[i]["type"] == base_node_type["waiting"]]
        for i in queue_nodes_id:
            in_nodes = [self.reduced_edges[j]["sourceNodes"][0] for j in sorted(self.reduced_edges)
                        if self.reduced_edges[j]["sourceNodes"][-1] == i]
            out_nodes = [self.reduced_edges[j]["sourceNodes"][-1] for j in sorted(self.reduced_edges)
                         if self.reduced_edges[j]["sourceNodes"][0] == i]
            if len(in_nodes) != 1:
                raise GraphError("Only one intersection node should be connected as input with waiting node.")
            if len(out_nodes) != 1:
                raise GraphError("Only one POI node should be connected as output with waiting node.")

            in_node_type = self.source_nodes[in_nodes[0]]["type"]
            out_node_type = self.source_nodes[out_nodes[0]]["type"]["nodeSection"]
            if not (in_node_type == base_node_type["intersection"] and
                    (out_node_type == base_node_section_type["dockWaitUndock"] or
                     out_node_type == base_node_section_type["waitPOI"])):
                raise GraphError("Connected waiting node with given nodes not allowed.Available connection: "
                                 "intersection->waiting->POI.")

            in_edge_type = [self.reduced_edges[j]["wayType"] for j in sorted(self.reduced_edges)
                            if self.reduced_edges[j]["sourceNodes"][0] == in_nodes[0]
                            and self.reduced_edges[j]["sourceNodes"][-1] == i]

            out_edge_type = [self.reduced_edges[j]["wayType"] for j in sorted(self.reduced_edges)
                             if self.reduced_edges[j]["sourceNodes"][0] == i
                             and self.reduced_edges[j]["sourceNodes"][-1] == out_nodes[0]]
            if not (in_edge_type[0] == way_type["oneWay"] and out_edge_type[0] == way_type["oneWay"]):
                raise GraphError("Edges should be one way in connection intersection->waiting->POI.")

    def validate_departure_connection_nodes(self):
        """
        Pobiera wszystkie wezly typu departure. Sa to wezly odjazdu od stanowiska. Po przejechaniu robota za wezel
        departure moze nastapic wyslanie kolejnego robota do stanowiska. Nastepuje sprawdzenie czy wezel poprzedzajacy
        jest stanowiskiem, a nastepny skrzyzowaniem. Polaczenie miedzy odpowiednimi wezlami powinny byc jednokierunkowe
        POI->departure->intersection
        """
        queue_nodes_id = [i for i in self.sorted_source_nodes_list
                          if self.source_nodes[i]["type"] == base_node_type["departure"]]
        for i in queue_nodes_id:
            in_nodes = [self.reduced_edges[j]["sourceNodes"][0] for j in sorted(self.reduced_edges)
                        if self.reduced_edges[j]["sourceNodes"][-1] == i]
            out_nodes = [self.reduced_edges[j]["sourceNodes"][-1] for j in sorted(self.reduced_edges)
                         if self.reduced_edges[j]["sourceNodes"][0] == i]
            if len(in_nodes) != 1:
                raise GraphError("Only one POI node should be connected as input with departure node.")
            if len(out_nodes) != 1:
                raise GraphError("Only one departure node should be connected as output with intersection node.")

            in_node_type = self.source_nodes[in_nodes[0]]["type"]["nodeSection"]
            out_node_type = self.source_nodes[out_nodes[0]]["type"]
            if not (out_node_type == base_node_type["intersection"] and
                    (in_node_type == base_node_section_type["dockWaitUndock"] or
                     in_node_type == base_node_section_type["waitPOI"])):
                raise GraphError("Connected departure node with given nodes not allowed. Available connection: "
                                 "POI->departure->intersection.")

            in_edge_type = [self.reduced_edges[j]["wayType"] for j in sorted(self.reduced_edges)
                            if self.reduced_edges[j]["sourceNodes"][0] == in_nodes[0]
                            and self.reduced_edges[j]["sourceNodes"][-1] == i]

            out_edge_type = [self.reduced_edges[j]["wayType"] for j in sorted(self.reduced_edges)
                             if self.reduced_edges[j]["sourceNodes"][0] == i
                             and self.reduced_edges[j]["sourceNodes"][-1] == out_nodes[0]]
            if not (in_edge_type[0] == way_type["oneWay"] and out_edge_type[0] == way_type["oneWay"]):
                raise GraphError("Edges should be one way in connection intersection->queue->intersection.")

    def validate_wait_dep_connection_nodes(self):
        """
        Pobiera wszystkie wezly typu waiting-departure (dojazd-odjazd od stanowiska). Sprawdza czy krawedzie polaczen
        sa nastepujacego typu:
        - twoWay - polaczenie intersection <-> waiting-departure
        - narrowTwoWay - polaczenie waiting-departure <-> POI
        """
        queue_nodes_id = [i for i in self.sorted_source_nodes_list
                          if self.source_nodes[i]["type"] == base_node_type["waiting-departure"]]
        for i in queue_nodes_id:
            in_nodes = [self.reduced_edges[j]["sourceNodes"][0] for j in sorted(self.reduced_edges)
                        if self.reduced_edges[j]["sourceNodes"][-1] == i]
            out_nodes = [self.reduced_edges[j]["sourceNodes"][-1] for j in sorted(self.reduced_edges)
                         if self.reduced_edges[j]["sourceNodes"][0] == i]
            if not (len(in_nodes) == 2 and len(out_nodes) == 2):
                raise GraphError("Too much nodes connected with witing-departure node.")

            in_node_type = [self.source_nodes[in_nodes[0]]["type"], self.source_nodes[in_nodes[1]]["type"]]
            out_node_type = [self.source_nodes[out_nodes[0]]["type"], self.source_nodes[out_nodes[1]]["type"]]
            in_node_type_section = [self.source_nodes[in_nodes[0]]["type"]["nodeSection"],
                                    self.source_nodes[in_nodes[1]]["type"]["nodeSection"]]
            out_node_type_section = [self.source_nodes[out_nodes[0]]["type"]["nodeSection"],
                                     self.source_nodes[out_nodes[1]]["type"]["nodeSection"]]

            if not ((base_node_type["intersection"] in in_node_type)
                    and (base_node_section_type["dockWaitUndock"] in in_node_type_section or base_node_section_type[
                        "waitPOI"] in in_node_type_section) and (base_node_type["intersection"] in out_node_type)
                    and (base_node_section_type["dockWaitUndock"] in out_node_type_section or base_node_section_type[
                        "waitPOI"] in out_node_type_section)):
                raise GraphError("Connected waiting-departure node with given nodes not allowed. Node should be "
                                 "connected with intersection and POI.")

            # powstale krawedzie z polaczen powinny byc odpowiednio dwukierunkowe szerokie oraz waskie dwukierunkowe
            inter_wait_dep_path_nodes = []
            poi_wait_dep_path_nodes = []
            if in_node_type[0] == base_node_type["intersection"]:
                # pierwszy wezel jest skrzyzowaniem
                inter_wait_dep_path_nodes.append([in_nodes[0], i])
                poi_wait_dep_path_nodes.append([in_nodes[1], i])
            else:
                # drugi wezel jest skrzyzowaniem
                inter_wait_dep_path_nodes.append([in_nodes[1], i])
                poi_wait_dep_path_nodes.append([in_nodes[0], i])

            if out_node_type[0] == base_node_type["intersection"]:
                # pierwszy wezel jest skrzyzowaniem
                inter_wait_dep_path_nodes.append([i, out_nodes[0]])
                poi_wait_dep_path_nodes.append([i, out_nodes[1]])
            else:
                # drugi wezel jest skrzyzowaniem
                inter_wait_dep_path_nodes.append([i, out_nodes[1]])
                poi_wait_dep_path_nodes.append([i, out_nodes[0]])

                # sprawdzenie typu krawedzi laczacych sie z waiting departure
            inter_wait_dep_path_type = []
            poi_wait_dep_path_type = []
            for j in sorted(self.reduced_edges):
                edge = self.reduced_edges[j]
                for path in inter_wait_dep_path_nodes:
                    if edge["sourceNodes"][0] == path[0] and edge["sourceNodes"][-1] == path[1]:
                        inter_wait_dep_path_type.append(edge["wayType"])
                for path in poi_wait_dep_path_nodes:
                    if edge["sourceNodes"][0] == path[0] and edge["sourceNodes"][-1] == path[1]:
                        poi_wait_dep_path_type.append(edge["wayType"])

            if not (inter_wait_dep_path_type[0] == way_type["twoWay"]
                    and inter_wait_dep_path_type[1] == way_type["twoWay"]):
                raise GraphError("Edges should be twoWay in connection intersection<->waiting-departure.")

            if not (poi_wait_dep_path_type[0] == way_type["narrowTwoWay"]
                    and poi_wait_dep_path_type[1] == way_type["narrowTwoWay"]):
                raise GraphError("Edges should be twoNarrowWay in connection waiting-departure<->POI")


def get_node_area(start, robot_path_coordinates):
    """
    Zwraca fragment korytarza dookola punktu startowego/koncowego dla podanej sciezki pomiedzy kolejnymi punktami ruchu
    robota.
    Parameters:
        start (boolean): informuje dla ktorej wspolrzednej sciezki ma byc wyznaczony korytarz dookola wezla. Jest True
            to brany jest pod uwage wezel startowy, a dla False wezel celu.
        robot_path_coordinates([(float, float), ...]): lista z kolejnymi wspolrzednymi krawedzi ktorymi powinien
            poruszac sie robot.

    Returns:
        (LineString): wspolrzedne kolejnych wierzcholkow korytarza dla danego poi
    """
    goal = robot_path_coordinates[0] if start else robot_path_coordinates[-1]
    orient_point = robot_path_coordinates[1] if start else robot_path_coordinates[-2]

    x = goal[0] - orient_point[0]
    y = goal[1] - orient_point[1]
    radius = math.sqrt(x * x + y * y)
    theta = math.atan2(y, x)
    new_x = (radius + 0.01) * math.cos(theta)
    new_y = (radius + 0.01) * math.sin(theta)

    # nowy punkt w ukladzie mapy
    new_point = (new_x + orient_point[0], new_y + orient_point[1])
    poi = LineString([[goal[0], goal[1]], [new_point[0], new_point[1]]]).buffer(ROBOT_CORRIDOR_WIDTH, cap_style=3,
                                                                                join_style=2)
    return poi


def _get_intersection_step_node_pos(in_pos, out_pos, is_narrow, is_in_edge):
    """
    Wyznacza wspolrzedna posrednia na skrzyzowaniu.
    Parameters:
        in_pos ((float,float)): wspolrzedne wezla laczacego sie ze skrzyzowaniem
        out_pos ((float,float)): wspolrzedne wezla poprzedzajacego/nastepnego dla krawedzi laczacej sie ze skrzyzowaniem
        is_narrow (boolean): informacja czy podana krawedz jest waska czy nie
        is_in_edge (boolean): informacja czy z danej krawedzi nastepuje wjazd na skrzyzowanie
    Returns:
        ((float,float)): wspolrzedne wezla posredniego przejazdu przez skrzyzowanie
    """
    translate_base_node = np.array([[1, 0, 0, in_pos[0]], [0, 1, 0, in_pos[1]],
                                    [0, 0, 1, 0], [0, 0, 0, 1]])
    angle_start = np.arctan2(out_pos[1] - in_pos[1], out_pos[0] - in_pos[0])
    rotation_start_node = np.array([[math.cos(angle_start), -math.sin(angle_start), 0, 0],
                                    [math.sin(angle_start), math.cos(angle_start), 0, 0],
                                    [0, 0, 1, 0], [0, 0, 0, 1]])

    if is_narrow:
        path_to_intersection = np.array([[1, 0, 0, MAIN_CORRIDOR_WIDTH / 2],
                                        [0, 1, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]])
        way_start = np.dot(np.dot(translate_base_node, rotation_start_node), path_to_intersection)
    else:
        path_to_intersection = np.array([[1, 0, 0, MAIN_CORRIDOR_WIDTH / 2],
                                         [0, 1, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]])
        path_to_intersection[1][3] = MAIN_CORRIDOR_WIDTH / 2 if is_in_edge else -MAIN_CORRIDOR_WIDTH / 2
        way_start = np.dot(np.dot(translate_base_node, rotation_start_node), path_to_intersection)

    return way_start[0][3], way_start[1][3]


class SupervisorGraphCreator(DataValidator):
    """
    Klasa odpowiedzialna za utworzenie rozbudowanego grafu dla supervisora.
    Attributes:
        graph (DiGraph): wlasciwy graf. Id wezlow sa typu (int).
            Atrybuty wszystkich krawedzi:
                "id" (int): identyfikator krawedzi
                "weight" (float): waga zwiazana z czasem przejazdu/wykonania akcji na danej krawedzi
                "behaviour" (Behaviour.TYPES["..."]): typ zachowania zwiazany z krawedzia
                "robots" (list): lista z id robotow znajdujacych sie aktualnie na krawedzi
                "edgeGroupId" (int): identyfikatory grupy krawedzi
                "sourceNodes" (list): lista z wezlami na podstawie, ktorych powstala dana krawedz
                "sourceEdges" (list): lista krawedzi z ktorych zlozona jest dana krawedz

            Niektore dodatkowe atrybuty krawedzi:
                "connectedPoi" (string): tylko dla krawedzi nalezacych/ laczacych sie z POI
                "maxRobots" (int): maksymalna liczba robotow mogaca przebywac na krawedzi z zachowaniem GOTO i nie
                                   nalezaca do POI
                "corridor" (list): lista kolejnych wspolrzednych (x,y) (float,float), korytarza dla krawedzi grafu
                                   rozszerzonego, dotyczy krawedzi z zachowaniem GOTO
            Atrybuty wezlow:
                "nodeType" (new_node_type["..."]): typ wezla
                "sourceNode" (string): id wezla zrodlowego
                "color" (node_color["..."]): kolor wezla dla danego typu
                "poiId" (string): id POI
                "pos" (float, float): wspolrzedne wezla na mapie
                "pose" (ROS pose): pozycja robota w wezle ({"position": {"x": , "y": , "z":},
                                                            "orientation": {"x": , "y": , "z": , "w":}})
        graph_node_id (int): id kolejnego wezla grafu, wartosc inkrementowana z kazdym wprowadzeniem nowego wezla do
            grafu
        edge_group_id (int): id kolejnej grupy krawedzi, z kazda kolejna grupa wartosc jest inkrementowana. Grupa
            zwiazana jest z pojedynczym skrzyzowaniem, POI i wezlami bezposrednio zwiazanymi (waiting, departure,
            waiting-departure) oraz krawedziami przy parkingach
        edge_id (int): id kolejnej krawedzi grafu, wartosc inkrementowana po dodaniu kolejnej krawedzi do grafu
        group_id_switcher ({string: int)}): slownik z przydzielonymi grupami krawedzi w
            zaleznosci od wezla zrodla. Kluczem jest id wezla bazowego, a wartoscia grupa przynaleznosci.
    """
    def __init__(self, source_nodes, source_edges, pois_raw_data):
        """
        Inicjalizacja i utworzenie właściwego grafu dla supervisora.
        Parameters:
            source_nodes ({"node_id": {"name": string, "pos": (float,float) "type": base_node_type[""],
                                       "poiId": string}}, ...}) - slownik z krawedziami grafu
            source_edges ({"edge_id": {"startNode": string, "endNode": string, "type": way_type[""],
                                       "isActive": boolen}, ...}) - slownik z krawedziami grafu
            pois_raw_data: ([{"id": string, "pose": (float,float)), "type": gc.base_node_type["..."]}, ...]) - lista
                POI w systemie
        """
        super().__init__(source_nodes, source_edges)
        self.graph = nx.DiGraph()
        self.graph_node_id = 1
        self.edge_group_id = 1
        self.edge_id = 1
        self.group_id_switcher = {}
        self.create_graph(pois_raw_data)

    def create_graph(self, pois_raw_data):
        """
        Utworzenie grafu dla supervisora.
        Parameters:
             pois_raw_data: ([{"id": string, "pose": (float,float)), "type": gc.base_node_type["..."]}, ...]) - lista
                POI w systemie
        """
        self.set_groups()
        self.add_poi_docking_nodes()
        self.add_poi_no_docking()
        self.add_poi_no_changes()
        self.add_main_path()
        self.add_intersetions_path()
        if OFFLINE_TEST:
            self.add_nodes_position_test_offline()
        else:
             self.add_nodes_position()
        self.connect_poi_to_waiting_node()
        self.set_default_time_weight()
        self.set_max_robots()
        self.set_corridor()
        self.set_robots_position(pois_raw_data)

    def set_groups(self):
        """
        Odpowiada za wygenerowanie numerow grup dla POI i krawedzi dwukierunkowych waskich. Przypisanie krawedzi
        do tych grup.
        """
        poi_node_ids = [i for i in self.sorted_source_nodes_list if self.source_nodes[i]["type"]["nodeSection"]
                        in [base_node_section_type["dockWaitUndock"], base_node_section_type["waitPOI"]]
                        or self.source_nodes[i]["type"] == base_node_type["parking"]]
        for i in poi_node_ids:
            self.group_id_switcher[i] = self.edge_group_id
            self.edge_group_id = self.edge_group_id + 1

        for i in sorted(self.reduced_edges):
            edge = self.reduced_edges[i]
            group_id = 0
            if edge["sourceNodes"][0] in poi_node_ids:
                group_id = self.group_id_switcher[edge["sourceNodes"][0]]
            elif edge["sourceNodes"][-1] in poi_node_ids:
                group_id = self.group_id_switcher[edge["sourceNodes"][-1]]
            self.reduced_edges[i]["edgeGroupId"] = group_id
        # pobranie waskich dwukierunkowych drog ktore nie sa przypisane do grupy
        narrow_ways_id = [i for i in sorted(self.reduced_edges)
                          if self.reduced_edges[i]["wayType"] == way_type["narrowTwoWay"]
                          and self.reduced_edges[i]["edgeGroupId"] == 0 and
                          self.reduced_edges[i]["sourceNodes"][0] not in poi_node_ids and
                          self.reduced_edges[i]["sourceNodes"][-1] not in poi_node_ids]
        if len(narrow_ways_id) > 0:
            while True:
                path_id = next(iter(narrow_ways_id))
                current_path = self.reduced_edges[path_id]["sourceNodes"]
                twin_path = current_path[::-1]
                narrow_ways_id.remove(path_id)
                for i in narrow_ways_id:
                    if twin_path == self.reduced_edges[i]["sourceNodes"]:
                        narrow_ways_id.remove(i)
                        self.reduced_edges[path_id]["edgeGroupId"] = self.edge_group_id
                        self.reduced_edges[i]["edgeGroupId"] = self.edge_group_id
                        self.edge_group_id = self.edge_group_id + 1
                        break
                if len(narrow_ways_id) == 0:
                    break

    def get_all_nodes_by_type_section(self, given_type):
        """
        Zwraca liste wezlow na podstawie danej grupy typu POI.
        Parameters:
            given_type (base_node_section_type["..."]): typ grupy POI

        Returns:
            ([(string, {"name": string, "pos": (float,float) "type": base_node_type[""], "poiId": string}}]): lista
                wezlow, ktore naleza do danej grupy
        """
        nodes = [(i, self.source_nodes[i]) for i in self.sorted_source_nodes_list if
                 self.source_nodes[i]["type"]["nodeSection"] == given_type]
        return nodes

    def add_poi_docking_nodes(self):
        """
        Dodaje wezly i krawedzie do grafu dla POI z dokowaniem.
        """
        dock_nodes = self.get_all_nodes_by_type_section(base_node_section_type["dockWaitUndock"])
        for dock_node in dock_nodes:
            node_id = dock_node[0]
            return_end_node = self.graph_node_id
            self.graph.add_node(self.graph_node_id, nodeType=new_node_type["dock"], sourceNode=node_id,
                                color=node_color["dock"], poiId=dock_node[1]["poiId"])
            self.graph.add_edge(self.graph_node_id, self.graph_node_id + 1, id=self.edge_id, weight=0,
                                behaviour=Behaviour.TYPES["dock"], robots=[],
                                edgeGroupId=self.group_id_switcher[node_id], sourceNodes=[node_id], sourceEdges=[0])
            self.graph_node_id = self.graph_node_id + 1
            self.edge_id = self.edge_id + 1
            self.graph.add_node(self.graph_node_id, nodeType=new_node_type["wait"], sourceNode=node_id,
                                color=node_color["wait"], poiId=dock_node[1]["poiId"])
            self.graph.add_edge(self.graph_node_id, self.graph_node_id + 1, id=self.edge_id, weight=0,
                                behaviour=Behaviour.TYPES["wait"], robots=[],
                                edgeGroupId=self.group_id_switcher[node_id], sourceNodes=[node_id], sourceEdges=[0])
            self.graph_node_id = self.graph_node_id + 1
            self.edge_id = self.edge_id + 1
            self.graph.add_node(self.graph_node_id, nodeType=new_node_type["undock"], sourceNode=node_id,
                                color=node_color["undock"], poiId=dock_node[1]["poiId"])
            self.graph.add_edge(self.graph_node_id, self.graph_node_id + 1, id=self.edge_id, weight=0,
                                behaviour=Behaviour.TYPES["undock"], robots=[],
                                edgeGroupId=self.group_id_switcher[node_id], sourceNodes=[node_id], sourceEdges=[0])
            self.graph_node_id = self.graph_node_id + 1
            self.edge_id = self.edge_id + 1
            self.graph.add_node(self.graph_node_id, nodeType=new_node_type["end"], sourceNode=node_id,
                                color=node_color["end"], poiId=dock_node[1]["poiId"])
            return_start_node = self.graph_node_id
            self.graph_node_id = self.graph_node_id + 1
            # krawedz powrotna do poczatku stanowiska - dla przydzielenia kolejnego dojazdu do tego samego punktu
            self.graph.add_edge(return_start_node, return_end_node, id=self.edge_id, weight=0,
                                behaviour=Behaviour.TYPES["goto"], robots=[],
                                edgeGroupId=self.group_id_switcher[node_id], sourceNodes=[node_id], sourceEdges=[0])
            self.edge_id = self.edge_id + 1

    def add_poi_no_docking(self):
        """
        Dodaje wezly i krawedzie do grafu dla POI bez dokowania.
        """
        no_dock_nodes = self.get_all_nodes_by_type_section(base_node_section_type["waitPOI"])
        for no_dock_node in no_dock_nodes:
            node_id = no_dock_node[0]
            return_end_node = self.graph_node_id
            self.graph.add_node(self.graph_node_id, nodeType=new_node_type["wait"], sourceNode=node_id,
                                color=node_color["wait"], poiId=no_dock_node[1]["poiId"])
            self.graph.add_edge(self.graph_node_id, self.graph_node_id + 1, id=self.edge_id, weight=0,
                                behaviour=Behaviour.TYPES["wait"], robots=[],
                                edgeGroupId=self.group_id_switcher[node_id], sourceNodes=[node_id], sourceEdges=[0])
            self.graph_node_id = self.graph_node_id + 1

            self.graph.add_node(self.graph_node_id, nodeType=new_node_type["end"], sourceNode=node_id,
                                color=node_color["end"], poiId=no_dock_node[1]["poiId"])
            return_start_node = self.graph_node_id
            self.graph_node_id = self.graph_node_id + 1
            # krawedz powrotna do poczatku stanowiska - dla przydzielenia kolejnego dojazdu do tego samego punktu
            self.graph.add_edge(return_start_node, return_end_node, id=self.edge_id, weight=0,
                                behaviour=Behaviour.TYPES["goto"], robots=[],
                                edgeGroupId=self.group_id_switcher[node_id], sourceNodes=[node_id], sourceEdges=[0])
            self.edge_id = self.edge_id + 1

    def add_poi_no_changes(self):
        """
        Dodaje wezly i krawedzie do grafu dla wezlow, ktore nie ulegaja zmianom.
        """
        nodes = self.get_all_nodes_by_type_section(base_node_section_type["noChanges"])
        for node in nodes:
            node_id = node[0]
            self.graph.add_node(self.graph_node_id, nodeType=new_node_type["noChanges"], sourceNode=node_id,
                                color=node_color["noChanges"], poiId=node[1]["poiId"])
            self.graph_node_id = self.graph_node_id + 1

    ###############################################################################################################
    def add_main_path(self):
        """
        Dodanie wezlow i krawedzi dla glownych drog z pominieciem krawedzi dla skrzyzowan.
        """
        for i in sorted(self.reduced_edges):
            # a,b skrajne wezly grafu zrodlowego utworzonej krawedzi
            source_node_id = self.reduced_edges[i]["sourceNodes"]
            # print(i, combinedEdges[i])
            a_node = self.source_nodes[source_node_id[0]]
            a_node_type = a_node["type"]["nodeSection"]
            b_node = self.source_nodes[source_node_id[-1]]
            b_node_type = b_node["type"]["nodeSection"]
            if a_node_type == base_node_section_type["intersection"]\
                    and b_node_type == base_node_section_type["intersection"]:
                # oba wezly sa skrzyowaniami, mozna od razu utworzyc docelowa krawedz grafu laczaca je
                self.graph.add_node(self.graph_node_id, nodeType=new_node_type["intersection_out"],
                                    sourceNode=source_node_id[0], color=node_color["out"], poiId="0")
                self.graph_node_id = self.graph_node_id + 1
                self.graph.add_node(self.graph_node_id, nodeType=new_node_type["intersection_in"],
                                    sourceNode=source_node_id[-1], color=node_color["in"], poiId="0")
                self.graph.add_edge(self.graph_node_id - 1, self.graph_node_id, id=self.edge_id, weight=0,
                                    behaviour=Behaviour.TYPES["goto"], edgeGroupId=self.reduced_edges[i]["edgeGroupId"],
                                    wayType=self.reduced_edges[i]["wayType"], sourceNodes=source_node_id,
                                    sourceEdges=self.reduced_edges[i]["sourceEdges"], robots=[])
                self.graph_node_id = self.graph_node_id + 1
                self.edge_id = self.edge_id + 1
            elif b_node_type == base_node_section_type["intersection"] and \
                    a_node_type != base_node_section_type["intersection"]:
                # wezel koncowy krawedzi jest typu intersection, a drugi wezel jest innego typu, moze byc to POI
                self.graph.add_node(self.graph_node_id, nodeType=new_node_type["intersection_in"],
                                    sourceNode=source_node_id[-1], color=node_color["in"], poiId="0")
                self.graph_node_id = self.graph_node_id + 1
                g_node_id = self.get_connected_graph_node_id(source_node_id[0])
                self.graph.add_edge(g_node_id, self.graph_node_id - 1, id=self.edge_id, weight=0,
                                    behaviour=Behaviour.TYPES["goto"],
                                    edgeGroupId=self.reduced_edges[i]["edgeGroupId"],
                                    wayType=self.reduced_edges[i]["wayType"], sourceNodes=source_node_id,
                                    sourceEdges=self.reduced_edges[i]["sourceEdges"], robots=[])
                if a_node["poiId"] != "0":
                    self.graph.edges[g_node_id, self.graph_node_id - 1]["connectedPoi"] = a_node["poiId"]
                self.edge_id = self.edge_id + 1
            elif a_node_type == base_node_section_type["intersection"] \
                    and b_node_type != base_node_section_type["intersection"]:
                # wezel poczatkowy krawedzi jest typu intersection, a drugi wezel jest innego typu, moze byc to POI
                self.graph.add_node(self.graph_node_id, nodeType=new_node_type["intersection_out"],
                                    sourceNode=source_node_id[0], color=node_color["out"], poiId="0")
                self.graph_node_id = self.graph_node_id + 1
                g_node_id = self.get_connected_graph_node_id(source_node_id[-1], edge_start_node=False)
                self.graph.add_edge(self.graph_node_id - 1, g_node_id, id=self.edge_id, weight=0,
                                    behaviour=Behaviour.TYPES["goto"],
                                    edgeGroupId=self.reduced_edges[i]["edgeGroupId"],
                                    wayType=self.reduced_edges[i]["wayType"], sourceNodes=source_node_id,
                                    sourceEdges=self.reduced_edges[i]["sourceEdges"], robots=[])
                if b_node["poiId"] != "0":
                    self.graph.edges[self.graph_node_id - 1, g_node_id]["connectedPoi"] = b_node["poiId"]
                self.edge_id = self.edge_id + 1
            else:
                start_node_id = self.get_connected_graph_node_id(source_node_id[0])
                end_node_id = self.get_connected_graph_node_id(source_node_id[-1], edge_start_node=False)
                self.graph.add_edge(start_node_id, end_node_id, id=self.edge_id, weight=0,
                                    behaviour=Behaviour.TYPES["goto"], edgeGroupId=self.reduced_edges[i]["edgeGroupId"],
                                    wayType=self.reduced_edges[i]["wayType"], sourceNodes=source_node_id,
                                    sourceEdges=self.reduced_edges[i]["sourceEdges"], robots=[])
                self.edge_id = self.edge_id + 1

    def get_connected_graph_node_id(self, source_node_id, edge_start_node=True):
        """
        Zwraca id wezla rozbudowanego grafu na podstawie wezla grafu zrodlowego oraz informacji czy zwracany wezel
        jest pocatkowym wezlem krawedzi czy nie.
        Parameters:
             source_node_id (string): id wezla z grafu bazowego
             edge_start_node (boolean): informacja czy dany wezel jest wezlem startowym.

        Returns:
            (int): id wezla rozbudowanego grafu, jeśli nie istnieje to zwracana wartosc None.
        """
        data = [(n, v) for n, v in self.graph.nodes(data=True) if v["sourceNode"] == source_node_id]
        node_type = self.source_nodes[source_node_id]["type"]["nodeSection"]
        if node_type == base_node_section_type["dockWaitUndock"]:
            if edge_start_node:
                # zakonczono operacje na stanowisku
                end = [node for node, v in data if v["nodeType"] == new_node_type["end"]]
                return end[0]
            else:
                # operacja na stanowisku zostanie rozpoczeta
                start = [node for node, v in data if v["nodeType"] == new_node_type["dock"]]
                return start[0]
        elif node_type == base_node_section_type["waitPOI"]:
            if edge_start_node:
                # zakonczono operacje na stanowisku
                end = [node for node, v in data if v["nodeType"] == new_node_type["end"]]
                return end[0]
            else:
                # operacja na stanowisku zostanie rozpoczeta
                start = [node for node, v in data if v["nodeType"] == new_node_type["wait"]]
                return start[0]
        elif node_type == base_node_section_type["noChanges"]:
            start = [node for node, v in data]
            return start[0]
        else:
            return None

    def add_intersetions_path(self):
        """
        Dolozenie krawedzi do skrzyzowan i przypisanie odpowiednich grup krawedzi. Jesli skrzyzowanie generowane jest
        z wezlu waiting-departure to grupa zwiazana jest z POI laczacym sie z ta krawedzia.
        """
        intersections = self.get_all_nodes_by_type_section(base_node_section_type["intersection"])
        operation_pois = [i for i in self.sorted_source_nodes_list
                          if self.source_nodes[i]["type"]["nodeSection"]
                          in [base_node_section_type["dockWaitUndock"], base_node_section_type["waitPOI"]]]

        for intersection in intersections:
            i = intersection[0]
            wait_dep_intersection = False
            group_id = self.edge_group_id
            node_in = [node for node, v in self.graph.nodes(data=True)
                       if v["sourceNode"] == i and v["nodeType"] == new_node_type["intersection_in"]]
            node_out = [node for node, v in self.graph.nodes(data=True)
                        if v["sourceNode"] == i and v["nodeType"] == new_node_type["intersection_out"]]
            all_combinations = list(itertools.product(node_in, node_out))

            if self.source_nodes[i]["type"] == base_node_type["waiting-departure"]:
                # wezel dla ktorego budowane jest skrzyzowanie jest wezlem oczekiwania
                # krawedzie zwiazane z tym skrzyzowaniem powinny nalezec do stanowiska
                connected_edges = [edge for edge in self.reduced_edges.values()
                                   if (edge["sourceNodes"][0] in operation_pois and
                                       edge["sourceNodes"][-1] == i) or (edge["sourceNodes"][-1] in operation_pois
                                                                         and edge["sourceNodes"][0] == i)]
                start_node = connected_edges[0]["sourceNodes"][0]
                end_node = connected_edges[0]["sourceNodes"][-1]
                poi_source_node = start_node if start_node in operation_pois else end_node
                group_id = self.group_id_switcher[poi_source_node]
                wait_dep_intersection = True
            if len(all_combinations) != 0:
                for edge in all_combinations:
                    self.graph.add_edge(edge[0], edge[1], id=self.edge_id, weight=0, behaviour=Behaviour.TYPES["goto"],
                                        edgeGroupId=group_id, sourceNodes=[i], sourceEdges=[0], robots=[])
                    self.edge_id = self.edge_id + 1
                if not wait_dep_intersection:
                    self.edge_group_id = self.edge_group_id + 1

    def connect_poi_to_waiting_node(self):
        """
        Polaczenie wezlow grafu, do ktorych przypisane sa POI z odpowiednimi wezlami oczekiwania tego samego grafu.
        Dla wezlow parking, queue nastepuje polaczenie z poprzedzajacym wezlem skrzyzowania "intersection_out". Jesli
        POI jest z dokowaniem to wybierany jest wezel grafu dla tego POI typu "dock", a jeśi bez dokowania to "wait".
        Nastepuje polaczenie tego wezla z wezlem "waiting", jesli bazowy wezel byl typu waiting lub odpowiedni
        "intersection_out", jesli wezel byl typu waiting-departure.
        Pominiecie polaczen intersection->POI->intersection, bo utworzone zostaly przy laczeniu glownych drog
        (main path).
        """
        # pobranie id wezlow bazowych dla parking, queue
        waiting_nodes = [i for i in self.sorted_source_nodes_list if
                         self.source_nodes[i]["type"] in [base_node_type["parking"], base_node_type["queue"]]]
        waiting_graph_nodes = [node for node in self.graph.nodes(data=True) if node[1]["sourceNode"] in waiting_nodes]
        for node in waiting_graph_nodes:
            # wezel grafu do ktorego punkt jest przypisany
            start_waiting_node = node[0]
            # wyznaczenie wezla poprzedzajacego
            end_waiting_node = [edge[0] for edge in self.graph.edges(data=True) if edge[1] == start_waiting_node][0]
            # dopisanie do krawedzi o poczatku w wezle poprzedzajacym i koncu w wezle odniesienia grafu id
            # poi typu parking, queue
            source_node_id = node[1]["sourceNode"]
            self.graph.edges[end_waiting_node, start_waiting_node]["connectedPoi"] = self.source_nodes[source_node_id][
                "poiId"]

        # pobranie id wezlow bazowych waiting
        poi_wait_nodes = [i for i in self.sorted_source_nodes_list
                          if self.source_nodes[i]["type"] == base_node_type["waiting"]]
        poi_wait_graph_nodes = [node for node in self.graph.nodes(data=True) if node[1]["sourceNode"] in poi_wait_nodes]
        for node in poi_wait_graph_nodes:
            # wezel grafu do ktorego punkt jest przypisany
            start_waiting_node = node[0]
            # wyznaczenie wezla poprzedzajacego
            end_waiting_node = [edge[0] for edge in self.graph.edges(data=True) if edge[1] == start_waiting_node][0]
            connected_poi = [edge[1] for edge in self.graph.edges(data=True) if edge[0] == start_waiting_node][0]
            graph_poi_node = self.graph.nodes[connected_poi]["sourceNode"]
            self.graph.edges[end_waiting_node, start_waiting_node]["connectedPoi"] = self.source_nodes[graph_poi_node][
                "poiId"]

        # pobranie id wezlow bazowych waiting-departure
        poi_wait_dep_nodes = [i for i in self.sorted_source_nodes_list if
                              self.source_nodes[i]["type"] == base_node_type["waiting-departure"]]
        for node_id in poi_wait_dep_nodes:
            # print("startWaitingNode", startWaitingNode)
            graph_node_ids = [node[0] for node in self.graph.nodes(data=True)
                              if node[1]["sourceNode"] == node_id
                              and node[1]["nodeType"] == new_node_type["intersection_in"]]
            # powinny byc dwa wezly, jeden laczy sie ze stanowiskiem, a drugi z wezlem
            # skrzyzowania i wchodzi w sklad krawedzi na ktorej kolejkują się roboty
            edges = [edge for edge in self.graph.edges(data=True)
                     if edge[1] in graph_node_ids]
            # powinny zostac znalezione dwie krawedzie spelniajace wymagania
            if len(edges) != 2:
                raise GraphError("waiting path, departure-waiting poi error")

            if edges[0][2]["edgeGroupId"] != 0:
                # pierwsza zapisana krawedz zwiazana jest ze stanowiskiem
                # druga dotyczy oczekiwania
                start_waiting_node = edges[1][1]
                end_waiting_node = edges[1][0]
                source_id = self.graph.nodes[edges[0][0]]["sourceNode"]
            else:
                # druga zapisana krawedz dotyczy stanowiska, a pierwsza oczekiwania
                start_waiting_node = [0][1]
                end_waiting_node = edges[0][0]
                source_id = self.graph.nodes[edges[1][0]]["sourceNode"]
            self.graph.edges[end_waiting_node, start_waiting_node]["connectedPoi"] = \
                self.source_nodes[source_id]["poiId"]

    def add_nodes_position(self):
        """
        Ustawienie wspolrzednych wezlow na mapie.
        """
        for node_id, node_data in self.graph.nodes(data=True):
            node_position = self.source_nodes[node_data["sourceNode"]]["pos"]
            node_type = node_data["nodeType"]
            if node_type in [new_node_type["intersection_in"], new_node_type["intersection_out"]]:
                self.graph.nodes[node_id]["pos"] = self.get_new_intersection_node_position(node_id)
            else:
                self.graph.nodes[node_id]["pos"] = node_position

    def add_nodes_position_test_offline(self):
        """
        Ustawienie polozen wezlow do testow. Dla POI nastepuje odpowiednie przesuniecie wezlow, aby przy wyswietlaniu
        sprawdzic czy wystepuje poprawne polaczenie wezlow dla POI.
        """
        for node_id, node_data in self.graph.nodes(data=True):
            node_position = self.source_nodes[node_data["sourceNode"]]["pos"]
            node_type = node_data["nodeType"]
            if node_type in [new_node_type["dock"], new_node_type["wait"], new_node_type["undock"],
                             new_node_type["end"]]:
                self.graph.nodes[node_id]["pos"] = self.get_poi_nodes_pos(node_id)
            elif node_type == new_node_type["noChanges"]:
                self.graph.nodes[node_id]["pos"] = node_position
            elif node_type in [new_node_type["intersection_in"], new_node_type["intersection_out"]]:
                self.graph.nodes[node_id]["pos"] = self.get_new_intersection_node_position(node_id)

    def get_poi_nodes_pos(self, graph_node_id):
        """
        Zwraca wspolrzedne przesunietego wezla dla POI.

        Parameters:
            graph_node_id (int): id wezla grafu rozszerzonego, wezel zwiazany z POI

        Returns:
            (float,float): wspolrzedne wezla na mapie
        """
        # poszukiwanie id wezlow przed i za stanowiskiem na podstawie krawedzi grafu
        source_node_poi = self.graph.nodes[graph_node_id]
        source_node_poi_id = source_node_poi["sourceNode"]

        a = [data["sourceNodes"][0] for data in self.reduced_edges.values()
             if data["sourceNodes"][-1] == source_node_poi_id]

        node_before_poi_id = a[0]
        b = [data["sourceNodes"][-1] for data in self.reduced_edges.values()
             if data["sourceNodes"][0] == source_node_poi_id]

        node_after_poi_id = b[0]
        node_before_poi_pos = self.source_nodes[node_before_poi_id]["pos"]
        node_after_poi_pos = self.source_nodes[node_after_poi_id]["pos"]
        pA = [node_before_poi_pos[0], node_before_poi_pos[1]]
        pB = [node_after_poi_pos[0], node_after_poi_pos[1]]

        base_angle = math.radians(np.rad2deg(np.arctan2(pB[1] - pA[1], pB[0] - pA[0])))
        distance = math.sqrt(math.pow(pA[0] - pB[0], 2) + math.pow(pA[1] - pB[1], 2))
        translate_to_base_node = np.array([[1, 0, 0, node_before_poi_pos[0]],
                                          [0, 1, 0, node_before_poi_pos[1]],
                                          [0, 0, 1, 0],
                                          [0, 0, 0, 1]])

        rotation_to_way = np.array([[math.cos(base_angle), -math.sin(base_angle), 0, 0],
                                   [math.sin(base_angle), math.cos(base_angle), 0, 0],
                                   [0, 0, 1, 0],
                                   [0, 0, 0, 1]])

        step = distance / 5
        nodes_vect = []
        poi_step_translation = np.array([[1, 0, 0, step * source_node_poi["nodeType"]],
                                        [0, 1, 0, 0],
                                        [0, 0, 1, 0],
                                        [0, 0, 0, 1]])
        node_translation = np.dot(np.dot(translate_to_base_node, rotation_to_way), poi_step_translation)
        if self.source_nodes[node_before_poi_id]["type"] == base_node_type["waiting-departure"]\
                or self.source_nodes[node_before_poi_id]["type"] == base_node_type["intersection"]:
            s_id = self.graph.nodes[graph_node_id]["sourceNode"]
            nodes_vect.append([self.source_nodes[s_id]["pos"][0], self.source_nodes[s_id]["pos"][1]])
        else:
            nodes_vect.append([node_translation[0][3], node_translation[1][3]])

        return nodes_vect[0][0], nodes_vect[0][1]

    def get_new_intersection_node_position(self, graph_node_id):
        """
        Zwraca wspolrzedne wezla skrzyzowania w zaleznosci od id wezla grafu rozszerzonego
            A - punkt startowy krawedzi
            B - punkt koncowy krawedzi

        Parameters:
            graph_node_id (int): wspolrzedne wezla grafu rozszerzonego, powinnien byc to wezel skrzyzowania

        Returns:
            (float, float): wspolrzedne wezla na mapie
        """
        node_type = self.graph.nodes[graph_node_id]["nodeType"]
        source_node_id = self.graph.nodes[graph_node_id]["sourceNode"]
        main_graph_nodes_id = []
        for i in self.graph.edges:
            if i[0] == graph_node_id:
                main_graph_nodes_id.append(i[1])
            elif i[1] == graph_node_id:
                main_graph_nodes_id.append(i[0])

        end_graph_node_id = 0
        end_source_node_id = None
        for i in main_graph_nodes_id:
            if self.graph.nodes[i]["sourceNode"] != source_node_id:
                end_source_node_id = self.graph.nodes[i]["sourceNode"]
                end_graph_node_id = i
        pA = [self.source_nodes[source_node_id]["pos"][0], self.source_nodes[source_node_id]["pos"][1]]

        path_type = [edgeType[2]["wayType"] for edgeType in self.graph.edges(data=True)
                     if (edgeType[0] == graph_node_id and edgeType[1] == end_graph_node_id) or
                     (edgeType[1] == graph_node_id and edgeType[0] == end_graph_node_id)]
        if end_source_node_id is not None:
            graph_source_nodes = [edge[2]["sourceNodes"] for edge in self.graph.edges(data=True)
                                  if (edge[0] == graph_node_id and edge[1] == end_graph_node_id)
                                  or (edge[0] == end_graph_node_id and edge[1] == graph_node_id)]
            if len(graph_source_nodes[0]) >= 2:
                if graph_source_nodes[0][0] == source_node_id:
                    position = self.source_nodes[graph_source_nodes[0][1]]["pos"]
                else:
                    position = self.source_nodes[graph_source_nodes[0][-2]]["pos"]
            else:
                position = self.source_nodes[end_source_node_id]["pos"]
            pB = [position[0], position[1]]
            base_angle = math.radians(np.rad2deg(np.arctan2(pB[1] - pA[1], pB[0] - pA[0])))
            translate_to_base_node = np.array([[1, 0, 0, pA[0]],
                                              [0, 1, 0, pA[1]],
                                              [0, 0, 1, 0],
                                              [0, 0, 0, 1]])

            rotation_to_way = np.array([[math.cos(base_angle), -math.sin(base_angle), 0, 0],
                                       [math.sin(base_angle), math.cos(base_angle), 0, 0],
                                       [0, 0, 1, 0],
                                       [0, 0, 0, 1]])

            way_node = np.array([[1, 0, 0, WAITING_STOP_DIST_TO_INTERSECTION],
                                [0, 1, 0, MAIN_CORRIDOR_WIDTH / 2],
                                [0, 0, 1, 0],
                                [0, 0, 0, 1]])

            if node_type == new_node_type["intersection_out"]:
                way_node[1][3] = -MAIN_CORRIDOR_WIDTH / 2

            if len(path_type) != 0:
                if path_type[0] != way_type["twoWay"]:
                    way_node[1][3] = 0
            way = np.dot(np.dot(translate_to_base_node, rotation_to_way), way_node)
            return way[0][3], way[1][3]
        else:
            return 0, 0

    def set_default_time_weight(self):
        """
        Ustawia domyslna wage na kazdej krawedzi.
        """
        robot_velocity = 0.5  # [m/s]
        for i in self.graph.edges:
            edge = self.graph.edges[i]
            is_blocked = False
            for e_id in edge["sourceEdges"]:
                if e_id != 0:
                    if not self.source_edges[e_id]["isActive"]:
                        is_blocked = True
                        break
            if is_blocked:
                self.graph.edges[i]["weight"] = None
            # elif edge["behaviour"] == Behaviour.TYPES["goto"] and edge["edgeGroupId"] != 0 \
            #         and len(edge["sourceNodes"]) == 1:
            #     self.graph.edges[i]["weight"] = 3
            elif edge["behaviour"] == Behaviour.TYPES["goto"]:
                nodes_pos = []
                for node_id in edge["sourceNodes"]:
                    nodes_pos.append(self.source_nodes[node_id]["pos"])
                dist = 0
                for j in range(len(nodes_pos) - 1):
                    dist = dist + math.hypot(nodes_pos[j + 1][0] - nodes_pos[j][0],
                                             nodes_pos[j + 1][1] - nodes_pos[j][1])
                self.graph.edges[i]["weight"] = math.ceil(dist / robot_velocity)
            elif edge["behaviour"] == Behaviour.TYPES["dock"]:
                self.graph.edges[i]["weight"] = DOCKING_TIME_WEIGHT
            elif edge["behaviour"] == Behaviour.TYPES["wait"]:
                self.graph.edges[i]["weight"] = WAIT_WEIGHT
            elif edge["behaviour"] == Behaviour.TYPES["undock"]:
                self.graph.edges[i]["weight"] = UNDOCKING_TIME_WEIGHT

    def set_max_robots(self):
        """
        Ustawia maksymalna liczbe robotow na krawedziach goto
        """
        operation_pois = [i for i in self.sorted_source_nodes_list
                          if self.source_nodes[i]["type"]["nodeSection"]
                          in [base_node_section_type["dockWaitUndock"], base_node_section_type["waitPOI"]]
                          or self.source_nodes[i]["type"] == base_node_type["parking"]]
        for i in self.graph.edges:
            edge = self.graph.edges[i]
            no_poi_nodes = not (edge["sourceNodes"][0] in operation_pois or edge["sourceNodes"][-1] in operation_pois)
            if edge["behaviour"] == Behaviour.TYPES["goto"] and len(edge["sourceNodes"]) != 1 and no_poi_nodes:
                nodes_pos = []
                for node_id in edge["sourceNodes"]:
                    nodes_pos.append(self.source_nodes[node_id]["pos"])
                dist = 0
                for j in range(len(nodes_pos) - 1):
                    dist = dist + math.hypot(nodes_pos[j + 1][0] - nodes_pos[j][0],
                                             nodes_pos[j + 1][1] - nodes_pos[j][1])                         
                self.graph.edges[i]["maxRobots"] = max(math.floor(dist / ROBOT_LENGTH), 1)

    def get_corridor_path(self, edge):
        """
        Wyznacza wspolrzedne sciezki na bazie ktorej wygenerowany zostanie korytarz

        Returns:
            (list): Zwraca liste kolejnych wspolrzednych sciezki (float, float)
        """
        # sourcePath = [(x,y),(x2,y2),...]
        source_id = [data[2]["sourceNodes"] for data in self.graph.edges(data=True) if data[0] == edge[0]
                     and data[1] == edge[1]][0]
        start_pos = self.graph.nodes[edge[0]]["pos"]
        end_pos = self.graph.nodes[edge[1]]["pos"]
        if len(source_id) > 1 and self.graph.edges[edge]["wayType"] == way_type["twoWay"]:
            # wiecej wezlow zrodlowych, krawedz nie jest krawedzia skrzyzowania
            source_path = [self.source_nodes[i]["pos"] for i in source_id]
            line = LineString(source_path)
            corridor = line.buffer(MAIN_CORRIDOR_WIDTH / 2, cap_style=3, join_style=2)
            unia = unary_union([corridor])
            x, y = unia.exterior.coords.xy
            source_path = [(x[i], y[i]) for i in range(len(x))]
            item_to_del = int((len(source_path) - 3) / 2)
            del source_path[0:item_to_del]
            del source_path[-3:]
            source_path = source_path[::-1]
            # odleglosc do poczatku krawedzi
            distanceA = math.sqrt(((start_pos[0] - source_path[0][0]) ** 2)+((start_pos[1] - source_path[0][1]) ** 2))
            # odleglosc do konca krawedzi
            distanceB = math.sqrt(((start_pos[0] - source_path[-1][0]) ** 2)+((start_pos[1] - source_path[-1][1]) ** 2))
            if distanceA > distanceB:  # punkt startowy jest na koncu wyznaczonej krawedzi
                source_path[0] = end_pos
                source_path[-1] = start_pos
            else:
                source_path[0] = start_pos
                source_path[-1] = end_pos
            return source_path
        elif len(source_id) > 1 and self.graph.edges[edge]["wayType"] != way_type["twoWay"]:
            source_path = [self.source_nodes[i]["pos"] for i in source_id]
            source_path[0] = start_pos
            source_path[-1] = end_pos
            return source_path
        elif len(source_id) == 1:
            # krawedz nalezy do skrzyzowania
            return self.get_intersection_corridor_path(edge)

    def get_intersection_corridor_path(self, edge):
        """
        Wyznaczenie sciezki ruchu dla skrzyzowania.

        Parameters:
             edge (int, int): krawedz nalezaca do skrzyzowania dla grafu rozszerzonego

        Returns:
            (list): lista kolejnych wspolrzednych dla skrzyzowania
        """
        source_node_id = [data[2]["sourceNodes"][0] for data in self.graph.edges(data=True) if data[0] == edge[0]
                          and data[1] == edge[1]][0]
        # wyznaczenie dla wezla startowego id poprzedzajacego wezla zrodla z
        # pominieciem normalnych dla krawedzi wchodzacej do stanowiska
        connected_in_edge = [data[2] for data in self.graph.edges(data=True)
                             if edge[0] in [data[0], data[1]] and len(data[2]["sourceNodes"]) > 1][0]
        previous_start_node_id = connected_in_edge["sourceNodes"][0] \
            if connected_in_edge["sourceNodes"][0] != source_node_id \
            else connected_in_edge["sourceNodes"][-1]

        # wyznaczenie dla wezla koncowego id poprzedzajacego wezla zrodla z
        # pominieciem normalnych dla krawedzi wychodzacej do stanowiska
        connected_out_edge = [data[2] for data in self.graph.edges(data=True)
                              if edge[1] in [data[0], data[1]] and len(data[2]["sourceNodes"]) > 1][0]
        previous_end_node_id = connected_out_edge["sourceNodes"][0] \
            if connected_out_edge["sourceNodes"][0] != source_node_id \
            else connected_out_edge["sourceNodes"][-1]

        if previous_start_node_id == previous_end_node_id:
            # robot zawraca na skrzyzowaniu, bezposredni przejazd przez srodek nie jest konieczny.
            return [self.graph.nodes[edge[0]]["pos"], self.graph.nodes[edge[1]]["pos"]]
        else:
            edge_in_pos = self.source_nodes[connected_in_edge["sourceNodes"][-1]]["pos"]
            edge_in_previous_pos = self.source_nodes[connected_in_edge["sourceNodes"][-2]]["pos"]
            is_in_edge_narrow = connected_in_edge["wayType"] != way_type["twoWay"]
            start_pos = _get_intersection_step_node_pos(edge_in_pos, edge_in_previous_pos,
                                                        is_in_edge_narrow, True)

            edge_out_pos = self.source_nodes[connected_out_edge["sourceNodes"][0]]["pos"]
            edge_out_previous_pos = self.source_nodes[connected_out_edge["sourceNodes"][1]]["pos"]
            is_out_edge_narrow = connected_out_edge["wayType"] != way_type["twoWay"]
            end_pos = _get_intersection_step_node_pos(edge_out_pos, edge_out_previous_pos, is_out_edge_narrow, False)

            edge_int_in_pos = self.graph.nodes[edge[0]]["pos"]
            edge_int_out_pos = self.graph.nodes[edge[1]]["pos"]
            return [edge_int_in_pos, start_pos, end_pos, edge_int_out_pos]

    def get_corridor_coordinates(self, edge):
        """
        Wyznaczenie wspolrzednych korytarza ruchu.

        Parameters:
             edge (int,int): krawedz grafu rozszerzonego

        Returns:
            (list): lista kolejnych wspolrzednych (float,float) korytarza
        """
        if not (Behaviour.TYPES["goto"] == self.graph.edges[edge]["behaviour"]):
            raise GraphError("Corridors can be only created to 'goto' behaviur edge type")

        corridor_path = self.get_corridor_path(edge)
        line = LineString(corridor_path)
        corridor = line.buffer(ROBOT_CORRIDOR_WIDTH / 2, cap_style=3, join_style=2)

        poi_a = get_node_area(True, corridor_path)
        poi_b = get_node_area(False, corridor_path)

        # create final corridor
        unia = unary_union([poi_b, corridor, poi_a])
        x, y = unia.exterior.coords.xy
        final_corridor_coordinates = [(x[i], y[i]) for i in range(len(x))]
        return final_corridor_coordinates

    def set_corridor(self):
        """
        Ustawia korytarz dla krawedzi z zachowaniami GOTO
        """
        for edge in self.graph.edges(data=True):
            if edge[2]["behaviour"] == Behaviour.TYPES["goto"]:
                self.graph.edges[edge[0], edge[1]]["corridor"] = self.get_corridor_coordinates([edge[0], edge[1]])

    def print_corridor(self, edge):
        """
        Wyswietla wykres przedstawiajacy krawedzie z ktoryh powstal korytarz i korytarz.
            zielony - wezly zrodlowe na podstawie, ktorych generowana jest sciezka
            czerwony - wirtualna sciezka ruchu robota, na podstaie ktorej generowany jest korytarz
            niebieski - korytarz ruchu

        Parameters:
            edge (int, int): krawedz grafu rozszerzonego, z zachowaniem GOTO
        """
        source_id = [data[2]["sourceNodes"] for data in self.graph.edges(data=True) if data[0] == edge[0]
                     and data[1] == edge[1]][0]
        source_path = [self.source_nodes[i]["pos"] for i in source_id]
        # wspolrzedne sciezki w korytarzu
        path_coordinates = self.get_corridor_path(edge)
        corridor_coordinates = self.get_corridor_coordinates(edge)
        # wyswietlenie korytarza
        x_source = [point[0] for point in source_path]
        y_source = [point[1] for point in source_path]
        x_path = [point[0] for point in path_coordinates]
        y_path = [point[1] for point in path_coordinates]
        x_cor = [point[0] for point in corridor_coordinates]
        y_cor = [point[1] for point in corridor_coordinates]
        plt.figure(figsize=(7, 7))
        plt.axis('equal')
        plt.plot(x_source, y_source, "g", x_path, y_path, "r", x_cor, y_cor, "b")
        plt.xlabel("x[m]")
        plt.ylabel("y[m]")
        plt.show()

    def set_robots_position(self, pois_raw_data):
        """
        Ustawia pozycje dla kazdego wezla, ktora bedzie wysylana do robota, jesli jest to wezel celu.
        Parameters:
            pois_raw_data: ([{"id": string, "pose": (float,float)), "type": gc.base_node_type["..."]}, ...]) - lista
                POI w systemie
        """
        # in nodes
        in_nodes = [node[0] for node in self.graph.nodes(data=True) if
                    node[1]["nodeType"] == new_node_type["intersection_in"]]
        for i in in_nodes:
            in_edge = [edge for edge in self.graph.edges(data=True) if edge[1] == i
                       and self.graph.nodes[edge[0]]["sourceNode"] != self.graph.nodes[edge[1]]["sourceNode"]][0]
            start_pos = self.source_nodes[in_edge[2]["sourceNodes"][-2]]["pos"]
            end_pos = self.source_nodes[in_edge[2]["sourceNodes"][-1]]["pos"]
            node_pos = self.graph.nodes[i]["pos"]
            self.graph.nodes[i]["pose"] = self.get_ros_pose_msg(start_pos, end_pos, node_pos)

        # out nodes
        out_nodes = [node[0] for node in self.graph.nodes(data=True)
                     if node[1]["nodeType"] == new_node_type["intersection_out"]
                     or self.source_nodes[node[1]["sourceNode"]]["type"] in [base_node_type["parking"],
                                                                             base_node_type["queue"],
                                                                             base_node_type["waiting"],
                                                                             base_node_type["departure"]]]

        for i in out_nodes:
            out_edge = [edge for edge in self.graph.edges(data=True) if edge[0] == i
                        and self.graph.nodes[edge[0]]["sourceNode"] != self.graph.nodes[edge[1]]["sourceNode"]][0]
            node_pos = self.graph.nodes[i]["pos"]
            start_pos = self.source_nodes[out_edge[2]["sourceNodes"][0]]["pos"]
            end_pos = self.source_nodes[out_edge[2]["sourceNodes"][1]]["pos"]
            self.graph.nodes[i]["pose"] = self.get_ros_pose_msg(start_pos, end_pos, node_pos)

        for node in self.graph.nodes(data=True):
            if "pose" not in node[1] and node[1]["poiId"] != "0":
                poi_pose = [poi["pose"] for poi in pois_raw_data if poi["id"] == node[1]["poiId"]][0]
                self.graph.nodes[node[0]]["pose"] = poi_pose

    def get_ros_pose_msg(self, start_point, end_point, node_pos):
        """
        Wygenerowanie struktury wiadomosci dla robota.
        Parameters:
            start_point ((float, float)): wspolrzedne wezla (zrodlowy) poczatkowego odcinka
            end_point ((float, float)): wspolrzedne wezla (zrodlowy) koncowego odcinka
            node_pos ((float, float)): wspolrzedna wezla (grafu rozszerzonego) koncowego

        Returns:
            (ROS pose): Pozycja wezla dla robota
                        {"position": {"x": , "y": , "z":}, "orientation": {"x": , "y": , "z": , "w":}
        """
        robot_pose = {"position": {}, "orientation": {}}

        robot_pose["position"]["x"] = node_pos[0]
        robot_pose["position"]["y"] = node_pos[1]
        robot_pose["position"]["z"] = 0

        robot_pose["orientation"]["x"] = 0.0
        robot_pose["orientation"]["y"] = 0.0
        robot_pose["orientation"]["z"] = 0.0
        robot_pose["orientation"]["w"] = 0.0

        last_segment_x = end_point[0] - start_point[0]
        last_segment_y = end_point[1] - start_point[1]

        finish_angle = math.atan2(last_segment_y, last_segment_x)
        robot_pose["orientation"]["z"] = math.sin(finish_angle / 2)
        robot_pose["orientation"]["w"] = math.cos(finish_angle / 2)

        return robot_pose

    def is_return_edge(self, edge):
        """
        Sprawdza czy podana krawedz grafu jest krawedzia powrotna.
        Parameters:
            edge ((string,string)): krawedz
        Returns:
            (bool): informacja czy podana krawedz pozwala na bezposredni powrot do tego samego POI
        """
        data = self.graph.edges[edge]
        return data["edgeGroupId"] != 0 and data["behaviour"] == Behaviour.TYPES["goto"] and data["weight"] == 0

    def print_graph(self, plot_size=(45, 45)):
        """
        Wyswietla utworzony graf.
        Parameters
            plot_size (float,float): rozmiar wykresu w calach
        """
        plt.figure(figsize=plot_size)
        plt.axis('equal')
        node_pos = nx.get_node_attributes(self.graph, "pos")

        max_robots = nx.get_edge_attributes(self.graph, "maxRobots")
        # edge_col = [G[u][v]["color"] for u,v in self.graph.edges()]

        node_col = [self.graph.nodes[i]["color"] for i in self.graph.nodes()]

        # nx.draw_networkx(self.graph, node_pos,node_color = node_col, node_size=550,font_size=15,
        # with_labels=True,font_color="w", width=2)

        # nx.draw_networkx(self.graph, node_pos, node_color=node_col, node_size=3000, font_size=20,
        #                  with_labels=True, font_color="w", width=4)
        # nx.draw_networkx_edge_labels(self.graph, node_pos,
        #                              edge_labels=max_robots, font_size=30)

        nx.draw_networkx(self.graph, node_pos, node_color=node_col, node_size=2000, font_size=30,
                                          with_labels=True, font_color="w", width=4)
        nx.draw_networkx_edge_labels(self.graph, node_pos, edge_labels=max_robots, font_size=10)


        # nx.draw_networkx(self.graph, node_pos,edge_color= edge_col, node_color = node_col, node_size=3000,
        # font_size=25,with_labels=True,font_color="w", width=4)
        # nx.draw_networkx_edge_labels(self.graph, node_pos, edge_color= edge_col, node_color = node_col,
        # edge_labels=maxRobots,font_size=30)
        # nx.drawing.nx_agraph.write_dot(self.graph, "/home/pawel/proj/SMART/supervisor/graph.dot")
        plt.show()
        plt.close()
