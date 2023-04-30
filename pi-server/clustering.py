from difftree.nodes import ASTNode
from difftree.schema import *

'''
find select_results node
return [node.children.text]
'''

def get_component(node, rule):
    if node.rule == rule:
        return node.get_text()
    for c in node.children:
        t = get_component(c, rule)
        if t is not None:
            return t
    return None


def get_projected_content(node, results):
    if isinstance(node, ASTNode) and node.rule in ['sel_res_all_star', 'sel_res_tab_star', 'sel_res_col']:
        results.append((node.get_text(), node.typ))
    elif isinstance(node, ASTNode) and node.rule == 'sel_res_val':
        name = get_component(node, 'name')
        results.append((name or node.get_text(), node.typ))
    elif isinstance(node, ASTNode) and node.rule in ['from_clause', 'join_clause', 'where_clause', 'gb_clause']:
        # Only recurse over parts of the select clause
        return
    else:
        for c in node.children:
            get_projected_content(c, results)
    return results


'''
return a list of clusters
    [[tree_1, tree_2, ...]...]
'''
def clustering_query_trees(trees):
    clusters = {}
    for tree, i in trees:

        sel, sch = zip(*get_projected_content(tree, []))
        select = tuple(sel)
        '''
        clusters[('selected content name', ..)] = [[tree1, ...], [typ1, ...]]
        '''
        if select in clusters:
            clusters[select][0].append(tree)
            clusters[select][1] = list(sch)
        else:
            clusters[select] = [[tree], list(sch)]
    cluster = []
    '''
        update type to be the most compatible types. 
    '''
    for cl, sch in clusters.values():
        if sch:
            for i, s in enumerate(sch):
                if s.type in [EType.NUMBER, EType.STRING]:
                    sch[i] = TypeSchema(Type(s.type))
                if s.type == EType.ADVANCED:
                    sch[i] = TypeSchema(Type(s.ctype))
                if s.type in [EType.NONE, EType.AST]:
                    sch = None
                    break
            if sch is not None:
                cluster.append((cl, ListSchema(sch)))
            else:
                cluster.append((cl, None))
        else:
            cluster.append((cl, None))

    return cluster
