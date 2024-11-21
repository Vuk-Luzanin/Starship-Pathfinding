import heapq
import random
from collections import deque
import config


# state - stanje sistema
# path - lista akcija koje vode ka resenju (torka pocetnog i krajnjeg polozaja)

class Algorithm:
    def get_path(self, state):
        pass


class ExampleAlgorithm(Algorithm):
    def get_path(self, state):
        path = []
        while not state.is_goal_state():
            possible_actions = state.get_legal_actions()
            action = possible_actions[random.randint(0, len(possible_actions) - 1)]  # random possible action
            path.append(action)
            state = state.generate_successor_state(action)
        return path


class Blue(Algorithm):  # DFS
    def get_path(self, state):
        stack = [(state, [])]  # Stack contains tuples of (current state, path leading to this state)
        visited = set()  # Set to track visited states to avoid revisiting

        while stack:
            current_state, current_path = stack.pop()

            if current_state.is_goal_state():
                return current_path

            if current_state in visited:
                continue

            visited.add(current_state)
            possible_actions = current_state.get_legal_actions()
            reversed_possible_actions = possible_actions[::-1]

            for action in reversed_possible_actions:
                successor_state = current_state.generate_successor_state(action)
                if successor_state.is_goal_state():
                    return current_path + [action]
                stack.append((successor_state, current_path + [action]))
        return []


class Red(Algorithm):  # BFS
    def get_path(self, state):
        queue = deque([(state, [])])  # Queue for BFS, storing (current state, path to this state)
        visited = set()  # Set to track visited states to avoid revisiting

        while queue:
            current_state, current_path = queue.popleft()

            if current_state in visited:
                continue

            visited.add(current_state)
            possible_actions = current_state.get_legal_actions()

            for action in possible_actions:
                successor_state = current_state.generate_successor_state(action)
                if successor_state.is_goal_state():
                    return current_path + [action]
                queue.append((successor_state, current_path + [action]))
        return []


""" 
For Branch and Bound Search and A* Search
We do not save minimal cost for every state, because it is quaranted that when we visit state, we will visit it 
with the lowest cost 
"""


class Black(Algorithm):  # Branch & Bound Search
    def get_path(self, state):
        priority_queue = []  # (total_cost, insertion_index, state, path)
        visited = set()  # set to store visited states
        insertion_index = 0  # remembers squence of inserting when adding two states with same path_cost in order to use heapq

        heapq.heappush(priority_queue, (0, insertion_index, state, []))

        while priority_queue:
            total_cost, _, current_state, path = heapq.heappop(priority_queue)

            if current_state.is_goal_state():
                return path

            if (current_state, total_cost) not in visited:
                visited.add((current_state, total_cost))

                possible_actions = current_state.get_legal_actions()
                for action in possible_actions:
                    successor = current_state.generate_successor_state(action)
                    new_cost = total_cost + current_state.get_action_cost(action)
                    if (successor, new_cost) not in visited:
                        heapq.heappush(priority_queue, (new_cost, insertion_index, successor, path + [action]))
                        insertion_index += 1
        return []


class White(Algorithm):         # A* Search
    def find_heuristic(self, state):
        spaceship_positions = self.get_positions(state.spaceships)
        goal_positions = self.get_positions(state.goals)
        total_distance = 0

        # find min Manhattan distance between spaceship and goal
        for s in spaceship_positions:
            min_distance = float('inf')
            for g in goal_positions:
                distance = abs(s[0] - g[0]) + abs(s[1] - g[1])
                if distance < min_distance:
                    min_distance = distance
            total_distance += min_distance
        return total_distance

    # possitions for given bitmask -> 0001 -> (0, 0)
    # code was taken from State class
    def get_positions(self, bitmask):  # top left corner is the lowest bit
        positions = []
        for i in range(config.M * config.N):
            if bitmask & (1 << i):
                positions.append((i // config.N, i % config.N))
        return positions

    def get_path(self, state):
        priority_queue = []  # (total_cost, insertion_index, state, path)
        visited = set()  # set to store visited states
        insertion_index = 0  # remembers squence of inserting when adding two states with same path_cost in order to use heapq

        heapq.heappush(priority_queue, (self.find_heuristic(state), insertion_index, state, []))

        while priority_queue:
            total_cost, _, current_state, path = heapq.heappop(priority_queue)

            if current_state.is_goal_state():
                return path

            if current_state not in visited:
                visited.add(current_state)

                for action in current_state.get_legal_actions():
                    successor = current_state.generate_successor_state(action)
                    # - self.find_heuristic(current_state) -> we are arriving at the next state, so we sub previous heuristic
                    new_cost = total_cost + current_state.get_action_cost(action) - self.find_heuristic(current_state) + self.find_heuristic(successor)

                    if successor not in visited:
                        heapq.heappush(priority_queue, (new_cost, insertion_index, successor, path + [action]))
                        insertion_index += 1
        return []
