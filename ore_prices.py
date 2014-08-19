import urllib
import xml.etree.ElementTree as ET


class Config:
    def __init__(self):
        self.tid = {}
        self.names = {}
        self.regions = {}
        self.systems = {}

    def load_typeid(self,filename):
        with open(filename) as f:
            for line in f:
                val = line.split()
                name = " ".join(val[1:])
                self.tid[name] = val[0]
                self.names[val[0]] = name

    def load_systemid(self,filename):
        with open(filename) as f:
            f.readline()
            for line in f:
                val = line.split(',')
                self.systems[val[3]] = val[2]

    def load_regionid(self,filename):
        with open(filename) as f:
            f.readline()
            for line in f:
                val = line.split(',')
                self.regions[val[1]] = val[0]

    def t2q(self, name):
        return "typeid="+self.tid[name]

    def r2q(self, region_name):
        return "regionlimit="+self.regions[region_name]

    def s2q(self, system_name):
        return "usesystem="+self.systems[system_name]


glob = Config()
glob.load_typeid('typeid.txt')
glob.load_systemid('mapSolarSystems.csv')
glob.load_regionid('mapRegions.csv')

class Stats:
    def __init__(self,item):
        self.item = item
        self.min = self.item.find('min').text
        self.max = self.item.find('max').text
        self.avg = self.item.find('avg').text

    def __repr__(self):
        return self.min+"/"+self.max+"/"+self.avg


class StatItem:
    def __init__(self,tid, item):
        self.tid = tid
        self.name = glob.names[tid]
        self.buy = Stats(item.find('buy'))
        self.sell = Stats(item.find('sell'))

    def __repr__(self): return "Stat: "+self.name

class MarketStat:
    def __init__(self):
        self.baseurl = 'http://api.eve-central.com/api/marketstat?'

    def market_query(self, types, regions=[], systems=[]):
        query = self.baseurl + glob.t2q(types[0])
        for t in types[1:]:
            query = query + '&' + glob.t2q(t)
        for r in regions:
            query = query + '&' + glob.r2q(r)
        for s in systems:
            query = query + '&' + glob.s2q(s)

        #print "QUERY: " + query

        xml_str = urllib.urlopen(query).read()
        self.res = ET.fromstring(xml_str).find('marketstat')
        items = []
        for item in self.res:
            tid = item.attrib['id']
            items.append(StatItem(tid, item))
        return items

def calc_ore_prices(system, cargo_size):
    res = m.market_query(ores,systems=[system])
    res_sorted = []
    for i in range(len(res)):
        iks_max = float(res[i].buy.max)
        iks_m3 = float(iks_max/volumes[i])*cargo_size
        res_sorted.append( (iks_m3, iks_max, float(res[i].sell.min), res[i].name) )

    res_sorted.sort(reverse=True)
    print "Ore prices ISK/m3 in "+system
    for i in res_sorted:
        print '%.0f, %.2f, %.2f, %s' % i
    print "\n"


m = MarketStat()
ores = ['Veldspar',
        'Concentrated Veldspar',
        'Dense Veldspar',
        'Scordite',
        'Condensed Scordite',
        'Massive Scordite',
        'Pyroxeres',
        'Solid Pyroxeres',
        'Viscous Pyroxeres',
        'Plagioclase',
        'Azure Plagioclase',
        'Rich Plagioclase',
        'Omber',
        'Silvery Omber',
        'Golden Omber',
        'Kernite',
        'Luminous Kernite',
        'Fiery Kernite']

volumes = [.1,.1,.1,
           .15,.15,.15,
           .3,.3,.3,
           .35,.35,.35,
           .6,.6,.6,
           1.2,1.2,1.2]

cargo = 5000.


calc_ore_prices('Rens',cargo)
calc_ore_prices('Amarr',cargo)
calc_ore_prices('Jita',cargo)
calc_ore_prices('Dodixie',cargo)
