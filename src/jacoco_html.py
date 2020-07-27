import os
import sys
import shutil
from bs4 import BeautifulSoup

def createOutDir(dir):
    try:
        if os.path.exists(dir):
            shutil.rmtree(dir)
        os.mkdir(dir)
    except FileExistsError:
        pass


def copyDir(src, dest):
    try:
        if os.path.exists(dest):
            shutil.rmtree(dest)
        shutil.copytree(src, dest)
    except FileExistsError:
        pass


def findJacocoHtml(xmlFiles):
    htmls = []
    for xmlPath in xmlFiles:
        jacocoDir = os.path.dirname(xmlPath)
        htmlFile = os.path.join(jacocoDir, "index.html")
        if os.path.exists(htmlFile):
            htmls.append(htmlFile)
    return htmls


def copyPackages(htmlFiles, dest):
    for f in htmlFiles:
        jacocoDir = os.path.dirname(f)
        for package in os.listdir(jacocoDir):
            packagePath = os.path.join(jacocoDir, package)
            if os.path.isdir(packagePath):
                destPath = os.path.join(dest, package)
                copyDir(packagePath, destPath)


def mergeHtml(htmlFiles, dest):
    dest = os.path.join(dest, "index.html")
    baseSoup = None

    with open(htmlFiles[0]) as f:
        baseSoup = BeautifulSoup(f, features="html.parser")

    for f in htmlFiles[1:]:
        with open(f) as f:
            soup = BeautifulSoup(f, features="html.parser")
            
            header = soup.body.div
            title = soup.body.h1
            table = soup.body.table

            baseSoup.body.append(header)
            baseSoup.body.append(title)
            baseSoup.body.append(table)

    with open(dest, "w", encoding='utf-8') as f:
        f.write(str(baseSoup))


def Merge(xmlFiles, destDir):
    createOutDir(destDir)

    htmlFiles = findJacocoHtml(xmlFiles)

    copyPackages(htmlFiles, destDir)
    mergeHtml(htmlFiles, destDir)
