// PARSER RULES
/* Always attempt to avoid reuse of a grammar variable as
 * the first symbol in a production body. Do not use
 *      exp -> exp op exp | value
 * but instead use
 *      exp -> value op exp | value
 */

grammar MyGrammar;

exp: valueexp ';';

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

BOP:    [+\-*/><%] | '==';
UOP:    [+\-];
LOP:    '!' | '&&' | '||' ;
COP:    '<=' | '>=' | '!=' ;
INT:    [0-9]+ ;
WS :    [ \r\t\n]+ -> skip ;
