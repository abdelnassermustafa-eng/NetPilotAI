# NetPilot AI v2 — Events Ingestion Milestone (EC2)

**Status:** ✅ COMPLETED & VERIFIED  
**Date:** 2026-01-12  
**Scope:** EC2 lifecycle events (start / stop / reboot)  
**Mode:** Read-only, production-backed

---

## Objective

Implement real AWS Events ingestion to establish a truthful observability foundation for NetPilot AI v2.

---

## Implemented Components

### DynamoDB
- Table: `netpilot_events`
- PK: `ACCOUNT#{account_id}#REGION#{region}`
- SK: `EVENTTIME#{event_time_utc}#ID#{event_id}`
- GSIs:
  - `GSI1_ResourceTime`
  - `GSI2_ServiceTime`
- Billing: On-demand
- Deletion protection: Enabled

### Ingestion Pipeline
- Lambda: `netpilot-events-ingest`
- IAM: Least privilege
  - Allow: PutItem, logging
  - Deny: Update/Delete/BatchWrite
- Idempotent writes
- Canonical schema (`schema_version = v1`)

### Event Source
- EventBridge rule: `NetPilot-EC2-StateChange`
- Source: `aws.ec2`
- Detail type: EC2 Instance State-change Notification

---

## Validation Performed

- Temporary EC2 instance launched via CLI
- Instance started, stopped, and restarted
- DynamoDB event count increased from 1 → 7
- Multiple real event_ids and timestamps observed
- Test instance terminated after validation

---

## Truth Guarantees

The system:
- Ingests real EC2 events
- Stores immutable, append-only records
- Supports read-only consumption

The system does not yet:
- Replay historical events
- Provide correlation or alerts
- Expose Events via API or UI

---

## Roadmap Impact

- Events (EC2): ✅ Implemented
- Metrics: Unblocked
- Alerts: Now credible

---

## Milestone Declaration

Events ingestion is LIVE (EC2 scope) in NetPilot AI v2.
