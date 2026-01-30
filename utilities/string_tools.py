def pluralize(value, unit):
    # Add an "s" to a unit (day, meter, whatever) for values > 1
    return f"{value} {unit}{'' if value == 1 else 's'}"

def encode_newlines(s):
    """Escape NL characters for output to storage"""
    return s.replace("\n", "\\n")

def decode_newlines(s):
    """Un-scape NL characters read in from storage"""
    return s.replace("\\n", "\n")
