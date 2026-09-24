# Security Considerations

JOS is a declarative format for describing intended AI and automation behavior. That makes untrusted JOS content more security-sensitive than ordinary passive configuration.

This document is normative for JOS 1.0.0 implementations.

## Trust model

A JOS document is **untrusted input** unless a runtime has independently established its provenance and authorization.

A JOS document MUST NOT be able to grant itself privileges.

Runtime, tenant, user, operating-system, network, and platform policy MUST take precedence over declarations inside the document.

## Parsing

Implementations MUST:

- parse JOS as JSON data, never as source code;
- enforce UTF-8;
- reject duplicate object member names for conformance processing;
- validate the document against the applicable JOS schema before execution;
- impose reasonable limits on document size, nesting depth, strings, arrays, and object members.

## Command and code execution

A JOS document may contain declarations that reference shell commands, scripts, HTTP endpoints, JOS artifacts, tools, or services.

Such references are not authorization.

Before execution, runtimes MUST independently validate:

- caller authorization,
- tenant and runtime isolation,
- tool or command allowlists,
- filesystem scope,
- environment variables and secret exposure,
- network egress policy,
- resource budgets,
- approval requirements.

Shell-backed execution SHOULD occur in a sandbox with least privilege and a constrained filesystem and network environment.

## Prompt injection and model-mediated attacks

Natural-language members may contain malicious or adversarial instructions.

When JOS content is passed to a language model, implementations SHOULD:

- preserve provenance between trusted system instructions and untrusted document content;
- avoid concatenating untrusted fields into higher-privilege instructions without delimitation;
- constrain tool access independently of model output;
- validate model-produced arguments before tool execution;
- require approval for sensitive actions when appropriate.

## External references and SSRF

URIs in a JOS document are untrusted.

Before dereferencing a URI, an implementation SHOULD defend against:

- SSRF,
- redirects to disallowed destinations,
- loopback and link-local access,
- private-network traversal,
- DNS rebinding,
- credential forwarding,
- unsupported URI schemes,
- excessive redirects or response sizes.

## Dependencies and supply chain

Dependencies, referenced artifacts, schemas, tools, and services can be replaced or compromised.

Implementations SHOULD:

- pin versions where reproducibility matters;
- verify integrity metadata when available;
- obtain artifacts from trusted registries or origins;
- apply independent authorization before installation or invocation;
- avoid interpreting artifact identity as publisher identity.

## Integrity

`integrity.hash` can detect document changes when computed as defined by the JOS specification.

A hash is not an authentication mechanism.

The JOS 1.0.0 `signed_by` member is an identifier hint only and MUST NOT be interpreted as a digital signature.

## Billing and resource exhaustion

Billing values are untrusted. Implementations MUST validate pricing, wallets, quotas, credits, and chargeable events against authoritative systems.

Runtimes MUST enforce their own resource limits even if a document declares larger limits.

Relevant limits include:

- total cost,
- per-call cost,
- tokens,
- execution duration,
- retries,
- concurrency,
- network requests,
- output size,
- storage.

## Authentication and authorization

The JOS `security` and `tool_policy` objects describe requirements or restrictions. They do not perform authentication and they do not grant authorization.

A runtime MUST fail closed when required authorization cannot be established.

## Multi-tenant isolation

A multi-tenant JOS runtime MUST maintain tenant isolation for data, credentials, caches, tools, logs, artifacts, and execution environments.

An artifact created for an administrative or privileged runtime MUST NOT become executable in a less constrained or unrelated tenant merely because it is syntactically valid JOS.

## Secrets

JOS documents SHOULD NOT contain plaintext secrets.

Secret references SHOULD use opaque identifiers resolved by the runtime under least-privilege access controls.

Logs and telemetry SHOULD redact secrets and sensitive values.

## Network transport

JOS documents transmitted over untrusted networks SHOULD use an authenticated, integrity-protected transport such as HTTPS/TLS.

Transport security does not replace document authorization or integrity verification.
