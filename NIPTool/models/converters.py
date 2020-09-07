def empty_str(x):
    """Convert empty string to None"""

    if not isinstance(x, str):
        return x
    x = x.strip()
    if not x:
        return None
    return x


CONVERTERS = {str: ["SampleProject"], empty_str: ["SampleType", "Description"]}
