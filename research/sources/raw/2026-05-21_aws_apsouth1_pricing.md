# AWS ap-south-1 (Mumbai) pricing — captured 2026-05-21

Source: https://aws-pricing.com/ap-south-1.html (T3 — third-party scrape of AWS public pricing API; corroborated with vantage.sh)
Cross-check: instances.vantage.sh, AWS public price list.

## EC2 — Linux on-demand
| Instance   | $/hour  | ≈ $/month (730h) |
|------------|---------|------------------|
| t4g.small  | $0.0112 | ~$8.18          |
| t4g.medium | $0.0224 | ~$16.35         |

## 1-yr Standard RI, No Upfront, Linux
| Instance   | $/month |
|------------|---------|
| t4g.small  | $5.18   |
| t4g.medium | $10.37  |

## EBS
- gp3 storage: **$0.0912 / GB-month** ap-south-1
- gp3 IOPS above 3,000 baseline and throughput above 125 MB/s baseline metered separately

## Data transfer (Internet egress, ap-south-1)
- First 100 GB/mo aggregate: free (global AWS allowance)
- Next up to 10 TB: **$0.1093 / GB**
- Next 40 TB: $0.085 / GB
- (Mumbai egress is ~22% above us-east-1.)

STALENESS: MEDIUM. AWS price drops are infrequent but possible; re-verify at production cutover.
