import fire
import graphviz

from .thompson import make_nfa
from .determinize import determinize
from .minimize import minimize_dfa
from .nfa import Automaton, State

default_nfa_file = "txt/nfa.txt"
default_dfa_file = "txt/dfa.txt"
default_mcdfa_file = "txt/mcdfa.txt"

default_draw_nfa_file = "png/nfa"
default_draw_dfa_file = "png/dfa"
default_draw_mcdfa_file = "png/mcdfa"

eps_str = "eps"

class CLI:
    def make_nfa(self, regex, output=default_nfa_file, draw=default_draw_nfa_file):
        nfa = make_nfa(regex)
        write_nfa(nfa, output)
        draw_nfa(nfa, draw)

    def determinize(self, input=default_nfa_file, output=default_dfa_file, draw=default_draw_dfa_file):
        nfa = read_nfa(input)
        dfa = determinize(nfa)
        write_nfa(dfa, output)
        draw_nfa(dfa, draw)

    def minimize(self, input=default_dfa_file, output=default_mcdfa_file, draw=default_draw_mcdfa_file):
        dfa = read_nfa(input)
        mcdfa = minimize_dfa(dfa)
        write_nfa(mcdfa, output)
        draw_nfa(mcdfa, draw)

    def process(self, regex, output=default_mcdfa_file, draw=default_draw_mcdfa_file):
        self.make_nfa(regex)
        self.determinize()
        self.minimize(output=output, draw=draw)

def main():
    fire.Fire(CLI)

if __name__ == '__main__':
    main()

def get_state_cnt_dfs(nfa, state, visited):
    if state in visited:
        return 0
    visited.append(state)
    
    cnt = 0
    for (c, states) in state.transitions.items():
        for to in states:
            cnt += get_state_cnt_dfs(nfa, to, visited)

    return cnt + 1

def get_state_cnt(nfa):
    return get_state_cnt_dfs(nfa, nfa.start, [])

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

def write_nfa_dfs(file, state, nfa, visited):
    if state in visited:
        return
    visited.append(state)

    final_str = "final" if state in nfa.final else "nonfinal"
    file.write(f"state {state.id} {final_str} {len(state.transitions)}\n")
    for (c, states) in state.transitions.items():
        if c == '':
            c = eps_str

        file.write(f"transition {c} ")
        for to in states:
            file.write(f"{to.id} ")
        file.write("\n")

    for (c, states) in state.transitions.items():
        for to in states:
            write_nfa_dfs(file, to, nfa, visited)

def write_nfa(nfa, filename):
    normalize_ids(nfa)
    with open(filename, "w", encoding="utf-8") as file:
        file.write(f"{get_state_cnt(nfa)}\n")
        write_nfa_dfs(file, nfa.start, nfa, [])

def read_nfa(filename):
    with open(filename, "r", encoding="utf-8") as file:
        state_cnt = int(file.readline())
        states = [State(id) for id in range(state_cnt)]
        start_id = -1
        final_states = set()

        for _ in range(state_cnt):
            state_str, id, final, trans_cnt = file.readline().split()
            assert state_str == "state"
            id = int(id)
            trans_cnt = int(trans_cnt)

            if final == "final":
                final_states.add(states[id])
            if start_id == -1:
                start_id = id
            
            for _ in range(trans_cnt):
                trans_str, c, *to_ids = file.readline().split()
                assert trans_str == "transition"
                if c == eps_str:
                    c = ''

                for to in to_ids:
                    states[id].add_transition(c, states[int(to)])

        return Automaton(states[start_id], final_states)

def draw_nfa(nfa, filename):
    dot = graphviz.Digraph(comment='Automaton', graph_attr={'rankdir': 'LR'})
    states = nfa.get_states()
    dot.node('before_start', shape='point', width='0')

    for state in states:
        id = str(state.id)
        if state in nfa.final:
            dot.node(id, shape='doublecircle')
        else:
            dot.node(id, shape='circle')
    
        if state == nfa.start:
            dot.edge('before_start', id)
            
    edges = {}
    for state in states:
        fro = str(state.id)
        for c, to_list in state.transitions.items():
            for to in to_list:
                key = (fro, str(to.id))
                if key not in edges:
                    edges[key] = []
                edges[key].append(str(c))
                
    for (fro, to), symbols in edges.items():
        dot.edge(fro, to, label=", ".join(symbols))
        
    dot.render(filename, format="png", cleanup=True)
    return dot

