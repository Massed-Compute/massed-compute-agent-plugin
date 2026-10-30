/** @jest-environment node */
/*
 * Run with the authorized vm-marketplace checkout's Jest configuration.
 * Every account credential is synthetic; database and write handlers are mocked.
 * This is a local authorization proof, never a production MCP test.
 */
process.env.NEXTAUTH_URL = "https://vm.massedcompute.com";

import { POST } from "@/app/api/mcp/directory/route";
import { dispatchJsonRpc } from "@/app/api/mcp/_lib/dispatcher";
import { findToolOnSurface } from "@/app/api/mcp/_lib/registry";
import { resolveMcpAuth } from "@/app/api/mcp/_lib/resolveAuth";

jest.mock("@/app/_utils/pgConfig", () => ({
    getPgPool: jest.fn(() => { throw new Error("No database permitted"); }),
    getOAuthPgPool: jest.fn(() => { throw new Error("No database permitted"); }),
}));
jest.mock("@/app/api/mcp/_lib/resolveAuth", () => ({ resolveMcpAuth: jest.fn() }));
jest.mock("@sentry/nextjs", () => ({ captureException: jest.fn(), captureMessage: jest.fn() }), { virtual: true });
jest.mock("@/app/api/mcp/_lib/mcpAudit", () => ({ recordMcpEvent: jest.fn().mockResolvedValue(undefined) }));
jest.mock("@/app/_utils/signozServerLogger", () => ({ __esModule: true, default: jest.fn(), sendLogToSigNozServer: jest.fn() }));
jest.mock("@/app/_utils/authFailureLogger", () => ({
    ...jest.requireActual("@/app/_utils/authFailureLogger"), logAuthFailure: jest.fn(),
}));
jest.mock("@/app/api/v1/_utils/publicApiAdapters", () => ({
    PublicApiError: class PublicApiError extends Error {},
    createSshKey: jest.fn(), deleteSshKey: jest.fn(),
    getAccountBilling: jest.fn(), getCouponAcceptedProducts: jest.fn(),
    getCouponInformation: jest.fn(), getGpuInventory: jest.fn(),
    getImages: jest.fn(), getInstance: jest.fn(), launchInstanceTool: jest.fn(),
    listInstances: jest.fn(), listSshKeys: jest.fn(), restartInstanceTool: jest.fn(),
    terminateInstanceTool: jest.fn(), validateToken: jest.fn(),
}));
jest.mock("@/app/api/mcp/_lib/recipeHandlers", () => ({
    recipesGetHandler: jest.fn(), recipesListHandler: jest.fn(), recipesSearchHandler: jest.fn(),
}));

const readonlyAuth = {
    ok: true as const,
    context: {
        user: { user_id: 1, user_account_id: 10 }, token: "local-test-only",
        userUuid: "test-user", readonly: 1 as const, apiKeyId: 42, accountId: 999,
        membership: { memberUuid: "test-member", role: "owner" as const, permissions: null, userId: 1, accountId: 999 },
    },
};
const writes = ["instances_restart", "instances_terminate", "ssh_keys_create", "ssh_keys_delete"];

beforeEach(() => {
    jest.clearAllMocks();
    (resolveMcpAuth as jest.Mock).mockResolvedValue(readonlyAuth);
});
afterEach(() => jest.restoreAllMocks());

describe.each(["legacy", "modern"] as const)("directory readonly dispatcher (%s)", (era) => {
    it.each(writes)("rejects %s before its handler", async (name) => {
        const tool = findToolOnSurface(name, "chatgpt-directory")!;
        expect(tool.requiredReadonly).toBe(0);
        const handler = jest.spyOn(tool, "handler").mockResolvedValue({ forbiddenExecution: true });
        const out = await dispatchJsonRpc(
            { jsonrpc: "2.0", id: 1, method: "tools/call", params: { name, arguments: {} } },
            async () => readonlyAuth,
            { requestId: "local-readonly-proof", era, mcpSurface: "chatgpt-directory" },
        );
        expect(out).toMatchObject({ error: { code: 40300 } });
        expect(JSON.stringify(out)).toContain("read-only");
        expect(handler).not.toHaveBeenCalled();
    });
});

it.each(writes)("HTTP directory route rejects readonly %s before its handler", async (name) => {
    const tool = findToolOnSurface(name, "chatgpt-directory")!;
    const handler = jest.spyOn(tool, "handler").mockResolvedValue({ forbiddenExecution: true });
    const response = await POST(new Request("https://vm.massedcompute.com/api/mcp/directory", {
        method: "POST", headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ jsonrpc: "2.0", id: 1, method: "tools/call", params: { name, arguments: {} } }),
    }));
    expect(await response.json()).toMatchObject({ error: { code: 40300 } });
    expect(handler).not.toHaveBeenCalled();
});
