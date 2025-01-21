---
title: Check if two digit even number
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

```py3 test.py -r 'python test.py'
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
<suffix_invisible>
{% include '../function_type_and_modify_check_suffix.py.jinja' %}
</suffix_invisible>
```

# Public Test Cases

## Input 1

```
is_equal(
    is_two_digit_even(42),
    True
)
```

## Output 1

```
True
```

## Input 2

```
is_equal(
    is_two_digit_even(55),
    False
)
```

## Output 2

```
False
```

## Input 3 

```
is_equal(
    is_two_digit_even(100),
    False
)
```

## Output 3

```
False
```

# Private Test Cases

## Input 1

```
n = 102
is_equal(
    is_two_digit_even(n),
    False
)
n = 10
is_equal(
    is_two_digit_even(n),
    True
)
n = 88
is_equal(
    is_two_digit_even(n),
    True
)
n = 11
is_equal(
    is_two_digit_even(n),
    False
)
```

## Output 1

```
False
True
True
False
```
