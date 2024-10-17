---
title: Sum of numbers in even indices of a list.
---

# Problem Statement

Find the sum of the numbers present in the even indices of the given list. 

**Note:** The indices start from 0.

**Input Format:** Comma seperated integers in a single line.  

**Output Format:** The expected sum as integer.

**Sample Input**
```
1,2,3,4,5
```
**Sample Output**
```
9
```

**Explanation**  

The elements at even positions are 1, 3 and 5. Their sum is 9.


# Solution
```py test.py -r 'python test.py' 
<prefix>
def sum_even_indices(l:int) -> int:
    '''
    Return the sum of numbers in 
    even indices of the list.
    '''
</prefix>
<template>
    return <sol>sum(l[::2])</sol><los>...</los>
</template>
<suffix>
# Driver code
l = list(map(int, input().split(',')))
print(sum_even_indices(l))
</suffix>
```

# Public Test Cases

## Input 1

```
1,2,3,4,5
```

## Output 1 

```
9
```


## Input 2

```
4,3,1
```

## Output 2

```
5
```


## Input 3

```
-1,4,3,2,-3,4,-4,-2,1,1
```

## Output 3

```
-4
```


# Private Test Cases

## Input 1

```
-1,1,-1,1,-1
```

## Output 1

```
-3
```

## Input 2

```
4
```

## Output 2

```
4
```

## Input 3

```
9,4,3,2,0,3
```

## Output 3

```
12
```
