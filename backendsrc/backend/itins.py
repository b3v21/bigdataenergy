ALLOWED_SUBURBS = [
    # "Toowong",
    "Indooroopilly",
    # "Taringa",
    "St Lucia",
    # "Chapel Hill",
    "West End",
    # "Bardon",
    # "Paddington",
    # "Ashgrove",
    # "Herston",
    # "Newstead",
    # "Teneriffe",
    # "New Farm",
    "Fortitude Valley",
    # "Brisbane City",
    # "Highgate Hill",
    "South Brisbane",
    # "Kangaroo Point",
    # "East Brisbane",
    # "Dutton Park",
    # "Fairfield",
    # "Stones Corner",
    # "Coorparoo",
    # "Norman Park",
    # "Seven  Hills",
    # "Cannon Hill",
    # "Morningside",
    # "Hawthorne",
    # "Balmoral",
    # "Bulimba",
    # "Murarrie",
    # "Hamilton",
    # "Eagle Farm",
    # "Ascot",
    # "Hendra",
    # "Clayfield",
    # "Albion",
    # "Windsor",
    # "Kelvin Grove",
    # "Red Hill",
]

ALLOWED_STATIONS = ["1850", "1064", "2200", "600014", "1660", "1074", "1076", "1070", "1137"]

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
    },
    {
        "itinerary_id": 2,
        "routes": [
            {"route_id": "199-3136", "start": "1064", "end": "10802"},
            {"route_id": "61-3136", "start": "10802", "end": "815"},
            {"route_id": "walk", "start": "815", "end": "-1"},
        ],
    },
]

INPUT_ITINS["1074"] = [
    {
        "itinerary_id": 3,
        "routes": [
            {"route_id": "199-3136", "start": "1074", "end": "10802"},
            {"route_id": "385-3136", "start": "10802", "end": "817"},
            {"route_id": "walk", "start": "817", "end": "-1"},
        ],
    },    
    {
        "itinerary_id": 8,
        "routes": [
            {"route_id": "199-3136", "start": "1074", "end": "10802"},
            {"route_id": "61-3136", "start": "10802", "end": "815"},
            {"route_id": "walk", "start": "815", "end": "-1"},
        ],
    },
]

INPUT_ITINS["1137"] = [
    {
        "itinerary_id": 10,
        "routes": [
            {"route_id": "199-3136", "start": "1137", "end": "10802"},
            {"route_id": "385-3136", "start": "10802", "end": "817"},
            {"route_id": "walk", "start": "817", "end": "-1"},
        ],
    },    
    {
        "itinerary_id": 11,
        "routes": [
            {"route_id": "199-3136", "start": "1137", "end": "10802"},
            {"route_id": "61-3136", "start": "10802", "end": "815"},
            {"route_id": "walk", "start": "815", "end": "-1"},
        ],
    },
]

INPUT_ITINS["1070"] = [
    {
        "itinerary_id": 9,
        "routes": [
            {"route_id": "199-3136", "start": "1070", "end": "10802"},
            {"route_id": "61-3136", "start": "10802", "end": "815"},
            {"route_id": "walk", "start": "815", "end": "-1"},
        ],
    },
]

## South Brisbane ##
INPUT_ITINS["1076"] = [
    {
        "itinerary_id": 4,
        "routes": [
            {"route_id": "199-3136", "start": "1076", "end": "10802"},
            {"route_id": "385-3136", "start": "10802", "end": "817"},
            {"route_id": "walk", "start": "817", "end": "-1"},
        ],
    }
]


## INDRO ##
INPUT_ITINS["2200"] = [
    {
        "itinerary_id": 5,
        "routes": [
            {"route_id": "444-3136", "start": "2200", "end": "271"},
            {"route_id": "walk", "start": "271", "end": "-1"},
        ],
    }
]

INPUT_ITINS["1660"] = [
    {
        "itinerary_id": 6,
        "routes": [
            {"route_id": "walk", "start": "1660", "end": "2200"},
            {"route_id": "453-3251", "start": "2200", "end": "10792"},
            {"route_id": "walk", "start": "10792", "end": "125"},
            {"route_id": "walk", "start": "125", "end": "-1"},
        ],
    }
]

## FORTITUDE VALLEY ##
INPUT_ITINS["600014"] = [
    {
        "itinerary_id": 7,
        "routes": [
            {"route_id": "BDVL-3124", "start": "600014", "end": "600036"},
            {"route_id": "walk", "start": "600036", "end": "10793"},
            {"route_id": "385-3136", "start": "10793", "end": "816"},
            {"route_id": "walk", "start": "816", "end": "-1"},
        ],
    }
]
