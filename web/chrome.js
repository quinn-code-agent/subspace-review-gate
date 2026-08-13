// Client chrome boundary. Implementation will serialize only portable Subspace Annotations
// and call the existing feedback-only Relay endpoints; no Human Review protocol is used here.
export const chromeContract = Object.freeze({
  layout: ["stage", "handle", "rail", "rail-scroll", "compose", "cards", "rail-foot"],
  annotation: "amber-selection-and-highlight",
  transport: "subspace-annotation-feedback-result",
});
