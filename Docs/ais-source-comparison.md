# AIS Source Comparison

Status: initial research, 2026-11-13

The decisive requirement is not merely live position access. The provider must support lawful server-side collection, short-term raw retention, derived event processing, and publication of a public event log.

## Shortlist

| Option | Delivery | Cost posture | Strengths | Risks / open checks | Recommendation |
|---|---|---:|---|---|---|
| AISStream.io | WebSocket stream | Free advertised | Real-time stream, geographic subscriptions, easy fit for a server-side collector | Coverage in Casco Bay, service limits, historical access, and derived-data redistribution terms must be confirmed | Best prototype baseline |
| AISHub | API / feed | Free for contributing stations | JSON/XML/CSV real-time data; useful if a local receiver contributes | Access generally depends on membership/data sharing; rate limit and public-derived-data rights need confirmation | Good supplementary option |
| VesselFinder | REST/API subscriptions | Paid; published credit and subscription models | Straightforward API, vessel/position endpoints, established coverage | Per-call economics can be poor for frequent polling; derived-public-feed terms need confirmation | Low-volume paid fallback |
| MarineTraffic / Kpler | API, feed, data services | Commercial | Broad terrestrial/satellite network and mature data products | Likely overkill for six local geofences; pricing and redistribution are contract-specific | Reliability fallback |
| Local AIS receiver + aggregator | NMEA/JSON receiver feed | Hardware plus hosting | Local control and predictable local observations | Requires hardware, antenna placement, maintenance, and may miss vessels transmitting outside terrestrial range | Future resilience option |

## Recommended evaluation order

### 1. AISStream.io proof of concept

Subscribe only to a bounding box around South Portland and filter by the six circles. Record:

- message freshness
- percentage of messages with vessel name, IMO, destination, speed, and course
- update cadence for vessels near the terminals
- coverage gaps
- reconnect behavior
- provider terms for derived event publication

This should be tested before committing to a paid plan.

### 2. AISHub as an independent comparison

Use the same test window and compare vessel identity, position freshness, destination completeness, and missing-message behavior. Do not assume it can be used without satisfying its station-sharing or membership requirements.

### 3. Paid fallback

Request a written quote and terms from VesselFinder or MarineTraffic/Kpler for:

- six small geographic areas
- real-time positions
- ETA/destination fields
- at least seven days of raw retention
- public display of derived arrival/departure events
- API rate limits supporting 15-minute post-arrival checks

## Cost-control design

The application should not repeatedly request all local traffic at the same rate. Use:

1. low-frequency destination/route screening while distant;
2. higher frequency only when ETA is within one hour;
3. 15-minute checks after confirmed arrival;
4. a provider webhook/event feed when available;
5. deduplication by MMSI and observation timestamp.

For a stream provider, “polling” is implemented as local state evaluation rather than repeated API requests. For a request/response provider, the scheduler must enforce per-provider quotas.

## Terms and attribution checklist

Before production use, confirm in writing:

- commercial or nonprofit use is permitted;
- derived event data may be published publicly;
- vessel identity fields may be displayed;
- raw position retention for seven days is permitted;
- historical data may be used for model calibration;
- required attribution and links;
- API key may be used only server-side;
- rate limits and outage behavior;
- no automatic resale or redistribution of raw AIS data is occurring.

## Sources

- AISStream: https://aisstream.io/ and https://aisstream.io/documentation
- AISHub: https://www.aishub.net/ and https://www.aishub.net/api
- VesselFinder API: https://api.vesselfinder.com/ and https://www.vesselfinder.com/vessel-positions-api
- MarineTraffic/Kpler data services: https://www.kpler.com/product/maritime/data-services
