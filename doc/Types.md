<h3>Types</h3>

This page describes which types are supported by the compiler.

<h3>Literals</h3>

<h4>Char Literal</h4>

We recognize a character literal as a single-quote enclosed element of the following types:

<ul>
    <li>basic source character set minus single-quote ('), backslash (\), or the newline character</li>
    <li>character escape sequence</li>
    <li><del>octal escape sequence</del></li>
    <li><del>hexadecimal escape sequence</del></li>
</ul>

<h4>String Literal</h4>

We recognize a string literal as a double-quote enclosed series of elements of the following types:
<ul>
    <li>basic source character set minus double-quote ("), backslash (\), or the newline character</li>
    <li>character escape sequence</li>
    <li><del>octal escape sequence</del></li>
    <li><del>hexadecimal escape sequence</del></li>
</ul>

String literals will be interpreted as char arrays of the length of the string literal plus one. The plus one accommodates
the null terminator of the string. All string literals will automatically have a null terminator added during the compilation
process.

<h3>Array Type</h3>

An array may contain elements of the following types: int, float, char and their pointer equivalents. The following statements
correspond to the declaration of arrays of primitive and primitive pointer types respectively:

```
type identifier [ int-literal ]
type pointers-and-qualifiers identifier [ int-literal ]
```

Pointers to arrays are not supported.
