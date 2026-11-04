# Saved Notebook Output vs. the Slides

## Latest Colab-saved version: d2c81b7

After another pull on 2026-11-03, the new commits only updated the output of 2-B and 2-E. All eight notebooks are valid in format, and the saved output contains no error cells. All program sources are identical to 12235d3, which already passed the 19 tests and the eight-notebook flow check. So this round did not regenerate any notebook and did not overwrite any Colab result.

| Notebook | Cells with output / code cells | Match with the slides |
| --- | --- | --- |
| 1-0 | 2/9 | The new core cells are blank. The slides already say which version the historical handoff demo comes from. |
| 1-A | 10/10 | The missing-parenthesis branch and the first draft passing the format check agree with the slides. |
| 1-B | 16/18 | The new counts cell and the MCP list cell are blank. The old accumulated history cannot stand in for new output. |
| 2-A | 13/16 | The new A / B / C cells are blank. The existing history only holds the old baseline and must not pose as the new comparison. |
| 2-B | 14/14 | The new three runs still find six items each, and the model calls total 3/6/0, which matches slides 14–18. |
| 2-C | 11/12 | The new locating-prompt cell is blank. The line numbers in the old history are still 0, and the slides do not wrongly claim it was done. |
| 2-D | 5/11 | The new State.spec flow, pause / resume, eval, and other cells do not yet have output for this version. We only confirmed that the code and the instructions agree. |
| 2-E | 21/21 | The MCP, local HTTP, API, and human-confirmation runs all finished. There is one content-quality counterexample, described below. |

Blank output only describes what is saved in Git. It does not mean the user did not run the cell in Colab. The reasons for the blanks from the earlier rebuild, and the snapshots of real output, have all been kept. The two new commits this round did not bring back new output for the other notebooks, so we still cannot confirm that all the cells of the new version passed a real-model check.

### Content-quality counterexample found in the new output

In 2-E cell 17, the feedback for Fiona both asks to standardize to four spaces per level and suggests changing `total += s` to four spaces, without saying it sits inside the `for` loop. The verifying agent still judged that feedback as passed, and cell 19 also recorded a simulated send after the human confirmation.

The original program's two-space / eight-space indentation still parses. Changing only the inner eight spaces to four and keeping the outer two spaces also still parses. The problem is that if you standardize to four spaces per level, the `for` should be at four spaces and the inner statement at eight. If both are put at four spaces, you get an IndentationError. We confirmed these three cases with `ast.parse`, and we did not wrongly write a conditional risk as a line that always fails.

Slide 35 (s2-037, "Verifying feedback: rules first, then independent judgment") now includes this real counterexample, and slide 54 (s2-053, "Waiting for confirmation before sending: interrupt") adds that human confirmation should check the suggested edit, not just the "verification passed" flag. The other slides agree with the output we can currently check, and the numbers in 2-B need no change. This is a quality limit of model auditing. It is not a notebook error cell, and it does not mean all feedback is correct.

---

## Previous full review and fix log

Review date: 2026-11-03. This round was based on `2aabc81` on GitHub `main`. Three subagents split up the work of cross-checking the eight notebooks, using the Colab output that was really saved. We did not fill anything in with local fake-model output.

The table below describes the real-output snapshot before the fixes. The program fixes and the new-version verification from this round are listed separately further down. These records do not mean the user never ran the experiments that lack output. Cell indexes start from 0. "Has output" also counts file writes, downloads, and prompt messages, so it cannot be used directly as a completion rate for the experiments.

| Notebook | Code cells with output / total | Result of the check |
| --- | --- | --- |
| 1-0 | 2/9 | The current file only has the save and download output. A full snapshot of the older version, with output in 9/9 cells, was found separately. |
| 1-A | 10/10 | Added AI feedback: it passed the format check after one generation. We still have no saved comparison for a rejected rewrite or for failing at the limit. |
| 1-B | 18/18 | The new output is complete. The step-limit experiment mixed up tool-request counts and actual executions, and the MCP list label also needed adjusting. |
| 2-A | 16/16 | The new output is complete, but all of it is baseline conditions. There are no saved before/after comparisons for changing the request, changing the closing rule, or swapping the description. |
| 2-B | 14/14 | A / B / C each found the same six items in all three runs, and the model calls total 3/6/0, which matches the slides. |
| 2-C | 12/12 | The permission comparison and the scan have results. The locating question is still filled with 0, so only the handbook is displayed and nobody has answered yet. |
| 2-D | 11/11 | Integration, pause, one resume, and history are saved. The eval went from 1/5 to 5/5. There was also a problem pairing homework with its assignment. |
| 2-E | 21/21 | MCP, a single-homework review, human confirmation, and a local API batch of five all have results. The pre-launch check still has three warnings. |

Before the fixes, none of the eight saved notebooks had an `output_type=error`. Blank output, or an optional cell that was not enabled, cannot be used to judge that it passed.

## Check results for all eight notebooks this round

- All eight notebooks pass format validation. The 19 regression tests pass. The fake-model flow check, run start to finish on all eight, passes. The fake-model results are saved in separate ignored executed files. They do not overwrite the real Colab output, and they do not show real model quality.
- Before the fixes, only the eval form value in 2-D differed from the generator's default. After the rebuild, changed code cells do not keep old output. The complete old code and output are saved in a snapshot, and the eval goes back to the optional default of False.
- The new 1-0 still only has the backup and download output. The full historical version is kept. Blank output cannot be used to infer that the user did not run it.

### Three problems fixed

1. **1-B counts separated.** It now counts the tool requests for always_fail and the ToolMessage returns separately, and prints and records them in two fields. A regression test reproduces 13 requests and 12 returns before reaching the limit, confirming they are no longer mixed up.
2. **1-B permission list aligned.** It first lists the three MCP tools the server can provide, then the five tools actually given to the agent (three local tools and two MCP read tools). The printed list is exactly the list that create_agent receives, and it does not include send_email. A test checks that the display, the record, and what is actually passed in all agree.
3. **2-D pairs each homework with its assignment.** The new input uses an explicit mapping to store the assignment in State.spec, and the read_spec tool is bound to that homework's assignment. It no longer reads a global spec.md. After a pause it uses the saved assignment, and the average and addition threads run interleaved without affecting each other. A missing assignment or an unknown homework no longer falls back to a wrong default assignment. The optional eval also builds a matching tool for each question. If an old checkpoint has no spec, the operation cell tells you to use a brand-new ID and keeps the original checkpoint.

### Run, but the comparison conditions are not complete

- **2-A**: A only saved the beginner request. B saved the original handbook, so "ends with the specified sentence = False" is the baseline result, and you cannot say the model violated the new rule. C's description was not swapped. The history has accumulated ten rows, but they are still two identical baseline rounds. A proper comparison still requires changing the specified conditions according to the instructions. C is optional.
- **2-C**: The locating question is still filled with 0 and only displays the handbook, so the learner's locating answer is not done. The permission comparison and the scan results are valid.
- **1-A, 2-D**: The success branches that exist can be checked. Branches without saved results, such as failing at the generation limit or the other thread states, cannot be claimed as tested.

This round fixed the three items above, and strengthened the baseline / after-change completion conditions of 2-A and the line-number-0 prompt of 2-C. Before the four changed notebooks were rebuilt, their real code, forms, output, and execution counts were all saved in full in the [latest snapshot](../notebooks/output-history/README.md). The new versions only keep output from sources that are exactly the same. The program flow and regression tests use the fake model, and they do not replace a real-model check of the new version on Colab.

## Explanations fixed based on the output

- **2-B / slide 18**: Added the observation that all three versions were correct this time. The model calls 3/6/0 are totals over three runs each. B's "keeps every item" comparison checks line numbers and the set of names. It is not a verbatim comparison of the whole text.
- **2-C / slides 23–24**: This time, with the read_env tool, the fake data was fetched and printed. After removing it, nothing was. The line-by-line locating still has to be done. The three habits in the notebook are now unified as "check the content / limit permissions / confirm the source and version", and the slide references for the scanner and the locating section were corrected.
- **1-A / slide 27**: This time the baseline was at most 3 generations and 150 characters in the Chinese edition (the English edition uses 450 characters). The first draft already had format_ok=True, so only one generation happened. 30 characters (90 in the English edition) with at most 1 generation is the next observation condition, and there is no saved result for that round yet.
- **2-D / slide 44**: The measured result saved before the fixes was baseline 1/5 → v2 5/5. All four baseline failures happened because the first tool was not check_syntax. The scoring only checks tool order and reply keywords. It does not mean the feedback is correct overall, or that the score will always be perfect later. The eval stays optional.
- **2-E / slides 48 and 50**: The deployment diagram and project tree now use the real deploy/multi_agent.py, check_naming, and run_code. 2-E fixes a mild handbook and verifies after reviewing. 2-D is where picking a handbook and a full format redo are shown.
- **2-E / slides 52–55**: Separate the Colab local HTTP from a cross-machine remote deployment. 200 submissions is an extended scenario, and no parallel-speed comparison was saved this time. The pre-launch check still has three warnings: the model credentials, SQLite persistence, and the remote MCP.
- **Reading 2-E results**: "Verification passed" means the feedback check passed. It does not mean the student's homework is correct. A syntax-error notice can also pass the feedback check. Chloe did not call a tool this time, yet there were still two model calls, one to review and one to verify. We cannot claim her homework was run.

## Confirmed reason for the reduced output, and the recovery

Git history proves that these three notebooks used to have full output: commit `8d4b4b3` has 9/9 for 1-0, 18/18 for 1-B, and 11/11 for 2-A. After the course material was edited, commits `1d5246d` and `5653194` rebuilt the notebooks. The generator only keeps output for code cells with exactly the same source, so the cells that were changed became blank. This is not evidence that the user did not run or save them.

The three original notebooks have been fully restored to [output-history](../notebooks/output-history/README.md). They include the code at the time, the forms, the real output, and the execution counts, and they are byte-identical to the original commits. The latest notebooks do not attach historical output that no longer matches.

Historical observations:

- **1-0**: With history, it answered Alice. Without history, it did not know the name. The missing-parenthesis sample did not call a tool, and the model judged it directly. The single handoff really ran print(1+1) and returned 2. In the loop, the first run hit a NameError, and on the next round the model explained it and stopped. Its suggested fix (y=2 and output 6) is only an untested example.
- **1-B**: All three comparison runs answered directly, and the tool order was an empty list each time, so it cannot be forced into "three different runs". always_fail was called 11 times and the model stopped by itself after 23 streamed steps, with no GraphRecursionError. The MCP get_homework → run_code really ran and reported that summ is undefined. send_email was excluded before the tools were given to the agent. The token comparison is an estimate, not a bill.
- **2-A**: Only one beginner request was kept. In the end it loaded friendly-feedback and pointed out that summ should be changed to total. The old loader defaulted to the first handbook when parsing failed, and there was no raw reply from the pick, so the result alone cannot prove the model picked the handbook successfully. There is no comparison for the new version's A (two requests), B (fixed handbook, changed body), or C (swapped description).

## Evidence still missing for the new version

You do not need to re-run anything just to recover old results. Only when you want to accept the new code, or a newly added control condition, do you need to get the real output for that version. A historical snapshot cannot replace it. Keep the existing real output and forms, do not fill in learner answers, and do not run repeatedly to get an illustrative result. The optional eval does not need to be run for this.

The current 1-A records confirm the syntax error and one passing format check, but they do not save every form branch. The current 2-D records confirm an unfinished resume, but there are no saved runs where a finished ID is only retrieved or a new ID starts from the beginning, and no comparison for a syntax failure or a failure at the limit. Every cell having output does not mean every branch is done.

## Limits of the 2-D assignment-pairing check

In the old cells 9 and 15, an average-value homework read the addition assignment, which is the direct evidence for this fix. The new version isolates each assignment through State.spec. Tests confirm the pairing and the resume results for the average, the addition, and interleaved threads. format_ok still only checks the format and cannot replace a review of the feedback content.

The old eval score of 1/5 → 5/5, together with the True form value, is fully kept in the snapshot. In the new eval, each question has its own matching assignment, and the default is still optional (False). The old score cannot be carried over as the new version's score. The real-model feedback quality and the eval score of the new version still have to be confirmed by re-running the changed cells on Colab.

## Safeguards going forward

Before stale output is replaced, the generator now saves the whole original notebook to output-history and prints the location. A snapshot with identical content is not saved twice, and if the backup fails, it stops instead of overwriting. If only Markdown changed and all code output can still be kept, no snapshot is added. Keeping output still uses an exact-source comparison, so old results are never attached to new code by mistake.
