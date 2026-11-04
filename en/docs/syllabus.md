# Syllabus: From LangGraph to Skills

Two sessions of 120 minutes each. The audience is beginners who understand Python dicts, functions, `if`, and `while`. Class follows the rhythm "predict, run, compare, explain why". Learners are not asked to write framework code live.

## Shared learning goals

Both sessions use the same "Homework Helper". By the end, learners should be able to:

1. Tell apart the model's reply, a tool request, what the program actually runs, and the loop that hands the result back to the model.
2. Trace a workflow's State, nodes, and conditional branches, and tell "passed the check" apart from "stopped because the limit on attempts was reached".
3. Keep the homework fixed and change only one of the request, the handbook body, or the description at a time, then observe how a Skill affects selection and replies.
4. Decide separately "where the rule lives" and "who decides when it runs", without treating Skill, tool, and flow node as mutually exclusive options.
5. Point out what a malicious handbook asks for, which tool permission it needs, and which capability disappears when that permission is removed.
6. Distinguish resuming an unfinished checkpoint, retrieving a finished result, and a brand-new run on a new thread.

"Valid syntax", "runs successfully", and "meets the assignment" are three different judgments. This course's examples never claim a homework is correct just because a syntax check passed.

## Session 1: What is an agent, and building one with LangGraph

Date: 2026-11-09. The slides follow the latest order in the [slide-by-slide outline](slides-session1-outline.md).

| Time | Main line | Notebook / activity | Completion check |
| --- | --- | --- | --- |
| 0:00–0:10 | The task, prerequisite ideas, what we build today | Look at the Homework Helper's input and output once | Can say what needs to be checked |
| 0:10–0:35 | Model, context, tool requests, and the loop | 1-0: single reply → manual handoff → loop | Can point out which step is where Python actually runs the tool |
| 0:35–1:00 | State → Node → Edge → conditional branch → limited redo | 1-A: predict the next station, then change the homework and the limit | Can name the syntax-error branch and the reason it stopped |
| 1:00–1:10 | Break | Keep the runtime | n/a |
| 1:10–1:40 | An agent's choices, tool boundaries, and MCP | 1-B main line: try the tools first, build the agent, observe the route and the limit, and finish with an MCP demo | Can read the execution trace; knows it is not the model's internal thinking |
| 1:40–1:55 | When to fix the flow, and when to hand over to the agent | Small design questions, comparison examples | Can give one must-do step and one judgment step |
| 1:55–2:00 | Wrap-up and after-class practice | Write down observations, keep your own files | Can explain the reasons behind their own design |

### 1-0: See the handoff before talking about automation

- The main line first shows the model's answer, then the tool request, then the program running the tool and returning the result.
- The model not calling a tool is also a valid observation. Success does not depend on re-running until the wanted result shows up.
- Context is explained with visible conversation messages. The model does not automatically read local files, or earlier conversation that was not passed in.
- Token and response metadata are supplementary. Measured values and estimated values are kept apart.
- The details of a hand-built loop are not something beginners must memorize.

### 1-A: Understand one state change first, then the redo

Read the input and the expected output first, then look at the State before and after each node. Predict which path a syntax error takes before looking at the format check's rejection.

"Maximum generations" includes the first generation. The compatible field inside the program may still be named `max_retries` (legacy name), but the form and the explanations in class must not describe it as extra retries. The marker check and the character count are only a format check. They cannot verify that the feedback content is correct.

Minimum to finish: use one homework with a syntax error and one with valid syntax, and point out the difference in route. Then tell apart stopping because it succeeded from stopping because it reached the limit.

### 1-B: Understand the tools first, then connect external tools

The main line tests the tools directly first, then looks at the tool descriptions, builds the agent, observes the route and the execution limit, and ends with an MCP handoff demo. When you run it repeatedly, the same route or a different route are both valid. Record what you actually observed. A change is not required.

MCP is a protocol for connecting tools and data. Calling an API directly is also an option. MCP does not mean the model can see how a tool is implemented, and it does not guarantee that all tool descriptions will save context. The agent can only use the capabilities the program gives it as tools.

The hand-built StateGraph and the side-by-side full code are moved to the supplementary material, so they do not interrupt the first hands-on run.

## Session 2: How Skills, tools, and flows work together

Date: 2026-11-16. The slides follow the latest order in the [slide-by-slide outline](slides-session2-outline.md).

| Time | Main line | Notebook / activity | Completion check |
| --- | --- | --- | --- |
| 0:00–0:08 | Recall one tool handoff from last session | Point out model / tool / flow | Can say what each was responsible for last time |
| 0:08–0:28 | Meet the card and the body; pick the handbook first, then change the rules | 2-A: A (pick a handbook) and B (change the body) are required; C (swap the card) is optional | Can say which single thing was changed this time |
| 0:28–0:48 | Three ways to run the same rule | 2-B: text / agent picks a script / flow runs it directly | Reads the raw tool result and the AI's final reply separately |
| 0:48–0:58 | Break | n/a | n/a |
| 0:58–1:08 | Malicious handbook and tool permissions | 2-C: same handbook, with and without the tool permission | Whether or not the model was tricked, can point out the malicious line |
| 1:08–1:23 | Fixed flow outside, agent inside; saving and resuming | 2-D: three checkpoint states | Tells apart resuming, retrieving a result, and a new run |
| 1:23–1:48 | Two design questions, batching and division of labor, human confirmation | Division-of-labor diagram and design discussion | Can say who guarantees each must-do step |
| 1:48–2:00 | Design exercise and wrap-up | Groups fill in the design sheet, peer check | Can draw a minimal system and name one failure-handling step |

### 2-A: Three experiments, one change at a time

1. **A: fix the homework and the two default handbooks; change only the request.** Look at the selected handbook first, then observe the feedback. This builds the relationship between request, card, and handbook.
2. **B: fix the friendly handbook and the beginner request; change only one observable closing rule.** After the change, run the file-writing cell. Compare before and after, and do not change the request at the same time.
3. **C: restore the default content, fix the request, and change only the description.** Observe which handbook gets selected, separately from the effect of the body text.

Picking one handbook first and then reading its body is the behavior of this course's loader. It is not something a model naturally does by scanning a folder. A selection failure should be visible. It should not quietly fall back to the first handbook and cause a misreading.

### 2-B: Compare the reliability of the same rule

The naming rule's scope, the constant exception, and the expected set of names are the same in all three versions. Let learners look at the homework and find the suspicious names first, then reveal the baseline answer.

| Version | How the rule is expressed | Who decides to run it | What to observe |
| --- | --- | --- | --- |
| A | Handbook text | The program asks the model to interpret and judge | The names listed in the reply; three identical runs are also acceptable |
| B | The same rule written as a script; the handbook explains how to use it | The agent decides whether to call the tool | Whether it was called, the raw tool result, the final reply |
| C | The same checking code placed directly in the flow | The program always runs it | Whether the raw check result is consistent |

A script's determinism only covers the script's output for the same input. It does not guarantee that the agent calls it, and it does not guarantee that the AI relays it completely. Names parsed out of natural language are listed separately. Never present the parser's result as the raw tool result.

A and B use different handbook files, so the second experiment does not overwrite the first. When you re-run, run that version's setup cell first.

### 2-C: Fix the handbook, change the available capability

The main line is limited to 10 minutes. Predict first, then use the same handbook to compare having and not having the read_env tool, and find the malicious line from the records. The tool reads only practice fake data. It does not read arbitrary variables from the real environment, and it does not run the remote shell commands in the handbook.

The model refusing the malicious request is an acceptable result. Do not re-run repeatedly until data leaks and then declare the experiment a success. What learners need to understand is the boundary between capability and permission. Static scanning and install-script analysis are supplementary. Key nodes and human confirmation must not be written as only "ask the AI to remember".

### 2-D: Finish one run first, then look at saving

Reserve 15 minutes. This notebook uses a clearly stated default handbook. It does not automatically carry over a file modified in another Colab runtime.

| State | Operation and result | The difference learners should be able to state |
| --- | --- | --- |
| Same thread, a next step remains | Continue the remaining work from the checkpoint | Pick up where it left off |
| Same thread, already finished | Retrieve the saved result. Do not call it re-running | Get the result back |
| New thread | Start from a new initial input | A new run |

Listing historical checkpoints is a history view. It cannot be called Replay. Truly re-running a specific checkpoint is a different operation. The pure-agent comparison and repeated evaluation are optional, so the main line does not pile several new concepts together.

## System design: ask two questions first

**First: how are the rules or knowledge expressed?** They can be Skill text, specification data, or an executable script.
**Second: who decides when it runs?** A fixed flow can call it, or the agent can choose.

The same script can be wrapped as a tool. The same tool can be connected through MCP. A Skill can teach an agent to use it. A workflow can place it at a node that every applicable branch must pass through. These roles can be combined and are not mutually exclusive categories. At run time you still have to handle tool failures and interruptions.

Design order:

1. Find the checks and human confirmations that cannot be skipped, and put them in the program flow first.
2. Turn questions that fixed code can answer into testable tools.
3. Write tone, step-by-step guidance, and situational judgment into the handbook.
4. Confirm which choices are left for the agent, and limit its tool permissions and execution limits.
5. Consider MCP when an external service needs a shared interface. Not every external call needs MCP.
6. For many independent homework submissions, consider batch execution first. Consider sub-agents when there are separable tasks, context, or permission needs.

"Several role names" does not by itself make review reliable. A verifier needs clear pass criteria and evidence that can be cross-checked. Rules that can be written as code are verified by code first. Actions that cannot be decided automatically and that matter go to human confirmation.

### Design sheet

For your own Homework Helper, fill in: input / output, must-do checks, tools, handbook content, what the agent may decide, stop conditions, failure handling, and actions that need human confirmation. Draw the smallest working version first, then explain whether a second agent is needed.

## Main line, optional work, and minimum completion

| Notebook | Main-line result | Optional |
| --- | --- | --- |
| 1-0 | Explain one tool handoff | Token metadata, more loop details |
| 1-A | Predict the branch and identify the reason it stopped | Closer code reading |
| 1-B | Record the tool route and understand the MCP handoff | Hand-built agent |
| 2-A | Change one thing at a time and record the handbook experiment | Write a more complete Skill of your own |
| 2-B | Compare three ways to run the same rule | Add cases; do not assume the model must get it wrong |
| 2-C | Find the malicious line and compare tool permissions | Static scanning and reading install scripts |
| 2-D | Distinguish unfinished / finished / new thread | Pure-agent comparison and eval |
| 2-E | After-class extension | MCP, batching and division of labor, API, pre-deployment checks |

If time runs short, the instructor can demonstrate 2-B, and learners then read the records and answer. Keep the permission comparison of 2-C and the three-state recognition of 2-D. Do not skip the main line's completion checks just to rush through the advanced supplementary material.

2-E first runs one homework to confirm the pipeline, then runs several for a comparison of batching and parallelism. The concurrency limit mainly affects how many run at the same time. Latency, retries, and model calls can change token usage, so no fixed multiplier is guaranteed. Do the API exercise according to its prerequisites. Generating files does not mean a service has been deployed.

RAG, formal deployment, repeated eval, a complete multi-agent system, and a production checklist go in the supplementary slides after the main line wraps up. In class they are only marked as pointers and are not implemented one by one.

## Course material implementation and verification rules

- The notebook sources are scripts/nbspec/ and review-bot/. Do not edit the generated ipynb files directly.
- Large infrastructure blocks are collapsed by default. The handbook and homework that learners edit stay visible. Every main-line experiment has a prerequisite note, a prediction question, and an observation point.
- After editing SKILL.md you must run the file-writing cell. Re-running the setup cell may overwrite your changes, and this must be stated.
- Whether each Part can be re-run on its own depends on its prerequisites. Do not promise that all of them are independent. After a runtime is recycled, redo the environment and file preparation. A browser disconnect does not mean the files disappear immediately.
- When regenerating, only code cells with exactly the same source keep their old output. Old output is not evidence from a real-model check of this run.
- Locally, run the eight notebooks with the fake model to verify program flow. Real model quality, the Colab connection, and the time class actually takes are tested separately in a pre-class trial run.
- After reordering the slides, run scripts/sync_slide_navigation.py to sync the slide-by-slide outline, the notebooks' slide numbers, and the README.

## Further reading

These are for the instructor's extension. Learners are not required to finish them before the two sessions. Detailed sources are listed in the slide appendix.

- [Building effective agents](https://www.anthropic.com/research/building-effective-agents)
- [Agent Skills specification](https://agentskills.io/specification)
- [LangChain 1.0 release notes](https://docs.langchain.com/oss/python/releases/langchain-v1)
- [MCP documentation](https://modelcontextprotocol.io/docs/getting-started/intro)
- [Anthropic skills examples](https://github.com/anthropics/skills)
