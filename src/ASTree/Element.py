from src.Visitor.ASTreeVisitor import ASTreeVisitor


# Abstract element interface for the visitor pattern
class Element:
    def accept(self, visitor: ASTreeVisitor):
        pass
