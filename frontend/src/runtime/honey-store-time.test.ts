import { beforeEach, describe, expect, it } from "vitest";
import { useHoneyStore } from "./honey-store";
import { initialRunState } from "./honey-events";

describe("live message timestamps", () => {
  beforeEach(() => useHoneyStore.setState({ messages: [], run: initialRunState, replyTimestamp: undefined }));
  it("keeps server completion time when committing a reply on the next turn", () => {
    const store = useHoneyStore.getState;
    store().beginTurn("hello");
    store().applyRunEvent({ name: "run.started", payload: { ts: 1792944600 } });
    expect(store().messages[0].timestamp).toBe(1792944600);
    store().applyRunEvent({ name: "assistant.completed", payload: { content: "hi", ts: 1792944603 } });
    store().beginTurn("again");
    const reply = store().messages.find((message) => message.role === "assistant");
    expect(reply?.timestamp).toBe(1792944603);
    expect(store().replyTimestamp).toBeUndefined();
  });
});
