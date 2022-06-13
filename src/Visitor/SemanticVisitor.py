from src.Nodes.ASTreeNode import *
from src.Exceptions.exceptions import MisplacedJumpStatement, InvalidReturnStatement, InvalidFunctionCall, \
    InvalidBinaryOperation, UnsupportedFeature, DeclarationException, InitializationException, OutOfBoundsLiteral, \
    GlobalScopeException, ConstAssigException, UndefinedFunction
from src.Nodes.JumpNodes import ContinueNode, BreakNode, ReturnNode
from src.Nodes.LiteralNodes import IntegerNode, FloatNode, CharNode
from src.Nodes.OperatorNodes import ModNode, ArraySubscriptNode, PrefixIncrementNode, PostfixDecrementNode, \
    PostfixIncrementNode, PrefixDecrementNode
from src.Visitor.ASTreeVisitor import AssignmentNode


class SemanticVisitor(ASTreeVisitor):
    def __init__(self, typeList: TypeList):
        self.typeList: TypeList = typeList
        self.mainExists = False

    def toTypeName(self, ctype: CType):
        return ctype.typeName(self.typeList)

    def visitJumpstatement(self, node: JumpstatementNode):
        if (isinstance(node, ContinueNode) or isinstance(node, BreakNode)) and\
                not node.hasTypeAncestor(IterationstatementNode):
            raise MisplacedJumpStatement(node.__str__(), "iteration statement", node.location)
        elif isinstance(node, ReturnNode) and not node.hasTypeAncestor(FunctiondefinitionNode):
            raise MisplacedJumpStatement(node.__str__(), "function definition", node.location)

        self.visitChildren(node)

    def visitFunctiondefinition(self, node: FunctiondefinitionNode):
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
                                         f"'{self.toTypeName(idNode.getType())}'", node.location)

        for returnNode in returnNodes:
            if returnNode.getChild(0) is None:
                raise InvalidReturnStatement(f"function '{idNode.identifier}' is missing a return expression of type "
                                             f"'{self.toTypeName(idNode.getType())}'", node.location)

            returnType: CType = returnNode.getChild(0).inferType(self.typeList)

            # differing return type and return statement type
            if returnType != idNode.getType():
                raise InvalidReturnStatement(f"function '{idNode.identifier}' return type mismatch, needed "
                                             f"'{self.toTypeName(idNode.getType())}' but got "
                                             f"'{self.toTypeName(returnType)}'", node.location)

        self.visitChildren(node)

    def visitFunctioncall(self, node: FunctioncallNode):
        self.visitChildren(node)

        params = node.getParameterNodes()
        cType = node.inferType(self.typeList)
        identifier = node.getIdentifierNode()
        if identifier.identifier == "printf":
            return

        if not node.getAncestorOfType(FunctiondefinitionNode).symbolTable[identifier.identifier].type.isDefinition:
            raise UndefinedFunction(node.toLegibleRepr(self.typeList), node.location)

        if len(params) != len(cType.paramTypes):
            raise InvalidFunctionCall(f"function '{node.getIdentifierNode().identifier}' at line has invalid param count.\n"
                                      f"Needed {len(cType.paramTypes)} but got {len(params)}", node.location)

        paramTypes = [param.inferType(self.typeList) for param in params]
        for idx in range(len(paramTypes)):
            if paramTypes[idx] != cType.paramTypes[idx]:
                raise InvalidFunctionCall(f"function '{node.getIdentifierNode().identifier}' has invalid param types.\n"
                                          f"Needed {[self.toTypeName(t) for t in cType.paramTypes]} "
                                          f"but got {[self.toTypeName(t) for t in paramTypes]}", node.location)

    def visitBinaryop(self, node: BinaryopNode):
        lhs = node.getChild(0)
        rhs = node.getChild(1)
        lhsType: CType = lhs.inferType(self.typeList)
        rhsType: CType = rhs.inferType(self.typeList)
        if not isinstance(node, ArraySubscriptNode) and lhsType != rhsType:
            raise UnsupportedFeature(f"The compiler does not support implicit nor explicit type conversions of any kind.\n"
                                     f"In binary {node.__str__()} got (lhs type, rhs type) = "
                                     f"({self.toTypeName(lhsType)}, {self.toTypeName(rhsType)})", node.location)

        if isinstance(node, ModNode) and\
            not (lhsType == self.typeList[BuiltinNames.INT] and rhsType == self.typeList[BuiltinNames.INT]):
            raise InvalidBinaryOperation(node.__str__(), f"operation only supported between two operands of type '{BuiltinNames.INT}'",node.location)

        if isinstance(node, ArraySubscriptNode) and rhsType != self.typeList[BuiltinNames.INT]:
            raise InvalidBinaryOperation(node.__str__(),
                                         f"array subscription expression must be of type {BuiltinNames.INT} literal", node.location)

        self.visitChildren(node)

    def visitVariabledeclaration(self, node: VariabledeclarationNode):
        declarator = node.getDeclaratorNode()
        if isinstance(declarator, ArrayDeclaratorNode):
            arrayElems = node.children[2:]
            sizeExps = declarator.getSubscriptExpressions()

            if len(sizeExps) != 1:
                raise UnsupportedFeature("Multidimensional arrays are not supported",node.location)

            if sizeExps[0].getValue() < len(arrayElems):
                raise InitializationException(f"Array initializer has too many elements: "
                                              f"expected {sizeExps[0].getValue()}, but got {len(arrayElems)}", node.location)

            arrayIdentifier = node.getIdentifierNode()
            requiredType = arrayIdentifier.inferType(self.typeList)

            for idx, elem in enumerate(arrayElems):
                if not isinstance(elem, LiteralNode):
                    raise InitializationException(f"Array initializer element must be computable at compile time: "
                                                  f"{arrayIdentifier.identifier}[{idx}]",node.location)

                if not requiredType.__eq__(elem.inferType(self.typeList), True):
                    raise InitializationException(f"Array initializer element is of incorrect type. Expected {self.toTypeName(requiredType)}, "
                                                  f"but got {self.toTypeName(elem.inferType(self.typeList))}: "
                                                  f"{arrayIdentifier.identifier}[{idx}]", node.location)

        self.visitChildren(node)

    def visitDeclarator(self, node: DeclaratorNode):
        if isinstance(node, ArrayDeclaratorNode):
            preamble = "Incorrect array declaration: "
            exps = node.getSubscriptExpressions()
            for exp in exps:
                if not isinstance(exp, IntegerNode):
                    raise DeclarationException(f"{preamble}array size expression must be of type {BuiltinNames.INT} literal", node.location)
                if exp.getValue() < 1:
                    raise DeclarationException(f"{preamble}array size expression must be greater than 0, but got size {exp.getValue()}",node.location)

        self.visitChildren(node)

    def visitUnaryexpression(self, node: UnaryexpressionNode):
        # TODO  make sure & and * operations are applied validly
        self.visitChildren(node)

    def visitUnaryop(self, node: UnaryopNode):
        if isinstance(node, PrefixIncrementNode) or isinstance(node, PostfixIncrementNode) or\
            isinstance(node, PrefixDecrementNode) or isinstance(node, PostfixDecrementNode):
            raise UnsupportedFeature(f"Unsupported unary operator: {node.__str__()}", node.location)

    def visitVar_assig(self, node: Var_assigNode):
        lhsType = node.getIdentifierNode().inferType(self.typeList)
        rhsType = node.getChild(1).inferType(self.typeList)
        if isinstance(node.getSibling(-1),VariabledeclarationNode) and node.getChild(0).inferType(self.typeList).isConstType:
            raise ConstAssigException("Can't assign a value to a const variable", node.location)
        # A char type may be assigned an int value
        if lhsType == self.typeList[BuiltinNames.CHAR] and (rhsType == self.typeList[BuiltinNames.INT]):
            pass

        elif lhsType != rhsType:
            raise UnsupportedFeature(f"The compiler does not support implicit nor explicit type conversions of any kind.\n"
                                     f"In binary {node.__str__()} got (lhs type, rhs type) = "
                                     f"({self.toTypeName(lhsType)}, {self.toTypeName(rhsType)})", node.location)

        if not node.hasTypeAncestor(FunctiondefinitionNode) and not isinstance(node.getChild(1), LiteralNode):
            raise InitializationException(f"Global assignments must have a literal rhs, but got {node.getChild(1).__str__()}", node.location)

        # This check depends on initializations being split off from declarations
        if not node.hasTypeAncestor(FunctiondefinitionNode) and not isinstance(node.getSibling(-1), VariabledeclarationNode):
            raise GlobalScopeException("Variable assignments not allowed, only initializations", node.location)

        self.visitChildren(node)

    def visitLiteral(self, node: LiteralNode):
        # -2^31, 2^31-1, 32-bit single precision floating point + and -
        lims = [-2147483648, 2147483647, -3.40282346639e+38, 3.40282346639e+38, -128, 127]
        baseIdx = 0 if isinstance(node, IntegerNode) else\
            (2 if isinstance(node, FloatNode) else
             (4 if isinstance(node, CharNode) else -1))

        if baseIdx == -1:
            raise UnsupportedFeature(f"Unknown literal type: {self.toTypeName(node.inferType(self.typeList))}", node.location)

        minLim, maxLim = lims[baseIdx], lims[baseIdx+1]
        if not isinstance(node.getValue(), str):
            if not (minLim <= node.getValue() <= maxLim):
                raise OutOfBoundsLiteral(f"An {self.toTypeName(node.inferType(self.typeList))} literal must be between "
                                         f"{minLim} and {maxLim}", node.location)
