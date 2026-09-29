from typing import Set, Dict, FrozenSet, List
from .nfa import State, Automaton

def get_epsilon_closure(states):
    closure = set(states)
    stack = list(states)
    
    while stack != []:
        cur = stack.pop()
        if '' not in cur.transitions:
            continue

        for next in cur.transitions['']:
            if next not in closure:
                closure.add(next)
                stack.append(next)
                    
    return frozenset(closure)

def get_transition(states, c):
    move = set()
    for state in states:
        if c in state.transitions:
            move.update(state.transitions[c])
    return move

def get_alphabet(nfa):
    alphabet = set()
    states = nfa.get_states()
    for state in states:
        for c in state.transitions:
            if c != '':
                alphabet.add(c)
    return alphabet

def get_dfa_final(nfa, state_map):
    dfa_final = set()
    for nfa_state, dfa_state in state_map.items():
        if any(s in nfa.final for s in nfa_state):
            dfa_final.add(dfa_state)
    return dfa_final

def get_dfa_state(nfa_state, state_map, cnt):
    if nfa_state not in state_map:
        state_map[nfa_state] = State(cnt)
    return state_map[nfa_state], cnt + 1

def determinize(nfa):
    alphabet = get_alphabet(nfa)
    nfa_start_closure = get_epsilon_closure({nfa.start})
    cnt = 0
    state_map = {}
    dfa_start, cnt = get_dfa_state(nfa_start_closure, state_map, cnt)

    state_queue = [nfa_start_closure]
    processed = set()
    while state_queue != []:
        nfa_cur = state_queue.pop(0)
        processed.add(nfa_cur)
        cur_dfa = state_map[nfa_cur]
        
        for c in alphabet:
            transition = get_transition(nfa_cur, c)
            if transition == set():
                continue
                
            trans_closure = get_epsilon_closure(transition)
            if trans_closure not in state_queue and trans_closure not in processed:
                state_queue.append(trans_closure)
            next_dfa, cnt = get_dfa_state(trans_closure, state_map, cnt)
            cur_dfa.add_transition(c, next_dfa)
                    
    return Automaton(dfa_start, get_dfa_final(nfa, state_map))
