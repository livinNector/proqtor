---
title: Delete first three elements of a list
---

# Problem Statement

Given a list `l`, delete the first three elements of the list. If the list has fewer than three elements, delete all elements.

**Example**
```
l = [1, 2, 3, 4, 5]
```
After deleting the first three elements, the list becomes `[4, 5]`.

# Solution

```py3 test.py -r 'python test.py'
<template>
def delete_first_three(l: list) -> None:
    '''
    Given a list, delete the first three elements in the list.

    Arguments:
    l: list - a list of elements.

    Return: None - the list is modified in place.
    '''
    <los>...</los>
    <sol>del l[:3]</sol>
</template>
<suffix_invisible>
{% include '../function_type_and_modify_check_suffix.py.jinja' %}
```

# Public Test Cases

## Input 1

```
l = [10, 20, 30, 40, 50]
modify_check(
    lambda x: delete_first_three(x),
    l, [40, 50],
    should_modify=True
)
```

## Output 1

```
[40, 50]
```

## Input 2

```
l = [1, 2, 3, 4, 5, 6, 7]
modify_check(
    lambda x: delete_first_three(x),
    l, [4, 5, 6, 7],
    should_modify=True
)
```

## Output 2

```
[4, 5, 6, 7]
```

## Input 3

```
l = [1, 2]
modify_check(
    lambda x: delete_first_three(x),
    l, [],
    should_modify=True
)
```

## Output 3

```
[]
```

# Private Test Cases

## Input 1

```
l = [3, 4, 5]
modify_check(
    lambda x: delete_first_three(x),
    l, [],
    should_modify=True
)
l = [7, 8, 9, 10, 11]
modify_check(
    lambda x: delete_first_three(x),
    l, [10, 11],
    should_modify=True
)
l = [1, 2, 3, 4, 5, 6, 7, 8, 9]
modify_check(
    lambda x: delete_first_three(x),
    l, [4, 5, 6, 7, 8, 9],
    should_modify=True
)
```

## Output 1

```
[]
[10, 11]
[4, 5, 6, 7, 8, 9]
```
