---
name: naming-check
description: Checks whether the variable and function names in a Python homework are lowercase English with underscores (snake_case). Use it when reviewing a homework and you need to list the naming problems.
---

# Naming Check

Run scripts/check_naming.py (the tool is named check_naming) and write its output into the feedback.
Don't judge by yourself, and don't add or drop any item. Copy every line it prints.

Shared rules: check assigned variables, function names and function parameters; for repeated names, list only the first definition; don't check class names; skip self and cls.
A name may have one leading underscore, followed by a lowercase English letter, and then lowercase English letters, digits or underscores.
This exercise has no exception for constants: MAX fails; result_2 passes. The script runs these rules.

Output format: copy every line the script prints, for example "Line 3: myVar breaks the rule (suggest my_var)"
