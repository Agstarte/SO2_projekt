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
    _list_of_people = list()

    def __init__(self, inhabitants=0, materials=0, food=0):
        logging.info("Creating an object of %s.", type(self).__name__)
        if inhabitants != 0 and type(self) is not LivingSector:
            logging.error("Sector other than LivingSector cannot have inhabitants initially.")
        # self._inhabitants = inhabitants

        for i in range(inhabitants):
            self._list_of_people.append(Person(i))

        self._materials = materials
        self._food = food
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
            f'---------------------------------------\n'
            f'Sector \t\t:\t {type(self).__name__}\n'
            f'Inhabitants :\t {self._list_of_people}\n'
            f'Materials \t:\t {self._materials}\n'
            f'Food \t\t:\t {self._food}'
        )
        return self._inhabitants, self._materials, self._food

    # def update_inhabitants(self, quantity=0):
    #     logging.info("Updating a quantity of inhabitants in %s by %i.", type(self).__name__, quantity)
    #     self._inhabitants += quantity

    def update_materials(self, quantity=0):
        logging.info("Updating a quantity of materials in %s by %i.", type(self).__name__, quantity)
        self._materials += quantity

    def update_food(self, quantity=0):
        logging.info("Updating a quantity of food in %s by %i.", type(self).__name__, quantity)
        self._food += quantity

    def get_type(self):
        return type(self).__name__

    def take_people(self, new_people: list):
        logging.info(f'Adding {new_people} to {type(self).__name__}')
        self._list_of_people += new_people

    def send_people(self):
        logging.info(f'Sending all people from {type(self).__name__}')
        temp = self._list_of_people
        self._list_of_people = list()
        return temp

    def process(self):
        pass


class LivingSector(AbstractSector):
    # todo zarządzanie ludźmi - proces
    def startup(self):
        for n in range(self._inhabitants):
            self._list_of_people.append(Person(n))

    def process(self):
        while True:
            daytime.wait()
            logging.info("living_sector\t\t : \tSend the people off.")
            people_sent.release()
            people_sent.release()

            while daytime.isSet():
                pass
            people_sent.acquire()
            people_sent.acquire()
            logging.info("living_sector\t\t : \tFeed people.")


class MaterialSector(AbstractSector):
    # todo wytwarzanie materiałów - proces
    def process(self):
        while True:
            daytime.wait()

            people_sent.acquire()
            logging.info("material_sector\t : \tGet people.")
            while daytime.isSet():
                logging.info("material_sector\t : \tProducing materials.")
                time.sleep(2)
            logging.info("material_sector\t : \tSend off people.")
            time.sleep(0.1)
            people_sent.release()


class FoodSector(AbstractSector):
    # todo wytwarzanie jedzenia - proces
    def process(self):
        while True:
            daytime.wait()

            people_sent.acquire()
            logging.info("food_sector\t\t : \tGet people.")
            while daytime.isSet():
                logging.info("food_sector\t\t : \tProducing food.")
                time.sleep(2)
            logging.info("food_sector\t\t : \tSend off people.")
            time.sleep(0.1)
            people_sent.release()


class Person(object):
    # todo starzenie się, jedzenie + to ile ma siły w zależności ile zjadł
    _age = 0
    _is_alive = True

    def __init__(self, name=0):
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


class Cart:

    def __init__(self, current_location):
        self.current_location = current_location

    def cart(self, do: AbstractSector, co: int):
        logging.info(f"Wyruszono z {type(self.current_location).__name__} z {co}")
        self.current_location.ile_update(-co)
        time.sleep(2)
        do.ile_update(co)
        self.current_location = do
        logging.info(f"Dotarto do {type(do).__name__} z {co}")


class SupplyRequest:
    def __init__(self, supply_type, sender):
        self.supply_type = supply_type
        self.sender = sender

        self.send_request()

    def send_request(self):
        logging.info(f"{type(self).__name__} przekazał request od {self.sender}")
        carts_controller.receive_request(self)


class CartsController:
    carts_lock = threading.Lock()

    free_carts = {
        'sector1': Queue(),
        'sector2': Queue(),
        'sector3': Queue()
    }

    request_queue = Queue()

    def main_loop(self):
        while True:
            if self.request_queue.qsize() > 0:
                req = self.request_queue.get()
                max_sect = None
                for sect in sectors:
                    if sect != req.sender:
                        if sect.ile >= req.supply_type:
                            if max_sect is None:
                                max_sect = sect
                            elif sect.ile > max_sect.ile:
                                max_sect = sect
                logging.info(f"{type(self).__name__} próbuje wysłać cart z {type(max_sect).__name__} do"
                             f" {type(req.sender).__name__}")
                threading.Thread(target=self.send_cart, args=(req, max_sect)).start()

    def send_cart(self, req: SupplyRequest, from_where):
        from_where_ = repr(from_where)

        if self.free_carts[from_where_].qsize() > 0:
            self._send_cart(from_where, req.sender, req.supply_type)

        elif self.free_carts[repr(living_sector)].qsize() > self.free_carts[repr(material_sector)].qsize():
            if self.free_carts[repr(living_sector)].qsize() > self.free_carts[repr(food_sector)].qsize():
                if self.free_carts[repr(living_sector)].qsize() > 0:
                    self._send_cart(living_sector, from_where, 0)
                    self._send_cart(from_where, req.sender, req.supply_type)

            elif self.free_carts[repr(food_sector)].qsize() > 0:
                self._send_cart(food_sector, from_where, 0)
                self._send_cart(from_where, req.sender, req.supply_type)

        elif self.free_carts[repr(material_sector)].qsize() > 0:
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

    global living_sector, material_sector, food_sector
    living_sector = LivingSector(inhabitants=100)
    material_sector = MaterialSector(materials=199)
    food_sector = FoodSector(food=1299)

    living_sector.start()
    material_sector.start()
    food_sector.start()

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
