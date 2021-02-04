import gpudb
import json

db = gpudb.GPUdb(encoding='JSON', host="135.181.158.255", port="9191")
table = gpudb.GPUdbTable(name="crowd2train.annotated_plots", db=db)
records = table.get_records(0,200,"geojson")
json = json.dumps(records, indent=2, sort_keys=True)

print(json)