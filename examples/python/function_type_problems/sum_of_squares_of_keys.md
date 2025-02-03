---
title: Sum of squares of dict keys
---

# Problem Statement

Given a dictionary `d` and two keys `k1` and `k2`, return the sum of the squares of the values corresponding to those keys. If either of the keys are not in the given dictionary return '0'.

**Example**
```
d = {'a': 2, 'b': 3, 'c': 4}
sum_of_squares(d, 'a','b') # Output: 13
sum_of_squares(d, 'a','e') # Output: 0
```
First case: The sum of squares is `2^2 + 3^2 = 4 + 9 = 13`, so the result is `13`.
Second case: The key 'e' is not present in the dict, so the result is `0`.

# Solution

```python test.py -r 'python test.py'
<template>
def sum_of_squares(d: dict, k1: str, k2: str) -> int:
    '''
    Given a dictionary and two keys, return the sum of the squares 
    of the values corresponding to those keys. If either of the keys
    are not in the given dictionary return None.

    Arguments:
    d: dict - a dictionary with key-value pairs.
    k1: str - the first key.
    k2: str - the second key.

    Return: int - sum of squares of values of k1 and k2.
    '''
    <los>...</los>
    <sol>
    if k1 in d and k2 in d:
        return d[k1]**2 + d[k2]**2
    return 0  </sol>

</template>
<suffix_invisible>
{% include '../function_type_and_modify_check_suffix.py.jinja' %}
```

# Public Test Cases

## Input 1

```
d = {'x': 1, 'y': 2, 'z': 3}
is_equal(
    sum_of_squares(d, 'y', 'x'),
    5
)
```

## Output 1

```
5
```

## Input 2

```
d = {'a': 4, 'b': 5, 'c': 6}
is_equal(
    sum_of_squares(d, 'c', 'b'),
    61
)
```

## Output 2

```
61
```

## Input 3

```
d = {'p': 7, 'q': 8}
is_equal(
    sum_of_squares(d, 'p', 'r'),
    0
)
```

## Output 3

```
0
```

# Private Test Cases

## Input 1

```
d = {'a': 2, 'b': 3, 'c': 4}
is_equal(
    sum_of_squares(d, 'c', 'a'),
    20
)
d = {'m': 10, 'n': 11}
is_equal(
    sum_of_squares(d, 'm', 'n'),
    221
)
d = {'u': 9, 'v': 12}
is_equal(
    sum_of_squares(d, 'u', 'v'),
    225
)
is_equal(
    sum_of_squares(d, 'x', 'u'),
    0
)
```

## Output 1

```
20
221
225
0
```
