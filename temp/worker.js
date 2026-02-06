const GITHUB_OWNER = "AndreaColamedici";
const GITHUB_REPO = "castello";

const TOOLS = [
  {
    name: "castello_list_files",
    description: "Elenca i file nel repository castello",
    inputSchema: {
      type: "object",
      properties: {
        path: { type: "string", description: "Percorso della directory (default: root)" }
      }
    }
  },
  {
    name: "castello_read_file",
    description: "Legge un file dal repository castello",
    inputSchema: {
      type: "object",
      properties: {
        path: { type: "string", description: "Percorso del file" }
      },
      required: ["path"]
    }
  },
  {
    name: "castello_push_file",
    description: "Scrive o aggiorna un file nel repository castello",
    inputSchema: {
      type: "object",
      properties: {
        path: { type: "string", description: "Percorso del file" },
        content: { type: "string", description: "Contenuto del file" },
        message: { type: "string", description: "Messaggio di commit" }
      },
      required: ["path", "content", "message"]
    }
  },
  {
    name: "castello_append_file",
    description: "Aggiunge contenuto in fondo a un file esistente nel repository castello.",
    inputSchema: {
      type: "object",
      properties: {
        path: { type: "string", description: "Percorso del file" },
        content: { type: "string", description: "Contenuto da aggiungere" },
        message: { type: "string", description: "Messaggio di commit" }
      },
      required: ["path", "content", "message"]
    }
  }
];

export default {
  async fetch(request, env, ctx) {
    const url = new URL(request.url);

    if (request.method === "OPTIONS") {
      return new Response(null, {
        headers: {
          "Access-Control-Allow-Origin": "*",
          "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
          "Access-Control-Allow-Headers": "*"
        }
      });
    }

    if (url.pathname === "/sse" || url.pathname === "/sse/") {
      return handleMCP(request, env);
    }

    return new Response("Castello MCP Server OK", { status: 200 });
  }
};

async function handleMCP(request, env) {
  if (request.method === "GET") {
    const { readable, writable } = new TransformStream();
    const writer = writable.getWriter();
    const encoder = new TextEncoder();

    (async () => {
      const msg = {
        jsonrpc: "2.0",
        method: "server/info",
        params: {
          name: "Castello MCP",
          version: "1.0.0"
        }
      };
      await writer.write(encoder.encode("data: " + JSON.stringify(msg) + "\n\n"));
      await writer.close();
    })();

    return new Response(readable, {
      headers: {
        "Content-Type": "text/event-stream",
        "Cache-Control": "no-cache",
        "Connection": "keep-alive",
        "Access-Control-Allow-Origin": "*"
      }
    });
  }

  if (request.method === "POST") {
    const body = await request.json();
    let response;

    if (body.method === "initialize") {
      response = {
        jsonrpc: "2.0",
        id: body.id,
        result: {
          protocolVersion: "2024-11-05",
          serverInfo: { name: "Castello MCP", version: "1.0.0" },
          capabilities: { tools: {} }
        }
      };
    } else if (body.method === "tools/list") {
      response = {
        jsonrpc: "2.0",
        id: body.id,
        result: { tools: TOOLS }
      };
    } else if (body.method === "tools/call") {
      const { name, arguments: args } = body.params;
      let result;

      try {
        if (name === "castello_list_files") {
          result = await listFiles(args.path || "", env.GITHUB_TOKEN);
        } else if (name === "castello_read_file") {
          result = await readFile(args.path, env.GITHUB_TOKEN);
        } else if (name === "castello_push_file") {
          result = await pushFile(args.path, args.content, args.message, env.GITHUB_TOKEN);
        } else if (name === "castello_append_file") {
          result = await appendFile(args.path, args.content, args.message, env.GITHUB_TOKEN);
        } else {
          result = { error: "Unknown tool: " + name };
        }
      } catch (e) {
        result = { error: e.message };
      }

      response = {
        jsonrpc: "2.0",
        id: body.id,
        result: {
          content: [{ type: "text", text: JSON.stringify(result, null, 2) }]
        }
      };
    } else {
      response = { jsonrpc: "2.0", id: body.id, result: {} };
    }

    return new Response(JSON.stringify(response), {
      headers: {
        "Content-Type": "application/json",
        "Access-Control-Allow-Origin": "*"
      }
    });
  }

  return new Response("Method not allowed", { status: 405 });
}

async function listFiles(path, token) {
  const apiPath = path ? path : "";
  const response = await fetch(
    "https://api.github.com/repos/" + GITHUB_OWNER + "/" + GITHUB_REPO + "/contents/" + apiPath,
    {
      headers: {
        "Authorization": "Bearer " + token,
        "Accept": "application/vnd.github.v3+json",
        "User-Agent": "Castello-MCP"
      }
    }
  );

  if (!response.ok) {
    throw new Error("Directory not found: " + (path || "/"));
  }

  const data = await response.json();

  if (!Array.isArray(data)) {
    return [{ name: data.name, type: data.type, path: data.path }];
  }

  return data.map(function(item) {
    return {
      name: item.name,
      type: item.type === "dir" ? "dir" : "file",
      path: item.path
    };
  });
}

async function readFile(path, token) {
  const response = await fetch(
    "https://api.github.com/repos/" + GITHUB_OWNER + "/" + GITHUB_REPO + "/contents/" + path,
    {
      headers: {
        "Authorization": "Bearer " + token,
        "Accept": "application/vnd.github.v3+json",
        "User-Agent": "Castello-MCP"
      }
    }
  );

  if (!response.ok) {
    throw new Error("File not found: " + path);
  }

  const data = await response.json();
  const content = atob(data.content.replace(/\n/g, ""));
  return { content: content, sha: data.sha, path: data.path };
}

async function pushFile(path, content, message, token) {
  var sha = null;
  try {
    var existing = await readFile(path, token);
    sha = existing.sha;
  } catch (e) {
    // File doesn't exist yet
  }

  var body = {
    message: message,
    content: btoa(unescape(encodeURIComponent(content)))
  };
  if (sha) body.sha = sha;

  var response = await fetch(
    "https://api.github.com/repos/" + GITHUB_OWNER + "/" + GITHUB_REPO + "/contents/" + path,
    {
      method: "PUT",
      headers: {
        "Authorization": "Bearer " + token,
        "Accept": "application/vnd.github.v3+json",
        "User-Agent": "Castello-MCP",
        "Content-Type": "application/json"
      },
      body: JSON.stringify(body)
    }
  );

  if (!response.ok) {
    var err = await response.text();
    throw new Error("Push failed: " + err);
  }

  return { success: true, path: path, message: message };
}

async function appendFile(path, content, message, token) {
  var existing = await readFile(path, token);
  var newContent = existing.content + "\n\n" + content;
  return await pushFile(path, newContent, message, token);
}
