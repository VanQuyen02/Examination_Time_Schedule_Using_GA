import random
import logging

class DistributedRandom:
    def __init__(self):
        self.dis_map = {}
        self.total_weight = 0

    @classmethod
    def new_distributed_random_slot(cls, num_slot, num_room_per_slot):
        rnd = cls()
        for i in range(num_slot):
            rnd.add(i, num_room_per_slot)
        return rnd

    def add(self, key, value):
        if key in self.dis_map.keys():
            self.dis_map[key] += value
        else:
            self.dis_map[key] = value
        self.total_weight += value

    def delete(self, key):
        if key in self.dis_map.keys():
            self.total_weight -= self.dis_map[key]
            del self.dis_map[key]

    def print_count_key(self):
        print(f"Current number of keys: {len(self.dis_map)}, total weight: {self.total_weight}")

    def get_random(self):
        if self.total_weight <= 0:
            print(f"Total weight is non-positive: {self.total_weight}")
        random_value = random.randint(0, self.total_weight - 1)
        for key, weight in self.dis_map.items():
            if random_value < weight:
                return key
            random_value -= weight
        return 0

# Example usage:
if __name__ == "__main__":
    # Create a new distributed random object
    rnd = DistributedRandom()

    # Add some values
    rnd.add(0, 5)
    rnd.add(1, 3)
    rnd.add(2, 7)

    # Print count of keys and total weight
    rnd.print_count_key()

    # Get a random value
    random_value = rnd.get_random()
    print("Random value:", random_value)

    # Delete a key
    rnd.delete(1)

    # Print count of keys and total weight after deletion
    rnd.print_count_key()