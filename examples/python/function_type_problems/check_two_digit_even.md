---
title: Check if two digit even number
tags: [numbers, boolean expression]
---

# Problem Statement

Given an integer `n`, return `True` if the number is a two-digit even number, and `False` otherwise.

**Example**
```py3
is_two_digit_even(22) # True , both two digit and even
is_two_digit_even(2) # False, even but not two digit
is_two_digit_even(21) # False, two digit but not even
```

# Solution

```python test.py -r 'python test.py'
<template>
def is_two_digit_even(n: int) -> bool:
    '''
    Given an integer, check if it is a two-digit even number.

    Arguments:
    n: int - an integer to check.

    Return: bool - True if it is a two-digit even number, else False.
    '''
    <los>...</los>
    <sol>return 10 <= n <= 99 and n % 2 == 0</sol>
</template>
import sys
exec(sys.stdin.read())
```

# Public Test Cases

## Input 1

```
print(is_two_digit_even(42))
```

## Output 1

```
True
```

## Input 2

```
print(is_two_digit_even(55))
```

## Output 2

```
False
```

## Input 3

```
print(is_two_digit_even(100))
```

## Output 3

```
False
```

# Private Test Cases

## Input 1

```
n = 102
print(is_two_digit_even(n))
n = 10
print(is_two_digit_even(n))
n = 88
print(is_two_digit_even(n))
n = 11
print(is_two_digit_even(n))
```

## Output 1

```
False
True
True
False
```
