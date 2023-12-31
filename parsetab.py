
# parsetab.py
# This file is automatically generated. Do not edit.
# pylint: disable=W,C,R
_tabversion = '3.10'

_lr_method = 'LALR'

_lr_signature = 'COMP DIVIDE LOGIC LPAREN MINUS NAME NUMBER PLUS RPAREN STRING TIMES UNARY_LOGIC\n    bool_expr : UNARY_LOGIC bool_term\n    \n    bool_expr : bool_term LOGIC bool_term\n    \n    bool_expr : bool_term\n    \n    bool_term : expression COMP expression\n    \n    expression : term PLUS term\n               | term MINUS term\n    \n    expression : term\n    \n    term : factor TIMES factor\n         | factor DIVIDE factor\n    \n    term : factor\n    \n    factor : NUMBER\n    \n    factor : NAME\n    \n    factor : PLUS factor\n           | MINUS factor\n    \n    factor : LPAREN expression RPAREN\n    '
    
_lr_action_items = {'UNARY_LOGIC':([0,],[2,]),'NUMBER':([0,2,6,7,11,13,14,15,16,19,20,],[9,9,9,9,9,9,9,9,9,9,9,]),'NAME':([0,2,6,7,11,13,14,15,16,19,20,],[10,10,10,10,10,10,10,10,10,10,10,]),'PLUS':([0,2,5,6,7,8,9,10,11,13,14,15,16,17,18,19,20,26,27,28,],[6,6,15,6,6,-10,-11,-12,6,6,6,6,6,-13,-14,6,6,-8,-9,-15,]),'MINUS':([0,2,5,6,7,8,9,10,11,13,14,15,16,17,18,19,20,26,27,28,],[7,7,16,7,7,-10,-11,-12,7,7,7,7,7,-13,-14,7,7,-8,-9,-15,]),'LPAREN':([0,2,6,7,11,13,14,15,16,19,20,],[11,11,11,11,11,11,11,11,11,11,11,]),'$end':([1,3,5,8,9,10,12,17,18,22,23,24,25,26,27,28,],[0,-3,-7,-10,-11,-12,-1,-13,-14,-2,-4,-5,-6,-8,-9,-15,]),'LOGIC':([3,5,8,9,10,17,18,23,24,25,26,27,28,],[13,-7,-10,-11,-12,-13,-14,-4,-5,-6,-8,-9,-15,]),'COMP':([4,5,8,9,10,17,18,24,25,26,27,28,],[14,-7,-10,-11,-12,-13,-14,-5,-6,-8,-9,-15,]),'RPAREN':([5,8,9,10,17,18,21,24,25,26,27,28,],[-7,-10,-11,-12,-13,-14,28,-5,-6,-8,-9,-15,]),'TIMES':([8,9,10,17,18,28,],[19,-11,-12,-13,-14,-15,]),'DIVIDE':([8,9,10,17,18,28,],[20,-11,-12,-13,-14,-15,]),}

_lr_action = {}
for _k, _v in _lr_action_items.items():
   for _x,_y in zip(_v[0],_v[1]):
      if not _x in _lr_action:  _lr_action[_x] = {}
      _lr_action[_x][_k] = _y
del _lr_action_items

_lr_goto_items = {'bool_expr':([0,],[1,]),'bool_term':([0,2,13,],[3,12,22,]),'expression':([0,2,11,13,14,],[4,4,21,4,23,]),'term':([0,2,11,13,14,15,16,],[5,5,5,5,5,24,25,]),'factor':([0,2,6,7,11,13,14,15,16,19,20,],[8,8,17,18,8,8,8,8,8,26,27,]),}

_lr_goto = {}
for _k, _v in _lr_goto_items.items():
   for _x, _y in zip(_v[0], _v[1]):
       if not _x in _lr_goto: _lr_goto[_x] = {}
       _lr_goto[_x][_k] = _y
del _lr_goto_items
_lr_productions = [
  ("S' -> bool_expr","S'",1,None,None,None),
  ('bool_expr -> UNARY_LOGIC bool_term','bool_expr',2,'p_unary_2','query.py',45),
  ('bool_expr -> bool_term LOGIC bool_term','bool_expr',3,'p_logic_2','query.py',51),
  ('bool_expr -> bool_term','bool_expr',1,'p_bool_expr_2','query.py',57),
  ('bool_term -> expression COMP expression','bool_term',3,'p_bool_expr','query.py',63),
  ('expression -> term PLUS term','expression',3,'p_expression','query.py',69),
  ('expression -> term MINUS term','expression',3,'p_expression','query.py',70),
  ('expression -> term','expression',1,'p_expression_term','query.py',81),
  ('term -> factor TIMES factor','term',3,'p_term','query.py',87),
  ('term -> factor DIVIDE factor','term',3,'p_term','query.py',88),
  ('term -> factor','term',1,'p_term_factor','query.py',94),
  ('factor -> NUMBER','factor',1,'p_factor_number','query.py',100),
  ('factor -> NAME','factor',1,'p_factor_name','query.py',106),
  ('factor -> PLUS factor','factor',2,'p_factor_unary','query.py',112),
  ('factor -> MINUS factor','factor',2,'p_factor_unary','query.py',113),
  ('factor -> LPAREN expression RPAREN','factor',3,'p_factor_grouped','query.py',119),
]
