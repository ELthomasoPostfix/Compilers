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
    | 'printf' LPAREN (literal | var) RPAREN  // TODO un-hack
    ;

// An expression must be reducible to some c_typed value (rval?).
expression
    : LPAREN expression RPAREN                              # parenthesisexp
    | unaryexpression                                       # unaryexp
    | expression (STAR | DIV | MOD) expression              # multiplicationexp
    | expression (PLUS | MIN) expression                    # addexp
    | expression ((LT | LTE) | (GT | GTE)) expression       # relationalexp
    | expression (EQ | NEQ) expression                      # equalityexp
    | expression AND expression                             # andexp
    | expression OR expression                              # orexp
    | var                                                   # varexp
    | literal                                               # literalexp
    ;

unaryexpression
    : var (INCR | DECR)
    | (INCR | DECR) var
    | unaryop+ (literal | var)
    ;

unaryop
    : (PLUS | MIN)
    // TODO: BITWISE 'NOT' & 'AND'
    | NOT
    | STAR
    | REF
    ;

literal
    : INT
    | FLOAT
    ;

var
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
    : c_type var (ASSIG expression)?
    ;

var_assig
    : var ASSIG expression
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
NOT:        '!'
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