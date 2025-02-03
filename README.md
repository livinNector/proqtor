# Proq

Proq - A command line tool for authoring programming questions at scale.

## In this Package
- `ProQ` - A pydantic model defining a programming question. This provides an pyhton API that can be used to integrate proq with other code evaluation environments.
- [**Proq file format**](#proq-file-format) - A Markdown based jinja template format for authoring a proq in a human readable format.
- [**Proq set config file format**](#proq-set-config-file) - An YAML file that defines a set of proqs with heading outline with references to the proq file.
- `proq` - A command line tool for working with proq files.

This library defines a pydantic model for a programming question and a markdown based jinja template format for authoring a proq which can be loaded as the proq model.


## The proq command line

- **`proq`** - The main command line tool with sub-commands for creating, evaluating and exporting programming questions.

### Installation

To use proq as a command line the recommended way is to install it as a tool using `uv`. See [here](https://docs.astral.sh/uv/getting-started/installation/) here for instructions regarding using `uv`.
```
uv python install 3.12
uv tool install git+https://github.com/livinNector/proq.git
```

### Commands

Use `proq [command] --help` to know more about the sub-command.

- `proq create` - create a empty proq file templates for authoring the programming questions.
- `proq evaluate` - evaluate the test cases configured using the build and compile process defined proq files.
- `proq correct` - corrects the given proq by computing the outputs from the inputs and the solution given.
- `proq export-test-cases` - export the test cases into a folder with two subfolders public and private with the inputs and outputs as text files.
- `proq show-code` - Displays the different sections of the code block in a highlighted manner.
- `proq export` - export a **proq file** or a **proq set config file** as JSON, html or pdf.

### Examples

#### Creating a proq

1. Default template (uses python).  
   ```bash
   proq create sample.md
   ```
2. Specifying number of public and private testcases.  
   ```bash
   proq create --num-public 3 --num-private 5 sample.md
   ```
3. Specifying the programming language. Currently `python`, `java` and `c` are supported. For other languages the execute config have to be configured manually ([see here](#code-block-header---execute-config)).  
   ```bash
   proq create --lang c sample.md
   ```

#### Evaluating a proq

1. Evaluating a single proq file.  
   ```
   proq evaluate sample.md
   ```

2. Evaluating a single proq file in verbose mode displaying what went wrong.
   ```
   proq evaluate sample.md -v
   ```

3. Evaluating multiple files.
   ```
   proq evaluate sample1.md sample2.md sample3.md
   ```
   This evaluates the given three files.

4. Evaluating multiple files using glob patterns and brace expansions.
   ```
   proq evaluate sample*.md 
   proq evaluate sample{1..4}.md
   proq evaluate sample{1,3}.md
   ```
   This evaluates the files that are expanded as the result.

#### Correcting a proq
1. Correcting a single proq file.
   ```
   proq correct sample.md
   ```
2. Correcting a single proq file.
   ```
   proq correct sample*.md 
   proq correct sample{1..4}.md
   proq correct sample{1,3}.md
   ```

#### Exporting the Test Cases
1. Exporting the test cases as a folder
   ```
   proq export-test-cases sample.md
   ```

2. Exporting the test cases as a zip
   ```
   proq export-test-cases sample.md --zip
   proq export-test-cases sample.md -z
   ```

#### Displaying Code block


#### Exporting a proq

`proq export` supports exporting to `json`, `html` and `pdf` formats. PDF conversion uses the systems chrome executable. It uses `'chrome'` as the default executable name. To set a different executable name configure `CHROME` environment variable.

1. Specifying only the format. Uses the same file name with the extension of the export format. 
   ```
   proq export sample.md -f pdf
   ```
   This will create a file called sample.pdf  

2. With different chrome executable.
   ```
   export CHROME=google-chrome-stable
   proq export sample.md -f pdf
   ```
3. Hiding Private testcases in the HTML or PDF output.
   ```
   proq export sample.md -f html --hide-private-testcases
   ```

## Proq File Format

The **Proq File Format** is a structured way to define coding problems, solutions, and test cases using a combination of Markdown-based Jinja templates. This format ensures clarity, flexibility, and compatibility with auto-grading environments. Each file is divided into well-defined sections with specific purposes and annotations.

The proq file is a jinja template which is rendered before loaded.

### File Structure

A Proq file is composed of three main sections:
1. **YAML Header**
2. **Problem Statement**
3. **Solution**
4. **Test Cases**

### 1. YAML Header
The YAML header contains metadata about the problem, such as its title and tags. The `title` and `tags` is defined in the pydantic model. But also support additional tags.

**Example**
```yaml
---
title: Delete first three elements of a list
tags: ['list','list manipulation','slicing']
---
```

### 2. Problem Statement
This section describes the coding task to be solved, along with examples to clarify the requirements. 

### 3. Solution
The solution is defined in a Markdown code block and annotated with special HTML-like tags to structure the code into editable and non-editable parts.

#### Solution Parts Overview:
- **Template** (Required): The `<template>...</template>` tag denotes the editable area of the code which can contain multiple `<sol>...</sol>` and `<los>...</los>` tags within. The template includes the parts of the code that common in both solution and the editable template.
  - `<sol>...</sol>`: Marks the content that is only present in the solution.
  - `<los>...</los>`: Marks the content that is only present in the template.
- **Prefix** (Optional): The part above the template block.  
  Non-editable code that appears before the main solution.
- `<template>...</template>`(Required):  
  
- **Suffix** (Optional): The part below the template block. 
  Non-editable code after the solution.
- **Invisible Suffix** (Optional):  The part comes after the suffix whose begining is marked by the opening tag `<suffix_invisible>`.
  Non-visible code for additional functionality or testing.

#### Code Block Header - Execute Config

The language specified in the start of the solution code block is considered as the coding language. In addition to the language, the first line also has some arguments that resemble command line arguments of the below format.
```
```lang FILE_NAME -r 'RUN_COMMAND' -b 'BUILD_COMMAND'
```
**Examples**

```
```python test.py -r 'python test.py'
```

```
```c test.c -b 'gcc test.c -o test' -r './test'
```

This is used for local evaluation of the programming assignments.

**Sample Solution**
````markdown
# Solution

```python test.py -r 'python test.py'
# Anything above the template is the prefix part
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
# Visible part of the suffix would go here
<suffix_invisible>
{% include '../function_type_and_modify_check_suffix.py.jinja' %}
```
````

### 4. Test Cases

Test cases verify the solution and are divided into **Public** and **Private** cases. Each case specifies input, the function call, and the expected output. The Test cases will have the following structure. The code blocks inside the second level headings are alternatively assumed to be inputs and outputs. **Each Input and Output header should be unique.**

````markdown

# Public Test Cases

## Input 1
```
Some input
```

## Output 1
```
Some output
```

# Private Test Cases

## Input 1 - With Some info
```
Some hidden input
```

## Output 1 
```
Some hidden output
```
````

## Proq Set Config File

A proq set config file can be used to define a set of proqs under different sections and subsections in a yaml having the following structure.

```python
class NestedProq:
  title: str 
  content: NestedProq | str # relative path to the proq file
```

### Example
See [assessment.yaml](examples/python/assessment.yaml) and [unit.yaml](examples/python/unit.yaml)

## ProQ Python API

See [core.py](src/proq/core.py) and [prog_langs.py](src/proq/prog_langs.py) for proq related classess and functions.
