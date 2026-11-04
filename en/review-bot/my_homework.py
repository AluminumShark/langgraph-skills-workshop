# Replace this with a piece of Python homework you wrote yourself, then remember to run this cell
def average(scores):
    total = 0
    for s in scores:
        total = total + s
    return total / len(scores)

print(average([90, 85, 77]))
