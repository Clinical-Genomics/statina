def empty_str(x):
    """Convert empty string to None"""

    if not isinstance(x, str):
        return x
    x = x.strip()
    if not x:
        return None
    return x


CONVERTERS = {
    str: ["SampleProject"],
    empty_str: [
        "SampleType",
        "Description",
        "Library_nM",
        "Index1",
        "Index2",
        "CNVSegment",
        "Flowcell",
        "QCFlag",
    ],
}

def convert(key, value):
    """Convert values according to the converter model"""

    if value is None:
        return None

    for function, keys in CONVERTERS.items():
        if key in keys:
            return function(value)

    return value
