# Relay Web Chrome Migration

This directory deliberately separates the Human Review-compatible browser chrome from the Relay transport.

- `chrome.html` provides the Human Review layout contract: stage, hide handle, cream feedback rail, rail compose card, comment cards, and footer submission area.
- `chrome.css` ports the Human Review visual token system and layout primitives.
- `chrome.js` will own client interaction only: identity cover, anchored selection state, annotation rendering, rail interaction, and fetch calls to the existing `/api/submit` and `/api/shared-feedback` endpoints.

The Python `bin/subspace-relay-web` remains the only owner of package verification, owner-side shared projection, reviewer state isolation, and feedback-only Relay submission. No Human Review API, token, feedback batch, poll, or acknowledgement protocol belongs in these files.
