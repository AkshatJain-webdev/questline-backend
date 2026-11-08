class NotFoundError(Exception):
    pass


# Well-formed, but breaks a rule: a duplicate, a cycle, or an inconsistent tree.
class ConflictError(Exception):
    pass
