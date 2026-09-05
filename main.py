from parser import MapParser
from path.path import Pathfinder
from scheduler import ReservationTable, DroneScheduler, Scheduler
from simulation import Simulator
from visualization.visualization import Visualizer


def main() -> None:
    try:
        parser = MapParser("test_maps/test2.txt")
        map, drones = parser.parse()
        path = Pathfinder(map)
        rtable = ReservationTable(map)
        htable = path.distances_to(map.end.name)
        dscheduler = DroneScheduler(map, rtable, htable)
        scheduler = Scheduler(dscheduler)
        sim = Simulator(map, scheduler, drones)
        moves = sim.extract_moves()
        for i in range(len(moves)):
            print(f"{i}: {moves[i]}")
        v = Visualizer(map, sim.schedule)
        v.run()
    except Exception as e:
        print(e)
        exit()


if __name__ == "__main__":
    main()
