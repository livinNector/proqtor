# Proq

Proq - A commandline tool for authoring programming questions at scale.

# Terminology

- ProQ or Proq - short for Programming Question present in a structured markdown template.
- Proq file - A structured markdown jinja2 template containg the Proq.
- Nested proq file - An YAML file containing nested structure for creating structured set of proq in multiple levels.


# The proq commandline

- **`proq`** - The main commandline tool with subcommands for creating, evaluating and exporting programming questions.

## Subcommands
Use `proq subcommand --help` to know more about the subcommand.

- `proq create` - create a markdown template (proq files) for authoring the programming questions.
- `proq evaluate` - evaluate the testcases configured using the build and compile process defined proq files.
- `proq export` - export a Proq file or a Nested proq file as JSON, html or pdf.
