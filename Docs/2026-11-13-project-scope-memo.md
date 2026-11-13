# South Portland Petroleum Terminal Vessel Monitor

## Project scope memo

**Prepared:** November 13, 2026  
**Status:** Phase 1 requirements approved; architecture and geofence validation materials prepared

## Purpose

Create a public, real-time status monitor that uses vessel Automatic Identification System (AIS) data to identify commercial vessels approaching, entering, remaining at, and leaving petroleum terminals in South Portland, Maine.

The immediate public-use goal is an accessible event log showing when vessels are likely present at a terminal. The monitor is intended to help community members understand vessel activity that may coincide with petroleum transfer operations. It will not claim that cargo was transferred, that a vessel was offloaded, or that emissions occurred.

## Phase 1 objectives

Phase 1 will:

- monitor six South Portland petroleum terminals;
- identify qualifying commercial vessels using AIS data;
- record destination-supported en-route activity;
- estimate and confirm terminal arrival;
- estimate and internally confirm departure;
- publish a searchable event log;
- provide downloadable CSV/JSON data;
- preserve summarized visit history indefinitely;
- retain raw position observations for seven days;
- support moderated community corrections.

Air-quality data, odor reports, public live mapping, and notifications are deferred to Phase 2.

## Facilities in scope

The facility registry is based on the [South Portland Petroleum Terminals: Permit & License Register](https://alexanderredfield-dev.github.io/tanks/South_Portland_Terminal_Permit_Register.html).

| Facility | Address |
|---|---|
| Portland Pipe Line Corp. | 30 Hill St, South Portland, ME 04106 |
| Sprague Operating Resources LLC | 59 Main St, South Portland, ME 04106 |
| South Portland Terminal LLC / Buckeye South Portland Terminal LLC | 170 Lincoln St, South Portland, ME 04106 |
| Global Companies LLC | 1 Clark Rd, South Portland, ME 04102 |
| CITGO Petroleum Corp. | 102 Mechanic St, South Portland, ME 04106 |
| Sunoco Midstream LLC / Portland Terminals / Gulf Oil | 175 Front St, South Portland, ME 04106 |

### Geofence approach

Each facility begins with a 500-meter circular geofence centered on the geocoded address. The circles are provisional and must be visually reviewed against open basemap or satellite imagery before activation.

Two validation issues require particular attention:

1. The Sprague and South Portland Terminal centers are close enough that their 500-meter circles overlap.
2. The Global Companies address has more than one plausible map feature; its terminal center must be checked against permit or site materials.

The current registry and review map are in:

- `config/facilities.json`
- `geofences/facilities.geojson`
- `geofences/review-map.html`

The review map includes OpenStreetMap and Esri World Imagery layers. Imagery is used for review and is not intended to be redistributed as project data.

## Vessel scope

The primary event log will include commercial AIS vessel categories while excluding obvious support craft, including:

- tugs;
- pilot boats;
- workboats;
- similar service vessels.

No minimum length or tonnage threshold will be applied initially.

## Vessel matching

The system will normalize and compare AIS destination text against:

- facility names;
- operator names;
- historical names;
- abbreviations;
- terminal aliases;
- relevant port or terminal identifiers.

Destination data is often missing, abbreviated, stale, or ambiguous. When no usable destination is available, route history and movement toward a facility may still support a candidate event. Those events must be labeled below the 95-percent confidence threshold unless later evidence supports a stronger classification.

## Monitoring lifecycle

The intended lifecycle is:

```text
candidate
  → en route
  → estimated arrival
  → confirmed present
  → estimated departure
  → departed
```

### Adaptive monitoring

The system should control data usage and cost rather than poll every vessel at the same rate:

1. **Distant:** use low-frequency checks while a vessel is far from South Portland.
2. **Approaching:** use the provider ETA when available. Otherwise calculate an ETA from position, speed, and course. Increase monitoring to the fastest practical provider-supported interval when predicted arrival is within one hour.
3. **Present:** after arrival is confirmed, check the vessel every 15 minutes.

The actual interval will depend on the selected AIS provider, API limits, and available budget.

### Arrival

1. The first position inside a facility geofence is recorded as estimated arrival.
2. The next position update must still place the vessel inside the geofence to confirm presence.
3. If the vessel leaves before confirmation, the event is not treated as a completed visit unless route or destination evidence supports publishing it as an uncertain event.

### Departure

After arrival:

1. Check position every 15 minutes.
2. When the first position outside the facility geofence is observed, start a departure timer.
3. If the next 15-minute check also shows the vessel outside, confirm that it has departed.
4. If it re-enters, cancel the timer.
5. Publish the first outside observation as the estimated departure time.
6. Retain the later confirming observation internally.

This provides a public departure estimate within roughly 15 minutes of the first observed exit, subject to AIS data availability and provider update timing.

If AIS stops updating while a vessel is present, estimate departure using the last known position and expected tracking gap. Administrators may manually close unresolved visits, but must provide a reason. The administrative audit trail is retained privately.

## Public event log

### Required public fields

- vessel name;
- MMSI and/or IMO number when available;
- matched facility;
- estimated arrival time;
- estimated departure time;
- event status;
- confidence label.

### Confidence labels

The system will retain a numeric confidence score internally but show only:

- **Over 95% certain**
- **Under 95% certain**

The initial statistical or machine-learning model will use historical review data and ongoing moderated community corrections for calibration. The public interface will explain that confidence describes the AIS-based facility-visit classification, not whether petroleum was transferred or emitted.

### Public wording

The monitor should use neutral language such as:

> AIS data indicates that the vessel entered the facility geofence.

It should not state or imply:

- that the vessel definitely docked at a berth;
- that petroleum was transferred;
- that cargo was offloaded;
- that emissions occurred;
- that a health impact occurred.

## Data retention and corrections

- Summarized vessel-visit events: retained indefinitely.
- Raw AIS positions: retained for seven days.
- Community corrections: accepted through a moderated workflow.
- Administrator closures: require a reason and are recorded in an administrative-only audit history.

## Deployment and data-source requirements

The service should run in the cloud.

The AIS provider must permit:

- server-side API or stream access;
- the required raw-data retention;
- processing into derived vessel-visit events;
- public display of derived event data;
- use of vessel identity fields where displayed;
- historical review and model calibration;
- required attribution.

### AIS source options

The initial shortlist is:

1. **AISStream.io** — free advertised real-time WebSocket stream; recommended proof-of-concept source.
2. **AISHub** — real-time feed/API, subject to membership or data-sharing requirements.
3. **VesselFinder** — paid API with published credit/subscription models.
4. **MarineTraffic/Kpler** — commercial options with broad coverage and mature services.
5. **Local AIS receiver** — possible future resilience option requiring hardware and maintenance.

The source comparison is documented in `docs/ais-source-comparison.md`. No provider should be selected for production until coverage, field completeness, rate limits, outage behavior, and derived-data publication rights are verified.

## Proposed technical architecture

```text
AIS adapter(s)
  → normalized position store
  → destination/route matcher
  → adaptive scheduler
  → geofence/event state machine
  → confidence scorer
  → summarized event store
  → public API and downloadable feed
  → administrator review interface
```

The AIS adapter should be replaceable so the project can begin with a free stream and later move to a paid provider without rewriting event logic.

## Phase 1 acceptance criteria

The first implementation is ready for pilot review when it can demonstrate that:

1. destination-matched vessels are monitored less frequently while distant;
2. monitoring accelerates when ETA is within one hour;
3. first geofence entry creates an estimated arrival;
4. the next inside observation confirms presence;
5. a first outside observation starts departure timing;
6. a second outside observation 15 minutes later confirms departure;
7. re-entry cancels pending departure;
8. AIS interruption does not silently erase a present visit;
9. unresolved visits can be manually closed with a reason;
10. public records use neutral AIS-based language;
11. no public record claims that offloading or emissions occurred;
12. summarized events can be searched and downloaded.

## Immediate next steps

1. Manually review the six geofence overlays, especially Sprague, South Portland Terminal, and Global.
2. Approve or revise each facility center and 500-meter radius.
3. Run a limited AISStream.io coverage test around South Portland.
4. Compare the test against AISHub or a paid provider if coverage or licensing is inadequate.
5. Implement the normalized AIS adapter and event state machine.
6. Build a private review dashboard before publishing the first public event feed.
