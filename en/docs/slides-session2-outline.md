# Session 2 slide outline: Agent Skills and the system's division of labor

The HTML deck has 57 slides: 40 main-line slides and 17 optional slides for after class. The existing graphics and styles are kept, and each slide maps to its original page by a stable ID. Slide numbers follow the current presentation order.

## Two-hour schedule

| Time | Content | Done when |
| --- | --- | --- |
| 0:00–0:08 | Review, the request, and the first draft | You know the three outputs: normal, syntax error, and retry limit reached |
| 0:08–0:28 | 2-A Skill | First learn how a handbook is picked; A (picking) and B (editing the body) are required; C moves to optional reading after class |
| 0:28–0:48 | 2-B Three placements of the same check | You can say that how it is done and who controls when it runs are two separate questions |
| 0:48–0:58 | Break | 10-minute break |
| 0:58–1:08 | 2-C Security | Compare the same handbook with and without the fake-key tool |
| 1:08–1:23 | 2-D Combining workflow and agent | About 7 minutes for integration, about 8 minutes for the three saved states |
| 1:23–1:48 | System design | Roles can be combined; run independent batches first, then consider parallelism or sub-agents |
| 1:48–2:00 | Student task and wrap-up | 8 minutes of design, 4 minutes of sharing and summary |

## Slide order

| New slide | Original page / stable ID | Content | Type |
| --- | --- | --- | --- |
| 1 | 1 / s2-001 | Title | Main line |
| 2 | 2 / s2-002 | Today's route | Main line |
| 3 | 3 / s2-003 | Three things you learned last week | Main line |
| 4 | 4 / s2-004 | Sticky note: a real request | Main line |
| 5 | 5 / s2-005 | Stop 1: Skill handbooks | Main line |
| 6 | 6 / s2-006 | Last week's leftover problem: feedback style hard-coded | Main line |
| 7 | 7 / s2-007 | What do you give a new colleague on day one? | Main line |
| 8 | 8 / s2-008 | What a handbook looks like | Main line |
| 9 | 9 / s2-009 | Pick a handbook by its card, then read the body | Main line |
| 10 | new / s2-new-skill-choice | Experiment A: change only the request, see which handbook is picked | Main line |
| 11 | 11 / s2-011 | Experiment B: keep the handbook, add one rule | Main line |
| 12 | 12 / s2-012 | Handbook attachments: scripts and reference material | Main line |
| 13 | 13 / s2-013 | Stop 2: Code · Text · Scripts | Main line |
| 14 | 14 / s2-014 | One naming check, three placements | Main line |
| 15 | 15 / s2-015 | Placement A: the model judges from the handbook text | Main line |
| 16 | 16 / s2-016 | Placement B: the model picks a tool, a script checks | Main line |
| 17 | 17 / s2-017 | Placement C: the workflow always runs the same check | Main line |
| 18 | 18 / s2-018 | Two questions, decided separately | Main line |
| 19 | 19 / s2-019 | Pause: five tasks, two questions each | Main line |
| 20 | 20 / s2-020 | 10-minute break | Main line |
| 21 | 21 / s2-021 | Stop 3: Security and integration | Main line |
| 22 | 22 / s2-022 | Can you use someone else's handbook as is? Observe first | Main line |
| 23 | new / s2-new-permissions | Same handbook, only the available tools change | Main line |
| 24 | 23 / s2-023 | Three habits before using an external Skill | Main line |
| 25 | 24 / s2-024 | Combining workflow and agent: wiring handbooks and tools | Main line |
| 26 | 25 / s2-025 | Where workflow meets agent: load the handbook, provide the tools | Main line |
| 27 | new / s2-new-checkpoint | Pause once, then resume with the same ID | Main line |
| 28 | new / s2-new-checkpoint-compare | Then compare: a finished ID vs. a new ID | Main line |
| 29 | 28 / s2-028 | Stop 4: What goes where | Main line |
| 30 | 30 / s2-030 | Back to the sticky note: does every step need an agent? | Main line |
| 31 | 31 / s2-031 | Feature 1: fetching homework from GitHub | Main line |
| 32 | 32 / s2-032 | Syntax, tone, and the assignment: separate responsibilities | Main line |
| 33 | 35 / s2-035 | Pause: which checks must run on every submission? | Main line |
| 34 | 36 / s2-036 | Reviewing 200 submissions: independent first, then parallel | Main line |
| 35 | 37 / s2-037 | Verifying feedback: rules first, then independent judgment | Main line |
| 36 | 39 / s2-039 | Before sending email, make the flow wait for confirmation | Main line |
| 37 | 40 / s2-040 | The Homework Helper's full division of labor | Main line |
| 38 | 42 / s2-042 | Six questions to ask, in order, when designing | Main line |
| 39 | 43 / s2-043 | 8 minutes: your turn to design | Main line |
| 40 | 44 / s2-044 | Wrapping up both sessions | Main line |
| 41 | 46 / s2-046 | After class: optional reading by need | Optional after class |
| 42 | 10 / s2-010 | Optional after class: swap the cards, see if the pick changes | Optional after class |
| 43 | 26 / s2-026 | Optional: checking a pure agent with code | Optional after class |
| 44 | 27 / s2-027 | Optional: a fixed test set, before vs. after a change | Optional after class |
| 45 | 34 / s2-034 | Optional reading: when data grows, retrieve before answering (RAG) | Optional after class |
| 46 | 45 / s2-045 | Optional reading: from demo to maintainable | Optional after class |
| 47 | 47 / s2-047 | Supplementary: moving to the cloud | Optional after class |
| 48 | 41 / s2-041 | The division of labor in the cloud: where each box lives | Optional after class |
| 49 | 48 / s2-048 | Leaving Colab: three things to replace | Optional after class |
| 50 | 49 / s2-049 | Packaging: langgraph.json is the packing slip | Optional after class |
| 51 | 50 / s2-050 | Optional reading: choose a deployment by operational needs | Optional after class |
| 52 | 51 / s2-051 | Moving each role to the cloud | Optional after class |
| 53 | 52 / s2-052 | Reviewing 200 at once: Send | Optional after class |
| 54 | 53 / s2-053 | Waiting for confirmation before sending: interrupt | Optional after class |
| 55 | 54 / s2-054 | After launch: observable and containable | Optional after class |
| 56 | 55 / s2-055 | References and further resources | Optional after class |
| 57 | 56 / s2-056 | References (cont.): supplementary and cloud | Optional after class |

## Notebook alignment and teaching notes

For the check of saved outputs from 2026-11-03 and the items still to be synced, see [Notebook output review](notebook-output-review.md). "Saved result from this run" on a slide means what was actually observed that time; it is not a promise that every rerun will match.

- **2-A: change one variable at a time.** Part 1 introduces the handbook. In Part 2, Experiment A changes only the request. Experiment B fixes the beginner request and the description, has the program choose friendly-feedback, and adds only a rule 5 under rule 4, the closing rule "Next step: please test again" (the first four rules stay as they are). Experiment C is optional after class: the program restores the original body and then swaps only the descriptions. Each run shows the current request, the chosen handbook, and the rules in effect. Experiment B does not pick a handbook again; explain the picking mechanism first, then use A to observe the pick and B to fix the handbook and observe the body. If the model does not follow the new rule, record that as it is. Each text cell overwrites the handbook at the same path, so confirm what was loaded this time. Token counts and downloading an official Skill are optional.
- **2-B: predict first, then see the answer.** The naming rule and the homework are shared. Look at variables, functions, and parameters; digits are allowed and constants are not exempt. A has the program call the model directly (no tool choice); record the actual result and do not rerun until it differs. B separately checks whether the tool was called, the script result, and the final relay. C uses the same script. Record a parse failure of the output separately from a check error. Three identical runs do not show general reliability. In Part 6, the assignment "generate at most three times" includes the first generation, so generating and rewriting are not mixed up.
- **2-B: two decisions.** How it gets done: fixed rules can use code or a script, and judgment criteria go in the handbook. Who controls when it runs: required steps go in the workflow, and on-demand ones can be given to the agent as a tool. The exercise allows different answers under different conditions, and does not teach code, handbooks, and scripts as mutually exclusive categories.
- **2-B: main thread of the explanation (slides 14–18).** Fix the same homework and rule first, then ask "who does the checking, and who controls when it runs?" From A to B, the check moves from the model to a script; from B to C, the same script is reused and the workflow now guarantees it runs. In A, look at the judgment and the parsed result; in B, look separately at the tool call, the script's raw output, and the final relay; in C, look at the node's execution and the State result. Each slide's speaker notes give wording you can use as is.
- **2-C: predict → permission comparison → locate.** Part 1 introduces the handbook and the prediction. Part 2 compares the behavior of the same handbook with and without read_env. Part 3 then finds the suspicious instruction from the tool record and the reply, using only fake demo keys. Record it if nothing leaks, and do not treat that as proof of safety; text guessed without permission is not the same as reading the data. Scripts, encodings, and scanners are optional.
- **2-D: pairing the assignment.** The assignment and the code enter State together; read_spec reads this submission's assignment, and a resumed save uses the same one. A save from an older version without a spec requires a brand-new ID, and the original save stays.
- **2-D: connection points and output.** First observe skill_loader, the inner tool calls, and the outer format check; the default handbook does not automatically follow your edits from 2-A. A syntax error is reported as a syntax error; normal feedback needs Strengths/Improvements; the maximum generations include the first; reaching the limit while still failing is reported as not passed and must not be counted as success. Finish the integration with the syntactically valid default homework first, then try the error branch.
- **2-D: the three saved states.** Only the same unfinished ID resumes; a never-used new ID with new input starts from the beginning; viewing a finished ID shows the finished state. Viewing history is not a history rerun, which is left for optional reading. On one slide, do the Part 3 pause and the first round of Part 4 (resume). On the next slide, compare the second round of Part 4 (a finished ID) and the third round (a brand-new ID); Part 5 views the history. The minimum is being able to explain these three states and which steps ran. To redo the experiment, rebuild the paused state as the notebook says, and do not reuse a finished ID.
- **2-D eval: optional after class; be clear about the architecture switch.** What it compares is a pure agent's baseline against a prompt change, not the main line's combined workflow and agent. The scoring does not call the model again, while the agent under test still uses a model. A pass rate over five tests describes only that run; a workflow still needs tests for routing, format, and content.
- **System design: roles can be combined.** A tool is an ability to act, MCP is one way to connect, a Skill is the way and criteria for doing something, and the workflow is control. A Skill does not automatically hide MCP tool schemas. First discuss using the same agent on independent inputs one by one, then limited parallelism if speed requires it; a sub-agent needs a reason of context, permission, or independent judgment, not just a different tone.
- **The GitHub requirement and the demo boundary (slide 31).** Collecting homework from GitHub is the design goal. 2-E currently uses five homeworks in a Python dictionary as the data source, served through a real custom MCP server that provides list_homework and get_homework; the workflow calls them directly and does not connect to students' GitHub repos. Both stdio and HTTP are local demos on Colab, and sending email only writes to a simulated outbox. Connecting to GitHub means implementing or adapting tool names, parameters, and return formats.
- **The latest real counter-example (slides 35 and 54).** 2-E once let feedback with an ambiguous indentation level pass model verification. Four spaces per level does not mean four spaces on every line; before sending, still check the full suggested edit, and rerun syntax and behavior tests if needed.
- **Verification: fixed rules first, then semantic review where needed.** A verifier needs the assignment, the original homework, and the draft feedback, not an isolated answer. It can also be wrong. 2-E is a simplified version: no assignment attachment and no read_spec, and the auditor only sees the homework with line numbers and the feedback. The confirmation before sending must be a required node in the flow, so no other tool path can bypass it.
- **The wrap-up order is fixed.** The full division-of-labor diagram → the six design questions → the student task → the two-session summary. RAG, eval, the production checklist, and deployment all move to optional reading after the summary, with no added in-class explanation.
- **2-E: keep the outcome stages separate.** Simulated tools and human confirmation in Colab, a local API, generating deployment files, and actually building and deploying are different stages of completion. Generating a Dockerfile or langgraph.json does not mean it is publicly live; no real email is sent in class.

## Pause points and merged slides

- **2-A (20 minutes)**: background and handbook about 5 minutes, the picking mechanism about 2, the A picking activity about 3, B editing the body about 5, comparing results and attachments about 5. In Part 1, stop to identify the card and the body; stop after A before B; stop after B, and don't let students run on into C. The explanation of C moves to appendix slide 42. The notebook code and the A→B→C order need no changes.
- **2-D (15 minutes)**: integration about 7 minutes; pause and resume about 4; the finished/brand-new ID comparison about 3; viewing history about 1. Slide 27 does one unfinished-thread resume only; slide 28 does the finished and brand-new IDs, ending with the Part 5 history. Use the syntactically valid default homework first, and confirm the next station before continuing.
- **System design (25 minutes)**: slides 29–38, 10 slides in all. Opening and roles 2 minutes, fetching homework 3, syntax and tone comparison 3, the must-run-checks activity 3, independent batches 3, verification 3, confirmation before sending 2, the whole diagram 3, the six-question recap 2, and about 1 minute of buffer. In each case, students add one row to the same design sheet; the six questions are only a review, not a re-teach.
- **The last 12 minutes**: slide 39, student design, 8 minutes; slide 40, sharing and summary, 4 minutes. The appendix starts at slide 41, and we don't keep teaching after the main line ends.

Merges this time: `s2-029` (back to the sticky note) merged into `s2-030`; `s2-033` (tone and assignment requirements) merged into `s2-032`; `s2-038` (division-of-labor principles) merged into `s2-036` and `s2-037`. Added `s2-new-skill-choice` and `s2-new-checkpoint-compare`. `s2-010` moved to the appendix. All other stable IDs are kept; the table is the authority for the order.

## How to teach it

Students need only basic Python: variables, functions, dictionaries, if, and loops. The core activities are running prepared cells, editing a request or text, and observing records; API implementation details and cloud setup are not prerequisites. For each observation, have students predict first, then see the result; don't require the model to act out a default failure. The original slides' source numbers are kept on the HTML reference pages, and specifications and prices of external services should follow the official documents at the time of use.
