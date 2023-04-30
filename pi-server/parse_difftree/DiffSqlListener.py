# Generated from DiffSql.g4 by ANTLR 4.10.1
from antlr4 import *
if __name__ is not None and "." in __name__:
    from .DiffSqlParser import DiffSqlParser
else:
    from DiffSqlParser import DiffSqlParser

# This class defines a complete listener for a parse tree produced by DiffSqlParser.
class DiffSqlListener(ParseTreeListener):

    # Enter a parse tree produced by DiffSqlParser#root.
    def enterRoot(self, ctx:DiffSqlParser.RootContext):
        pass

    # Exit a parse tree produced by DiffSqlParser#root.
    def exitRoot(self, ctx:DiffSqlParser.RootContext):
        pass


    # Enter a parse tree produced by DiffSqlParser#single_select_cores.
    def enterSingle_select_cores(self, ctx:DiffSqlParser.Single_select_coresContext):
        pass

    # Exit a parse tree produced by DiffSqlParser#single_select_cores.
    def exitSingle_select_cores(self, ctx:DiffSqlParser.Single_select_coresContext):
        pass


    # Enter a parse tree produced by DiffSqlParser#opt_orderby.
    def enterOpt_orderby(self, ctx:DiffSqlParser.Opt_orderbyContext):
        pass

    # Exit a parse tree produced by DiffSqlParser#opt_orderby.
    def exitOpt_orderby(self, ctx:DiffSqlParser.Opt_orderbyContext):
        pass


    # Enter a parse tree produced by DiffSqlParser#opt_limit.
    def enterOpt_limit(self, ctx:DiffSqlParser.Opt_limitContext):
        pass

    # Exit a parse tree produced by DiffSqlParser#opt_limit.
    def exitOpt_limit(self, ctx:DiffSqlParser.Opt_limitContext):
        pass


    # Enter a parse tree produced by DiffSqlParser#query.
    def enterQuery(self, ctx:DiffSqlParser.QueryContext):
        pass

    # Exit a parse tree produced by DiffSqlParser#query.
    def exitQuery(self, ctx:DiffSqlParser.QueryContext):
        pass


    # Enter a parse tree produced by DiffSqlParser#compound_op_multi_select_core_compound_op.
    def enterCompound_op_multi_select_core_compound_op(self, ctx:DiffSqlParser.Compound_op_multi_select_core_compound_opContext):
        pass

    # Exit a parse tree produced by DiffSqlParser#compound_op_multi_select_core_compound_op.
    def exitCompound_op_multi_select_core_compound_op(self, ctx:DiffSqlParser.Compound_op_multi_select_core_compound_opContext):
        pass


    # Enter a parse tree produced by DiffSqlParser#single_select_core.
    def enterSingle_select_core(self, ctx:DiffSqlParser.Single_select_coreContext):
        pass

    # Exit a parse tree produced by DiffSqlParser#single_select_core.
    def exitSingle_select_core(self, ctx:DiffSqlParser.Single_select_coreContext):
        pass


    # Enter a parse tree produced by DiffSqlParser#opt_compound_op_multi_select_core_compound_op.
    def enterOpt_compound_op_multi_select_core_compound_op(self, ctx:DiffSqlParser.Opt_compound_op_multi_select_core_compound_opContext):
        pass

    # Exit a parse tree produced by DiffSqlParser#opt_compound_op_multi_select_core_compound_op.
    def exitOpt_compound_op_multi_select_core_compound_op(self, ctx:DiffSqlParser.Opt_compound_op_multi_select_core_compound_opContext):
        pass


    # Enter a parse tree produced by DiffSqlParser#multi_select_core_compound_op.
    def enterMulti_select_core_compound_op(self, ctx:DiffSqlParser.Multi_select_core_compound_opContext):
        pass

    # Exit a parse tree produced by DiffSqlParser#multi_select_core_compound_op.
    def exitMulti_select_core_compound_op(self, ctx:DiffSqlParser.Multi_select_core_compound_opContext):
        pass


    # Enter a parse tree produced by DiffSqlParser#select_cores.
    def enterSelect_cores(self, ctx:DiffSqlParser.Select_coresContext):
        pass

    # Exit a parse tree produced by DiffSqlParser#select_cores.
    def exitSelect_cores(self, ctx:DiffSqlParser.Select_coresContext):
        pass


    # Enter a parse tree produced by DiffSqlParser#single_select_clause.
    def enterSingle_select_clause(self, ctx:DiffSqlParser.Single_select_clauseContext):
        pass

    # Exit a parse tree produced by DiffSqlParser#single_select_clause.
    def exitSingle_select_clause(self, ctx:DiffSqlParser.Single_select_clauseContext):
        pass


    # Enter a parse tree produced by DiffSqlParser#opt_from_clause.
    def enterOpt_from_clause(self, ctx:DiffSqlParser.Opt_from_clauseContext):
        pass

    # Exit a parse tree produced by DiffSqlParser#opt_from_clause.
    def exitOpt_from_clause(self, ctx:DiffSqlParser.Opt_from_clauseContext):
        pass


    # Enter a parse tree produced by DiffSqlParser#opt_where_clause.
    def enterOpt_where_clause(self, ctx:DiffSqlParser.Opt_where_clauseContext):
        pass

    # Exit a parse tree produced by DiffSqlParser#opt_where_clause.
    def exitOpt_where_clause(self, ctx:DiffSqlParser.Opt_where_clauseContext):
        pass


    # Enter a parse tree produced by DiffSqlParser#opt_gb_clause.
    def enterOpt_gb_clause(self, ctx:DiffSqlParser.Opt_gb_clauseContext):
        pass

    # Exit a parse tree produced by DiffSqlParser#opt_gb_clause.
    def exitOpt_gb_clause(self, ctx:DiffSqlParser.Opt_gb_clauseContext):
        pass


    # Enter a parse tree produced by DiffSqlParser#select_core.
    def enterSelect_core(self, ctx:DiffSqlParser.Select_coreContext):
        pass

    # Exit a parse tree produced by DiffSqlParser#select_core.
    def exitSelect_core(self, ctx:DiffSqlParser.Select_coreContext):
        pass


    # Enter a parse tree produced by DiffSqlParser#opt_top_or_distinct.
    def enterOpt_top_or_distinct(self, ctx:DiffSqlParser.Opt_top_or_distinctContext):
        pass

    # Exit a parse tree produced by DiffSqlParser#opt_top_or_distinct.
    def exitOpt_top_or_distinct(self, ctx:DiffSqlParser.Opt_top_or_distinctContext):
        pass


    # Enter a parse tree produced by DiffSqlParser#single_select_results.
    def enterSingle_select_results(self, ctx:DiffSqlParser.Single_select_resultsContext):
        pass

    # Exit a parse tree produced by DiffSqlParser#single_select_results.
    def exitSingle_select_results(self, ctx:DiffSqlParser.Single_select_resultsContext):
        pass


    # Enter a parse tree produced by DiffSqlParser#select_clause.
    def enterSelect_clause(self, ctx:DiffSqlParser.Select_clauseContext):
        pass

    # Exit a parse tree produced by DiffSqlParser#select_clause.
    def exitSelect_clause(self, ctx:DiffSqlParser.Select_clauseContext):
        pass


    # Enter a parse tree produced by DiffSqlParser#single_top_clause.
    def enterSingle_top_clause(self, ctx:DiffSqlParser.Single_top_clauseContext):
        pass

    # Exit a parse tree produced by DiffSqlParser#single_top_clause.
    def exitSingle_top_clause(self, ctx:DiffSqlParser.Single_top_clauseContext):
        pass


    # Enter a parse tree produced by DiffSqlParser#top_or_distinct.
    def enterTop_or_distinct(self, ctx:DiffSqlParser.Top_or_distinctContext):
        pass

    # Exit a parse tree produced by DiffSqlParser#top_or_distinct.
    def exitTop_or_distinct(self, ctx:DiffSqlParser.Top_or_distinctContext):
        pass


    # Enter a parse tree produced by DiffSqlParser#single_number.
    def enterSingle_number(self, ctx:DiffSqlParser.Single_numberContext):
        pass

    # Exit a parse tree produced by DiffSqlParser#single_number.
    def exitSingle_number(self, ctx:DiffSqlParser.Single_numberContext):
        pass


    # Enter a parse tree produced by DiffSqlParser#top_clause.
    def enterTop_clause(self, ctx:DiffSqlParser.Top_clauseContext):
        pass

    # Exit a parse tree produced by DiffSqlParser#top_clause.
    def exitTop_clause(self, ctx:DiffSqlParser.Top_clauseContext):
        pass


    # Enter a parse tree produced by DiffSqlParser#comma_multi_select_result_comma.
    def enterComma_multi_select_result_comma(self, ctx:DiffSqlParser.Comma_multi_select_result_commaContext):
        pass

    # Exit a parse tree produced by DiffSqlParser#comma_multi_select_result_comma.
    def exitComma_multi_select_result_comma(self, ctx:DiffSqlParser.Comma_multi_select_result_commaContext):
        pass


    # Enter a parse tree produced by DiffSqlParser#single_select_result.
    def enterSingle_select_result(self, ctx:DiffSqlParser.Single_select_resultContext):
        pass

    # Exit a parse tree produced by DiffSqlParser#single_select_result.
    def exitSingle_select_result(self, ctx:DiffSqlParser.Single_select_resultContext):
        pass


    # Enter a parse tree produced by DiffSqlParser#opt_comma_multi_select_result_comma.
    def enterOpt_comma_multi_select_result_comma(self, ctx:DiffSqlParser.Opt_comma_multi_select_result_commaContext):
        pass

    # Exit a parse tree produced by DiffSqlParser#opt_comma_multi_select_result_comma.
    def exitOpt_comma_multi_select_result_comma(self, ctx:DiffSqlParser.Opt_comma_multi_select_result_commaContext):
        pass


    # Enter a parse tree produced by DiffSqlParser#multi_select_result_comma.
    def enterMulti_select_result_comma(self, ctx:DiffSqlParser.Multi_select_result_commaContext):
        pass

    # Exit a parse tree produced by DiffSqlParser#multi_select_result_comma.
    def exitMulti_select_result_comma(self, ctx:DiffSqlParser.Multi_select_result_commaContext):
        pass


    # Enter a parse tree produced by DiffSqlParser#select_results.
    def enterSelect_results(self, ctx:DiffSqlParser.Select_resultsContext):
        pass

    # Exit a parse tree produced by DiffSqlParser#select_results.
    def exitSelect_results(self, ctx:DiffSqlParser.Select_resultsContext):
        pass


    # Enter a parse tree produced by DiffSqlParser#single_sel_res_all_star.
    def enterSingle_sel_res_all_star(self, ctx:DiffSqlParser.Single_sel_res_all_starContext):
        pass

    # Exit a parse tree produced by DiffSqlParser#single_sel_res_all_star.
    def exitSingle_sel_res_all_star(self, ctx:DiffSqlParser.Single_sel_res_all_starContext):
        pass


    # Enter a parse tree produced by DiffSqlParser#single_sel_res_tab_star.
    def enterSingle_sel_res_tab_star(self, ctx:DiffSqlParser.Single_sel_res_tab_starContext):
        pass

    # Exit a parse tree produced by DiffSqlParser#single_sel_res_tab_star.
    def exitSingle_sel_res_tab_star(self, ctx:DiffSqlParser.Single_sel_res_tab_starContext):
        pass


    # Enter a parse tree produced by DiffSqlParser#single_sel_res_val.
    def enterSingle_sel_res_val(self, ctx:DiffSqlParser.Single_sel_res_valContext):
        pass

    # Exit a parse tree produced by DiffSqlParser#single_sel_res_val.
    def exitSingle_sel_res_val(self, ctx:DiffSqlParser.Single_sel_res_valContext):
        pass


    # Enter a parse tree produced by DiffSqlParser#single_sel_res_col.
    def enterSingle_sel_res_col(self, ctx:DiffSqlParser.Single_sel_res_colContext):
        pass

    # Exit a parse tree produced by DiffSqlParser#single_sel_res_col.
    def exitSingle_sel_res_col(self, ctx:DiffSqlParser.Single_sel_res_colContext):
        pass


    # Enter a parse tree produced by DiffSqlParser#select_result.
    def enterSelect_result(self, ctx:DiffSqlParser.Select_resultContext):
        pass

    # Exit a parse tree produced by DiffSqlParser#select_result.
    def exitSelect_result(self, ctx:DiffSqlParser.Select_resultContext):
        pass


    # Enter a parse tree produced by DiffSqlParser#single_name.
    def enterSingle_name(self, ctx:DiffSqlParser.Single_nameContext):
        pass

    # Exit a parse tree produced by DiffSqlParser#single_name.
    def exitSingle_name(self, ctx:DiffSqlParser.Single_nameContext):
        pass


    # Enter a parse tree produced by DiffSqlParser#sel_res_tab_star.
    def enterSel_res_tab_star(self, ctx:DiffSqlParser.Sel_res_tab_starContext):
        pass

    # Exit a parse tree produced by DiffSqlParser#sel_res_tab_star.
    def exitSel_res_tab_star(self, ctx:DiffSqlParser.Sel_res_tab_starContext):
        pass


    # Enter a parse tree produced by DiffSqlParser#sel_res_all_star.
    def enterSel_res_all_star(self, ctx:DiffSqlParser.Sel_res_all_starContext):
        pass

    # Exit a parse tree produced by DiffSqlParser#sel_res_all_star.
    def exitSel_res_all_star(self, ctx:DiffSqlParser.Sel_res_all_starContext):
        pass


    # Enter a parse tree produced by DiffSqlParser#as_name.
    def enterAs_name(self, ctx:DiffSqlParser.As_nameContext):
        pass

    # Exit a parse tree produced by DiffSqlParser#as_name.
    def exitAs_name(self, ctx:DiffSqlParser.As_nameContext):
        pass


    # Enter a parse tree produced by DiffSqlParser#single_expr.
    def enterSingle_expr(self, ctx:DiffSqlParser.Single_exprContext):
        pass

    # Exit a parse tree produced by DiffSqlParser#single_expr.
    def exitSingle_expr(self, ctx:DiffSqlParser.Single_exprContext):
        pass


    # Enter a parse tree produced by DiffSqlParser#opt_as_name.
    def enterOpt_as_name(self, ctx:DiffSqlParser.Opt_as_nameContext):
        pass

    # Exit a parse tree produced by DiffSqlParser#opt_as_name.
    def exitOpt_as_name(self, ctx:DiffSqlParser.Opt_as_nameContext):
        pass


    # Enter a parse tree produced by DiffSqlParser#sel_res_val.
    def enterSel_res_val(self, ctx:DiffSqlParser.Sel_res_valContext):
        pass

    # Exit a parse tree produced by DiffSqlParser#sel_res_val.
    def exitSel_res_val(self, ctx:DiffSqlParser.Sel_res_valContext):
        pass


    # Enter a parse tree produced by DiffSqlParser#single_col_ref.
    def enterSingle_col_ref(self, ctx:DiffSqlParser.Single_col_refContext):
        pass

    # Exit a parse tree produced by DiffSqlParser#single_col_ref.
    def exitSingle_col_ref(self, ctx:DiffSqlParser.Single_col_refContext):
        pass


    # Enter a parse tree produced by DiffSqlParser#sel_res_col.
    def enterSel_res_col(self, ctx:DiffSqlParser.Sel_res_colContext):
        pass

    # Exit a parse tree produced by DiffSqlParser#sel_res_col.
    def exitSel_res_col(self, ctx:DiffSqlParser.Sel_res_colContext):
        pass


    # Enter a parse tree produced by DiffSqlParser#comma_multi_single_source_comma.
    def enterComma_multi_single_source_comma(self, ctx:DiffSqlParser.Comma_multi_single_source_commaContext):
        pass

    # Exit a parse tree produced by DiffSqlParser#comma_multi_single_source_comma.
    def exitComma_multi_single_source_comma(self, ctx:DiffSqlParser.Comma_multi_single_source_commaContext):
        pass


    # Enter a parse tree produced by DiffSqlParser#single_single_source.
    def enterSingle_single_source(self, ctx:DiffSqlParser.Single_single_sourceContext):
        pass

    # Exit a parse tree produced by DiffSqlParser#single_single_source.
    def exitSingle_single_source(self, ctx:DiffSqlParser.Single_single_sourceContext):
        pass


    # Enter a parse tree produced by DiffSqlParser#opt_comma_multi_single_source_comma.
    def enterOpt_comma_multi_single_source_comma(self, ctx:DiffSqlParser.Opt_comma_multi_single_source_commaContext):
        pass

    # Exit a parse tree produced by DiffSqlParser#opt_comma_multi_single_source_comma.
    def exitOpt_comma_multi_single_source_comma(self, ctx:DiffSqlParser.Opt_comma_multi_single_source_commaContext):
        pass


    # Enter a parse tree produced by DiffSqlParser#multi_single_source_comma.
    def enterMulti_single_source_comma(self, ctx:DiffSqlParser.Multi_single_source_commaContext):
        pass

    # Exit a parse tree produced by DiffSqlParser#multi_single_source_comma.
    def exitMulti_single_source_comma(self, ctx:DiffSqlParser.Multi_single_source_commaContext):
        pass


    # Enter a parse tree produced by DiffSqlParser#from_list.
    def enterFrom_list(self, ctx:DiffSqlParser.From_listContext):
        pass

    # Exit a parse tree produced by DiffSqlParser#from_list.
    def exitFrom_list(self, ctx:DiffSqlParser.From_listContext):
        pass


    # Enter a parse tree produced by DiffSqlParser#single_join.
    def enterSingle_join(self, ctx:DiffSqlParser.Single_joinContext):
        pass

    # Exit a parse tree produced by DiffSqlParser#single_join.
    def exitSingle_join(self, ctx:DiffSqlParser.Single_joinContext):
        pass


    # Enter a parse tree produced by DiffSqlParser#join_multi_single_join_join.
    def enterJoin_multi_single_join_join(self, ctx:DiffSqlParser.Join_multi_single_join_joinContext):
        pass

    # Exit a parse tree produced by DiffSqlParser#join_multi_single_join_join.
    def exitJoin_multi_single_join_join(self, ctx:DiffSqlParser.Join_multi_single_join_joinContext):
        pass


    # Enter a parse tree produced by DiffSqlParser#single_single_join.
    def enterSingle_single_join(self, ctx:DiffSqlParser.Single_single_joinContext):
        pass

    # Exit a parse tree produced by DiffSqlParser#single_single_join.
    def exitSingle_single_join(self, ctx:DiffSqlParser.Single_single_joinContext):
        pass


    # Enter a parse tree produced by DiffSqlParser#opt_join_multi_single_join_join.
    def enterOpt_join_multi_single_join_join(self, ctx:DiffSqlParser.Opt_join_multi_single_join_joinContext):
        pass

    # Exit a parse tree produced by DiffSqlParser#opt_join_multi_single_join_join.
    def exitOpt_join_multi_single_join_join(self, ctx:DiffSqlParser.Opt_join_multi_single_join_joinContext):
        pass


    # Enter a parse tree produced by DiffSqlParser#multi_single_join_join.
    def enterMulti_single_join_join(self, ctx:DiffSqlParser.Multi_single_join_joinContext):
        pass

    # Exit a parse tree produced by DiffSqlParser#multi_single_join_join.
    def exitMulti_single_join_join(self, ctx:DiffSqlParser.Multi_single_join_joinContext):
        pass


    # Enter a parse tree produced by DiffSqlParser#join_clause.
    def enterJoin_clause(self, ctx:DiffSqlParser.Join_clauseContext):
        pass

    # Exit a parse tree produced by DiffSqlParser#join_clause.
    def exitJoin_clause(self, ctx:DiffSqlParser.Join_clauseContext):
        pass


    # Enter a parse tree produced by DiffSqlParser#opt_join_clause.
    def enterOpt_join_clause(self, ctx:DiffSqlParser.Opt_join_clauseContext):
        pass

    # Exit a parse tree produced by DiffSqlParser#opt_join_clause.
    def exitOpt_join_clause(self, ctx:DiffSqlParser.Opt_join_clauseContext):
        pass


    # Enter a parse tree produced by DiffSqlParser#join_source.
    def enterJoin_source(self, ctx:DiffSqlParser.Join_sourceContext):
        pass

    # Exit a parse tree produced by DiffSqlParser#join_source.
    def exitJoin_source(self, ctx:DiffSqlParser.Join_sourceContext):
        pass


    # Enter a parse tree produced by DiffSqlParser#from_source.
    def enterFrom_source(self, ctx:DiffSqlParser.From_sourceContext):
        pass

    # Exit a parse tree produced by DiffSqlParser#from_source.
    def exitFrom_source(self, ctx:DiffSqlParser.From_sourceContext):
        pass


    # Enter a parse tree produced by DiffSqlParser#single_from_source.
    def enterSingle_from_source(self, ctx:DiffSqlParser.Single_from_sourceContext):
        pass

    # Exit a parse tree produced by DiffSqlParser#single_from_source.
    def exitSingle_from_source(self, ctx:DiffSqlParser.Single_from_sourceContext):
        pass


    # Enter a parse tree produced by DiffSqlParser#from_clause.
    def enterFrom_clause(self, ctx:DiffSqlParser.From_clauseContext):
        pass

    # Exit a parse tree produced by DiffSqlParser#from_clause.
    def exitFrom_clause(self, ctx:DiffSqlParser.From_clauseContext):
        pass


    # Enter a parse tree produced by DiffSqlParser#single_source_func.
    def enterSingle_source_func(self, ctx:DiffSqlParser.Single_source_funcContext):
        pass

    # Exit a parse tree produced by DiffSqlParser#single_source_func.
    def exitSingle_source_func(self, ctx:DiffSqlParser.Single_source_funcContext):
        pass


    # Enter a parse tree produced by DiffSqlParser#single_source_table.
    def enterSingle_source_table(self, ctx:DiffSqlParser.Single_source_tableContext):
        pass

    # Exit a parse tree produced by DiffSqlParser#single_source_table.
    def exitSingle_source_table(self, ctx:DiffSqlParser.Single_source_tableContext):
        pass


    # Enter a parse tree produced by DiffSqlParser#single_source_subq.
    def enterSingle_source_subq(self, ctx:DiffSqlParser.Single_source_subqContext):
        pass

    # Exit a parse tree produced by DiffSqlParser#single_source_subq.
    def exitSingle_source_subq(self, ctx:DiffSqlParser.Single_source_subqContext):
        pass


    # Enter a parse tree produced by DiffSqlParser#single_source.
    def enterSingle_source(self, ctx:DiffSqlParser.Single_sourceContext):
        pass

    # Exit a parse tree produced by DiffSqlParser#single_source.
    def exitSingle_source(self, ctx:DiffSqlParser.Single_sourceContext):
        pass


    # Enter a parse tree produced by DiffSqlParser#source_table.
    def enterSource_table(self, ctx:DiffSqlParser.Source_tableContext):
        pass

    # Exit a parse tree produced by DiffSqlParser#source_table.
    def exitSource_table(self, ctx:DiffSqlParser.Source_tableContext):
        pass


    # Enter a parse tree produced by DiffSqlParser#source_subq.
    def enterSource_subq(self, ctx:DiffSqlParser.Source_subqContext):
        pass

    # Exit a parse tree produced by DiffSqlParser#source_subq.
    def exitSource_subq(self, ctx:DiffSqlParser.Source_subqContext):
        pass


    # Enter a parse tree produced by DiffSqlParser#source_func.
    def enterSource_func(self, ctx:DiffSqlParser.Source_funcContext):
        pass

    # Exit a parse tree produced by DiffSqlParser#source_func.
    def exitSource_func(self, ctx:DiffSqlParser.Source_funcContext):
        pass


    # Enter a parse tree produced by DiffSqlParser#and_or.
    def enterAnd_or(self, ctx:DiffSqlParser.And_orContext):
        pass

    # Exit a parse tree produced by DiffSqlParser#and_or.
    def exitAnd_or(self, ctx:DiffSqlParser.And_orContext):
        pass


    # Enter a parse tree produced by DiffSqlParser#and_or_multi_expr_and_or.
    def enterAnd_or_multi_expr_and_or(self, ctx:DiffSqlParser.And_or_multi_expr_and_orContext):
        pass

    # Exit a parse tree produced by DiffSqlParser#and_or_multi_expr_and_or.
    def exitAnd_or_multi_expr_and_or(self, ctx:DiffSqlParser.And_or_multi_expr_and_orContext):
        pass


    # Enter a parse tree produced by DiffSqlParser#opt_and_or_multi_expr_and_or.
    def enterOpt_and_or_multi_expr_and_or(self, ctx:DiffSqlParser.Opt_and_or_multi_expr_and_orContext):
        pass

    # Exit a parse tree produced by DiffSqlParser#opt_and_or_multi_expr_and_or.
    def exitOpt_and_or_multi_expr_and_or(self, ctx:DiffSqlParser.Opt_and_or_multi_expr_and_orContext):
        pass


    # Enter a parse tree produced by DiffSqlParser#multi_expr_and_or.
    def enterMulti_expr_and_or(self, ctx:DiffSqlParser.Multi_expr_and_orContext):
        pass

    # Exit a parse tree produced by DiffSqlParser#multi_expr_and_or.
    def exitMulti_expr_and_or(self, ctx:DiffSqlParser.Multi_expr_and_orContext):
        pass


    # Enter a parse tree produced by DiffSqlParser#where_clause.
    def enterWhere_clause(self, ctx:DiffSqlParser.Where_clauseContext):
        pass

    # Exit a parse tree produced by DiffSqlParser#where_clause.
    def exitWhere_clause(self, ctx:DiffSqlParser.Where_clauseContext):
        pass


    # Enter a parse tree produced by DiffSqlParser#single_group_clause.
    def enterSingle_group_clause(self, ctx:DiffSqlParser.Single_group_clauseContext):
        pass

    # Exit a parse tree produced by DiffSqlParser#single_group_clause.
    def exitSingle_group_clause(self, ctx:DiffSqlParser.Single_group_clauseContext):
        pass


    # Enter a parse tree produced by DiffSqlParser#opt_having_clause.
    def enterOpt_having_clause(self, ctx:DiffSqlParser.Opt_having_clauseContext):
        pass

    # Exit a parse tree produced by DiffSqlParser#opt_having_clause.
    def exitOpt_having_clause(self, ctx:DiffSqlParser.Opt_having_clauseContext):
        pass


    # Enter a parse tree produced by DiffSqlParser#gb_clause.
    def enterGb_clause(self, ctx:DiffSqlParser.Gb_clauseContext):
        pass

    # Exit a parse tree produced by DiffSqlParser#gb_clause.
    def exitGb_clause(self, ctx:DiffSqlParser.Gb_clauseContext):
        pass


    # Enter a parse tree produced by DiffSqlParser#comma_multi_grouping_term_comma.
    def enterComma_multi_grouping_term_comma(self, ctx:DiffSqlParser.Comma_multi_grouping_term_commaContext):
        pass

    # Exit a parse tree produced by DiffSqlParser#comma_multi_grouping_term_comma.
    def exitComma_multi_grouping_term_comma(self, ctx:DiffSqlParser.Comma_multi_grouping_term_commaContext):
        pass


    # Enter a parse tree produced by DiffSqlParser#single_grouping_term.
    def enterSingle_grouping_term(self, ctx:DiffSqlParser.Single_grouping_termContext):
        pass

    # Exit a parse tree produced by DiffSqlParser#single_grouping_term.
    def exitSingle_grouping_term(self, ctx:DiffSqlParser.Single_grouping_termContext):
        pass


    # Enter a parse tree produced by DiffSqlParser#opt_comma_multi_grouping_term_comma.
    def enterOpt_comma_multi_grouping_term_comma(self, ctx:DiffSqlParser.Opt_comma_multi_grouping_term_commaContext):
        pass

    # Exit a parse tree produced by DiffSqlParser#opt_comma_multi_grouping_term_comma.
    def exitOpt_comma_multi_grouping_term_comma(self, ctx:DiffSqlParser.Opt_comma_multi_grouping_term_commaContext):
        pass


    # Enter a parse tree produced by DiffSqlParser#multi_grouping_term_comma.
    def enterMulti_grouping_term_comma(self, ctx:DiffSqlParser.Multi_grouping_term_commaContext):
        pass

    # Exit a parse tree produced by DiffSqlParser#multi_grouping_term_comma.
    def exitMulti_grouping_term_comma(self, ctx:DiffSqlParser.Multi_grouping_term_commaContext):
        pass


    # Enter a parse tree produced by DiffSqlParser#group_clause.
    def enterGroup_clause(self, ctx:DiffSqlParser.Group_clauseContext):
        pass

    # Exit a parse tree produced by DiffSqlParser#group_clause.
    def exitGroup_clause(self, ctx:DiffSqlParser.Group_clauseContext):
        pass


    # Enter a parse tree produced by DiffSqlParser#grouping_term.
    def enterGrouping_term(self, ctx:DiffSqlParser.Grouping_termContext):
        pass

    # Exit a parse tree produced by DiffSqlParser#grouping_term.
    def exitGrouping_term(self, ctx:DiffSqlParser.Grouping_termContext):
        pass


    # Enter a parse tree produced by DiffSqlParser#and_multi_expr_and.
    def enterAnd_multi_expr_and(self, ctx:DiffSqlParser.And_multi_expr_andContext):
        pass

    # Exit a parse tree produced by DiffSqlParser#and_multi_expr_and.
    def exitAnd_multi_expr_and(self, ctx:DiffSqlParser.And_multi_expr_andContext):
        pass


    # Enter a parse tree produced by DiffSqlParser#opt_and_multi_expr_and.
    def enterOpt_and_multi_expr_and(self, ctx:DiffSqlParser.Opt_and_multi_expr_andContext):
        pass

    # Exit a parse tree produced by DiffSqlParser#opt_and_multi_expr_and.
    def exitOpt_and_multi_expr_and(self, ctx:DiffSqlParser.Opt_and_multi_expr_andContext):
        pass


    # Enter a parse tree produced by DiffSqlParser#multi_expr_and.
    def enterMulti_expr_and(self, ctx:DiffSqlParser.Multi_expr_andContext):
        pass

    # Exit a parse tree produced by DiffSqlParser#multi_expr_and.
    def exitMulti_expr_and(self, ctx:DiffSqlParser.Multi_expr_andContext):
        pass


    # Enter a parse tree produced by DiffSqlParser#having_clause.
    def enterHaving_clause(self, ctx:DiffSqlParser.Having_clauseContext):
        pass

    # Exit a parse tree produced by DiffSqlParser#having_clause.
    def exitHaving_clause(self, ctx:DiffSqlParser.Having_clauseContext):
        pass


    # Enter a parse tree produced by DiffSqlParser#comma_multi_ordering_term_comma.
    def enterComma_multi_ordering_term_comma(self, ctx:DiffSqlParser.Comma_multi_ordering_term_commaContext):
        pass

    # Exit a parse tree produced by DiffSqlParser#comma_multi_ordering_term_comma.
    def exitComma_multi_ordering_term_comma(self, ctx:DiffSqlParser.Comma_multi_ordering_term_commaContext):
        pass


    # Enter a parse tree produced by DiffSqlParser#single_ordering_term.
    def enterSingle_ordering_term(self, ctx:DiffSqlParser.Single_ordering_termContext):
        pass

    # Exit a parse tree produced by DiffSqlParser#single_ordering_term.
    def exitSingle_ordering_term(self, ctx:DiffSqlParser.Single_ordering_termContext):
        pass


    # Enter a parse tree produced by DiffSqlParser#opt_comma_multi_ordering_term_comma.
    def enterOpt_comma_multi_ordering_term_comma(self, ctx:DiffSqlParser.Opt_comma_multi_ordering_term_commaContext):
        pass

    # Exit a parse tree produced by DiffSqlParser#opt_comma_multi_ordering_term_comma.
    def exitOpt_comma_multi_ordering_term_comma(self, ctx:DiffSqlParser.Opt_comma_multi_ordering_term_commaContext):
        pass


    # Enter a parse tree produced by DiffSqlParser#multi_ordering_term_comma.
    def enterMulti_ordering_term_comma(self, ctx:DiffSqlParser.Multi_ordering_term_commaContext):
        pass

    # Exit a parse tree produced by DiffSqlParser#multi_ordering_term_comma.
    def exitMulti_ordering_term_comma(self, ctx:DiffSqlParser.Multi_ordering_term_commaContext):
        pass


    # Enter a parse tree produced by DiffSqlParser#orderby.
    def enterOrderby(self, ctx:DiffSqlParser.OrderbyContext):
        pass

    # Exit a parse tree produced by DiffSqlParser#orderby.
    def exitOrderby(self, ctx:DiffSqlParser.OrderbyContext):
        pass


    # Enter a parse tree produced by DiffSqlParser#asc_desc.
    def enterAsc_desc(self, ctx:DiffSqlParser.Asc_descContext):
        pass

    # Exit a parse tree produced by DiffSqlParser#asc_desc.
    def exitAsc_desc(self, ctx:DiffSqlParser.Asc_descContext):
        pass


    # Enter a parse tree produced by DiffSqlParser#opt_asc_desc.
    def enterOpt_asc_desc(self, ctx:DiffSqlParser.Opt_asc_descContext):
        pass

    # Exit a parse tree produced by DiffSqlParser#opt_asc_desc.
    def exitOpt_asc_desc(self, ctx:DiffSqlParser.Opt_asc_descContext):
        pass


    # Enter a parse tree produced by DiffSqlParser#ordering_term.
    def enterOrdering_term(self, ctx:DiffSqlParser.Ordering_termContext):
        pass

    # Exit a parse tree produced by DiffSqlParser#ordering_term.
    def exitOrdering_term(self, ctx:DiffSqlParser.Ordering_termContext):
        pass


    # Enter a parse tree produced by DiffSqlParser#limit.
    def enterLimit(self, ctx:DiffSqlParser.LimitContext):
        pass

    # Exit a parse tree produced by DiffSqlParser#limit.
    def exitLimit(self, ctx:DiffSqlParser.LimitContext):
        pass


    # Enter a parse tree produced by DiffSqlParser#table_dot.
    def enterTable_dot(self, ctx:DiffSqlParser.Table_dotContext):
        pass

    # Exit a parse tree produced by DiffSqlParser#table_dot.
    def exitTable_dot(self, ctx:DiffSqlParser.Table_dotContext):
        pass


    # Enter a parse tree produced by DiffSqlParser#col_ref.
    def enterCol_ref(self, ctx:DiffSqlParser.Col_refContext):
        pass

    # Exit a parse tree produced by DiffSqlParser#col_ref.
    def exitCol_ref(self, ctx:DiffSqlParser.Col_refContext):
        pass


    # Enter a parse tree produced by DiffSqlParser#single_btwnexpr.
    def enterSingle_btwnexpr(self, ctx:DiffSqlParser.Single_btwnexprContext):
        pass

    # Exit a parse tree produced by DiffSqlParser#single_btwnexpr.
    def exitSingle_btwnexpr(self, ctx:DiffSqlParser.Single_btwnexprContext):
        pass


    # Enter a parse tree produced by DiffSqlParser#single_biexpr.
    def enterSingle_biexpr(self, ctx:DiffSqlParser.Single_biexprContext):
        pass

    # Exit a parse tree produced by DiffSqlParser#single_biexpr.
    def exitSingle_biexpr(self, ctx:DiffSqlParser.Single_biexprContext):
        pass


    # Enter a parse tree produced by DiffSqlParser#single_unexpr.
    def enterSingle_unexpr(self, ctx:DiffSqlParser.Single_unexprContext):
        pass

    # Exit a parse tree produced by DiffSqlParser#single_unexpr.
    def exitSingle_unexpr(self, ctx:DiffSqlParser.Single_unexprContext):
        pass


    # Enter a parse tree produced by DiffSqlParser#single_value.
    def enterSingle_value(self, ctx:DiffSqlParser.Single_valueContext):
        pass

    # Exit a parse tree produced by DiffSqlParser#single_value.
    def exitSingle_value(self, ctx:DiffSqlParser.Single_valueContext):
        pass


    # Enter a parse tree produced by DiffSqlParser#expr.
    def enterExpr(self, ctx:DiffSqlParser.ExprContext):
        pass

    # Exit a parse tree produced by DiffSqlParser#expr.
    def exitExpr(self, ctx:DiffSqlParser.ExprContext):
        pass


    # Enter a parse tree produced by DiffSqlParser#btwnexpr.
    def enterBtwnexpr(self, ctx:DiffSqlParser.BtwnexprContext):
        pass

    # Exit a parse tree produced by DiffSqlParser#btwnexpr.
    def exitBtwnexpr(self, ctx:DiffSqlParser.BtwnexprContext):
        pass


    # Enter a parse tree produced by DiffSqlParser#single_binaryop_no_andor.
    def enterSingle_binaryop_no_andor(self, ctx:DiffSqlParser.Single_binaryop_no_andorContext):
        pass

    # Exit a parse tree produced by DiffSqlParser#single_binaryop_no_andor.
    def exitSingle_binaryop_no_andor(self, ctx:DiffSqlParser.Single_binaryop_no_andorContext):
        pass


    # Enter a parse tree produced by DiffSqlParser#biexpr.
    def enterBiexpr(self, ctx:DiffSqlParser.BiexprContext):
        pass

    # Exit a parse tree produced by DiffSqlParser#biexpr.
    def exitBiexpr(self, ctx:DiffSqlParser.BiexprContext):
        pass


    # Enter a parse tree produced by DiffSqlParser#single_unaryop.
    def enterSingle_unaryop(self, ctx:DiffSqlParser.Single_unaryopContext):
        pass

    # Exit a parse tree produced by DiffSqlParser#single_unaryop.
    def exitSingle_unaryop(self, ctx:DiffSqlParser.Single_unaryopContext):
        pass


    # Enter a parse tree produced by DiffSqlParser#unexpr.
    def enterUnexpr(self, ctx:DiffSqlParser.UnexprContext):
        pass

    # Exit a parse tree produced by DiffSqlParser#unexpr.
    def exitUnexpr(self, ctx:DiffSqlParser.UnexprContext):
        pass


    # Enter a parse tree produced by DiffSqlParser#single_parenval.
    def enterSingle_parenval(self, ctx:DiffSqlParser.Single_parenvalContext):
        pass

    # Exit a parse tree produced by DiffSqlParser#single_parenval.
    def exitSingle_parenval(self, ctx:DiffSqlParser.Single_parenvalContext):
        pass


    # Enter a parse tree produced by DiffSqlParser#single_boolean.
    def enterSingle_boolean(self, ctx:DiffSqlParser.Single_booleanContext):
        pass

    # Exit a parse tree produced by DiffSqlParser#single_boolean.
    def exitSingle_boolean(self, ctx:DiffSqlParser.Single_booleanContext):
        pass


    # Enter a parse tree produced by DiffSqlParser#single_function.
    def enterSingle_function(self, ctx:DiffSqlParser.Single_functionContext):
        pass

    # Exit a parse tree produced by DiffSqlParser#single_function.
    def exitSingle_function(self, ctx:DiffSqlParser.Single_functionContext):
        pass


    # Enter a parse tree produced by DiffSqlParser#single_string.
    def enterSingle_string(self, ctx:DiffSqlParser.Single_stringContext):
        pass

    # Exit a parse tree produced by DiffSqlParser#single_string.
    def exitSingle_string(self, ctx:DiffSqlParser.Single_stringContext):
        pass


    # Enter a parse tree produced by DiffSqlParser#single_domain.
    def enterSingle_domain(self, ctx:DiffSqlParser.Single_domainContext):
        pass

    # Exit a parse tree produced by DiffSqlParser#single_domain.
    def exitSingle_domain(self, ctx:DiffSqlParser.Single_domainContext):
        pass


    # Enter a parse tree produced by DiffSqlParser#single_range.
    def enterSingle_range(self, ctx:DiffSqlParser.Single_rangeContext):
        pass

    # Exit a parse tree produced by DiffSqlParser#single_range.
    def exitSingle_range(self, ctx:DiffSqlParser.Single_rangeContext):
        pass


    # Enter a parse tree produced by DiffSqlParser#value.
    def enterValue(self, ctx:DiffSqlParser.ValueContext):
        pass

    # Exit a parse tree produced by DiffSqlParser#value.
    def exitValue(self, ctx:DiffSqlParser.ValueContext):
        pass


    # Enter a parse tree produced by DiffSqlParser#domain.
    def enterDomain(self, ctx:DiffSqlParser.DomainContext):
        pass

    # Exit a parse tree produced by DiffSqlParser#domain.
    def exitDomain(self, ctx:DiffSqlParser.DomainContext):
        pass


    # Enter a parse tree produced by DiffSqlParser#range.
    def enterRange(self, ctx:DiffSqlParser.RangeContext):
        pass

    # Exit a parse tree produced by DiffSqlParser#range.
    def exitRange(self, ctx:DiffSqlParser.RangeContext):
        pass


    # Enter a parse tree produced by DiffSqlParser#parenval.
    def enterParenval(self, ctx:DiffSqlParser.ParenvalContext):
        pass

    # Exit a parse tree produced by DiffSqlParser#parenval.
    def exitParenval(self, ctx:DiffSqlParser.ParenvalContext):
        pass


    # Enter a parse tree produced by DiffSqlParser#opt_arg_list.
    def enterOpt_arg_list(self, ctx:DiffSqlParser.Opt_arg_listContext):
        pass

    # Exit a parse tree produced by DiffSqlParser#opt_arg_list.
    def exitOpt_arg_list(self, ctx:DiffSqlParser.Opt_arg_listContext):
        pass


    # Enter a parse tree produced by DiffSqlParser#function.
    def enterFunction(self, ctx:DiffSqlParser.FunctionContext):
        pass

    # Exit a parse tree produced by DiffSqlParser#function.
    def exitFunction(self, ctx:DiffSqlParser.FunctionContext):
        pass


    # Enter a parse tree produced by DiffSqlParser#comma_multi_expr_comma.
    def enterComma_multi_expr_comma(self, ctx:DiffSqlParser.Comma_multi_expr_commaContext):
        pass

    # Exit a parse tree produced by DiffSqlParser#comma_multi_expr_comma.
    def exitComma_multi_expr_comma(self, ctx:DiffSqlParser.Comma_multi_expr_commaContext):
        pass


    # Enter a parse tree produced by DiffSqlParser#opt_comma_multi_expr_comma.
    def enterOpt_comma_multi_expr_comma(self, ctx:DiffSqlParser.Opt_comma_multi_expr_commaContext):
        pass

    # Exit a parse tree produced by DiffSqlParser#opt_comma_multi_expr_comma.
    def exitOpt_comma_multi_expr_comma(self, ctx:DiffSqlParser.Opt_comma_multi_expr_commaContext):
        pass


    # Enter a parse tree produced by DiffSqlParser#multi_expr_comma.
    def enterMulti_expr_comma(self, ctx:DiffSqlParser.Multi_expr_commaContext):
        pass

    # Exit a parse tree produced by DiffSqlParser#multi_expr_comma.
    def exitMulti_expr_comma(self, ctx:DiffSqlParser.Multi_expr_commaContext):
        pass


    # Enter a parse tree produced by DiffSqlParser#arg_list.
    def enterArg_list(self, ctx:DiffSqlParser.Arg_listContext):
        pass

    # Exit a parse tree produced by DiffSqlParser#arg_list.
    def exitArg_list(self, ctx:DiffSqlParser.Arg_listContext):
        pass


    # Enter a parse tree produced by DiffSqlParser#boolean.
    def enterBoolean(self, ctx:DiffSqlParser.BooleanContext):
        pass

    # Exit a parse tree produced by DiffSqlParser#boolean.
    def exitBoolean(self, ctx:DiffSqlParser.BooleanContext):
        pass


    # Enter a parse tree produced by DiffSqlParser#compound_op.
    def enterCompound_op(self, ctx:DiffSqlParser.Compound_opContext):
        pass

    # Exit a parse tree produced by DiffSqlParser#compound_op.
    def exitCompound_op(self, ctx:DiffSqlParser.Compound_opContext):
        pass


    # Enter a parse tree produced by DiffSqlParser#binaryop.
    def enterBinaryop(self, ctx:DiffSqlParser.BinaryopContext):
        pass

    # Exit a parse tree produced by DiffSqlParser#binaryop.
    def exitBinaryop(self, ctx:DiffSqlParser.BinaryopContext):
        pass


    # Enter a parse tree produced by DiffSqlParser#binaryop_no_andor.
    def enterBinaryop_no_andor(self, ctx:DiffSqlParser.Binaryop_no_andorContext):
        pass

    # Exit a parse tree produced by DiffSqlParser#binaryop_no_andor.
    def exitBinaryop_no_andor(self, ctx:DiffSqlParser.Binaryop_no_andorContext):
        pass


    # Enter a parse tree produced by DiffSqlParser#unaryop.
    def enterUnaryop(self, ctx:DiffSqlParser.UnaryopContext):
        pass

    # Exit a parse tree produced by DiffSqlParser#unaryop.
    def exitUnaryop(self, ctx:DiffSqlParser.UnaryopContext):
        pass


    # Enter a parse tree produced by DiffSqlParser#string.
    def enterString(self, ctx:DiffSqlParser.StringContext):
        pass

    # Exit a parse tree produced by DiffSqlParser#string.
    def exitString(self, ctx:DiffSqlParser.StringContext):
        pass


    # Enter a parse tree produced by DiffSqlParser#name.
    def enterName(self, ctx:DiffSqlParser.NameContext):
        pass

    # Exit a parse tree produced by DiffSqlParser#name.
    def exitName(self, ctx:DiffSqlParser.NameContext):
        pass


    # Enter a parse tree produced by DiffSqlParser#number.
    def enterNumber(self, ctx:DiffSqlParser.NumberContext):
        pass

    # Exit a parse tree produced by DiffSqlParser#number.
    def exitNumber(self, ctx:DiffSqlParser.NumberContext):
        pass


    # Enter a parse tree produced by DiffSqlParser#comma.
    def enterComma(self, ctx:DiffSqlParser.CommaContext):
        pass

    # Exit a parse tree produced by DiffSqlParser#comma.
    def exitComma(self, ctx:DiffSqlParser.CommaContext):
        pass


    # Enter a parse tree produced by DiffSqlParser#and.
    def enterAnd(self, ctx:DiffSqlParser.AndContext):
        pass

    # Exit a parse tree produced by DiffSqlParser#and.
    def exitAnd(self, ctx:DiffSqlParser.AndContext):
        pass


    # Enter a parse tree produced by DiffSqlParser#or.
    def enterOr(self, ctx:DiffSqlParser.OrContext):
        pass

    # Exit a parse tree produced by DiffSqlParser#or.
    def exitOr(self, ctx:DiffSqlParser.OrContext):
        pass


    # Enter a parse tree produced by DiffSqlParser#join.
    def enterJoin(self, ctx:DiffSqlParser.JoinContext):
        pass

    # Exit a parse tree produced by DiffSqlParser#join.
    def exitJoin(self, ctx:DiffSqlParser.JoinContext):
        pass


    # Enter a parse tree produced by DiffSqlParser#distinct.
    def enterDistinct(self, ctx:DiffSqlParser.DistinctContext):
        pass

    # Exit a parse tree produced by DiffSqlParser#distinct.
    def exitDistinct(self, ctx:DiffSqlParser.DistinctContext):
        pass



del DiffSqlParser