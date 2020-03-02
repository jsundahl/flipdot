from characters import Characters


def scrolling_text(text, start_from_right=True, scroll_length=1):
    """
    take in a string, output a generator that is a series of
    frames (5x7 matrices)
    """
    if start_from_right:
        matrix = [[0 for _ in range(6)] for __ in range(5)]
    else:
        matrix = [[] for _ in range(5)]

    for char in list(text):
        trimmed_char = _trim_frame(Characters.string_to_matrices(char)[0])

        for i in range(5):
            matrix[i] += trimmed_char[i] + [0]

        while len(matrix[0]) >= 7:
            yield [col[:7] for col in matrix]
            matrix = [col[scroll_length:] for col in matrix]

    while(len(matrix[0]) > 0):
        padding = [0 for _ in range(7 - len(matrix[0]))]
        yield [matrix[i] + padding for i in range(5)]

        matrix = [col[scroll_length:] for col in matrix]


def _trim_frame(frame):
    """
    trim the whitespace off the rows, i.e. represent the image with the fewest
    required number of rows.
    """
    # TODO: is it worth the effort to memoize this?
    last_meaningful_row = -1

    for col in frame:
        try:
            last_yellow_index = "".join([str(dot) for dot in col]).rindex("1")
            last_meaningful_row = max(last_meaningful_row, last_yellow_index)
        except ValueError:
            pass

    # if it's a space just return a row of zeros
    if last_meaningful_row == -1:
        return [[] for _ in range(5)]

    return [col[:last_meaningful_row + 1] for col in frame]
