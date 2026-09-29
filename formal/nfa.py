from typing import Set, Dict, FrozenSet

class State:
    def __init__(self, id):
        self.id = id
        self.transitions = {}

    def add_transition(self, symbol, to):
        if symbol not in self.transitions:
            self.transitions[symbol] = set()
        self.transitions[symbol].add(to)

    def __repr__(self):
        return f"State({self.id})"


class Automaton:
    def __init__(self, start, final):
        self.start = start
        self.final = final

    def get_states(self):
        visited = set()
        qu = [self.start]
        while qu != []:
            cur = qu.pop(0)
            if cur in visited:
                continue
                
            visited.add(cur)
            for symbol, states in cur.transitions.items():
                for s in states:
                    if s not in visited:
                        qu += [s]
        return visited
