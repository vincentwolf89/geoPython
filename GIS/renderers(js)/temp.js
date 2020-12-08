//renderer:RENDERER_labels:kleur,grootte,kolom,aan/uit

{
    type: "unique-value",
        field: "traject",
            defaultSymbol: { type: "simple-line" },
    legendOptions: { "title": "Dijktraject" },
    uniqueValueInfos: [{

        value: "KINDERDIJK - SCHOONHOVENSEVEER",
        label: "Kinderdijk - Schoonhovenseveer",
        symbol: {
            type: "simple-line",
            color: "#3937BF",
            size: "7px",
            width: "5px",
            style: "solid"

        }
    },
    {
        value: "NIEUWPOORT",
        label: "Nieuwpoort",
        symbol: {
            type: "simple-line",
            color: "#A1EC15",
            size: "7px",
            width: "5px",
            style: "solid"

        }
    },
    {
        value: "SCHOONHOVENSEVEER - LANGERAK",
        label: "Schoonhovenseveer - Langerak",
        symbol: {
            type: "simple-line",
            color: "#EC2A15",
            size: "7px",
            width: "5px",
            style: "solid"

        }
    },
    {
        value: "ZEDERIK",
        label: "Zederik",
        symbol: {
            type: "simple-line",
            color: "#EC15DB",
            size: "7px",
            width: "5px",
            style: "solid"

        }
    },


    ],
};