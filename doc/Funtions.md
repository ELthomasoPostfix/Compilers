<h3>Functions</h3>

This page details which function declaration and definition syntax are supported by the compiler and actually get correctly compiled.
It may be the case that some declaration syntax gets recognized by the compiler, but does not result in functioning output LLVM or MIPS.

<h4>Function Declaration</h4>

A single function declaration syntax is supported,

```
type-declaration identifier [ parameter-list ]
```

where ```type-declaration``` is any base type of pointer type and ```parameter-list``` is either the singular keyword void
or a comma separated list of basic type or pointer type declarations.