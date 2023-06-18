# Conversion from Regex to NFA

import json
import sys

non_symbols = ['+', '*', '.', '(', ')']
nfa = {}

class charType:
    SYMBOL = 1
    CONCAT = 2
    UNION  = 3
    KLEENE = 4


class NFAState:
    def __init__(self):
        self.next_state = {}


class ExpressionTree:

    def __init__(self, charType, value=None):
        self.charType = charType
        self.value = value
        self.left = None
        self.right = None
    

def make_exp_tree(regexp):
    stack = []
    for c in regexp:
        if c == "+":
            z = ExpressionTree(charType.UNION)
            z.right = stack.pop()
            z.left = stack.pop()
            stack.append(z)
        elif c == ".":
            z = ExpressionTree(charType.CONCAT)
            z.right = stack.pop()
            z.left = stack.pop()
            stack.append(z)
        elif c == "*":
            z = ExpressionTree(charType.KLEENE)
            z.left = stack.pop() 
            stack.append(z)
        elif c == "(" or c == ")":
            continue  
        else:
            stack.append(ExpressionTree(charType.SYMBOL, c))
    return stack[0]


def compPrecedence(a, b):
    p = ["+", ".", "*"]
    return p.index(a) > p.index(b)


def compute_regex(exp_t):
    # returns E-NFA
    if exp_t.charType == charType.CONCAT:
        return do_concat(exp_t)
    elif exp_t.charType == charType.UNION:
        return do_union(exp_t)
    elif exp_t.charType == charType.KLEENE:
        return do_kleene_star(exp_t)
    else:
        return eval_symbol(exp_t)


def eval_symbol(exp_t):
    start = NFAState()
    end = NFAState()
    
    start.next_state[exp_t.value] = [end]
    return start, end


def do_concat(exp_t):
    left_nfa  = compute_regex(exp_t.left)
    right_nfa = compute_regex(exp_t.right)

    left_nfa[1].next_state['$'] = [right_nfa[0]]
    return left_nfa[0], right_nfa[1]


def do_union(exp_t):
    start = NFAState()
    end = NFAState()

    first_nfa = compute_regex(exp_t.left)
    second_nfa = compute_regex(exp_t.right)

    start.next_state['$'] = [first_nfa[0], second_nfa[0]]
    first_nfa[1].next_state['$'] = [end]
    second_nfa[1].next_state['$'] = [end]

    return start, end


def do_kleene_star(exp_t):
    start = NFAState()
    end = NFAState()

    starred_nfa = compute_regex(exp_t.left)

    start.next_state['$'] = [starred_nfa[0], end]
    starred_nfa[1].next_state['$'] = [starred_nfa[0], end]

    return start, end


def arrange_transitions(state, states_done, symbol_table):
    global nfa

    if state in states_done:
        return

    states_done.append(state)

    for symbol in list(state.next_state):
        if symbol not in nfa['letters']:
            nfa['letters'].append(symbol)
        for ns in state.next_state[symbol]:
            if ns not in symbol_table:
                symbol_table[ns] = sorted(symbol_table.values())[-1] + 1
                q_state = "Q" + str(symbol_table[ns])
                nfa['states'].append(q_state)
            nfa['transition_function'].append(["Q" + str(symbol_table[state]), symbol, "Q" + str(symbol_table[ns])])

        for ns in state.next_state[symbol]:
            arrange_transitions(ns, states_done, symbol_table)

def notation_to_num(str):
    return int(str[1:])


# def final_st_dfs(st):
#     global nfa
#     for val in nfa['transition_function']:
#         if val[0] == st and val[1] == "$" and val[2] not in nfa["final_states"]:
#             nfa["final_states"].append(val[2])
#             final_st_dfs(val[2])

def final_st_dfs():
    global nfa
    for st in nfa["states"]:
        count = 0
        for val in nfa['transition_function']:
            if val[0] == st and val[2] != st:
                count += 1
        if count == 0 and st not in nfa["final_states"]:
            nfa["final_states"].append(st)


def arrange_nfa(fa):
    global nfa
    nfa['states'] = []
    nfa['letters'] = []
    nfa['transition_function'] = []
    nfa['start_states'] = []
    nfa['final_states'] = []
    q_1 = "Q" + str(1)
    nfa['states'].append(q_1)
    arrange_transitions(fa[0], [], {fa[0] : 1})
    
    st_num = [notation_to_num(i) for i in nfa['states']]

    nfa["start_states"].append("Q1")
    # nfa["final_states"].append("Q" + str(sorted(st_num)[-1]))
    # final_st_dfs(nfa["final_states"][0])
    final_st_dfs()


def add_concat(regex):
    global non_symbols
    l = len(regex)
    res = []
    for i in range(l - 1):
        res.append(regex[i])
        if regex[i] not in non_symbols:
            if regex[i + 1] not in non_symbols or regex[i + 1] == '(':
                res += '.'
        if regex[i] == ')' and regex[i + 1] == '(':
            res += '.'
        if regex[i] == '*' and regex[i + 1] == '(':
            res += '.'
        if regex[i] == '*' and regex[i + 1] not in non_symbols:
            res += '.'
        if regex[i] == ')' and regex[i + 1] not in non_symbols:
            res += '.'

    res += regex[l - 1]
    return res


def compute_postfix(regexp):
    stk = []
    res = ""

    for c in regexp:
        if c not in non_symbols or c == "*":
            res += c
        elif c == ")":
            while len(stk) > 0 and stk[-1] != "(":
                res += stk.pop()
            stk.pop()
        elif c == "(":
            stk.append(c)
        elif len(stk) == 0 or stk[-1] == "(" or compPrecedence(c, stk[-1]):
            stk.append(c)
        else:
            while len(stk) > 0 and stk[-1] != "(" and not compPrecedence(c, stk[-1]):
                res += stk.pop()
            stk.append(c)

    while len(stk) > 0:
        res += stk.pop()

    return res

def polish_regex(regex):
    reg = add_concat(regex)
    regg = compute_postfix(reg)
    return regg


def load_regex():
    with open(sys.argv[1], 'r') as inpjson:
        regex = json.loads(inpjson.read())
    return regex

def output_nfa():
    global nfa
    with open(sys.argv[2], 'w') as outjson:
        outjson.write(json.dumps(nfa, indent = 4))



    #r = load_regex()
    #reg = r['regex']
reg = "(a+b)*abb"
pr = polish_regex(reg)
et = make_exp_tree(pr)
fa = compute_regex(et)
arrange_nfa(fa)
#print(nfa)
    #output_nfa()

'''
{'states': ['Q1', 'Q2', 'Q3', 'Q4', 'Q5', 'Q6', 'Q7', 'Q8', 'Q9', 'Q10', 'Q11', 'Q12', 'Q13', 'Q14'], 
'letters': ['$', 'a', 'b'], 
'transition_function': [['Q1', '$', 'Q2'], ['Q1', '$', 'Q3'], ['Q2', '$', 'Q4'], ['Q2', '$', 'Q5'], ['Q4', 'a', 'Q6'], ['Q6', '$', 'Q7'], ['Q7', '$', 'Q2'], ['Q7', '$', 'Q3'], ['Q3', '$', 'Q8'], ['Q8', 'a', 'Q9'], ['Q9', '$', 'Q10'], ['Q10', 'b', 'Q11'], ['Q11', '$', 'Q12'], ['Q12', 'b', 'Q13'], ['Q5', 'b', 'Q14'], ['Q14', '$', 'Q7']], 
'start_states': ['Q1'], 
'final_states': ['Q13']}


'''
import json
import sys

dfa = {}
nfa_states = []
dfa_states = []

def get_power_set(nfa_st):
    powerset = [[]]
    for i in nfa_st:
        for sub in powerset:
            powerset = powerset + [list(sub) + [i]]
    return powerset

def load_nfa():
    global nfa
    with open(sys.argv[1], 'r') as inpjson:
        nfa = json.loads(inpjson.read())

def out_dfa():
    global dfa
    with open(sys.argv[2], 'w') as outjson:
        outjson.write(json.dumps(dfa, indent = 4))

if True:
    dfa['states'] = []
    dfa['letters'] = nfa['letters']
    dfa['transition_function'] = []
    
    for state in nfa['states']:
        nfa_states.append(state)

    dfa_states = get_power_set(nfa_states)


    dfa['states'] = []
    for states in dfa_states:
        temp = []
        for state in states:
            temp.append(state)
        dfa['states'].append(temp)

    for states in dfa_states:
        for letter in nfa['letters']:
            q_to = []
            for state in states:
                for val in nfa['transition_function']:
                    start = val[0]
                    inp = val[1]
                    end = val[2]
                    if state == start and letter == inp:
                        if end not in q_to:
                            q_to.append(end)
            q_states = []
            for i in states:
                q_states.append(i)
            dfa['transition_function'].append([q_states, letter, q_to])

    dfa['start_states'] = []
    for state in nfa['start_states']:
        dfa['start_states'].append([state])
    dfa['final_states'] = []
    for states in dfa['states']:
        for state in states:
            if state in nfa['final_states'] and states not in dfa['final_states']:
                dfa['final_states'].append(states)
    print(dfa)
