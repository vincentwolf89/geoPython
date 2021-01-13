//renderer:RENDERER_labels:kleur,grootte,kolom,aan/uit

{
    type: "unique-value",
        field: "beheergroep",
            defaultSymbol: { type: "simple-fill" },
    legendOptions: { "title": "Soort beplanting" },
    uniqueValueInfos: [{

        value: "Bosschage/Struw",
        label: "Bosschage/Struw",
        symbol: {
            type: "simple-fill",
            color: "#7C551D",
            size: "7px",
            outline: {
                color: "black",
                width: 0.5,
            }
        }
    }, {

        value: "Hagen",
        label: "Hagen",
        symbol: {
            type: "simple-fill",
            color: "#DA8810",
            size: "7px",
            outline: {
                color: "black",
                width: 0.5,
            }
        }
    }, {

        value: "Hakhout",
        label: "Hakhout",
        symbol: {
            type: "simple-fill",
            color: "#0C812C",
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
            type: "simple-fill",
            color: "#C8C824",
            size: "7px",
            outline: {
                color: "black",
                width: 0.5,
            }
        }
    }, 

    ],
};