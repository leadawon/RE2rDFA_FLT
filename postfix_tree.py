class node:
    def __init__(self, cn, cv=None, left=None, right=None):
        # cn : 0:+ 1:. 2:* 3:symbols
        self.cn = cn
        self.cv = cv
        self.left = None
        self.right = None

postall = "ab+*a.b.b."

stack = []
for c in postall:
        if c == "+":
            nd = node(0,c)
            nd.right = stack.pop()
            nd.left = stack.pop()
            stack.append(nd)
        elif c == ".":
            nd = node(1,c)
            nd.right = stack.pop()
            nd.left = stack.pop()
            stack.append(nd)
        elif c == "*":
            nd = node(2,c)
            nd.left = stack.pop() 
            stack.append(nd)
        elif c == "(" or c == ")":
            continue  
        else:
            stack.append(node(3,c))

class eNFA:
    def __init__(self):
        self.next_state = {}

def scan_plus(exp_t):
    start = eNFA()
    end = eNFA()

    first_nfa = node_filter(exp_t.left)
    second_nfa = node_filter(exp_t.right)

    start.next_state['$'] = [first_nfa[0], second_nfa[0]]
    first_nfa[1].next_state['$'] = [end]
    second_nfa[1].next_state['$'] = [end]

def scan_dot(exp_t):
    left_nfa  = node_filter(exp_t.left)
    right_nfa = node_filter(exp_t.right)

    left_nfa[1].next_state['$'] = [right_nfa[0]]
    return left_nfa[0], right_nfa[1]

def scan_star(exp_t):
    start = eNFA()
    end = eNFA()

    starred_nfa = node_filter(exp_t.left)

    start.next_state['$'] = [starred_nfa[0], end]
    starred_nfa[1].next_state['$'] = [starred_nfa[0], end]

    return start, end

def scan_symbol(exp_t):
    start = eNFA()
    end = eNFA()
    
    start.next_state[exp_t.cv] = [end]
    return start, end

def node_filter(nd):
    if nd.cn == 0:
        print(nd.cv)
        return scan_plus(nd)
    elif nd.cn == 1:
        print(nd.cv)
        return scan_dot(nd)
    elif nd.cn == 2:
        print(nd.cv)
        return scan_star(nd)
    elif nd.cn == 3:
        print(nd.cv)
        return scan_symbol(nd)
    else:
        print("error")

nfa = node_filter(stack[0])
