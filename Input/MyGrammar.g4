// PARSER RULES
/* Always attempt to avoid reuse of a grammar variable as
 * the first symbol in a production body. Do not use
 *      exp -> exp op exp | value
 * but instead use
 *      exp -> value op exp | value
 */

grammar MyGrammar;

cfile
    : block EOF
    ;

block
    : statement*
    ;

statement
    : expression ';'
    | var_decl ';'
    | var_assig ';'
    | 'printf' LPAREN (literal | lval) RPAREN  // TODO un-hack
    ;

// An expression must be reducible to some c_typed value (rval?).
expression
    : LPAREN expression RPAREN
    | lval (INCR | DECR) | (INCR | DECR) lval
    | unaryop+ (literal | lval)
    | expression (STAR | DIV | MOD) expression
    | expression (PLUS | MIN) expression
    | expression relationalop expression
    | lval
    | literal
    ;

unaryop
    : (PLUS | MIN)
    // TODO: BITWISE 'NOT' & 'AND'
    | (STAR | REF)
    ;

relationalop
    : (LT | LTE)
    | (GT | GTE)
    | (EQ | NEQ)
    | (AND | OR)
    ;

literal
    : INT
    | FLOAT
    ;

lval
    : ID
    ;

c_type
    : qualifier?          // prefix const
    ( T_INT
    | T_FLOAT
    | T_CHAR
    ) qualifier?          // postfix const
     (STAR+ qualifier?)?  // ptr, possibly const
    ;

qualifier
    : Q_CONST
    ;

var_decl
    : c_type ID
    | c_type ID ASSIG expression
    ;

var_assig
    : ID ASSIG expression
    ;


///////////////////////////////////////////
//              LEXER RULES              //
///////////////////////////////////////////

WS:         [ \r\t\n]+ -> skip
    ;


INCR:       '++'
    ;
DECR:       '--'
    ;
LPAREN:     '('
    ;
RPAREN:     ')'
    ;
STAR:       '*'        //Multiplication or Pointer
    ;
DIV:        '/'
    ;
MOD:        '%'
    ;
REF:        '&'
    ;
EQ:         '=='
    ;
PLUS:       '+'
    ;
MIN:        '-'
    ;
LT:         '<'
    ;
GT:         '>'
    ;
AND:        '&&'
    ;
OR:         '||'
    ;
LTE:        '<='
    ;
GTE:        '>='
    ;
NEQ:        '!='
    ;
ASSIG:      '='
    ;


Q_CONST:    'const'
    ;


T_CHAR:     'char'
    ;
T_FLOAT:    'float'
    ;
T_INT:      'int'
    ;


ID:         [a-zA-Z_]+[a-zA-Z0-9_]*
    ;
fragment NAT:   [0-9]+
    ;
INT:        NAT
    ;
FLOAT:      (NAT ('.' NAT?)?) | (NAT? '.' NAT)
    ;

///////////////////////////////////////////