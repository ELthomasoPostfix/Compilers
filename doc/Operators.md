<h3>Operators</h3>

This page gives an explanation on the effects of different operators.

<h4>Member Access Operators</h4>

Any occurrence of the following sequence is simply ignored when encountered:

```& * expression```

The two unary operators are never added to the AST, and thus neither operator is ever evaluated.

<h4>Array subscript operator</h4>

This operator is used in expressions of the form

```lvalue [ expression ]```

where ```lvalue``` is an array type or pointer type expression. Note that ```expression``` must evaluate to an interger
value. Should it evaluate to a negative integer value, undefined behavior occurs.