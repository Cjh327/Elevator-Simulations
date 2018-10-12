"""
=== Module Description ===

This file contains two sets of algorithms: ones for generating new arrivals to
the simulation, and ones for making decisions about how elevators should move.

As with other files, you may not change any of the public behaviour (attributes,
methods) given in the starter code, but you can definitely add new attributes
and methods to complete your work here.

See the 'Arrival generation algorithms' and 'Elevator moving algorithsm'
sections of the assignment handout for a complete description of each algorithm
you are expected to implement in this file.
"""
import csv
from enum import Enum
import random
from typing import Dict, List, Optional

from entities import Person, Elevator


###############################################################################
# Arrival generation algorithms
###############################################################################
class ArrivalGenerator:
    """An algorithm for specifying arrivals at each round of the simulation.

    === Attributes ===
    max_floor: The maximum floor number for the building.
               Generated people should not have a starting or target floor
               beyond this floor.
    num_people: The number of people to generate, or None if this is left
                up to the algorithm itself.

    === Representation Invariants ===
    max_floor >= 2
    num_people is None or num_people >= 0
    """
    max_floor: int
    num_people: Optional[int]

    def __init__(self, max_floor: int, num_people: Optional[int]) -> None:
        """Initialize a new ArrivalGenerator.

        Preconditions:
            max_floor >= 2
            num_people is None or num_people >= 0
        """
        self.max_floor = max_floor
        self.num_people = num_people

    def generate(self, round_num: int) -> Dict[int, List[Person]]:
        """Return the new arrivals for the simulation at the given round.

        The returned dictionary maps floor number to the people who
        arrived starting at that floor.

        You can choose whether to include floors where no people arrived.
        """
        raise NotImplementedError


class RandomArrivals(ArrivalGenerator):
    """Generate a fixed number of random people each round.

    Generate 0 people if self.num_people is None.

    For our testing purposes, this class *must* have the same initializer header
    as ArrivalGenerator. So if you choose to to override the initializer, make
    sure to keep the header the same!

    Hint: look up the 'sample' function from random.
    """
    def __init__(self, max_floor: int, num_people: Optional[int]) -> None:
        ArrivalGenerator.__init__(self, max_floor, num_people)
        self.max_floor = max_floor
        self.num_people = num_people
        
    def generate(self, round_num: int) -> Dict[int, List[Person]]:
        #new_people = []
        newPeople = {}
        for i in range(self.num_people):
            start = random.randint(1, self.max_floor)
            target = random.randint(1, self.max_floor)
            while target == start:
                start = random.randint(1, self.max_floor)
                target = random.randint(1, self.max_floor)
            person = Person(start, target, 0)
            if start in newPeople.keys():
                newPeople[start].append(person)
            else:
                newPeople[start] = [person]
        return newPeople


class FileArrivals(ArrivalGenerator):
    """Generate arrivals from a CSV file.
    """
    file_name: str
    def __init__(self, max_floor: int, filename: str) -> None:
        """Initialize a new FileArrivals algorithm from the given file.

        The num_people attribute of every FileArrivals instance is set to None,
        since the number of arrivals depends on the given file.

        Precondition:
            <filename> refers to a valid CSV file, following the specified
            format and restrictions from the assignment handout.
        """
        ArrivalGenerator.__init__(self, max_floor, None)
        self.file_name = filename
        
    def generate(self, round_num: int) -> Dict[int, List[Person]]:
        # We've provided some of the "reading from csv files" boilerplate code
        # for you to help you get started.
        #new_people = []
        dic = {}
        with open(self.file_name) as csvfile:
            reader = csv.reader(csvfile)
            for line in reader:
                # TODO: complete this. <line> is a list of strings corresponding
                # to one line of the original file.
                # You'll need to convert the strings to ints and then process
                # and store them.
                if round_num == int(line[0]):
                    for i in range(1, len(line) - 1, 2):
                        start = int(line[i])
                        target = int(line[i + 1])
                        person = Person(start, target, 0)
                        if start in dic.keys():
                            dic[start].append(person)
                        else:
                            dic[start] = [person]
        return dic
                


###############################################################################
# Elevator moving algorithms
###############################################################################
class Direction(Enum):
    """
    The following defines the possible directions an elevator can move.
    This is output by the simulation's algorithms.

    The possible values you'll use in your Python code are:
        Direction.UP, Direction.DOWN, Direction.STAY
    """
    UP = 1
    STAY = 0
    DOWN = -1


class MovingAlgorithm:
    """An algorithm to make decisions for moving an elevator at each round.
    """
    def move_elevators(self,
                       elevators: List[Elevator],
                       waiting: Dict[int, List[Person]],
                       max_floor: int) -> List[Direction]:
        """Return a list of directions for each elevator to move to.

        As input, this method receives the list of elevators in the simulation,
        a dictionary mapping floor number to a list of people waiting on
        that floor, and the maximum floor number in the simulation.

        Note that each returned direction should be valid:
            - An elevator at Floor 1 cannot move down.
            - An elevator at the top floor cannot move up.
        """
        raise NotImplementedError
        


class RandomAlgorithm(MovingAlgorithm):
    """A moving algorithm that picks a random direction for each elevator.
    """
    def move_elevators(self,
                       elevators: List[Elevator],
                       waiting: Dict[int, List[Person]],
                       max_floor: int) -> List[Direction]:
        import random
        directions = []
        for elevator in elevators:
            direction = random.sample([Direction.DOWN, Direction.STAY, Direction.UP], 1)[0]
            while (elevator.curFloor == 1 and direction == Direction.DOWN) or \
            (elevator.curFloor == max_floor and direction == Direction.UP):
                direction = random.sample([Direction.DOWN, Direction.STAY, Direction.UP], 1)[0]
            directions.append(direction)
            print(direction)
        return directions

class PushyPassenger(MovingAlgorithm):
    """A moving algorithm that preferences the first passenger on each elevator.

    If the elevator is empty, it moves towards the *lowest* floor that has at
    least one person waiting, or stays still if there are no people waiting.

    If the elevator isn't empty, it moves towards the target floor of the
    *first* passenger who boarded the elevator.
    """
    def move_elevators(self,
                       elevators: List[Elevator],
                       waiting: Dict[int, List[Person]],
                       max_floor: int) -> List[Direction]:
        directions = []
        waiting_people = max_floor
        if len(waiting) == 0:
            waiting_people = -1
        else:
            for floor in range(1, max_floor + 1):
                if floor in waiting.keys():
                    if len(waiting[floor]) > 0:
                        waiting_people = floor
                        break
        for elevator in elevators:
            if len(elevator.passengers) == 0:
                if len(waiting) == 0 or waiting_people == elevator.curFloor:
                    directions.append(Direction.STAY)
                elif waiting_people > elevator.curFloor:
                    directions.append(Direction.UP)
                else:
                    directions.append(Direction.DOWN)
            else:
                if elevator.passengers[0].target > elevator.curFloor:
                    directions.append(Direction.UP)
                else:
                    directions.append(Direction.DOWN)
        return directions


class ShortSighted(MovingAlgorithm):
    """A moving algorithm that preferences the closest possible choice.

    If the elevator is empty, it moves towards the *closest* floor that has at
    least one person waiting, or stays still if there are no people waiting.

    If the elevator isn't empty, it moves towards the closest target floor of
    all passengers who are on the elevator.

    In this case, the order in which people boarded does *not* matter.
    """
    def move_elevators(self,
                       elevators: List[Elevator],
                       waiting: Dict[int, List[Person]],
                       max_floor: int) -> List[Direction]:
        directions = []
        for elevator in elevators:
            if len(elevator.passengers) == 0:
                nextFloor = 0
                for floor in waiting.keys():
                    assert len(waiting[floor]) > 0
                    if nextFloor == 0 or abs(floor - elevator.curFloor) < abs(nextFloor - elevator.curFloor):
                        nextFloor = floor
                if nextFloor == 0:
                    directions.append(Direction.STAY)
                elif nextFloor > elevator.curFloor:
                    directions.append(Direction.UP)
                elif nextFloor < elevator.curFloor:
                    directions.append(Direction.DOWN)
                else:
                    directions.append(Direction.STAY)
            else:
                nextFloor = 0
                for person in elevator.passengers:
                    if nextFloor == 0 or abs(person.target - elevator.curFloor) < abs(closest - elevator.curFloor):
                        nextFloor = person.target
                if nextFloor == 0:
                    directions.append(Direction.STAY)
                elif nextFloor > elevator.curFloor:
                    directions.append(Direction.UP)
                elif nextFloor < elevator.curFloor:
                    directions.append(Direction.DOWN)
                else:
                    directions.append(Direction.STAY)
        return directions


if __name__ == '__main__':
    # Don't forget to check your work regularly with python_ta!
    import python_ta
    python_ta.check_all(config={
        'allowed-io': ['__init__'],
        'extra-imports': ['entities', 'random', 'csv', 'enum'],
        'max-nested-blocks': 4,
        'disable': ['R0201']
    })
