<h3>Output</h3>

The compiler takes in (an) input file(s) and outputs them in several possible output formats. The following formats are supported:

<ul>
    <li>dot</li>
    <li><s>llvm</s></li>
    <li><s>mips</s></li>
</ul>

<h3>Dot files</h3>

As of the <b style="color:darkred">11th April 2022</b>, The compiler will by default output two dot files. The first, beginTree.dot,
is the AST before any visitors passes while the second one, endTree.dot, is the AST after visitor passes.