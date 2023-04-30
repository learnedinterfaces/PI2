from collections import defaultdict
char_sizes = defaultdict(lambda: dict(width=10, height=19))
char_sizes.update( {
    "0": {
        "width": 9,
        "height": 19
    },
    "1": {
        "width": 7,
        "height": 19
    },
    "2": {
        "width": 9,
        "height": 19
    },
    "3": {
        "width": 9,
        "height": 19
    },
    "4": {
        "width": 10,
        "height": 19
    },
    "5": {
        "width": 10,
        "height": 19
    },
    "6": {
        "width": 10,
        "height": 19
    },
    "7": {
        "width": 8,
        "height": 19
    },
    "8": {
        "width": 10,
        "height": 19
    },
    "9": {
        "width": 10,
        "height": 19
    },
    "'": {
        "width": 2,
        "height": 19
    },
    ",": {
        "width": 5,
        "height": 19
    },
    ".": {
        "width": 5,
        "height": 19
    },
    "p": {
        "width": 9,
        "height": 19
    },
    "y": {
        "width": 8,
        "height": 19
    },
    "f": {
        "width": 5,
        "height": 19
    },
    "g": {
        "width": 9,
        "height": 19
    },
    "c": {
        "width": 8,
        "height": 19
    },
    "r": {
        "width": 6,
        "height": 19
    },
    "l": {
        "width": 4,
        "height": 19
    },
    "/": {
        "width": 5,
        "height": 19
    },
    "a": {
        "width": 9,
        "height": 19
    },
    "o": {
        "width": 9,
        "height": 19
    },
    "e": {
        "width": 8,
        "height": 19
    },
    "u": {
        "width": 9,
        "height": 19
    },
    "i": {
        "width": 4,
        "height": 19
    },
    "d": {
        "width": 9,
        "height": 19
    },
    "h": {
        "width": 9,
        "height": 19
    },
    "t": {
        "width": 5,
        "height": 19
    },
    "n": {
        "width": 9,
        "height": 19
    },
    "s": {
        "width": 8,
        "height": 19
    },
    "-": {
        "width": 7,
        "height": 19
    },
    ";": {
        "width": 5,
        "height": 19
    },
    "q": {
        "width": 9,
        "height": 19
    },
    "j": {
        "width": 4,
        "height": 19
    },
    "k": {
        "width": 8,
        "height": 19
    },
    "x": {
        "width": 8,
        "height": 19
    },
    "b": {
        "width": 9,
        "height": 19
    },
    "m": {
        "width": 14,
        "height": 19
    },
    "w": {
        "width": 12,
        "height": 19
    },
    "v": {
        "width": 8,
        "height": 19
    },
    "z": {
        "width": 8,
        "height": 19
    },
    "\"": {
        "width": 7,
        "height": 19
    },
    "<": {
        "width": 10,
        "height": 19
    },
    ">": {
        "width": 10,
        "height": 19
    },
    "P": {
        "width": 9,
        "height": 19
    },
    "Y": {
        "width": 10,
        "height": 19
    },
    "F": {
        "width": 9,
        "height": 19
    },
    "G": {
        "width": 12,
        "height": 19
    },
    "C": {
        "width": 11,
        "height": 19
    },
    "R": {
        "width": 10,
        "height": 19
    },
    "L": {
        "width": 7,
        "height": 19
    },
    "?": {
        "width": 8,
        "height": 19
    },
    "+": {
        "width": 10,
        "height": 19
    },
    "|": {
        "width": 5,
        "height": 19
    },
    "A": {
        "width": 10,
        "height": 19
    },
    "O": {
        "width": 12,
        "height": 19
    },
    "E": {
        "width": 10,
        "height": 19
    },
    "U": {
        "width": 11,
        "height": 19
    },
    "I": {
        "width": 4,
        "height": 19
    },
    "D": {
        "width": 12,
        "height": 19
    },
    "H": {
        "width": 11,
        "height": 19
    },
    "T": {
        "width": 10,
        "height": 19
    },
    "N": {
        "width": 12,
        "height": 19
    },
    "S": {
        "width": 10,
        "height": 19
    },
    "_": {
        "width": 6,
        "height": 19
    },
    ":": {
        "width": 5,
        "height": 19
    },
    "Q": {
        "width": 12,
        "height": 19
    },
    "J": {
        "width": 8,
        "height": 19
    },
    "K": {
        "width": 10,
        "height": 19
    },
    "X": {
        "width": 11,
        "height": 19
    },
    "B": {
        "width": 10,
        "height": 19
    },
    "M": {
        "width": 14,
        "height": 19
    },
    "W": {
        "width": 15,
        "height": 19
    },
    "V": {
        "width": 10,
        "height": 19
    },
    "Z": {
        "width": 10,
        "height": 19
    },
    "!": {
        "width": 5,
        "height": 19
    },
    "@": {
        "width": 15,
        "height": 19
    },
    "#": {
        "width": 10,
        "height": 19
    },
    "$": {
        "width": 10,
        "height": 19
    },
    "%": {
        "width": 13,
        "height": 19
    },
    "^": {
        "width": 6,
        "height": 19
    },
    "&": {
        "width": 11,
        "height": 19
    },
    "*": {
        "width": 7,
        "height": 19
    },
    "(": {
        "width": 5,
        "height": 19
    },
    ")": {
        "width": 6,
        "height": 19
    },
    "[": {
        "width": 6,
        "height": 19
    },
    "]": {
        "width": 5,
        "height": 19
    }
})
