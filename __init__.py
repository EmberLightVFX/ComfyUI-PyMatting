from .PyMatte import PyMatte

# A dictionary that contains all nodes you want to export with their names
# NOTE: names should be globally unique

NODE_CLASS_MAPPINGS = {
    "PyMatte": PyMatte,
}
