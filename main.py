import random
import logging
import time
import threading
from queue import Queue

format = "%(asctime)s: %(message)s"
logging.basicConfig(format=format, level=logging.INFO,
                    datefmt="%H:%M:%S")

daytime = threading.Event()
people_sent = threading.Semaphore(0)

sectors = list()

global living_sector, material_sector, food_sector, carts_controller


class AbstractSector(object):
    # _list_of_people = list()

    # przerabiamy na słownik, żeby było łatwiej tym zarządzać
    def __init__(self, inhabitants=0, materials=0, food=0):

        self.resources_lock = threading.Lock()
        self.resources = {
            'people': list(),
            'food': 0,
            'materials': 0
        }


        logging.info("Creating an object of %s.", type(self).__name__)

        if inhabitants != 0 and type(self) is not LivingSector:
            logging.error("Sector other than LivingSector cannot have inhabitants initially.")
        # self._inhabitants = inhabitants

        # for i in range(inhabitants):
        #     self._list_of_people.append(Person(i))

        for i in range(inhabitants):
            self.resources['people'].append(Person(i))

        # self._materials = materials
        # self._food =

        self.resources['food'] = food
        self.resources['materials'] = materials

        if type(self) is AbstractSector:
            raise NotImplementedError("Can't create an object of an abstract class.")

        self.startup()

    def startup(self):
        pass

    def start(self):
        thread = threading.Thread(target=self.process)
        thread.start()

    def get_resources(self):
        print(
            f"---------------------------------------\n"
            f"Sector \t\t:\t {type(self).__name__}\n"
            f"Inhabitants :\t {self.resources['people']}\n"
            f"Materials \t:\t {self.resources['materials']}\n"
            f"Food \t\t:\t {self.resources['food']}"
        )
        return self.resources['people'], self.resources['materials'], self.resources['food']

    # def update_inhabitants(self, quantity=0):
    #     logging.info("Updating a quantity of inhabitants in %s by %i.", type(self).__name__, quantity)
    #     self._inhabitants += quantity

    # def update_materials(self, quantity=0):
    #     logging.info("Updating a quantity of materials in %s by %i.", type(self).__name__, quantity)
    #     self.materials += quantity
    #
    # def update_food(self, quantity=0):
    #     logging.info("Updating a quantity of food in %s by %i.", type(self).__name__, quantity)
    #     self.food += quantity

    def update_resources(self, res_type, quantity=0):
        with self.resources_lock:
            logging.info(f"Updating a quantity of {res_type} in {type(self).__name__} by {quantity}.")
            if -quantity > self.resources[res_type]:
                quantity = - self.resources[res_type]
            self.resources[res_type] += quantity

            return quantity

    def get_type(self):
        return type(self).__name__

    def take_people(self, new_people: list):
        with self.resources_lock:
            logging.info(f'Adding {new_people} to {type(self).__name__}')
            self.resources['people'] += new_people

    def send_people(self):
        with self.resources_lock:
            logging.info(f'Sending all people from {type(self).__name__}')
            temp = self.resources['people']
            self.resources['people'] = list()
            return temp

    def send_request(self, supply_type):
        logging.info(f"{type(self).__name__} poprosił o {supply_type}")
        SupplyRequest(supply_type, self)

    def process(self):
        pass


class LivingSector(AbstractSector):
    # todo zarządzanie ludźmi - proces

    def process(self):
        while True:
            people_sent.release()
            people_sent.release()

            while daytime.isSet():
                pass

            people_sent.acquire()
            people_sent.acquire()

            self.age_people()
            self.feed_people()
            daytime.wait()

    def age_people(self):
        people_temp = self.resources['people']
        for person in people_temp:
            person.age_up()
            if not person.is_alive():
                self.resources['people'].remove(person)
                logging.info(f'Person {person} died')

    def feed_people(self):
        # karmienie posortowanych ludzi przez ich wartość
        self.resources['people'].sort(key=lambda p: p.get_value(), reverse=True)
        people_temp = self.resources['people']
        for person in people_temp:
            if self.update_resources('food', -10) == 0:
                person.age_up()
                person.age_up()
                person.age_up()
                if not person.is_alive():
                    self.resources['people'].remove(person)
                    logging.info(f'Person {person} died')

    def __repr__(self):
        return 'LivingSector'


class MaterialSector(AbstractSector):
    # todo wytwarzanie materiałów - proces
    def process(self):
        while True:
            # daytime.wait()

            # people_sent.acquire()
            # logging.info("material_sector\t : \tGet people.")
            # while daytime.isSet():
            #     logging.info("material_sector\t : \tProducing materials.")
            #     time.sleep(2)
            # logging.info("material_sector\t : \tSend off people.")
            # time.sleep(0.1)
            # people_sent.release()
            while daytime.isSet():
                # TODO PRACA
                produced_materials = len(self.resources['people']) * 50
                self.update_resources('materials', produced_materials)
                time.sleep(1)

    def __repr__(self):
        return 'MaterialSector'


class FoodSector(AbstractSector):
    # todo wytwarzanie jedzenia - proces
    def process(self):
        while True:
            # daytime.wait()
            #
            # people_sent.acquire()
            # logging.info("food_sector\t\t : \tGet people.")
            # while daytime.isSet():
            #     logging.info("food_sector\t\t : \tProducing food.")
            #     time.sleep(2)
            # logging.info("food_sector\t\t : \tSend off people.")
            # time.sleep(0.1)
            # people_sent.release()

            while daytime.isSet():
                # TODO PRACA
                produced_food = len(self.resources['people']) * self.update_resources('materials', 50)
                self.update_resources('food', produced_food)
                time.sleep(1)

    def __repr__(self):
        return 'FoodSector'


class Person(object):
    # todo starzenie się, jedzenie + to ile ma siły w zależności ile zjadł

    def __init__(self, name=0):
        self._age = 0
        self._is_alive = True
        logging.info("Creating an object of %s.", type(self).__name__)
        self._days = random.randrange(100, 150)
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
        self._age += 1
        if self._age >= self._days:
            self.die()

    def die(self):
        self._is_alive = False

    def get_value(self):
        value = 0
        value += (self._days - self._age)
        value *= self._work_speed
        return value

    def __repr__(self):
        return f'(Person {self._name}, Age: {self._age}/{self._days}, Work speed: {self._work_speed})'


class Cart:
    resources_amount = {
        'food': 100,
        'materials': 200
    }

    def __init__(self, current_location: AbstractSector):
        self.current_location = current_location

    def cart(self, do: AbstractSector, res_type):
        if res_type != 0:
            q = -self.current_location.update_resources(res_type, -self.resources_amount[res_type])
            logging.info(f"Wyruszono z {type(self.current_location).__name__} z {res_type}: {q}")
            time.sleep(2)
            do.update_resources(res_type, q)
            self.current_location = do
            logging.info(f"Dotarto do {type(do).__name__} z {res_type}: {q}")
        else:
            logging.info(f"Wyruszono z {type(self.current_location).__name__} z niczym")
            time.sleep(2)
            self.current_location = do
            logging.info(f"Dotarto do {type(do).__name__} z niczym")


class SupplyRequest:

    def __init__(self, supply_type, sender):
        self.supply_type = supply_type
        self.sender = sender

        self.send_request()

    def send_request(self):
        logging.info(f"{type(self).__name__} przekazał request od {self.sender} o {self.supply_type}")
        carts_controller.receive_request(self)


class CartsController:
    carts_lock = threading.Lock()

    free_carts = {
        'LivingSector': Queue(),
        'MaterialSector': Queue(),
        'FoodSector': Queue()
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
                logging.info(f"{type(self).__name__} próbuje wysłać cart z {type(max_sect).__name__} do"
                             f" {type(req.sender).__name__}")
                threading.Thread(target=self.send_cart, args=(req, max_sect)).start()

    def send_cart(self, req: SupplyRequest, from_where):
        from_where_ = repr(from_where)
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

        else:
            logging.info(f"{type(self).__name__} nie udało się wysłać carta z {type(from_where).__name__} do"
                         f" {type(req.sender).__name__}")
            self.request_queue.put(req)

    def _send_cart(self, from_where, to_where, supply_type):
        used_cart = self.free_carts[repr(from_where)].get()
        cart_travel = threading.Thread(target=used_cart.cart, args=(to_where, supply_type))
        cart_travel.start()
        cart_travel.join()
        self.free_carts[repr(used_cart.current_location)].put(used_cart)

    def receive_request(self, req: SupplyRequest):
        self.request_queue.put(req)


class SectorsController:
    pass


def day_cycle():
    while True:
        logging.info("day_cycle\t\t\t : \tDay is raising!")
        daytime.set()
        time.sleep(16)
        logging.info("day_cycle\t\t\t : \tNight has come...")
        daytime.clear()
        time.sleep(8)


def start_sectors():
    logging.info("start_sectors\t\t : \tStarting processes.")
    global living_sector
    living_sector = LivingSector(inhabitants=100)
    global material_sector
    material_sector = MaterialSector(materials=199)
    global food_sector
    food_sector = FoodSector(food=1299)

    # living_sector.start()
    # material_sector.start()
    # food_sector.start()
    # living_sector.get_resources()
    # material_sector.get_resources()
    # food_sector.get_resources()

    global sectors
    sectors = [
        living_sector,
        material_sector,
        food_sector
    ]

    day = threading.Thread(target=day_cycle)
    day.start()

    global carts_controller
    carts_controller = CartsController()
    carts_controller.start()

    carts_controller.free_carts['LivingSector'].put(Cart(living_sector))

    food_sector.send_request('materials')


# start_sectors()
