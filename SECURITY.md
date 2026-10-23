# Security Considerations

This document is normative for implementations of `.jos` 2.0.0 and is the security analysis for `application/vnd.jos+json` required by RFC 6838 Section 4.6. It extends, and does not replace, Section 12 of RFC 8259. It applies to 1.0.0 documents that a 2.0.0 implementation reads.

The key words MUST, MUST NOT, SHOULD, SHOULD NOT and MAY are to be interpreted as described in RFC 2119 and RFC 8174 when, and only when, they appear in capitals.

## 1. Summary of risks

| Risk | Where it arises | Requirement |
|---|---|---|
| Active content (declared commands and invocations) | Section 3 | Never evaluated by the parser; runtime authorization is independent |
| Prompt injection | Section 4 | Delimit, constrain tools independently of model output, validate arguments |
| Time-of-check to time-of-use on `integrity.hash` | Section 5 | Canonicalize (RFC 8785), hash, verify, then execute the verified in-memory object |
| Untrusted `billing` values | Section 6 | Validate against an authoritative system |
| Server-side request forgery through URIs | Section 7 | Scheme allowlist, destination checks, redirect and size limits |
| Resource exhaustion | Section 8 | Size, depth and count limits before validation; runtime budgets above document budgets |
| Transport | Section 9 | TLS with certificate verification |
| Duplicate keys and encoding | Section 2 | Duplicate member names rejected; UTF-8 without BOM |

JOS does not employ compression. A document that arrives compressed by the transport (for example HTTP `Content-Encoding`) is subject to the decompressed-size limit in Section 8.

## 2. Parsing and encoding

A JOS document is data. An implementation MUST parse it as JSON (RFC 8259) and MUST NOT pass it to `eval()`, to a template engine, or to any interpreter of a programming language (RFC 8259 Section 12).

An implementation MUST:

1. Accept only UTF-8. A document that is not valid UTF-8 MUST be rejected (RFC 8259 Section 8.1).
2. Reject a document that starts with a byte order mark (U+FEFF). RFC 8259 Section 8.1 allows a parser to ignore a BOM; a JOS document is defined as UTF-8 without BOM, and a document with a BOM is not a JOS document.
3. Reject a document whose top-level value is not an object.
4. Reject a document in which any object has two members with the same name, at any depth. RFC 8259 Section 4 says only that names SHOULD be unique, and parsers that accept duplicates differ in the member they keep (first, last, or both). That difference allows a validator and an executor to read different values from the same bytes. RFC 8785 Section 3.1 also requires that duplicate names do not occur in the data that is canonicalized.
5. Treat member names as case-sensitive, and MUST NOT rewrite member names while parsing.
6. Reject numbers that cannot be represented as IEEE 754 double-precision values in any member that participates in `integrity.hash` (RFC 8785 Section 3.1). Large integers SHOULD be carried as strings.
7. Validate the normalized document (SPEC-2.0 Section 2.4) against the JOS JSON Schema before any interpretation of its contents. Schema validation is necessary and is not sufficient: it does not establish authorization (Section 3).
8. Apply the limits in Section 8 before validation, so that validation cannot be used to exhaust resources.

Unknown root members that do not start with `x-` make a document invalid. Members that start with `x-` and members of unknown profiles MUST be preserved, MUST be included in the canonical hash, and MUST NOT be interpreted.

## 3. Active content: declarative execution

RFC 6838 Section 4.6 requires an analysis to state whether the media type employs active content. JOS does not execute anything: a JOS document is not a program, and parsing or validating it MUST NOT run anything. A JOS document does declare the following members, which name things a runtime can execute or call. They are declarations of intended execution, and they are the active content of this media type.

| Member | What it declares |
|---|---|
| `orchestration.definitions.<name>` with `type` `shell` and `command` | A command line to run |
| `execution.run`, with `execution.engine` `shell` | An argument vector (array), or a command line (string, only with `execution.shell` `true`) |
| `execution.shell` | Whether a command line is interpreted by a shell |
| `execution.flow[].invoke` | Another artifact to invoke (1.0.0 alias of `orchestration.flows.main`) |
| `orchestration.definitions.<name>` with `type` `jos` and `artifact`, `use` | Another document to load and run |
| `orchestration.definitions.<name>` with `type` `http` and `url`; `execution.bindings.mcp`, `execution.bindings.a2a` | A network endpoint to call |
| `lifecycle.on_install`, `lifecycle.on_remove` | An artifact to invoke at install or removal |
| `persona.system_prompt`, `persona.rules`, `prompt` | Text that a language model receives as instructions |

Requirements:

1. A parser, a validator, a normalizer and a hasher MUST NOT evaluate, execute, resolve or fetch any of these members.
2. A declaration is not an authorization. The presence of a command, an invocation, a permission or a tool in a document MUST NOT cause a runtime to run, call or grant it. `security.permissions`, `tool_policy`, `guardrails` and `execution.budget` describe requirements or restrictions. They do not perform authentication and do not grant authorization.
3. Runtime, tenant, user, operating-system, network and platform policy takes precedence over declarations in the document. A document MUST NOT be able to widen policy. In a `.jos/` directory chain, a child document MUST NOT widen its parent (SPEC-2.0 Section 9.2).
4. Before running anything declared in a document, a runtime MUST establish, independently of the document: caller authorization; tenant and runtime isolation; the command or tool allowlist; filesystem scope; environment variables and secrets exposed (`execution.env` is an allow-list of names, default `PATH`); network egress policy; resource budgets; approval requirements. If any of them cannot be established, the runtime MUST NOT run the declaration (fail closed). A document whose `requires[]` the runtime cannot satisfy is not run (SPEC-2.0 Section 6.6, exit code 5).
5. A runtime SHOULD run `shell` engine declarations as an argument vector without a shell. A string `run` or `execution.shell: true` SHOULD be refused unless policy allows it explicitly.
6. A runtime SHOULD run declared commands in a sandbox with least privilege: a working directory confined to `execution.cwd`, a constrained filesystem, no network unless granted, and kill limits for time and output. When the effective tier of a step is `sandbox`, this is a requirement (SPEC-2.0 Section 6.5): the runtime confines the step or refuses the run (exit code 5).
7. A runtime MUST treat a document that arrives from a source it has not authenticated as untrusted, including documents referenced by `use`, `artifact` or `invoke`.
8. A document made for a privileged runtime MUST NOT become executable in a less constrained or unrelated tenant because it is syntactically valid.
9. `guardrails.avoid` is a defense in depth and is not a boundary: it is a pattern match on the input to an engine and does not replace the controls in item 4.

## 4. Prompt injection and model-mediated attacks

Members with natural-language content (`intention.objective`, `intention.success_criteria`, `persona.*`, `meta.description`, `execution.inputs`, step `with` values, and any `x-*` data) can contain text written to change the behavior of a language model that reads them. Documents obtained from a third party are untrusted input to the model.

When document content or content produced by a step is given to a language model, an implementation SHOULD:

1. Keep trusted instructions (the runtime's system prompt and policy) and untrusted content (every document field, tool result and previous step output) in separate message roles. Untrusted content MUST NOT be concatenated into the system role.
2. Wrap each untrusted field in an explicit delimiter that the runtime generates per call, label it with its origin (document id, field path, `art_` hash), and instruct the model that the delimited text is data. The delimiter MUST NOT be a value an author can predict from the document.
3. Decide the set of tools available to a step from runtime policy and `tool_policy` intersected with the Capability, and never from model output. A tool call that names a tool outside the set MUST be refused.
4. Validate every argument that the model produces for a tool call against the tool's input schema (for a JOS step, `execution.inputs`) before the call, and reject values that do not conform.
5. Require approval (`orchestration.flows.*.gates` with `kind: human`) before an action that writes, spends, deletes, sends data outside the tenant, or runs a command.
6. Pass output of one step to another step only as delimited data (item 2), not as instructions.
7. Record in the receipt the document hash and the field paths included in each model call, so that an injection can be traced.

A mitigation in this section reduces risk and does not eliminate it. The authoritative control is item 3 together with Section 3: the model's output cannot enlarge what the runtime allows.

## 5. Integrity and time of check to time of use

`integrity.hash` detects change to a document. It is not authentication: anyone can compute a hash. `integrity.signed_by` is an identifier hint and MUST NOT be interpreted as a digital signature or as proof of identity. A signature (`integrity.signature`, with the key identifier in `integrity.signed_by`) authenticates the hash only after the verifier has chosen the algorithm itself (no member of the document selects the verification algorithm) and has obtained the public key from a trust anchor the verifier configured.

Procedure for a runtime that claims to verify `integrity.hash`:

1. Read the document bytes once into memory. All later steps use this single in-memory parse. The runtime MUST NOT re-read the file, the URL or the registry entry between verification and execution.
2. Parse; apply Section 2 (duplicate names rejected); normalize (SPEC-2.0 Section 2.4).
3. Canonicalize with the JSON Canonicalization Scheme (JCS), RFC 8785, with `integrity.hash` and `integrity.signature` set to the empty string (SPEC-2.0 Section 8.1).
4. Compute SHA-256 over the canonical UTF-8 bytes and compare it with `integrity.hash` in constant time. A mismatch is an error: exit code 3, `reason` `integrity.hash`.
5. Verify the signature when policy requires it (`security.tier: privileged`, or a registry policy).
6. Only then authorize and execute, using the object that was hashed in step 3. This follows RFC 8785 Section 5: parse and verify I-JSON, verify the data, verify the signature, and only then act on the data.

Hashing before canonicalization, hashing a different parse than the one that is executed, and verifying a copy that is later replaced are TOCTOU defects. A runtime MUST NOT execute data that it did not hash.

Scope of the hash:

- For an artifact (one document), `integrity.hash` covers the canonical document.
- For a directory (`kind: directory`), `integrity.hash` of the manifest is the directory hash of SPEC-2.0 Section 9.3: SHA-256 over the canonical map of relative path to SHA-256 of every entry of `D/.jos/` (the manifest in canonical form with `integrity.hash` and `integrity.signature` empty), excluding `logs`, `replays`, `dev` and `ai/cache`, read without following symbolic links. A kernel verifies it before running `D`. Files of `D` outside `.jos/` are not covered, including programs that the steps of `D` run. The directory hash therefore identifies the folder's documents, not what they execute, and it does not make a run reproducible: a program, script or data file outside `D/.jos/` can change after the folder is sealed and the folder still runs with the same artifact (vector `dir-sealed-external-program`). Pin such a program by content with `requires[].digest` (SPEC-2.0 Section 6.6), and do not present the `art_` of a directory run as evidence of the integrity of the programs it ran.
- A document referenced by `use` is verified before inclusion. A reference MAY pin content with `requires[].digest`. A resolved document that has no hash or digest is unverified content.
- A crystal (`kind: crystal`) served in place of an execution MUST be verified like any other document before it is served, and its `crystal.key` MUST match the step's key.

## 6. Billing and wallet data

`billing`, and any value that states prices, wallets, quotas, credits, entitlements or chargeable events, is input from the document's author and is untrusted. An implementation MUST validate such values against an authoritative system (for example the marketplace or billing service of the operator) before acting on them, and MUST NOT debit, credit, grant or price on the strength of the document alone. A document that declares a price of zero or an unlimited quota does not make the price zero or the quota unlimited.

## 7. External references and server-side request forgery

URIs in a JOS document (`jos.schema`, `type: http` definitions `url`, bindings, `use` registries, `requires[].ref`, URI values of `execution.inputs` and `execution.bindings`, and any URI in `x-*` data) are untrusted. Before dereferencing a URI an implementation MUST apply the following, and SHOULD apply them to every redirect hop:

1. Allow only schemes in an allow-list. The default allow-list is `https`. `file`, `ftp`, `gopher`, `data`, `jar` and similar schemes MUST NOT be dereferenced unless policy enables them.
2. Resolve the host name once, check the resulting address, and connect to that address (this prevents DNS rebinding). Refuse loopback addresses, link-local addresses (including cloud metadata endpoints), private ranges (RFC 1918 and unique-local IPv6) and unspecified addresses, unless policy lists the destination.
3. Refuse URIs that contain credentials. Do not forward credentials, cookies or authorization headers to a host other than the one for which they were issued, including after a redirect.
4. Limit redirects (at most 3 is RECOMMENDED) and re-apply items 1 and 2 on each hop.
5. Limit the response size and the time to complete (Section 8).
6. Do not dereference a `jos.schema` value or any other URI in order to validate a document. Validation uses the schema the validator ships or has pinned by hash.

## 8. Limits

Implementations MUST impose limits, apply them before validation, and fail closed when a limit is exceeded. RECOMMENDED starting values for a general-purpose parser, which a deployment MAY change by configuration:

| Quantity | Starting value |
|---|---|
| Document size (decompressed) | 1 MiB |
| Nesting depth | 64 |
| Length of one string | 64 KiB |
| Members in one object, elements in one array | 10 000 |
| Steps in one flow | 1 000 |
| Referenced documents resolved per run | 100 |
| Response size of one dereferenced URI | 1 MiB |

A runtime MUST enforce its own limits on cost, tokens, duration, retries, concurrency, network requests, output size and storage, whatever the document declares. A document value larger than the runtime limit does not raise the limit. In a flow, the effective limit of a step is the element-wise minimum of the step's limit, its parent's remaining budget and the Capability's budget (SPEC-2.0 Section 3.5).

## 9. Transport

A JOS document sent over a network that is not trusted SHOULD use an authenticated, integrity-protected channel: HTTPS with TLS 1.2 or later (TLS 1.3 preferred), with certificate and host name verification enabled. A client MUST NOT disable certificate verification to retrieve a document, a schema or a referenced artifact. Transport security does not replace Section 5: it protects the channel and does not establish that the document is authorized or unchanged at rest.

JOS does not provide confidentiality. A document that carries sensitive information requires external confidentiality protection (RFC 6838 Section 4.6, last item).

## 10. Dependencies and supply chain

Referenced artifacts, schemas, tools and services can be replaced or compromised. Implementations SHOULD:

- pin versions where reproducibility matters (`use: "id@version"`, `requires[].digest`, `model_policy.model_id`);
- obtain artifacts from configured registries or origins, and MUST NOT fall back silently from one source to another when a `use` does not resolve (SPEC-2.0 Section 5.3: an unresolved `use` is an error);
- verify `integrity.hash`, and the signature when policy requires it, before including a referenced artifact;
- not treat artifact identity (`id`, `art_` hash) as publisher identity.

## 11. Multi-tenancy, secrets, privacy

- A multi-tenant runtime MUST keep data, credentials, caches, tools, logs, artifacts and execution environments separate per tenant.
- Documents SHOULD NOT contain plaintext secrets. Secret references SHOULD be opaque identifiers that the runtime resolves under least privilege. Logs, receipts and telemetry SHOULD redact secrets and sensitive values.
- A document and its receipts can contain personal data. The operator is responsible for retention and access control.
- Receipts and the ledger are evidence of what ran. They do not prove that what ran was authorized.

## 12. Reporting a vulnerability

Report a security issue in the specification or in the package to jos@josfox.cloud. Do not open a public issue for an exploitable defect before the maintainers have had an opportunity to respond. Reports about an implementation go to the maintainer of that implementation.
