from typing import Set, Dict, FrozenSet, List
from .nfa import State, NFA, get_alphabet

def complete_dfa(dfa, alphabet):
    states = dfa.get_states()
    complete = True
    for state in states:
        for c in alphabet:
            if c not in state.transitions or not state.transitions[c]:
                complete = False
                break
    if complete:
        return dfa

    trap = State(max([s.id for s in states]))
    for c in alphabet:
        trap.add_transition(c, trap)
    for state in states:
        for c in alphabet:
            if c not in state.transitions:
                state.add_transition(c, trap)
    return dfa

def get_to_set(to_list, states, c):
    fro = set()
    for state in states:
        if c not in state.transitions:
            continue
        to = list(state.transitions[c])[0]
        if to in to_list:
            fro.add(state)
    return fro

def partition_classes(classes, splitter, queue):
    new_classes = []

    for clas in classes:
        inside = clas & splitter
        outside = clas - splitter
        new_classes += [s for s in [inside, outside] if s]
        if not inside or not outside:
            continue

        if clas in queue:
            queue.remove(clas)
        queue += [inside, outside]

    return new_classes

def get_partition(dfa, alphabet):
    states = dfa.get_states()
    classes = [frozenset(s) for s in [dfa.final, states - dfa.final] if s]
    queue = classes.copy()
        
    while queue != []:
        to = queue.pop(0)
        for c in alphabet:
            splitter = get_to_set(to, states, c)
            if splitter == set():
                continue  

            classes = partition_classes(classes, frozenset(splitter), queue)
    return classes

def partition_to_dfa(dfa, classes):
    state_cnt, clas_to_new, old_to_clas = 0, {}, {}
    
    for clas in classes:
        new_state = State(state_cnt)
        state_cnt += 1
        clas_to_new[clas] = new_state
        for state in clas:
            old_to_clas[state] = clas
            
    for clas in classes:
        old_state = list(clas)[0]
        new_state = clas_to_new[clas]
        for c, to in old_state.transitions.items():
            new_state.add_transition(c, clas_to_new[old_to_clas[list(to)[0]]])
            
    new_start, new_final = clas_to_new[old_to_clas[dfa.start]], set()
    for clas in classes:
        if any(s in dfa.final for s in clas):
            new_final.add(clas_to_new[clas])

    return NFA(new_start, new_final)

def minimize_dfa(dfa):
    alphabet = get_alphabet(dfa.get_states())
    dfa = complete_dfa(dfa, alphabet)
    classes = get_partition(dfa, alphabet)
    return partition_to_dfa(dfa, classes)
