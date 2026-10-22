# This is a decorator.
# A decorator is a function that adds extra behavior to another function
# without changing the original function code directly.
def logging_decorator(func):
    # wrapper is the new function that replaces the original function.
    # It accepts any number of arguments using *args.
    def wrapper(*args):
        # Print the name of the function and the arguments passed to it.
        # Example: You called a_function(1, 2, 3)
        print(f"You called {func.__name__}{args}")

        # Call the original function with the same arguments.
        result = func(*args)

        # Print the result returned by the original function.
        print(f"It returned: {result}")

        # Return the result so the function behaves normally.
        return result

    # Return the wrapper function to replace the original function.
    return wrapper


# This is the function that gets decorated.
# The @logging_decorator syntax means:
# "a_function = logging_decorator(a_function)"
@logging_decorator
def a_function(*args):
    # This function adds all the numbers passed to it.
    return sum(args)


# Calling the function now triggers the decorator first.
# So it prints:
# 1. function name + arguments
# 2. result of the function
a_function(1, 2, 3)