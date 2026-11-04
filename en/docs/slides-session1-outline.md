# Session 1 slide teaching order (restructured edition)

Deck: [session1.html](../slides/session1.html), 48 slides in total. Slide numbers follow the revised order; the HTML `s1-NNN` ids keep each slide's original identity so it is easy to trace.

## Timing and learning rhythm

- 0:00–0:10: look at the problem and the finished product first, then explain the learning route.
- 0:10–0:35: model calls, relevant history, tokens, tool requests, and the agent loop; paired with 1-0.
- 0:35–1:00: first separate valid syntax, running, and correctness, then learn State → Node → Edge in a row; paired with 1-A Parts 1–3.
- 1:00–1:10: break.
- 1:10–1:40: test the local tools first, read the tool manuals, build the agent, then watch the trace and the limit; finish with the instructor's MCP demo.
- 1:40–1:55: required checks vs. flexible judgment, combining workflow and agent, the worksheet.
- 1:55–2:00: three takeaways, the homework, and a preview of next session.

For every experiment, write a prediction first, then run it, then compare with the output. Model results may be the same or different; there is no need to rerun until they match the example. Run long file-writing cells directly; look at the visible result first.

## Slide-by-slide map

| Slide | Stable id (original identity) | Topic | How to teach it |
| --- | --- | --- | --- |
| 1 | `s1-001` | From LangGraph to Skills | Core |
| 2 | `s1-004` | Same AI, two outcomes | Core |
| 3 | `s1-005` | What we'll build: the Homework Helper | Core |
| 4 | `s1-002` | Today's route | Core |
| 5 | `s1-006` | Stop 1: How AI gets things done | Core |
| 6 | `s1-007` | An LLM is a "continuation machine" | Core |
| 7 | `s1-008` | LLMs have no memory: your program supplies the conversation | Core |
| 8 | `s1-009` | Tokens and the context window | Core |
| 9 | `s1-011` | Prompts and system prompts | Core |
| 10 | `s1-012` | Models can't act, so how does an agent "do" things? | Core |
| 11 | `s1-013` | Tool calling: the model only "says" which tool it wants | Core |
| 12 | `s1-014` | Predict first: will the model ask to use a tool? | Core |
| 13 | `s1-new-tool-result` | Read the tool request, then call the model again | Hands-on pause |
| 14 | `s1-015` | Agent = model + tools + loop | Core |
| 15 | `s1-016` | Workflow vs. agent: who decides the next step | Core |
| 16 | `s1-017` | Stop 2: Workflow 1-A | Core |
| 17 | `s1-018` | LangGraph: connecting functions with arrows | Core |
| 18 | `s1-019` | The Homework Helper's flow: four workstations | Core |
| 19 | `s1-003` | Tell them apart: valid syntax, runs, correct answer | Core |
| 20 | `s1-020` | Component 1: State, the order slip that travels along | Core |
| 21 | `s1-021` | Component 2: Node, one workstation | Core |
| 22 | `s1-023` | Component 3: Edge, the arrows between workstations | Core |
| 23 | `s1-024` | One table for the three components | Core |
| 24 | `s1-025` | No AI yet: three homework samples, guess then run | Core |
| 25 | `s1-026` | Data flow: watch the order slip fill in | Core |
| 26 | `s1-027` | Putting AI into one node | Core |
| 27 | `s1-new-format-stop` | The flow ended. Did the feedback pass? | Hands-on pause |
| 28 | `s1-028` | Back to the helper's flow: all three design patterns | Core |
| 29 | `s1-029` | 10-minute break | Core |
| 30 | `s1-030` | Stop 3: Agent 1-B | Core |
| 31 | `s1-031` | A different approach: no flow diagram, just a toolbox | Core |
| 32 | `s1-032` | Try the tools first, then hand them to the agent | Core |
| 33 | `s1-034` | What a tool interface tells the model | Core |
| 34 | `s1-033` | An agent in one line: create_agent | Core |
| 35 | `s1-037` | Reading an agent's execution trace | Core |
| 36 | `s1-038` | Same homework, three runs: same order? | Core |
| 37 | `s1-039` | If a tool keeps failing, will the agent stop? | Core |
| 38 | `s1-new-recursion-limit` | Set a limit, then work out why it stopped | Hands-on pause |
| 39 | `s1-035` | Where tools come from: your own functions vs. MCP sockets | Instructor demo |
| 40 | `s1-040` | Stop 4: Flow control and AI judgment | Core |
| 41 | `s1-041` | The math of ten checkpoints | Core |
| 42 | `s1-042` | Combining workflow and agent: an agent inside a node | Core |
| 43 | `s1-043` | Worksheet: flow control or AI judgment? | Core |
| 44 | `s1-044` | Three takeaways and homework | Core |
| 45 | `s1-010` | Optional appendix: usage fields in the returned object | Optional reading after class |
| 46 | `s1-022` | Optional appendix: how messages in State are merged | Optional reading after class |
| 47 | `s1-036` | Optional appendix: the core model-and-tool loop | Optional reading after class |
| 48 | `s1-045` | References | Core |

## Notebook mapping

- **1-0**: Part 1 history (slides 6–7), Part 2 returned content (slide 8; usage fields are optional reading in appendix slide 45), Part 3 tool requests (slides 11–12), Part 4 a single tool round (slide 13) → loop cell (slide 14), Part 5 workflow vs. agent comparison (slide 15).
- **1-A**: Part 1 flow and the three components (slides 17–23), Part 2 data flow with fixed feedback (slides 24–25), Part 3 model call (slide 26) → form experiment and stop reason (slide 27) → review of design patterns (slide 28). The message merge rule is in appendix slide 46, optional after class.
- **1-B**: Part 1 local tools (slides 31–32), Part 2 tool descriptions (slide 33), Part 3 build the agent and read the trace (slides 34–35), Part 4 repeated comparison (slide 36), Part 5 first observe the failing loop (slide 37) → set the limit and run (slide 38), Part 6 instructor's MCP demo (slide 39), Part 7 optional core loop (appendix slide 47).
- **Wrap-up and integration**: combining workflow and agent is on slide 42, the worksheet on slide 43, and the homework instructions on slide 44.

## Why the structure was adjusted

The deck grew from 45 to 48 slides. The new slides are hands-on pauses for existing notebook content. No experiment or lecture time was added, so the total stays at 120 minutes.

1. For tool calling, predict first, then run and read name/args. Only after one tool result has been returned do we introduce the loop. The new slide continues from the first cell of 1-0 Part 4, so the deck does not jump straight from the comic to the agent.
2. After the AI feedback node, students work the form first and read the result through format_ok and the stop reason, then review the flow design patterns. Stopping and passing are essential ideas and cannot live only in a footnote.
3. For the failing loop, observe and predict first, then introduce recursion_limit and run the notebook that already has a limit. The original single slide crammed in the trace, the exception, the setup, and the conclusion; after the split, each slide has one main learning task.

Timing for the speaker: the single tool round takes about 2 minutes, reading the format result about 90 seconds, and the failing loop plus the limit about 3 minutes in total. All of it comes out of the time already allotted to each part's experiment. Wait until students have finished the specified output before moving on; do not speed up the hands-on work because of the extra slides.

## Teaching and acceptance points

- Explain the project's output contract first: a syntax error is explained directly and the flow ends, with no format check. When syntax passes, feedback is generated, and then the "Strengths:" and "Improvements:" parts and the character limit are checked. Passing the format does not mean the content is correct.
- `retries` stays as an internal field name. It actually counts the feedbacks generated so far, including the first. The student form and the handouts call it "maximum generations (including the first)".
- Keep these apart: the run finished, the limit was reached, the format passed, and the assignment's answer is correct. Check the final `format_ok` and the stop reason.
- Do not bring a reducer into State, Node, and Edge. First understand updating a single field; message merging comes later in the appendix.
- `pretty_trace` shows only model messages, tool requests, and tool results. It is not the model's hidden thinking.
- `recursion_limit` limits the number of graph steps, not the number of tool calls. The model stopping by itself and hitting the limit are both valid observations.
- MCP is an interface for connecting external programs or services. The program chooses which tools to hand to the model, and authentication and authorization are set up separately. A Skill does not automatically remove tool definitions.
- Homework acceptance: one screenshot of the 1-A State history and one of the 1-B tool execution log, plus one sentence that compares how much to trust each result, based on evidence.

- Stop 4 is always called "Flow control and AI judgment". The dual-core diagram only draws the syntax-OK path; the syntax-error branch is explained directly and ends. The worksheet items about tool execution and tone are discussed according to the requirements; they should not be treated as the only classification for every system.
