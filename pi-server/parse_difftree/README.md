## Difftree Syntax

Regular SQL + 

- Any Node:
  
      Any{child1, child2, .. (: default = expr)? }
  Examples:
  
      Any{a, b, c: default = 1}
      default is b

      THIS IS DOMAIN
      Any{$state: default = "California"}
      default is California
      "state" is a column name

      THIS IS RANGE
      Any{[100,300]: default = 150}

- Optional Node:
  
      Opt{child}

- Subset:
  
      Subset{delim, child1, child2, ...}

- Multi:
  
      Multi{delim, child}
