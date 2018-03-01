import sys
import os
import numpy as np

current_dir = os.path.dirname(os.path.abspath(__file__))
output_file = f"{current_dir}/output.txt"

def clear_output():
    with open(output_file, "w") as f:
        f.write("")

def append_ride(vehicle):
    """Appends rides to the output file"""
    with open(output_file, "a") as f:
        f.write(f"{len(vehicle.handled_rides)} {' '.join([str(ride.index) for ride in vehicle.handled_rides])}\n")

def output_is_valid():
    """Returns True if the output is valid.
    Raises nooby runtime-errors if it's not. (indicating why)"""
    with open(output_file, "r") as f:
        lines = f.readlines()

    if not lines:
        raise RuntimeError("The output file seems to be empty.")

    all_rides = []
    for line in lines:
        line_array = line.split(" ")
        count = int(line_array[0])
        rides = [int(r) for r in line_array[1:]]

        if len(rides) != count:
            raise RuntimeError("Wrong count for the given amount of rides")

        for ride in rides:
            if ride in all_rides:
                raise RuntimeError("Ride was already given to a different vehicle")
            else:
                all_rides.append(ride)

    return True # If all is good and well.

class Point:
    x = 0
    y = 0

    def __init__(self, x, y):
        self.x = x
        self.y = y

class Ride:
    earliest_start = 0
    latest_finish = 0
    _from = None
    _to = None
    length = 0
    index = 0

    def __init__(self, row, index):
        parts = row.split(' ')

        self.index = index
        self._from = Point(int(parts[0]), int(parts[1]))
        self._to = Point(int(parts[2]), int(parts[3]))
        self.earliest_start = int(parts[4])
        self.latest_finish = int(parts[5])

        self.length = abs(self._to.x - self._from.x)
        self.length += abs(self._to.y - self._from.y)

    def on_time(self, step):
        return self.length + step <= self.latest_finish

class Vehicle:
    pos = Point(0,0)
    start_ride = False
    next_available_turn = 0
    current_ride = None
    index = 0
    handled_rides = None
    ride_done = False
    heading_to = False

    current_step = 0

    def __init__(self, index):
        self.handled_rides = []
        self.ride_done = True
        self.index = index

    def calc_steps(self, intersection):
        diff = 0
        if(intersection.x < self.pos.x):
            diff = self.pos.x - intersection.x
        else:
            diff = intersection.x - self.pos.x

        if(intersection.y < self.pos.y):
            diff += self.pos.y - intersection.y
        else:
            diff += intersection.y - self.pos.y

        return diff

    def handle_ride(self, ride):
        self.ride_done = False
        self.start_ride = False

        self.handled_rides.append(ride)
        self.current_ride = ride

        # Calculate the next moment it is ready again
        self.next_available_turn = self.current_step + self.calc_steps(ride._from)
        self.pos = ride._from
        self.next_available_turn += self.calc_steps(ride._to)
        self.pos = ride._to

        #print("Vehicle %d got ride %d" % (self.index, ride.index))

    def sort_by_earliest(self, rides):
        return

    def get_distance(self, _from):
        return abs(self.pos.x - _from.x) + abs(self.pos.y - _from.y)

    def get_closest_ride(self, rides):
        min_length = 1e6
        closest_ride = None

        rides.sort(key=lambda ride: (ride.earliest_start, ride.length))

        for ride in rides:
            distance = self.get_distance(ride._from)
            if (distance) < min_length:
                min_length = distance
                closest_ride = ride

        return closest_ride

    def is_available(self):
        return self.ride_done

    def do_step(self):
        self.current_step += 1
        if(self.next_available_turn < self.current_step):
            #print("Available again")
            self.ride_done = True

class Simulation:
    current_step = 0
    rides = None
    vehicles = []
    rides = []
    all_rides = []
    short_rides = []
    rows = 0
    columns = 0
    bonus = 0
    max_steps = 0

    total_rides = 0

    def __init__(self, file):
        with open(file) as f:
            lines = [line.rstrip('\n') for line in f]

            parts = lines[0].split(' ')
            self.rows = int(parts[0])
            self.columns = int(parts[1])

            #TODO Loop vehicels index: 2

            index = 0
            for x in range(0, int(parts[2])):
                self.vehicles.append(Vehicle(index))
                index+=1

            self.bonus = int(parts[4])
            self.max_steps = int(parts[5])

            lines = lines[1:]

            index = 0
            for line in lines:
                self.all_rides.append(Ride(line, index))
                index += 1

            self.short_rides, self.long_rides = self.split_rides(self.all_rides)
            self.all_rides = len(self.rides) + len(self.long_rides)

    def split_rides(self, rides):
        rides.sort(key=lambda x: x.length, reverse=False)
        total_len = len(rides)
        short_rides = rides[0:total_len-1000]
        long_rides = rides[total_len-1000+1:]
        return (short_rides, long_rides)
    def remove_ride(self, index):
        for ride in self.rides:
            if ride.index == index:
                self.rides.remove(ride)

    def ride(self):
        for step in range(0, self.max_steps):
            for ride in self.short_rides:
                if ride.earliest_start <= step:
                    self.rides.append(ride)
                    self.short_rides.remove(ride)

                if not ride.on_time(step):
                    self.short_rides.remove(ride)

            if len(self.rides) < len(self.vehicles):
                for ride in self.long_rides:
                    if ride.earliest_start <= step:
                        self.rides.append(ride)
                        self.long_rides.remove(ride)

                    if not ride.on_time(step):
                        self.long_rides.remove(ride)
            for v in self.vehicles:
                if v.is_available() and len(self.rides) > 0:
                    ride = v.get_closest_ride(self.rides)
                    self.rides.remove(ride)
                    v.handle_ride(ride)
                    print("%d of %d rides left" % (len(self.rides), self.total_rides))

                v.do_step()

        for v in self.vehicles:
            append_ride(v)

if __name__ == '__main__':
    open(output_file, "w")
    sim = Simulation(sys.argv[1])
    sim.ride()
