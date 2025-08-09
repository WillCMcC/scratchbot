const { request } = require("@octokit/request");

const manifest = {
  name: "ScratchBot",
  url: "https://example.com",
  hook_attributes: { url: "https://example.com/webhooks/github" },
  redirect_url: "http://localhost:3000/api/auth/callback",
  public: false,
  default_permissions: {
    contents: "write",
    pull_requests: "write"
  },
  default_events: ["pull_request"]
};

async function registerApp(code) {
  const { data } = await request("POST /app-manifests/{code}/conversions", {
    headers: {
      Accept: "application/vnd.github+json"
    },
    code,
    data: manifest
  });
  console.log(data); // Contains app credentials
}

const code = process.argv[2];
if (!code) {
  console.error("Usage: npm run register-app <code>");
  process.exit(1);
}

registerApp(code).catch((err) => {
  console.error(err);
  process.exit(1);
});
