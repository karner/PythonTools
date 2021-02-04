import json

def _byteify(data, ignore_dicts = False):
    # if this is a unicode string, return its string representation
    if isinstance(data, unicode):
        return data.encode('utf-8')
    # if this is a list of values, return list of byteified values
    if isinstance(data, list):
        return [_byteify(item, ignore_dicts=True) for item in data]
    # if this is a dictionary, return dictionary of byteified keys and values
    # but only if we haven't already byteified it
    if isinstance(data, dict) and not ignore_dicts:
        return {
            _byteify(key, ignore_dicts=True): _byteify(value, ignore_dicts=True)
            for key, value in data.iteritems()
        }
    # if it's anything else, return it in its original form
    return data

def addClassInsert(sample_id, legend_id):
    # create a db function which will create the fotoquestitem and the validation
    str = 'select from gw_city_oases_insert_poi_validation ('
    str += `sample_id` + ', ' + legend_id + ', null'
    str += ');\n';
    return str

def addPercentageInsert(sample_id, legend_id, percentage):
    str = 'select from gw_city_oases_insert_poi_validation ('
    str += `sample_id` + ', ' + legend_id + ', ' + `percentage`
    str += ');\n';
    return str

def handlePointAttribute(sample_id, param_name, param_value):
    if param_name == 'X':
        return
    if param_name == 'Y':
        return
    if param_name == 'fid':
        return
    if param_name == 'sample_id':
        return
    legend_id = param_name

    if param_value == True:
        return addClassInsert(sample_id, legend_id)
    else:
        return addPercentageInsert(sample_id, legend_id, param_value/100.0)

def getInsertsForPoint(point):
    lines = []
    sample_id = point.get('sample_id', None)
    if sample_id is None:
        print 'Warning: sample_id not set for: '
        print(point)
        return
    else:
        print 'Sample id found: ', sample_id

    for param in point.iterkeys():
        lines.append(handlePointAttribute(sample_id, param, point[param]))
    return lines



with open('/Users/karner/Downloads/auto_poi.json') as json_data:
    data = json.load(json_data, object_hook=_byteify)

lines = []
for point in data:
    lines.extend(getInsertsForPoint(point))
outfile = open('/Users/karner/Downloads/inserts.sql', 'w')
for line in lines:
    if line == None:
        continue
    outfile.write(line)
outfile.close()


