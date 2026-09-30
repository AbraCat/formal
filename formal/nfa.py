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

class NFA:
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

    def __repr__(self):
        return f"NFA({self.start.id}, {sorted([state.id for state in self.final])})"

def get_alphabet(states):
    alphabet = set()
    for state in states:
        for c in state.transitions:
            if c != '':
                alphabet.add(c)
    return alphabet

def get_state_cnt(nfa):
    return get_state_cnt_dfs(nfa, nfa.start, [])

def get_state_cnt_dfs(nfa, state, visited):
    if state in visited:
        return 0
    visited.append(state)
    
    cnt = 0
    for (c, states) in state.transitions.items():
        for to in states:
            cnt += get_state_cnt_dfs(nfa, to, visited)

    return cnt + 1

def normalize_ids(nfa):
    state_cnt = get_state_cnt(nfa)
    normalize_ids_dfs(nfa, nfa.start, 0, [])

def normalize_ids_dfs(nfa, state, new_cnt, visited):
    if state in visited:
        return new_cnt
    visited.append(state)
    state.id = new_cnt
    new_cnt += 1

    for (c, states) in state.transitions.items():
        for to in states:
            new_cnt = normalize_ids_dfs(nfa, to, new_cnt, visited)
    return new_cnt