"""
=== Module description ===
This module contains classes for the two "basic" entities in this simulation:
people and elevators. We have provided basic outlines of these two classes
for you; you are responsible for implementing these two classes so that they
work with the rest of the simulation.

You may NOT change any existing attributes, or the interface for any public
methods we have provided. However, you can (and should) add new attributes,
and of course you'll have to implement the methods we've provided, as well
as add your own methods to complete this assignment.

Finally, note that Person and Elevator each inherit from a kind of sprite found
in sprites.py; this is to enable their instances to be visualized properly.
You may not change sprites.py, but are responsible for reading the documentation
to understand these classes, as well as the abstract methods your classes must
implement.
"""
#from __future__ import annotations
from typing import List
from sprites import PersonSprite, ElevatorSprite


class Person(PersonSprite):
    """A person in the elevator simulation.

    === Attributes ===
    start: the floor this person started on
    target: the floor this person wants to go to
    wait_time: the number of rounds this person has been waiting

    === Representation invariants ===
    start >= 1
    target >= 1
    wait_time >= 0
    """
    start: int
    target: int
    wait_time: int
    
    def __init__(self, start: int, target: int, wait_time: int) -> None:
        self.start = start
        self.target = target
        self.wait_time = wait_time
        PersonSprite.__init__(self)
        
    def get_anger_level(self) -> int:
        if self.wait_time <= 2:
            return 0
        elif self.wait_time <= 4:
            return 1
        elif self.wait_time <= 6:
            return 2
        elif self.wait_time <= 8:
            return 3
        else:
            return 4
        """Return this person's anger level.

        A person's anger level is based on how long they have been waiting
        before reaching their target floor.
            - Level 0: waiting 0-2 rounds
            - Level 1: waiting 3-4 rounds
            - Level 2: waiting 5-6 rounds
            - Level 3: waiting 7-8 rounds
            - Level 4: waiting >= 9 rounds
        """

class Elevator(ElevatorSprite):
    """An elevator in the elevator simulation.

    Remember to add additional documentation to this class docstring
    as you add new attributes (and representation invariants).

    === Attributes ===
    passengers: A list of the people currently on this elevator

    === Representation invariants ===
    """
    passengers: List[Person]
    passenNum: int
    capacity: int
    maxFloor: int
    curFloor: int
    
    def __init__(self, passengers: List[Person], maxFloor: int, capacity: int) -> None:
        self.passengers = passengers
        self.curFloor = 1
        self.maxFloor = maxFloor
        self.capacity = capacity
        self.passenNum = 0
        ElevatorSprite.__init__(self)

    def fullness(self) -> float:
        return float(self.passenNum) / self.capacity

    def moveUp(self):
        self.curFloor += 1
    
    def moveDown(self):
        self.curFloor -= 1
        
    def boarding(self, person: Person):
        self.passengers.append(person)
        self.passenNum += 1
        
    def disembarking(self, i):
        self.passengers.pop(i)
        self.passenNum -= 1

if __name__ == '__main__':
    import python_ta
    python_ta.check_all(config={
        'extra-imports': ['sprites'],
        'max-nested-blocks': 4
    })
