from __future__ import annotations

from typing import List

from src.ASTree.Element import ASTreeVisitor
from src.ASTree.ASTree import ASTree
from src.CompilersUtils import first
from src.Enumerations import BuiltinNames
from src.SymbolTable import Record, SymbolTable, CType, CType, TypeList, FunctionCType
from abc import ABCMeta, abstractmethod



class ExpressionNode(ASTree):
    def __init__(self, parent=None, location=None):
        super(ExpressionNode, self).__init__(parent, location=location)
        self.ershovNumber = 0

    def accept(self, visitor: ASTreeVisitor):
        visitor.visitExpression(self)

    @abstractmethod
    def inferType(self, typeList: TypeList) -> CType:
        return CType(typeList[BuiltinNames.VOID])

    @abstractmethod
    def evaluateErshovNumber(self):
        pass

    def ershovNumberIsEvaluated(self):
        return self.ershovNumber >= 1

    def sethiUllmanNumber(self, base: int):
        """
        Calculate the number of the register the callee expression
        will store its result in.

        :param base: The base in the Sethi-Ullman algorithm
        :return: The index of the expression's result register
        """

        return base + self.ershovNumber - 1


class TypedNode(ExpressionNode):
    __metaclass__ = ABCMeta

    """An abstract base class for nodes that are registered into the symbol table."""
    def __init__(self, parent=None, location = None):
        super().__init__(parent, location=location)
        self.record: Record | None = None

    def getType(self) -> CType:
        return self.record.type

    @abstractmethod
    def inferType(self, typeList: TypeList) -> CType:
        return super().inferType(typeList)

    @abstractmethod
    def evaluateErshovNumber(self):
        pass

    def __repr__(self):
        return self.__str__() + "\\n" + str(self.record)


class ScopedNode(ASTree):
    __metaclass__ = ABCMeta

    """
    An abstract base class for nodes that are require a reference to a symbol table,
    as they introduce a new scope.
    """

    def __init__(self, parent=None, location=None):
        super().__init__(parent, location)
        self.symbolTable: SymbolTable | None = None

    def __repr__(self):
        return self.__str__() + f"\\nhasST: {self.symbolTable is not None}"


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

    def __str__(self):
        return "no-op"


## An recursive instance of an ExpressionNode.
# Provides an interface to infer the CType type of the result of the unary expression through UnaryexpressionNode::inferType.
#
class UnaryexpressionNode(ExpressionNode):
    def accept(self, visitor: ASTreeVisitor):
        visitor.visitUnaryexpression(self)

    ## Retrieve the CType type of the result of the unary expression.
    def inferType(self, typeList: TypeList) -> CType:
        return self.getSubExpression().inferType(typeList)

    ## Retrieve the child of the unary expression that will be applied last of all operators or atoms
    def getSubExpression(self) -> ExpressionNode:
        """
        Retrieve the operator or atom (identifier or literal) that will
        be applied last in evaluating the unary expression.

        :return: The child applied last
        """

        return self.getChild(0)

    def evaluateErshovNumber(self):
        subExpression = self.getSubExpression()
        subExpression.evaluateErshovNumber()
        self.ershovNumber = subExpression.ershovNumber


class UnaryopNode(ExpressionNode):
    def accept(self, visitor: ASTreeVisitor):
        visitor.visitUnaryop(self)

    ## Retrieve the CType type of the result of the unary operation.
    @abstractmethod
    def inferType(self, typeList: TypeList):
        return self.getSubExpression().inferType(typeList)

    @abstractmethod
    def evaluate(self, value: LiteralNode):
        pass

    ## Get the expression the unary operator will be applied to
    def getSubExpression(self) -> ExpressionNode:
        """
        Get the expression the unary operator will be applied to

        :return: The sub expression of the operator
        """

        return self.parent.getChild(self.parent.children.index(self) + 1)

    def evaluateErshovNumber(self):
        subExpression = self.getSubExpression()
        subExpression.evaluateErshovNumber()
        self.ershovNumber = subExpression.ershovNumber


class IdentifierNode(TypedNode):
    def __init__(self, identifier: str, parent: ASTree = None, location = -1):
        super().__init__(parent, location=location)
        self.identifier: str = identifier

    def inferType(self, typeList: TypeList) -> CType:
        return self.getType()

    def accept(self, visitor: ASTreeVisitor):
        visitor.visitIdentifier(self)

    def evaluateErshovNumber(self):
        self.ershovNumber = 1

    def __str__(self):
        return self.identifier


class VariabledeclarationNode(ASTree):
    def accept(self, visitor: ASTreeVisitor):
        visitor.visitVariabledeclaration(self)

    def getDeclaratorNode(self) -> DeclaratorNode:
        return self.getChild(1)

    def getIdentifierNode(self) -> IdentifierNode:
        return first(self.getDeclaratorNode().children, lambda child: isinstance(child, IdentifierNode))


class FunctiondeclarationNode(ScopedNode):
    def accept(self, visitor: ASTreeVisitor):
        visitor.visitFunctiondeclaration(self)

    def getIdentifierNode(self) -> IdentifierNode:
        return first(self.getChild(1).children, lambda child: isinstance(child, IdentifierNode))


class FunctiondefinitionNode(ScopedNode):
    def accept(self, visitor: ASTreeVisitor):
        visitor.visitFunctiondefinition(self)

    def getIdentifierNode(self) -> IdentifierNode:
        return first(self.getChild(1).children, lambda child: isinstance(child, IdentifierNode))

    def getParamIdentifierNodes(self) -> List[IdentifierNode]:
        return [varDeclaration.getIdentifierNode() for varDeclaration in self.getChild(1).children if isinstance(varDeclaration, VariabledeclarationNode)]


class Var_assigNode(ASTree):
    def accept(self, visitor: ASTreeVisitor):
        visitor.visitVar_assig(self)

    def getIdentifierNode(self) -> IdentifierNode:
        return self.getChild(0)

class IncludedirectiveNode(ASTree):
    def accept(self, visitor: ASTreeVisitor):
        visitor.visitIncludedirective(self)



class DeclaratorNode(ASTree):
    def accept(self, visitor: ASTreeVisitor):
        visitor.visitDeclarator(self)

    def getIdentifierNode(self):
        return next(node for node in self.children if isinstance(node, IdentifierNode))


class ArrayDeclaratorNode(DeclaratorNode):
    def accept(self, visitor: ASTreeVisitor):
        visitor.visitDeclarator(self)

    def getArraySize(self):
        return self.getChild(1)

    def getSubscriptExpressions(self):
        return self.children[next(idx+1 for idx, child in enumerate(self.children) if isinstance(child, IdentifierNode)):]


class FunctionDeclaratorNode(DeclaratorNode):
    def accept(self, visitor: ASTreeVisitor):
        visitor.visitDeclarator(self)


class TypedeclarationNode(ASTree):
    def __init__(self, parent: ASTree = None, const: bool = False, location=None):
        super().__init__(parent, location=location)
        self.const: bool = const

    def accept(self, visitor: ASTreeVisitor):
        visitor.visitTypedeclaration(self)


class QualifiersNode(ASTree):
    def accept(self, visitor: ASTreeVisitor):
        visitor.visitQualifiers(self)


class QualifierNode(ASTree):
    def accept(self, visitor: ASTreeVisitor):
        visitor.visitQualifier(self)


class TypequalifierNode(ASTree):
    def accept(self, visitor: ASTreeVisitor):
        visitor.visitTypequalifier(self)


class TypespecifierNode(ASTree):
    def __init__(self, specifier: str, parent: ASTree = None, location = None):
        super().__init__(parent, location= location)
        self.specifier: str = specifier

    def accept(self, visitor: ASTreeVisitor):
        visitor.visitTypespecifier(self)

    def __str__(self):
        return self.specifier


## An atomic instance of an ExpressionNode.
# Provides an interface to infer the type of its concrete instantiations through LiteralNode::inferType.
# Provides an interface needed for built-in type conversions, see LiteralNode::rank.
#
class LiteralNode(ExpressionNode):
    """
    An atomic instance of an ExpressionNode.
    """

    def __init__(self, value, parent: ASTree = None, location = None):
        super().__init__(parent, location=location)
        self._value = None
        self.setValue(value)

    def accept(self, visitor: ASTreeVisitor):
        visitor.visitLiteral(self)

    ## Retrieve the CType type of the concrete LiteralNode (built-in type).
    @staticmethod
    @abstractmethod
    def inferType(typeList: TypeList) -> CType:
        """
        Determine the CType of the LiteralNode.

        :param typeList: The type list used in the parse
        :return: The CType of the LiteralNode
        """

        pass

    ## Retrieve the rank of the concrete LiteralNode (built-in type).
    @staticmethod
    @abstractmethod
    def rank() -> int:
        pass

    def getValue(self):
        """
        Retrieve the value of the LiteralNode, guaranteed to be of the correct type.

        :return: The value of the LiteralNode
        """
        return self._value

    ## Set the value of the concrete LiteralNode. Fails if incorrectly type value is supplied.
    @abstractmethod
    def setValue(self, value) -> None:
        """
        Set the value of the LiteralNode.
        pre-cond: :value: is convertible to the correct type for the concrete LiteralNode
        post-cond: value member of LiteralNode is assigned the passed value

        :param value: The new value of the LiteralNode
        """
        pass

    def __repr__(self):
        return self.getValue()

    def evaluateErshovNumber(self):
        self.ershovNumber = 1


## An recursive instance of an ExpressionNode.
# Provides an interface to infer the CType return type of the function call through FunctioncallNode::inferType.
#
class FunctioncallNode(ExpressionNode):
    def accept(self, visitor: ASTreeVisitor):
        visitor.visitFunctioncall(self)

    ## Retrieve the CType return type of the function call.
    def inferType(self, typeList: TypeList) -> FunctionCType:
        return self.getIdentifierNode().getType()

    def getParameterNodes(self) -> List[ExpressionNode]:
        return self.children[1:]

    def getIdentifierNode(self) -> IdentifierNode:
        return self.getChild(0)

    def evaluateErshovNumber(self):
        self.ershovNumber = 1       # need a register to store the return value
        paramExpressions = self.getParameterNodes()
        if len(paramExpressions) == 0:
            return

        for param in paramExpressions:
            param.evaluateErshovNumber()

        # The first expression needs to at least be evaluated
        for idx in range(0, len(paramExpressions)):
            self.ershovNumber = max(self.ershovNumber, paramExpressions[idx].ershovNumber)


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

        # TODO as long as no conversions are supported, this is okay
        return self.getChild(0).inferType(typeList)

    @abstractmethod
    def getLLVMOpKeyword(self) -> str:
        return "dummyKeyword"

    @staticmethod
    @abstractmethod
    def getMIPSROpKeyword(instructionType: str) -> str:
        if instructionType == "I":
            return "dummy-I"
        elif instructionType == "R":
            return "dummy-R"
        return "dummyKeyword"

    @abstractmethod
    def evaluate(self, left: LiteralNode, right: LiteralNode) -> LiteralNode:
        pass

    def evaluateErshovNumber(self):
        for operand in self.children:
            operand.evaluateErshovNumber()
        if self.getChild(0).ershovNumber != self.getChild(1).ershovNumber:
            self.ershovNumber = max([operand.ershovNumber for operand in self.children])
        else:
            self.ershovNumber = self.getChild(1).ershovNumber + 1


class PointerNode(ASTree):
    def accept(self, visitor: ASTreeVisitor):
        visitor.visitPointer(self)

    def makeConst(self, constQualifier: QualifierNode):
        if self.getChild(0) is not None and\
                isinstance(self.getChild(0), TypequalifierNode):
            return
        self.addChild(constQualifier, 0)

    def __repr__(self):
        return '*'
