
# parsetab.py
# This file is automatically generated. Do not edit.
# pylint: disable=W,C,R
_tabversion = '3.10'

_lr_method = 'LALR'

_lr_signature = "expressionAND BINCOMP BOOLEAN CONCAT FROM GROUP ID LIKE NOT NUMBER OR SELECT STRING WHERE XORexpression : term\n        bin_expr_term : '(' bin_expr ')'\n    \n        bin_expr_term : expression BINCOMP expression\n                      | expression LIKE expression\n        bin_expr      : bin_expr AND bin_expr\n                      | bin_expr OR bin_expr\n                      | bin_expr XOR bin_expr\n        expression    : expression '+' term\n                      | expression '-' term\n                      | expression CONCAT term\n        term          : term '*' factor\n                      | term '/' factor\n    \n        bin_expr   : NOT bin_expr_term\n    term : factor\n        factor : ID\n    \n        bin_expr : bin_expr_term\n                 | BOOLEAN\n        term     : STRING\n        factor   : NUMBER\n                 | function\n    \n        factor : '(' expression ')'\n    \n        function : ID '(' arglist ')'\n    arglist : \n        arglist : expression\n                | bin_expr\n    \n        arglist : arglist ',' expression\n                | arglist ',' bin_expr\n    "
    
_lr_action_items = {'STRING':([0,8,9,10,11,14,21,25,32,33,34,35,36,37,],[4,4,4,4,4,4,4,4,4,4,4,4,4,4,]),'ID':([0,8,9,10,11,12,13,14,21,25,32,33,34,35,36,37,],[5,5,5,5,5,5,5,5,5,5,5,5,5,5,5,5,]),'NUMBER':([0,8,9,10,11,12,13,14,21,25,32,33,34,35,36,37,],[6,6,6,6,6,6,6,6,6,6,6,6,6,6,6,6,]),'(':([0,5,8,9,10,11,12,13,14,21,25,32,33,34,35,36,37,],[8,14,8,8,8,8,8,8,21,21,21,21,8,8,21,21,21,]),'$end':([1,2,3,4,5,6,7,16,17,18,19,20,28,31,],[0,-1,-14,-18,-15,-19,-20,-8,-9,-10,-11,-12,-21,-22,]),'+':([1,2,3,4,5,6,7,15,16,17,18,19,20,23,28,30,31,39,41,43,44,],[9,-1,-14,-18,-15,-19,-20,9,-8,-9,-10,-11,-12,9,-21,9,-22,9,9,9,9,]),'-':([1,2,3,4,5,6,7,15,16,17,18,19,20,23,28,30,31,39,41,43,44,],[10,-1,-14,-18,-15,-19,-20,10,-8,-9,-10,-11,-12,10,-21,10,-22,10,10,10,10,]),'CONCAT':([1,2,3,4,5,6,7,15,16,17,18,19,20,23,28,30,31,39,41,43,44,],[11,-1,-14,-18,-15,-19,-20,11,-8,-9,-10,-11,-12,11,-21,11,-22,11,11,11,11,]),')':([2,3,4,5,6,7,14,15,16,17,18,19,20,22,23,24,26,27,28,29,30,31,38,40,41,42,43,44,45,46,47,],[-1,-14,-18,-15,-19,-20,-23,28,-8,-9,-10,-11,-12,31,-24,-25,-16,-17,-21,40,28,-22,-13,-2,-26,-27,-3,-4,-5,-6,-7,]),'BINCOMP':([2,3,4,5,6,7,16,17,18,19,20,23,28,30,31,39,41,],[-1,-14,-18,-15,-19,-20,-8,-9,-10,-11,-12,33,-21,33,-22,33,33,]),'LIKE':([2,3,4,5,6,7,16,17,18,19,20,23,28,30,31,39,41,],[-1,-14,-18,-15,-19,-20,-8,-9,-10,-11,-12,34,-21,34,-22,34,34,]),',':([2,3,4,5,6,7,14,16,17,18,19,20,22,23,24,26,27,28,31,38,40,41,42,43,44,45,46,47,],[-1,-14,-18,-15,-19,-20,-23,-8,-9,-10,-11,-12,32,-24,-25,-16,-17,-21,-22,-13,-2,-26,-27,-3,-4,-5,-6,-7,]),'AND':([2,3,4,5,6,7,16,17,18,19,20,24,26,27,28,29,31,38,40,42,43,44,45,46,47,],[-1,-14,-18,-15,-19,-20,-8,-9,-10,-11,-12,35,-16,-17,-21,35,-22,-13,-2,35,-3,-4,35,35,35,]),'OR':([2,3,4,5,6,7,16,17,18,19,20,24,26,27,28,29,31,38,40,42,43,44,45,46,47,],[-1,-14,-18,-15,-19,-20,-8,-9,-10,-11,-12,36,-16,-17,-21,36,-22,-13,-2,36,-3,-4,36,36,36,]),'XOR':([2,3,4,5,6,7,16,17,18,19,20,24,26,27,28,29,31,38,40,42,43,44,45,46,47,],[-1,-14,-18,-15,-19,-20,-8,-9,-10,-11,-12,37,-16,-17,-21,37,-22,-13,-2,37,-3,-4,37,37,37,]),'*':([2,3,4,5,6,7,16,17,18,19,20,28,31,],[12,-14,-18,-15,-19,-20,12,12,12,-11,-12,-21,-22,]),'/':([2,3,4,5,6,7,16,17,18,19,20,28,31,],[13,-14,-18,-15,-19,-20,13,13,13,-11,-12,-21,-22,]),'NOT':([14,21,32,35,36,37,],[25,25,25,25,25,25,]),'BOOLEAN':([14,21,32,35,36,37,],[27,27,27,27,27,27,]),}

_lr_action = {}
for _k, _v in _lr_action_items.items():
   for _x,_y in zip(_v[0],_v[1]):
      if not _x in _lr_action:  _lr_action[_x] = {}
      _lr_action[_x][_k] = _y
del _lr_action_items

_lr_goto_items = {'expression':([0,8,14,21,25,32,33,34,35,36,37,],[1,15,23,30,39,41,43,44,39,39,39,]),'term':([0,8,9,10,11,14,21,25,32,33,34,35,36,37,],[2,2,16,17,18,2,2,2,2,2,2,2,2,2,]),'factor':([0,8,9,10,11,12,13,14,21,25,32,33,34,35,36,37,],[3,3,3,3,3,19,20,3,3,3,3,3,3,3,3,3,]),'function':([0,8,9,10,11,12,13,14,21,25,32,33,34,35,36,37,],[7,7,7,7,7,7,7,7,7,7,7,7,7,7,7,7,]),'arglist':([14,],[22,]),'bin_expr':([14,21,32,35,36,37,],[24,29,42,45,46,47,]),'bin_expr_term':([14,21,25,32,35,36,37,],[26,26,38,26,26,26,26,]),}

_lr_goto = {}
for _k, _v in _lr_goto_items.items():
   for _x, _y in zip(_v[0], _v[1]):
       if not _x in _lr_goto: _lr_goto[_x] = {}
       _lr_goto[_x][_k] = _y
del _lr_goto_items
_lr_productions = [
  ("S' -> expression","S'",1,None,None,None),
  ('expression -> term','expression',1,'p_expr_term','parser.py',13),
  ('bin_expr_term -> ( bin_expr )','bin_expr_term',3,'p_binop_par','parser.py',18),
  ('bin_expr_term -> expression BINCOMP expression','bin_expr_term',3,'p_binop','parser.py',24),
  ('bin_expr_term -> expression LIKE expression','bin_expr_term',3,'p_binop','parser.py',25),
  ('bin_expr -> bin_expr AND bin_expr','bin_expr',3,'p_binop','parser.py',26),
  ('bin_expr -> bin_expr OR bin_expr','bin_expr',3,'p_binop','parser.py',27),
  ('bin_expr -> bin_expr XOR bin_expr','bin_expr',3,'p_binop','parser.py',28),
  ('expression -> expression + term','expression',3,'p_binop','parser.py',29),
  ('expression -> expression - term','expression',3,'p_binop','parser.py',30),
  ('expression -> expression CONCAT term','expression',3,'p_binop','parser.py',31),
  ('term -> term * factor','term',3,'p_binop','parser.py',32),
  ('term -> term / factor','term',3,'p_binop','parser.py',33),
  ('bin_expr -> NOT bin_expr_term','bin_expr',2,'p_unary','parser.py',39),
  ('term -> factor','term',1,'p_term_factor','parser.py',44),
  ('factor -> ID','factor',1,'p_factor_id','parser.py',49),
  ('bin_expr -> bin_expr_term','bin_expr',1,'p_identity','parser.py',55),
  ('bin_expr -> BOOLEAN','bin_expr',1,'p_identity','parser.py',56),
  ('term -> STRING','term',1,'p_identity','parser.py',57),
  ('factor -> NUMBER','factor',1,'p_identity','parser.py',58),
  ('factor -> function','factor',1,'p_identity','parser.py',59),
  ('factor -> ( expression )','factor',3,'p_factor_expr','parser.py',66),
  ('function -> ID ( arglist )','function',4,'p_function','parser.py',72),
  ('arglist -> <empty>','arglist',0,'p_arglist_empty','parser.py',77),
  ('arglist -> expression','arglist',1,'p_arglist2','parser.py',82),
  ('arglist -> bin_expr','arglist',1,'p_arglist2','parser.py',83),
  ('arglist -> arglist , expression','arglist',3,'p_arglist','parser.py',89),
  ('arglist -> arglist , bin_expr','arglist',3,'p_arglist','parser.py',90),
]
