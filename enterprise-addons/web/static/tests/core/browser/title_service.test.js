import { beforeEach, describe, expect, test } from "@odoo/hoot";
import { getService, makeMockEnv } from "@web/../tests/web_test_helpers";

describe.current.tags("headless");

let titleService;

beforeEach(async () => {
    await makeMockEnv();
    titleService = getService("title");
});

test("simple title", () => {
    titleService.setParts({ one: "MyErp" });
    expect(titleService.current).toBe("MyErp");
});

test("add title part", () => {
    titleService.setParts({ one: "MyErp", two: null });
    expect(titleService.current).toBe("MyErp");
    titleService.setParts({ three: "Import" });
    expect(titleService.current).toBe("MyErp - Import");
});

test("modify title part", () => {
    titleService.setParts({ one: "MyErp" });
    expect(titleService.current).toBe("MyErp");
    titleService.setParts({ one: "Zopenerp" });
    expect(titleService.current).toBe("Zopenerp");
});

test("delete title part", () => {
    titleService.setParts({ one: "MyErp" });
    expect(titleService.current).toBe("MyErp");
    titleService.setParts({ one: null });
    expect(titleService.current).toBe("Erp");
});

test("all at once", () => {
    titleService.setParts({ one: "MyErp", two: "Import" });
    expect(titleService.current).toBe("MyErp - Import");
    titleService.setParts({ one: "Zopenerp", two: null, three: "Sauron" });
    expect(titleService.current).toBe("Zopenerp - Sauron");
});

test("get title parts", () => {
    expect(titleService.current).toBe("");
    titleService.setParts({ one: "MyErp", two: "Import" });
    expect(titleService.current).toBe("MyErp - Import");
    const parts = titleService.getParts();
    expect(parts).toEqual({ one: "MyErp", two: "Import" });
    parts.action = "Export";
    expect(titleService.current).toBe("MyErp - Import"); // parts is a copy!
});
