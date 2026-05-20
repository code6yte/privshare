# API.md

## Routes

## `GET /`

Shows upload form.

## `POST /upload`

Accepts multipart form data.

Fields:

| Field | Type | Required | Description |
|---|---|---:|---|
| `file` | file | yes | Uploaded file |
| `password` | string | yes | Password used for encryption |
| `expiry_hours` | number | no | Link expiry in hours |

Response:

- Renders success page with unique link.

## `GET /file/<token>`

Shows password form for the receiver.

## `POST /file/<token>`

Fields:

| Field | Type | Required | Description |
|---|---|---:|---|
| `password` | string | yes | Password needed for decryption |

Response:

- If correct: decrypted file download
- If incorrect: invalid password message
- If expired: expired message

## `GET /health`

Returns JSON health check.

Example:

```json
{
  "status": "ok",
  "service": "privshare"
}
```

## CLI Commands

See [`CLI_AGENTS.md`](CLI_AGENTS.md).
