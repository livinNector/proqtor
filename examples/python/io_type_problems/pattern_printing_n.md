---
title: Pattern Print - N
tags: [pattern printing, I/O]
---

# Problem Statement

Given an integer `n` (where `n > 0`), print an "N" shaped pattern with `n` rows. The pattern should have vertical bars (`|`) on the left and right sides of each row, with a backslash (`\`) moving diagonally from the top-left to the bottom-right. There should be no spaces to the right of the pattern.

**NOTE: This is an I/O type question, you need to write the whole code for taking input and printing the output.**

**Input Format**
- A single integer `n`, representing the number of rows in the pattern.

**Output Format**
- An "N" shaped pattern with `n` rows, as described.

**Examples**

**Input:**
```
1
```

**Output:**
```
|\|
```

**Input:**
```
2
```

**Output:**
```
|\ |
| \|
```

**Input:**
```
3
```

**Output:**
```
|\  |
| \ |
|  \|
```

# Solution

```python test.py -r 'python test.py'
<template>
<sol>
n = int(input())
for i in range(n):
    print(f"|{' '*i}\\{' '*(n-i-1)}|")
</sol>
</template>
```

# Public Test Cases

## Input 1

```
5
```

## Output 1

```
|\    |
| \   |
|  \  |
|   \ |
|    \|
```

## Input 2

```
1
```

## Output 2

```
|\|
```

## Input 3

```
2
```

## Output 3

```
|\ |
| \|
```

## Input 4

```
3
```

## Output 4

```
|\  |
| \ |
|  \|
```

# Private Test Cases

## Input 1

```
16
```

## Output 1

```
|\               |
| \              |
|  \             |
|   \            |
|    \           |
|     \          |
|      \         |
|       \        |
|        \       |
|         \      |
|          \     |
|           \    |
|            \   |
|             \  |
|              \ |
|               \|
```

## Input 2

```
18
```

## Output 2

```
|\                 |
| \                |
|  \               |
|   \              |
|    \             |
|     \            |
|      \           |
|       \          |
|        \         |
|         \        |
|          \       |
|           \      |
|            \     |
|             \    |
|              \   |
|               \  |
|                \ |
|                 \|
```

## Input 3

```
20
```

## Output 3

```
|\                   |
| \                  |
|  \                 |
|   \                |
|    \               |
|     \              |
|      \             |
|       \            |
|        \           |
|         \          |
|          \         |
|           \        |
|            \       |
|             \      |
|              \     |
|               \    |
|                \   |
|                 \  |
|                  \ |
|                   \|
```
