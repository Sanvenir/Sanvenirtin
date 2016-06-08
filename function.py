import pickle


def save_byte(obj, file_path):
    with open(file_path, "wb") as f:
        pickle.dump(obj, f)


def load_byte(file_path):
    try:
        with open(file_path, "rb") as f:
            return pickle.load(f)
    except FileNotFoundError:
        return False


def double_range(*args):
    if len(args) == 2:
        for i in range(args[0]):
            for j in range(args[1]):
                yield (i, j)
    elif len(args) == 4:
        for i in range(args[0], args[1]):
            for j in range(args[2], args[3]):
                yield (i, j)
    elif len(args) == 6:
        for i in range(args[0], args[1], args[2]):
            for j in range(args[3], args[4], args[5]):
                yield (i, j)
    else:
        raise TypeError("double_range expected 2 or 4 or 6 arguments, got %d"%len(args))
    