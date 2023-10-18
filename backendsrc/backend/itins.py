# These are the hardcoded itineraries that will appear on the frontend
INPUT_ITINS = {}

## ST LUCIA ##
INPUT_ITINS["1850"] = [
    {
        "itinerary_id": 0,
        "routes": [
            {"route_id": "412-3136", "start": "1850", "end": "273"},
            {"route_id": "walk", "start": "273", "end": "-1"},
        ],
    }
]


## WEST END ##
INPUT_ITINS["1064"] = [
    {
        "itinerary_id": 1,
        "routes": [
            {"route_id": "199-3136", "start": "1064", "end": "10802"},
            {"route_id": "385-3136", "start": "10802", "end": "817"},
            {"route_id": "walk", "start": "817", "end": "-1"},
        ],
    }
]

## INDRO ##
INPUT_ITINS["2200"] = [
    {
        "itinerary_id": 2,
        "routes": [
            {"route_id": "444-3136", "start": "2200", "end": "271"},
            {"route_id": "walk", "start": "271", "end": "-1"},
        ],
    }
]

## FORTITUDE VALLEY ##
INPUT_ITINS["600014"] = [
    {
        "itinerary_id": 3,
        "routes": [
            {"route_id": "BDVL-3124", "start": "600014", "end": "600036"},
            {"route_id": "walk", "start": "600036", "end": "10793"},
            {"route_id": "385-3136", "start": "10793", "end": "816"},
            {"route_id": "walk", "start": "816", "end": "-1"},
        ],
    }
]