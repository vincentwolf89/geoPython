<0, 0-10, 10-20. Etc 90-100, 100-110, 110-120 > 120 

{
    type:"class-breaks",
    field:"max_kwelweg_tekort", 
    defaultSymbol:{type:"simple-marker"},
    legendOptions:
        {title:"Tekort aan kwelweg [m]"},
    classBreakInfos: [
        {
            minValue: -999,
            maxValue: -0.01,
            symbol: {
                type: "simple-marker",
                color: "#d1ff00",
                size: "7px",
                outline: {
                    color: "red",
                    width: 0.5,
                }
            },
            label: "< 0"
        },
        {
            minValue: 0,
            maxValue: 9.99,
            symbol: {
                type: "simple-marker",
                color: "#d2ea01",
                size: "7px",
                outline: {
                    color: "red",
                    width: 0.5,
                }
            },
            label: "0 - 10"
        },
        {
            minValue: 10,
            maxValue: 19.99,
            symbol: {
                type: "simple-marker",
                color: "#d3d502",
                size: "7px",
                outline: {
                    color: "red",
                    width: 0.5,
                }
            },
            label: "10 - 20"
        },
        {
            minValue: 10,
            maxValue: 19.99,
            symbol: {
                type: "simple-marker",
                color: "#d4c003",
                size: "7px",
                outline: {
                    color: "red",
                    width: 0.5,
                }
            },
            label: "10 - 20"
        },
        {
            minValue: 20,
            maxValue: 29.99,
            symbol: {
                type: "simple-marker",
                color: "#d5aa05",
                size: "7px",
                outline: {
                    color: "red",
                    width: 0.5,
                }
            },
            label: "20 - 30"
        },
        {
            minValue: 30,
            maxValue: 39.99,
            symbol: {
                type: "simple-marker",
                color: "#d69506",
                size: "7px",
                outline: {
                    color: "red",
                    width: 0.5,
                }
            },
            label: "30 - 40"
        },
        {
            minValue: 40,
            maxValue: 49.99,
            symbol: {
                type: "simple-marker",
                color: "#d78007",
                size: "7px",
                outline: {
                    color: "red",
                    width: 0.5,
                }
            },
            label: "40 - 50"
        },
        {
            minValue: 50,
            maxValue: 59.99,
            symbol: {
                type: "simple-marker",
                color: "#d86b09",
                size: "7px",
                outline: {
                    color: "red",
                    width: 0.5,
                }
            },
            label: "50 - 60"
        },
        {
            minValue: 60,
            maxValue: 69.99,
            symbol: {
                type: "simple-marker",
                color: "#d9550a",
                size: "7px",
                outline: {
                    color: "red",
                    width: 0.5,
                }
            },
            label: "60 - 70"
        },
        {
            minValue: 70,
            maxValue: 79.99,
            symbol: {
                type: "simple-marker",
                color: "#da400b",
                size: "7px",
                outline: {
                    color: "red",
                    width: 0.5,
                }
            },
            label: "70 - 80"
        },
        {
            minValue: 80,
            maxValue: 89.99,
            symbol: {
                type: "simple-marker",
                color: "#db2b0d",
                size: "7px",
                outline: {
                    color: "red",
                    width: 0.5,
                }
            },
            label: "80 - 90"
        },
        {
            minValue: 90,
            maxValue: 99.99,
            symbol: {
                type: "simple-marker",
                color: "#dc160e",
                size: "7px",
                outline: {
                    color: "red",
                    width: 0.5,
                }
            },
            label: "90 - 100"
        },
        {
            minValue: 100,
            maxValue: 1000,
            symbol: {
                type: "simple-marker",
                color: "#dd000f",
                size: "7px",
                outline: {
                    color: "red",
                    width: 0.5,
                }
            },
            label: "> 100"
        },
        

    
    ]
}


renderer:{"type":"class-breaks","field":"max_kwelweg_tekort","defaultSymbol":{"type":"simple-marker"},"legendOptions":{"title":"Tekort aan kwelweg [m]"},"classBreakInfos":[{"minValue":-999,"maxValue":-0.01,"symbol":{"type":"simple-marker","color":"#d1ff00","size":"7px","outline":{"color":"red","width":0.5}},"label":"< 0"},{"minValue":0,"maxValue":9.99,"symbol":{"type":"simple-marker","color":"#d2ea01","size":"7px","outline":{"color":"red","width":0.5}},"label":"0 - 10"},{"minValue":10,"maxValue":19.99,"symbol":{"type":"simple-marker","color":"#d3d502","size":"7px","outline":{"color":"red","width":0.5}},"label":"10 - 20"},{"minValue":10,"maxValue":19.99,"symbol":{"type":"simple-marker","color":"#d4c003","size":"7px","outline":{"color":"red","width":0.5}},"label":"10 - 20"},{"minValue":20,"maxValue":29.99,"symbol":{"type":"simple-marker","color":"#d5aa05","size":"7px","outline":{"color":"red","width":0.5}},"label":"20 - 30"},{"minValue":30,"maxValue":39.99,"symbol":{"type":"simple-marker","color":"#d69506","size":"7px","outline":{"color":"red","width":0.5}},"label":"30 - 40"},{"minValue":40,"maxValue":49.99,"symbol":{"type":"simple-marker","color":"#d78007","size":"7px","outline":{"color":"red","width":0.5}},"label":"40 - 50"},{"minValue":50,"maxValue":59.99,"symbol":{"type":"simple-marker","color":"#d86b09","size":"7px","outline":{"color":"red","width":0.5}},"label":"50 - 60"},{"minValue":60,"maxValue":69.99,"symbol":{"type":"simple-marker","color":"#d9550a","size":"7px","outline":{"color":"red","width":0.5}},"label":"60 - 70"},{"minValue":70,"maxValue":79.99,"symbol":{"type":"simple-marker","color":"#da400b","size":"7px","outline":{"color":"red","width":0.5}},"label":"70 - 80"},{"minValue":80,"maxValue":89.99,"symbol":{"type":"simple-marker","color":"#db2b0d","size":"7px","outline":{"color":"red","width":0.5}},"label":"80 - 90"},{"minValue":90,"maxValue":99.99,"symbol":{"type":"simple-marker","color":"#dc160e","size":"7px","outline":{"color":"red","width":0.5}},"label":"90 - 100"},{"minValue":100,"maxValue":1000,"symbol":{"type":"simple-marker","color":"#dd000f","size":"7px","outline":{"color":"red","width":0.5}},"label":"> 100"}]}_labels:black,8,eindoordeel_wbi,uit