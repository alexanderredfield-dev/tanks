# South Portland Tanker Monitor — Phase 1 Architecture

Status: design baseline, 2026-11-13

## Goal

Publish an auditable public event log showing when qualifying commercial vessels are likely en route to, present at, and departing from six South Portland petroleum terminals.

The system reports AIS-derived vessel presence only. A visit does not prove cargo transfer, petroleum offloading, or an emissions event.

## Phase 1 scope

- Six terminals in `config/facilities.json`.
- 500-meter circular geofences, pending visual approval.
- Commercial AIS vessel classes, excluding obvious tug, pilot, workboat, and similar support craft.
- Public searchable event log plus CSV/JSON download.
- En-route records when destination or route evidence supports a facility match.
- Estimated arrival, confirmed arrival, estimated departure, and internal departure confirmation.
- Indefinite retention of summarized events.
- Seven-day retention of raw position observations.
- Cloud deployment.

Air-quality, odor, live map, and notifications are intentionally deferred to Phase 2.

## Event lifecycle

```text
candidate
  -> en_route
  -> estimated_arrival
  -> present_confirmed
  -> estimated_departure
  -> departed_confirmed
```

### Candidate and destination matching

The matcher normalizes AIS destination text against facility names, aliases, port/terminal identifiers, and known historical variants. If destination is absent or ambiguous, route history and motion toward a facility may support an under-95%-confidence candidate.

Destination matching is advisory. Geofence observations are the basis for presence.

### Arrival

1. The first position inside a facility's circle is an **estimated arrival**.
2. The next inside observation confirms presence.
3. If the vessel exits before confirmation, do not publish a completed visit unless destination or route evidence supports it.

### Adaptive polling

The scheduler has three broad modes:

| Mode | Trigger | Behavior |
|---|---|---|
| `distant` | No credible arrival within one hour | Low-frequency checks to control cost |
| `approaching` | Provider ETA, or calculated ETA, is within one hour | Fastest practical provider-supported interval |
| `present` | Arrival is confirmed | Position checks every 15 minutes |

The selected AIS source determines the actual floor, rate limits, and whether provider ETA/webhook events exist.

### Departure

1. In `present`, check every 15 minutes.
2. The first outside observation starts a departure timer.
3. If the next 15-minute observation is still outside, publish the first outside observation as **estimated departure**.
4. Keep the second observation as the internal confirmation time.
5. If the vessel re-enters, cancel the timer.

If AIS stops updating, estimate departure from the last position and expected tracking gap. Administrators may close an unresolved visit with a required reason; that administrative audit trail is not public.

## Confidence

The confidence model should retain a numeric score internally but expose only:

- `over_95_percent`
- `under_95_percent`

Initial features can include vessel class, destination match quality, route consistency, geofence entry/confirmation, position age, and polling/source reliability. Historical review plus ongoing moderated community corrections provide calibration data.

## Suggested service boundaries

```text
AIS adapter(s)
  -> normalized position store (7-day TTL)
  -> destination/route matcher
  -> adaptive scheduler
  -> geofence/event state machine
  -> confidence scorer
  -> summarized event store
  -> public API + downloadable feed
  -> admin review/correction interface
```

Keep the AIS adapter behind an interface so a free WebSocket source can be replaced by a paid API without changing event logic.

## Public event fields

Required:

- vessel name and MMSI/IMO when available
- matched facility
- estimated arrival
- estimated departure
- confidence label
- event status

Recommended provenance fields:

- source name
- first/last observation time
- confirmation time
- destination as reported
- source position age
- correction status

## Acceptance tests

1. A destination-matched vessel is low-frequency polled while distant.
2. Polling accelerates when ETA is within one hour.
3. First geofence entry creates an estimated arrival.
4. A second inside observation confirms presence.
5. An outside observation starts, and a second outside observation 15 minutes later confirms, departure.
6. Re-entry cancels pending departure.
7. An AIS outage does not silently erase a present visit.
8. Manual closure requires a reason and preserves the administrative audit record.
9. Public records never claim that offloading or emissions occurred.
