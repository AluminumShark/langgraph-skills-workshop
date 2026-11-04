from nbbuild import RB, badge, code, ending, md, project_intro, setup, writefile

NAME = "2-A_skills"
BEGINNER_REQUEST = "Take a look for a beginner handing in homework for the first time"
MIDTERM_REQUEST = "Midterm exam, official grading: please review strictly"
REQUEST_OPTIONS = f'["{BEGINNER_REQUEST}", "{MIDTERM_REQUEST}"] {{allow-input: true}}'
TWO_HANDBOOKS = '["friendly-feedback", "strict-review"]'


def _feedback_cell(title: str, mode: str):
    REQUEST_FORM = (
        f'review_request = "{BEGINNER_REQUEST}"  #@param {REQUEST_OPTIONS}'
        if mode == "pick"
        else f'#@markdown This experiment always uses the request "{BEGINNER_REQUEST}", so you do not need to change it.'
    )
    return code(f"""
    #@title ▶ Experiment {title}
    {REQUEST_FORM}
    {{PREAMBLE}}
    from langchain_core.messages import HumanMessage, SystemMessage
    import skill_loader
    experiment_mode = {mode!r}
    if experiment_mode != "pick":
        review_request = "{BEGINNER_REQUEST}"
    cards = skill_loader.list_cards({TWO_HANDBOOKS})
    if len(cards) != 2:
        raise SystemExit("Run the two handbook text cells that come before this experiment first, or use Restore defaults in this part.")
    print("Request this time:", review_request)
    print("Fixed homework: Variable typo")
    for c in cards:
        print(f"Card {{c['name']}}: {{c['description']}}")
    if experiment_mode == "fixed":
        card = next(c for c in cards if c["name"] == "friendly-feedback")
        print("In this experiment the code fixes the handbook; the model does not pick again.")
    else:
        card = skill_loader.pick_handbook(model, review_request, cards)
    handbook_body = skill_loader.read_body(card)
    print("Handbook picked:", card["name"])
    print("Rules read this time:\\n" + handbook_body)
    feedback = model.invoke([SystemMessage(handbook_body), HumanMessage(
        f"Please review this homework:\\n```python\\n{{load_homework('Variable typo')}}\\n```"
    )]).text
    print("Feedback:\\n" + feedback)
    if experiment_mode == "fixed":
        new_rule_loaded = "Next step: please test again" in handbook_body
        print("Does the handbook loaded this time contain the new closing rule:", new_rule_loaded)
        if new_rule_loaded:
            print("Does the feedback end with the specified sentence:", feedback.strip().rstrip(".!").endswith("Next step: please test again"))
        else:
            print("This is still the original-rules baseline; we have not yet tested whether the model follows the new rule. Edit and run B's handbook text cell, then rerun this cell to compare.")
    record(f"2-A experiment {{experiment_mode}}", {{"request": review_request, "picked": card["name"], "body": handbook_body, "feedback": feedback}})
    """)


def cells():
    return [
        md(f"""
        # 2-A: A Skill is a work handbook for the AI

        {badge(NAME)}

        > 📍 **Matching slides**: Session 2 "Stop 1: Skill handbooks", slides **5-12**; Experiment C is optional after class, slide **42** (class time 0:08-0:28)
        """),
        project_intro("Write the tone and rules of the feedback into a handbook (a Skill) for the AI to read: change not one line of code, swap a handbook, and the style changes."),
        md("""
        ## What this notebook does

        The Homework Helper hands the "write the feedback" step to an AI. The most direct way to say what tone and rules the AI should follow is the **system prompt**:
        a piece of text placed first in every call to the AI that tells it "who you are and what to obey", for example "You are a Python homework helper; keep a gentle tone".

        In the earlier examples, that text lived inside the code. When a club officer says "be stricter for the midterm", you have to find that text and edit it, and many styles quickly become hard to maintain.
        Is there a way to **leave the code alone and swap only a sheet of paper**?

        Yes: a **Skill**. It is a folder with a text file `SKILL.md` that describes how to do some job, like a **work handbook** for a new colleague.
        The program gives the handbook to the AI, which writes feedback following its rules. Not one line of Python changes.

        This notebook introduces two terms: **Skill (handbook)** and **card (description)**.

        | Part | What you do | Matching slides |
        | --- | --- | --- |
        | Part 1 | Write two handbooks, "gentle and encouraging" and "strict review", and look at the cards on the shelf | 6-8 |
        | Part 2 | A: pick a handbook; B: add one rule (both required); C: swap the cards (optional after class) | A: 9-10; B: 11; C, optional after class: 42 |
        | Part 3 (optional reading after class) | Download an official Skill from Anthropic and take it apart: card, body, appendix | 12 |

        ## How to use it

        1. First use the menu at the top, "File → Save a copy in Drive", and work in your own copy. You will edit text cells here, and without a copy your changes are lost.
        2. Run **"0. Environment setup"**.
        3. What you edit here are the **SKILL.md text cells** (each experiment has its own) and the form fields. After editing a handbook cell, **run that cell again** so it is saved to a file.
        4. Every part: **🤔 write a prediction first → ▶ run → 👀 compare**. When you rerun, first make sure the environment is still there, then follow each experiment's setup steps.
        5. A reminder: "0. Environment setup" in this notebook does not include the handbooks. Rerunning it rewrites the shared support code but does not change the two handbooks. Each `%%writefile` text cell and "Restore defaults" overwrites its file, so keep any edits you want before running them. After the runtime is rebuilt, rerun the setup, Part 1, and the setup cells of your current experiment, in that order.
        """),
        setup(NAME, support=["skill_loader.py"]),
        md("""
        ---
        ## Part 1: What a handbook looks like, and why the shelf shows only cards

        > 📍 **Matching slides**: slide 6 "Last week's leftover problem: feedback style hard-coded", slide 7 "What do you give a new colleague on day one?", slide 8 "What a handbook looks like"

        The introduction explained why we need handbooks. This part looks at what one looks like. A `SKILL.md` has two parts:

        ```markdown
        ---
        name: friendly-feedback                      ← card: this course reads only these two fields
        description: Feedback on homework for Python beginners...   ← (what it does, when to use it)
        ---

        # Gentle feedback rules                       ← handbook body: how to do the job
        1. Start with one thing done well
        ```

        - **Card**: between the two `---` lines. `name` is the handbook's name (lowercase letters, digits, and hyphens only; at most 64 characters). `description` says **what the handbook does and when to use it**.
        - **Handbook body**: below the card; steps that a person can also read and understand.

        The next two cells are the two handbooks, "gentle and encouraging" and "strict review". Just run them for now. **In Part 2, edit the text cell named under each experiment**; it writes back to the same handbook file.
        The third cell writes out `skill_loader.py`, which reads cards and picks a handbook (you do not edit it).

        ### 🤔 Predictions
        1. In friendly-feedback, which sentence says "when to use it"? Which lines say "how to do it"?
        2. When the AI picks a handbook, can it see the handbook's "body"? Or only the card?
        3. (Optional) Which takes up more of the desk (tokens): the card or the body?
           A **token** is the unit the AI uses to read text (characters and tokens do not map one to one; it depends on the model and the content).
           There is a limit to how many tokens the AI can read at once. Think of it as a **desk** (the proper name is the context window): put too much on it and things will not fit.
        """),
        writefile("skills/friendly-feedback/SKILL.md"),
        writefile("skills/strict-review/SKILL.md"),
        writefile("skill_loader.py"),
        code(f"""
        #@title ▶ Run: see which cards are on the shelf
        {{PREAMBLE}}
        import skill_loader

        cards = skill_loader.list_cards({TWO_HANDBOOKS})
        card_total = body_total = 0
        for c in cards:
            body = skill_loader.read_body(c)
            card_tokens = estimate_tokens(c["name"] + c["description"])
            body_tokens = estimate_tokens(body)
            card_total += card_tokens
            body_total += body_tokens
            print(f"📕 name: {{c['name']}}")
            print(f"   description: {{c['description']}}")
            print(f"   The card is about {{card_tokens}} tokens; opening the body adds about {{body_tokens}} tokens\\n")

        print(f"When the AI picks a book, only {{len(cards)}} cards are on the desk: about {{card_total}} tokens")
        print(f"If every body were spread out on the desk: about {{card_total + body_total}} tokens")
        print(f"Suppose 50 handbooks, each about as long as these two: cards only is about {{card_total * 25}} tokens; everything open is about {{(card_total + body_total) * 25}} tokens (estimate)")
        record("2-A Part 1: cards on the shelf", {{c["name"]: c["description"] for c in cards}})
        """),
        md("""
        ### 👀 What did you see

        - Each handbook's card is just a sentence or two; you see the full rules only when you open it.
        - This program lets the AI **look only at the cards** when it picks a book, and puts the body on the desk only after one is picked. With two handbooks the difference is small, but with 50,
          spreading them all out raises context use a lot, while cards only is far lighter. This is **progressive disclosure**: card → body → appendix, opened only when needed.
        - You did not change a single line of Python. You wrote two text files, and now there are two "feedback styles" to choose from.
        """),
        md("""
        ---
        ## Part 2: Three experiments (A and B required; C optional after class), change one thing at a time

        > 📍 **Matching slides**: slides 9-10 (pick a handbook first), 11 (fix the handbook and add one rule); C optional after class, 42

        | Experiment | Held fixed | The only change | Where to look |
        | --- | --- | --- | --- |
        | A: pick a handbook | Same homework, two default handbooks | The review request | Name of the picked handbook |
        | B: change the method | Same homework, beginner request, gentle handbook fixed | One extra closing rule in the handbook | Whether the feedback has the specified closing sentence |
        | C: change the selection condition | Same homework, beginner request, original bodies | The two descriptions | Which one is picked, and which rules are read |

        Each run lets you observe only one difference. **Do both requests in A first, then B; C is a further experiment for after class.**
        **Running every cell once usually gives only each experiment's baseline. To finish a comparison you must change one condition as described below and run again.**
        "Restore defaults" below resets only the two handbook files in Colab. It does not change notebook text cells; download first if you want to keep your edits.
        """),
        code(f"""
        #@title ↺ Restore the default content of the two handbooks (run this when you start the experiments over)
        {{PREAMBLE}}
        default_handbook = { {name: (RB / "skills" / name / "SKILL.md").read_text(encoding="utf-8") for name in ["friendly-feedback", "strict-review"]}!r}
        for name, text in default_handbook.items():
            (BASE / "skills" / name / "SKILL.md").write_text(text, encoding="utf-8")
        print("✅ Both handbooks restored. Experiment A can run directly; for Experiment B, edit the dedicated text cell below.")
        """),
        md("""
        ### Experiment A: change only the request, observe the choice (required)

        Run "Restore defaults" above first, then run with the "beginner" request; the second time, change only the request to the "midterm" one. Keep both handbooks at their defaults. If you come back to redo A after B or C, restore defaults first too.
        **Guess first: which handbook fits the request better?** After running, find "Handbook picked" first, then read the feedback.
        **Done when: you keep one output each for "beginner" and "midterm", and confirm the two printed requests differ while the two cards are unchanged.** Rerunning the same request does not complete this comparison; if the same book is picked both times, you can discuss that honestly.
        """),
        _feedback_cell("A: change only the request, let the model pick a handbook", "pick"),
        md("""
        ### 👀 What did you see

        Note which handbook was picked each time. The model chooses from the cards, and the result is not guaranteed to be the same every time. If it differs from your prediction, first compare the two cards it saw.
        **Tool descriptions and Skill cards do the same job: they say what something is for and when to use it.**

        ### Experiment B: add just one rule, observe the feedback (required)

        > Matches slide 11. When you finish this experiment, stop and compare the results; Experiment C is optional after class.

        The cell below is B's gentle handbook text. It overwrites the file at the same path. The first time, run it unchanged and then run the feedback cell to keep one baseline. To redo it, delete rule 5 and restore the original four rules first, then take the baseline.
        Next, below rule 4 add one rule: **5. End the feedback with "Next step: please test again"**. Leave the other four rules alone.
        Run the handbook cell to save it, then run the feedback cell.

        **Guess first: with the handbook choice unchanged, what will the feedback gain?**
        This experiment fixes the "beginner" request and has the code fix the gentle handbook, which temporarily rules out the effect of picking the wrong handbook.
        **Done when: you keep one output with the original rules and one with the new rule; the new-rule output must first show "Does the handbook loaded this time contain the new closing rule: True".**
        If that line still says False, you can only say the file has not loaded the new rule yet; you cannot say the model ignored it. Rerun the edited handbook text cell first.
        """),
        writefile("skills/friendly-feedback/SKILL.md"),
        _feedback_cell("B: gentle handbook fixed, compare before and after the edit", "fixed"),
        md("""
        ### 👀 What did you see

        First confirm that the printed handbook body really contains the new rule, then check the feedback. If the file did not change, run the text cell you just edited first.
        If the body has the new rule but the feedback lacks the specified sentence, write down "not followed this time"; do not rerun until it complies.
        Standard for done: say which rule you added, and explain the result using the outputs from before and after the edit.

        ### Experiment C: restore the bodies, swap only the cards (optional after class)

        The two cells below each carry a default handbook text. Running them overwrites the same file paths as B and clears B's closing sentence. The first time, run the two cells and the feedback cell unchanged to get a baseline. If you have already swapped the descriptions in these two cells, swap them back before redoing it, or run "Restore defaults" for a baseline; do not rerun the already swapped cells as if they were the defaults.
        Then **swap only the two description values**, leaving name and body alone; rerun both cells to save, then run the feedback cell.
        The request stays "beginner". **Guess first: which one is picked this time? Do the picked card and its body match?**
        **Done when: you keep one output from before the swap and one from after, and confirm the two descriptions are swapped while the request and bodies are unchanged.** Simply rerunning the two unchanged cells is still the baseline, not the after-swap result. Always judge from the cards and body that the feedback cell actually printed.
        """),
        writefile("skills/friendly-feedback/SKILL.md"),
        writefile("skills/strict-review/SKILL.md"),
        _feedback_cell("C: beginner request fixed, compare only the cards", "compare_cards"),
        md("""
        ### 👀 What did you see

        Compare five pieces of evidence: the request, the two cards, the picked name, the body that was read, and the feedback.
        After the swap, the model may pick the handbook whose body is stricter; if it does not switch, record that honestly and discuss the clues in the names and descriptions.
        Here we implemented "pick by card, then read the body" in code; not every agent automatically reads any folder.
        When you finish, you can run "Restore defaults" at the top of this part. The next notebook prepares its own instructor-default files and does not import your edits automatically.
        """),
        md("""
        ---
        ## Part 3 (optional reading after class): take apart an official Skill

        > 📍 **Matching slides**: slide 12 "Handbook attachments: scripts and reference material"

        In the first two parts, each handbook was a single `SKILL.md`. Real-world handbooks can carry other files too:

        ```
        some-handbook/
        ├── SKILL.md          ← the handbook itself (card + body)
        ├── scripts/          ← small programs that can be run (2-B uses them next)
        └── references/ or examples/  ← long reference material, opened only when needed
        ```

        The next cell downloads a real Skill from Anthropic's official skills repo: `internal-comms` (a handbook for writing internal company announcements, Apache-2.0 licensed),
        and takes it apart into three layers for you. If there is no network, it takes apart our own `friendly-feedback` instead.

        ### 🤔 Predictions
        1. Does the official handbook's description say **when to use it**?
        2. The files in the `examples/` folder it ships: when does the AI open them?
        """),
        code("""
        #@title ▶ Run: download an official Skill and split it into card, body, and appendix
        {PREAMBLE}
        import json
        import urllib.request

        url = "https://raw.githubusercontent.com/anthropics/skills/main/skills/internal-comms/SKILL.md"
        appendix_url = "https://api.github.com/repos/anthropics/skills/contents/skills/internal-comms/examples"
        fallback_appendix = ["3p-updates.md", "company-newsletter.md", "faq-answers.md", "general-comms.md"]

        try:
            with urllib.request.urlopen(url, timeout=10) as r:
                text = r.read().decode("utf-8")
            source = "Anthropic's official skills repo: skills/internal-comms (Apache-2.0)"
            try:
                with urllib.request.urlopen(appendix_url, timeout=10) as r:
                    appendix = [f["name"] for f in json.load(r)]
            except Exception:
                appendix = fallback_appendix
        except Exception as e:
            print(f"⚠️ Cannot reach GitHub ({type(e).__name__}); taking apart our own friendly-feedback instead\\n")
            text = (BASE / "skills" / "friendly-feedback" / "SKILL.md").read_text(encoding="utf-8")
            source = "review-bot/skills/friendly-feedback"
            appendix = []

        _, header, body = text.split("---", 2)
        card = {}
        for line in header.strip().splitlines():
            key, _, value = line.partition(":")
            card[key.strip()] = value.strip()

        print(f"Source: {source}\\n")
        print("① Card (given to the model when it picks)")
        for key, value in card.items():
            print(f"   {key}: {value}")
        print(f"   → about {estimate_tokens(header)} tokens\\n")

        print("② Body (opened only when picked), first 12 lines:")
        for line in body.strip().splitlines()[:12]:
            print(f"   {line}")
        print(f"   ... (body has {len(body.strip().splitlines())} lines, about {estimate_tokens(body)} tokens)\\n")

        print("③ Appendix (opened only when the body says to open it):")
        for name in appendix:
            mentioned = "(mentioned in the body)" if name in body else ""
            print(f"   examples/{name} {mentioned}")
        if not appendix:
            print("   (this handbook has no appendix)")
        record("2-A Part 3: taking apart a Skill", {"source": source, "card": card, "body_lines": len(body.strip().splitlines()), "appendix": appendix})
        """),
        md("""
        ### 👀 What did you see

        - **Card**: the official handbook's description is long, and it clearly says "when to use this handbook" (status reports, company newsletters, FAQs...).
          The clearer it is, the better the AI knows when to open it.
        - **Body**: the steps read like an SOP for a new colleague: first decide which kind of announcement it is → open the matching example file → write in the example's format.
        - **Appendix**: this handbook's `examples/` offers different examples, and the body says "which case opens which one". This cell only lists the file names; it did not read the example contents or have the AI do an announcement task. Actually reading them also needs tool support.
          This is the **progressive disclosure** of three layers: the card when picking, the body once picked, the appendix only when needed. Length and loading method vary by handbook and tool.
        - Skill is an open standard: different supporting tools can share this handbook structure; where files go and how they are discovered and run still depends on the tool.
        - The next notebook, **2-B**, uses a handbook's `scripts/`: write a check that must be identical every time as a small program, and tell the AI to run it.
        """),
        *ending(),
    ]
