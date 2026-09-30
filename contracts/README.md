# Shared SDK contract cases

Language-independent examples for the Energy Tracker Python and TypeScript clients.
Run the Python adapter with `make test-contracts`; the cases also run in the normal
test and release checks. No API token, live backend or sibling checkout is needed.

## Format and execution

`schema.json` defines fixture format version 1. Each file in `cases/` contains a
`schemaVersion` and an array of cases with globally unique IDs.

- `operation` and `input` describe a public SDK call. Bind these to the target
  language's API; they do not prescribe method names or classes. Reading values
  are decimal strings, environment values are JSON numbers, dates are offset ISO
  timestamps. Missing optional inputs mean omitted arguments.
- `request` specifies the method, API-relative path, decoded query parameters,
  required headers and body. Preserve a base URL's `/public-api/` prefix. Compare
  header names case-insensitively; additional transport headers are allowed.
  Query key order and JSON object key order are irrelevant; extra query/body
  fields and duplicate query keys are not allowed.
- Meter-reading CSV exports default to `semicolon`. Explicit `comma`, `semicolon`
  and `tab` selections override the default.
- `response` is the local server's synthetic HTTP response. Bodies use exactly
  one of `json`, UTF-8 `text`, or `base64`; `{}` means no body. A `json: null`
  body is distinct from no body. Base64 preserves exact CSV bytes, including BOM
  and line endings.
- `expected` contains either a normalized `result` or an `error`. Results use
  camelCase DTO fields, decimal strings, and `{ "base64": "..." }` for bytes.
  Void results and absent optional DTO fields are normalized to `null`.
  Errors specify a semantic category, HTTP status, API message list and, when
  present, `retryAfter` in seconds. Exception class names and local wording are
  language-specific. Assert exactly one request, including on errors/redirects.

Compare `timestamp`, `date`, `lastUpdatedAt`, `from`, `to`, `updatedAfter` and
`updatedBefore` as offset-aware instants. `Z` and equivalent offsets/fractional
spellings are interchangeable. Do not round to calendar boundaries. Compare
all other values directly, preserving decimal precision and list order.

The wire examples were checked against the Public API controllers and DTOs in
[energy-tracker-core at fcc269a06184426caf64c882291d4209be57a723](https://github.com/StefaniOSApps/energy-tracker-core/tree/fcc269a06184426caf64c882291d4209be57a723/backend/src/app/public-api).
Error/redirect/malformed-response cases additionally specify SDK behavior; their
messages are illustrative, not fixed backend wording. These mocked responses
do not verify server calculations, validation rules or authorization scopes.
Timeouts, session lifecycle and language-specific input validation remain in
each SDK's own tests.

## Reuse and versioning

This directory is the fixture source. Pin an immutable Git commit of this
repository when consuming it; do not fetch a moving `main` in SDK CI. Export
with `git archive <commit> LICENSE contracts`, retain the repository's MIT license, and
record the source commit alongside the imported files. A TypeScript repository
can vendor that snapshot and run its own HTTP test adapter entirely offline.
Update the source fixtures here and import updates explicitly into consumers.

`schemaVersion` versions the fixture format, independently of Python releases.
The pinned Git commit identifies the exact case revision. Unknown schema
versions and operations must fail rather than be skipped. Fixtures are included
in the source distribution, but are not a runtime dependency or part of the wheel.
