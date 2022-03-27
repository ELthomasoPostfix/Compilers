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
    : expression SEMICOLON
    | var_decl   SEMICOLON
    | var_assig  SEMICOLON
    | 'printf' LPAREN (expression) RPAREN  // TODO un-hack
    ;

// An expression must be reducible to some typed value (rval?).
expression
    : LPAREN expression RPAREN                              # parenthesisexp
    | unaryexpression                                       # unaryexp
    | expression (STAR | DIV | MOD) expression              # multiplicationexp
    | expression (PLUS | MIN) expression                    # addexp
    | expression ((LT | LTE) | (GT | GTE)) expression       # relationalexp
    | expression (EQ | NEQ) expression                      # equalityexp
    | expression AND expression                             # andexp
    | expression OR expression                              # orexp
    | identifier                                            # identifierexp
    | literal                                               # literalexp
    ;

unaryexpression
    : identifier (INCR | DECR)
    | (INCR | DECR) identifier
    | unaryop+ (literal | identifier)
    ;

unaryop
    : (PLUS | MIN)
    // TODO: BITWISE 'NOT' & 'AND'
    | NOT
    | STAR
    | REF
    ;

var_decl
    : typedeclaration declarator (ASSIG expression)?
    ;

var_assig
    : identifier ASSIG expression
    ;

declarator
    : identifier
    | LPAREN declarator RPAREN
    | (pointer qualifiers?)+ declarator
    | declarator LBRACE expression RBRACE
    ;

typedeclaration
    : (typequalifier | typespecifier)* typespecifier typequalifier?
    ;

qualifiers
    : qualifier+
    ;

qualifier
    : typequalifier
    ;

typequalifier
    : Q_CONST
    ;

typespecifier
    : (T_VOID
    |  T_CHAR
    |  S_SHORT
    |  T_INT
    |  S_LONG
    |  T_FLOAT
    |  T_DOUBLE
    |  S_SIGNED
    |  S_UNSIGNED)
    ;

pointer
    : STAR
    ;

literal
    : INT
    | FLOAT
    ;

identifier
    : ID
    ;

///////////////////////////////////////////
//              LEXER RULES              //
///////////////////////////////////////////

WS:         [ \r\t\n]+ -> skip
    ;
SEMICOLON:  ';'
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
LBRACKET:   '['
    ;
RBRACKET:   ']'
    ;
LBRACE:     '{'
    ;
RBRACE:     '}'
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


S_SIGNED:    'signed'
    ;
S_UNSIGNED: 'unsigned'
    ;
S_LONG:     'long'
    ;
S_SHORT:    'short'
    ;


T_VOID:      'void'
    ;
T_CHAR:     'char'
    ;
T_DOUBLE:   'double'
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