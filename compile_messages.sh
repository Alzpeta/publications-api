#!/bin/bash

pybabel extract -o publications/translations/messages.pot publications
pybabel update -d publications/translations -i publications/translations/messages.pot -l cs
pybabel update -d publications/translations -i publications/translations/messages.pot -l en
pybabel compile -d publications/translations
