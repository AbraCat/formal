import os
import pytest
from unittest.mock import MagicMock, patch

import formal
import formal.cli
import formal.nfa
from formal.nfa import State, NFA, get_state_cnt, normalize_ids
from formal.cli import CLI, write_nfa, read_nfa, draw_nfa

@pytest.fixture
def mock_algorithms():
    with patch('formal.cli.make_nfa') as m_make, patch('formal.cli.determinize') as m_det, patch('formal.cli.minimize_dfa') as m_min:
        yield m_make, m_det, m_min

@pytest.fixture
def nfa1():
    s0 = State(0)
    s1 = State(1)
    s0.transitions = {}
    s1.transitions = {}
    
    s0.add_transition('a', s1)
    s1.add_transition('', s0)
    
    final_states = {s1}
    return NFA(s0, final_states)

def test_make_nfa(mock_algorithms):
    m_make, _, _ = mock_algorithms
    cli = CLI()
    
    with patch('formal.cli.write_nfa') as m_write, patch('formal.cli.draw_nfa') as m_draw:
        cli.make_nfa("a*")
        m_make.assert_called_once_with("a*")
        m_write.assert_called_once()
        m_draw.assert_called_once()


def test_determinize(mock_algorithms):
    _, m_det, _ = mock_algorithms
    cli = CLI()
    
    with patch('formal.cli.read_nfa') as m_read, patch('formal.cli.write_nfa') as m_write, patch('formal.cli.draw_nfa') as m_draw:
        cli.determinize()
        m_read.assert_called_once_with(formal.cli.default_nfa_file)
        m_det.assert_called_once()
        m_write.assert_called_once()


def test_minimize(mock_algorithms):
    _, _, m_min = mock_algorithms
    cli = CLI()
    
    with patch('formal.cli.read_nfa') as m_read, patch('formal.cli.write_nfa') as m_write, patch('formal.cli.draw_nfa') as m_draw:
        cli.minimize()
        m_read.assert_called_once_with(formal.cli.default_dfa_file)
        m_min.assert_called_once()
        m_write.assert_called_once()


def test_process():
    cli = CLI()
    with patch.object(cli, 'make_nfa') as m_make, patch.object(cli, 'determinize') as m_det, patch.object(cli, 'minimize') as m_min:
        cli.process("a+b")
        m_make.assert_called_once_with("a+b")
        m_det.assert_called_once()
        m_min.assert_called_once()

def test_get_state_cnt(nfa1):
    assert get_state_cnt(nfa1) == 2

def test_normalize_ids(nfa1):
    for s in nfa1.get_states():
        s.id = 10565740
            
    normalize_ids(nfa1)
    ids = [state.id for state in nfa1.get_states()]
    assert nfa1.start.id == 0
    assert sorted(ids) == list(range(get_state_cnt(nfa1)))

def test_read_write_nfa(nfa1, tmp_path):
    filepath = tmp_path / "nfa.txt"
    write_nfa(nfa1, str(filepath))
    nfa2 = read_nfa(str(filepath))
    next = list(nfa2.start.transitions['a'])[0]

    assert get_state_cnt(nfa2) == 2
    assert 'a' in nfa2.start.transitions
    assert '' in next.transitions
    assert list(next.transitions[''])[0] == nfa2.start

def test_draw_nfa(nfa1, tmp_path):
    output = tmp_path / "nfa_output"
    with patch('graphviz.Digraph.render') as m_render:
        dot = draw_nfa(nfa1, str(output))
        m_render.assert_called_once_with(str(output), format="png", cleanup=True)
        assert all([text in dot.source for text in ['doublecircle', 'circle', 'before_start']])
