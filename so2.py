import random
import logging
import time
import threading

format = "%(asctime)s: %(message)s"
logging.basicConfig(format=format, level=logging.INFO,
                    datefmt="%H:%M:%S")

daytime = threading.Event()
people_sent = threading.Semaphore(0)


# logging.getLogger().setLevel(logging.DEBUG)

# ogólnie todo - wszystkie todo poniżej + klasa/thread ogarniający przepływ wózków i ludzi

class AbstractSector(object):
    # todo jakiekolwiek wspólne funkcje tutaj
    _list_of_people = list()

    def __init__(self, inhabitants=0, materials=0, food=0):
        logging.info("Creating an object of %s.", type(self).__name__)
        if inhabitants != 0 and type(self) is not LivingSector:
            logging.error("Sector other than LivingSector cannot have inhabitants initially.")
        self._inhabitants = inhabitants
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
            f'Inhabitants :\t {self._inhabitants}\n'
            f'Materials \t:\t {self._materials}\n'
            f'Food \t\t:\t {self._food}'
        )
        return self._inhabitants, self._materials, self._food

    def update_inhabitants(self, quantity=0):
        logging.info("Updating a quantity of inhabitants in %s by %i.", type(self).__name__, quantity)
        self._inhabitants += quantity

    def update_materials(self, quantity=0):
        logging.info("Updating a quantity of materials in %s by %i.", type(self).__name__, quantity)
        self._materials += quantity

    def update_food(self, quantity=0):
        logging.info("Updating a quantity of food in %s by %i.", type(self).__name__, quantity)
        self._food += quantity

    def get_type(self):
        return type(self).__name__

    def take_people(self, new_people: list):
        self._list_of_people += new_people

    def send_people(self):
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


class Cart(object):
    # todo podróż i dobieranie operatorów + przeworzenie towarów

    def __init__(self, capacity=10, operators_number=1, name=0):
        logging.info("Creating an object of %s.", type(self).__name__)
        self._capacity = capacity
        self._operators_number = operators_number
        self._name = name
        self._operators = []

    def add_operator(self, operator: Person):
        if len(self._operators) < self._operators_number:
            logging.info("Adding an operator - Person %s - to the cart %s.", operator.get_name(), self._name)
            self._operators.append(operator)
            return True
        else:
            logging.info("Cannot add an operator - Person %s - to the cart %s. Cart is full.", operator.get_name(),
                         self._name)
            return False

    def release_operators(self):
        if len(self._operators) > 0:
            released_operators = self._operators.copy()
            self._operators.clear()
            released_operators_str = ''
            for released_operator in released_operators:
                released_operators_str += str(released_operator.get_name()) + ', '
            logging.info("Release operators - Person(s) %s - from the cart %s.", released_operators_str[:-2],
                         self._name)
            return released_operators
        else:
            logging.info("The cart %s is empty.", self._name)
            return []

    def move_cart(self, origin: AbstractSector, destination: AbstractSector):
        if len(self._operators) != self._operators_number:
            logging.info("Cart %s has too less operators.", self._name)
            # TODO jakiś request?
            return False
        else:
            logging.info("Cart %s travels from %s to %s.", self._name, origin.get_type(), destination.get_type())
            pass
            # TODO podróż
            return True


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
    living_sector = LivingSector(inhabitants=100)
    material_sector = MaterialSector(materials=199)
    food_sector = FoodSector(food=1299)

    living_sector.start()
    material_sector.start()
    food_sector.start()

    day = threading.Thread(target=day_cycle)
    day.start()


# living_sector = LivingSector()
# material_sector = MaterialSector()
#
# people = list()
# for i in range(6):
#     people.append(Person(name=i))
#
# for person in people:
#     person.print_person()
#
# carts = list()
# for i in range(3):
#     cart = Cart(name=i, operators_number=2)
#     cart.add_operator(people[i])
#     cart.add_operator(people[5 - i])
#     cart.add_operator(people[3])
#     carts.append(cart)
#
# for cart in carts:
#     cart.move_cart(living_sector, material_sector)
#     cart.move_cart(material_sector, living_sector)


# abstract = Abstract()
# a = LivingSector(inhabitants=100)
# time.sleep(0.1)
# a.get_resources()
#
# time.sleep(0.1)
#
# a.update_inhabitants(-29)
# time.sleep(0.1)
# a.get_resources()
#
# time.sleep(0.1)
#
# a.update_materials(2334)
# time.sleep(0.1)
# a.get_resources()
#
# time.sleep(0.1)
#
# a.update_food(2909)
# time.sleep(0.1)
# a.get_resources()
#
# time.sleep(0.1)
#
# a = MaterialSector(materials=199)
# time.sleep(0.1)
# a.get_resources()
#
# time.sleep(0.1)
#
# a = FoodSector(food=1299)
# time.sleep(0.1)
# a.get_resources()

# start_sectors()

a = LivingSector(inhabitants=10)

people = a.send_people()
for person in people:
    for i in range(person.get_days()):
        person.age_up()
    person.print_person()
