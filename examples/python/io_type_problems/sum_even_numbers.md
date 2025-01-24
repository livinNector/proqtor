---
title: Sum of the even numbers from space separated input
tags: [aggregation, filtering, I/O, definite input]
---

# Problem Statement

Given a space separated string of numbers, find the sum of the even numbers from the given numbers.

Assume the numbers are non-negative integers.

# Solution

```python test.py  -r 'python test.py'
<template>
<sol>
nums = list(map(int, input().split()))
print(sum(num for num in nums if num%2==0))
</sol>
</template>
```

# Public Test Cases

## Input 1

```
1 2 3 4 5
```

## Output 1

```
6
```

## Input 2

```
2 4 6 8 10
```

## Output 2

```
30
```

## Input 3

```
9 4 3 2 7 3 6
```

## Output 3

```
12
```

# Private Test Cases

## Input 1

```
181 17 28 193 17 128 93
```

## Output 1

```
156
```

## Input 2

```
192 3923 33820  338 2744 92
```

## Output 2

```
37186
```

## Input 3

```
392 482 929 92 7239 87 82
```

## Output 3

```
1048
```
