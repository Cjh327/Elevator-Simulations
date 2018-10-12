"""
=== Module description ===
This contains the main Simulation class that is actually responsible for
creating and running the simulation. You'll also find the function `sample_run`
here at the bottom of the file, which you can use as a starting point to run
your simulation on a small configuration.

Note that we have provided a fairly comprehensive list of attributes for
Simulation already. You may add your own *private* attributes, but should not
remove any of the existing attributes.
"""
# You may import more things from these modules (e.g., additional types from
# typing), but you may not import from any other modules.
from typing import Dict, List, Any

import algorithms
from algorithms import Direction
from entities import Person, Elevator
from visualizer import Visualizer


class Simulation:
    """The main simulation class.

    === Attributes ===
    arrival_generator: the algorithm used to generate new arrivals.
    elevators: a list of the elevators in the simulation
    moving_algorithm: the algorithm used to decide how to move elevators
    num_floors: the number of floors
    visualizer: the Pygame visualizer used to visualize this simulation
    waiting: a dictionary of people waiting for an elevator
             (keys are floor numbers, values are the list of waiting people)
    """
    arrival_generator: algorithms.ArrivalGenerator
    elevators: List[Elevator]
    moving_algorithm: algorithms.MovingAlgorithm
    num_floors: int
    visualizer: Visualizer
    waiting: Dict[int, List[Person]]
    
    statistics: Dict[str, int]

    def __init__(self,
                 config: Dict[str, Any]) -> None:
        """Initialize a new simulation using the given configuration."""
        # Initialize the visualizer.
        # Note that this should be called *after* the other attributes
        # have been initialized.
        self.statistics = {}
        #self.statistics['num_iterations'] = config['num_elevators']
        self.statistics['total_people'] = 0
        self.statistics['people_completed'] = 0
        self.statistics['max_time'] = 0
        self.statistics['min_time'] = float("inf")
        self.statistics['avg_time'] = 0
        self.statistics['total_time'] = 0
        self.arrival_generator = config['arrival_generator']
        self.num_floors = config['num_floors']
        self.moving_algorithm = config['moving_algorithm']
        self.waiting = {}
        for i in range(self.num_floors):
            self.waiting[i] = []
        self.elevators = []
        for i in range(config['num_elevators']):
            self.elevators.append(Elevator([], \
                                           config['num_floors'], config['elevator_capacity']))
        self.moving_algorithm = config['moving_algorithm']
        self.waiting = {}
        self.visualizer = Visualizer(self.elevators,  # should be self.elevators
                                     self.num_floors,
                                     config['visualize'])
        
        
    ############################################################################
    # Handle rounds of simulation.
    ############################################################################
    def run(self, num_rounds: int) -> Dict[str, Any]:
        """Run the simulation for the given number of rounds.

        Return a set of statistics for this simulation run, as specified in the
        assignment handout.

        Precondition: num_rounds >= 1.

        Note: each run of the simulation starts from the same initial state
        (no people, all elevators are empty and start at floor 1).
        """
        self.statistics['num_iterations'] = num_rounds
        for i in range(num_rounds):
            self.visualizer.render_header(i)

            # Stage 1: generate new arrivals
            self._generate_arrivals(i)

            # Stage 2: leave elevators
            self._handle_leaving()

            # Stage 3: board elevators
            self._handle_boarding()

            # Stage 4: move the elevators using the moving algorithm
            self._move_elevators()

            # Pause for 1 second
            self.visualizer.wait(1)
        if self.statistics['people_completed'] == 0:
            self.statistics['avg_time'] = -1
            self.statistics['max_time'] = -1
            self.statistics['min_time'] = -1
        else:
            self.statistics['avg_time'] = self.statistics['total_time'] // self.statistics['people_completed']

        return self._calculate_stats()

    def _generate_arrivals(self, round_num: int) -> None:
        newPeople = self.arrival_generator.generate(round_num)
        for floor in newPeople:
            self.statistics['total_people'] += len(newPeople[floor])
        for floor, people in newPeople.items():
            if floor in self.waiting.keys():
                self.waiting[floor] = self.waiting[floor] + people
            else:
                self.waiting[floor] = people
        self.visualizer.show_arrivals(newPeople)

    def _handle_leaving(self) -> None:
        """Handle people leaving elevators."""
        for i, elevator in enumerate(self.elevators):
            for j, passenger in enumerate(elevator.passengers):
                if passenger.target == elevator.curFloor:
                    if passenger.wait_time > self.statistics['max_time']:
                        self.statistics['max_time'] = passenger.wait_time
                    if passenger.wait_time < self.statistics['min_time']:
                        self.statistics['min_time'] = passenger.wait_time
                    self.elevators[i].disembarking(j)
                    self.visualizer.show_disembarking(passenger, self.elevators[i])
                    self.statistics['total_time'] += passenger.wait_time
                    self.statistics['people_completed'] += 1
                    

    def _handle_boarding(self) -> None:
        """Handle boarding of people and visualize."""
        for _, elevator in enumerate(self.elevators):
            if elevator.curFloor in self.waiting.keys():
                pop_list = []
                for j, wait_person in enumerate(self.waiting[elevator.curFloor]):
                    if elevator.passenNum < elevator.capacity:
                        elevator.boarding(wait_person)
                        pop_list.append(j)
                        self.visualizer.show_boarding(wait_person, elevator)
                cnt = 0
                for j in pop_list:
                    self.waiting[elevator.curFloor].pop(j - cnt)
                    cnt += 1
                if len(self.waiting[elevator.curFloor]) == 0:
                    self.waiting.pop(elevator.curFloor)
                    
                    
            
    def _move_elevators(self) -> None:
        """Move the elevators in this simulation.

        Use this simulation's moving algorithm to move the elevators.
        """
        directions = self.moving_algorithm.move_elevators(self.elevators, self.waiting, self.num_floors)
        for i, direction in enumerate(directions):
            if direction == Direction.DOWN:
                self.elevators[i].moveDown()
            elif direction == Direction.UP:
                self.elevators[i].moveUp()
        self.visualizer.show_elevator_moves(self.elevators, directions)
        for i, elevator in enumerate(self.elevators):
            for j, _ in enumerate(elevator.passengers):
                self.elevators[i].passengers[j].wait_time += 1
        for floor in self.waiting:
            for i in range(len(self.waiting[floor])):
                self.waiting[floor][i].wait_time += 1

    ############################################################################
    # Statistics calculations
    ############################################################################
    def _calculate_stats(self) -> Dict[str, int]:
        """Report the statistics for the current run of this simulation.
        
        return {
            'num_iterations': 0,
            'total_people': 0,
            'people_completed': 0,
            'max_time': 0,
            'min_time': 0,
            'avg_time': 0
        }"""
        return self.statistics


def sample_run() -> Dict[str, int]:
    """Run a sample simulation, and return the simulation statistics."""
    config = {
        'num_floors': 6,
        'num_elevators': 6,
        'elevator_capacity': 3,
        'num_people_per_round': 2,
        # Random arrival generator with 6 max floors and 2 arrivals per round.
        #'arrival_generator': algorithms.RandomArrivals(6, 2),
        'arrival_generator': algorithms.FileArrivals(6, 'sample_arrivals.csv'),
        #'moving_algorithm': algorithms.RandomAlgorithm(),
        'moving_algorithm': algorithms.ShortSighted(),
        'visualize': True
    }

    sim = Simulation(config)
    stats = sim.run(15)
    return stats

if __name__ == '__main__':
    # Uncomment this line to run our sample simulation (and print the
    # statistics generated by the simulation).
    print(sample_run())

    import python_ta
    python_ta.check_all(config={
        'extra-imports': ['entities', 'visualizer', 'algorithms', 'time'],
        'max-nested-blocks': 4
    })