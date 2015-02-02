import os
import linecache
import re
import json

KVData = json.loads(open('KVData.json').read())

fileout = open("npc_units_custom.txt", 'w')
 
__location__ = os.path.realpath(
    os.path.join(os.getcwd(), os.path.dirname(__file__)))
 
namedict = {}
unitNames = {}
slks = []
 
#dictionary cointaining position of all 'y' columns
#in unitbalance.slk, *data, *weapons
#bravery
 
bCols = {}
dCols = {}
uCols = {}
wCols = {}

#gets the proper unit names to replace 4 char wc3 unit ids 
for sf in os.listdir(os.getcwd()):
    if 'UnitStrings' in os.path.basename(sf):
        f = open(sf)
        for line in f:
            if '[' in line[0]:
                unitID = line[1:-2]
                unitString = next(f)[5:]
                namedict[unitID] = re.sub("[^a-zA-Z 0-9]", "", unitString)
    if '.slk' in os.path.basename(sf):
        slks.append(sf)
 
unitIndex = 0

#find how many units total
unitMax = int(linecache.getline("UnitBalance.slk", 2).split('Y')[1].split(';')[0])
 
text = ''

#gets the line number of each new row for unitbalance, unitdata, unitweapons.
f = open("UnitBalance.slk")
for num, line in enumerate(f):
    k, temp, v = line[2:].partition(';')
    if 'PWXL' in v:
        continue 
    if 'Y' in k or 'Y' and ';K' in v or 'Y2;'in v:
        bCols[unitIndex] = num
        unitIndex += 1

unitIndex = 0

f = open("UnitData.slk")
for num, line in enumerate(f):
    k, temp, v = line[2:].partition(';')
    if 'PWXL' in v:
        continue
    if 'Y' in k or 'Y' and ';K' in v or 'Y2;'in v:
        dCols[unitIndex] = num
        unitIndex += 1

f = open("UnitUI.slk")
for line in f:
    k, temp, v = line[2:].partition(';')
    if 'PWXL' in v:
        continue
    if 'X8' in k:
        uCols[unitIndex] = num
        unitIndex += 1

unitIndex = 0

f = open("UnitWeapons.slk")
for num, line in enumerate(f):
    k, temp, v = line[2:].partition(';')
    if 'PWXL' in v:
        continue
    if 'Y' in k or 'Y' and ';K' in v or 'Y2;'in v:
        wCols[unitIndex] = num
        unitIndex += 1

unitIndex = 1
#make a dict of all unit names and their corresponding ids
f = open("UnitBalance.slk")
for num, line in enumerate(f):
    if len(line.split(';')) == 3:
        unitKey = line.split(';')[2][1:]
        if re.sub("[^a-zA-Z 0-9]", "", unitKey) in namedict and num > 64:
            v = namedict[re.sub("[^a-zA-Z 0-9]", "", unitKey)]
            unitNames[unitIndex] = v
            unitIndex += 1 


#for each unit, currently limited at 5 for testing, use unitMax if you want all of them
for i in range (1, unitMax - 2):

    fileout.write('"' + unitNames[i].replace(" ","_").strip() + '"' + '\n' + '{' + '\n')
    #for each possible value
    for num in range(bCols[i], bCols[i + 1]):


            #get the line from bCols, which stores the occurence of each new row after the first lot of 
            #definitions and other crap, print bCols to see them
            k, temp, v = linecache.getline("UnitBalance.slk", num)[2:].partition(';')

            #if its a stat change the v/value to correct in dota kv style
            if k == 'X49':
                if '_' in v:
                    k = 'NO'
                if 'INT' in v:
                    v = ' DOTA_ATTRIBUTE_INTELLECT'
                if 'STR' in v:
                    v = ' DOTA_ATTRIBUTE_STRENGTH'
                if 'AGI' in v:
                    v = ' DOTA_ATTRIBUTE_AGILITY'               
            #if the key is one we are looking for, as defined in kvdict_bal
            if k in KVData["UnitBalance"]:
                v = v.lstrip ('K')
                #print("num is " + str(num) + " k is " + k + " v is " + v + " bCols[i] is " + str(bCols[i]) + "num + bcols / line is " + str(bCols[i] + num)) 
                #forgot what this regex does exactly lmao think it tabs it twice, writes the key,
                #puts a " then wirte the value then another " then removes the new line, since
                #i think write makes one anyway 
                text = ('\t\t' + KVData["UnitBalance"][k] + '\t' + '\"' + v.strip("\r\n") + '\"' + '\n')
                fileout.write(text)

    for num in range(dCols[i], dCols[i + 1]):

            k, temp, v = linecache.getline("UnitData.slk", num)[2:].partition(';')

            if k in KVData["UnitData"]:
                v = v.lstrip('K')
                text = ('\t\t' + KVData["UnitData"][k] + '\t' + '\"' + v.strip("\r\n") + '\"' + '\n')
                fileout.write(text)


    for num in range(wCols[i], wCols[i + 1]):

            k, temp, v = linecache.getline("UnitWeapons.slk", num)[2:].partition(';')

            if k == 'X22':
                if 'hero' in v:
                    v = 'DOTA_COMBAT_CLASS_ATTACK_HERO'
                if 'pierce' in v:
                    v = 'DOTA_COMBAT_CLASS_ATTACK_PIERCE'
                if 'normal' in v:
                    v = 'DOTA_COMBAT_CLASS_ATTACK_BASIC'
                if 'magic' in v:
                    k = 'X0'
                    v = 'DAMAGE_TYPE_MAGICAL'
                if 'siege' in v:
                    v = 'DOTA_COMBAT_CLASS_ATTACK_SIEGE'
                if 'chaos' in v:
                    k = 'X0'
                    v = 'DAMAGE_TYPE_PURE'

            if k == 'X23':
                if '_' in  v:
                    v = 'DOTA_UNIT_CAP_NO_ATTACK'
                elif 'normal' in v:
                    v = 'DOTA_UNIT_CAP_MELEE_ATTACK'
                elif 'missile' or 'artillery' in  v:
                    v = 'DOTA_UNIT_CAP_RANGED_ATTACK'

            if k in KVData["UnitWeapons"]:
                v = v.lstrip('K')
                text = ('\t\t' + KVData["UnitWeapons"][k] + '\t' + '\"' + v.strip("\r\n") + '\"' + '\n')
                fileout.write(text)
    fileout.write('}' + '\n')
