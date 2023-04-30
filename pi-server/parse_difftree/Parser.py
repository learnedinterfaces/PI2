from antlr4 import *
from parse_difftree.DiffSqlLexer import DiffSqlLexer
from parse_difftree.DiffSqlParser import DiffSqlParser
import json
import re
import copy
from antlr4.error.ErrorListener import ErrorListener


def is_any_node(children):
    # Any { elem1 , elem2 , ... , elemN ( ; default = elem )? }
    if len(children) > 3 and \
            (children[0]["node_type"] == "terminal" and children[0]["text"] == "Any") and \
            (children[1]["node_type"] == "terminal" and children[1]["text"] == "{") and \
            (children[-1]["node_type"] == "terminal" and children[-1]["text"] == "}"):
        if len(children) > 6 and \
            (children[-5]["node_type"] == "terminal" and children[-5]["text"] == ":") and \
            (children[-4]["node_type"] == "terminal" and children[-4]["text"] == "default") and \
            (children[-3]["node_type"] == "terminal" and children[-3]["text"] == "="):
            default = children[-2]
            choices = children[2:-5:2]  # Any { (<-- get here and skip "," -->) }
        else:
            default = None
            choices = children[2:-1:2]  # Any { (<-- get here and skip "," -->) }
        return {"children": choices, "default": default}
    else:
        return None


def is_optional_node(children):
    # Opt { elem ( ; default = expr )? }
    if len(children) >= 4 and \
            (children[0]["node_type"] == "terminal" and children[0]["text"] == "Opt") and \
            (children[1]["node_type"] == "terminal" and children[1]["text"] == "{") and \
            (children[-1]["node_type"] == "terminal" and children[-1]["text"] == "}"):
        if len(children) == 8 and \
            (children[-5]["node_type"] == "terminal" and children[-5]["text"] == ":") and \
            (children[-4]["node_type"] == "terminal" and children[-4]["text"] == "default") and \
            (children[-3]["node_type"] == "terminal" and children[-3]["text"] == "="):
            default = children[-2]
        else:
            default = None
        choice = children[2]
        return {"child": choice, "default": default}
    else:
        return None


def is_multi_node(children):
    # Multi { elem , delim } optinoal_following_content
    if len(children) == 7 and \
            (children[0]["node_type"] == "terminal" and children[0]["text"] == "Multi") and \
            (children[1]["node_type"] == "terminal" and children[1]["text"] == "{") and \
            (children[-2]["node_type"] == "terminal" and children[-2]["text"] == "}"):
        choice = children[2]
        delim = children[4]
        return choice, delim, children[-1]
    else:
        return None


def is_subset_node(children):
    # Subset { delim , elem1 , elem2 , ... , elemN } optinoal_following_content
    if len(children) >= 7 and \
            (children[0]["node_type"] == "terminal" and children[0]["text"] == "Subset") and \
            (children[1]["node_type"] == "terminal" and children[1]["text"] == "{") and \
            (children[-2]["node_type"] == "terminal" and children[-2]["text"] == "}"):
        choice = children[4:-2:2]
        delim = children[2]
        return choice, delim, children[-1]
    else:
        return None


def to_ast(node):
    node_type = type(node)
    if hasattr(node, "children") and node.children:
        children = list(filter(lambda c:c, [to_ast(c) for c in node.children]))
    else:
        children = []
    if isinstance(node, TerminalNode):
        return {"node_type": "terminal", "text": str(node)}
    else:
        m = re.match(r"<class '.*DiffSqlParser.DiffSqlParser.([^']*)'>", str(node_type))
        rule_name = m.group(1)[:-len("Context")].lower()
        try_any = is_any_node(children)
        if try_any:
            return {"node_type": "choice", "choice_node_type": "Any", "rule": rule_name, "children": try_any["children"], "default": try_any["default"]}
        try_opt = is_optional_node(children)
        if try_opt:
            return {"node_type": "choice", "choice_node_type": "Optional", "rule": rule_name,  "children": [try_opt["child"]], "default": try_opt["default"]}
        try_multi = is_multi_node(children)
        if try_multi:
            return {"node_type": "ast", "rule": rule_name,
                    "children": [
                        {"node_type": "choice", "choice_node_type": "Multi", "rule": rule_name, "children": [try_multi[0]], "delim": try_multi[1]},
                        try_multi[2]
                    ]}
        try_subset = is_subset_node(children)
        if try_subset:
            return {"node_type": "ast", "rule": rule_name,
                    "children": [
                        {"node_type": "choice", "choice_node_type": "Subset", "rule": rule_name, "children": try_subset[0], "delim": try_subset[1]},
                        try_subset[2]
                    ]}
        if children:
            return {"node_type": "ast", "rule": rule_name, "children": children}
        else:
            return None


def __compress(node):
    if node["node_type"] == "ast" and len(node["children"]) == 1 and node["children"][0]["node_type"] == "ast":
        child = __compress(node["children"][0])
        child["rule"] = [node["rule"]] + child["rule"]
        return child
    else:
        if "children" in node:
            node["children"] = list(map(lambda c: __compress(c), node["children"]))
        if "default" in node and node["default"]:
            node["default"] = __compress(node["default"])
        if "rule" in node:
            node["rule"] = [node["rule"]]
        return node


def compress(node):
    return __compress(copy.deepcopy(node))


def __decompress(node):
    if node["node_type"] == "terminal":
        return node
    if len(node["rule"]) == 1:
        node["rule"] = node["rule"][0]
        if "children" in node:
            node["children"] = list(map(lambda c: __decompress(c), node["children"]))
        if "default" in node and node["default"]:
            node["default"] = __decompress(node["default"])
        return node
    else:
        rules = node["rules"]
        node["rules"] = [rules[-1]]
        return __decompress({"node_type": "ast", "rule": rules[:-1], "children": [node]})


def decompress(node):
    return __decompress(copy.deepcopy(node))

class MyErrorListener( ErrorListener ):

    def __init__(self):
        super(MyErrorListener, self).__init__()

    def syntaxError(self, recognizer, offendingSymbol, line, column, msg, e):
        raise Exception("syntaxError!!", "line", line, "column", column, msg)

# parse a string, return the parsed AST
def parse_difftree(diffsql, compact=False):
    input_stream = InputStream(diffsql.strip())
    lexer = DiffSqlLexer(input_stream)
    stream = CommonTokenStream(lexer)
    parser = DiffSqlParser(stream)
    parser.addErrorListener( MyErrorListener() )

    root = parser.root()
    if compact:
        return compress(to_ast(root))
    else:
        return to_ast(root)
