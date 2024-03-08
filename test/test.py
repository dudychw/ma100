from random import shuffle

ans = []
for fail_count in range(100):
    local_ans = []
    for t in range(10 ** 4):
        order_count = 100
        fail_order = int((order_count / 100) * fail_count)

        profit = 1.02
        stop_loss = 0.98

        a = fail_order * [1] + (order_count - fail_order) * [0]
        shuffle(a)

        start_balance = 1000
        balance = start_balance

        for i in range(order_count):
            if a[i]:
                balance *= stop_loss
            else:
                balance *= profit
        local_ans.append(balance)

    ans.append(round(sum(local_ans) / len(local_ans), 2))

balance = 1000
for i in range(len(ans)):
    print(i, ans[i], f"{round(((ans[i] - balance) / balance * 100), 2)}%")
