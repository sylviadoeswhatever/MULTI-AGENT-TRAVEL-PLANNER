import { useState } from "react";

const categories = [
  {
    id: "secrets",
    icon: "🔑",
    label: "Secrets & Credentials",
    color: "#ff4757",
    mistakes: [
      {
        id: "s1",
        title: "API Keys Hardcoded in Frontend",
        severity: "CRITICAL",
        description: "AI places API keys, tokens, or secrets directly in client-side JS — visible to anyone in DevTools.",
        examples: ["const openai = new OpenAI({ apiKey: 'sk-proj-abc123...' })", "REACT_APP_SECRET_KEY=supersecret (shipped to every browser)", "Supabase/Firebase keys in frontend config files"],
        fix: "Move all secrets to server-side environment variables. Use a backend proxy to call third-party APIs. Never prefix secret keys with NEXT_PUBLIC_ or VITE_ — those are intentionally exposed.",
        tools: ["gitleaks", "trufflehog", "dotenv-safe"],
      },
      {
        id: "s2",
        title: "Secrets Committed to Git",
        severity: "CRITICAL",
        description: "AI generates .env files or config files with real credentials and they get committed. Git history is permanent.",
        examples: ["database_url = postgres://user:realpassword@host", ".env file not in .gitignore", "config.js with API keys"],
        fix: "Add .env to .gitignore before first commit. Scan git history with trufflehog. Rotate any exposed keys immediately. Use secret scanning in your CI/CD pipeline.",
        tools: ["git-secrets", "trufflehog", "GitHub Secret Scanning"],
      },
      {
        id: "s3",
        title: "Secrets Returned in API Responses",
        severity: "HIGH",
        description: "AI serializes entire database objects or configs into API responses, accidentally exposing internal fields.",
        examples: ["Returning full user object including password_hash", "Leaking internal API keys in response body", "Debug info containing connection strings"],
        fix: "Always whitelist response fields explicitly. Never return raw DB objects. Use a DTO (Data Transfer Object) pattern or response serializer.",
        tools: ["Zod", "class-transformer"],
      },
    ],
  },
  {
    id: "auth",
    icon: "🔐",
    label: "Authentication & Authorization",
    color: "#ff6b35",
    mistakes: [
      {
        id: "a1",
        title: "Client-Side-Only Authentication",
        severity: "CRITICAL",
        description: "Auth logic lives entirely in JavaScript — any user can open DevTools and bypass it by calling the API directly.",
        examples: ["if (user.isAdmin) showAdminPanel()", "Frontend route guards with no server-side check", "JWT decoded and trusted client-side without server verification"],
        fix: "Every protected action must be verified server-side. Frontend guards are UX only. Verify the auth token / session on every API request in middleware.",
        tools: ["NextAuth.js", "Supabase Auth", "JWT verify on server"],
      },
      {
        id: "a2",
        title: "Missing Row-Level Security (RLS)",
        severity: "CRITICAL",
        description: "AI creates Supabase/Firebase tables without RLS policies — the anon key gives full read/write access to all rows.",
        examples: ["Supabase table with no RLS policies enabled", "Firebase rules: allow read, write: if true", "Any table where users can read other users' data"],
        fix: "Enable RLS on every table. Write policies that check auth.uid() = user_id. Test with the anon key to verify data isolation.",
        tools: ["Supabase RLS Policies", "Firebase Rules"],
      },
      {
        id: "a3",
        title: "IDOR — Insecure Direct Object References",
        severity: "HIGH",
        description: "AI generates endpoints that accept a user ID parameter without verifying the logged-in user owns that resource.",
        examples: ["GET /api/documents/:id  — no ownership check", "DELETE /api/posts/:id  — deletes any post", "PUT /api/users/:userId/profile  — editable by anyone"],
        fix: "Every endpoint must verify: does the authenticated user own this resource? Add WHERE user_id = req.user.id to every query involving user data.",
        tools: ["Manual review", "ZeroPath", "Burp Suite"],
      },
      {
        id: "a4",
        title: "Admin Routes Protected Only by Frontend",
        severity: "HIGH",
        description: "AI hides admin UI with conditional rendering but doesn't protect the underlying API routes.",
        examples: ["{isAdmin && <AdminPanel />}", "Route /admin with no server-side role check", "Admin API endpoints without role middleware"],
        fix: "Protect every admin API endpoint with server-side role middleware. Frontend hiding is cosmetic only.",
        tools: ["Middleware guards", "RBAC libraries"],
      },
      {
        id: "a5",
        title: "Weak Password Hashing",
        severity: "HIGH",
        description: "AI uses MD5, SHA-1, or plaintext for passwords. These are trivially crackable if the database is breached.",
        examples: ["md5(password)", "sha1(password)", "Storing plaintext passwords"],
        fix: "Use bcrypt, scrypt, or Argon2 exclusively. Never use MD5/SHA-1 for passwords. Add a salt. Verify the hashing library is modern.",
        tools: ["bcrypt", "argon2", "scrypt"],
      },
    ],
  },
  {
    id: "injection",
    icon: "💉",
    label: "Injection Vulnerabilities",
    color: "#ffa502",
    mistakes: [
      {
        id: "i1",
        title: "SQL Injection via String Concatenation",
        severity: "CRITICAL",
        description: "AI builds SQL queries by concatenating user input instead of using parameterized statements.",
        examples: ["SELECT * FROM users WHERE id = '${userId}'", "query('SELECT * FROM orders WHERE user = ' + username)", "db.execute(`DELETE FROM posts WHERE id = ${req.params.id}`)"],
        fix: "Always use parameterized queries or an ORM. Never concatenate user input into SQL. Use prepared statements.",
        tools: ["Prisma", "Knex.js parameterized", "pg-promise"],
      },
      {
        id: "i2",
        title: "Cross-Site Scripting (XSS)",
        severity: "HIGH",
        description: "AI renders user input directly in HTML without sanitization — attackers can inject scripts that run in other users' browsers.",
        examples: ["innerHTML = userInput", "dangerouslySetInnerHTML={{ __html: userComment }}", "Displaying unescaped URL parameters"],
        fix: "Never use innerHTML/dangerouslySetInnerHTML with user data. Use textContent for text. Sanitize HTML with DOMPurify if rich text is required. Set Content-Security-Policy headers.",
        tools: ["DOMPurify", "CSP headers", "Helmet.js"],
      },
      {
        id: "i3",
        title: "OS Command Injection",
        severity: "CRITICAL",
        description: "AI passes user input directly into shell commands.",
        examples: ["exec(`convert ${userFilename} output.png`)", "spawn('grep', [userInput, '/etc/passwd'])", "child_process.exec('ls ' + req.query.path)"],
        fix: "Never pass user input to shell commands. Use language-native APIs instead. If unavoidable, use execFile with explicit argument arrays, never exec with string interpolation.",
        tools: ["ESLint security rules", "Semgrep"],
      },
      {
        id: "i4",
        title: "Missing Input Validation",
        severity: "HIGH",
        description: "AI generates the happy path only — no validation of user-submitted data on the server side.",
        examples: ["No type checking on API body params", "Accepting arbitrary file extensions for upload", "No length limits on text fields"],
        fix: "Validate ALL inputs server-side using a schema validator. Reject anything that doesn't match the expected shape. Never trust the client.",
        tools: ["Zod", "Joi", "express-validator"],
      },
    ],
  },
  {
    id: "config",
    icon: "⚙️",
    label: "Security Misconfiguration",
    color: "#eccc68",
    mistakes: [
      {
        id: "c1",
        title: "DEBUG Mode Enabled in Production",
        severity: "HIGH",
        description: "AI leaves debug flags on — stack traces, internal paths, and database errors get exposed to users.",
        examples: ["DEBUG=True in Django settings.py", "NODE_ENV not set to 'production'", "Verbose error messages with stack traces in API responses"],
        fix: "Set NODE_ENV=production / DEBUG=False before deploy. Return generic error messages to clients. Log detailed errors server-side only.",
        tools: ["dotenv", "environment config validation"],
      },
      {
        id: "c2",
        title: "Wildcard CORS Policy",
        severity: "HIGH",
        description: "AI sets CORS to Access-Control-Allow-Origin: * — any website can make authenticated requests to your API.",
        examples: ["cors({ origin: '*' })", "Access-Control-Allow-Origin: *  with credentials", "No CORS restriction on internal APIs"],
        fix: "Explicitly whitelist your frontend domain(s) only. Never use * when credentials (cookies/auth headers) are involved.",
        tools: ["cors npm package", "Helmet.js"],
      },
      {
        id: "c3",
        title: "Missing HTTP Security Headers",
        severity: "MEDIUM",
        description: "AI skips headers like CSP, HSTS, X-Frame-Options — leaving the app open to clickjacking, MITM, and script injection.",
        examples: ["No Content-Security-Policy", "No Strict-Transport-Security", "No X-Frame-Options header"],
        fix: "Use Helmet.js (Node) or equivalent. Set CSP, HSTS, X-Frame-Options, X-Content-Type-Options on every response.",
        tools: ["Helmet.js", "securityheaders.com"],
      },
      {
        id: "c4",
        title: "Cloud Storage Buckets Set to Public",
        severity: "CRITICAL",
        description: "AI creates S3 buckets or cloud storage without access restrictions.",
        examples: ["S3 bucket with public ACL", "Firebase Storage rules: allow read: if true", "GCS bucket with allUsers permission"],
        fix: "Default to private. Explicitly grant access only to authenticated users. Audit bucket policies before launch.",
        tools: ["AWS S3 Block Public Access", "IAM policies"],
      },
      {
        id: "c5",
        title: "Default / Unchanged Credentials",
        severity: "HIGH",
        description: "AI uses placeholder passwords that never get changed — admin/admin, postgres/postgres, etc.",
        examples: ["database password: 'password'", "admin account: admin/admin123", "Redis with no AUTH password"],
        fix: "Rotate all default credentials. Use a password manager or secrets manager. Audit for common default passwords before deploy.",
        tools: ["1Password", "Vault", "AWS Secrets Manager"],
      },
    ],
  },
  {
    id: "crypto",
    icon: "🔒",
    label: "Cryptography Mistakes",
    color: "#2ed573",
    mistakes: [
      {
        id: "cr1",
        title: "Weak or Outdated Algorithms",
        severity: "HIGH",
        description: "AI suggests MD5, SHA-1, or DES — all broken. AI replicates insecure patterns from old training data.",
        examples: ["crypto.createHash('md5')", "Using DES or 3DES for encryption", "SHA-1 for signatures"],
        fix: "Use SHA-256 or SHA-3 for hashing. AES-256-GCM for encryption. RSA-2048+ or Ed25519 for signatures. bcrypt/Argon2 for passwords.",
        tools: ["Node crypto built-ins", "libsodium"],
      },
      {
        id: "cr2",
        title: "Hardcoded Encryption Keys",
        severity: "CRITICAL",
        description: "AI hardcodes encryption/signing keys in source code.",
        examples: ["const SECRET_KEY = 'myverysecretkey123'", "JWT signed with 'secret'", "AES key embedded in code"],
        fix: "Generate strong random keys. Store in environment variables or a secrets manager. Rotate keys regularly.",
        tools: ["crypto.randomBytes()", "AWS KMS", "Vault"],
      },
      {
        id: "cr3",
        title: "Predictable Random Number Generation",
        severity: "MEDIUM",
        description: "AI uses Math.random() for security-sensitive values like tokens, session IDs, or OTPs.",
        examples: ["Math.random() for token generation", "Date.now() as a session ID", "Predictable reset tokens"],
        fix: "Use crypto.randomBytes() or crypto.randomUUID() for all security-sensitive randomness.",
        tools: ["Node.js crypto module", "uuid"],
      },
    ],
  },
  {
    id: "performance",
    icon: "⚡",
    label: "Performance & Scalability",
    color: "#1e90ff",
    mistakes: [
      {
        id: "p1",
        title: "N+1 Query Problem",
        severity: "HIGH",
        description: "AI fetches related data inside a loop — 1 query becomes 100+ in production.",
        examples: ["for (post of posts) { post.comments = await getComments(post.id) }", "Fetching user for every post in a list", "No eager loading of relations"],
        fix: "Use JOIN queries or ORM eager loading (.include / .with). Always fetch related data in bulk, not in loops.",
        tools: ["Prisma include", "Sequelize eager loading", "DataLoader"],
      },
      {
        id: "p2",
        title: "No Caching",
        severity: "MEDIUM",
        description: "AI generates code where every request hits the database cold — no caching layer.",
        examples: ["Fetching static config from DB on every request", "No Redis cache for frequently-read data", "Recomputing expensive queries every time"],
        fix: "Add caching for frequently-read, rarely-changed data. Use Redis, in-memory cache, or HTTP caching headers appropriately.",
        tools: ["Redis", "node-cache", "SWR/React Query"],
      },
      {
        id: "p3",
        title: "Database Connection Leaks",
        severity: "HIGH",
        description: "AI opens database connections but never closes them — the DB gets overwhelmed after a few hundred requests.",
        examples: ["No connection pooling", "DB connections opened in request handlers without cleanup", "Unclosed connections in error paths"],
        fix: "Use a connection pool. Always close connections in finally blocks. Verify pool configuration for your expected concurrency.",
        tools: ["pg-pool", "Prisma connection pool", "Sequelize pool config"],
      },
      {
        id: "p4",
        title: "Loading Entire Table into Memory",
        severity: "HIGH",
        description: "AI fetches all rows and filters in JavaScript instead of using SQL WHERE clauses.",
        examples: ["const users = await db.all(); return users.filter(u => u.role === 'admin')", "No LIMIT on queries", "Processing thousands of records in-memory"],
        fix: "Always filter, sort, and paginate at the database level. Never load unbounded result sets into application memory.",
        tools: ["Cursor-based pagination", "SQL WHERE/LIMIT/OFFSET"],
      },
      {
        id: "p5",
        title: "No Rate Limiting",
        severity: "HIGH",
        description: "AI generates APIs with no rate limiting — open to abuse, brute force, and DDoS.",
        examples: ["Login endpoint with unlimited attempts", "Public API with no request throttling", "Password reset with no cooldown"],
        fix: "Add rate limiting to all public endpoints, especially auth. Use exponential backoff for login attempts.",
        tools: ["express-rate-limit", "Upstash Redis rate limit", "Cloudflare"],
      },
      {
        id: "p6",
        title: "Missing Database Indexes",
        severity: "MEDIUM",
        description: "AI creates tables without indexes on commonly queried columns — queries slow to a crawl as data grows.",
        examples: ["No index on user_id foreign key", "Querying by email with no index", "Full table scans on large tables"],
        fix: "Add indexes on all foreign keys and columns used in WHERE/ORDER BY clauses. Use EXPLAIN ANALYZE to verify query plans.",
        tools: ["EXPLAIN ANALYZE", "Prisma @@index", "pg_stat_statements"],
      },
    ],
  },
  {
    id: "errors",
    icon: "💥",
    label: "Error Handling",
    color: "#a29bfe",
    mistakes: [
      {
        id: "e1",
        title: "Stack Traces Leaked to Client",
        severity: "HIGH",
        description: "AI exposes internal error details in API responses — attackers learn your stack, file paths, and query structure.",
        examples: ["res.json({ error: err.stack })", "Unhandled promise rejections with full error detail", "Framework default error pages in production"],
        fix: "Catch all errors. Log full details server-side. Return only a generic message to the client (e.g. 'Something went wrong').",
        tools: ["Sentry", "winston", "Helmet.js"],
      },
      {
        id: "e2",
        title: "No Error Handling for Async Operations",
        severity: "HIGH",
        description: "AI generates async code without try/catch — one failed API call crashes the whole request.",
        examples: ["await fetch(url) with no try/catch", "Unhandled Promise rejections", "Database errors that bubble up unhandled"],
        fix: "Wrap all async operations in try/catch. Use a global error handler middleware. Never let errors propagate to the user unformatted.",
        tools: ["express-async-errors", "Global error middleware"],
      },
      {
        id: "e3",
        title: "Silent Logic Failures",
        severity: "MEDIUM",
        description: "AI code returns wrong results with no error — off-by-one errors, null handling issues, incorrect business logic.",
        examples: ["Returning undefined instead of 404", "Empty array treated the same as not-found", "Silent NaN in calculations"],
        fix: "Add explicit checks for null/undefined/empty. Write unit tests for edge cases. Validate return values, not just inputs.",
        tools: ["Jest", "Vitest", "TypeScript strict mode"],
      },
    ],
  },
  {
    id: "architecture",
    icon: "🏗️",
    label: "Architecture & Design",
    color: "#fd79a8",
    mistakes: [
      {
        id: "ar1",
        title: "No Environment Separation",
        severity: "HIGH",
        description: "AI generates one config for all environments — development debug settings run in production.",
        examples: ["Single config file used in dev and prod", "Production DB pointed to in development", "Detailed logs in production"],
        fix: "Use separate .env files per environment (.env.development, .env.production). Validate required env vars at startup.",
        tools: ["dotenv", "envalid", "zod env validation"],
      },
      {
        id: "ar2",
        title: "Hallucinated / Non-existent Dependencies",
        severity: "HIGH",
        description: "AI invents package names that don't exist on npm/PyPI — or packages that have been typosquatted.",
        examples: ["import from 'react-super-form-handler' (doesn't exist)", "pip install tensorflow-utils-pro", "Using abandoned packages with known CVEs"],
        fix: "Always verify every dependency on the official registry before installing. Check download counts, last publish date, and open issues.",
        tools: ["npmjs.com", "snyk advisor", "socket.dev"],
      },
      {
        id: "ar3",
        title: "No Soft Deletes",
        severity: "MEDIUM",
        description: "AI uses hard deletes (DELETE FROM ...) with no ability to recover data.",
        examples: ["Permanent deletion with no recycle bin", "No deleted_at timestamp pattern", "Deleted records unrecoverable"],
        fix: "Add a deleted_at column. Filter out soft-deleted records in queries. Only permanently delete after a safe period.",
        tools: ["Prisma soft delete middleware", "Sequelize paranoid mode"],
      },
      {
        id: "ar4",
        title: "Missing Webhook Signature Verification",
        severity: "HIGH",
        description: "AI creates webhook endpoints that accept any payload without verifying the signature.",
        examples: ["Stripe webhook with no signature check", "GitHub webhook without secret verification", "Accepting any POST to /webhook"],
        fix: "Verify webhook signatures using the provider's SDK. Reject requests with missing or invalid signatures.",
        tools: ["stripe.webhooks.constructEvent()", "GitHub webhook secret"],
      },
      {
        id: "ar5",
        title: "No Logging or Monitoring",
        severity: "MEDIUM",
        description: "AI builds apps with no structured logging — impossible to debug issues in production.",
        examples: ["console.log in production", "No error tracking", "No request logging for audit trail"],
        fix: "Use structured logging (JSON). Integrate error tracking. Set up uptime monitoring and alerts.",
        tools: ["Sentry", "Datadog", "Pino/Winston"],
      },
      {
        id: "ar6",
        title: "Technical Debt from Blind AI Trust",
        severity: "MEDIUM",
        description: "AI adds unnecessary microservices, wrong data structures, or overly complex patterns without understanding your actual constraints.",
        examples: ["Microservices where a monolith is fine", "ORM when a raw SQL query is simpler", "Reinventing functionality that exists in standard libraries"],
        fix: "Give the AI your architectural constraints upfront. Review generated code for unnecessary complexity. Ask the AI to justify architectural choices.",
        tools: ["Code review", "Architecture review sessions"],
      },
    ],
  },
  {
    id: "deps",
    icon: "📦",
    label: "Dependencies & Supply Chain",
    color: "#00cec9",
    mistakes: [
      {
        id: "d1",
        title: "Unreviewed AI-Added Dependencies",
        severity: "HIGH",
        description: "AI silently adds libraries without explanation — you deploy unknown code with unknown CVEs.",
        examples: ["AI added 12 new packages to package.json", "Unused dependencies left in codebase", "Old versions with known vulnerabilities"],
        fix: "Audit every AI-added dependency. Check for known CVEs. Remove unused packages. Pin versions and review changelogs.",
        tools: ["npm audit", "snyk", "socket.dev", "dependabot"],
      },
      {
        id: "d2",
        title: "License Contamination",
        severity: "MEDIUM",
        description: "AI reproduces GPL/copyleft code from training data — shipping it commercially creates legal liability.",
        examples: ["GPL-licensed code in a proprietary product", "Copyleft dependencies without license review", "Unattributed copied code"],
        fix: "Audit licenses of all dependencies. Use license-checker in CI. Replace GPL libraries with MIT/Apache alternatives for commercial projects.",
        tools: ["license-checker", "FOSSA", "WhiteSource"],
      },
    ],
  },
];

const severityConfig = {
  CRITICAL: { color: "#ff4757", bg: "#ff475720", label: "CRITICAL" },
  HIGH: { color: "#ff6b35", bg: "#ff6b3520", label: "HIGH" },
  MEDIUM: { color: "#ffa502", bg: "#ffa50220", label: "MEDIUM" },
};

export default function App() {
  const [activeCategory, setActiveCategory] = useState("secrets");
  const [checked, setChecked] = useState({});
  const [expandedItem, setExpandedItem] = useState(null);
  const [search, setSearch] = useState("");

  const toggleCheck = (id) => {
    setChecked((prev) => ({ ...prev, [id]: !prev[id] }));
  };

  const toggleExpand = (id) => {
    setExpandedItem((prev) => (prev === id ? null : id));
  };

  const totalItems = categories.flatMap((c) => c.mistakes).length;
  const checkedCount = Object.values(checked).filter(Boolean).length;
  const progress = Math.round((checkedCount / totalItems) * 100);

  const allMistakes = categories.flatMap((c) =>
    c.mistakes.map((m) => ({ ...m, categoryColor: c.color, categoryLabel: c.label }))
  );

  const filteredBySearch = search.trim()
    ? allMistakes.filter(
        (m) =>
          m.title.toLowerCase().includes(search.toLowerCase()) ||
          m.description.toLowerCase().includes(search.toLowerCase()) ||
          m.fix.toLowerCase().includes(search.toLowerCase())
      )
    : null;

  const currentCat = categories.find((c) => c.id === activeCategory);
  const displayMistakes = filteredBySearch || currentCat?.mistakes || [];

  const criticalUnchecked = allMistakes.filter(
    (m) => m.severity === "CRITICAL" && !checked[m.id]
  ).length;

  return (
    <div style={{
      fontFamily: "'Courier New', 'Lucida Console', monospace",
      background: "#0a0a0f",
      minHeight: "100vh",
      color: "#e0e0e0",
      display: "flex",
      flexDirection: "column",
    }}>
      {/* Header */}
      <div style={{
        background: "linear-gradient(135deg, #0d0d1a 0%, #1a0a2e 100%)",
        borderBottom: "1px solid #2a2a4a",
        padding: "24px 28px 20px",
      }}>
        <div style={{ display: "flex", alignItems: "flex-start", justifyContent: "space-between", flexWrap: "wrap", gap: "12px" }}>
          <div>
            <div style={{ display: "flex", alignItems: "center", gap: "10px", marginBottom: "4px" }}>
              <span style={{ fontSize: "22px" }}>🤖</span>
              <h1 style={{
                margin: 0,
                fontSize: "18px",
                fontWeight: "bold",
                color: "#fff",
                letterSpacing: "0.05em",
                textTransform: "uppercase",
              }}>
                AI Code Mistakes Checklist
              </h1>
            </div>
            <p style={{ margin: 0, fontSize: "12px", color: "#8888aa", letterSpacing: "0.03em" }}>
              {totalItems} known failure patterns · sourced from OWASP, Veracode, Kaspersky, Escape.tech &amp; others
            </p>
          </div>
          <div style={{ display: "flex", flexDirection: "column", alignItems: "flex-end", gap: "6px" }}>
            {criticalUnchecked > 0 && (
              <div style={{
                background: "#ff475720",
                border: "1px solid #ff4757",
                borderRadius: "4px",
                padding: "4px 10px",
                fontSize: "11px",
                color: "#ff4757",
                fontWeight: "bold",
              }}>
                ⚠ {criticalUnchecked} CRITICAL UNCHECKED
              </div>
            )}
            <div style={{ fontSize: "12px", color: "#8888aa" }}>{checkedCount}/{totalItems} resolved</div>
            <div style={{
              width: "160px",
              height: "6px",
              background: "#1a1a2e",
              borderRadius: "3px",
              overflow: "hidden",
            }}>
              <div style={{
                width: `${progress}%`,
                height: "100%",
                background: progress === 100 ? "#2ed573" : progress > 60 ? "#ffa502" : "#ff4757",
                borderRadius: "3px",
                transition: "width 0.3s ease",
              }} />
            </div>
            <div style={{ fontSize: "12px", color: progress === 100 ? "#2ed573" : "#8888aa" }}>
              {progress}% {progress === 100 ? "✓ ALL CLEAR" : "complete"}
            </div>
          </div>
        </div>

        {/* Search */}
        <div style={{ marginTop: "16px", position: "relative" }}>
          <span style={{
            position: "absolute", left: "12px", top: "50%", transform: "translateY(-50%)",
            color: "#8888aa", fontSize: "13px",
          }}>🔍</span>
          <input
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search all mistakes..."
            style={{
              width: "100%",
              padding: "8px 12px 8px 34px",
              background: "#0d0d1a",
              border: "1px solid #2a2a4a",
              borderRadius: "6px",
              color: "#e0e0e0",
              fontSize: "13px",
              outline: "none",
              boxSizing: "border-box",
              fontFamily: "inherit",
            }}
          />
        </div>
      </div>

      <div style={{ display: "flex", flex: 1, overflow: "hidden", minHeight: 0 }}>
        {/* Sidebar */}
        {!search && (
          <div style={{
            width: "220px",
            flexShrink: 0,
            background: "#0d0d1a",
            borderRight: "1px solid #1a1a2e",
            overflowY: "auto",
            padding: "12px 0",
          }}>
            {categories.map((cat) => {
              const catChecked = cat.mistakes.filter((m) => checked[m.id]).length;
              const isActive = activeCategory === cat.id;
              return (
                <button
                  key={cat.id}
                  onClick={() => { setActiveCategory(cat.id); setSearch(""); }}
                  style={{
                    display: "flex",
                    alignItems: "center",
                    gap: "10px",
                    width: "100%",
                    padding: "10px 16px",
                    background: isActive ? `${cat.color}18` : "transparent",
                    border: "none",
                    borderLeft: isActive ? `3px solid ${cat.color}` : "3px solid transparent",
                    color: isActive ? "#fff" : "#8888aa",
                    cursor: "pointer",
                    textAlign: "left",
                    fontSize: "12px",
                    letterSpacing: "0.03em",
                    transition: "all 0.15s",
                    fontFamily: "inherit",
                  }}
                >
                  <span style={{ fontSize: "15px" }}>{cat.icon}</span>
                  <div style={{ flex: 1, minWidth: 0 }}>
                    <div style={{
                      fontWeight: isActive ? "bold" : "normal",
                      whiteSpace: "nowrap",
                      overflow: "hidden",
                      textOverflow: "ellipsis",
                    }}>{cat.label}</div>
                    <div style={{ fontSize: "10px", color: catChecked === cat.mistakes.length ? "#2ed573" : "#55556a", marginTop: "2px" }}>
                      {catChecked}/{cat.mistakes.length} fixed
                    </div>
                  </div>
                </button>
              );
            })}
          </div>
        )}

        {/* Main Content */}
        <div style={{ flex: 1, overflowY: "auto", padding: "16px 20px" }}>
          {search && filteredBySearch && (
            <div style={{ marginBottom: "12px", fontSize: "12px", color: "#8888aa" }}>
              {filteredBySearch.length} result{filteredBySearch.length !== 1 ? "s" : ""} for "{search}"
            </div>
          )}

          {displayMistakes.length === 0 && (
            <div style={{ color: "#8888aa", fontSize: "13px", padding: "20px 0" }}>No results found.</div>
          )}

          {displayMistakes.map((mistake) => {
            const isChecked = checked[mistake.id];
            const isExpanded = expandedItem === mistake.id;
            const sev = severityConfig[mistake.severity];

            return (
              <div
                key={mistake.id}
                style={{
                  background: isChecked ? "#0d1a0d" : "#0f0f1a",
                  border: `1px solid ${isChecked ? "#2ed57330" : "#1e1e3a"}`,
                  borderRadius: "8px",
                  marginBottom: "8px",
                  overflow: "hidden",
                  transition: "all 0.2s ease",
                  opacity: isChecked ? 0.7 : 1,
                }}
              >
                {/* Row */}
                <div
                  style={{
                    display: "flex",
                    alignItems: "center",
                    padding: "12px 14px",
                    gap: "12px",
                    cursor: "pointer",
                  }}
                  onClick={() => toggleExpand(mistake.id)}
                >
                  {/* Checkbox */}
                  <div
                    onClick={(e) => { e.stopPropagation(); toggleCheck(mistake.id); }}
                    style={{
                      width: "18px",
                      height: "18px",
                      flexShrink: 0,
                      border: `2px solid ${isChecked ? "#2ed573" : "#3a3a5a"}`,
                      borderRadius: "4px",
                      background: isChecked ? "#2ed573" : "transparent",
                      display: "flex",
                      alignItems: "center",
                      justifyContent: "center",
                      cursor: "pointer",
                      transition: "all 0.15s",
                    }}
                  >
                    {isChecked && <span style={{ color: "#000", fontSize: "11px", fontWeight: "bold" }}>✓</span>}
                  </div>

                  {/* Severity badge */}
                  <span style={{
                    flexShrink: 0,
                    fontSize: "9px",
                    fontWeight: "bold",
                    letterSpacing: "0.08em",
                    color: sev.color,
                    background: sev.bg,
                    border: `1px solid ${sev.color}50`,
                    borderRadius: "3px",
                    padding: "2px 6px",
                  }}>{sev.label}</span>

                  {/* Title */}
                  <span style={{
                    flex: 1,
                    fontSize: "13px",
                    fontWeight: "600",
                    color: isChecked ? "#55556a" : "#e0e0e0",
                    textDecoration: isChecked ? "line-through" : "none",
                    letterSpacing: "0.02em",
                  }}>{mistake.title}</span>

                  {/* Expand indicator */}
                  <span style={{
                    color: "#55556a",
                    fontSize: "12px",
                    transition: "transform 0.2s",
                    transform: isExpanded ? "rotate(180deg)" : "rotate(0deg)",
                  }}>▼</span>
                </div>

                {/* Brief description always visible */}
                <div style={{ padding: "0 14px 10px 44px", fontSize: "11px", color: "#6a6a8a", lineHeight: "1.5" }}>
                  {mistake.description}
                </div>

                {/* Expanded detail */}
                {isExpanded && (
                  <div style={{
                    padding: "0 14px 14px 44px",
                    borderTop: "1px solid #1e1e3a",
                    paddingTop: "12px",
                  }}>
                    {/* Examples */}
                    <div style={{ marginBottom: "10px" }}>
                      <div style={{ fontSize: "10px", color: "#ff4757", fontWeight: "bold", marginBottom: "6px", textTransform: "uppercase", letterSpacing: "0.08em" }}>
                        ❌ What AI does wrong
                      </div>
                      {mistake.examples.map((ex, i) => (
                        <div key={i} style={{
                          background: "#1a0a0a",
                          border: "1px solid #3a1a1a",
                          borderRadius: "4px",
                          padding: "5px 10px",
                          fontSize: "11px",
                          color: "#cc8888",
                          marginBottom: "4px",
                          fontFamily: "'Courier New', monospace",
                        }}>{ex}</div>
                      ))}
                    </div>

                    {/* Fix */}
                    <div style={{ marginBottom: "10px" }}>
                      <div style={{ fontSize: "10px", color: "#2ed573", fontWeight: "bold", marginBottom: "6px", textTransform: "uppercase", letterSpacing: "0.08em" }}>
                        ✅ The fix
                      </div>
                      <div style={{
                        background: "#0a1a0a",
                        border: "1px solid #1a3a1a",
                        borderRadius: "4px",
                        padding: "8px 10px",
                        fontSize: "12px",
                        color: "#aaddaa",
                        lineHeight: "1.6",
                      }}>{mistake.fix}</div>
                    </div>

                    {/* Tools */}
                    <div>
                      <div style={{ fontSize: "10px", color: "#1e90ff", fontWeight: "bold", marginBottom: "6px", textTransform: "uppercase", letterSpacing: "0.08em" }}>
                        🛠 Tools
                      </div>
                      <div style={{ display: "flex", flexWrap: "wrap", gap: "5px" }}>
                        {mistake.tools.map((tool, i) => (
                          <span key={i} style={{
                            background: "#0a0a1a",
                            border: "1px solid #1e3050",
                            borderRadius: "3px",
                            padding: "2px 8px",
                            fontSize: "11px",
                            color: "#6699cc",
                          }}>{tool}</span>
                        ))}
                      </div>
                    </div>
                  </div>
                )}
              </div>
            );
          })}
        </div>
      </div>

      {/* Footer */}
      <div style={{
        borderTop: "1px solid #1a1a2e",
        padding: "8px 20px",
        fontSize: "10px",
        color: "#44445a",
        letterSpacing: "0.04em",
        background: "#0a0a0f",
      }}>
        SOURCES: OWASP TOP 10 · VERACODE 2025 GENAICSR · KASPERSKY · ESCAPE.TECH · INVICTI · AUGMENT CODE · NOBL9 · SERENITIES AI
      </div>
    </div>
  );
}
