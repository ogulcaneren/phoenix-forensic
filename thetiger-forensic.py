import time, csv, re, os
import argparse as ap
from pathlib import Path


def process(type, whitelist, blacklist):
    if blacklist != None:
        blacklistRegex = '|'.join(w for w in blacklist)
    else:
        blacklistRegex = ""

    if whitelist != None:
        whitelistRegex = '^' + ''.join('(?=.*' + w + ')' for w in whitelist)
    else:
        whitelistRegex = ""

    ##Cikti dosyasinin olusturulmasi + aranacak dosya ismini belirleme
    csvname = '\\' + str(time.strftime("%d-%m-%Y--%H_%M_%S")) + '_'

    if type == 'a':
        fileExt = '*UnassociatedFileEntries.csv'
        csvname += 'Amcache_'
    elif type == 's':
        fileExt = '*AppCompatCache.csv'
        csvname += 'Shimcache_'

    if (whitelist == None) & (blacklist == None):
        csvname += 'Merge.csv'
    elif whitelist != None:
        csvname += 'WhiteList.csv'
    elif blacklist != None:
        csvname += 'BlackList.csv'
    #######################################
    ## cikti dosyasi olusturup baslik basma
    with open(args.path + csvname, "a") as thecsvfile:
        if type == 'a': thecsvfile.write("FileKeyLastWriteTimestamp,SHA1,FullPath,Name,Hostname\n")
        if type == 's': thecsvfile.write("Path,LastModifiedTimeUTC,Executed,Hostname\n")
        thecsvfile.close()
    ###
    for filePath in Path(args.path).rglob(fileExt):
        hostname = filePath.parts[-3].split("ParsedArtifacts")[1]
        with open(filePath) as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=',')
            for row in csv_reader:
                if type == 'a':
                    newRow = row[2] + ',' + row[3] + ',' + row[5] + ',' + row[6] + ',' + hostname + '\n'
                if type == 's':
                    newRow = row[2] + ',' + row[3] + ',' + row[4] + ',' + hostname + '\n'
                if (blacklist != None) & (re.search(blacklistRegex,
                                                    newRow) != None):  # Search'a üçüncü parametre olarak re.I verirsen case sensitivei kapatır
                    continue
                if (whitelist != None) & (re.search(whitelistRegex, newRow) == None):
                    continue
                if (re.search('Path,LastModifiedTimeUTC,Executed', newRow) != None) | (
                        re.search('FileKeyLastWriteTimestamp,SHA1,FullPath,Name', newRow) != None):
                    continue
                with open(args.path + csvname, "a") as thecsvfile:
                    thecsvfile.write(newRow)
                    thecsvfile.close()
            csv_file.close()

    if sum(1 for line in open(args.path + csvname)) <= 1:
        os.remove(args.path + csvname)
        return "ERROR: No records found"
    else:
        return "DONE! Results written to: " + args.path + csvname


parser = ap.ArgumentParser(description='Description of your program', add_help=True)
query_group = parser.add_argument_group('Query Type')
parser.add_argument('-p', action='store', dest='path', help='FullPath to Kape folder', required=True)
parser.add_argument('-t', action='store', dest='type', choices=('s', 'a', 'b'),
                    help="Choose analyze type: s  for shimcache, a for amcache, b for both", required=True)
query_group.add_argument('--blacklist', help='Choose a blacklist query for get only specified', dest='blacklist',
                         action='store', required=False, nargs='+')
query_group.add_argument('--whitelist', action='store', dest='whitelist',
                         help='Choose whitelist query for get only specified', required=False, nargs='+')

timestr: str = time.strftime("%d%m%Y-%H%M%S")
args = parser.parse_args()

print("\n")
if args.type == 'b':
    print("Amcache: " + process('a', args.whitelist, args.blacklist))
    print("Simcache: " + process('s', args.whitelist, args.blacklist))
elif args.type == 'a':
    print("Amcache: " + process(args.type, args.whitelist, args.blacklist))
elif args.type == 's':
    print("Simcache: " + process(args.type, args.whitelist, args.blacklist))
