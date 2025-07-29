import math
import random
from IPython.display import display, Markdown

def prime_factors(n):
    factors = []
    if n < 0:
        factors.append(-1)
        n = -n
        
    if n < 4:        
        return factors
    
    while n // 2 == n / 2:
        factors.append(2)
        n //= 2

    f = 3
    c = n // 3
    while f <= c: 
        if n // f == n / f:
            factors.append(f)
            n //= f

        if n // f != n / f:
            #odds
            f += 2

    return factors

    
def ftree(n: int, method="depth_first"):
    if n < -1:
        return (n, -1, ftree(-n, method))
    
    if n < 4:
        return n

    if "depth_first".startswith(str(method).lower()):
        div = 2
        predicate = lambda d: d <= n // 2
        inc = 1

    elif "breadth_first".startswith(str(method).lower()):
        div = int(math.sqrt(n))
        predicate = lambda d: d > 1
        inc = -1

    elif "random".startswith(str(method).lower()):
        factors = prime_factors(n)
        if not factors:
            return n

        ct = random.choice(range(1, len(factors)))
        factors = random.sample(factors, k=ct)
        
        prod = 1
        for factor in factors:
            prod *= factor
            
        div = prod
        predicate = lambda d: True
        
    else:
        raise Exception("method must be 'depth_first' or 'breadth_first'")

    while predicate(div):
        if n // div == n / div:
            return (n, ftree(div, method), ftree(n // div, method))

        div += inc

    return n

def generate_mermaid_tree(tree, parent_id=None, depth=0, node_prefix="node"):
    diagram = ""
    
    # Assign an id to the current node (unique identifier)
    node_id = f"{node_prefix}_{depth}"

    # If the tree is a leaf (a single number), return that node as a leaf
    if isinstance(tree, int):
        diagram += f"    {node_id}[\"{tree}\"]\n"
        if parent_id is not None:
            diagram += f"    {parent_id} --> {node_id}\n"
        return diagram, tree
    else:
        # For non-leaf nodes (internal nodes)
        # Recursively calculate the product of the current node (multiply its children)
        child_values = []
        diagram += f"    {node_id}[\"{tree[0]}\"]\n"
        if parent_id is not None:
            diagram += f"    {parent_id} --> {node_id}\n"
        
        # Recur for each child of the current node and compute the product of values
        product = 1
        for i, subtree in enumerate(tree[1:]):
            child_prefix = f"{node_prefix}_{depth + 1}_{i}"
            child_diagram, child_value = generate_mermaid_tree(subtree, node_id, depth + 1, child_prefix)
            diagram += child_diagram
            child_values.append(child_value)
            product *= child_value

        return diagram, product

def factor_tree(n: int, method: str = "breadth_first"):
    tree = ftree(n, method)
    
    # Start with the Mermaid graph declaration
    mermaid_code = "flowchart TD\n"
    # Generate the tree diagram and get the final product
    diagram, _ = generate_mermaid_tree(tree)
    mermaid_code += diagram
    mermaid_code = "```{mermaid}\n" + mermaid_code + "```"
  
    print(mermaid_code)
    display(Markdown(mermaid_code))
    