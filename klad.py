
in_xml = r'C:\Users\Vincent\Desktop\test\BHR000000004313_IMBRO_A.xml'

import xml.dom.minidom as minidom

doc = minidom.parse(in_xml)

# print doc.nodeName
# print doc.firstChild.tagName

aantal_lagen = len(doc.getElementsByTagName("ns9:upperBoundary"))
bovenkanten = doc.getElementsByTagName("ns9:upperBoundary")
onderkanten = doc.getElementsByTagName("ns9:lowerBoundary")
soorten = doc.getElementsByTagName("ns9:horizonCode")


for item in bovenkanten:
    print item.childNodes[0].nodeValue

for item in soorten:
    print item.childNodes[0].nodeValue




# test_bovenkant_ = doc.getElementsByTagName("ns9:upperBoundary")[1].childNodes[0].nodeValue
# test_onderkant = doc.getElementsByTagName("ns9:lowerBoundary")[1].childNodes[0].nodeValue
# print test_bovenkant_,test_onderkant
