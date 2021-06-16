import random
import logging
import time
import threading
from queue import Queue

format = "%(asctime)s: %(message)s"
logging.basicConfig(format=format, level=logging.INFO,
                    datefmt="%H:%M:%S")

daytime = threading.Event()
people_in_home = threading.Semaphore(1)

sectors = list()

global living_sector, material_sector, food_sector, carts_controller

"""#### SETUP ####"""

carts = [
    20,  # living_sector
    20,  # material_sector
    20  # food_sector
]

"""###############"""


class AbstractSector(object):

    def __init__(self, inhabitants=0, materials=0, food=0):
        """funkcja inicjująca sektor"""

        self.resources_lock = threading.Lock()
        self.resources = {
            'people': list(),
            'food': 0,
            'materials': 0
        }

        logging.debug("Creating an object of %s.", type(self).__name__)

        if inhabitants != 0 and type(self) is not LivingSector:
            logging.error("Sector other than LivingSector cannot have inhabitants initially.")
        for i in range(inhabitants):
            self.resources['people'].append(Person(i))

        self.resources['food'] = food
        self.resources['materials'] = materials

        if type(self) is AbstractSector:
            raise NotImplementedError("Can't create an object of an abstract class.")

    def start(self):
        """funkcja startująca proces sektoru"""
        thread = threading.Thread(target=self.process)
        thread.start()

    def get_resources_str(self):
        """funckja zwracająca reprezentację stringową zasobów sektoru"""
        return f"---------------------------------------\n" \
               f"Sector \t\t:\t {type(self).__name__}\n" \
               f"Inhabitants :\t {len(self.resources['people'])}\n" \
               f"Materials \t:\t {self.resources['materials']}\n" \
               f"Food \t\t:\t {self.resources['food']}"

    def get_resources(self):
        """funckja zwracająca zasoby sektoru"""
        return self.resources['people'], self.resources['materials'], self.resources['food']

    def update_resources(self, res_type, quantity=0):
        """funckja aktualizująca zasoby sektoru - wykorzystuje do tego
            Lock, który zabezbiecza self.resources przed błędami.
            Do tego nie pozwala ona na odjęcie większej ilości zasobów
            niż jest dostępne i zwraca ilość dodanych lub odjętych zasobów"""
        with self.resources_lock:
            logging.debug(f"Updating a quantity of {res_type} in {type(self).__name__} by {quantity}.")
            if -quantity > self.resources[res_type]:
                quantity = - self.resources[res_type]
            self.resources[res_type] += quantity

            return quantity

    def get_type(self):
        """funkcja zwracjąca typ klasy"""
        return type(self).__name__

    def take_people(self, new_people: list):
        """funkcja dodająca ludzi do sektoru"""
        with self.resources_lock:
            logging.debug(f'Adding {new_people} to {type(self).__name__}')
            self.resources['people'] += new_people

    def send_people(self):
        """funckja wysyłająca wszystkich ludzi z sektoru"""
        with self.resources_lock:
            logging.debug(f'Sending all people from {type(self).__name__}')
            temp = self.resources['people']
            self.resources['people'] = list()
            return temp

    def send_request(self, supply_type):
        """funckja wysyłająca request do CartsController'a"""
        logging.debug(f"{type(self).__name__} poprosił o {supply_type}")
        SupplyRequest(supply_type, self)

    def process(self):
        """placeholder procesu, który jest nadpisywany w klasach poszczególnych sektorów"""
        pass


class LivingSector(AbstractSector):

    def process(self):
        """główny proces klasy LivingSector"""
        while True:

            while daytime.isSet():
                pass
            # kiedy przychodzi noc i ludzie zostali przysłani do sektoru starzeje ich i karmi
            with people_in_home:
                self.age_people()
                self.feed_people()
            daytime.wait()

    def age_people(self):
        """funkcja starzeje ludzi i usuwa z listy martwych"""
        people_temp = self.resources['people']
        for person in people_temp:
            person.age_up()
            if not person.is_alive():
                self.resources['people'].remove(person)
                logging.debug(f'Person {person} died')

    def feed_people(self):
        """funckja karmiąca posortowanych ludzi przez ich wartość
        - nienakarmieni zostają postarzeni (odejmuje się im dni życia)"""
        self.resources['people'].sort(key=lambda p: p.get_value(), reverse=True)
        people_temp = self.resources['people']
        for person in people_temp:
            if self.update_resources('food', -10) == 0:
                person.age_up()
                person.age_up()
                person.age_up()
                if not person.is_alive():
                    self.resources['people'].remove(person)
                    logging.debug(f'Person {person} died')
        # jeśli jedzenia jest więcej niż racje na 2 dni, to rodzi się nowy człowiek za każde 100 jedzenia nadmiaru
        while self.resources['food'] > len(self.resources['people']) * 10 * 2:
            self.update_resources('food', -100)
            self.take_people([Person()])

    def __repr__(self):
        return 'LivingSector'


class MaterialSector(AbstractSector):
    def process(self):
        """główny proces klasy MaterialSector, produkujący materiały"""
        while True:
            while daytime.isSet():
                produced_materials = 0
                for person in self.resources['people']:
                    produced_materials += person.get_work_speed() * 2
                self.update_resources('materials', produced_materials)
                time.sleep(1)

    def __repr__(self):
        return 'MaterialSector'


class FoodSector(AbstractSector):
    def process(self):
        """główny proces klasy FoodSector, produkujący jedzenie zużywając materiały"""
        while True:
            while daytime.isSet():
                produced_food = 0
                for person in self.resources['people']:
                    produced_food += person.get_work_speed() * (-self.update_resources('materials', -2))
                self.update_resources('food', produced_food)
                time.sleep(1)

    def __repr__(self):
        return 'FoodSector'


class Person(object):
    def __init__(self, name=0):
        """funckja inicjująca osobę, nadając jej losowe dni, które ma przeżyć i losową prędkość pracy"""
        self._age = 0
        self._is_alive = True
        logging.debug("Creating an object of %s.", type(self).__name__)
        self._days = random.randrange(10, 15)
        self._work_speed = random.randrange(70, 130) / 100
        self._name = name

    def get_days(self):
        return self._days

    def get_work_speed(self):
        return self._work_speed

    def get_name(self):
        return self._name

    def get_age(self):
        return self._age

    def is_alive(self):
        return self._is_alive

    def print_person(self):
        print(
            f'Person \t\t:\t {self._name}\n'
            f'Is alive \t:\t {self._is_alive}\n'
            f'Work speed \t:\t {self._work_speed}\n'
            f'Age \t\t:\t {self._age}\n'
            f'Days \t\t:\t {self._days}\n'
        )

    def age_up(self):
        """funckja starzejąca człowieka o 1 dzień i wywołująca funkcję die jeśli skończyły się jego dni"""
        self._age += 1
        if self._age >= self._days:
            self.die()

    def die(self):
        self._is_alive = False

    def get_value(self):
        """funkcja zwracająca wartość człowieka na podstawie jego pozostałych dni i prędkości pracy"""
        value = 0
        value += (self._days - self._age)
        value *= self._work_speed
        return value

    def __repr__(self):
        return f'(Person {self._name}, Age: {self._age}/{self._days}, Work speed: {self._work_speed})'


class Cart:
    # pojemność wózka - może przewozić mniej
    resources_amount = {
        'food': 10,
        'materials': 20
    }

    def __init__(self, current_location: AbstractSector):
        self.current_location = current_location

    def cart(self, do: AbstractSector, res_type):
        """funckja przeworząca zasoby między sektorami"""
        if res_type != 0:
            q = -self.current_location.update_resources(res_type, -self.resources_amount[res_type])
            logging.debug(f"Wyruszono z {type(self.current_location).__name__} z {res_type}: {q}")
            time.sleep(2)
            do.update_resources(res_type, q)
            self.current_location = do
            logging.debug(f"Dotarto do {type(do).__name__} z {res_type}: {q}")
        else:
            logging.debug(f"Wyruszono z {type(self.current_location).__name__} z niczym")
            time.sleep(2)
            self.current_location = do
            logging.debug(f"Dotarto do {type(do).__name__} z niczym")


class SupplyRequest:

    def __init__(self, supply_type, sender):
        self.supply_type = supply_type
        self.sender = sender

        self.send_request()

    def send_request(self):
        """funckja wysyłająca request do CartsController'a"""
        logging.debug(f"{type(self).__name__} przekazał request od {self.sender} o {self.supply_type}")
        carts_controller.receive_request(self)


class CartsController:
    carts_lock = threading.Lock()

    free_carts = {
        'LivingSector': Queue(),
        'MaterialSector': Queue(),
        'FoodSector': Queue()
    }

    carts_in_road = {
        'LivingSector - MaterialSector': 0,
        'MaterialSector - LivingSector': 0,
        'FoodSector - MaterialSector': 0,
        'MaterialSector - FoodSector': 0,
        'LivingSector - FoodSector': 0,
        'FoodSector - LivingSector': 0
    }

    request_queue = Queue()

    def start(self):
        thread = threading.Thread(target=self.main_loop)
        thread.start()

    def main_loop(self):
        while True:
            if self.request_queue.qsize() > 0:
                req = self.request_queue.get()
                max_sect = None
                for sect in sectors:
                    if sect != req.sender:
                        if sect.resources[req.supply_type] > 0:
                            if max_sect is None:
                                max_sect = sect
                            elif sect.resources[req.supply_type] > max_sect.resources[req.supply_type]:
                                max_sect = sect
                logging.debug(f"{type(self).__name__} próbuje wysłać cart z {type(max_sect).__name__} do"
                              f" {type(req.sender).__name__}")
                threading.Thread(target=self.send_cart, args=(req, max_sect)).start()
            else:
                if material_sector.resources['materials'] >= 10:
                    food_sector.send_request('materials')
                if food_sector.resources['food'] >= 0:
                    living_sector.send_request('food')

    def send_cart(self, req: SupplyRequest, from_where):
        from_where_ = repr(from_where)
        if from_where_ == 'None':
            return
        material_sector_ = repr(material_sector)
        living_sector_ = repr(living_sector)
        food_sector_ = repr(food_sector)

        if self.free_carts[from_where_].qsize() > 0:
            self._send_cart(from_where, req.sender, req.supply_type)

        elif self.free_carts[living_sector_].qsize() > self.free_carts[material_sector_].qsize():
            if self.free_carts[living_sector_].qsize() > self.free_carts[food_sector_].qsize():
                if self.free_carts[living_sector_].qsize() > 0:
                    self._send_cart(living_sector, from_where, 0)
                    self._send_cart(from_where, req.sender, req.supply_type)

            elif self.free_carts[food_sector_].qsize() > 0:
                self._send_cart(food_sector, from_where, 0)
                self._send_cart(from_where, req.sender, req.supply_type)
        elif self.free_carts[material_sector_].qsize() > 0:
            self._send_cart(material_sector, from_where, 0)
            self._send_cart(from_where, req.sender, req.supply_type)
        elif self.free_carts[food_sector_].qsize() > 0:
            self._send_cart(food_sector, from_where, 0)
            self._send_cart(from_where, req.sender, req.supply_type)

        else:
            logging.debug(f"{type(self).__name__} nie udało się wysłać carta z {type(from_where).__name__} do"
                          f" {type(req.sender).__name__}")
            self.request_queue.put(req)

    def _send_cart(self, from_where, to_where, supply_type):
        used_cart = self.free_carts[repr(from_where)].get()

        self.carts_in_road[repr(from_where) + ' - ' + repr(to_where)] += 1

        cart_travel = threading.Thread(target=used_cart.cart, args=(to_where, supply_type))
        cart_travel.start()
        cart_travel.join()
        self.free_carts[repr(used_cart.current_location)].put(used_cart)
        self.carts_in_road[repr(from_where) + ' - ' + repr(to_where)] -= 1

    def receive_request(self, req: SupplyRequest):
        self.request_queue.put(req)


class SectorsController:
    def __init__(self, carts=[0, 0, 0]):
        self.start_processes(carts)

    def start_processes(self, carts):
        logging.debug("SectorsController\t\t : \tStarting processes.")
        global living_sector, material_sector, food_sector
        living_sector = LivingSector(inhabitants=100)
        material_sector = MaterialSector(materials=0)
        food_sector = FoodSector(food=0)

        global sectors
        sectors = [
            living_sector,
            material_sector,
            food_sector
        ]

        for sector in sectors:
            sector.start()

        day = threading.Thread(target=self.day_cycle)
        day.start()

        global carts_controller
        carts_controller = CartsController()
        carts_controller.start()

        for i in range(carts[0]):
            carts_controller.free_carts['LivingSector'].put(Cart(living_sector))

        for i in range(carts[1]):
            carts_controller.free_carts['MaterialSector'].put(Cart(material_sector))

        for i in range(carts[2]):
            carts_controller.free_carts['FoodSector'].put(Cart(food_sector))

        threading.Thread(target=self.main_loop).start()

    def main_loop(self):
        while True:
            people_in_home.acquire()
            people = living_sector.send_people()
            food = 0
            materials = 0
            for sector in sectors:
                food += sector.resources['food']
                materials += sector.resources['materials']
            if food * 2 > materials:
                material_sector.take_people(people[:int(len(people) / 2)])
                food_sector.take_people(people[int(len(people) / 2):])
            else:
                food_sector.take_people(people[:int(len(people) / 2)])
                material_sector.take_people(people[int(len(people) / 2):])

            while daytime.isSet():
                print(f'Dzień\n'
                      f'{living_sector.get_resources_str()}\n'
                      f'{material_sector.get_resources_str()}\n'
                      f'{food_sector.get_resources_str()}\n\n'
                      )

                print(f"Free carts:")
                for sect in carts_controller.free_carts:
                    print(f"{sect}: {carts_controller.free_carts[sect].qsize()}")
                print(f"\nCarts in Road:")
                for road in carts_controller.carts_in_road:
                    print(f"{road}: {carts_controller.carts_in_road[road]}")

                print('\n\n\n')
                time.sleep(2)

            people = food_sector.send_people()
            people += material_sector.send_people()
            living_sector.take_people(people)

            people_in_home.release()

            print(f'Noc\n'
                  f'{living_sector.get_resources_str()}\n'
                  f'{material_sector.get_resources_str()}\n'
                  f'{food_sector.get_resources_str()}\n\n'
                  )

            print('\n\n\n')
            daytime.wait()

    @staticmethod
    def day_cycle():
        while True:
            logging.debug("day_cycle\t\t\t : \tDay is raising!")
            daytime.set()
            time.sleep(16)
            logging.debug("day_cycle\t\t\t : \tNight has come...")
            daytime.clear()
            time.sleep(8)


start = SectorsController(carts)
