---
name: naming-check
description: Checks whether the variable and function names in a Python homework are lowercase English with underscores (snake_case). Use it when reviewing a homework and you need to list the naming problems.
---

# Naming Check

Check assigned variables, function names and function parameters, and list every name that breaks the rule.
Name format: one leading underscore is allowed, followed by a lowercase English letter, and then lowercase English letters, digits or underscores.
For repeated names, list only the place of the first definition; don't check class names; skip self and cls.
This exercise has no exception for constants: MAX fails; result_2 passes.
If no name breaks the rule, answer "OK: all names follow this course's rules".

Output format: one line per problem, for example "Line 3: myVar"
