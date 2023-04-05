def invalidTransactions(transactions):
    """
    :type transactions: List[str]
    :rtype: List[str]
    """
    invalid_transactions = []
    for i in range(len(transactions)-1):
        for j in range(i+1, len(transactions)):
            print(j, len(transactions))
            if int(transactions[i].split(',')[2]) > 1000:
                invalid_transactions.append(transactions[i])
                transactions.pop(i)
            elif j > len(transactions):
                print(j, len(transactions))
                break
            elif int(transactions[j].split(',')[2]) > 1000:
                invalid_transactions.append(transactions[j])
                transactions.pop(j)
            elif transactions[i].split(',')[0] == transactions[j].split(',')[0] and \
                    int(transactions[j].split(',')[1]) - int(transactions[i].split(',')[1]) <= 60:
                invalid_transactions.append(transactions[i])
                invalid_transactions.append(transactions[j])
                transactions.pop(i)
                transactions.pop(j-1)
    return invalid_transactions

print(invalidTransactions(["alice,20,800,mtv","alice,50,100,mtv","alice,51,100,frankfurt"]))