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
    :(statement | (functiondefinition))*
    ;

statement
    : expressionstatement
    | compoundstatement
    | labelstatement
    | selectionstatement
    | iterationstatement
    | jumpstatement
    | nullstatement
    | var_decl   SEMICOLON
    | var_assig  SEMICOLON
    | 'printf' LPAREN (expression) RPAREN  // TODO un-hack
    ;

expressionstatement
    : expression SEMICOLON
    ;

compoundstatement
    : LBRACE (statement)* RBRACE        // TODO   '(statements)*' > 'block' ???
    ;

labelstatement
    : identifier COLON statement
    // | CASE constantexpression COLON statement       // TODO  introduce constantexpression for switch to allow cases
    | DEFAULT COLON statement
    ;

selectionstatement
    :   IF LPAREN expression RPAREN statement selectionelse?     # ifstatement
    ;

selectionelse
    : (ELSE statement)
    ;

iterationstatement
    :   WHILE LPAREN expression RPAREN statement                # whilestatement
    |   DO statement WHILE LPAREN expression RPAREN SEMICOLON   # dowhilestatement
    |   FOR LPAREN forCondition RPAREN statement                # forstatement
    ;

jumpstatement
    : ((CONTINUE | BREAK) | RETURN expression?) SEMICOLON
    ;

nullstatement
    : SEMICOLON
    ;


// An expression must be reducible to some typed value (rval?).
expression
    : LPAREN expression RPAREN                              # parenthesisexp
    | unaryop* lvalue (INCR | DECR)                         # unarypostfixexp
    | (INCR | DECR) unaryop* lvalue                         # unaryprefixexp
    | unaryop+ expression                                   # unaryexp
    | expression (STAR | DIV | MOD) expression              # multiplicationexp
    | expression (PLUS | MIN) expression                    # addexp
    | expression ((LT | LTE) | (GT | GTE)) expression       # relationalexp
    | expression (EQ | NEQ) expression                      # equalityexp
    | expression AND expression                             # andexp
    | expression OR expression                              # orexp
    | rvalue                                                # rvalueexp
    ;

// INCR and DECR unary operators con ONLY appear immediately beside a variable
// identifier of a pointer type (pointer arithmetic)
unaryexpression
    : unaryop* lvalue (INCR | DECR)
    | (INCR | DECR) unaryop* lvalue
    | unaryop+ expression
    ;

unaryop
    : (PLUS | MIN)
    |  NOT
    | (STAR | REF)
    ;

forCondition
	:   forinitclause? SEMICOLON forexpression? SEMICOLON forexpression?
	;

forinitclause
    : var_decl
    | expression
    ;

forexpression
    : expression
    ;

var_decl
    : typedeclaration declarator assignment?
    ;

// TODO  assigning to expression is very wide --> Many semantic checks
//      ==> the problem lies with 'lvalue assignment' rule not taking into account
//      any unary operations for the left hand side in an assignment, e.g.
//      int* i;
//      *i = &some_other_int;
//      ==> incorporate '*' unary operator into lvalue somehow
var_assig
    : (lvalue | expression) assignment
    ;

assignment
    : ASSIG expression
    ;

functiondefinition
    : typedeclaration declarator compoundstatement
    ;

expressionlist
    : expression (COMMA expression)*
    ;

// TODO  check https://devdocs.io/c/language/compatible_type#Type_groups
//   Replacing xBRACE by xPAREN would result in function def?
declarator
    : pointersandqualifiers? noptrdeclarator
    ;

pointersandqualifiers
    : (pointer qualifiers?)+
    ;

noptrdeclarator
    : identifier
    | LPAREN declarator RPAREN
    | noptrdeclarator LBRACKET expression RBRACKET
    | noptrdeclarator LPAREN parameterlist? RPAREN
    ;

parameterlist
    : functionparameter (COMMA functionparameter)*
    | TYPE_VOID
    ;

functionparameter
    : typedeclaration declarator
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
    : QUALIFIER_CONST
    ;

typespecifier
    : (TYPE_VOID
    |  TYPE_CHAR
    |  SPECIFIER_SHORT
    |  TYPE_INT
    |  SPECIFIER_LONG
    |  TYPE_FLOAT
    |  TYPE_DOUBLE
    |  SPECIFIER_SIGNED
    |  SPECIFIER_UNSIGNED)
    ;

pointer
    : STAR
    ;

lvalue
    // atomary lvalues
    : identifier                            # lvalueidentifier
    // lvalue operations
    | LITERAL_STRING                        # lvalueliteralstring
    | LPAREN lvalue RPAREN                  # lvalueparenthesis
    | lvalue LBRACKET expression RBRACKET   # lvaluearraysubscript
    | lvalue LPAREN expressionlist? RPAREN  # lvaluefunctioncall
    ;

rvalue
    : literal
    | lvalue       // TODO  should &/REF be part of unaryop?
    ;

literal
    : LITERAL_INT
    | LITERAL_FLOAT
    | LITERAL_CHAR
    | LITERAL_STRING
    ;

identifier
    : ID
    ;

///////////////////////////////////////////
//              LEXER RULES              //
///////////////////////////////////////////

WS:                 [ \r\t\n]+ -> skip
    ;
LINE_COMMENT:       '//' ~[\r\n]* -> skip
    ;
MULTI_LINE_COMMENT: '/*' .*? '*/' -> skip
    ;

SEMICOLON:  ';'
    ;
COLON:      ':'
    ;
COMMA:      ','
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
SINGLE_QUOTE:   '\''
    ;
DOUBLE_QUOTE:   '"'
    ;

// QUALIFIER KEYWORDS

QUALIFIER_CONST:    'const'
    ;

// TYPE SPECIFIER KEYWORDS

SPECIFIER_SIGNED:    'signed'
    ;
SPECIFIER_UNSIGNED: 'unsigned'
    ;
SPECIFIER_LONG:     'long'
    ;
SPECIFIER_SHORT:    'short'
    ;

// CONTROL KEYWORDS

IF:         'if'
    ;
ELSE:       'else'
    ;
WHILE:      'while'
    ;
DO:         'do'
    ;
FOR:        'for'
    ;
BREAK:      'break'
    ;
CONTINUE:   'continue'
    ;
SWITCH:     'switch'
    ;
DEFAULT:    'default'
    ;


RETURN:     'return'
    ;

// BUILT-IN TYPES

TYPE_VOID:     'void'
    ;
TYPE_CHAR:     'char'
    ;
TYPE_DOUBLE:   'double'
    ;
TYPE_FLOAT:    'float'
    ;
TYPE_INT:      'int'
    ;

// LITERALS

ID:         [a-zA-Z_]+[a-zA-Z0-9_]*
    ;
fragment NAT:   [0-9]+
    ;
LITERAL_INT:        NAT
    ;
LITERAL_FLOAT:      (NAT ('.' NAT?)?) | (NAT? '.' NAT)
    ;

LITERAL_CHAR:   SINGLE_QUOTE CCHAR? SINGLE_QUOTE
    ;
LITERAL_STRING
    :   DOUBLE_QUOTE SCharSequence? DOUBLE_QUOTE
    ;
fragment CCHAR
    :       ~['\\\n]
    |       ESCAPE_SEQUENCE
    ;
fragment ESCAPE_SEQUENCE
    :   CHARACTER_ESCAPE_SEQUENCE
    |   OCTYPE_ESCAPE_SEQUENCE
    |   HEX_ESCAPE_SEQUENCE
    ;
fragment CHARACTER_ESCAPE_SEQUENCE
    :   '\\' ['"?abfnrtv\\]
    ;
fragment OCTYPE_DIG
    :   [0-7]
    ;
fragment OCTYPE_ESCAPE_SEQUENCE
    :   '\\' OCTYPE_DIG OCTYPE_DIG? OCTYPE_DIG?
    ;
fragment HEX_DIG
    :    [0-9a-fA-F]
    ;
fragment HEX_ESCAPE_SEQUENCE
    :   '\\x' HEX_DIG HEX_DIG?
    ;
fragment SCharSequence
    :   SChar+
    ;
fragment SChar
    :   ~["\\\r\n]
    |   ESCAPE_SEQUENCE
    |   '\\\n'   // Added line
    |   '\\\r\n' // Added line
    ;
///////////////////////////////////////////