//renderer:RENDERER_labels:kleur,grootte,kolom,aan/uit

{
    type: "unique-value",
        field: "beheergroep",
            defaultSymbol: { type: "simple-marker" },
    legendOptions: { "title": "Type boom" },
    uniqueValueInfos: [{

        value: "Bomen",
        label: "Bomen",
        symbol: {
            type: "simple-marker",
            color: "#7C551D",
            size: "7px",
            outline: {
                color: "black",
                width: 0.5,
            }
        }
    }, {

        value: "Fruitbomen",
        label: "Fruitbomen",
        symbol: {
            type: "simple-marker",
            color: "#DA8810",
            size: "7px",
            outline: {
                color: "black",
                width: 0.5,
            }
        }
    }, {

        value: "Knotbomen",
        label: "Knotbomen",
        symbol: {
            type: "simple-marker",
            color: "#0C812C",
            size: "7px",
            outline: {
                color: "black",
                width: 0.5,
            }
        }
    }, {

        value: "Leibomen",
        label: "Leibomen",
        symbol: {
            type: "simple-marker",
            color: "#C8C824",
            size: "7px",
            outline: {
                color: "black",
                width: 0.5,
            }
        }
    }, {

        value: "Struiken",
        label: "Struiken",
        symbol: {
            type: "simple-marker",
            color: "#B5380D",
            size: "7px",
            outline: {
                color: "black",
                width: 0.5,
            }
        }
    },

    {

        value: "Onbekend",
        label: "Onbekend",
        symbol: {
            type: "simple-marker",
            color: "grey",
            size: "7px",
            outline: {
                color: "black",
                width: 0.5,
            }
        }
    },

    ],
        };