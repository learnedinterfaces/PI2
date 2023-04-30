import sys

def is_SINGLE(elem):
    return elem.startswith("SINGLE")


def is_OPT(elem):
    return elem.startswith("OPT")


def is_MULTI(elem):
    return elem.startswith("MULTI")


def add_new_rule(name, rule, rules):
    for i in rules:
        if name == i[0]:
            assert( rule == i[1])
            return False
    rules.append((name, rule))
    return True


'''
input: elem = SINGLE(name)
build new rules for single_name
return "single_name"
'''
def construct_SINGLE(elem, new_rules):
    p = elem[7: -1]
    name = 'single_' + p
    '''
    single_p = p | Any{single_p (, single_p)*}
    '''
    rule = [
        '(', "'Any'", "'{'", name, "(", "'|'", name, ")", "*", "(", "':'", "'default'", "'='",  "expr", ")", "?", "'}'", ')',
        '|', '(', p, ')',
    ]
    # “(”, “;”, “’default’”, “’=’”,  “expr”, “)”, “?”,

    # Any{a, b, c; default = 1}
    # default is b

    # THIS IS DOMAIN
    # Any{$state; default = "California"}
    # default is California

    # THIS IS RANGE
    # Any{[100,300]; default = 150}

    # run python translate.py and it automatically generates the .g4 file
    # don't need to modify .g4 manually
    # do the same stuff for optional and multi

    add_new_rule(name, rule, new_rules)
    return name


def construct_OPT(elem, new_rules):
    p = elem[4: -1]
    name = "opt_" + p
    '''
    opt_p = p? | Any{opt_p (, opt_p)* } | Opt{opt_p}
    '''
    rule = [
        '(', "'Any'", "'{'", name, '(', "'|'", name, ')', '*', "(", "':'", "'default'", "'='",  "expr", ")", "?", "'}'", ')',
        '|', '(', "'Opt'", "'{'", name, "(", "':'", "'default'", "'='",  "expr", ")", "?", "'}'", ')',
        '|', '(', p, '?', ')',
    ]
    add_new_rule(name, rule, new_rules)
    return name


def construct_MULTI(elem, new_rules):
    p, delim = elem[6:-1].split(",")[0], elem[6:-1].split(",")[1]
    name = "multi_" + p + "_" + delim
    '''
    name = SINGLE(item) OPT(delim MULTI(item, delim)) 
    | MULTI(item, delim) delim MULTI(item, delim)
    | Subset{delim, SINGLE(item) (,SINGLE(item))*} 
    | Multi{SINGLE(item), delim}
    '''
    delim_name = delim + "_" + name
    new_rules.append((delim_name, [delim, name]))
    single_p = construct_SINGLE("SINGLE(" + p + ")", new_rules)
    opt_p = construct_OPT("OPT("+delim_name+")", new_rules)
    rule = [
        '(', "'Subset'", "'{'", delim, "','", single_p, '(',  "'|'", single_p, ')', '*', "'}'", opt_p, ')',
        '|', '(', "'Multi'", "'{'", delim, "','", single_p, "(", "':'", "'default'", "'='",  "expr", ")", "?", "'}'", opt_p, ')',
        '|', '(', single_p, opt_p, ')',
    ]
    add_new_rule(name, rule, new_rules)
    return name


def translate(origf):
    new_rules = []
    for i in origf:
        name = i.split(' : ')[0].strip()
        rule = i.split(' : ')[1].strip().split(' ')
        rule = list(filter(lambda s: s, map(lambda s: s.strip(), rule)))
        substituted_rule = []
        for j in rule:
            if is_SINGLE(j):
                substituted_rule.append(construct_SINGLE(j, new_rules))
            elif is_OPT(j):
                substituted_rule.append(construct_OPT(j, new_rules))
            elif is_MULTI(j):
                substituted_rule.append(construct_MULTI(j, new_rules))
            else:
                substituted_rule.append(j)
        new_rules.append((name, substituted_rule))
    return new_rules


def main():
    name = sys.argv[1]
    origfilename = name + ".txt"
    outputfilename = name + ".g4"
    origf = open(origfilename, 'r').readlines()

    new_rules = translate(origf)

    outf = open(outputfilename, 'w')
    outf.write(f"grammar {name};\n\n")
    for name, rule in new_rules:
        rule = "    " + (' '.join(rule)).replace(" | ", "\n    | ")
        outf.write(name + ' :' + "\n" + rule + "\n")
        outf.write(";\n")

    outf.close()


if __name__ == "__main__":
    main()
