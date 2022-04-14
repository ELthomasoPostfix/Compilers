from src.ASTree.Element import ASTreeVisitor
from src.ASTree.ASTree import ASTree
from src.Nodes.BuiltinInfo import BuiltinNames
from src.SymbolTable import Record, SymbolTable, CType, VariableCType, TypeList
from abc import ABCMeta, abstractmethod


class TypedNode(ASTree):
    __metaclass__ = ABCMeta

    """An abstract base class for nodes that are registered into the symbol table."""
    def __init__(self, value, name, parent=None):
        super().__init__(value, name, parent)
        self.record: Record = None

    def __repr__(self):
        return self.__str__() + "\\n" + str(self.record)

    def __str__(self):
        return self.value


class ScopedNode(ASTree):
    __metaclass__ = ABCMeta

    """
    An abstract base class for nodes that are require a reference to a symbol table,
    as they introduce a new scope.
    """

    def __init__(self, value, name, parent=None):
        super().__init__(value, name, parent)
        self.symbolTable: SymbolTable = None

    def __repr__(self):
        return self.__str__() + f"\\nhasST: {self.symbolTable is not None}"

    def __str__(self):
        return super().__str__()


class CfileNode(ASTree):
    def accept(self, visitor: ASTreeVisitor):
        visitor.visitCfile(self)


class BlockNode(ScopedNode):
    def accept(self, visitor: ASTreeVisitor):
        visitor.visitBlock(self)


class CompoundstatementNode(ScopedNode):
    def accept(self, visitor: ASTreeVisitor):
        visitor.visitCompoundstatement(self)


class StatementNode(ASTree):
    def accept(self, visitor: ASTreeVisitor):
        visitor.visitStatement(self)


class IterationstatementNode(ScopedNode):
    def accept(self, visitor: ASTreeVisitor):
        visitor.visitIterationstatement(self)


class JumpstatementNode(ScopedNode):
    def accept(self, visitor: ASTreeVisitor):
        visitor.visitJumpstatement(self)


class SelectionstatementNode(ScopedNode):
    def accept(self, visitor: ASTreeVisitor):
        visitor.visitSelectionstatement(self)


class NullstatementNode(ASTree):
    def accept(self, visitor: ASTreeVisitor):
        visitor.visitStatement(self)

    def __repr__(self):
        return self.name


# TODO  Give an expression a type member: char c = 1.1 / 4.1 MUST result in compile error due to lack of implicit conversions???
class ExpressionNode(ASTree):
    def accept(self, visitor: ASTreeVisitor):
        visitor.visitExpression(self)

    @abstractmethod
    def inferType(self, typeList: TypeList) -> CType:   # TODO extrapolate to ExpressionNode inheritors: UnaryexpressionNode, BinaryopNode
        return VariableCType(typeList[BuiltinNames.VOID]) # TODO  TypeList does not globally initialize
        # TODO   with the builtin types yet, so an instance would have to be passed.
        # TODO   Also, are the CType class derivatives and Literal class derivatives mutually exclusive???


## An recursive instance of an ExpressionNode.
# Provides an interface to infer the CType type of the result of the unary expression through UnaryexpressionNode::inferType.
#
class UnaryexpressionNode(ExpressionNode):
    def accept(self, visitor: ASTreeVisitor):
        visitor.visitUnaryexpression(self)

    ## Retrieve the CType type of the result of the binary unary expression.
    def inferType(self, typeList: TypeList) -> CType:
        pass # TODO  Handle the following cases: deref, addr-of, +, -


class UnaryopNode(ASTree):
    def accept(self, visitor: ASTreeVisitor):
        visitor.visitUnaryop(self)

    def __repr__(self):
        return self.value


class Var_declNode(ASTree):
    def accept(self, visitor: ASTreeVisitor):
        visitor.visitVar_decl(self)


class Var_assigNode(ASTree):
    def accept(self, visitor: ASTreeVisitor):
        visitor.visitVar_assig(self)


class DeclaratorNode(ASTree):
    def accept(self, visitor: ASTreeVisitor):
        visitor.visitDeclarator(self)


class ArrayDeclaratorNode(DeclaratorNode):
    def accept(self, visitor: ASTreeVisitor):
        visitor.visitDeclarator(self)

class TypedeclarationNode(ASTree):
    def __init__(self, value, name, const: bool = False):
        super().__init__(value, name)
        self.const: bool = const

    def accept(self, visitor: ASTreeVisitor):
        visitor.visitTypedeclaration(self)


class QualifiersNode(ASTree):
    def accept(self, visitor: ASTreeVisitor):
        visitor.visitQualifiers(self)


class QualifierNode(ASTree):
    def accept(self, visitor: ASTreeVisitor):
        visitor.visitQualifier(self)

    def __repr__(self):
        return self.value


class TypequalifierNode(ASTree):
    def accept(self, visitor: ASTreeVisitor):
        visitor.visitTypequalifier(self)

    def __repr__(self):
        return self.value


class TypespecifierNode(ASTree):
    def accept(self, visitor: ASTreeVisitor):
        visitor.visitTypespecifier(self)

    def __repr__(self):
        return self.value

## An atomic instance of an ExpressionNode.
# Provides an interface to infer the type of its concrete instantiations through LiteralNode::inferType.
# Provides an interface needed for built-in type conversions, see LiteralNode::rank.
#
class LiteralNode(ExpressionNode):
    """
    An atomic instance of an ExpressionNode.
    """
    def accept(self, visitor: ASTreeVisitor):
        visitor.visitLiteral(self)

    ## Retrieve the CType type of the concrete LiteralNode (built-in type).
    @abstractmethod
    def inferType(self, typeList: TypeList) -> CType:
        pass

    ## Retrieve the rank of the concrete LiteralNode (built-in type).
    def rank(self) -> int:
        pass

    def getValue(self):
        pass

    def __repr__(self):
        return self.getValue()


class IdentifierNode(TypedNode):
    def accept(self, visitor: ASTreeVisitor):
        visitor.visitIdentifier(self)


# TODO  make sure function inherits from TypedNode
# TODO  make sure function inherits from TypedNode
# TODO  make sure function inherits from TypedNode

## An recursive instance of an ExpressionNode.
# Provides an interface to infer the CType return type of the function call through FunctioncallNode::inferType.
#
class FunctioncallNode(ExpressionNode):  # TODO children: [IdentifierNode -> stores SymbolTable record (has type), arguments]
    def accept(self, visitor: ASTreeVisitor):
        #visitor.visitFunctioncall(self)
        pass

    ## Retrieve the CType return type of the function call.
    def inferType(self, typeList: TypeList) -> CType:
        return self.getChild(0).record.type
# TODO  make sure function inherits from TypedNode
# TODO  make sure function inherits from TypedNode
# TODO  make sure function inherits from TypedNode


## An recursive instance of an ExpressionNode.
# Provides an interface to infer the CType type of the result of the binary expression through BinaryopNode::inferType.
#
class BinaryopNode(ExpressionNode):
    def accept(self, visitor: ASTreeVisitor):
        visitor.visitBinaryop(self)

    ## Retrieve the CType type of the result of the binary expression.
    def inferType(self, typeList: TypeList) -> CType:
        lType = self.getChild(0).inferType(typeList)
        rType = self.getChild(1).inferType(typeList)
        # TODO return promote(lType, rType) # ???????
        return VariableCType(typeList[BuiltinNames.VOID])

    def evaluate(self, left: LiteralNode, right: LiteralNode):
        pass


class PointerNode(ASTree):
    def accept(self, visitor: ASTreeVisitor):
        visitor.visitPointer(self)

    def __repr__(self):
        return self.value
