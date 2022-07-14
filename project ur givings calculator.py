matchNum = 42
while True:
    print(f'match: {matchNum // 7} v.s. {matchNum % 7}')
    print("Input 25 simulation results")
    num25 = float(input())
    print("Input 75 simulation results")
    num75 = float(input())
    print("Here's the win rate:")
    print(num25 * 0.25 + num75 * 0.75)
    matchNum += 1
