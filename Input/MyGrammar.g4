// PARSER RULES

grammar MyGrammar;

exp
    : valueexp ';'
    ;

valueexp
    : '(' valueexp ')'
    | value bop valueexp
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

UOP:    [+-] ;
COP:    '<=' | '>=' | '!=' ;
BOP:    [+\-*/><%] | '==' ;
LOP:    '!' | '&&' | '||' ;
INT:    [0-9]+ ;
WS :    [ \r\t\n]+ -> skip ;
