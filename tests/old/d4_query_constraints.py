"""
D4 — query -> constraints layer.
Turns a structured query into the {field: predicate} constraints the R1 gate checks.
Built against the REAL fields in Michael's S1 data: category, offers, location, startDate.
"""
import datetime

def category_contains(keyword):
    kw = keyword.lower()
    def pred(cat_value):
        if not cat_value: return False
        cats = cat_value if isinstance(cat_value, list) else [cat_value]
        labels = [c.get("prefLabel","") if isinstance(c,dict) else str(c) for c in cats]
        return any(kw in str(l).lower() for l in labels)
    return pred

def price_free(offers_value):
    if not offers_value: return False
    offers = offers_value if isinstance(offers_value, list) else [offers_value]
    return any(o.get("price")==0 for o in offers if isinstance(o,dict) and o.get("price") is not None)

def price_max(limit):
    def pred(offers_value):
        if not offers_value: return False
        offers = offers_value if isinstance(offers_value, list) else [offers_value]
        prices = [o.get("price") for o in offers if isinstance(o,dict) and o.get("price") is not None]
        return bool(prices) and min(prices) <= limit
    return pred

def region_is(region_name):
    target = region_name.lower()
    def pred(location_value):
        if not isinstance(location_value, dict): return False
        addr = location_value.get("address", {})
        if not isinstance(addr, dict): return False
        fields = [addr.get("addressRegion"), addr.get("addressLocality")]
        return any(f and target in str(f).lower() for f in fields)
    return pred

def day_type(kind):
    def pred(sd):
        if not sd: return False
        try: d = datetime.datetime.fromisoformat(sd)
        except (ValueError, TypeError): return False
        wkend = d.weekday() >= 5
        return wkend if kind=="weekend" else not wkend
    return pred

def time_of_day(period):
    ranges = {"morning":(5,12),"afternoon":(12,17),"evening":(17,22)}
    lo,hi = ranges.get(period,(0,24))
    def pred(sd):
        if not sd: return False
        try: d = datetime.datetime.fromisoformat(sd)
        except (ValueError, TypeError): return False
        return lo <= d.hour < hi
    return pred

def build_constraints(query: dict):
    c = {}
    if query.get("activity"): c["category"] = category_contains(query["activity"])
    if query.get("free"): c["offers"] = price_free
    elif query.get("max_price") is not None: c["offers"] = price_max(query["max_price"])
    if query.get("region"): c["location"] = region_is(query["region"])
    if query.get("when"): c["startDate"] = day_type(query["when"])
    if query.get("time"):
        base = c.get("startDate"); tp = time_of_day(query["time"])
        c["startDate"] = (lambda b,t:(lambda v:b(v) and t(v)))(base,tp) if base else tp
    return c

def query_text_from(query: dict):
    return query.get("activity") or query.get("text") or ""

if __name__ == "__main__":
    import json
    cards = [json.loads(l) for l in open("sample_100_records.jsonl")]
    query = {"activity":"swim","when":"weekday","max_price":6.0}
    cons = build_constraints(query)
    print(f"query: {query}\nconstraints on: {list(cons.keys())}\n")
    for rec in cards[:12]:
        f = rec["fields"]
        checks = {field: pred(f.get(field)) for field,pred in cons.items()}
        print(f"  {'MATCH' if all(checks.values()) else '  -  '}  {f.get('name','')[:26]:26s} {checks}")
