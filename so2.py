import random
import logging
import time

format = "%(asctime)s: %(message)s"
logging.basicConfig(format=format, level=logging.INFO,
                    datefmt="%H:%M:%S")


# logging.getLogger().setLevel(logging.DEBUG)

# ogólnie todo - wszystkie todo poniżej + klasa/thread ogarniający przepływ wózków i ludzi

class AbstractSector(object):
    # todo jakiekolwiek wspólne funkcje tutaj

    def __init__(self, inhabitants=0, materials=0, food=0):
        logging.info("Creating an object of %s.", type(self).__name__)
        self._inhabitants = inhabitants
        self._materials = materials
        self._food = food
        if type(self) is AbstractSector:
            raise NotImplementedError("Can't create an object of an abstract class.")

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


class LivingSector(AbstractSector):
    # todo ogarnianie ludzi - proces
    def a(self):
        pass


class MaterialSector(AbstractSector):
    # todo wytwarzanie materiałów - proces
    def a(self):
        pass


class FoodSector(AbstractSector):
    # todo wytwarzanie jedzenia - proces
    def a(self):
        pass


class Person(object):
    # todo starzenie się, jedzenie + to ile ma siły w zależności ile zjadł
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

    def print_person(self):
        print(
            f'Person \t\t:\t {self._name}\n'
            f'Work speed \t:\t {self._work_speed}\n'
            f'Days \t\t:\t {self._days}\n'
        )


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
a = LivingSector(inhabitants=100)
time.sleep(0.1)
a.get_resources()

time.sleep(0.1)

a.update_inhabitants(-29)
time.sleep(0.1)
a.get_resources()

time.sleep(0.1)

a.update_materials(2334)
time.sleep(0.1)
a.get_resources()

time.sleep(0.1)

a.update_food(2909)
time.sleep(0.1)
a.get_resources()

time.sleep(0.1)

a = MaterialSector(materials=199)
time.sleep(0.1)
a.get_resources()

time.sleep(0.1)

a = FoodSector(food=1299)
time.sleep(0.1)
a.get_resources()
