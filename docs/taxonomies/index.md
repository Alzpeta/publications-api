---
layout: default
---

# Taxonomies

The following are the managed taxonomic trees currently available on the repository API.

To determine which terms are currently available in each taxonomic tree, run:
```shell
curl -XGET ${API_URL}?representation:include=dsc
```

_NOTE:_ replace the `127.0.0.1:5000` in API URLs with your actual repository `SERVER_NAME`

## Contributor Type _[contributor-type]_
Defines types of contributors of the described document/resource.

**API_URL**: `https://127.0.0.1:5000/2.0/taxonomies/contributor-type/`

## Languages _[languages]_
Defines all available language codes and names of each language.

**API_URL**: `https://127.0.0.1:5000/2.0/taxonomies/languages/`

## Licenses _[licenses]_
Contains all available licences for described documents/resources.

**API_URL**: `https//127.0.0.1:5000/2.0/taxonomies/licenses/`

## The type of relationship of the described document to the interconnected item (unit) _[itemRelationType]_
Defines relationship types of possible relationships between documents or
resources.

**API_URL**: `https://127.0.0.1:5000/2.0/taxonomies/itemRelationType/`

## Resource type _[resourceType]_
Holds enumeration of types of described documents or resources.

**API_URL**: `https://127.0.0.1:5000/2.0/taxonomies/resourceType/`