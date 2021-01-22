

{
    type:"class-breaks",
    field:"beta_doorsnede_kans", 
    defaultSymbol:{type:"simple-marker"},
    legendOptions:
        {title:"Oordeel [Beta]"},
    classBreakInfos: [
        {
            minValue: -99,
            maxValue: 3.29,
            symbol: {
                type: "simple-marker",
                color: "#F23716",
                size: "7px",
                outline: {
                    color: "red",
                    width: 0.5,
                }
            },
            label: "< 3.3"
        },
        {
            minValue: 3.3,
            maxValue: 3.99,
            symbol: {
                type: "simple-marker",
                color: "#E1E711",
                size: "7px",
                outline: {
                    color: "red",
                    width: 0.5,
                }
            },
            label: "3.3 - 4"
        },
        {
            minValue: 4,
            maxValue: 5.99,
            symbol: {
                type: "simple-marker",
                color: "#18DA2A",
                size: "7px",
                outline: {
                    color: "red",
                    width: 0.5,
                }
            },
            label: "4 - 6"
        },
        {
            minValue: 6,
            maxValue: 9.99,
            symbol: {
                type: "simple-marker",
                color: "#17B926",
                size: "7px",
                outline: {
                    color: "red",
                    width: 0.5,
                }
            },
            label: "6 - 10"
        },
        {
            minValue: 10,
            maxValue: 100,
            symbol: {
                type: "simple-marker",
                color: "#11831B",
                size: "7px",
                outline: {
                    color: "red",
                    width: 0.5,
                }
            },
            label: "> 10"
        },

    
    ]
}


renderer:{"type":"class-breaks","field":"beta_doorsnede_kans","defaultSymbol":{"type":"simple-marker"},"legendOptions":{"title":"Oordeel [Beta]"},"classBreakInfos":[{"minValue":-99,"maxValue":3.29,"symbol":{"type":"simple-marker","color":"#F23716","size":"7px","outline":{"color":"red","width":0.5}},"label":"<- 3.3"},{"minValue":3.3,"maxValue":3.99,"symbol":{"type":"simple-marker","color":"#E1E711","size":"7px","outline":{"color":"red","width":0.5}},"label":"3.3 - 4"},{"minValue":4,"maxValue":5.99,"symbol":{"type":"simple-marker","color":"#18DA2A","size":"7px","outline":{"color":"red","width":0.5}},"label":"4 - 6"},{"minValue":6,"maxValue":9.99,"symbol":{"type":"simple-marker","color":"#17B926","size":"7px","outline":{"color":"red","width":0.5}},"label":"6 - 10"},{"minValue":10,"maxValue":100,"symbol":{"type":"simple-marker","color":"#11831B","size":"7px","outline":{"color":"red","width":0.5}},"label":"-> 10"}]}_labels:black,8,eindoordeel_wbi,uit