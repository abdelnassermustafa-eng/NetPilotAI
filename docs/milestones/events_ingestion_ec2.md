# NetPilot AI v2 — Events Ingestion (EC2)

## Status
✅ COMPLETE (Read-only)

## Scope
- AWS EventBridge → Lambda → DynamoDB
- EC2 instance lifecycle events
- Account + region scoped
- Cursor-based pagination
- Single-event drill-down

## API Endpoints
- GET /api/v1/observability/events
- GET /api/v1/observability/events/{event_id}

## UI
- Observability → Events tab
- Timeline list
- Event details panel
- Back-to-list navigation

## Guarantees
- Read-only
- No infrastructure mutation
- Safe for production visibility

## Notes
- Filters planned (service, resource_id)
- Alerting and automation deferred
