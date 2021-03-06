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
    ;

expression
    : LPAREN expression RPAREN
    | unaryop* value
    | expression (STAR | DIV | MOD) expression
    | expression (PLUS | MIN) expression
    | expression relationalop expression
    ;

unaryop
    : (INCR | DECR)
    | (PLUS | MIN)
    // TODO: BITWISE 'NOT' & 'AND'
    | (STAR | REF)
    ;

relationalop
    : (LT | LTE)
    | (GT | GTE)
    | (EQ | NEQ)
    | (AND | OR)
    ;

value
    : INT
    | FLOAT
    ;

var
    : VAR
    ;


///////////////////////////////////////////
//              LEXER RULES              //
///////////////////////////////////////////

WS:        [ \r\t\n]+ -> skip
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
T_CHAR:     'char'
    ;
T_FLOAT:    'float'
    ;
T_INT:      'int'
    ;
VAR:         [a-zA-Z_]+ [a-zA-Z0-9_]*
    ;
fragment NAT:   [0-9]+
    ;
INT:        NAT
    ;
FLOAT:      (NAT ('.' NAT?)?) | (NAT? '.' NAT)
    ;

///////////////////////////////////////////