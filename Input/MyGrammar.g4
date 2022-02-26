// PARSER RULES

grammar MyGrammar;

exp: valueexp ';';

valueexp
    : '(' valueexp ')'
    | valueexp bop valueexp
    | value
    ;

value
    : UOP value
    | INT
    ;
bop
    : BOP
    | LOP
    | COP
    ;


// LEXER RULES

BOP:    '+' | '-' | '*' | '/' | '>' | '<' | '%' | '==' ;
UOP:    '+' | '-' ;
LOP:    '!' | '&&' | '||' ;
COP:    '<=' | '>=' | '!=' ;
INT:    [0-9]+ ;
WS :    [ \r\t\n]+ -> skip ;
