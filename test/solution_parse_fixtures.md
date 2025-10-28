No blank lines
.
```py test.py -r 'python test.py'
# prefix
<template>
def test():
  <los># one line placeholder</los>
  <sol># one line solution</sol>
  a = <los>...</los><sol>input()</sol>
  <los>
  # placeholder line 1
  # placeholder line 2
  </los>
  <sol>
  # solution line 1
  # solution line 2
  </sol>
</template>
# suffix
```
.
```python
# prefix
```
.
```python
def test():
  # one line solution
  a = input()
  # solution line 1
  # solution line 2
```
.
```python
def test():
  # one line placeholder
  a = ...
  # placeholder line 1
  # placeholder line 2
```
.
```python
# suffix
```
.
```python
# prefix
def test():
  # one line solution
  a = input()
  # solution line 1
  # solution line 2
# suffix
```
.
With blank lines inside template
.
```py test.py -r 'python test.py'
# prefix
<template>
def test():
  <los># one line placeholder</los>  
  <sol># one line solution</sol>

  a = <los>...</los><sol>input()</sol>

  <los>
  # placeholder line 1
  # placeholder line 2
  </los>
  <sol>
  # solution line 1
  # solution line 2
  </sol>
</template>
# suffix
```
.
```python
# prefix
```
.
```python
def test():
  # one line solution

  a = input()

  # solution line 1
  # solution line 2
```
.
```python
def test():
  # one line placeholder

  a = ...

  # placeholder line 1
  # placeholder line 2
```
.
```python
# suffix
```
.
```python
# prefix
def test():
  # one line solution

  a = input()

  # solution line 1
  # solution line 2
# suffix
```
.
With new lines around template tag
.
```py test.py -r 'python test.py'
# prefix


<template>  


def test():

  <los># one line placeholder</los>
  <sol># one line solution</sol>

  a = <los>...</los><sol>input()</sol>

  <los>
  # placeholder line 1
  # placeholder line 2
  </los>
  <sol>
  # solution line 1
  # solution line 2
  </sol>


</template>


# suffix
```
.
```python
# prefix


```
.
```python


def test():

  # one line solution

  a = input()

  # solution line 1
  # solution line 2


```
.
```python


def test():

  # one line placeholder

  a = ...

  # placeholder line 1
  # placeholder line 2


```
.
```python


# suffix
```
.
```python
# prefix




def test():

  # one line solution

  a = input()

  # solution line 1
  # solution line 2




# suffix
```
.
Indented Template with no blank line
.
```py test.py -r 'python test.py'
# prefix
def test():
  <template>   
  <los># one line placeholder</los>  
  <sol># one line solution</sol>
  a = <los>...</los><sol>input()</sol>
  <los>
  # placeholder line 1
  # placeholder line 2
  </los>
  <sol>
  # solution line 1
  # solution line 2
  </sol>
  </template>
# suffix
```
.
```python
# prefix
def test():
```
.
```python
  # one line solution
  a = input()
  # solution line 1
  # solution line 2
```
.
```python
  # one line placeholder
  a = ...
  # placeholder line 1
  # placeholder line 2
```
.
```python
# suffix
```
.
```python
# prefix
def test():
  # one line solution
  a = input()
  # solution line 1
  # solution line 2
# suffix
```
.
Indented template with new lines around template tag
.
```py test.py -r 'python test.py'
# prefix

def test():

  <template>   

  <los># one line placeholder</los>  
  <sol># one line solution</sol>

  a = <los>...</los><sol>input()</sol>

  <los>
  # placeholder line 1
  # placeholder line 2
  </los>
  <sol>
  # solution line 1
  # solution line 2
  </sol>

  </template>

# suffix
```
.
```python
# prefix

def test():

```
.
```python

  # one line solution

  a = input()

  # solution line 1
  # solution line 2

```
.
```python

  # one line placeholder

  a = ...

  # placeholder line 1
  # placeholder line 2

```
.
```python

# suffix
```
.
```python
# prefix

def test():


  # one line solution

  a = input()

  # solution line 1
  # solution line 2


# suffix
```