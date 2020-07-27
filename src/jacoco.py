import os
import json
import shutil
from xml.dom import minidom
from flowci import domain, client
from jacoco_html import Merge
from util import GetOutputDir

def default(o):
    return o._asdict()


class Package:
    def __init__(self, xmlNode):
        self.name = xmlNode.attributes["name"].value
        self.counters = []

    def __str__(self):
        return "[{}]".format(self.name)

    def _asdict(self):
        return self.__dict__


class Counter:
    def __init__(self, xmlNode):
        self.type = xmlNode.attributes['type'].value
        self.missed = int(xmlNode.attributes['missed'].value)
        self.covered = int(xmlNode.attributes['covered'].value)

    def add(self, counter):
        self.missed += counter.missed
        self.covered += counter.covered

    def __str__(self):
        return "[{}] missed: {}, covered: {}".format(self.type, self.missed, self.covered)

    def _asdict(self):
        return self.__dict__


def parse(xmlFile):
    reportDoc = minidom.parse(xmlFile)
    root = reportDoc.getElementsByTagName('report')
    packages = []

    for node in root[0].childNodes:
        if node.nodeName != "package":
            continue

        package = Package(node)

        for cNode in node.childNodes:
            if cNode.nodeName == "counter":
                package.counters.append(Counter(cNode))

        packages.append(package)

    return packages


def sendStatistic(packages):
    types = {}

    for p in packages:
        for c in p.counters:
            if c.type not in types:
                types[c.type] = c

            types[c.type].add(c)

    for key in types:
        d = types[key]

        body = {
            "type": "jacoco_" + d.type,
            "data": {
                "missed": d.missed,
                "covered": d.covered
            }
        }

        api = client.Client()
        status = api.sendStatistic(body)
        print(
            "[plugin-maven-test]: jacoco {} statistic data sent {}".format(d.type, status))

def listFiles(dirName):
  filePaths = []
   
  for root, directories, files in os.walk(dirName):
    for filename in files:
        filePath = os.path.join(root, filename)
        filePaths.append(filePath)
         
  return filePaths

def sendReport(reports):
    outputDir = GetOutputDir()
    jacocoDir = os.path.join(outputDir, "jacoco")
    Merge(reports, jacocoDir)

    zipFile = os.path.join(outputDir, "jacoco-report")
    zipFile = shutil.make_archive(zipFile, 'zip', jacocoDir)

    api = client.Client()
    status = api.sendJobReport(
        path=zipFile, 
        name=domain.JobReportCodeCoverage,
        zipped="true",
        contentType=domain.ContentTypeHtml,
        entryFile="index.html"
    )

    print("[plugin-maven-test]: upload jacoco report with status {}".format(status))


def start():
    reports = client.FindFiles("jacoco.xml")

    if len(reports) == 0:
        print("[plugin-maven-test]: jacoco.xml not found")
        return

    # report
    sendReport(reports)

    packages = []
    for report in reports:
        packages += parse(report)

    # statistic for all modules
    # sendStatistic(packages)

start()
