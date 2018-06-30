from safe_eval import safe_eval


class Definition:
    def __init__(self, type_size, dimensions, address):
        """
        A definition for an array
        :param type_size: Integer representing the type size of an element
        :param dimensions: List of Integers representing dimensions of the array
        :param address: Integer representing the starting address of the array
        """
        self.type_size = type_size
        self.dimensions = dimensions
        self.address = address

    def __str__(self):
        return (f"Definition: size {self.type_size}, "
                f"dimensions {self.dimensions}, "
                f"start address {self.address}")


class Expression:
    def __init__(self, definition, indices, offset=0):
        """
        An expression consisting of a single array access
        :param definition: Definition that this Expression accesses
        :param indices: List of Format Strings representing how to access the Definition.
                        has the form ["{i} + 1", "{j} * 2"] which means definition[i+1][j*2]
        :param offset: Integer offset from the address, used in structs
        """
        self.indices = indices
        self.type_size = definition.type_size
        self.dimensions = definition.dimensions
        self.base_address = definition.address
        self.offset = offset

    def get_address(self, bindings):
        address = self.base_address
        scale = self.type_size
        for i in range(len(self.indices) - 1, -1, -1):
            address += scale * safe_eval(self.indices[i].format(**bindings))
            scale *= self.dimensions[i]
        return address + self.offset


class Statement:
    def __init__(self, left, right):
        """
        An assignment statement
        :param left: Expression on the left hand side of this assignment Statement
        :param right: List of Expressions on the right hand side of this assignment Statement
        """
        self.left = left
        self.right = right

    def run(self, cache, bindings):
        # Making the assumption that subexpressions on the right are evaluated left to right
        for subexpression in self.right:
            cache.access(subexpression.get_address(bindings), subexpression.type_size, "r")
        cache.access(self.left.get_address(bindings), self.left.type_size, "w")


class Loop:
    def __init__(self, variable, initialization, condition, increment, body):
        """
        A for loop
        :param variable: String name of the loop variable
        :param initialization: String representation of the initial value
        :param condition: Format String representation of the loop condition
        :param increment: Format String representation of the incrementer
                            note that it cannot have the form "{i}++", use "{i}+1"
        :param body: Body of the for loop
        """
        self.variable = variable
        self.binding = int(initialization)
        self.condition = condition
        self.increment = increment
        self.body = body

    def run(self, cache, bindings):
        bindings[self.variable] = self.binding
        while safe_eval(self.condition.format(**bindings)):
            self.body.run(cache, bindings)
            binding = safe_eval(self.increment.format(**bindings))
            bindings[self.variable] = binding


class Body:
    def __init__(self, statements=None):
        """
        The body of a program or for loop
        :param statements: List of Loops and Statements
        """
        if statements is None:
            statements = list()
        self.statements = statements

    def add_statement(self, statement):
        self.statements.append(statement)

    def run(self, cache, bindings=None):
        if bindings is None:
            bindings = dict()
        for statement in self.statements:
            statement.run(cache, bindings)
