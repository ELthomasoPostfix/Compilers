// PARSER RULES
/* Always attempt to avoid reuse of a grammar variable as
 * the first symbol in a production body. Do not use
 *      exp -> exp op exp | value
 * but instead use
 *      exp -> value op exp | value
 */

grammar MyGrammar;

statement: expression ';';

valueexp
    : LPAREN valueexp RPAREN
    | valueexp bop valueexp
    | value
    ;

value
    :

///////////////////////////////////////////
//              LEXER RULES              //
///////////////////////////////////////////
WS :        [ \r\t\n]+ -> skip ;
INCR:       '++'
    ;
DECR:       '--'
    ;
LPAREN:     '('
    ;
RPAREN:     ')'
    ;
MUL:        '*'
    ;
DIV:        '/'
    ;
MOD:        '%'
    ;
EQUAL:      '=='
    ;
PLUS:       '+'
    ;
MIN:        '-'
    ;
LESS:       '<'
    ;
GREAT:      '>'
    ;
AND:        '&&'
    ;
OR:         '||'
    ;
LESSEQ:     '<='
    ;
GREATEQ:    '>='
    ;
NOT:        '!='
    ;
TYPE:       'char' | 'int' | 'float'
    ;
INT:        [0-9]+
    ;
FLOAT:      [0-9] + ('.' [0-9]+)?
    ;
POINT:      '*'
    ;
REF:        '&'
    ;
ID:        [a-zA-Z]+
///////////////////////////////////////////