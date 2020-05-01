from google.cloud import datastore


PART_TYPE = 'part'


def set_part(client, part):
    key = client.key(PART_TYPE, part["number"])
    ic = datastore.Entity(key=key)
    for k, v in part.items():
        ic[k] = str(v)
    client.put(ic)


def get_part(client, number):
    key = client.key(PART_TYPE, number)
    ic = client.get(key)
    part = {"number":ic["number"], "pdf":ic["pdf"], "manufacturer":ic["manufacturer"], "details_page":ic["details_page"]}
    return part