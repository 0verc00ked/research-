# Oracle Cloud Always Free — captured 2026-05-21

Source: https://docs.oracle.com/en-us/iaas/Content/FreeTier/freetier_topic-Always_Free_Resources.htm (T3 primary)
Plus search corroboration on Mumbai region availability.

## Resources (still offered as of May 2026)
- 2× VM.Standard.E2.1.Micro (AMD), 1/8 OCPU + 1 GB RAM each
- Ampere A1 (Arm): up to 4 OCPU + 24 GB RAM total, across up to 4 VMs
- 200 GB block storage total
- 20 GB object storage total
- 10 TB/month outbound

## Mumbai (ap-mumbai-1) availability
Oracle's official line: "Free Tier is available in all regions where commercial OCI is available." Mumbai is commercial-OCI. No public-facing line excluding Mumbai. However A1 Arm capacity in Mumbai is documented as chronically constrained ("out of host capacity" is the common error). Not formally a separate-region exclusion, but a practical one.

## Reclamation clause (the key risk)
Quoted: "Idle Always Free compute instances may be reclaimed by Oracle." Trigger: over a 7-day window, all of {CPU p95 < 20%, network < 20%, memory < 20% (A1 only)}. No mandatory notice period documented; reclamation is at Oracle's discretion.

## Implication for trading workload
A correctly-running trading bot (cron pulling prices, LLM call cadence, WS keepalive) will typically clear the 20% network or memory bar, so idle reclamation is not the dominant risk. The dominant risk is:
1. Capacity unavailable when re-provisioning after a failure (no SLA).
2. Oracle's general right to terminate Free Tier accounts without compensation.
3. No support entitlement.

Verdict: Real, but NOT contractually durable enough for production capital. Acceptable for paper/G1 stage with a hot-standby on AWS.

STALENESS: LOW-MEDIUM.
