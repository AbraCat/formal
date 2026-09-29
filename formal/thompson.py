from typing import List
from .nfa import State, Automaton

class Thompson:
    def __init__(self):
        self.state_cnt = 0

    def create_state(self):
        state = State(self.state_cnt)
        self.state_cnt += 1
        return state

    def process_klini(self, nfa):
        start = self.create_state()
        new_fin = self.create_state()

        start.add_transition('', nfa.start)
        start.add_transition('', new_fin)
        for fin in nfa.final:
            fin.add_transition('', nfa.start)
            fin.add_transition('', new_fin)

        return Automaton(start, {new_fin})

    def process_concat(self, nfa1, nfa2):
        for nfa1_fin in nfa1.final:
            nfa1_fin.add_transition('', nfa2.start)
        return Automaton(nfa1.start, nfa2.final)

    def process_or(self, nfa1, nfa2):
        start = self.create_state()
        new_fin = self.create_state()
        
        start.add_transition('', nfa1.start)
        start.add_transition('', nfa2.start)
        
        for fin in nfa1.final:
            fin.add_transition('', new_fin)
        for fin in nfa2.final:
            fin.add_transition('', new_fin)
            
        return Automaton(start, {new_fin})

    def process_char(self, c):
        start = self.create_state()
        fin = self.create_state()
        start.add_transition(c, fin)
        return Automaton(start, {fin})

def add_explicit_concat(regex):
    explicit_concat = ""
    operators = {'+', '*', '(', ')'}
    
    for i in range(len(regex)):
        explicit_concat += regex[i]
        if i == len(regex) - 1:
            continue

        if regex[i] not in ['(', '+'] and regex[i + 1] not in [')', '+', '*']:
            explicit_concat += '.'

    return explicit_concat

def regex_to_postfix(regex):
    regex = add_explicit_concat(regex)

    postfix = ""
    stack = []
    precedence = {'*': 3, '.': 2, '+': 1}
    
    for c in regex:
        if c not in precedence and c not in {'(', ')'}:
            postfix += c
        elif c == '(':
            stack.append(c)
        elif c == ')':
            while stack != [] and stack[-1] != '(':
                postfix += stack.pop()
            stack.pop()
        else:
            while stack != [] and stack[-1] != '(' and precedence.get(stack[-1], 0) >= precedence[c]:
                postfix += stack.pop()
            stack.append(c)
            
    while stack != []:
        postfix += stack.pop()
        
    return postfix

def make_nfa(regex):
    t = Thompson()
    if regex == "":
        s = t.create_state()
        return Automaton(s, {s})

    postfix = regex_to_postfix(regex)
    stack = []

    for c in postfix:
        if c == '*':
            stack.append(t.process_klini(stack.pop()))
        elif c == '.':
            nfa2 = stack.pop()
            nfa1 = stack.pop()
            stack.append(t.process_concat(nfa1, nfa2))
        elif c == '+':
            nfa2 = stack.pop()
            nfa1 = stack.pop()
            stack.append(t.process_or(nfa1, nfa2))
        else:
            stack.append(t.process_char(c))

    return stack.pop()
