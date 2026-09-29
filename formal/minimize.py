from typing import Set, Dict, FrozenSet, List
from .nfa import State, Automaton

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
            if c not in state.transitions or not state.transitions[c]:
                state.add_transition(c, trap)
    return dfa


def get_alphabet(states):
    alphabet = set()
    for s in states:
        for c in s.transitions:
            alphabet.add(c)
    return alphabet

def get_to_set(clas, states, c):
    part = set()
    for state in states:
        if c not in state.transitions:
            continue
        to = list(state.transitions[c])[0]
        if to in clas:
            part.add(state)
    return part

def partition_classes(classes, part, queue):
    new_classes = []
    for clas in classes:
        inside = clas & part
        outside = clas - part
        
        if inside and outside:
            new_classes.append(inside)
            new_classes.append(outside)
            
            if clas in queue:
                queue.remove(clas)
                queue.append(inside)
                queue.append(outside)
            else:
                queue.append(inside if len(inside) <= len(outside) else outside)
        else:
            new_classes.append(clas)

    return new_classes

def get_partition(dfa, alphabet):
    states = dfa.get_states()
    final = dfa.final
    non_final = states - final

    classes = []
    queue = []
    if final:
        classes.append(frozenset(final))
        queue.append(frozenset(final))
    if non_final:
        classes.append(frozenset(non_final))
        queue.append(frozenset(non_final))
        
    while queue != []:
        queue_clas = queue.pop(0)
        for c in alphabet:
            part = get_to_set(queue_clas, states, c)
            if part == set():
                continue  

            part = frozenset(part)
            classes = partition_classes(classes, part, queue)

    return classes

def partition_to_dfa(dfa, classes):
    state_cnt = 0
    clas_to_new = {}
    old_to_clas = {}
    
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
            
    new_start = clas_to_new[old_to_clas[dfa.start]]
    new_final = set()
    for clas in classes:
        if any(s in dfa.final for s in clas):
            new_final.add(clas_to_new[clas])

    return Automaton(new_start, new_final)

def minimize_dfa(dfa):
    alphabet = get_alphabet(dfa.get_states())
    dfa = complete_dfa(dfa, alphabet)
    classes = get_partition(dfa, alphabet)
    return partition_to_dfa(dfa, classes)
