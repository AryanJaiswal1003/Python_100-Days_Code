## Advanced Python Decorator Functions:

# A class to represent a user in the application.
# It stores the user's name and whether they are logged in.
# This object is used to check whether a user is allowed to perform an action.
class User:
    def __init__(self, name):
        self.name = name
        self.is_logged_in = False


# A decorator is a function that takes another function as input
# and returns a new function that usually adds extra behavior.
#
# In this example, the decorator checks whether the user is logged in
# before allowing the original function to run.
#
# We keep the original *args and **kwargs unchanged because the goal is
# to preserve the same function call structure.
def is_authenticated_decorator(function):
    def wrapper(*args, **kwargs):
        # Here we check the first argument passed to the wrapper.
        # In this example, the first argument is the user object.
        #
        # If the user is logged in, we run the original function.
        # If not, nothing happens.
        if args[0].is_logged_in == True:
            # This calls the original function with the same user object.
            # We are not changing the code structure or the arguments.
            function(args[0])
    return wrapper


# The @ symbol is Python decorator syntax.
# It means:
# create_blog_post = is_authenticated_decorator(create_blog_post)
#
# So when create_blog_post() is called, it actually runs the wrapper
# created inside the decorator.
@is_authenticated_decorator
def create_blog_post(user):
    # This is the original task that only runs for logged-in users.
    print(f"This is {user.name}'s New Blog post..")


# Example usage:
# Create a user object and set them as logged in.
new_user = User("Robert Browne")
new_user.is_logged_in = True

# Call the decorated function.
create_blog_post(new_user)