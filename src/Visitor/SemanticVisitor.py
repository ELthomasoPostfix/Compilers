from src.Nodes.ASTreeNode import *
from src.Exceptions.exceptions import MisplacedJumpStatement
from src.Nodes.JumpNodes import ContinueNode, BreakNode, ReturnNode


class SemanticVisitor(ASTreeVisitor):

    def visitJumpstatement(self, node: JumpstatementNode):
        if (isinstance(node, ContinueNode) or isinstance(node, BreakNode)) and\
                not node.hasTypeAncestor(IterationstatementNode):
            raise MisplacedJumpStatement(node.__str__(), "iteration statement")
        elif isinstance(node, ReturnNode) and not node.hasTypeAncestor(FunctiondefinitionNode):
            raise MisplacedJumpStatement(node.__str__(), "function definition")
