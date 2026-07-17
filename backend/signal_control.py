import time
import logging
from collections import deque
from threading import Lock

# Configure logging
logger = logging.getLogger(__name__)

class SignalController:
    def __init__(self):
        self.last_signal_change = time.time()
        self.visited_roads = deque(maxlen=4)
        self.current_green_road = None
        self.road_timers = {
            "north": 30,
            "south": 30,
            "east": 30,
            "west": 30
        }
        self.min_green_time = 10
        self.max_green_time = 60
        self.vehicle_factor = 2
        self.yellow_duration = 5  # 5 seconds for yellow phase
        self.is_initialized = False
        self.lock = Lock()

    def get_next_road(self, vehicle_counts, wait_times):
        try:
            valid_roads = ["north", "south", "east", "west"]
            vehicle_counts = {road: max(0, count) for road, count in vehicle_counts.items() if road in valid_roads}
            wait_times = {road: max(0, wait) for road, wait in wait_times.items() if road in valid_roads}

            for road in valid_roads:
                if road not in vehicle_counts:
                    vehicle_counts[road] = 0
                if road not in wait_times:
                    wait_times[road] = 0

            unvisited_roads = [road for road in valid_roads if road not in self.visited_roads]
            if not unvisited_roads:
                logger.info("All roads visited, resetting visited_roads and enforcing round-robin")
                self.visited_roads.clear()
                unvisited_roads = valid_roads  # Start a new cycle

            scores = {road: vehicle_counts[road] + wait_times[road] * 0.1 for road in unvisited_roads}
            if not scores:
                scores = {road: vehicle_counts[road] + wait_times[road] * 0.1 for road in valid_roads}

            logger.debug(f"Scores for road selection: {scores}")
            next_road = max(scores, key=scores.get)
            logger.info(f"Selected next road: {next_road} with score {scores[next_road]}")
            return next_road
        except Exception as e:
            logger.error(f"Error in get_next_road: {str(e)}")
            return "north"

    def calculate_green_time(self, vehicle_count):
        try:
            vehicle_count = max(0, int(vehicle_count))
            green_time = min(max(self.min_green_time, vehicle_count * self.vehicle_factor), self.max_green_time)
            logger.debug(f"Calculated green time for {vehicle_count} vehicles: {green_time} seconds")
            return green_time
        except (ValueError, TypeError) as e:
            logger.error(f"Error calculating green time: {str(e)}")
            return self.min_green_time

    def decide_signal(self, vehicle_counts):
        with self.lock:
            try:
                # If not initialized (no images processed yet), return neutral state
                if not self.is_initialized:
                    signals = {"north": "", "south": "", "west": "", "east": ""}
                    timing_info = {
                        "current_green": "",
                        "visited_roads": [],
                        "remaining_time": 0
                    }
                    logger.debug("Signals not initialized, returning neutral state")
                    return signals, timing_info

                signals = {"north": "red", "south": "red", "west": "red", "east": "red"}  # Initialize all to red
                current_time = time.time()
                elapsed_time = current_time - self.last_signal_change
                logger.debug(f"Elapsed time since last signal change: {elapsed_time:.1f} seconds")

                wait_times = {road: elapsed_time if road != self.current_green_road else 0 for road in signals}
                logger.debug(f"Wait times: {wait_times}")

                actual_green_time = self.road_timers.get(self.current_green_road, self.min_green_time)

                if self.current_green_road is None:
                    next_road = self.get_next_road(vehicle_counts, wait_times)
                    self.current_green_road = next_road
                    self.road_timers[self.current_green_road] = self.calculate_green_time(vehicle_counts.get(self.current_green_road, 0))
                    self.last_signal_change = current_time
                    signals[self.current_green_road] = "green"
                    for road in signals:
                        if road != self.current_green_road:
                            signals[road] = "red"
                    remaining_time = self.road_timers[self.current_green_road]
                    logger.info(f"Defaulting to {self.current_green_road} (green) for {self.road_timers[self.current_green_road]} seconds")
                elif elapsed_time >= actual_green_time - self.yellow_duration and elapsed_time < actual_green_time:
                    # Start yellow phase 5 seconds before green ends
                    signals[self.current_green_road] = "yellow"
                    for road in signals:
                        if road != self.current_green_road:
                            signals[road] = "red"
                    remaining_time = max(1, actual_green_time - elapsed_time)  # Ensure at least 1 second for visibility
                    logger.info(f"Changing signal to: {self.current_green_road} (yellow) for {remaining_time:.1f} seconds, elapsed: {elapsed_time:.1f}, green time: {actual_green_time}")
                elif elapsed_time >= actual_green_time:
                    # Green time + yellow duration has expired, switch to next green
                    if self.current_green_road not in self.visited_roads:
                        self.visited_roads.append(self.current_green_road)
                        logger.info(f"Added {self.current_green_road} to visited_roads: {list(self.visited_roads)}")
                    
                    next_road = self.get_next_road(vehicle_counts, wait_times)
                    self.current_green_road = next_road
                    self.road_timers[self.current_green_road] = self.calculate_green_time(vehicle_counts.get(next_road, 0))
                    self.last_signal_change = current_time
                    signals[self.current_green_road] = "green"
                    for road in signals:
                        if road != self.current_green_road:
                            signals[road] = "red"
                    remaining_time = self.road_timers[self.current_green_road]
                    logger.info(f"Changing signal to: {self.current_green_road} (green) for {self.road_timers[self.current_green_road]} seconds")
                else:
                    signals[self.current_green_road] = "green"
                    for road in signals:
                        if road != self.current_green_road:
                            signals[road] = "red"
                    remaining_time = max(0, actual_green_time - elapsed_time)
                    logger.debug(f"Continuing with current green road: {self.current_green_road} for {remaining_time:.1f} seconds remaining")

                timing_info = {
                    "current_green": self.current_green_road if self.current_green_road else "",
                    "visited_roads": list(self.visited_roads),
                    "remaining_time": remaining_time
                }

                logger.debug(f"Final signals: {signals}, timing_info: {timing_info}")
                return signals, timing_info

            except Exception as e:
                logger.error(f"Error in decide_signal: {str(e)}")
                signals = {"north": "", "south": "", "west": "", "east": ""}
                timing_info = {
                    "current_green": "",
                    "visited_roads": [],
                    "remaining_time": 0
                }
                return signals, timing_info

    def mark_initialized(self):
        with self.lock:
            self.is_initialized = True
            logger.debug("Signals marked as initialized")

# Instantiate the controller
controller = SignalController()

# Expose functions for use in main.py
def decide_signal(vehicle_counts):
    return controller.decide_signal(vehicle_counts)

def mark_initialized():
    controller.mark_initialized()