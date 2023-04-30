grammar DiffSql;

root :
    query EOF
;
single_select_cores :
    ( 'Any' '{' single_select_cores ( '|' single_select_cores ) * ( ':' 'default' '=' expr ) ? '}' )
    | ( select_cores )
;
opt_orderby :
    ( 'Any' '{' opt_orderby ( '|' opt_orderby ) * ( ':' 'default' '=' expr ) ? '}' )
    | ( 'Opt' '{' opt_orderby ( ':' 'default' '=' expr ) ? '}' )
    | ( orderby ? )
;
opt_limit :
    ( 'Any' '{' opt_limit ( '|' opt_limit ) * ( ':' 'default' '=' expr ) ? '}' )
    | ( 'Opt' '{' opt_limit ( ':' 'default' '=' expr ) ? '}' )
    | ( limit ? )
;
query :
    single_select_cores opt_orderby opt_limit
;
compound_op_multi_select_core_compound_op :
    compound_op multi_select_core_compound_op
;
single_select_core :
    ( 'Any' '{' single_select_core ( '|' single_select_core ) * ( ':' 'default' '=' expr ) ? '}' )
    | ( select_core )
;
opt_compound_op_multi_select_core_compound_op :
    ( 'Any' '{' opt_compound_op_multi_select_core_compound_op ( '|' opt_compound_op_multi_select_core_compound_op ) * ( ':' 'default' '=' expr ) ? '}' )
    | ( 'Opt' '{' opt_compound_op_multi_select_core_compound_op ( ':' 'default' '=' expr ) ? '}' )
    | ( compound_op_multi_select_core_compound_op ? )
;
multi_select_core_compound_op :
    ( 'Subset' '{' compound_op ',' single_select_core ( '|' single_select_core ) * '}' opt_compound_op_multi_select_core_compound_op )
    | ( 'Multi' '{' compound_op ',' single_select_core ( ':' 'default' '=' expr ) ? '}' opt_compound_op_multi_select_core_compound_op )
    | ( single_select_core opt_compound_op_multi_select_core_compound_op )
;
select_cores :
    multi_select_core_compound_op
;
single_select_clause :
    ( 'Any' '{' single_select_clause ( '|' single_select_clause ) * ( ':' 'default' '=' expr ) ? '}' )
    | ( select_clause )
;
opt_from_clause :
    ( 'Any' '{' opt_from_clause ( '|' opt_from_clause ) * ( ':' 'default' '=' expr ) ? '}' )
    | ( 'Opt' '{' opt_from_clause ( ':' 'default' '=' expr ) ? '}' )
    | ( from_clause ? )
;
opt_where_clause :
    ( 'Any' '{' opt_where_clause ( '|' opt_where_clause ) * ( ':' 'default' '=' expr ) ? '}' )
    | ( 'Opt' '{' opt_where_clause ( ':' 'default' '=' expr ) ? '}' )
    | ( where_clause ? )
;
opt_gb_clause :
    ( 'Any' '{' opt_gb_clause ( '|' opt_gb_clause ) * ( ':' 'default' '=' expr ) ? '}' )
    | ( 'Opt' '{' opt_gb_clause ( ':' 'default' '=' expr ) ? '}' )
    | ( gb_clause ? )
;
select_core :
    single_select_clause opt_from_clause opt_where_clause opt_gb_clause
;
opt_top_or_distinct :
    ( 'Any' '{' opt_top_or_distinct ( '|' opt_top_or_distinct ) * ( ':' 'default' '=' expr ) ? '}' )
    | ( 'Opt' '{' opt_top_or_distinct ( ':' 'default' '=' expr ) ? '}' )
    | ( top_or_distinct ? )
;
single_select_results :
    ( 'Any' '{' single_select_results ( '|' single_select_results ) * ( ':' 'default' '=' expr ) ? '}' )
    | ( select_results )
;
select_clause :
    SELECT opt_top_or_distinct single_select_results
;
single_top_clause :
    ( 'Any' '{' single_top_clause ( '|' single_top_clause ) * ( ':' 'default' '=' expr ) ? '}' )
    | ( top_clause )
;
top_or_distinct :
    single_top_clause
    | distinct
;
single_number :
    ( 'Any' '{' single_number ( '|' single_number ) * ( ':' 'default' '=' expr ) ? '}' )
    | ( number )
;
top_clause :
    TOP single_number
;
comma_multi_select_result_comma :
    comma multi_select_result_comma
;
single_select_result :
    ( 'Any' '{' single_select_result ( '|' single_select_result ) * ( ':' 'default' '=' expr ) ? '}' )
    | ( select_result )
;
opt_comma_multi_select_result_comma :
    ( 'Any' '{' opt_comma_multi_select_result_comma ( '|' opt_comma_multi_select_result_comma ) * ( ':' 'default' '=' expr ) ? '}' )
    | ( 'Opt' '{' opt_comma_multi_select_result_comma ( ':' 'default' '=' expr ) ? '}' )
    | ( comma_multi_select_result_comma ? )
;
multi_select_result_comma :
    ( 'Subset' '{' comma ',' single_select_result ( '|' single_select_result ) * '}' opt_comma_multi_select_result_comma )
    | ( 'Multi' '{' comma ',' single_select_result ( ':' 'default' '=' expr ) ? '}' opt_comma_multi_select_result_comma )
    | ( single_select_result opt_comma_multi_select_result_comma )
;
select_results :
    multi_select_result_comma
;
single_sel_res_all_star :
    ( 'Any' '{' single_sel_res_all_star ( '|' single_sel_res_all_star ) * ( ':' 'default' '=' expr ) ? '}' )
    | ( sel_res_all_star )
;
single_sel_res_tab_star :
    ( 'Any' '{' single_sel_res_tab_star ( '|' single_sel_res_tab_star ) * ( ':' 'default' '=' expr ) ? '}' )
    | ( sel_res_tab_star )
;
single_sel_res_val :
    ( 'Any' '{' single_sel_res_val ( '|' single_sel_res_val ) * ( ':' 'default' '=' expr ) ? '}' )
    | ( sel_res_val )
;
single_sel_res_col :
    ( 'Any' '{' single_sel_res_col ( '|' single_sel_res_col ) * ( ':' 'default' '=' expr ) ? '}' )
    | ( sel_res_col )
;
select_result :
    single_sel_res_all_star
    | single_sel_res_tab_star
    | single_sel_res_val
    | single_sel_res_col
;
single_name :
    ( 'Any' '{' single_name ( '|' single_name ) * ( ':' 'default' '=' expr ) ? '}' )
    | ( name )
;
sel_res_tab_star :
    single_name '.*'
;
sel_res_all_star :
    STAR
;
as_name :
    AS name
;
single_expr :
    ( 'Any' '{' single_expr ( '|' single_expr ) * ( ':' 'default' '=' expr ) ? '}' )
    | ( expr )
;
opt_as_name :
    ( 'Any' '{' opt_as_name ( '|' opt_as_name ) * ( ':' 'default' '=' expr ) ? '}' )
    | ( 'Opt' '{' opt_as_name ( ':' 'default' '=' expr ) ? '}' )
    | ( as_name ? )
;
sel_res_val :
    single_expr opt_as_name
;
single_col_ref :
    ( 'Any' '{' single_col_ref ( '|' single_col_ref ) * ( ':' 'default' '=' expr ) ? '}' )
    | ( col_ref )
;
sel_res_col :
    single_col_ref opt_as_name
;
comma_multi_single_source_comma :
    comma multi_single_source_comma
;
single_single_source :
    ( 'Any' '{' single_single_source ( '|' single_single_source ) * ( ':' 'default' '=' expr ) ? '}' )
    | ( single_source )
;
opt_comma_multi_single_source_comma :
    ( 'Any' '{' opt_comma_multi_single_source_comma ( '|' opt_comma_multi_single_source_comma ) * ( ':' 'default' '=' expr ) ? '}' )
    | ( 'Opt' '{' opt_comma_multi_single_source_comma ( ':' 'default' '=' expr ) ? '}' )
    | ( comma_multi_single_source_comma ? )
;
multi_single_source_comma :
    ( 'Subset' '{' comma ',' single_single_source ( '|' single_single_source ) * '}' opt_comma_multi_single_source_comma )
    | ( 'Multi' '{' comma ',' single_single_source ( ':' 'default' '=' expr ) ? '}' opt_comma_multi_single_source_comma )
    | ( single_single_source opt_comma_multi_single_source_comma )
;
from_list :
    multi_single_source_comma
;
single_join :
    single_single_source ON expr
;
join_multi_single_join_join :
    join multi_single_join_join
;
single_single_join :
    ( 'Any' '{' single_single_join ( '|' single_single_join ) * ( ':' 'default' '=' expr ) ? '}' )
    | ( single_join )
;
opt_join_multi_single_join_join :
    ( 'Any' '{' opt_join_multi_single_join_join ( '|' opt_join_multi_single_join_join ) * ( ':' 'default' '=' expr ) ? '}' )
    | ( 'Opt' '{' opt_join_multi_single_join_join ( ':' 'default' '=' expr ) ? '}' )
    | ( join_multi_single_join_join ? )
;
multi_single_join_join :
    ( 'Subset' '{' join ',' single_single_join ( '|' single_single_join ) * '}' opt_join_multi_single_join_join )
    | ( 'Multi' '{' join ',' single_single_join ( ':' 'default' '=' expr ) ? '}' opt_join_multi_single_join_join )
    | ( single_single_join opt_join_multi_single_join_join )
;
join_clause :
    JOIN multi_single_join_join
;
opt_join_clause :
    ( 'Any' '{' opt_join_clause ( '|' opt_join_clause ) * ( ':' 'default' '=' expr ) ? '}' )
    | ( 'Opt' '{' opt_join_clause ( ':' 'default' '=' expr ) ? '}' )
    | ( join_clause ? )
;
join_source :
    single_single_source opt_join_clause
;
from_source :
    from_list
    | join_source
;
single_from_source :
    ( 'Any' '{' single_from_source ( '|' single_from_source ) * ( ':' 'default' '=' expr ) ? '}' )
    | ( from_source )
;
from_clause :
    FROM single_from_source
;
single_source_func :
    ( 'Any' '{' single_source_func ( '|' single_source_func ) * ( ':' 'default' '=' expr ) ? '}' )
    | ( source_func )
;
single_source_table :
    ( 'Any' '{' single_source_table ( '|' single_source_table ) * ( ':' 'default' '=' expr ) ? '}' )
    | ( source_table )
;
single_source_subq :
    ( 'Any' '{' single_source_subq ( '|' single_source_subq ) * ( ':' 'default' '=' expr ) ? '}' )
    | ( source_subq )
;
single_source :
    ( single_source_func
    | single_source_table
    | single_source_subq )
;
source_table :
    name as_name ?
;
source_subq :
    '(' query ')' as_name ?
;
source_func :
    function as_name ?
;
and_or :
    and
    | or
;
and_or_multi_expr_and_or :
    and_or multi_expr_and_or
;
opt_and_or_multi_expr_and_or :
    ( 'Any' '{' opt_and_or_multi_expr_and_or ( '|' opt_and_or_multi_expr_and_or ) * ( ':' 'default' '=' expr ) ? '}' )
    | ( 'Opt' '{' opt_and_or_multi_expr_and_or ( ':' 'default' '=' expr ) ? '}' )
    | ( and_or_multi_expr_and_or ? )
;
multi_expr_and_or :
    ( 'Subset' '{' and_or ',' single_expr ( '|' single_expr ) * '}' opt_and_or_multi_expr_and_or )
    | ( 'Multi' '{' and_or ',' single_expr ( ':' 'default' '=' expr ) ? '}' opt_and_or_multi_expr_and_or )
    | ( single_expr opt_and_or_multi_expr_and_or )
;
where_clause :
    WHERE multi_expr_and_or
;
single_group_clause :
    ( 'Any' '{' single_group_clause ( '|' single_group_clause ) * ( ':' 'default' '=' expr ) ? '}' )
    | ( group_clause )
;
opt_having_clause :
    ( 'Any' '{' opt_having_clause ( '|' opt_having_clause ) * ( ':' 'default' '=' expr ) ? '}' )
    | ( 'Opt' '{' opt_having_clause ( ':' 'default' '=' expr ) ? '}' )
    | ( having_clause ? )
;
gb_clause :
    GROUP BY single_group_clause opt_having_clause
;
comma_multi_grouping_term_comma :
    comma multi_grouping_term_comma
;
single_grouping_term :
    ( 'Any' '{' single_grouping_term ( '|' single_grouping_term ) * ( ':' 'default' '=' expr ) ? '}' )
    | ( grouping_term )
;
opt_comma_multi_grouping_term_comma :
    ( 'Any' '{' opt_comma_multi_grouping_term_comma ( '|' opt_comma_multi_grouping_term_comma ) * ( ':' 'default' '=' expr ) ? '}' )
    | ( 'Opt' '{' opt_comma_multi_grouping_term_comma ( ':' 'default' '=' expr ) ? '}' )
    | ( comma_multi_grouping_term_comma ? )
;
multi_grouping_term_comma :
    ( 'Subset' '{' comma ',' single_grouping_term ( '|' single_grouping_term ) * '}' opt_comma_multi_grouping_term_comma )
    | ( 'Multi' '{' comma ',' single_grouping_term ( ':' 'default' '=' expr ) ? '}' opt_comma_multi_grouping_term_comma )
    | ( single_grouping_term opt_comma_multi_grouping_term_comma )
;
group_clause :
    multi_grouping_term_comma
;
grouping_term :
    single_expr
;
and_multi_expr_and :
    and multi_expr_and
;
opt_and_multi_expr_and :
    ( 'Any' '{' opt_and_multi_expr_and ( '|' opt_and_multi_expr_and ) * ( ':' 'default' '=' expr ) ? '}' )
    | ( 'Opt' '{' opt_and_multi_expr_and ( ':' 'default' '=' expr ) ? '}' )
    | ( and_multi_expr_and ? )
;
multi_expr_and :
    ( 'Subset' '{' and ',' single_expr ( '|' single_expr ) * '}' opt_and_multi_expr_and )
    | ( 'Multi' '{' and ',' single_expr ( ':' 'default' '=' expr ) ? '}' opt_and_multi_expr_and )
    | ( single_expr opt_and_multi_expr_and )
;
having_clause :
    HAVING multi_expr_and
;
comma_multi_ordering_term_comma :
    comma multi_ordering_term_comma
;
single_ordering_term :
    ( 'Any' '{' single_ordering_term ( '|' single_ordering_term ) * ( ':' 'default' '=' expr ) ? '}' )
    | ( ordering_term )
;
opt_comma_multi_ordering_term_comma :
    ( 'Any' '{' opt_comma_multi_ordering_term_comma ( '|' opt_comma_multi_ordering_term_comma ) * ( ':' 'default' '=' expr ) ? '}' )
    | ( 'Opt' '{' opt_comma_multi_ordering_term_comma ( ':' 'default' '=' expr ) ? '}' )
    | ( comma_multi_ordering_term_comma ? )
;
multi_ordering_term_comma :
    ( 'Subset' '{' comma ',' single_ordering_term ( '|' single_ordering_term ) * '}' opt_comma_multi_ordering_term_comma )
    | ( 'Multi' '{' comma ',' single_ordering_term ( ':' 'default' '=' expr ) ? '}' opt_comma_multi_ordering_term_comma )
    | ( single_ordering_term opt_comma_multi_ordering_term_comma )
;
orderby :
    ORDER BY multi_ordering_term_comma
;
asc_desc :
    ASC|DESC
;
opt_asc_desc :
    ( 'Any' '{' opt_asc_desc ( '|' opt_asc_desc ) * ( ':' 'default' '=' expr ) ? '}' )
    | ( 'Opt' '{' opt_asc_desc ( ':' 'default' '=' expr ) ? '}' )
    | ( asc_desc ? )
;
ordering_term :
    single_expr opt_asc_desc
;
limit :
    LIMIT single_expr
;
table_dot :
    name '.'
;
col_ref :
    table_dot ? name
;
single_btwnexpr :
    ( 'Any' '{' single_btwnexpr ( '|' single_btwnexpr ) * ( ':' 'default' '=' expr ) ? '}' )
    | ( btwnexpr )
;
single_biexpr :
    ( 'Any' '{' single_biexpr ( '|' single_biexpr ) * ( ':' 'default' '=' expr ) ? '}' )
    | ( biexpr )
;
single_unexpr :
    ( 'Any' '{' single_unexpr ( '|' single_unexpr ) * ( ':' 'default' '=' expr ) ? '}' )
    | ( unexpr )
;
single_value :
    ( 'Any' '{' single_value ( '|' single_value ) * ( ':' 'default' '=' expr ) ? '}' )
    | ( value )
;
expr :
    single_btwnexpr
    | single_biexpr
    | single_unexpr
    | single_value
    | single_source_subq
;
btwnexpr :
    single_value BETWEEN single_value AND single_value
;
single_binaryop_no_andor :
    ( 'Any' '{' single_binaryop_no_andor ( '|' single_binaryop_no_andor ) * ( ':' 'default' '=' expr ) ? '}' )
    | ( binaryop_no_andor )
;
biexpr :
    single_value single_binaryop_no_andor single_expr
;
single_unaryop :
    ( 'Any' '{' single_unaryop ( '|' single_unaryop ) * ( ':' 'default' '=' expr ) ? '}' )
    | ( unaryop )
;
unexpr :
    single_unaryop single_expr
;
single_parenval :
    ( 'Any' '{' single_parenval ( '|' single_parenval ) * ( ':' 'default' '=' expr ) ? '}' )
    | ( parenval )
;
single_boolean :
    ( 'Any' '{' single_boolean ( '|' single_boolean ) * ( ':' 'default' '=' expr ) ? '}' )
    | ( boolean )
;
single_function :
    ( 'Any' '{' single_function ( '|' single_function ) * ( ':' 'default' '=' expr ) ? '}' )
    | ( function )
;
single_string :
    ( 'Any' '{' single_string ( '|' single_string ) * ( ':' 'default' '=' expr ) ? '}' )
    | ( string )
;
single_domain :
    ( 'Any' '{' single_domain ( '|' single_domain ) * ( ':' 'default' '=' expr ) ? '}' )
    | ( domain )
;
single_range :
    ( 'Any' '{' single_range ( '|' single_range ) * ( ':' 'default' '=' expr ) ? '}' )
    | ( range )
;
value :
    single_parenval
    | single_number
    | single_boolean
    | single_function
    | single_col_ref
    | single_string
    | single_name
    | single_domain
    | single_range
;
domain :
    '$' col_ref
;
range :
    '[' number ',' number ']'
;
parenval :
    '(' single_expr ')'
;
opt_arg_list :
    ( 'Any' '{' opt_arg_list ( '|' opt_arg_list ) * ( ':' 'default' '=' expr ) ? '}' )
    | ( 'Opt' '{' opt_arg_list ( ':' 'default' '=' expr ) ? '}' )
    | ( arg_list ? )
;
function :
    single_name '(' opt_arg_list ')'
;
comma_multi_expr_comma :
    comma multi_expr_comma
;
opt_comma_multi_expr_comma :
    ( 'Any' '{' opt_comma_multi_expr_comma ( '|' opt_comma_multi_expr_comma ) * ( ':' 'default' '=' expr ) ? '}' )
    | ( 'Opt' '{' opt_comma_multi_expr_comma ( ':' 'default' '=' expr ) ? '}' )
    | ( comma_multi_expr_comma ? )
;
multi_expr_comma :
    ( 'Subset' '{' comma ',' single_expr ( '|' single_expr ) * '}' opt_comma_multi_expr_comma )
    | ( 'Multi' '{' comma ',' single_expr ( ':' 'default' '=' expr ) ? '}' opt_comma_multi_expr_comma )
    | ( single_expr opt_comma_multi_expr_comma )
;
arg_list :
    multi_expr_comma
    | sel_res_all_star
;
boolean :
    'true'
    | 'false'
;
compound_op :
    'UNION'
    | 'union'
;
binaryop :
    '+'
    | '-'
    | STAR
    | '/'
    | '=='
    | '='
    | '<>'
    | '!='
    | '<='
    | '>='
    | '<'
    | '>'
    | LIKE
    | IN
    | and_or
;
binaryop_no_andor :
    '+'
    | '-'
    | STAR
    | '/'
    | '=='
    | '='
    | '<>'
    | '!='
    | '<='
    | '>='
    | '<'
    | '>'
    | LIKE
    | IN
;
unaryop :
    '+'
    | '-'
    | NOT
;
string :
    STRING
;
name :
    NAME
;
number :
    NUMBER
;
comma :
    COMMA
;
and :
    AND
;
or :
    OR
;
join :
    JOIN
;
distinct :
    DISTINCT
;
STAR :
    '*'
;
ADD :
    ('ADD'
    | 'add')
;
ALL :
    ('ALL'
    | 'all')
;
ALTER :
    ('ALTER'
    | 'alter')
;
AND :
    ('AND'
    | 'and')
;
AS :
    ('AS'
    | 'as')
;
ASC :
    ('ASC'
    | 'asc')
;
BETWEEN :
    ('BETWEEN'
    | 'between')
;
BY :
    ('BY'
    | 'by')
;
CAST :
    ('CAST'
    | 'cast')
;
COLUMN :
    ('COLUMN'
    | 'column')
;
DESC :
    ('DESC'
    | 'desc')
;
DISTINCT :
    ('DISTINCT'
    | 'distinct')
;
TOP :
    ('TOP'
    | 'top')
;
E :
    'E'
;
COMMA :
    ','
;
ESCAPE :
    ('ESCAPE'
    | 'escape')
;
EXCEPT :
    ('EXCEPT'
    | 'except')
;
EXISTS :
    ('EXISTS'
    | 'exists')
;
EXPLAIN :
    ('EXPLAIN'
    | 'explain')
;
EVENT :
    ('EVENT'
    | 'event')
;
FORALL :
    ('FORALL'
    | 'forall')
;
FROM :
    ('FROM'
    | 'from')
;
GLOB :
    ('GLOB'
    | 'glob')
;
GROUP :
    ('GROUP'
    | 'group')
;
HAVING :
    ('HAVING'
    | 'having')
;
IN :
    ('IN'
    | 'in')
;
INNER :
    ('INNER'
    | 'inner')
;
INSERT :
    ('INSERT'
    | 'insert')
;
INTERSECT :
    ('INTERSECT'
    | 'intersect')
;
INTO :
    ('INTO'
    | 'into')
;
IS :
    ('IS'
    | 'is')
;
ISNULL :
    ('ISNULL'
    | 'isnull')
;
JOIN :
    ('JOIN'
    | 'join')
;
KEY :
    ('KEY'
    | 'key')
;
LEFT :
    ('LEFT'
    | 'left')
;
LIKE :
    ('LIKE'
    | 'like')
;
LIMIT :
    ('LIMIT'
    | 'limit')
;
MATCH :
    ('MATCH'
    | 'match')
;
NO :
    ('NO'
    | 'no')
;
NOT :
    ('NOT'
    | 'not')
;
NOTNULL :
    ('NOTNULL'
    | 'notnull')
;
NULL :
    ('NULL'
    | 'null')
;
OF :
    ('OF'
    | 'of')
;
OFFSET :
    ('OFFSET'
    | 'offset')
;
ON :
    ('ON'
    | 'on')
;
OR :
    ('OR'
    | 'or')
;
ORDER :
    ('ORDER'
    | 'order')
;
OUTER :
    ('OUTER'
    | 'outer')
;
PRIMARY :
    ('PRIMARY'
    | 'primary')
;
QUERY :
    ('QUERY'
    | 'query')
;
RAISE :
    ('RAISE'
    | 'raise')
;
REFERENCES :
    ('REFERENCES'
    | 'references')
;
REGEXP :
    ('REGEXP'
    | 'regexp')
;
RENAME :
    ('RENAME'
    | 'rename')
;
REPLACE :
    ('REPLACE'
    | 'replace')
;
RETURN :
    ('RETURN'
    | 'return')
;
ROW :
    ('ROW'
    | 'row')
;
SAVEPOINT :
    ('SAVEPOINT'
    | 'savepoint')
;
SELECT :
    ('SELECT'
    | 'select')
;
SET :
    ('SET'
    | 'set')
;
TABLE :
    ('TABLE'
    | 'table')
;
TEMP :
    ('TEMP'
    | 'temp')
;
TEMPORARY :
    ('TEMPORARY'
    | 'temporary')
;
THEN :
    ('THEN'
    | 'then')
;
TO :
    ('TO'
    | 'to')
;
UNION :
    ('UNION'
    | 'union')
;
USING :
    ('USING'
    | 'using')
;
VALUES :
    ('VALUES'
    | 'values')
;
VIRTUAL :
    ('VIRTUAL'
    | 'virtual')
;
WITH :
    ('WITH'
    | 'with')
;
WHERE :
    ('WHERE'
    | 'where')
;
NUMBER :
    [0-9]* '.'? [0-9]+
;
STRING :
    '\'' ( ~'\''
    | '\'\'')* '\''
;
NAME :
    [_a-zA-Z][_a-zA-Z0-9]*
;
WS :
    [ \t\r\n]+ -> skip
;
