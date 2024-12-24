import operator

# depercated:
def compare(value, mode, limit):
    return ops[mode](value,limit)

def within_limits(measurement_result):
    """
    Takes the measurement_result and determines if the measurement is within the stated limits.
    """
    ops = {
        '>' : operator.gt,
        '<' : operator.lt,
        '=' : operator.eq,
        '>=' : operator.ge,
        '<=' : operator.le,
    }
    value = getattr(measurement_result, measurement_result._meta.get_field(measurement_result.measurement_result_type.name).column)
    if value:
        limit = measurement_result.limit
        comparison_mode = limit.limit_comparison_mode.name
        if comparison_mode.upper() == "NONE":
            return True
        elif comparison_mode.upper() == "LIMIT 1 AND LIMIT 2":
            return (
                ops[limit.limit_comparison_one.name](value, limit.limit_one)
            ) & (
                ops[limit.limit_comparison_two.name](value, limit.limit_two)
            )
        elif comparison_mode.upper() == "LIMIT 1 ONLY":
            return (
                ops[limit.limit_comparison_one.name](value, limit.limit_one)
            )

        elif comparison_mode.upper() == "LIMIT 2 ONLY":
            return (
                ops[limit.limit_comparison_two.name](value, limit.limit_two)
            )
        # Returning True if we have a value
        return True
    # returning False if empty
    return False
