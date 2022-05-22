from src.Nodes.ASTreeNode import *
from src.Exceptions.exceptions import MisplacedJumpStatement, InvalidReturnStatement, InvalidFunctionCall, \
    InvalidBinaryOperation, UnsupportedFeature, DeclarationException, InitializationException
from src.Nodes.JumpNodes import ContinueNode, BreakNode, ReturnNode
from src.Nodes.LiteralNodes import IntegerNode
from src.Nodes.OperatorNodes import ModNode, ArraySubscriptNode


class SemanticVisitor(ASTreeVisitor):
    def __init__(self, typeList: TypeList):
        self.typeList: TypeList = typeList

    def toTypeName(self, ctype: CType):
        return self.typeList[ctype.typeIndex]

    def visitJumpstatement(self, node: JumpstatementNode):
        if (isinstance(node, ContinueNode) or isinstance(node, BreakNode)) and\
                not node.hasTypeAncestor(IterationstatementNode):
            raise MisplacedJumpStatement(node.__str__(), "iteration statement")
        elif isinstance(node, ReturnNode) and not node.hasTypeAncestor(FunctiondefinitionNode):
            raise MisplacedJumpStatement(node.__str__(), "function definition")

    def visitFunctiondefinition(self, node: FunctiondefinitionNode):
        traverse = node.preorderTraverse([], 0)
        returnNodes = [retNode[0]
                       for retNode in node.preorderTraverse([], 0)
                       if isinstance(retNode[0], ReturnNode)]
        idNode = node.getIdentifierNode()

        # void return type and no return stmt
        if idNode.getType() == self.typeList[BuiltinNames.VOID]:
            if len(returnNodes) == 0:
                # Ensure each function exits at the end of its scope
                node.getChild(2).addChild(ReturnNode())
                return

            nonVoidReturns = []
            for retNode in returnNodes:
                if retNode.getChild(0) is not None:
                    nonVoidReturns.append(retNode)

            if len(nonVoidReturns) == 0:
                return
            returnNodes = nonVoidReturns

        # No return stmt (implicit not void return type)
        if len(returnNodes) == 0:
            raise InvalidReturnStatement(f"function '{idNode.identifier}' is missing a return statement of type "
                                         f"'{self.toTypeName(idNode.getType())}'")

        for returnNode in returnNodes:
            if returnNode.getChild(0) is None:
                raise InvalidReturnStatement(f"function '{idNode.identifier}' is missing a return expression of type "
                                             f"'{self.toTypeName(idNode.getType())}'")

            returnType: CType = returnNode.getChild(0).inferType(self.typeList)

            # differing return type and return statement type
            if returnType != idNode.getType():
                raise InvalidReturnStatement(f"function '{idNode.identifier}' return type mismatch, needed "
                                             f"'{self.toTypeName(idNode.getType())}' but got "
                                             f"'{self.toTypeName(returnType)}'")

        self.visitChildren(node)

    def visitFunctioncall(self, node: FunctioncallNode):
        params = node.getParameterNodes()
        cType = node.inferType(self.typeList)
        if len(params) != len(cType.paramTypes):
            raise InvalidFunctionCall(f"function '{node.getIdentifierNode().identifier}' has invalid param count.\n"
                                      f"Needed {len(cType.paramTypes)} but got {len(params)}")

        paramTypes = [param.inferType(self.typeList) for param in params]
        for idx in range(len(paramTypes)):
            if paramTypes[idx] != cType.paramTypes[idx]:
                raise InvalidFunctionCall(f"function '{node.getIdentifierNode().identifier}' has invalid param types.\n"
                                          f"Needed {cType.paramTypes} but got {paramTypes}")

    def visitBinaryop(self, node: BinaryopNode):
        lhs = node.getChild(0)
        rhs = node.getChild(1)
        lhsType: CType = lhs.inferType(self.typeList)
        rhsType: CType = rhs.inferType(self.typeList)
        if not isinstance(node, ArraySubscriptNode) and lhsType != rhsType:
            raise UnsupportedFeature(f"The compiler does not support implicit nor explicit type conversions of any kind.\n"
                                     f"In binary {node.__str__()} got (lhs type, rhs type) = "
                                     f"({self.toTypeName(lhsType)}, {self.toTypeName(rhsType)})")

        if isinstance(node, ModNode) and\
            not (lhsType == self.typeList[BuiltinNames.INT] and rhsType == self.typeList[BuiltinNames.INT]):
            raise InvalidBinaryOperation(node.__str__(), f"operation only supported between two operands of type '{BuiltinNames.INT}'")

        if isinstance(node, ArraySubscriptNode) and rhsType != self.typeList[BuiltinNames.INT]:
            raise InvalidBinaryOperation(node.__str__(),
                                         f"array subscription expression must be of type {BuiltinNames.INT} literal")

    def visitVariabledeclaration(self, node: VariabledeclarationNode):
        declarator = node.getDeclaratorNode()
        if isinstance(declarator, ArrayDeclaratorNode):
            arrayElems = node.children[2:]
            sizeExps = declarator.getSubscriptExpressions()

            if len(sizeExps) != 1:
                raise UnsupportedFeature("Multidimensional arrays are not supported")

            if sizeExps[0].getValue() < len(arrayElems):
                raise InitializationException(f"Array initializer has too many elements: "
                                              f"expected {sizeExps[0].getValue()}, but got {len(arrayElems)}")

            arrayIdentifier = node.getIdentifierNode()
            requiredType = arrayIdentifier.inferType(self.typeList)

            for idx, elem in enumerate(arrayElems):
                if not isinstance(elem, LiteralNode):
                    raise InitializationException(f"Array initializer element must be computable at compile time: "
                                                  f"{arrayIdentifier.identifier}[{idx}]")

                if not requiredType.__eq__(elem.inferType(self.typeList), True):
                    raise InitializationException(f"Array initializer element is of incorrect type. Expected {self.toTypeName(requiredType)}, "
                                                  f"but got {self.toTypeName(elem.inferType(self.typeList))}: "
                                                  f"{arrayIdentifier.identifier}[{idx}]")

        self.visitChildren(node)

    def visitDeclarator(self, node: DeclaratorNode):
        if isinstance(node, ArrayDeclaratorNode):
            preamble = "Incorrect array declaration: "
            exps = node.getSubscriptExpressions()
            for exp in exps:
                if not isinstance(exp, IntegerNode):
                    raise DeclarationException(f"{preamble}array size expression must be of type {BuiltinNames.INT} literal")
                if exp.getValue() < 1:
                    raise DeclarationException(f"{preamble}array size expression must be greater than 0, but got size {exp.getValue()}")

        self.visitChildren(node)

    def visitUnaryexpression(self, node: UnaryexpressionNode):
        # TODO  make sure & and * operations are applied validly
        self.visitChildren(node)
