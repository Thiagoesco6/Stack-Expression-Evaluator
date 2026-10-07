class Stack:
    def __init__(self):
        self.items = []

    def push(self, item):
        self.items.append(item)

    def pop(self):
        if self.is_empty():
            raise IndexError("Cannot pop from an empty stack.")
        return self.items.pop()

    def peek(self):
        if self.is_empty():
            raise IndexError("Cannot peek at an empty stack.")
        return self.items[-1]

    def is_empty(self):
        return len(self.items) == 0

def precedence(operator):
    """Return the priority of an operator."""
    if operator in ("+", "-"):
        return 1
    if operator in ("*", "/"):
        return 2
    return 0


def apply_operator(numbers, operators):
    """Apply the top operator to the top two numbers."""
    operator = operators.pop()

    # The right number comes off the stack first.
    right = numbers.pop()
    left = numbers.pop()

    if operator == "+":
        result = left + right
    elif operator == "-":
        result = left - right
    elif operator == "*":
        result = left * right
    elif operator == "/":
        if right == 0:
            raise ZeroDivisionError("Cannot divide by zero.")
        result = left / right
    else:
        raise ValueError("Unknown operator.")

    numbers.push(result)


def tokenize(expression):
    """Split an expression into numbers, operators, and parentheses."""
    tokens = []
    index = 0

    while index < len(expression):
        character = expression[index]

        if character.isspace():
            index += 1
            continue

        if character in "0123456789.":
            start = index

            while (
                index < len(expression)
                and expression[index] in "0123456789."
            ):
                index += 1

            number = expression[start:index]

            # Check that the number is valid.
            try:
                float(number)
            except ValueError:
                raise ValueError(f"Invalid number: {number}")

            tokens.append(number)

        elif character in "+-*/()":
            tokens.append(character)
            index += 1

        else:
            raise ValueError(f"Invalid character: {character}")

    return tokens


def evaluate_expression(expression):
    """Evaluate an expression using number and operator stacks."""
    numbers = Stack()
    operators = Stack()
    tokens = tokenize(expression)

    if not tokens:
        raise ValueError("The expression is empty.")

    expecting_number = True

    for token in tokens:
        if token == "(":
            if not expecting_number:
                raise ValueError("Missing operator before '('.")

            operators.push(token)

        elif token == ")":
            if expecting_number:
                raise ValueError("Missing number before ')'.")

            while not operators.is_empty() and operators.peek() != "(":
                apply_operator(numbers, operators)

            if operators.is_empty():
                raise ValueError("Unmatched closing parenthesis.")

            operators.pop()  # Remove the opening parenthesis.
            expecting_number = False

        elif token in ("+", "-", "*", "/"):
            if expecting_number:
                raise ValueError("Expected a number before the operator.")

            while (
                not operators.is_empty()
                and operators.peek() != "("
                and precedence(operators.peek()) >= precedence(token)
            ):
                apply_operator(numbers, operators)

            operators.push(token)
            expecting_number = True

        else:
            if not expecting_number:
                raise ValueError("Missing operator between numbers.")

            numbers.push(float(token))
            expecting_number = False

    if expecting_number:
        raise ValueError("The expression ends without a number.")

    while not operators.is_empty():
        if operators.peek() == "(":
            raise ValueError("Unmatched opening parenthesis.")

        apply_operator(numbers, operators)

    return numbers.pop()


def process_file(input_path, output_path):
    """Evaluate each expression and preserve separator and blank lines."""
    with open(input_path, "r", encoding="utf-8") as input_file:
        lines = input_file.readlines()

    results = []

    for line_number, line in enumerate(lines, start=1):
        expression = line.strip()

        if not expression:
            results.append(line)
            continue

        # A separator contains only two or more hyphens.
        if len(expression) >= 2 and set(expression) == {"-"}:
            results.append(line)
            continue

        try:
            result = evaluate_expression(expression)

            # Display whole-number results without ".0".
            if result.is_integer():
                result_text = str(int(result))
            else:
                result_text = str(result)

        except (ValueError, ZeroDivisionError, IndexError) as error:
            result_text = f"Error on line {line_number}: {error}"

        ending = "\n" if line.endswith("\n") else ""
        results.append(result_text + ending)

    with open(output_path, "w", encoding="utf-8") as output_file:
        output_file.writelines(results)


if __name__ == "__main__":
    from pathlib import Path

    # Locate the text files in the same folder as main.py.
    project_folder = Path(__file__).resolve().parent
    input_path = project_folder / "input.txt"
    output_path = project_folder / "output.txt"

    try:
        process_file(input_path, output_path)
        print("Finished! Open output.txt to view the results.")
    except OSError as error:
        print(f"File error: {error}")