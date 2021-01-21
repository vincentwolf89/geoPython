import pandas as pd

dct = {"test":[1,2],"test2":[3,4]}

# it = iter(dct.values())    
# first, second = next(it), next(it)    
# print first[0], second[0]

# print dct["test2"]

df = pd.DataFrame (columns = ['test1','test2'])

list = [1,2,3]

for item in list:
    df.loc[item] = ['bla','bla2']

print df