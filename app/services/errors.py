class NotFoundError(Exception):
    pass


# The request is well-formed but breaks a rule: a duplicate, a cycle, or a change
# that would leave the tree inconsistent.
class ConflictError(Exception):
    pass
