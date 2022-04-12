<h3>Types</h3>

This page describes which types are supported by the compiler.

<h3>Literals</h3>

<h4>Char Literal</h4>

We recognize a character literal as a single-quote enclosed element of the following types:

<ul>
    <li>basic source character set minus single-quote ('), backslash (\), or the newline character</li>
    <li>character escape sequence</li>
    <li>octal escape sequence</li>
    <li>hexadecimal escape sequence</li>
</ul>

<h4>String Literal</h4>

We recognize a string literal as a double-quote enclosed series of elements of the following types:
<ul>
    <li>basic source character set minus double-quote ("), backslash (\), or the newline character</li>
    <li>character escape sequence</li>
    <li>octal escape sequence</li>
    <li>hexadecimal escape sequence</li>
</ul>