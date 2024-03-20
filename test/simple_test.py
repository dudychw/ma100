import random

# дюна, в погоне за счастьем, достучаться до небес, уве, список шиндлера, шоу трумена

ans = []
for i in range(1000):
    ans.append(random.randint(1, 6))

for i in range(1, 7):
    print(ans.count(i))