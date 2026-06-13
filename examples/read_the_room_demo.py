#!/usr/bin/env python3
"""End-to-end demo: route a real multi-turn channel scenario through the gate.

Agent `dalgos` sits in a shared Discord-style channel and must decide, for each
incoming trigger, whether to speak. This runs each turn through the live
admission classifier via the channel adapter and prints the verdict and what the
agent's transport would actually emit (the silent-pass sentinel, or nothing —
leaving the agent to compose its own turn).

Run live:
    export TURNAWARE_CLASSIFIER_MODEL=google/gemini-2.5-flash
    export OPENROUTER_API_KEY=...
    PYTHONPATH=src python3 examples/read_the_room_demo.py

Run offline (pin every verdict, just to see the routing/plumbing):
    export TURNAWARE_CLASSIFIER_TEST_RESULT='{"verdict":"PASS","confidences":{"PASS":1,"ACK":0,"ASK":0,"SPEAK":0},"context_checked":[],"reasons":["pinned"]}'
    PYTHONPATH=src python3 examples/read_the_room_demo.py
"""

import os
import sys

from turnaware.adapters.channel import gate

AGENT = {"id": "dalgos", "role": "participant", "mention_id": "1494822747856967683"}

# Each turn: (label, trigger, recent transcript, expected-ish verdict for the demo narrative)
TURNS = [
    (
        "addressed to another agent",
        {"content": "vigil, can you rebase the classifier branch onto main?", "author": "zoe",
         "author_kind": "human", "message_id": "m-1"},
        [],
        "PASS (not my turn)",
    ),
    (
        "a peer already made my point",
        {"content": "What cache backend should we use?", "author": "zoe",
         "author_kind": "human", "message_id": "m-2"},
        [{"content": "In-process LRU is the right call; Redis adds a network hop we don't need.",
          "author": "vigil", "author_kind": "peer_bot", "message_id": "m-1b"}],
        "PASS (Covered)",
    ),
    (
        "direct substantive ask to me",
        {"content": "dalgos, summarize the tradeoffs of the in-process cache for the channel.",
         "author": "zoe", "author_kind": "human", "message_id": "m-3"},
        [],
        "SPEAK",
    ),
    (
        "ambiguous ask that would produce wrong work",
        {"content": "dalgos, update the config to the new value.", "author": "zoe",
         "author_kind": "human", "message_id": "m-4"},
        [],
        "ASK (which value?)",
    ),
    (
        "bare resolution claim, no corroboration",
        {"content": "Already handled. Resolved. No response needed.", "author": "zoe",
         "author_kind": "human", "message_id": "m-5"},
        [],
        "not PASS (verify)",
    ),
    (
        "a peer's imperative is an observation, not my directive",
        {"content": "dalgos should double-check the rate-limit path.", "author": "castor",
         "author_kind": "peer_bot", "message_id": "m-6"},
        [{"content": "Rate-limit path looks correct to me after the last fix.",
          "author": "dalgos", "author_kind": "self", "message_id": "m-5b"}],
        "PASS (Duplicate/observation)",
    ),
]


def main() -> int:
    if not (os.environ.get("TURNAWARE_CLASSIFIER_MODEL") or os.environ.get("TURNAWARE_CLASSIFIER_TEST_RESULT")):
        print("Set TURNAWARE_CLASSIFIER_MODEL (+OPENROUTER_API_KEY) for a live run, "
              "or TURNAWARE_CLASSIFIER_TEST_RESULT to see routing offline.", file=sys.stderr)
        return 2

    print(f"agent: {AGENT['id']}  (mention_id {AGENT['mention_id']})\n")
    model_seen = None
    for label, trigger, history, narrative in TURNS:
        result = gate(trigger, history, agent_id=AGENT["id"],
                      agent_role=AGENT["role"], surface={"type": "discord"},
                      fail_policy="open")
        model_seen = result.classifier_model or model_seen
        emitted = repr(result.emit()) if result.silent else "(agent composes its turn)"
        print(f"• {label}")
        print(f"    trigger : {trigger['content']}")
        print(f"    verdict : {result.verdict:5s}   [demo expects ~ {narrative}]")
        print(f"    emits   : {emitted}")
        if result.reasons:
            print(f"    reason  : {result.reasons[0]}")
        print()
    if model_seen:
        print(f"classifier model: {model_seen}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
