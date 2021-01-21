{
    type:"class-breaks",
    field:"betamaatge",
    defaultSymbol:{type:"simple-marker"},
    legendOptions:
        {title:"Oordeel"},
    classBreakInfos: [
        {
            minValue: 4,
            maxValue: 5,
            symbol: {
                type: "simple-marker",
                color: "#7C551D",
                size: "7px",
                outline: {
                    color: "red",
                    width: 0.5,
                }
            },
            label: "test1"
        },
        {
            minValue: 5.1,
            maxValue: 10,
            symbol: {
                type: "simple-marker",
                color: "#7C551D",
                size: "7px",
                outline: {
                    color: "yellow",
                    width: 0.5,
                }
            },
            label: "test2"
        },
    ]
}

renderer:{"type":"unique-value","field":"eindoordeel_wbi","defaultSymbol":{"type":"simple-marker"},"legendOptions":{"title":"Oordeel"},"uniqueValueInfos":[{"value":"Voldoet niet vanwege dijkbasisregel","label":"Voldoet niet vanwege dijkbasisregel","symbol":{"type":"simple-marker","color":"#4670FF","size":"7px","outline":{"color":"black","width":0.5}}},{"value":"Iv","label":"Iv  Voldoet","symbol":{"type":"simple-marker","color":"#009011","size":"7px","outline":{"color":"black","width":0.5}}},{"value":"IIv","label":"IIv  Voldoet","symbol":{"type":"simple-marker","color":"#0DB619","size":"7px","outline":{"color":"black","width":0.5}}},{"value":"IIIv","label":"IIIv  Voldoet","symbol":{"type":"simple-marker","color":"#E6E912","size":"7px","outline":{"color":"black","width":0.5}}},{"value":"IVv","label":"IIIv  Voldoet niet","symbol":{"type":"simple-marker","color":"#E91812","size":"7px","outline":{"color":"black","width":0.5}}},{"value":"IVv","label":"IVv  Voldoet niet","symbol":{"type":"simple-marker","color":"#C61D18","size":"7px","outline":{"color":"black","width":0.5}}},{"value":"Vv","label":"Vv  Voldoet niet","symbol":{"type":"simple-marker","color":"#AF100B","size":"7px","outline":{"color":"black","width":0.5}}}]}
            
renderer:{"type":"class-breaks","field":"betamaatge","defaultSymbol":{"type":"simple-marker"},"legendOptions":{"title":"Oordeel"},"classBreakInfos":[{"minValue":3,"maxValue":5,"symbol":{"type":"simple-marker","color":"#7C551D","size":"7px","outline":{"color":"red","width":0.5}},"label":"test1"},{"minValue":5.1,"maxValue":10,"symbol":{"type":"simple-marker","color":"#7C551D","size":"7px","outline":{"color":"yellow","width":0.5}},"label":"test2"}]}_labels:black,8,eindoordeel_wbi,uit