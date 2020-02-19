import xml.dom.minidom as minidom
import pandas as pd
in_xml = r'C:\Users\Vincent\Desktop\test\BHR000000004313_IMBRO_A.xml'



doc = minidom.parse(in_xml)

# print doc.nodeName
# print doc.firstChild.tagName

locations = doc.getElementsByTagName("ns8:deliveredLocation")
for location in locations:
    # print coordinate
    coordinates = location.getElementsByTagName("gml:pos")

    for coordinate in coordinates:
        total = coordinate.childNodes[0].nodeValue
        parts = total.split(" ")
        x = float(parts[0])
        y = float(parts[1])

print x,y

    # tree = minidom.parse(project_path)
    # item_group_nodes = tree.getElementsByTagName(item_group_tag)
    # for idx, item_group_node in enumerate(item_group_nodes):
    #     print("{} {} ------------------".format(item_group_tag, idx))
    #     cl_compile_nodes = item_group_node.getElementsByTagName(cl_compile_tag)
    #     for cl_compile_node in cl_compile_nodes:
    #         print("\t{}".format(cl_compile_node.toxml()))








aantal_lagen = len(doc.getElementsByTagName("ns9:upperBoundary"))
bovenkanten = doc.getElementsByTagName("ns9:upperBoundary")
onderkanten = doc.getElementsByTagName("ns9:lowerBoundary")
soorten = doc.getElementsByTagName("ns9:horizonCode")

soort = []
bovenkant = []
onderkant = []






for item in soorten:
    soort.append(item.childNodes[0].nodeValue)

for item in bovenkanten:
    bovenkant.append(float(item.childNodes[0].nodeValue))

for item in onderkanten:
    onderkant.append(float(item.childNodes[0].nodeValue))

dict = {'bovenkant': bovenkant, 'onderkant': onderkant, 'soort': soort}
df = pd.DataFrame(dict)
df['dikte_laag'] = abs(df['bovenkant']-df['onderkant'])

print df
