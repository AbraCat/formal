import pytest
from formal.nfa import State, Automaton
from formal.thompson import make_nfa, regex_to_postfix
from formal.determinize import determinize, get_epsilon_closure, get_transition
from formal.minimize import minimize_dfa

def test_add_transition():
    s1 = State(1)
    s2 = State(2)
    s1.add_transition('a', s2)
    s1.add_transition('a', s2)
    
    assert 'a' in s1.transitions
    assert s2 in s1.transitions['a']
    assert len(s1.transitions['a']) == 1
    assert "State(1)" in repr(s1)

def test_postfix():
    assert regex_to_postfix("ab") == "ab."
    assert regex_to_postfix("a+b") == "ab+"
    assert regex_to_postfix("a*") == "a*"
    assert regex_to_postfix("a(bc)*") == "abc.*."

def test_make_nfa():
    nfa_empty = make_nfa("")
    assert len(nfa_empty.get_states()) == 1
    
    nfa_single = make_nfa("a")
    states = nfa_single.get_states()
    assert len(states) == 2

def test_determinize_minimize():
    nfa = make_nfa("(a+b)*abb")
    
    dfa = determinize(nfa)
    assert len(dfa.get_states()) > 0
    assert len(dfa.final) >= 1
    
    min_dfa = minimize_dfa(dfa)
    assert len(min_dfa.get_states()) <= len(dfa.get_states())

def test_determinize_minimize2():
    nfa = make_nfa("(a+c)*abb")
    
    dfa = determinize(nfa)
    assert len(dfa.get_states()) > 0
    assert len(dfa.final) >= 1
    
    min_dfa = minimize_dfa(dfa)
    assert len(min_dfa.get_states()) <= len(dfa.get_states())

def test_closure_transition():
    s1 = State(1)
    s2 = State(2)
    s3 = State(3)
    s1.add_transition('', s2)
    s2.add_transition('a', s3)
    
    closure = get_epsilon_closure({s1})
    assert s1 in closure
    assert s2 in closure
    assert s3 not in closure
    move = get_transition(closure, 'a')
    assert s3 in move
    assert s1 not in move

def test_minimize_edge_case():
    s1 = State(1)
    dfa = Automaton(s1, set())
    min_dfa = minimize_dfa(dfa)
    assert len(min_dfa.get_states()) == 1
