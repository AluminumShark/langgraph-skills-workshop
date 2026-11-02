# 把這裡換成你自己寫過的一段 Python 作業，改完記得執行這一格
def average(scores):
    total = 0
    for s in scores:
        total = total + s
    return total / len(scores)

print(average([90, 85, 77]))
