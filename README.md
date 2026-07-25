# aurelia-base
# Agent Design Lab — Hotel Guest Issue Triage

## The company

A mid-size hotel chain. Guests text or call the front desk when something's
wrong in their room: a leak, broken AC, a dead electronic lock, a strange
smell. Someone — or something — has to decide what happens next.

## The problem

The naive version of this is "match the keyword, send the technician." But
the real decision is more layered than that:

- Is the guest **VIP**, or have they already reported **multiple issues
  this stay**? That changes the tolerance for "just send maintenance and
  hope."
- Is the right call actually **dispatching a technician**, or should the
  guest be **reassigned to a different room** — which only makes sense if
  a room is actually free?
- Anything the system can't confidently resolve should be **escalated to
  a human manager**, not guessed at.

That middle step — checking guest history, then *conditionally* checking
room availability, then deciding — is why this isn't a simple script: the
right next action depends on what an earlier lookup returned, not on the
raw message text alone. That dependency is also why a one-shot classifier
can only get partway there (see `routing/`'s own code comments, which
admit as much).

## The four folders

| Folder | Architecture | Model calls per request |
|---|---|---|
| `reactive/` | Rule-based keyword matching, no model call | 0 |
| `unconstrained_react/` | Free-form ReAct loop, model picks its own tools and stopping point | variable, unbounded |
| `routing/` | One classification call → fixed downstream code | 1 |
| `constrained_react/` | Schema-validated ReAct loop, allow-listed tools, `MAX_STEPS = 6`, forced exit | up to `MAX_STEPS` |

Each folder is runnable on its own and has its own README with exact setup
steps. All four read the same `shared_inputs.json` at the repo root, so
results are apples-to-apples.

**Model/provider:** Groq (`llama-3.3-70b-versatile' ) for every agent that makes
a model call, to keep the model itself constant across architectures — the
only thing that should vary between folders is the architecture.

## Comparison table

> **Note:** the numbers below for `reactive/` and `routing/` come from
> reading that code directly. The `constrained_react/` numbers need an
> actual run with a live `GROQ_API_KEY` to fill in — I can't call the
> Groq API from here to generate them myself. Whoever built
> `unconstrained_react/` should fill that row in the same pass, with the
> **same four test inputs**, so the comparison stays fair.

| | Calls per request | Rough cost / token usage | Latency | What broke on the tricky input (`id: 4`, "strange smell, no visible hazard") |
|---|---|---|---|---|
| Reactive | 0 | $0 | ~instant | Falls straight to the fallback rule — no leak/AC/lock keyword matches, so it escalates blind, with zero reasoning about whether that's actually right. |
| Unconstrained ReAct | *(fill in)* | *(fill in)* | *(fill in)* | *(fill in — did it call extra tools it didn't need, loop unexpectedly, or handle this fine?)* |
| Routing | 1 | 1 short prompt + 1-word completion | fast (single round trip) | Classifies as `HAZARD_UNKNOWN` correctly, but the routing code itself admits it can't check VIP status or room availability, so it can never actually decide *reassign vs. escalate* — it can only ever fall back to the human. |
| Constrained ReAct | ≤ 6 | *(fill in after a run)* | *(fill in — will be higher than routing due to multiple round trips)* | *(fill in — worth noting whether it correctly recognizes "no hazard" as low-severity and still escalates appropriately, vs. guessing a room reassignment it shouldn't)* |

## Guardrails followed

- No API key is committed anywhere in this repo. Each agent reads its key
  from a `.env` file (see `.env.example`), and `.env` is in `.gitignore`.
- The same `shared_inputs.json` is used by every architecture.
- The core decision (dispatch vs. reassign vs. escalate) genuinely depends
  on a prior tool result (guest history, then conditionally room
  availability) — not just a relabeled routing problem.
