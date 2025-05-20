from parser import (
    NumberLiteral, StringLiteral, Identifier,
    BinaryOp, VariableDeclaration, PrintStatement,
    FunctionDeclaration, CallExpression,
    ReturnStatement, IfStatement, WhileStatement, Assignment
)

def transform_node(node):
    if isinstance(node, NumberLiteral):
        return str(node.value)

    elif isinstance(node, StringLiteral):
        # Re-quote string literals for Python output
        escaped = node.value.replace('"', '\\"')
        return f'"{escaped}"'

    elif isinstance(node, Identifier):
        return node.name

    elif isinstance(node, BinaryOp):
        left = transform_node(node.left)
        right = transform_node(node.right)
        return f"({left} {node.op} {right})"

    elif isinstance(node, VariableDeclaration):
        # You can ignore kind in Python (let/var/const don't exist)
        name = node.name
        value = transform_node(node.value)
        return f"{name} = {value}"
    elif isinstance(node, Assignment):
        left = transform_node(node.left)
        right = transform_node(node.right)
        return f"{left} = {right}"

    elif isinstance(node, PrintStatement):
        values = ", ".join(transform_node(v) for v in node.value)
        return f"print({values})"

    elif isinstance(node, FunctionDeclaration):
        params = ", ".join(node.params)
        body_lines = [transform_node(stmt) for stmt in node.body]
        indented = ["    " + line for line in body_lines]
        body = "\n".join(indented)
        return f"def {node.name}({params}):\n{body if body else '    pass'}"

    elif isinstance(node, CallExpression):
        callee = transform_node(node.callee)
        args = ", ".join(transform_node(arg) for arg in node.arguments)
        return f"{callee}({args})"

    elif isinstance(node, ReturnStatement):
        arg = transform_node(node.argument)
        return f"return {arg}"

    elif isinstance(node, IfStatement):
        test = transform_node(node.test)
        consequent_lines = [transform_node(stmt) for stmt in node.consequent]
        consequent = "\n".join("    " + line for line in consequent_lines)

        code = f"if {test}:\n{consequent if consequent else '    pass'}"
        if node.alternate is not None:
            alternate_lines = [transform_node(stmt) for stmt in node.alternate]
            alternate = "\n".join("    " + line for line in alternate_lines)
            code += f"\nelse:\n{alternate if alternate else '    pass'}"

        return code

    elif isinstance(node, WhileStatement):
        test = transform_node(node.test)
        body_lines = [transform_node(stmt) for stmt in node.body]
        body = "\n".join("    " + line for line in body_lines)
        return f"while {test}:\n{body if body else '    pass'}"


    else:
        raise TypeError(f"Unknown AST node: {node}")
