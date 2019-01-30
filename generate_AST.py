#! /usr/local/bin/python3

# import sys

tab = "    " # Tab is four spaces

base_desc = {
    "Expr": {
        "Chain": [["Expr", "left"], ["Expr", "right"]],
        "Unary": [["Scanner.Token", "operator"], ["Expr", "right"]],
        "Binary": [["Expr", "left"], ["Scanner.Token", "operator"], ["Expr", "right"]],
        "Grouping": [["Expr", "expression"]],
        "Literal": [["object", "value"]],
        "Variable": [["Scanner.Token", "name"]],
        "Assign": [["Scanner.Token", "name"], ["Expr", "value"]],
        "Logical": [["Expr", "left"], ["Scanner.Token", "operator"], ["Expr", "right"]],

    },
    "Stmt": {
        "Expression": [["Expr", "expression"]],
        "Print": [["Expr", "expression"]],
        "Var": [["Scanner.Token", "name"], ["Expr", "initializer"]],
        "Block": [["Stmt", "statements"]],
        "If": [["Expr", "condition"], ["Stmt", "then_branch"], ["Stmt", "else_branch"]]
    }
}


def define_ast(con, base_name, types):
    """Generate the AST structure classes for the 'base_name' root."""
    con.write("import Scanner\n\n\n")
    con.writelines(["class " + base_name + ":\n",
                    tab + "pass\n\n"])
    for expr_type, expr in types.items():
        define_type(con, base_name, expr_type, expr)


def define_type(con, base_name, class_name, fields):
    """Generate the AST structure classes for the given sub-tree."""
    types, names = zip(*fields)

    field_str = ", ".join(names)

    assert_stmts = [tab + tab +
                    "assert isinstance(" + field[1] + ", " + field[0] + ")\n"
                    for field in fields]

    var_stmts = [tab + tab +
                 "self." + name + " = " + name + "\n"
                 for name in names]

    con.write("\n")
    con.writelines(["class " + class_name + "(" + base_name + "):\n"
                    "",
                    # The constructor
                    tab + "def __init__(self, " +field_str + "):\n"])
    con.writelines(assert_stmts)
    con.write("\n")
    con.writelines(var_stmts)
    con.write("\n")
    con.writelines([tab + "def accept(self, visitor):\n",
                    tab + tab + "return visitor.visit_" + class_name.lower() + "(self)\n\n"])


if __name__ == "__main__":
    path = "grammar.py"
    with open(path, "w+") as con:
        define_ast(con, "Expr", base_desc["Expr"])
        define_ast(con, "Stmt", base_desc["Stmt"])
