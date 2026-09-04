import struct, re, json, sys, os

JP_RE = re.compile(r'[\u3040-\u30ff\u4e00-\u9fff]')

def parse_tbb(path):
    data = open(path, 'rb').read()
    num_fields, num_records, val3 = struct.unpack_from("<III", data, 0)
    pos = 12
    field_names = []
    for i in range(num_fields):
        end = data.index(b'\x00', pos)
        field_names.append(data[pos:end])
        pos = end + 1
    schema_end = pos
    records = []
    for r in range(num_records):
        rec = []
        for f in range(num_fields):
            end = data.index(b'\x00', pos)
            rec.append(data[pos:end])
            pos = end + 1
        records.append(rec)
    trailer = data[pos:]  # anything left over after last record
    return {
        "num_fields": num_fields,
        "num_records": num_records,
        "val3": val3,
        "field_names": field_names,
        "schema_end": schema_end,
        "records": records,
        "trailer": trailer,
        "total_size": len(data),
        "consumed": pos,
    }

def rebuild_tbb(parsed):
    out = bytearray()
    out += struct.pack("<III", parsed["num_fields"], parsed["num_records"], parsed["val3"])
    for fn in parsed["field_names"]:
        out += fn + b'\x00'
    for rec in parsed["records"]:
        for f in rec:
            out += f + b'\x00'
    out += parsed["trailer"]
    return bytes(out)

if __name__ == "__main__":
    path = sys.argv[1]
    p = parse_tbb(path)
    print(f"{path}: fields={p['num_fields']} records={p['num_records']} val3={p['val3']} schema_end={p['schema_end']} consumed={p['consumed']} total={p['total_size']} trailer_len={len(p['trailer'])}")
    # sanity check rebuild matches original bytes exactly
    original = open(path,'rb').read()
    rebuilt = rebuild_tbb(p)
    print("round-trip matches original:", rebuilt == original)
