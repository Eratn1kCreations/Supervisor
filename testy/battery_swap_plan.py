import math
import numpy as np
import random

# mogą to być dodatkowe funkcje dispatchera do planowania lub nowy moduł wykorzystujący klasy z dispatchera
# potrzebne elementy: graf, robot, zadanie, manager zadan, manager robotow; czas dojazdu do ładowarki liczony jest
# względem krawędzi na której on się aktualnie znajduej
# później powinno być to uzależnione od zadania.

# Plan zwraca listę zadań z ładowaniem dla robotów -> w zadaniach ustawiany jest odpowiednio czas startu
# po stronie dispatchera ma nastąpić weryfikacja czy takie zadanie może zostać przydzielone w kolejnym kroku i jeśli tak
# to jest ono zlecane

# Do algorytmu planującego przekazywany jest słownik robotów i lista wszstkich zadań ładowania -> funkcja
# weryfikująca plan i ewentualną konieczność przeplanowania,
# czas ładowania i rozładowania baterii #jako stała
# próg przed którego przekrozeniem nie można dokonać wymiany #stała

# triger na różnicę w planie, jeśli jakieś zadanie należy znacząco przesunąć do wcześniejszego lub późniejszego
# wykonania
# to należy wygenerować aktualizację, jeśli różnica jest nieznaczna pozostaje poprzedni plan. (np. przesunięcie 2 minut)
# aby z tego korzystać należy mieć pewność, że za każdym razem plan generowany jest w ten sam sposób;

# ponowne uruchomienie funkcji do przeplanowania, gdy robot zglosi przekroczenie progu ostrzegawczego
# -> szybkie wygenerowanie planu i zadania wymiany ładowania dla robota, ustawiany jest aktualny czas -> po wejsicu w
# dispatcher od razu takie zadanie powinno byc przydzielone do robota
# zadaniem planowania jest takie ułożenie wymian, że po planowanym jej zakończeniu threshold nie zostanie przekroczony,
# czas zakończenia zadania wyznaczany z grafu

# zwracanie planu długookresowego w zakładanym horyzoncie czasowym
# plan krótkookresowy -> czas trwania -> maksymalny czas pracy robota z 1 wymianą (czas pracy dwóch rozładowań)


class Battery:
    idBat = 0
    statusAll = {
        "discharged": 1,
        "discharging": 2,
        "not use": 3,
        "charging": 4,
        "charged": 5
    }

    def __init__(self, percentage_value=None, discharge_speed=None, status=None):
        if percentage_value is None:
            percentage_value = 100
        if discharge_speed is None:
            discharge_speed = 1
        if status is None:
            status = self.statusAll["charged"]
        self.status = status
        self.percentage_value = percentage_value
        self.charge_speed = 5
        self.max_charge_speed = 10
        self.discharge_speed = discharge_speed

    def set_unique_id(self):
        self.idBat = Battery.idBat + 1
        Battery.idBat = Battery.idBat + 1

    def setChargeSpeed(self, newChargeSpeed):
        self.charge_speed = newChargeSpeed if newChargeSpeed <= self.max_charge_speed else self.max_charge_speed

    def getChargeSpeed(self):
        return self.charge_speed

    def getStatus(self):
        return self.status

    def use(self):
        if self.status == self.statusAll["charging"]:
            self.percentage_value = self.percentage_value + self.charge_speed
            if self.percentage_value >= 100:
                self.percentage_value = 100
                self.status = self.statusAll["charged"]
        elif self.status == self.statusAll["discharging"]:
            self.percentage_value = self.percentage_value - self.discharge_speed
            if self.percentage_value <= 0:
                self.percentage_value = 0
                self.status = self.statusAll["discharged"]
        return self.status

    def startCharging(self):
        self.status = self.statusAll["charging"]

    def stopUsing(self):
        self.status = self.statusAll["not use"]

    def startDischarging(self):
        self.status = self.statusAll["discharging"]

    def getId(self):
        return self.idBat

    def getVoltage(self):
        return self.percentage_value


class Robot:
    taskAll = {
        "starting": 1,
        "landing": 2,
        "swap_battery": 3,
        "goToGoal": 4
    }
    statusAll = {
        "in progress": 1,
        "done": 2
    }

    def __init__(self, battery, basePosition=None):
        if basePosition is None:
            basePosition = {"x": 0.0, "y": 0.0}
        self.startingTime = 3  # [s]
        self.landingTime = 5  # [s]
        self.swapTime = 3  # [s]
        self.speed = 4  # [m/s]
        self.position = basePosition  # [m]
        self.batteryUsage = 3  # [%/s]
        self.taskDuration = 0  # [s]
        self.status = self.statusAll["done"]
        self.task = self.taskAll["landing"]
        self.battery = battery

    def setUniqueId(self):
        self.idDrone = Drone.idDrone + 1
        Drone.idDrone = Drone.idDrone + 1

    def run(self):
        if self.task == taskAll["starting"]:
            self.battery.startDischarging()
            if self.status["in progress"] and self.taskDuration < self.startingTime:
                self.taskDuration = self.taskDuration + 1
            elif self.status["in progress"] and self.taskDuration >= self.startingTime:
                self.status = self.status["done"]

        elif self.task == taskAll["landing"]:
            if self.status["in progress"] and self.taskDuration < self.landingTime:
                self.battery.startDischarging()
                self.taskDuration = self.taskDuration + 1
            elif self.status["in progress"] and self.taskDuration >= self.landingTime:
                self.battery.stopUsing()
                self.status = self.status["done"]
            else:
                self.battery.stopUsing()

        elif self.task == taskAll["swap_battery"]:
            if self.status["in progress"] and self.taskDuration < self.swapTime:
                self.taskDuration = self.taskDuration + 1
            elif self.status["in progress"] and self.taskDuration >= self.swapTime:
                self.status = self.status["done"]
            self.battery.stopUsing()

        elif self.task == taskAll["goToGoal"]:
            self.battery.startDischarging()
            goalReached = self.goToPoint(goal)
            if goalReached:
                self.taskDuration = self.taskDuration + 1

        self.battery.use()
        return self.status

    def setTask(self, task, battery=None):
        self.taskDuration = 0
        self.task = task
        if task == taskAll["swap_battery"] and battery is not None:
            self.battery = battery

    def returnBattery(self):
        return self.battery

    def goToPoint(self, goal):
        stepDistance = self.speed
        pA = [self.position["x"], self.position["y"]]
        pB = [goal["x"], goal["y"]]
        baseAngle = math.radians(np.rad2deg(np.arctan2(pB[1] - pA[1], pB[0] - pA[0])))
        distance = math.sqrt(math.pow(pA[0] - pB[0], 2) + math.pow(pA[1] - pB[1], 2))
        if stepDistance >= distance:
            self.position = goal
            return True

        translateToDronePos = np.array([[1, 0, 0, pA[0]],
                                        [0, 1, 0, pA[1]],
                                        [0, 0, 1, 0],
                                        [0, 0, 0, 1]])

        rotationToGoal = np.array([[math.cos(baseAngle), -math.sin(baseAngle), 0, 0],
                                   [math.sin(baseAngle), math.cos(baseAngle), 0, 0],
                                   [0, 0, 1, 0],
                                   [0, 0, 0, 1]])

        stepDrone = np.array([[1, 0, 0, stepDistance],
                              [0, 1, 0, 0],
                              [0, 0, 1, 0],
                              [0, 0, 0, 1]])
        nodeTranslation = np.dot(np.dot(translateToDronePos, rotationToGoal), stepDrone)

        self.position["x"] = nodeTranslation[0][3]
        self.position["y"] = nodeTranslation[1][3]
        return False

    def getTimeToGoal(self, goal):
        stepDistance = self.speed
        pA = [self.position["x"], self.position["y"]]
        pB = [goal["x"], goal["y"]]
        distance = math.sqrt(math.pow(pA[0] - pB[0], 2) + math.pow(pA[1] - pB[1], 2))
        flyightTime = distance % stepDistance + 1
        return flyightTime

    def getStandardTime(self):
        # czas startu, wymiany i ladowania
        return {"startTime": self.startingTime, "swapTime": self.swapTime, "landingTime": self.landingTime}

    def getSwapTime(self):
        return self.startingTime + self.landingTime + self.swapTime

    def getMaxFlightTime(self):
        return math.ceil(100 / self.batteryUsage)


class BatteryStation:
    def __init__(self):
        self.maxChargingSpeed = 30  # [%/s]
        self.maxAllowedDrones = 5
        self.batteries = []

    def addBattery(self, battery):
        self.batteries.append(battery)

    def addBatteryList(self, batteries):
        for battery in batteries:
            self.batteries.append(battery)

    def removeBatteryById(self, idBat):
        removeBatteryId = None
        i = 0
        for battery in self.batteries:
            if idBat == battery.getId():
                removeBatteryId = i
                del self.batteries[i]
                break
            i = i + 1

    def getBatteryForDrone(self, threshold=30):
        chargedBatteries = [battery for battery in self.batteries if
                            battery.getStatus() == Battery().statusAll["charged"]]
        if len(chargedBatteries) != 0:
            return chargedBatteries[0]
        else:
            foundBattery = None
            for battery in self.batteries:
                if battery.getVoltage() >= threshold:
                    if foundBattery is None:
                        foundBattery = battery
                    elif foundBattery.getVoltage() < battery.getVoltage():
                        foundBattery = battery
            return foundBattery

    def getBatteriesData(self):
        return self.batteries

    def printBatteryVoltage(self):
        for battery in self.batteries:
            print("battery id ", battery.getId(), battery.getVoltage(), "%")

    def chargeBatteries(self):
        # jesli ladowanie danej baterii zostanie rozpoczete to jest ladowana do samego konca, aby
        # dostarczyc cala baterie dla drona
        freeChargingSpeed = self.maxChargingSpeed

        for i in range(len(self.batteries)):
            if self.batteries[i].getStatus() == Battery().statusAll["charging"]:
                self.batteries[i].setChargeSpeed(freeChargingSpeed)
                freeChargingSpeed = freeChargingSpeed - self.batteries[i].getChargeSpeed()
                self.batteries[i].use()
            if freeChargingSpeed == 0:
                break

        if freeChargingSpeed != 0:
            for i in range(len(self.batteries)):
                if self.batteries[i].getStatus() in [Battery().statusAll["discharged"], Battery().statusAll["not use"]]:
                    self.batteries[i].startCharging()
                    self.batteries[i].setChargeSpeed(freeChargingSpeed)
                    freeChargingSpeed = freeChargingSpeed - self.batteries[i].getChargeSpeed()
                    self.batteries[i].use()
                if freeChargingSpeed == 0:
                    break


class BatterySwapManagement:
    # tworzy plan do realizacji, posiada informację o stanie naładowania baterii w stacjach
    # położenie dronów i ich stanie baterii, na podstawie tych informacji ukladany jest plan
    def __init__(self, station):
        self.drones = []
        self.station = station

    def addDrone(self, drone):
        self.drones.append(drone)

    def removeDrone(self, idDrone):
        removeDroneId = None
        i = 0
        for battery in self.drones:
            if idDrone == drones.getId():
                removeDroneId = i
                del self.drones[i]
                break
            i = i + 1
