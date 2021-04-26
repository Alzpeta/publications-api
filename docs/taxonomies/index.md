---
layout: default
---

# Taxonomies

The following are the managed taxonomic trees currently available on the repository API.

To determine which terms are currently available in each taxonomic tree, run:
```
curl -XGET $API_URL
```

_NOTE:_ replace the `127.0.0.1:5000` in API URLs with your actual repository `SERVER_NAME`

### Contributor Type [contributor-type]

**API_URL**: http://127.0.0.1:5000/2.0/taxonomies/contributor-type/

### Languages [languages]

**API_URL**: http://127.0.0.1:5000/2.0/taxonomies/languages/

### Licenses [licenses]

**API_URL**: http://127.0.0.1:5000/2.0/taxonomies/licenses/

### The type of relationship of the described document to the interconnected item (unit) [itemRelationType]

**API_URL**: http://127.0.0.1:5000/2.0/taxonomies/itemRelationType/

### Resource type [resourceType]

**API_URL**: http://127.0.0.1:5000/2.0/taxonomies/resourceType/