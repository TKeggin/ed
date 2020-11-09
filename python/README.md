to install python functions:

1) first install requirements

python3 -m pip install -r requirements.txt

2) then install package

python3 -m pip install -e .

3) test import:

in python3 shell:

>>> import ed
>>> ed.test_route_finder()