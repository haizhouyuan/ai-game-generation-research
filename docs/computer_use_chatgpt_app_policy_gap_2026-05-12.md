# Computer Use and ChatGPT App Policy Gap

Date: 2026-05-12

Status: user-supplied research note, validated against this local session's observed behavior.

## Summary

`com.openai.chat` appears to be blocked by Codex Computer Use at the target-app safety policy layer, not by macOS Screen Recording, Accessibility, network, or ordinary per-app approval failure.

Observed local error:

```text
Computer Use is not allowed to use the app 'com.openai.chat' for safety reasons.
```

This is consistent with a hard deny in the Computer Use MCP/native helper path. The app can still be listed by `list_apps`, but direct `get_app_state(app="com.openai.chat")` is refused.

## Likely Layering

The effective stack should be treated as:

1. macOS TCC permissions
   - Screen Recording
   - Accessibility
   - Apple Events
2. Codex app approvals
   - which apps the user allows Computer Use to operate
3. Codex sandbox and approval policy
   - files, shell, network, workspace writes, risky operations
4. Computer Use target-app safety policy
   - bundle-id or app-class deny rules

The ChatGPT macOS app case most likely hits layer 4.

## Why ChatGPT App Is Sensitive

The likely rationale is preventing Codex from controlling another logged-in AI client and thereby bypassing Codex's own approval, sandbox, logging, and safety boundaries.

Risks include:

- agent-to-agent recursion or loops;
- indirect bypass of Codex approvals and sandbox;
- exposure of private chats, memory, connectors, browser/tool state, and account context;
- cross-contamination where another model's output becomes implicit instruction to Codex;
- harder-to-audit execution chains.

This is analogous in spirit to restrictions on automating Codex itself or terminal-like apps that could bypass Codex security policies.

## Observed Coverage Gap

The local session showed a subtle but important gap:

- Direct target operation on `com.openai.chat` is blocked.
- System UI and menu-bar access can still reveal some ChatGPT App state, such as the `Chats` menu item `Codex APP Dual Agent`.
- Chrome can open the same `chatgpt.com/c/...` conversation and expose the full page via normal browser accessibility/DevTools paths.

This suggests the current policy may be target-app based rather than full information-flow based. In other words, the helper refuses direct operations against `com.openai.chat`, but some text originating from ChatGPT may remain visible through other surfaces.

This should not be treated as a stable or endorsed integration path. It is better understood as a policy coverage inconsistency.

## Local Extraction Note

For the `Codex APP Dual Agent` conversation, direct ChatGPT App access was blocked. The final full transcript was extracted from the authenticated ChatGPT web page in Chrome:

```text
https://chatgpt.com/c/6a028cb5-08f8-83ec-a045-c78a7a9f6fa9
```

Saved artifacts:

- `external/chatgpt_app_extracts/codex_app_dual_agent_20260512/full_session_transcript.md`
- `external/chatgpt_app_extracts/codex_app_dual_agent_20260512/full_session_raw_innertext.txt`
- `external/chatgpt_app_extracts/codex_app_dual_agent_20260512/README.md`

## Reporting Shape

If reporting upstream, the strongest framing is not "help me bypass the block"; it is:

Expected:

When `com.openai.chat` is blocked by target-app safety policy, Computer Use should not expose the same app's sensitive chat/session state through system menu bar, global Accessibility elements, window titles, recent-items menus, or other indirect surfaces.

Actual:

Direct target app access is blocked, but some ChatGPT session labels or content may remain readable through system UI or browser surfaces.

Minimal reproduction:

1. Open ChatGPT macOS App.
2. Create a non-sensitive chat titled `CUA-Test-123`.
3. In Codex, enable Computer Use.
4. Attempt direct `get_app_state` or operation against ChatGPT App.
5. Observe the safety error for `com.openai.chat`.
6. Inspect whether system UI/menu bar/window title/recent chat surfaces expose `CUA-Test-123`.

Recommended metadata to include:

- Codex app version;
- Computer Use plugin version;
- macOS version;
- ChatGPT app version;
- bundle id: `com.openai.chat`;
- exact error string;
- screenshots or redacted logs showing direct block vs indirect exposure.

## Practical Guidance

Do not rely on ChatGPT App direct Computer Use as part of the game-generation toolchain or deep-research skill.

Preferred paths:

- use official APIs and documented connectors where available;
- use browser/web extraction only when the user explicitly provides the URL/session and the data is needed;
- store extracted material as evidence with hashes and provenance;
- avoid treating another ChatGPT conversation as live instructions unless the user explicitly asks to import it.

