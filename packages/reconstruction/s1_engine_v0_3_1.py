#!/usr/bin/env python3
"""
S1/S1b reconstruction engine — v0.3.1 PROPOSED  (M-09 / M-10 / M-05-S1b; successor to v0.2.2)

v0.2.2 (sha256 4ad4ada3…) remains the reproduced full-corpus baseline (66/66 providers
byte-identical across two machines, 3 Sep 2026). v0.3 supersedes it for NEW runs only.

v0.3.1 (4-5 Sep 2026) supersedes v0.3 (sha256 fe5f413b…, never run on real data) by ONE additive
output: per provider, s1_parent_provenance.jsonl — one row per folded SessionSeries parent that
carries an @id, with its page-level provenance — so a lineage pack can bind an INHERITED (or
BOTH_EQUAL / CHILD_OVERRIDES) value to the parent's served bytes, not just to a parent @id.
s1_records.jsonl is unchanged from v0.3 (= v0.2.2 + page_index + page_sha256).

New in v0.3
  * Page-level provenance. Corpus.pages() yields (page_index, page_sha256, body); every
    surviving item's provenance gains "page_index" and "page_sha256" — the sha256 of the
    exact served bytes that pages.csv verified. This is what a lineage pack binds to.
  * S1b expansion is WIRED (v0.2.2 defined expand() but never ran it). Windows are
    vintage-anchored per SOURCE-CONFLICT-M04-A: a horizon of H days covers calendar days D
    with vintage <= D < vintage + H, intersected with [startDate, endDate] (endDate
    inclusive, per schema.org). Never anchored at the schedule's own startDate.
  * exceptDate honoured (date form removes that local date; date-time form removes the
    occurrence whose UTC instant matches, naive date-times read in scheduleTimezone).
    repeatCount honoured (counted from startDate, only in-window occurrences emitted).
    repeatFrequency other than weekly (absent / P1W / P7D) => typed skip, never guessed.
    Cross-midnight endTime handled. Occurrences carry start/end in local and UTC.
  * Listed-child concordance: each occurrence records whether an explicit ScheduledSession
    with the same UTC start (minute precision) exists under the same superEvent; the
    reverse count (listed children in-window without a schedule-derived occurrence) is
    reported per provider. Both directions are descriptive, not a gate.
  * Per-provider s1b_occurrences.jsonl + s1b_summary.json; rollup "s1b" block; receipt
    binding for every S1b output; horizon parameters recorded with their status label
    (default PROVISIONAL-M05-D-HORIZON until the M05-D-HORIZON motion is ratified).
  * --selftest: fixture-built, no inputs needed. Checks DST (Europe/London, 25 Oct 2026),
    anchoring, exceptDate, repeatCount, repeatFrequency guard, cross-midnight, readiness,
    page provenance, concordance, exclusion of INCOMPLETE feeds, receipt binding, and
    byte-level determinism across two runs.
  * DST handling is standards-based and stated: local wall times are resolved by zoneinfo under
    PEP 495 with fold=0 — a non-existent spring-gap time maps with the pre-transition offset, an
    ambiguous autumn time maps to its FIRST occurrence. Fixtures FX-02/FX-03 (Europe/London,
    29 Mar and 25 Oct 2026) assert exactly this. The horizon is a scientific parameter, not a
    DST-coverage device (SOURCE-CONFLICT-M04-A); the register's fallback — a PROVISIONAL 28-day
    vintage-anchored window pending task definitions — is the default here, and re-expansion at
    the ratified horizon is one CLI flag.
  * Unchanged from v0.2.2 (so census / lineage / resolution totals reproduce exactly):
    fold semantics, reconstruct(), readiness()/READY_REQ, schedule_census(), zip/receipt
    verification, ledger pairing, cross-kind skip, sealed-vintage refusal, OA-1.

Provenance: Michael's stream, 4 Sep 2026, AI-assisted; PROPOSED pending review.
"""
from __future__ import annotations
import argparse, contextlib, csv, hashlib, io, json, re, shutil, sys, tempfile, zipfile
from collections import Counter, defaultdict
from datetime import date, datetime, time, timedelta, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

ENGINE_VERSION = "s1-engine-0.3.1-PROPOSED"
SUPERSEDES = {"s1_engine_v0_3.py": "fe5f413bb08a857e9ea3d43826322c557fbda682bcb2956f32013e6fc30f5031"}
PREDECESSOR = {"engine": "s1-engine-0.2.2-PROPOSED",
               "engine_sha256": "4ad4ada3e0dba68ba05fa74ff55b4bede00ad437671e4c342ec03c3d4af60dd5"}
POLICY_ID = "M06-INHERITANCE-v0.2-UNRATIFIED"
INTERP_ID = "M05-REGISTER-v0.2-UNRATIFIED"
HORIZON_STATUS_DEFAULT = "PROVISIONAL-M05-D-HORIZON"
WINDOW_RULE = ("SOURCE-CONFLICT-M04-A: vintage-anchored; horizon H covers calendar days D with "
               "vintage <= D < vintage+H, intersected with [startDate, endDate] (endDate inclusive)")
CONCORDANCE_RULE = ("listed_child_match: an explicit ScheduledSession under the same superEvent shares the "
                    "occurrence's UTC start at minute precision; listed_children_in_window: children of series "
                    "with >=1 expanded schedule whose local start date lies inside the horizon window; "
                    "_unmatched: those with no schedule-derived occurrence at the same UTC minute. Descriptive only.")
SEALED_VINTAGE_PATTERNS = (re.compile(r"(^|[/_-])H3([/_-]|$)", re.I),)

INHERITABLE_WHOLE = ["name", "location", "organizer", "activity", "category",
                     "offers", "url", "attendeeInstructions", "level", "ageRange"]
CHILD_ONLY = ["startDate", "endDate", "duration", "maximumAttendeeCapacity",
              "remainingAttendeeCapacity", "@id", "identifier"]
DAY_MAP = {"https://schema.org/" + d: i for i, d in enumerate(
    ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"])}
for d, i in list(DAY_MAP.items()):
    DAY_MAP[d.rsplit("/", 1)[1]] = i
WEEKLY_FREQ = {None, "", "P1W", "P7D"}

PARENT_KIND = re.compile(r"sessionseries", re.I)
CHILD_KIND = re.compile(r"scheduledsession", re.I)

sha = lambda b: hashlib.sha256(b).hexdigest()
UTC = timezone.utc


def refuse_sealed(tokens):
    for t in tokens:
        for pat in SEALED_VINTAGE_PATTERNS:
            if pat.search(str(t)):
                sys.exit(f"REFUSED: '{t}' matches a sealed-vintage pattern (H3). "
                         f"Development runs use exposed vintages only (Fahmi §4 / F-04).")


# ---------------- corpus access: zip-native, receipt-verified ----------------
class Corpus:
    """Reads pages from the delivery zip; verifies each against pages.csv."""

    def __init__(self, zip_path, pages_csv, ledger_csv, snapshot, strict=True, terminals_csv=None):
        self.zf = zipfile.ZipFile(zip_path)
        self.snapshot = snapshot
        self.strict = strict
        self.expected = {}          # (feed_id, page_index) -> sha256 from pages.csv
        self.quarantined = {}       # feed_id -> reason
        self.stats = Counter()
        with open(pages_csv, newline="", encoding="utf-8-sig") as f:
            for row in csv.DictReader(f):
                if row.get("snapshot_id") and snapshot and row["snapshot_id"] != snapshot:
                    continue
                h = (row.get("sha256") or "").strip().lower()
                if not h:
                    self.stats["ledger_failed_fetch_rows"] += 1   # failed fetches carry no hash
                    continue
                self.expected[(row["feed_id"], int(float(row["page_index"])))] = h
        self.feeds = []             # ledger rows
        with open(ledger_csv, newline="", encoding="utf-8-sig") as f:
            self.feeds = list(csv.DictReader(f))
        self.excluded_incomplete = {}
        if terminals_csv:
            with open(terminals_csv, newline="", encoding="utf-8-sig") as f:
                for row in csv.DictReader(f):
                    if (row.get("delivery") or "").upper() != "COMPLETE":
                        self.excluded_incomplete[row["feed_id"]] = row.get("terminal", "?")
        self.members = {}
        pat = re.compile(r"raw/(?P<feed>[^/]+)/page_(?P<idx>\d+)\.bytes$")
        for name in self.zf.namelist():
            m = pat.search(name.replace("\\", "/"))
            if m:
                self.members[(m.group("feed"), int(m.group("idx")))] = name
        for name in self.zf.namelist():
            if name.replace("\\", "/").endswith("manifest.json"):
                try:
                    man = json.loads(self.zf.read(name))
                    if snapshot and man.get("snapshot_id") not in (None, snapshot):
                        sys.exit(f"REFUSED: archive manifest snapshot_id "
                                 f"'{man.get('snapshot_id')}' != --snapshot '{snapshot}'.")
                    self.manifest = man
                except Exception:
                    self.manifest = None
                break
        else:
            self.manifest = None

    def pages(self, feed_id):
        """Yield (page_index, page_sha256_of_served_bytes, body_dict) for a feed, in page order."""
        idxs = sorted(i for (f, i) in self.members if f == feed_id)
        for i in idxs:
            name = self.members[(feed_id, i)]
            blob = self.zf.read(name)
            got, want = sha(blob), self.expected.get((feed_id, i))
            if want is None:
                self.stats["pages_missing_from_csv"] += 1
                self._fail(feed_id, f"page {i} absent from pages.csv")
                return
            if got != want:
                self.stats["pages_hash_mismatch"] += 1
                self._fail(feed_id, f"page {i} sha256 mismatch (got {got[:12]}, ledger {want[:12]})")
                return
            self.stats["pages_verified"] += 1
            if not blob:
                self.stats["pages_empty_body"] += 1
                continue
            if blob[:2] == b"\x1f\x8b":
                import gzip
                try:
                    blob = gzip.decompress(blob)
                    self.stats["pages_gzip_decompressed"] += 1
                except Exception as e:
                    self.stats["pages_unparseable"] += 1
                    self._fail(feed_id, f"page {i} verified but gzip-undecodable ({e})")
                    return
            try:
                body = json.loads(blob)
            except Exception as e:
                self.stats["pages_unparseable"] += 1
                self._fail(feed_id, f"page {i} verified but unparseable "
                                    f"({type(e).__name__}; first bytes {blob[:16]!r})")
                return
            yield i, got, body

    def _fail(self, feed_id, reason):
        if self.strict:
            print(f"VERIFICATION FAILURE (fail-closed): feed '{feed_id}': {reason}. "
                  f"Re-run with --continue-on-mismatch to quarantine and proceed. [exit 13]",
                  file=sys.stderr)
            raise SystemExit(13)
        self.quarantined[feed_id] = reason


# ---------------- Stage A: S0 fold (v0.2.2 semantics + page provenance) -----
def fold(pages_iter):
    state, tomb, prov, violations = {}, set(), {}, 0
    n_pages = 0
    for page_index, page_sha, body in pages_iter:
        n_pages += 1
        lic = body.get("license")
        last_mod = None
        for it in body.get("items", []):
            iid = it.get("id")
            if iid is None:
                continue
            m = it.get("modified")
            if last_mod is not None and m is not None and m < last_mod:
                violations += 1
            last_mod = m if m is not None else last_mod
            if it.get("state") == "deleted":
                state.pop(iid, None); tomb.add(iid)
            else:
                state[iid] = it
                prov[iid] = {"rpde_id": iid, "modified": it.get("modified"),
                             "kind": it.get("kind"), "page_license": lic,
                             "page_index": page_index, "page_sha256": page_sha}
    return state, tomb, prov, violations, n_pages


# ---------------- Stage B: S1 inheritance (unchanged from v0.2.2) -----------
def super_id(v):
    if isinstance(v, str): return v
    if isinstance(v, dict): return v.get("@id")
    return None


def reconstruct(children, parents_by_atid, prov, parent_feed):
    out, res_c, fld_c = [], Counter(), Counter()
    for iid, it in children.items():
        d = it.get("data") or {}
        rec = {"item_id": iid, "@id": d.get("@id"), "type": d.get("@type"),
               "provenance": prov.get(iid), "fields": {}, "lineage": {}}
        sid = super_id(d.get("superEvent"))
        parent = parents_by_atid.get(sid) if sid else None
        rec["parent_resolution"] = ("NO_SUPEREVENT" if sid is None else
                                    "RESOLVED" if parent is not None else
                                    "PARENT_NOT_IN_SAMPLE")
        if parent is not None:
            rec["parent_@id"] = sid
        res_c[rec["parent_resolution"]] += 1
        pd = (parent.get("data") if parent else None) or {}
        for f in CHILD_ONLY:
            if f in d:
                rec["fields"][f] = d[f]
                rec["lineage"][f] = {"class": "ON_CHILD", "rule": "M06:child-only"}
        for f in INHERITABLE_WHOLE:
            c_has, p_has = f in d and d[f] is not None, f in pd and pd[f] is not None
            if c_has and p_has:
                cls = "BOTH_EQUAL" if d[f] == pd[f] else "CHILD_OVERRIDES"; rec["fields"][f] = d[f]
            elif c_has:
                cls = "ON_CHILD"; rec["fields"][f] = d[f]
            elif p_has and rec["parent_resolution"] == "RESOLVED":
                cls = "INHERITED"; rec["fields"][f] = pd[f]
            elif rec["parent_resolution"] == "RESOLVED":
                cls = "SOURCE_ABSENT"
            else:
                cls = "UNRESOLVABLE_PARENT_UNAVAILABLE"
            rec["lineage"][f] = {"class": cls,
                                 "rule": f"{POLICY_ID}:SessionSeries->ScheduledSession:{f}",
                                 **({"parent_@id": sid, "parent_feed": parent_feed}
                                    if cls == "INHERITED" else {})}
            fld_c[(f, cls)] += 1
        out.append(rec)
    return out, res_c, fld_c


# ---------------- Stage C: schedule census (unchanged) + S1b expansion (new) --
READY_REQ = ("startDate", "endDate", "startTime", "endTime", "byDay", "scheduleTimezone")
_DATE_RE = re.compile(r"^(\d{4})-(\d{2})-(\d{2})$")
_TIME_RE = re.compile(r"^(\d{1,2}):(\d{2})(?::(\d{2}))?")
_DT_RE = re.compile(r"^(\d{4})-(\d{2})-(\d{2})[T ](\d{2}):(\d{2})(?::(\d{2})(?:\.(\d+))?)?"
                    r"\s*(Z|z|[+-]\d{2}:?\d{2})?$")


def readiness(s):
    if not isinstance(s, dict): return ["not-an-object"]
    if (s.get("@type") or "").lower() == "partialschedule":
        return ["PartialSchedule-never-expanded(OA-1)"]
    return [k for k in READY_REQ if not s.get(k)]


def schedule_census(parent_state, census):
    for v in parent_state.values():
        s = (v.get("data") or {}).get("eventSchedule")
        for sch in (s if isinstance(s, list) else [s] if s else []):
            miss = readiness(sch)
            census["schedules_total"] += 1
            if miss == ["PartialSchedule-never-expanded(OA-1)"]:
                census["partial_schedule"] += 1
            elif miss:
                census[f"not_ready:{','.join(sorted(miss))}"] += 1
            else:
                census["full_schedule_ready"] += 1


def parse_date(v):
    """schema.org Date (or the date part of a DateTime) -> date, else None."""
    if not isinstance(v, str): return None
    m = _DATE_RE.match(v[:10])
    if not m: return None
    try:
        return date(int(m.group(1)), int(m.group(2)), int(m.group(3)))
    except ValueError:
        return None


def parse_time(v):
    if not isinstance(v, str): return None
    m = _TIME_RE.match(v.strip())
    if not m: return None
    hh, mm, ss = int(m.group(1)), int(m.group(2)), int(m.group(3) or 0)
    if not (0 <= hh <= 23 and 0 <= mm <= 59 and 0 <= ss <= 59): return None
    return time(hh, mm, ss)


def parse_datetime(v, default_tz):
    """ISO 8601 date-time -> aware datetime (naive read in default_tz), else None.
    Written by hand so behaviour is identical on Python 3.9 - 3.12 (fromisoformat differs)."""
    if not isinstance(v, str): return None
    m = _DT_RE.match(v.strip())
    if not m: return None
    y, mo, d, hh, mi = (int(m.group(k)) for k in range(1, 6))
    ss = int(m.group(6) or 0)
    frac = m.group(7) or ""
    us = int((frac + "000000")[:6]) if frac else 0
    off = m.group(8)
    try:
        if off is None:
            tz = default_tz
        elif off.upper() == "Z":
            tz = UTC
        else:
            sign = 1 if off[0] == "+" else -1
            body = off[1:].replace(":", "")
            tz = timezone(sign * timedelta(hours=int(body[:2]), minutes=int(body[2:4])))
        return datetime(y, mo, d, hh, mi, ss, us, tzinfo=tz)
    except (ValueError, OverflowError):
        return None


def utc_minute(dt):
    return dt.astimezone(UTC).strftime("%Y-%m-%dT%H:%MZ")


def canonical_sha(obj):
    return sha(json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8"))


def expand(series_id, s, vintage, horizon_days, listed_child_starts=None):
    """Vintage-anchored S1b expansion of one ready full Schedule.

    Returns (occurrences, info). info["status"] is one of:
      expanded | window_empty | skipped:<typed reason>
    Never raises on data: every unsupported or unparseable shape is a typed skip.
    """
    info = {"status": None, "except_removed": 0, "except_unparseable": 0,
            "repeat_count_truncated": False, "byday_unrecognised": 0}
    try:
        tz = ZoneInfo(s["scheduleTimezone"])
    except Exception:
        info["status"] = "skipped:timezone_unknown"; return [], info
    rf = s.get("repeatFrequency")
    if not (rf is None or isinstance(rf, str)) or rf not in WEEKLY_FREQ:
        info["status"] = f"skipped:repeatFrequency_unsupported:{rf if isinstance(rf, str) else type(rf).__name__}"; return [], info
    d_start, d_end = parse_date(s.get("startDate")), parse_date(s.get("endDate"))
    if d_start is None or d_end is None:
        info["status"] = "skipped:date_unparseable"; return [], info
    t_start, t_end = parse_time(s.get("startTime")), parse_time(s.get("endTime"))
    if t_start is None or t_end is None:
        info["status"] = "skipped:time_unparseable"; return [], info
    bd = s.get("byDay"); bd = bd if isinstance(bd, list) else [bd]
    days = {DAY_MAP[x] for x in bd if isinstance(x, str) and x in DAY_MAP}
    info["byday_unrecognised"] = sum(1 for x in bd if not (isinstance(x, str) and x in DAY_MAP))
    if not days:
        info["status"] = "skipped:byDay_unrecognised"; return [], info
    rc = s.get("repeatCount")
    if rc is not None:
        try:
            rc = int(rc)
        except (TypeError, ValueError):
            info["status"] = "skipped:repeatCount_unparseable"; return [], info
        if rc < 0:
            info["status"] = "skipped:repeatCount_unparseable"; return [], info
    # exceptDate: date form -> local-date exclusion; date-time form -> UTC-instant exclusion
    ex = s.get("exceptDate"); ex = ex if isinstance(ex, list) else ([ex] if ex else [])
    ex_dates, ex_instants = set(), set()
    for e in ex:
        if isinstance(e, str) and _DATE_RE.match(e.strip()):
            ex_dates.add(parse_date(e.strip()))
        else:
            dt = parse_datetime(e, tz)
            if dt is not None: ex_instants.add(utc_minute(dt))
            else: info["except_unparseable"] += 1
    win_lo = max(d_start, vintage)
    win_hi = min(d_end, vintage + timedelta(days=horizon_days - 1))   # inclusive
    if win_lo > win_hi:
        info["status"] = "window_empty"; return [], info
    listed = listed_child_starts or set()
    occ, count = [], 0
    day = d_start if rc is not None else win_lo       # repeatCount counts from startDate
    while day <= win_hi:
        if day.weekday() in days:
            if rc is not None and count >= rc:
                info["repeat_count_truncated"] = True; break
            count += 1
            if day >= win_lo:
                start_local = datetime.combine(day, t_start, tzinfo=tz)
                end_day = day + timedelta(days=1) if t_end < t_start else day
                end_local = datetime.combine(end_day, t_end, tzinfo=tz)
                su = utc_minute(start_local)
                if day in ex_dates or su in ex_instants:
                    info["except_removed"] += 1
                else:
                    occ.append({"series": series_id, "date_local": day.isoformat(),
                                "start_local": start_local.isoformat(),
                                "start_utc": start_local.astimezone(UTC).strftime("%Y-%m-%dT%H:%M:%SZ"),
                                "end_local": end_local.isoformat(),
                                "end_utc": end_local.astimezone(UTC).strftime("%Y-%m-%dT%H:%M:%SZ"),
                                "listed_child_match": su in listed,
                                "grade": "schedule_derived",
                                "rule": f"{INTERP_ID}:expand-full-schedule-weekly-byDay"})
        day += timedelta(days=1)
    info["status"] = "expanded"
    return occ, info


def s1b_provider(p_state, p_prov, c_state, vintage, horizon_days, horizon_status):
    """Run S1b over one provider's folded parent state.

    Returns (occurrences, summary). summary["counts"] holds only additive integer counters
    (the rollup sums exactly these); "schedule_status" is the typed disposition of every
    ready schedule; the remaining keys are run parameters. Listed-child concordance is
    computed once per series over the union of its expanded schedules, so a series with
    several full schedules never double-counts its children.
    """
    listed_raw = defaultdict(list)          # superEvent @id -> raw child startDate strings
    for it in c_state.values():
        d = it.get("data") or {}
        sid = super_id(d.get("superEvent"))
        if sid and isinstance(d.get("startDate"), str):
            listed_raw[sid].append(d["startDate"])
    occs, summ, statuses = [], Counter(), Counter()
    win_lo_h, win_hi_h = vintage, vintage + timedelta(days=horizon_days - 1)
    for iid, v in sorted(p_state.items(), key=lambda kv: str(kv[0])):
        d = v.get("data") or {}
        s = d.get("eventSchedule")
        schedules = s if isinstance(s, list) else [s] if s else []
        if not schedules:
            continue
        series_id = d.get("@id") or iid
        summ["series_with_schedules"] += 1
        prov = p_prov.get(iid) or {}
        series_tz, series_listed, series_occ, series_expanded = None, None, [], False
        for j, sch in enumerate(schedules):
            if readiness(sch):
                continue                                   # census already typed these
            summ["schedules_ready"] += 1
            if series_tz is None:
                try:
                    series_tz = ZoneInfo(sch["scheduleTimezone"])
                except Exception:
                    series_tz = None
                if series_tz is not None:
                    series_listed = set()
                    for raw in listed_raw.get(series_id, []):
                        dt = parse_datetime(raw, series_tz)
                        if dt is None:
                            summ["listed_child_startDate_unparseable"] += 1
                        else:
                            series_listed.add(utc_minute(dt))
            occ, info = expand(series_id, sch, vintage, horizon_days, series_listed or set())
            statuses[info["status"]] += 1
            summ["occurrences_except_removed"] += info["except_removed"]
            summ["exceptDate_values_unparseable"] += info["except_unparseable"]
            if info["repeat_count_truncated"]: summ["schedules_repeat_count_truncated"] += 1
            summ["byDay_values_unrecognised"] += info["byday_unrecognised"]
            if info["status"] != "expanded":
                continue
            summ["schedules_expanded"] += 1
            series_expanded = True
            sch_sha = canonical_sha(sch)
            for o in occ:
                o.update({"schedule_index": j, "schedule_sha256": sch_sha,
                          "horizon_status": horizon_status,
                          "provenance": dict(prov)})     # parent item's provenance, same shape as s1_records
                series_occ.append(o)
                summ["occurrences_total"] += 1
                if o["listed_child_match"]: summ["occurrences_matching_listed_child"] += 1
        occs.extend(series_occ)
        # reverse direction, once per series with >= 1 expanded schedule: listed children
        # whose start falls inside the horizon window but which no expanded schedule of this
        # series reproduces (minute-precision UTC instant)
        if series_expanded and series_tz is not None:
            produced = {o["start_utc"][:16] + "Z" for o in series_occ}
            for raw in listed_raw.get(series_id, []):
                dt = parse_datetime(raw, series_tz)
                if dt is None: continue
                if win_lo_h <= dt.astimezone(series_tz).date() <= win_hi_h:
                    summ["listed_children_in_window"] += 1
                    if utc_minute(dt) not in produced:
                        summ["listed_children_in_window_unmatched"] += 1
    summary = {"counts": {k: summ[k] for k in sorted(summ)},
               "schedule_status": {k: statuses[k] for k in sorted(statuses)},
               "horizon_days": horizon_days, "horizon_status": horizon_status,
               "vintage_date": vintage.isoformat(), "window_rule": WINDOW_RULE,
               "concordance_rule": CONCORDANCE_RULE}
    return occs, summary


# ---------------- driver -----------------------------------------------------
def derive_vintage(a):
    m = re.search(r"(\d{4}-\d{2}-\d{2})", a.snapshot or "")
    snap_date = parse_date(m.group(1)) if m else None
    if a.vintage_date:
        v = parse_date(a.vintage_date)
        if v is None: sys.exit(f"--vintage-date '{a.vintage_date}' is not an ISO date (YYYY-MM-DD).")
        if snap_date is not None and v != snap_date:
            sys.exit(f"REFUSED: --vintage-date {v} contradicts the snapshot's own date {snap_date}. "
                     f"Anchoring elsewhere than the harvest date is a design change (SOURCE-CONFLICT-M04-A), "
                     f"not a run option.")
        return v
    if snap_date is None:
        sys.exit("S1b needs an anchor date: pass --vintage-date YYYY-MM-DD "
                 "(or a --snapshot that contains one).")
    return snap_date


def run(a):
    refuse_sealed([a.zip or ""] + a.parents + a.children + [a.snapshot or "", a.vintage_date or ""])
    out = Path(a.out); out.mkdir(parents=True, exist_ok=True)
    if not a.zip:
        sys.exit("v0.3 runs in --zip mode only (receipt-verified runs).")
    if not (a.pages_csv and a.ledger):
        sys.exit("--zip mode requires --pages-csv and --ledger (receipt-verified runs only).")
    if a.horizon_days < 1:
        sys.exit("--horizon-days must be >= 1.")
    vintage = derive_vintage(a)

    corpus = Corpus(a.zip, a.pages_csv, a.ledger, a.snapshot, strict=not a.continue_on_mismatch,
                    terminals_csv=a.terminals)

    by_provider = defaultdict(lambda: {"parents": [], "children": [], "cross_kind": []})
    for row in corpus.feeds:
        ft, fid, prov_name = row.get("feed_type", ""), row["feed_id"], row.get("provider", "?")
        if fid in corpus.excluded_incomplete:
            continue
        b = by_provider[prov_name]
        (b["parents"] if PARENT_KIND.search(ft) else
         b["children"] if CHILD_KIND.search(ft) else b["cross_kind"]).append(fid)

    rollup = {"engine": ENGINE_VERSION, "predecessor": PREDECESSOR, "supersedes": SUPERSEDES, "policy": POLICY_ID,
              "interpretation": INTERP_ID, "snapshot": a.snapshot,
              "s1b_parameters": {"vintage_date": vintage.isoformat(), "horizon_days": a.horizon_days,
                                 "horizon_status": a.horizon_status, "window_rule": WINDOW_RULE},
              "providers": {}, "totals": Counter(), "field_lineage": Counter(),
              "schedule_census": Counter(), "s1b": Counter(), "s1b_schedule_status": Counter(),
              "cross_kind_feeds_skipped": Counter(), "quarantined_feeds": {},
              "excluded_incomplete_feeds": corpus.excluded_incomplete,
              "verification": corpus.stats}
    per_provider_receipts = {}

    for prov_name, b in sorted(by_provider.items()):
        for fid in b["cross_kind"]:
            rollup["cross_kind_feeds_skipped"]["cross_kind_pending(M06-D-07)"] += 1
        if not b["parents"] and not b["children"]:
            continue
        p_state, p_prov = {}, {}
        for fid in b["parents"]:
            st, tb, pv, viol, np_ = fold(corpus.pages(fid))
            if fid in corpus.quarantined: continue
            for k, v in pv.items(): v["source_feed"] = fid
            p_state.update(st); p_prov.update(pv)
            rollup["totals"]["rpde_order_violations"] += viol
            rollup["totals"]["pages_folded"] += np_
        c_state, c_prov = {}, {}
        for fid in b["children"]:
            st, tb, pv, viol, np_ = fold(corpus.pages(fid))
            if fid in corpus.quarantined: continue
            for k, v in pv.items(): v["source_feed"] = fid
            c_state.update(st); c_prov.update(pv)
            rollup["totals"]["rpde_order_violations"] += viol
            rollup["totals"]["pages_folded"] += np_
        parents_by_atid = {v["data"]["@id"]: v for v in p_state.values()
                           if isinstance(v.get("data"), dict) and v["data"].get("@id")}
        recs, res_c, fld_c = reconstruct(c_state, parents_by_atid,
                                         {**p_prov, **c_prov}, ",".join(b["parents"]))
        census = Counter(); schedule_census(p_state, census)
        occs, s1b_sum = s1b_provider(p_state, p_prov, c_state, vintage, a.horizon_days, a.horizon_status)
        pdir = out / re.sub(r"[^A-Za-z0-9_-]+", "_", prov_name)[:60]
        pdir.mkdir(exist_ok=True)
        with open(pdir / "s1_records.jsonl", "w", encoding="utf-8") as f:
            for r in recs: f.write(json.dumps(r, ensure_ascii=False) + "\n")
        with open(pdir / "s1b_occurrences.jsonl", "w", encoding="utf-8") as f:
            for o in occs: f.write(json.dumps(o, ensure_ascii=False, sort_keys=True) + "\n")
        with open(pdir / "s1_parent_provenance.jsonl", "w", encoding="utf-8") as f:
            for atid in sorted(parents_by_atid):
                pv = p_prov.get(parents_by_atid[atid].get("id")) or {}
                f.write(json.dumps({"@id": atid, **pv}, ensure_ascii=False, sort_keys=True) + "\n")
        psum = {"provider": prov_name, "parents_s0": len(p_state), "children_s0": len(c_state),
                "parent_resolution": dict(res_c), "schedule_census": dict(census)}
        (pdir / "s1_summary.json").write_text(json.dumps(psum, indent=2), encoding="utf-8")
        s1b_sum["provider"] = prov_name
        (pdir / "s1b_summary.json").write_text(json.dumps(s1b_sum, indent=2, sort_keys=True), encoding="utf-8")
        per_provider_receipts[prov_name] = {
            "records_sha256": sha((pdir / "s1_records.jsonl").read_bytes()),
            "summary_sha256": sha((pdir / "s1_summary.json").read_bytes()),
            "s1b_occurrences_sha256": sha((pdir / "s1b_occurrences.jsonl").read_bytes()),
            "s1b_summary_sha256": sha((pdir / "s1b_summary.json").read_bytes()),
            "parent_provenance_sha256": sha((pdir / "s1_parent_provenance.jsonl").read_bytes())}
        rollup["providers"][prov_name] = psum
        for k, v in res_c.items(): rollup["totals"][f"resolution:{k}"] += v
        for (fld, cls), n in fld_c.items(): rollup["field_lineage"][f"{fld}:{cls}"] += n
        for k, v in census.items(): rollup["schedule_census"][k] += v
        for k, v in s1b_sum["counts"].items(): rollup["s1b"][k] += v
        for k, v in s1b_sum["schedule_status"].items(): rollup["s1b_schedule_status"][k] += v

    rollup["quarantined_feeds"] = corpus.quarantined
    for key in ("totals", "field_lineage", "schedule_census", "s1b", "s1b_schedule_status",
                "cross_kind_feeds_skipped", "verification"):
        rollup[key] = {k: rollup[key][k] for k in sorted(rollup[key])}
    (out / "corpus_rollup.json").write_text(json.dumps(rollup, indent=2, sort_keys=True), encoding="utf-8")
    master = {"engine_sha256": sha(Path(__file__).read_bytes()), "engine": ENGINE_VERSION,
              "predecessor": PREDECESSOR, "supersedes": SUPERSEDES,
              "policy": POLICY_ID, "interpretation": INTERP_ID, "snapshot": a.snapshot,
              "s1b_parameters": rollup["s1b_parameters"],
              "archive": Path(a.zip).name,
              "archive_sha256": {"value": a.zip_sha256, "status": "attested_by_caller"}
                                 if a.zip_sha256 else "not_supplied(page-level verification performed)",
              "pages_csv_sha256": sha(Path(a.pages_csv).read_bytes()),
              "ledger_sha256": sha(Path(a.ledger).read_bytes()),
              "terminals_csv_sha256": sha(Path(a.terminals).read_bytes()) if a.terminals else None,
              "outputs": {"corpus_rollup.json": sha((out / "corpus_rollup.json").read_bytes()),
                          "per_provider": per_provider_receipts},
              "verification": rollup["verification"],
              "quarantined": corpus.quarantined,
              "excluded_incomplete_feeds": corpus.excluded_incomplete,
              "deterministic": True, "seed": None}
    (out / "MASTER_RECEIPT.json").write_text(json.dumps(master, indent=2, sort_keys=True), encoding="utf-8")
    report = {"providers_run": len(rollup["providers"]), "totals": rollup["totals"],
              "schedule_census": rollup["schedule_census"], "s1b": rollup["s1b"],
              "s1b_schedule_status": rollup["s1b_schedule_status"],
              "s1b_parameters": rollup["s1b_parameters"],
              "verification": rollup["verification"], "quarantined": list(corpus.quarantined),
              "excluded_incomplete": len(corpus.excluded_incomplete)}
    print(json.dumps(report, indent=1))
    return rollup, master


# ---------------- self-test (fixture-built; no inputs needed) ----------------
def _sched(start, end, by, st="18:00", et="19:00", **kw):
    s = {"@type": "Schedule", "startDate": start, "endDate": end, "startTime": st, "endTime": et,
         "byDay": by, "scheduleTimezone": "Europe/London"}
    s.update(kw); return s


def build_fixture(root: Path, snapshot="2026-08-27"):
    """Two-page parent feed, one-page child feed, one cross-kind feed, one INCOMPLETE feed."""
    A_v1 = {"id": "A", "modified": 100, "kind": "SessionSeries", "state": "updated",
            "data": {"@type": "SessionSeries", "@id": "https://x.test/series/A", "name": "Yoga v1",
                     "location": {"@type": "Place", "name": "Hall"},
                     "eventSchedule": [_sched("2026-01-05", "2026-12-31", ["https://schema.org/Monday", "Wednesday"],
                                              exceptDate=["2026-09-07", "2026-09-09T18:00:00+01:00",
                                                          "2026-09-14T10:00:00+01:00"])]}}
    A_v2 = json.loads(json.dumps(A_v1)); A_v2["modified"] = 200; A_v2["data"]["name"] = "Yoga v2"
    B = {"id": "B", "modified": 101, "kind": "SessionSeries", "state": "updated",
         "data": {"@type": "SessionSeries", "@id": "https://x.test/series/B", "name": "Partial",
                  "eventSchedule": {"@type": "PartialSchedule", "startTime": "10:00"}}}
    C = {"id": "C", "modified": 102, "kind": "SessionSeries", "state": "updated",
         "data": {"@type": "SessionSeries", "@id": "https://x.test/series/C", "name": "NoByDay",
                  "eventSchedule": {"@type": "Schedule", "startDate": "2026-01-01", "endDate": "2026-12-31",
                                    "startTime": "09:00", "endTime": "10:00", "scheduleTimezone": "Europe/London"}}}
    E = {"id": "E", "modified": 103, "kind": "SessionSeries", "state": "updated",
         "data": {"@type": "SessionSeries", "@id": "https://x.test/series/E", "name": "Counted",
                  "eventSchedule": _sched("2026-08-24", "2026-12-31", ["Monday"], repeatCount=2)}}
    F = {"id": "F", "modified": 104, "kind": "SessionSeries", "state": "updated",
         "data": {"@type": "SessionSeries", "@id": "https://x.test/series/F", "name": "Fortnightly",
                  "eventSchedule": _sched("2026-01-01", "2026-12-31", ["Tuesday"], repeatFrequency="P2W")}}
    G = {"id": "G", "modified": 105, "kind": "SessionSeries", "state": "updated",
         "data": {"@type": "SessionSeries", "@id": "https://x.test/series/G", "name": "Ended",
                  "eventSchedule": _sched("2026-01-01", "2026-06-30", ["Friday"])}}
    X = {"id": "X", "modified": 106, "kind": "SessionSeries", "state": "updated",
         "data": {"@type": "SessionSeries", "@id": "https://x.test/series/X", "name": "Doomed"}}
    X_del = {"id": "X", "modified": 201, "kind": "SessionSeries", "state": "deleted"}
    p0 = {"license": "CC-BY", "next": "p1", "items": [A_v1, B, C, E, F, G, X]}
    p1 = {"license": "CC-BY", "next": "p1", "items": [A_v2, X_del]}

    def child(i, sup, start, **extra):
        d = {"@type": "ScheduledSession", "@id": f"https://x.test/session/{i}", "startDate": start}
        if sup: d["superEvent"] = sup
        d.update(extra)
        return {"id": f"c{i}", "modified": 300 + i, "kind": "ScheduledSession", "state": "updated", "data": d}
    kids = [child(1, "https://x.test/series/A", "2026-09-02T18:00:00+01:00"),
            child(2, "https://x.test/series/A", "2026-09-05T10:00:00+01:00"),
            child(3, "https://x.test/series/A", "2026-08-01T18:00:00+01:00", name="Own name"),
            child(4, "https://x.test/series/NOPE", "2026-09-02T18:00:00+01:00"),
            child(5, None, "2026-09-02T18:00:00+01:00"),
            child(6, {"@id": "https://x.test/series/E"}, "2026-08-31T18:00:00+01:00")]
    c0 = {"license": "CC-BY", "next": "c0", "items": kids}
    fu0 = {"license": "CC-BY", "next": "f0", "items": [{"id": "fu1", "modified": 1, "kind": "FacilityUse",
                                                          "state": "updated", "data": {"@type": "FacilityUse"}}]}
    inc0 = {"license": "CC-BY", "next": "i0", "items": [child(9, "https://x.test/series/A", "2026-09-07T18:00:00+01:00")]}
    # second provider: two full schedules on ONE series (Tue 07:00, Thu 07:00), two listed
    # children (one reproduced by schedule 2, one Sunday stray) -> tests per-series concordance
    H = {"id": "H", "modified": 400, "kind": "SessionSeries", "state": "updated",
         "data": {"@type": "SessionSeries", "@id": "https://z.test/series/H", "name": "Swim",
                  "eventSchedule": [_sched("2026-08-01", "2026-12-31", ["Tuesday"], st="07:00", et="08:00"),
                                    _sched("2026-08-01", "2026-12-31", ["Thursday"], st="07:00", et="08:00")]}}
    zp0 = {"license": "CC-BY", "next": "z0", "items": [H]}
    zc0 = {"license": "CC-BY", "next": "zc0", "items": [
        {"id": "h1", "modified": 401, "kind": "ScheduledSession", "state": "updated",
         "data": {"@type": "ScheduledSession", "@id": "https://z.test/session/1", "superEvent": "https://z.test/series/H",
                  "startDate": "2026-09-03T07:00:00+01:00"}},
        {"id": "h2", "modified": 402, "kind": "ScheduledSession", "state": "updated",
         "data": {"@type": "ScheduledSession", "@id": "https://z.test/session/2", "superEvent": "https://z.test/series/H",
                  "startDate": "2026-09-06T07:00:00+01:00"}}]}
    pages = {("fix-sessionseries", 0): p0, ("fix-sessionseries", 1): p1, ("fix-scheduledsession", 0): c0,
             ("fix-facilityuse", 0): fu0, ("fix-incomplete-scheduledsession", 0): inc0,
             ("zeta-sessionseries", 0): zp0, ("zeta-scheduledsession", 0): zc0}
    root.mkdir(parents=True, exist_ok=True)
    zpath = root / f"{snapshot}.zip"
    rows, page_bytes = [], {}
    with zipfile.ZipFile(zpath, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        zf.writestr(f"snapshots/{snapshot}/manifest.json", json.dumps({"snapshot_id": snapshot}))
        for (fid, idx), body in pages.items():
            raw = json.dumps(body, ensure_ascii=False).encode("utf-8")
            page_bytes[(fid, idx)] = raw
            zf.writestr(f"snapshots/{snapshot}/raw/{fid}/page_{idx:05d}.bytes", raw)
            rows.append({"snapshot_id": snapshot, "feed_id": fid, "page_index": idx, "sha256": sha(raw),
                         "byte_path": f"snapshots\\{snapshot}\\raw\\{fid}\\page_{idx:05d}.bytes"})
    with open(root / "pages.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["snapshot_id", "feed_id", "page_index", "sha256", "byte_path"])
        w.writeheader(); [w.writerow(r) for r in sorted(rows, key=lambda r: (r["feed_id"], r["page_index"]))]
    with open(root / "feeds_ledger.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["provider", "feed_id", "feed_type"])
        w.writeheader()
        for fid, ft in [("fix-sessionseries", "SessionSeries"), ("fix-scheduledsession", "ScheduledSession"),
                        ("fix-facilityuse", "FacilityUse"), ("fix-incomplete-scheduledsession", "ScheduledSession")]:
            w.writerow({"provider": "Fixture Prov", "feed_id": fid, "feed_type": ft})
        for fid, ft in [("zeta-sessionseries", "SessionSeries"), ("zeta-scheduledsession", "ScheduledSession")]:
            w.writerow({"provider": "Zeta/Prov Ltd.", "feed_id": fid, "feed_type": ft})
    with open(root / "walk_terminals.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["feed_id", "delivery", "terminal"])
        w.writeheader()
        for fid in ["fix-sessionseries", "fix-scheduledsession", "fix-facilityuse",
                    "zeta-sessionseries", "zeta-scheduledsession"]:
            w.writerow({"feed_id": fid, "delivery": "COMPLETE", "terminal": "live_edge"})
        w.writerow({"feed_id": "fix-incomplete-scheduledsession", "delivery": "INCOMPLETE", "terminal": "http_error"})
    return zpath, root / "pages.csv", root / "feeds_ledger.csv", root / "walk_terminals.csv", page_bytes


def selftest():
    results = []
    def check(name, cond, detail=""):
        results.append((name, bool(cond), detail))

    # --- unit level: expand() ---
    V = date(2026, 8, 27)
    # DST: Europe/London leaves BST on Sun 25 Oct 2026 (01:00 UTC)
    occ, info = expand("dst", _sched("2026-10-01", "2026-11-30", ["Saturday", "Sunday"]), date(2026, 10, 24), 2)
    check("DST-before: Sat 24 Oct 18:00 local = 17:00Z", len(occ) == 2 and occ[0]["start_utc"] == "2026-10-24T17:00:00Z",
          json.dumps([o["start_utc"] for o in occ]))
    check("DST-after: Sun 25 Oct 18:00 local = 18:00Z", len(occ) == 2 and occ[1]["start_utc"] == "2026-10-25T18:00:00Z")
    # FX-02 spring gap (29 Mar 2026, 01:00 GMT -> 02:00 BST) and FX-03 autumn ambiguity
    occ, info = expand("fx02", _sched("2026-03-01", "2026-04-30", ["Saturday", "Sunday"]), date(2026, 3, 28), 2)
    check("FX-02 spring: Sat 28 Mar 18:00 = 18:00Z (GMT); Sun 29 Mar 18:00 = 17:00Z (BST)",
          [o["start_utc"] for o in occ] == ["2026-03-28T18:00:00Z", "2026-03-29T17:00:00Z"], json.dumps([o["start_utc"] for o in occ]))
    occ, info = expand("fx02g", _sched("2026-03-01", "2026-04-30", ["Sunday"], st="01:30", et="02:30"), date(2026, 3, 29), 1)
    check("FX-02 gap: non-existent 01:30 on 29 Mar resolves fold=0 (PEP 495) = 01:30Z, stated not hidden",
          [o["start_utc"] for o in occ] == ["2026-03-29T01:30:00Z"])
    occ, info = expand("fx03a", _sched("2026-10-01", "2026-11-30", ["Sunday"], st="01:30", et="02:30"), date(2026, 10, 25), 1)
    check("FX-03 ambiguity: 01:30 on 25 Oct resolves to the FIRST occurrence (BST) = 00:30Z, stated not hidden",
          [o["start_utc"] for o in occ] == ["2026-10-25T00:30:00Z"])
    # SOURCE-CONFLICT-M04 required test: horizon partition is metamorphic — [V,V+10) U [V+10,V+28) == [V,V+28)
    for label, sch in [("A+exceptDate", _sched("2026-01-05", "2026-12-31", ["Monday", "Wednesday"],
                                               exceptDate=["2026-09-07", "2026-09-09T18:00:00+01:00"])),
                       ("E+repeatCount", _sched("2026-08-24", "2026-12-31", ["Monday"], repeatCount=3))]:
        whole = [o["start_utc"] for o in expand("mm", sch, V, 28)[0]]
        part = [o["start_utc"] for o in expand("mm", sch, V, 10)[0]] + \
               [o["start_utc"] for o in expand("mm", sch, V + timedelta(days=10), 18)[0]]
        check(f"metamorphic partition ({label}): [V,V+10) U [V+10,V+28) == [V,V+28)", whole == part and len(whole) > 0,
              json.dumps({"whole": whole, "part": part}))
    # anchoring: window is vintage-anchored, never startDate-anchored
    occ, info = expand("anch", _sched("2026-01-05", "2026-12-31", ["Monday", "Wednesday"]), V, 28)
    dates = [o["date_local"] for o in occ]
    check("anchoring: 8 occurrences, first >= vintage, last < vintage+28",
          dates == ["2026-08-31", "2026-09-02", "2026-09-07", "2026-09-09", "2026-09-14", "2026-09-16",
                    "2026-09-21", "2026-09-23"], json.dumps(dates))
    occ, info = expand("late", _sched("2026-09-10", "2026-12-31", ["Monday"]), V, 28)
    check("anchoring: startDate inside window respected (14, 21 Sep only)",
          [o["date_local"] for o in occ] == ["2026-09-14", "2026-09-21"])
    occ, info = expand("end", _sched("2026-01-05", "2026-09-07", ["Monday"]), V, 28)
    check("anchoring: endDate inclusive (31 Aug, 7 Sep)", [o["date_local"] for o in occ] == ["2026-08-31", "2026-09-07"])
    # exceptDate: date form, matching date-time form, non-matching date-time form
    occ, info = expand("exc", _sched("2026-01-05", "2026-12-31", ["Monday", "Wednesday"],
                                     exceptDate=["2026-09-07", "2026-09-09T18:00:00+01:00", "2026-09-14T10:00:00+01:00"]), V, 28)
    check("exceptDate: date removes 7 Sep; 09 Sep 18:00+01:00 removes; 14 Sep 10:00 does not",
          len(occ) == 6 and info["except_removed"] == 2 and "2026-09-14" in [o["date_local"] for o in occ]
          and "2026-09-09" not in [o["date_local"] for o in occ], json.dumps([o["date_local"] for o in occ]))
    occ, info = expand("excz", _sched("2026-01-05", "2026-12-31", ["Monday"], exceptDate="2026-09-07T17:00:00Z"), V, 28)
    check("exceptDate: scalar Z-form instant (17:00Z = 18:00 BST) removes 7 Sep", "2026-09-07" not in [o["date_local"] for o in occ] and info["except_removed"] == 1)
    occ, info = expand("excn", _sched("2026-01-05", "2026-12-31", ["Monday"], exceptDate=["2026-09-07T18:00:00"]), V, 28)
    check("exceptDate: naive date-time read in scheduleTimezone removes 7 Sep", "2026-09-07" not in [o["date_local"] for o in occ])
    # repeatCount from startDate; repeatFrequency guard; cross-midnight; typed skips
    occ, info = expand("rc", _sched("2026-08-24", "2026-12-31", ["Monday"], repeatCount=2), V, 28)
    check("repeatCount: counted from startDate (24 Aug #1 unemitted, 31 Aug #2 emitted, then truncated)",
          [o["date_local"] for o in occ] == ["2026-08-31"] and info["repeat_count_truncated"])
    occ, info = expand("rf", _sched("2026-01-01", "2026-12-31", ["Tuesday"], repeatFrequency="P2W"), V, 28)
    check("repeatFrequency P2W: typed skip, no guess", info["status"] == "skipped:repeatFrequency_unsupported:P2W" and occ == [])
    occ, info = expand("rf1", _sched("2026-01-01", "2026-12-31", ["Tuesday"], repeatFrequency="P1W"), V, 28)
    check("repeatFrequency P1W: expands", info["status"] == "expanded" and len(occ) == 4)
    occ, info = expand("xm", _sched("2026-01-05", "2026-12-31", ["Monday"], st="23:00", et="01:00"), V, 7)
    check("cross-midnight endTime lands next day", len(occ) == 1 and occ[0]["end_local"].startswith("2026-09-01T01:00"))
    occ, info = expand("we", _sched("2026-01-01", "2026-06-30", ["Friday"]), V, 28)
    check("window_empty typed when schedule ended before vintage", info["status"] == "window_empty")
    occ, info = expand("tz", _sched("2026-01-01", "2026-12-31", ["Friday"], scheduleTimezone="Mars/Olympus"), V, 28)
    check("unknown timezone: typed skip", info["status"] == "skipped:timezone_unknown")
    occ, info = expand("bd", _sched("2026-01-01", "2026-12-31", ["Funday"]), V, 28)
    check("unrecognised byDay: typed skip", info["status"] == "skipped:byDay_unrecognised")
    occ, info = expand("bdd", _sched("2026-01-01", "2026-12-31", [{"@type": "DayOfWeek"}, "Monday"]), V, 28)
    check("non-string byDay entry: ignored + counted, Monday still expands (no TypeError on odd shapes)",
          info["status"] == "expanded" and info["byday_unrecognised"] == 1 and len(occ) == 4)
    occ, info = expand("rfd", _sched("2026-01-01", "2026-12-31", ["Monday"], repeatFrequency={"@type": "Duration"}), V, 28)
    check("non-string repeatFrequency: typed skip naming the type", info["status"] == "skipped:repeatFrequency_unsupported:dict")
    occ, info = expand("exu", _sched("2026-01-05", "2026-12-31", ["Monday"], exceptDate=[{"bad": 1}, "not-a-date", "2026-09-07"]), V, 28)
    check("exceptDate: unparseable entries counted (2), valid one applied", info["except_unparseable"] == 2 and info["except_removed"] == 1)
    code = None
    try:
        derive_vintage(argparse.Namespace(vintage_date="2026-09-01", snapshot="2026-08-27"))
    except SystemExit as e:
        code = str(e.code)
    check("vintage override contradicting the snapshot date is refused", code is not None and code.startswith("REFUSED"))
    check("vintage derived from snapshot id (V2026-08-27-DEV form too)",
          derive_vintage(argparse.Namespace(vintage_date=None, snapshot="V2026-08-27-DEV")) == date(2026, 8, 27))
    check("readiness: PartialSchedule never expanded (OA-1)",
          readiness({"@type": "PartialSchedule", "startTime": "10:00"}) == ["PartialSchedule-never-expanded(OA-1)"])
    check("readiness: missing byDay reported", readiness({"@type": "Schedule", "startDate": "2026-01-01", "endDate": "2026-12-31",
          "startTime": "09:00", "endTime": "10:00", "scheduleTimezone": "Europe/London"}) == ["byDay"])
    check("parse_datetime: Z, offset, basic offset, naive", parse_datetime("2026-09-02T18:00:00Z", UTC).hour == 18
          and utc_minute(parse_datetime("2026-09-02T18:00:00+01:00", UTC)) == "2026-09-02T17:00Z"
          and utc_minute(parse_datetime("2026-09-02T18:00:00.250+0100", UTC)) == "2026-09-02T17:00Z"
          and utc_minute(parse_datetime("2026-09-02T18:00:00", ZoneInfo("Europe/London"))) == "2026-09-02T17:00Z")

    # --- driver level: fixture run, twice ---
    tmp = Path(tempfile.mkdtemp(prefix="s1v03_selftest_"))
    try:
        zpath, pcsv, ledger, terms, page_bytes = build_fixture(tmp / "fixture")
        outs = []
        for k in (1, 2):
            a = argparse.Namespace(zip=str(zpath), pages_csv=str(pcsv), ledger=str(ledger), terminals=str(terms),
                                   snapshot="2026-08-27", zip_sha256=None, continue_on_mismatch=False,
                                   parents=[], children=[], out=str(tmp / f"run{k}"), horizon_days=28,
                                   horizon_status=HORIZON_STATUS_DEFAULT, vintage_date=None)
            with contextlib.redirect_stdout(io.StringIO()):
                rollup, master = run(a)
            outs.append((rollup, master, tmp / f"run{k}"))
        rollup, master, od = outs[0]
        pdir = od / "Fixture_Prov"          # provider "Fixture Prov" -> sanitised directory name
        recs = [json.loads(l) for l in (pdir / "s1_records.jsonl").read_text(encoding="utf-8").splitlines()]
        occs = [json.loads(l) for l in (pdir / "s1b_occurrences.jsonl").read_text(encoding="utf-8").splitlines()]
        s1b = json.loads((pdir / "s1b_summary.json").read_text(encoding="utf-8"))
        check("exclusion: INCOMPLETE feed excluded upfront (6 children, not 7)",
              rollup["providers"]["Fixture Prov"]["children_s0"] == 6 and "fix-incomplete-scheduledsession" in rollup["excluded_incomplete_feeds"])
        check("cross-kind feed skipped (typed)", rollup["cross_kind_feeds_skipped"].get("cross_kind_pending(M06-D-07)") == 1)
        check("fold: tombstone removed X; 6 parents survive", rollup["providers"]["Fixture Prov"]["parents_s0"] == 6)
        fcen = rollup["providers"]["Fixture Prov"]["schedule_census"]
        check("census unchanged vs v0.2.2 semantics: 'Fixture Prov' total 6, partial 1, not_ready:byDay 1, ready 4",
              fcen == {"schedules_total": 6, "partial_schedule": 1, "not_ready:byDay": 1, "full_schedule_ready": 4}, json.dumps(fcen))
        check("census rollup sums both providers: total 8, ready 6",
              rollup["schedule_census"]["schedules_total"] == 8 and rollup["schedule_census"]["full_schedule_ready"] == 6)
        check("resolution: 'Fixture Prov' 4 RESOLVED / 1 PARENT_NOT_IN_SAMPLE / 1 NO_SUPEREVENT; rollup RESOLVED 6",
              rollup["providers"]["Fixture Prov"]["parent_resolution"] == {"RESOLVED": 4, "PARENT_NOT_IN_SAMPLE": 1, "NO_SUPEREVENT": 1}
              and rollup["totals"].get("resolution:RESOLVED") == 6)
        r1 = next(r for r in recs if r["item_id"] == "c1")
        check("page provenance: inherited name is 'Yoga v2' (last-wins across pages)", r1["fields"].get("name") == "Yoga v2")
        c3 = next(r for r in recs if r["item_id"] == "c3")
        check("lineage: CHILD_OVERRIDES on name for c3; INHERITED location", c3["lineage"]["name"]["class"] == "CHILD_OVERRIDES"
              and c3["lineage"]["location"]["class"] == "INHERITED")
        check("page provenance: child record carries page_index 0 + sha of served child page",
              r1["provenance"]["page_index"] == 0 and r1["provenance"]["page_sha256"] == sha(page_bytes[("fix-scheduledsession", 0)]))
        occA = [o for o in occs if o["series"] == "https://x.test/series/A"]
        check("S1b: series A -> 6 occurrences after exceptDate (2 removed)", len(occA) == 6 and s1b["counts"]["occurrences_except_removed"] == 2)
        check("S1b: occurrence provenance binds to parent page 1 (A's last-wins page) + its sha",
              all(o["provenance"]["page_index"] == 1 and o["provenance"]["page_sha256"] == sha(page_bytes[("fix-sessionseries", 1)])
                  and o["provenance"]["source_feed"] == "fix-sessionseries" and o["provenance"]["rpde_id"] == "A"
                  and o["provenance"]["modified"] == 200 for o in occA))
        check("S1b: series E repeatCount -> exactly 31 Aug", [o["date_local"] for o in occs if o["series"] == "https://x.test/series/E"] == ["2026-08-31"])
        check("S1b: schedule statuses expanded 2 / window_empty 1 / skipped P2W 1 (= 4 ready)",
              s1b["schedule_status"] == {"expanded": 2, "skipped:repeatFrequency_unsupported:P2W": 1, "window_empty": 1}
              and s1b["counts"]["schedules_ready"] == 4 == fcen["full_schedule_ready"] and s1b["counts"]["schedules_expanded"] == 2, json.dumps(s1b["schedule_status"]))
        check("S1b totals: 7 occurrences; 2 match listed children (c1 on A, c6 on E)",
              s1b["counts"]["occurrences_total"] == 7 and s1b["counts"]["occurrences_matching_listed_child"] == 2)
        check("S1b reverse: 3 listed children in window, 1 unmatched (c2 Sat 5 Sep)",
              s1b["counts"]["listed_children_in_window"] == 3 and s1b["counts"]["listed_children_in_window_unmatched"] == 1)
        check("S1b: every occurrence labelled with horizon status + schedule sha",
              all(o["horizon_status"] == HORIZON_STATUS_DEFAULT and len(o["schedule_sha256"]) == 64 for o in occs))
        zdir = od / "Zeta_Prov_Ltd_"
        zocc = [json.loads(l) for l in (zdir / "s1b_occurrences.jsonl").read_text(encoding="utf-8").splitlines()]
        zs1b = json.loads((zdir / "s1b_summary.json").read_text(encoding="utf-8"))
        check("S1b multi-schedule series: Tue+Thu schedules -> 8 occurrences (1,8,15,22 Sep; 27 Aug, 3,10,17 Sep)",
              sorted(o["date_local"] for o in zocc) == ["2026-08-27", "2026-09-01", "2026-09-03", "2026-09-08", "2026-09-10",
                                                          "2026-09-15", "2026-09-17", "2026-09-22"]
              and {o["schedule_index"] for o in zocc} == {0, 1}, json.dumps(sorted(o["date_local"] for o in zocc)))
        check("S1b concordance once per series (no double count): 2 listed in window, 1 unmatched, 1 matched",
              zs1b["counts"]["listed_children_in_window"] == 2 and zs1b["counts"]["listed_children_in_window_unmatched"] == 1
              and zs1b["counts"]["occurrences_matching_listed_child"] == 1, json.dumps(zs1b["counts"]))
        check("rollup s1b block = provider sums (15 occurrences, 4 expanded) and carries only counters",
              rollup["s1b"]["occurrences_total"] == 15 and rollup["s1b"]["schedules_expanded"] == 4
              and rollup["s1b_schedule_status"]["expanded"] == 4 and "horizon_days" not in rollup["s1b"]
              and all(isinstance(v, int) for v in rollup["s1b"].values()), json.dumps(rollup["s1b"]))
        pp = [json.loads(l) for l in (pdir / "s1_parent_provenance.jsonl").read_text(encoding="utf-8").splitlines()]
        ppA = next(r for r in pp if r["@id"] == "https://x.test/series/A")
        check("parent provenance sidecar: 6 parents with @id, sorted; A bound to page 1 + its sha (last-wins)",
              [r["@id"] for r in pp] == sorted(r["@id"] for r in pp) and len(pp) == 6 and ppA["page_index"] == 1
              and ppA["page_sha256"] == sha(page_bytes[("fix-sessionseries", 1)]) and ppA["modified"] == 200
              and ppA["source_feed"] == "fix-sessionseries" and ppA["rpde_id"] == "A")
        check("parent provenance sidecar: every INHERITED lineage row's parent_@id resolves to a sidecar row",
              all(r["lineage"][f]["parent_@id"] in {x["@id"] for x in pp} for r in recs for f in r["lineage"]
                  if r["lineage"][f]["class"] == "INHERITED") and any(r["lineage"][f]["class"] == "INHERITED" for r in recs for f in r["lineage"]))
        pr = master["outputs"]["per_provider"]["Fixture Prov"]
        check("receipt binds all five per-provider outputs by sha256",
              pr["s1b_occurrences_sha256"] == sha((pdir / "s1b_occurrences.jsonl").read_bytes())
              and pr["s1b_summary_sha256"] == sha((pdir / "s1b_summary.json").read_bytes())
              and pr["records_sha256"] == sha((pdir / "s1_records.jsonl").read_bytes())
              and pr["summary_sha256"] == sha((pdir / "s1_summary.json").read_bytes())
              and pr["parent_provenance_sha256"] == sha((pdir / "s1_parent_provenance.jsonl").read_bytes())
              and master["outputs"]["corpus_rollup.json"] == sha((od / "corpus_rollup.json").read_bytes()))
        check("receipt records vintage/horizon/status/predecessor",
              master["s1b_parameters"]["vintage_date"] == "2026-08-27" and master["s1b_parameters"]["horizon_days"] == 28
              and master["s1b_parameters"]["horizon_status"] == HORIZON_STATUS_DEFAULT and master["predecessor"] == PREDECESSOR
              and master["supersedes"] == SUPERSEDES)
        files = sorted(p.relative_to(od) for p in od.rglob("*") if p.is_file())
        same = all(sha((outs[0][2] / f).read_bytes()) == sha((outs[1][2] / f).read_bytes()) for f in files)
        check(f"determinism: two runs byte-identical over {len(files)} output files", same and len(files) == 12)
        # tamper: flip one served byte -> fail-closed exit 13 (strict) / quarantine (continue)
        zt = tmp / "tampered.zip"
        with zipfile.ZipFile(zpath) as zin, zipfile.ZipFile(zt, "w") as zout:
            for n in zin.namelist():
                b = zin.read(n)
                if n.endswith("fix-scheduledsession/page_00000.bytes"): b = b.replace(b"Own name", b"Own nam3")
                zout.writestr(n, b)
        a = argparse.Namespace(zip=str(zt), pages_csv=str(pcsv), ledger=str(ledger), terminals=str(terms),
                               snapshot="2026-08-27", zip_sha256=None, continue_on_mismatch=False, parents=[], children=[],
                               out=str(tmp / "tamper"), horizon_days=28, horizon_status=HORIZON_STATUS_DEFAULT, vintage_date=None)
        code = None
        try:
            with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
                run(a)
        except SystemExit as e:
            code = e.code
        check("verification: tampered page fails closed with exit 13", code == 13)
        a.continue_on_mismatch = True; a.out = str(tmp / "tamper2")
        with contextlib.redirect_stdout(io.StringIO()):
            rollup_t, _ = run(a)
        check("verification: --continue-on-mismatch quarantines the child feed (typed)",
              "fix-scheduledsession" in rollup_t["quarantined_feeds"] and rollup_t["providers"]["Fixture Prov"]["children_s0"] == 0)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    width = max(len(n) for n, _, _ in results)
    for n, ok, det in results:
        print(("OK   " if ok else "FAIL ") + n.ljust(width) + ("" if ok or not det else "   <- " + det))
    n_ok = sum(1 for _, ok, _ in results if ok)
    print(f"\nSELFTEST: {n_ok}/{len(results)} checks pass — " +
          ("ALL PASS" if n_ok == len(results) else "STOP: failures above"))
    return 0 if n_ok == len(results) else 1


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--zip", help="delivery archive (Wesley layout)")
    ap.add_argument("--pages-csv"); ap.add_argument("--ledger")
    ap.add_argument("--terminals", help="walk_terminals.csv; feeds not marked COMPLETE are excluded upfront (typed)")
    ap.add_argument("--snapshot", help="expected snapshot_id; run refuses mismatch")
    ap.add_argument("--zip-sha256", help="externally verified archive hash (recorded as attested)")
    ap.add_argument("--continue-on-mismatch", action="store_true",
                    help="quarantine feeds on hash mismatch instead of failing closed")
    ap.add_argument("--parents", nargs="*", default=[]); ap.add_argument("--children", nargs="*", default=[])
    ap.add_argument("--out", default="s1_out_v03")
    ap.add_argument("--horizon-days", type=int, default=28, help="S1b horizon H in calendar days (default 28)")
    ap.add_argument("--horizon-status", default=HORIZON_STATUS_DEFAULT,
                    help="label stamped on every occurrence; flip to the ratified id when M05-D-HORIZON is ratified")
    ap.add_argument("--vintage-date", help="anchor date YYYY-MM-DD (default: the date inside --snapshot)")
    ap.add_argument("--selftest", action="store_true", help="run the built-in fixture self-test and exit")
    a = ap.parse_args()
    if a.selftest:
        sys.exit(selftest())
    run(a)


if __name__ == "__main__":
    main()
