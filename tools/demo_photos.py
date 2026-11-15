"""The two photos of the talk deck (tools/demo_deck.py), each a data URI.

The deploy (infra/monitor/deploy.sh) ships only tools/*.py, so a photo has to live in a module. Put a JPEG here as
"data:image/jpeg;base64,..." (for example: python3 -c "import base64,sys; print('data:image/jpeg;base64,' +
base64.b64encode(open(sys.argv[1], 'rb').read()).decode())" photo.jpg). While a string is empty, its slide shows an
empty frame with the word "Photo".
"""

TEA = ""       # slide 3 (#tea): gong fu tea and meditation
MEDITATE = ""  # slide 9 (#close)
