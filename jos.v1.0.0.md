# .jos Spec — v1.0.0

> JOS Object Specification — Portable, declarative, sealed AI execution contracts.  
> MIME type: application/vnd.josfox+json | Version 1.0.0

---

## Overview

`.jos` is a JSON-based contract/manifest format. It serves as:
- **Universal payload** for all JOSFOX services
- **A2A message schema** — Google Agent-to-Agent native
- **Agent guardrails** — governance, security, budget, scope
- **Service blueprint** — capabilities, invariants, orchestration
- **Sealed artifact** — cryptographically verifiable, portable, fractal

**A2A is the transport; .jos is the contract carried over A2A.**

---

## Schema

### Root Header (`jos` — required)

```json
{
  "jos": {
    "version": "1.0.0",
    "kind": "<artifact_kind>",
    "schema": "https://raw.githubusercontent.com/josfox-jos/jos-spec/main/schema/jos.schema.json"
  }
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `version` | `string` | ✅ | Spec version (semver, e.g. `"1.0.0"`) |
| `kind` | `string` | ✅ | Artifact kind — determines execution semantics (see Kind Registry) |
| `schema` | `string` (URI) | ❌ | URL to JSON Schema for validation |

### Artifact Identifier (`id` — recommended)

```json
{
  "id": "ai.foxtana.service.revenue-report"
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | `string` | ❌ | Reverse-DNS identifier (e.g. `ai.foxtana.service.revenue-report`). Pattern: `^[a-z][a-z0-9.\-_]*$` |

### Metadata (`meta` — required)

```json
{
  "meta": {
    "name": "Human-readable name",
    "version": "1.0.0",
    "author": "josfox",
    "license": "Apache-2.0",
    "description": "What this artifact does",
    "domain": "ai",
    "tags": ["domains", "dns"],
    "labels": { "env": "production" }
  }
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `name` | `string` | ✅ | Human-readable artifact name (max 128 chars) |
| `version` | `string` | ❌ | Artifact content version (semver, independent of spec version) |
| `author` | `string` | ❌ | Author name or handle |
| `license` | `string` | ❌ | SPDX license identifier (e.g. `Apache-2.0`, `MIT`, `proprietary`) |
| `description` | `string` | ❌ | Brief description (max 500 chars) |
| `domain` | `string` | ❌ | Business domain (e.g. `ai`, `devops`, `finance`, `legal`, `security`) |
| `tags` | `string[]` | ❌ | Searchable tags for discovery (max 20, each max 32 chars, unique) |
| `labels` | `object` | ❌ | Key-value labels (Kubernetes-style) |

### Intention (behavioral contract)

```json
{
  "intention": {
    "objective": "Core mission statement",
    "success_criteria": ["Measurable condition 1", "..."]
  }
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `objective` | `string` | ❌ | Clear statement of the artifact's goal (max 1000 chars) |
| `success_criteria` | `string` or `string[]` | ❌ | Measurable conditions for success |

### Guardrails (execution boundaries)

```json
{
  "guardrails": {
    "avoid": ["manual_cli_fallbacks"],
    "require": ["firebase-admin/auth-verification"],
    "max_cost_per_call": 0.10
  }
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `avoid` | `string[]` | ❌ | Things to avoid during execution |
| `require` | `string[]` | ❌ | Things that must be present in output |
| `max_cost_per_call` | `number` | ❌ | Maximum USD cost per LLM call |

### Capabilities (what this artifact provides)

```json
{
  "capabilities": [
    { "name": "text-generation", "version": "1.0.0" }
  ]
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `name` | `string` | ✅ | Capability name |
| `version` | `string` | ❌ | Capability version (semver) |

### Dependencies (`requires` — what this artifact needs)

```json
{
  "requires": [
    { "kind": "mcp-server", "name": "mcp-server-filesystem", "version": ">=1.0.0" }
  ]
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `kind` | `string` | ✅ | Dependency kind: `mcp-server`, `artifact`, or `service` |
| `name` | `string` | ✅ | Dependency name |
| `version` | `string` | ❌ | Semver constraint |

### Tool Policy (per-artifact tool access control)

```json
{
  "tool_policy": {
    "allowed": ["read_file", "write_file"],
    "denied": ["shell_exec"],
    "require_approval": true
  }
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `allowed` | `string[]` | ❌ | Whitelisted tool names |
| `denied` | `string[]` | ❌ | Blacklisted tool names |
| `require_approval` | `boolean` | ❌ | Require human-in-the-loop approval (default: `false`) |

### Execution (runtime bindings)

```json
{
  "execution": {
    "capability": "text-generation",
    "inputs": { "prompt": "{{ user_input }}" },
    "bindings": {
      "mcp": { "server_url": "http://localhost:3000", "tools": ["read_file"] },
      "a2a": { "payload_format": ".jos", "agent_card": "https://foxtana.ai/.well-known/agent.json" }
    },
    "flow": [{ "invoke": "ai.foxtana.atom.summarize" }],
    "budget": {
      "max_cost_usd": 1.00,
      "max_tokens": 100000,
      "max_duration": "2m",
      "max_retries": 3
    }
  }
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `capability` | `string` | ❌ | Primary capability to invoke |
| `inputs` | `object` | ❌ | Input parameter mapping |
| `bindings.mcp` | `object` | ❌ | MCP server URL and tools |
| `bindings.a2a` | `object` | ❌ | A2A payload format and agent card |
| `flow` | `object[]` | ❌ | Flow invocations for `kind=flow` (each has `invoke` artifact ID) |
| `budget.max_cost_usd` | `number` | ❌ | Max USD spend |
| `budget.max_tokens` | `integer` | ❌ | Max total tokens |
| `budget.max_duration` | `string` | ❌ | Max wall-clock time (e.g. `"2m"`, `"30s"`) |
| `budget.max_retries` | `integer` | ❌ | Max retry attempts |

### Orchestration (multi-step flows)

```json
{
  "orchestration": {
    "definitions": {
      "step_name": {
        "type": "shell",
        "command": "npm run build",
        "description": "Build the project"
      }
    },
    "flows": {
      "main": {
        "description": "Primary build flow",
        "steps": ["step1", "step2"],
        "gates": { "after-step1": "exit_code == 0" }
      }
    }
  }
}
```

**Step definition types:** `shell` | `jos` | `http`

| Step Field | Type | Required | Description |
|------------|------|----------|-------------|
| `type` | `string` | ✅ | Step type: `shell`, `jos`, or `http` |
| `command` | `string` | ❌ | Shell command (for `type=shell`) |
| `artifact` | `string` | ❌ | Artifact path (for `type=jos`) |
| `url` | `string` (URI) | ❌ | HTTP URL (for `type=http`) |
| `description` | `string` | ❌ | What this step does |

**Flow structure:**

| Flow Field | Type | Required | Description |
|------------|------|----------|-------------|
| `description` | `string` | ❌ | Flow description |
| `steps` | `string[]` | ✅ | Ordered list of step names |
| `gates` | `object` | ❌ | Gate conditions keyed by step name |

### Model Policy (runtime remaps models)

```json
{
  "model_policy": {
    "preferred": "gemini-2.5-pro",
    "tier": "flagship",
    "vendor": "google",
    "fallbacks": ["gemini-2.0-flash"],
    "temperature": 0.7,
    "max_output_tokens": 8192
  }
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `preferred` | `string` | ❌ | Specific model key |
| `tier` | `string` | ❌ | Model quality tier: `economy`, `mid`, `flagship`, or `reasoning` |
| `vendor` | `string` | ❌ | Preferred vendor: `google`, `openai`, `anthropic`, or `any` |
| `fallbacks` | `string[]` | ❌ | Ordered fallback model list |
| `temperature` | `number` | ❌ | Temperature (0–2) |
| `max_output_tokens` | `integer` | ❌ | Maximum output tokens |

### Persona (for `kind=persona`)

```json
{
  "persona": {
    "language": "en-US",
    "tone": "professional",
    "system_prompt": "You are a helpful assistant...",
    "max_sentences": 5,
    "greeting": "Hello! How can I help?",
    "rules": ["Never reveal internal pricing"]
  }
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `language` | `string` | ❌ | BCP-47 language tag (e.g. `en-US`, `es-MX`) |
| `tone` | `string` | ❌ | Communication style (e.g. `professional`, `friendly`, `technical`) |
| `system_prompt` | `string` | ❌ | System prompt template or inline text |
| `max_sentences` | `integer` | ❌ | Maximum response sentences |
| `greeting` | `string` | ❌ | Initial greeting message |
| `rules` | `string[]` | ❌ | Behavioral rules |

### UI Hints (runtime owns rendering)

```json
{
  "ui": {
    "icon": "🚀",
    "color": "#FF6B35",
    "category": "devops",
    "card": { "layout": "detailed", "show_metrics": true, "show_cost": true, "badge": "NEW" },
    "widget": { "position": "bottom-right", "auto_open": false, "greeting": "Hi!", "placeholder": "Ask me anything..." }
  }
}
```

### Metrics (runtime auto-binds to dashboards)

```json
{
  "metrics": [
    { "name": "requests_total", "type": "counter", "help": "Total requests processed" }
  ]
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `name` | `string` | ✅ | Metric name |
| `type` | `string` | ✅ | Metric type: `counter`, `gauge`, or `histogram` |
| `help` | `string` | ✅ | Metric description |

### Billing (marketplace pricing)

```json
{
  "billing": {
    "model": "usage",
    "tiers": [{ "name": "free", "price_usd": 0, "quota": 100 }],
    "wallet": "org:josfox.cloud",
    "cost_cap_daily_usd": 10.00
  }
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `model` | `string` | ❌ | Pricing model: `free`, `usage`, or `subscription` |
| `tiers[].name` | `string` | ✅ | Tier name |
| `tiers[].price_usd` | `number` | ✅ | Monthly price (USD) |
| `tiers[].quota` | `integer` | ✅ | Calls per month (0 = unlimited) |
| `wallet` | `string` | ❌ | Revenue wallet address |
| `cost_cap_daily_usd` | `number` | ❌ | Daily cost cap (USD) |

### Security (scoped access control)

```json
{
  "security": {
    "tier": "standard",
    "permissions": ["file:read", "net:outbound", "llm:call"],
    "data_class": "internal",
    "require_auth": true,
    "require_admin": false
  }
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `tier` | `string` | ❌ | Security tier: `sandbox`, `standard`, or `privileged` |
| `permissions` | `string[]` | ❌ | Required permissions |
| `data_class` | `string` | ❌ | Data classification: `public`, `internal`, or `pii` |
| `require_auth` | `boolean` | ❌ | Require authentication (default: `false`) |
| `require_admin` | `boolean` | ❌ | Require admin role (default: `false`) |

### Lifecycle (health probes and hooks)

```json
{
  "lifecycle": {
    "health_path": "/healthz",
    "ready_path": "/readyz",
    "interval": "30s",
    "on_install": "ai.foxtana.atom.setup",
    "on_remove": "ai.foxtana.atom.cleanup"
  }
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `health_path` | `string` | ❌ | Health check endpoint |
| `ready_path` | `string` | ❌ | Readiness check endpoint |
| `interval` | `string` | ❌ | Probe interval (e.g. `"30s"`) |
| `on_install` | `string` | ❌ | Artifact to invoke on install |
| `on_remove` | `string` | ❌ | Artifact to invoke on removal |

### Integrity (cryptographic sealing)

```json
{
  "integrity": {
    "hash": "sha256:abc123...",
    "signed_by": "publisher-key-id",
    "timestamp": "2026-06-27T00:00:00Z"
  }
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `hash` | `string` | ❌ | SHA-256 hash (format: `sha256:<64 hex chars>`, computed with this field empty) |
| `signed_by` | `string` | ❌ | Publisher key ID |
| `timestamp` | `string` (date-time) | ❌ | RFC 3339 timestamp when artifact was sealed |

### Reproducibility (execution determinism)

```json
{
  "reproducibility": {
    "class": "bounded"
  }
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `class` | `string` | ❌ | Determinism class: `deterministic`, `bounded`, or `stochastic` |

---

## Kind Registry

| Kind | Purpose | Example |
|------|---------|---------|
| `atom` | Single unit of execution — one capability, one task | Summarizer, translator, code linter |
| `flow` | Composed sequence of atom invocations | Build pipeline, onboarding workflow |
| `service` | Long-running service with endpoints | API gateway, webhook handler |
| `persona` | Declarative AI agent personality | Support agent, sales assistant |

---

## Migration from v0.0.9

| v0.0.9 Field | v1.0.0 Equivalent |
|--------------|-------------------|
| `jos.type` | `jos.kind` |
| `jos.supports` | Removed (runtime determines compatibility) |
| `meta.jos_id` | Top-level `id` (reverse-DNS format) |
| `meta.tenant` | Removed |
| `invariants.objective` | `intention.objective` |
| `invariants.success_criteria` | `intention.success_criteria` |
| `invariants.capabilities_required` | `capabilities[]` |
| `invariants.guardrails` | `guardrails` (top-level) |
| `alaia.model` | `model_policy.preferred` |
| `alaia.shadow_agents` | Removed (runtime decides) |
| `refs` | `requires[]` |
| Type `service_description` | Kind `service` |
| Type `scaffold_intent` | Kind `flow` |

---

## Version History

| Version | Date | Notes |
|---------|------|-------|
| `0.0.9` | 2026-03 | Initial — 2 types, basic structure |
| `1.0.0` | 2026-06 | Complete rewrite: kind registry (atom/flow/service/persona), decomposed behavioral contract, execution bindings, model/tool policy, UI hints, billing, security, lifecycle, integrity, reproducibility |

---

