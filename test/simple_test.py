

while True:
    x = int(input())
    try:
        print(5/x)
    except Exception as err:
        print('error' + str(err))
    print('try again')