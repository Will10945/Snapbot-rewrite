import copy
import json
import random

from lib.utils.file_utils import get_relic_data, get_prime_access_list, update_relic_numbers, get_relic_numbers, get_gen_relic_filepaths, \
                                 new_gen_relics_data, new_gen_relics

gen_relic_f = get_gen_relic_filepaths()
relics = get_relic_data()
prime_access = get_prime_access_list()

ctrash = [
    'Lex',
    'Fang'
]
unctrash = [
    'Bronco',
    'Braton',
    'Burston',
    'Paris'
]
orthos = 'Orthos'

def partrarity():
    data = {}
    relic_names = {}

    for relic in relics:
        #print('for relic in relics')
        for part in relics[relic]['Intact']['drops']:
            #print('for part in relics[][][]')
            if 'Forma' not in part:

                setname = str(part.split(' Prime')[0]+' Prime')
                partname = str(part.split('Prime ')[1])
                if len(partname.split(' ')) == 2:
                    partname = partname.split(' ')[0]
                partducats = relics[relic]['Intact']['drops'][part]['ducats']
                partrarity = 'Common' if partducats == 15 else 'Common' if partducats == 25 else 'Uncommon' if partducats == 45 else 'Uncommon' if partducats == 65 else 'Rare'
                partvalue = 1 if partducats == 15 else 2 if partducats == 25 else 3 if partducats == 45 else 4 if partducats == 65 else 5
                if 'Volt Prime Neuroptics' in part or 'Odonata Prime Wings' in part or 'Ash Prime Systems' in part or 'Kavasa Prime Buckle' in part:
                    partrarity = 'Rare'
                if 'Saryn Prime Neuroptics' in part or 'Akstiletto Prime Receiver' in part:
                    partrarity = 'Common'
                    partvalue = int(3)
                    
                if len(data) == 0:
                    data['Sets'] = {
                        setname: {
                            partname: {
                                'ducats': partducats,
                                'rarity': partrarity,
                                'rarity value': int(partvalue)
                            }
                        }
                    }
                else:
                    if setname not in data['Sets']:
                        data['Sets'][setname] = {
                            partname: {
                                'ducats': partducats,
                                'rarity': partrarity,
                                'rarity value': int(partvalue)
                            }
                        }
                    else:
                        if partname not in data['Sets'][setname]:
                            data['Sets'][setname][partname] = {
                                'ducats': partducats,
                                'rarity': partrarity,
                                'rarity value': int(partvalue)
                            }

        if(len(relic_names) == 0 or relic.split(' ')[0] not in relic_names):
            relic_names[relic.split(' ')[0]] = {
                relic.split(' ')[1][0]: 1
            }
        elif(relic.split(' ')[1][0] not in relic_names[relic.split(' ')[0]]):
            relic_names[relic.split(' ')[0]][relic.split(' ')[1][0]] = 1
        else:
            relic_names[relic.split(' ')[0]][relic.split(' ')[1][0]] += 1

    relic_names['Neo']['S'] += 1

    update_relic_numbers(relic_names)
    with open(gen_relic_f['part_rarity'], 'w') as f0:
        json.dump(data, f0, indent=4)


    #print('\n\nPart list reloaded')

def updown(commons, uncommons, rares, dupebool):

    rtou = {}
    utoc = {}
    utor = {}
    prio1 = []
    prio0 = []
    rareslist = list(rares)

    #Duplicate Rare parts or upgrade Uncommon parts
    
    if len(rares) < 4 or len(rares)*2 <= len(uncommons)+2 or len(rares)*3 <= len(commons)+3:

        prio1 = list([k for k,v in rares.items() if v['priority'] == 1])
        prio0 = list([k for k,v in rares.items() if v['priority'] == 0])

        prio0unc = list([k for k,v in uncommons.items() if v['priority'] == 0])
        prio0unc65 = list([k for k,v in uncommons.items() if (v['priority'] == 0 and v['rarity value'] == 4)])

        #print(prio1)
        #print(prio0)
        #print(prio0unc65)

        while len(rares)+len(utor) < 4 or (len(rares)+len(utor))*2 < len(uncommons) or (len(rares)+len(utor))*3 < len(commons):
            #print('<4 rares loop')
            if(len(prio0unc65) > 0):
                random.shuffle(prio0unc65)
                #print('upgrading prio 0 uncommon to rare')
                #print(prio0unc65[0] + ' selected')
                utor[prio0unc65[0]] = uncommons[prio0unc65[0]]
                if len(rares)+len(utor) < 4 or (len(rares)+len(utor))*2 < len(uncommons) or (len(rares)+len(utor))*3 < len(commons):
                    utor[prio0unc65[0] + ' 2'] = uncommons[prio0unc65[0]]
                del(uncommons[prio0unc65[0]])
                del(prio0unc65[0])
            
            elif(len(prio0) > 0):
                random.shuffle(prio0)
                #print('Duplicating rares with prio 0')
                #print(prio0[0] + ' selected')
                utor[prio0[0]] = rares[prio0[0]]
                utor[prio0[0] + ' 2'] = rares[prio0[0]]
                del(rares[prio0[0]])
                del(prio0[0])
            
            elif(len(prio1) > 0):
                random.shuffle(prio1)
                #print('duplicating rares with prio 1')
                #print(prio1[0] + ' selected')
                utor[prio1[0]] = rares[prio1[0]]
                utor[prio1[0] + ' 2'] = rares[prio1[0]]
                del(rares[prio1[0]])
                del(prio1[0])

            elif len(prio0unc) > 0:
                random.shuffle(prio0unc)
                #print('upgrading prio 0 uncommon to rare')
                #print(prio0unc[0] + ' selected')
                utor[prio0unc[0]] = uncommons[prio0unc[0]]
                if len(rares)+len(utor) < 4 or (len(rares)+len(utor))*2 < len(uncommons) or (len(rares)+len(utor))*3 < len(commons):
                    utor[prio0unc[0] + ' 2'] = uncommons[prio0unc[0]]
                del(uncommons[prio0unc[0]])
                del(prio0unc[0])


        rares.update(utor)

    #Downgrade Rare Parts
    
    elif len(rares) > 4 or len(rares) >= len(uncommons) - 3 or len(rares)*2 > len(commons):

        i = int(0)
        duperaresprio0 = []
        duperaresprio1 = []
        prio0rare65 = []
        prio1rare65 = []

        #print(rares)
        #print(f"- - -\n{len(rares)}\n{len(uncommons)}\n{len(commons)}\n- - -")

        for k in range(len(rareslist) - 1):
            #print('finding dupe rare downgrades')
            if rareslist[k].split(' Prime')[0] == rareslist[k+1].split(' Prime')[0]:
                j = random.randint(0,1)

                if rares[rareslist[k + j]]['priority'] == 0:
                    duperaresprio0.append(rareslist[k + j])
                else:
                    duperaresprio1.append(rareslist[k + j])

                del(rareslist[k + j])
                i+=1

            if(len(rareslist) - i - 1 <= k):
                break

        for k in range(len(rareslist)):
            #print('finding previously upgraded rare downgrades')
            if rares[rareslist[k]]['priority'] == 0:
                if rares[rareslist[k]]['rarity value'] == 4:
                    prio0rare65.append(rareslist[k])
                else:
                    prio0.append(rareslist[k])
            else:
                if rares[rareslist[k]]['rarity value'] == 4:
                    prio1rare65.append(rareslist[k])
                else:
                    prio1.append(rareslist[k])

        #print(f"{len(rares)}   {len(uncommons)}   {len(commons)}")
        forcebreak = 0
        while len(rares) > (len(uncommons) + len(rtou))/2 + 2 and len(rares) > len(commons)/2 + 2:
            if forcebreak >= 200:
                break
            forcebreak += 1
            #print('too many rares loop')
            #print(f"{len(rares)}   {(len(uncommons) + len(rtou))/2 + 2}  |  {len(commons)/2 + 2}")
            if(len(duperaresprio0) > 0):
                random.shuffle(duperaresprio0)
                #print('Downgrading rare duplicate prio 0 part: ' + duperaresprio0[0])
                rtou[duperaresprio0[0]] = rares[duperaresprio0[0]]
                rtou[duperaresprio0[0]]['rarity value'] = 4
                del(rares[duperaresprio0[0]])
                del(duperaresprio0[0])

            elif(len(duperaresprio1) > 0):
                random.shuffle(duperaresprio1)
                #print('Downgrading rare duplicate prio 1 part: ' + duperaresprio1[0])
                rtou[duperaresprio1[0]] = rares[duperaresprio1[0]]
                rtou[duperaresprio1[0]]['rarity value'] = 4
                del(rares[duperaresprio1[0]])
                del(duperaresprio1[0])

            elif(len(prio0rare65) > 0):
                #print('Downgrading rare unique 65 duc prio 0 part')
                random.shuffle(prio0rare65)
                rtou[prio0rare65[0]] = rares[prio0rare65[0]]
                rtou[prio0rare65[0]]['rarity value'] = 4
                del(rares[prio0rare65[0]])
                del(prio0rare65[0])

            elif(len(prio1rare65) > 0):
                #print('Downgrading rare unique 65 duc prio 1 part')
                random.shuffle(prio1rare65)
                rtou[prio1rare65[0]] = rares[prio1rare65[0]]
                rtou[prio1rare65[0]]['rarity value'] = 4
                del(rares[prio1rare65[0]])
                del(prio1rare65[0])
            
            elif(len(prio0) > 0):
                #print('Downgrading rare unique prio 0 part')
                random.shuffle(prio0)
                rtou[prio0[0]] = rares[prio0[0]]
                rtou[prio0[0]]['rarity value'] = 4
                del(rares[prio0[0]])
                del(prio0[0])

            elif(len(prio1) > 0):
                #print('Downgrading rare unique prio 1 part')
                random.shuffle(prio1)
                rtou[prio1[0]] = rares[prio1[0]]
                rtou[prio1[0]]['rarity value'] = 4
                del(rares[prio1[0]])
                del(prio1[0])

        uncommons.update(rtou)
        #print('- - -')
        #print(rares)
        #print('- - -')

    if len(uncommons)*3 - 1 > (len(commons) + len(utoc))*2:
        uncommonslist = list(uncommons)
        while len(uncommons)*3 > (len(commons) + len(utoc))*2:
            #print('Uncommon downgrade loop')
            random.shuffle(uncommonslist)
            #print(uncommonslist)
            uindex = 0
            stopdowngrading = False
            for i in range(len(uncommonslist)):
                #print('downgrade parts with rarity value 3 loop')
                if uncommons[uncommonslist[0]]['rarity value'] == 3:
                    uindex = i
                    break
                if i >= len(uncommonslist) - 1:
                    stopdowngrading = True
            if stopdowngrading:
                break
            #print('uncommon downgrade: ' + uncommonslist[0])
            utoc[uncommonslist[uindex]] = uncommons[uncommonslist[uindex]].copy()
            utoc[uncommonslist[uindex]]['rarity value'] = 2
            #print(f"Downgrading {uncommonslist[uindex]}")
            del(uncommons[uncommonslist[uindex]])
            del(uncommonslist[uindex])

        commons.update(utoc)

        #print(f"- - - -\n{commons}\n\n{uncommons}\n\n{rares}\n- - - -")

    with open(gen_relic_f['part_rarity'], 'r') as f:
        praritydict = json.load(f)

    if dupebool:

        #print('Duplicating commons/uncommons')

        cprio1 = []
        cprio0 = []
        uprio1 = []
        uprio0 = []
        cprio125 = []
        cprio025 = []
        uprio165 = []
        uprio065 = []

        for k,v in commons.items():
            #print('for k. v in commons.items')
            if commons[k]['priority'] == 0:
                if commons[k]['rarity value'] == 2:
                    cprio025.append(k)
                else:
                    cprio0.append(k)
            else:
                if commons[k]['rarity value'] == 2:
                    cprio125.append(k)
                else:
                    cprio1.append(k)
        
        for k,v in uncommons.items():
            #print('for k, v in uncommons.items')
            if uncommons[k]['priority'] == 0:
                if uncommons[k]['rarity value'] == 4:
                    uprio065.append(k)
                else:
                    uprio0.append(k)
            else:
                if uncommons[k]['rarity value'] == 4:
                    uprio165.append(k)
                else:
                    uprio1.append(k)

        random.shuffle(cprio0)
        random.shuffle(cprio025)
        random.shuffle(cprio1)
        random.shuffle(cprio125)
        random.shuffle(uprio0)
        random.shuffle(uprio065)
        random.shuffle(uprio1)
        random.shuffle(uprio165)

        commonstemp = {}
        uncommonstemp = {}

        if len(commons) + len(cprio0) + len(cprio1) < len(rares)*3:
            #print('Doubling 15 duc prio1 and 0 commons')
            for x in cprio0:
                commonstemp[x + ' 2'] = commons[x].copy()
            for x in cprio1:
                commonstemp[x + ' 2'] = commons[x].copy()
            commons.update(commonstemp)
            commonstemp = {}

        elif len(cprio0) + len(commons) < len(rares)*3:
            #print('Duplicating prio0 commons')

            for i in range(len(cprio0)):
                commons[cprio0[i] + ' 2'] = commons[cprio0[i]].copy()
            
            if len(commons) < len(rares)*3 - 1:
                #print('Duplicating prio1 parts because not enough prio0')

                while len(commons) < len(rares)*3 - 1 and len(cprio1) > 0:
                    commons[cprio1[0] + ' 2'] = commons[cprio1[0]].copy()
                    del(cprio1[0])

            if len(commons) + len(cprio025) < len(rares)*3:
                #print('Doubling 25 duc prio0 commons')
                #print(cprio025)
                for x in cprio025:
                    commonstemp[k + ' 2'] = commons[x].copy()
                commons.update(commonstemp)
                commonstemp = {}

            if len(commons) + len(cprio125) < len(rares)*3:
                #print('Doubling 25 duc prio1 commons')
                #print(cprio125)
                for x in cprio125:
                    commonstemp[k + ' 2'] = commons[x].copy()
                commons.update(commonstemp)
                commonstemp = {}
        
        while len(commons) < len(rares)*3 and len(cprio0) > 0:
            #print('Adding more prio0 parts because ' + str(len(commons)) + ' < ' + str(len(rares)*3-1))
            random.shuffle(cprio0)
            if cprio0[0] + ' 2' in list(commons):
                commons[cprio0[0] + ' 2 2'] = commons[cprio0[0]].copy()
            else:
                commons[cprio0[0] + ' 2'] = commons[cprio0[0]].copy()
            #print(cprio0[0])
            del(cprio0[0])

        while len(commons) < len(rares)*3 and len(cprio1) > 0:
            #print('Adding more prio1 parts because ' + str(len(commons)) + ' < ' + str(len(rares)*3-1))
            random.shuffle(cprio1)
            if cprio1[0] + ' 2' in list(commons):
                commons[cprio1[0] + ' 2 2'] = commons[cprio1[0]].copy()
            else:
                commons[cprio1[0] + ' 2'] = commons[cprio1[0]].copy()
            #print(cprio1[0])
            del(cprio1[0])
        

        nou45left = False
        initlenu = len(uncommons)
        if len(uncommons) + len(uprio0) + len(uprio1) < len(rares)*2-1:
            #print('enough space to dupe uprio0 and uprio1')
            for x in uprio0:
                uncommonstemp[x + ' 2'] = uncommons[x].copy()
            for x in uprio1:
                uncommonstemp[x + ' 2'] = uncommons[x].copy()
            uncommons.update(uncommonstemp)
            uncommonstemp = {}
        
        uprio0used = False
        if len(uncommons) + len(uprio0) < len(rares)*2-1:
            #print('enough space to dupe all uprio0')
            for x in uprio0:
                uncommonstemp[x + ' 2'] = uncommons[x].copy()
            if len(uncommonstemp) == len(uprio0):
                uprio0used = True
            uncommons.update(uncommonstemp)
            uncommonstemp = {}

        if uprio0used and len(uncommons) + len(uprio1) < len(rares)*2-1:
            #print('uprio0 duped, need all of uprio1')
            for x in uprio1:
                uncommonstemp[x + ' 2'] = uncommons[x].copy()
            uncommons.update(uncommonstemp)
            uncommonstemp = {}

        if uprio0used:
            while len(uncommons) < len(rares)*2-1 and len(uprio1) > 0:
                #print('duplicating prio1 parts')
                if uprio1[0] + ' 2' in uncommons:
                    uncommons[uprio1[0] + ' 2 2'] = uncommons[uprio1[0]].copy()
                else:
                    uncommons[uprio1[0] + ' 2'] = uncommons[uprio1[0]].copy()
                del(uprio1[0])

            while len(uncommons) < len(rares)*2-1 and len(uprio065) > 0:
                #print('duplicating 65 duc prio0 parts')
                if uprio065[0] + ' 2' in uncommons:
                    uncommons[uprio065[0] + ' 2 2'] = uncommons[uprio065[0]].copy()
                else:
                    uncommons[uprio065[0] + ' 2'] = uncommons[uprio065[0]].copy()
                del(uprio065[0])

            while len(uncommons) < len(rares)*2-1 and len(uprio165) > 0:
                #print('duplicating 65 duc prio1 parts')
                if uprio165[0] + ' 2' in uncommons:
                    uncommons[uprio165[0] + ' 2 2'] = uncommons[uprio165[0]].copy()
                else:
                    uncommons[uprio165[0] + ' 2'] = uncommons[uprio165[0]].copy()
                del(uprio165[0])

            while len(uncommons) < len(rares)*2-1 and len(uprio0) > 0:
                #print('duplicating prio0 parts AGAIN')
                if uprio0[0] + ' 2' in uncommons:
                    uncommons[uprio0[0] + ' 2 2'] = uncommons[uprio0[0]].copy()
                else:
                    uncommons[uprio0[0] + ' 2'] = uncommons[uprio0[0]].copy()
                del(uprio0[0])
        else:
            while len(uncommons) < len(rares)*2-1 and len(uprio0) > 0:
                #print('duplicating prio0 parts')
                if uprio0[0] + ' 2' in uncommons:
                    uncommons[uprio0[0] + ' 2 2'] = uncommons[uprio0[0]].copy()
                else:
                    uncommons[uprio0[0] + ' 2'] = uncommons[uprio0[0]].copy()
                del(uprio0[0])

            while len(uncommons) < len(rares)*2-1 and len(uprio1) > 0:
                #print('duplicating prio1 parts')
                if uprio1[0] + ' 2' in uncommons:
                    uncommons[uprio1[0] + ' 2 2'] = uncommons[uprio1[0]].copy()
                else:
                    uncommons[uprio1[0] + ' 2'] = uncommons[uprio1[0]].copy()
                del(uprio1[0])

        #print(str(initlenu + len(uprio0) + len(prio1)) + ' ?= ' + str(len(uncommons)))

        if len(uprio0) + len(uprio1) == 0:
            nou45left = True


    elif not dupebool or len(commons) < len(rares)*3 - 1:

        ctrashsets = ctrash.copy()
        unctrashsets = unctrash.copy()

        if len(rares)*3 >= len(commons) + 1 and len(rares)*2 >= len(uncommons) + 2 and len(ctrashsets) > 0:
        
            psets = orthos
            #print('Adding ' + psets + ' as orthos trash')

            for part in praritydict['Sets'][psets + ' Prime']:
                #print('for part in partraritydict[][]')
                if praritydict['Sets'][psets + ' Prime'][part]['rarity'] == 'Common':
                    partname = psets + ' Prime ' + part
                    while partname in list(commons):
                        #print('while partname in list(commons)')
                        partname = partname + ' 2'
                    commons[partname] = {
                        'rarity value': praritydict['Sets'][psets + ' Prime'][part]['rarity value'],
                        'uses': int(0),
                        'priority': int(0)
                    }
                if praritydict['Sets'][psets + ' Prime'][part]['rarity'] == 'Uncommon':
                    partname = psets + ' Prime ' + part
                    while partname in list(uncommons):
                        #print('while partname in list(uncommons)')
                        partname = partname + ' 2'
                    uncommons[partname] = {
                        'rarity value': praritydict['Sets'][psets + ' Prime'][part]['rarity value'],
                        'uses': int(0),
                        'priority': int(0)
                    }

        while len(rares)*3 >= len(commons) + 4 and len(rares)*2 >= len(uncommons) + 2 and len(unctrashsets) > 0:
            trashindex = random.randint(0, len(unctrashsets)-1)
            psets = unctrashsets[trashindex]
            #del(unctrashsets[trashindex])
            #print('Adding ' + psets + ' as uncommon trash')
            #print('uncommon trash slotting loop')

            for part in praritydict['Sets'][psets + ' Prime']:
                #print('uncommon trash slotting inner loop')
                if praritydict['Sets'][psets + ' Prime'][part]['rarity'] == 'Common':
                    partname = psets + ' Prime ' + part
                    while partname in list(commons):
                        partname = partname + ' 2'
                    commons[partname] = {
                        'rarity value': praritydict['Sets'][psets + ' Prime'][part]['rarity value'],
                        'uses': int(0),
                        'priority': int(0)
                    }
                if praritydict['Sets'][psets + ' Prime'][part]['rarity'] == 'Uncommon':
                    partname = psets + ' Prime ' + part
                    while partname in list(uncommons):
                        partname = partname + ' 2'
                    uncommons[partname] = {
                        'rarity value': praritydict['Sets'][psets + ' Prime'][part]['rarity value'],
                        'uses': int(0),
                        'priority': int(0)
                    }

        while len(commons) <= len(rares)*3 - 4 and len(ctrashsets) > 0:
            trashindex = random.randint(0, len(ctrashsets)-1)
            psets = ctrashsets[trashindex]
            #del(ctrashsets[trashindex])
            #print('Adding ' + psets + ' as common trash')
            #print('common trash slotting loop')

            for part in praritydict['Sets'][psets + ' Prime']:
                #print('common trash slotting inner loop')
                if praritydict['Sets'][psets + ' Prime'][part]['rarity'] == 'Common':
                    partname = psets + ' Prime ' + part
                    while partname in list(commons):
                        partname = partname + ' 2'
                    commons[partname] = {
                        'rarity value': praritydict['Sets'][psets + ' Prime'][part]['rarity value'],
                        'uses': int(0),
                        'priority': int(0)
                    }

    
    #print(f"- - - -\n{commons}\n\n{uncommons}\n\n{rares}\n- - - -")

    return commons, uncommons, rares

def allocaterarities(framesets, stuffsets, dupebool):
    sets = framesets + stuffsets
    commons = {}
    uncommons = {}
    rares = {}

    with open(gen_relic_f['part_rarity'], 'r') as f:
        praritydict = json.load(f)
    
    #print(sets)

    excalpartlist = ['Blueprint', 'Chassis', 'Neuroptics', 'Systems']
    latopartlist = ['Blueprint', 'Barrel', 'Receiver']
    skanapartlist = ['Blueprint', 'Blade', 'Hilt']

    for psets in sets:
        #print('allocaterarities loop')
        if psets == 'Excalibur':
            random.shuffle(excalpartlist)
            for x in range(len(excalpartlist)):
                #print('excal parts')
                if x == 0:
                    rares['Excalibur Prime ' + excalpartlist[x]] = {
                        'rarity value': 5,
                        'uses': int(0),
                        'priority': int(1)
                    }
                elif x == 1:
                    uncommons['Excalibur Prime ' + excalpartlist[x]] = {
                        'rarity value': 3,
                        'uses': int(0),
                        'priority': int(1)
                    }
                elif x == 2:
                    commons['Excalibur Prime ' + excalpartlist[x]] = {
                        'rarity value': 1,
                        'uses': int(0),
                        'priority': int(1)
                    }
                elif x == 3:
                    commons['Excalibur Prime ' + excalpartlist[x]] = {
                        'rarity value': 1,
                        'uses': int(0),
                        'priority': int(1)
                    }

        elif psets == 'Lato' or psets == 'Skana':
            random.shuffle(skanapartlist)
            random.shuffle(latopartlist)
            for x in range(3):
                #print('lato/skana loop')
                if x == 0:
                    rares[psets + ' Prime ' + (latopartlist[x] if psets == 'Lato' else skanapartlist[x])] = {
                        'rarity value': 5,
                        'uses': int(0),
                        'priority': int(0)
                    }
                elif x == 1:
                    uncommons[psets + ' Prime ' + (latopartlist[x] if psets == 'Lato' else skanapartlist[x])] = {
                        'rarity value': 3,
                        'uses': int(0),
                        'priority': int(0)
                    }
                elif x == 2:
                    commons[psets + ' Prime ' + (latopartlist[x] if psets == 'Lato' else skanapartlist[x])] = {
                        'rarity value': 1,
                        'uses': int(0),
                        'priority': int(0)
                    }

        else:
            for part in praritydict['Sets'][psets + ' Prime']:
                #print('allocaterarities inner loop with real parts')
                if praritydict['Sets'][psets + ' Prime'][part]['rarity'] == 'Common':
                    commons[psets + ' Prime ' + part] = {
                        'rarity value': praritydict['Sets'][psets + ' Prime'][part]['rarity value'],
                        'uses': int(0),
                        'priority': int(1) if psets in framesets else 0
                    }
                if praritydict['Sets'][psets + ' Prime'][part]['rarity'] == 'Uncommon':
                    uncommons[psets + ' Prime ' + part] = {
                        'rarity value': praritydict['Sets'][psets + ' Prime'][part]['rarity value'],
                        'uses': int(0),
                        'priority': int(1) if psets in framesets else 0
                    }
                if praritydict['Sets'][psets + ' Prime'][part]['rarity'] == 'Rare':
                    rares[psets + ' Prime ' + part] = {
                        'rarity value': praritydict['Sets'][psets + ' Prime'][part]['rarity value'],
                        'uses': int(0),
                        'priority': int(1) if psets in framesets else 0
                    }

    #print(str(len(rares)) + '   ' + str(len(uncommons)) + '   ' + str(len(commons)))

    commons, uncommons, rares = updown(commons, uncommons, rares, dupebool)

    return commons, uncommons, rares

def buildrelics(framesets, stuffsets, dupebool):

    e5 = False
    s10 = False
    beste5 = False
    bests10 = False
    goodrelics = True
    validrelics = False
    invalidcnt = 0
    reliciter = 0
    finalnewrelics = {}

    totalcnt = 0

    commons = None
    uncommons = None
    rares = None

    commons_final = None
    uncommons_final = None
    rares_final = None

    relnum = get_relic_numbers()

    while reliciter < 5:

        commons, uncommons, rares = allocaterarities(framesets, stuffsets, dupebool)
        newrelics = {}
        e5 = False
        s10 = False

        relicnums = copy.deepcopy(relnum)

        rareslist = list(rares)
        uncommonslist = list(uncommons)
        commonslist = list(commons)

        random.shuffle(rareslist)
        random.shuffle(uncommonslist)
        random.shuffle(commonslist)

        #Relic name creation and rare slotting

        # print(f"iteration: {reliciter + 1}")

        for i in range(len(rareslist)):
            #print('relic naming and rare slotting loop')
            era = 'Lith' if i%4==0 else 'Meso' if i%4==1 else 'Neo' if i%4==2 else 'Axi'
            relicname = era + ' ' + rareslist[i][0] + str(relicnums[era][rareslist[i][0]]+1 if rareslist[i][0] in relicnums[era] else 1)

            if rareslist[i][0] in relicnums[era]:
                relicnums[era][rareslist[i][0]] += 1
                # print(f"{f'{era} {rareslist[i][0]}':<10} {relicnums[era][rareslist[i][0]]}")
            else:
                relicnums[era][rareslist[i][0]] = 1
                # print(f"{f'{era} {rareslist[i][0]}':<10} {relicnums[era][rareslist[i][0]]}")

            newrelics[relicname] = {
                'Rare': rareslist[i] if ' 2' not in rareslist[i] else rareslist[i].split(' 2')[0]
                }
            rares[rareslist[i]]['uses'] += 1

        relicslist = list(newrelics)

        #Uncommon slotting

        for i in range(len(relicslist)*2):
            #print('uncommon slotting loop')
            j = int(0)

            uncommonsdone = False
            for k in range(len(uncommonslist)):
                #print('inner uncommon slotting loop')
                for key, value in newrelics[relicslist[i%len(relicslist)]].items():
                    #print('inner uncommon part comparison loop')
                    if uncommonslist[k].split(' Prime')[0] not in value and uncommons[uncommonslist[k]]['uses'] == 0:
                        #print('Slotting part: ' + uncommonslist[k] + ' because set not in relic and ' + str(uncommons[uncommonslist[k]]['uses']) + ' = 0')
                        usepart = True
                    elif uncommonslist[k].split(' Prime')[0] in value or uncommons[uncommonslist[k]]['uses'] > 0:
                        usepart = False
                        break
                if usepart:
                    j = k
                    break
                
            #print('Slotting ' + uncommonslist[j] + ' in relic with:')
            #print(newrelics[relicslist[i%len(relicslist)]])
            
            if usepart:
                if 'Uncommon 1' not in newrelics[relicslist[i%len(relicslist)]]:
                    newrelics[relicslist[i%len(relicslist)]]['Uncommon 1'] = uncommonslist[j].split(' 2')[0] if ' 2' in uncommonslist[j] else uncommonslist[j]
                else:
                    newrelics[relicslist[i%len(relicslist)]]['Uncommon 2'] = uncommonslist[j].split(' 2')[0] if ' 2' in uncommonslist[j] else uncommonslist[j]
                uncommons[uncommonslist[j]]['uses'] += 1
            else:
                if 'Uncommon 1' not in newrelics[relicslist[i%len(relicslist)]]:
                    newrelics[relicslist[i%len(relicslist)]]['Uncommon 1'] = 'Forma Blueprint'
                else:
                    newrelics[relicslist[i%len(relicslist)]]['Uncommon 2'] =  'Forma Blueprint'
            

        z = int(0)

        #Common Slotting OLD
        for i in range(len(relicslist)*3):
            #print('common slotting loop')
            j = int(0)
            
            useforma = False
            usepart = False
            for k in range(len(commonslist)):
                #print('common slotting inner loop')
                for key, value in newrelics[relicslist[len(relicslist)-i%len(relicslist)-1]].items():
                    #print('inner common part comparison loop')
                    if commonslist[k].split('Prime')[0] not in value and commons[commonslist[k]]['uses'] == 0:
                        #print('Slotting part: ' + commonslist[k] + ' because set not in relic and ' + str(commons[commonslist[k]]['uses']) + ' = 0')
                        usepart = True
                    elif commonslist[k].split('Prime')[0] in value or commons[commonslist[k]]['uses'] > 0:
                        usepart = False
                        break
                if usepart:
                    j = k
                    break
            
            #print('Slotting ' + commonslist[j] + ' in relic with:')
            #print(newrelics[relicslist[len(relicslist)-i%len(relicslist)-1]])
            
            if usepart:
                if 'Common 1' not in newrelics[relicslist[len(relicslist)-i%len(relicslist)-1]]:
                    newrelics[relicslist[len(relicslist)-i%len(relicslist)-1]]['Common 1'] = commonslist[j].split(' 2')[0] if ' 2' in commonslist[j] else commonslist[j]
                elif 'Common 2' not in newrelics[relicslist[len(relicslist)-i%len(relicslist)-1]]:
                    newrelics[relicslist[len(relicslist)-i%len(relicslist)-1]]['Common 2'] = commonslist[j].split(' 2')[0] if ' 2' in commonslist[j] else commonslist[j]
                else:
                    newrelics[relicslist[len(relicslist)-i%len(relicslist)-1]]['Common 3'] = commonslist[j].split(' 2')[0] if ' 2' in commonslist[j] else commonslist[j]
                commons[commonslist[j]]['uses'] += 1
            else:
                if 'Uncommon 1' not in newrelics[relicslist[len(relicslist)-i%len(relicslist)-1]]:
                    newrelics[relicslist[len(relicslist)-i%len(relicslist)-1]]['Common 1'] = 'Forma Blueprint'
                elif 'Common 2' not in newrelics[relicslist[len(relicslist)-i%len(relicslist)-1]]:
                    newrelics[relicslist[len(relicslist)-i%len(relicslist)-1]]['Common 2'] = 'Forma Blueprint'
                else:
                    newrelics[relicslist[len(relicslist)-i%len(relicslist)-1]]['Common 3'] = 'Forma Blueprint'

        commonsunused = {}
        for i in range(len(commonslist)):
            #print('common part re-slotting loop')
            commonsunused[commonslist[i]] = commons.copy()[commonslist[i]].copy()
            commonsunused[commonslist[i]]['excluded'] = []
            if commons[commonslist[i]]['uses'] == 0:
                commonsunused[commonslist[i]]['unslotted'] = True
            else:
                commonsunused[commonslist[i]]['unslotted'] = False
            for j in newrelics:
                #print('finding excluded relics loop')
                for k in newrelics[j].values():
                    #print('inner finding excluded relics loop')
                    if commonslist[i].split('Prime')[0] in k:
                        commonsunused[commonslist[i]]['excluded'].append(j)
        
        #print(commonslist)
        #print(commonsunused)
                

        currentrelic = ''
        currentpart = ''
        currentset = ''
        currentexcluded = []
        currentpossible = []
        tempcurrentpart = ''
        tempcurrentpartcnt = 0
        possible = True
        skip = False
        noutofrelic = 0
        validrelics = True
        yesbreak = False



        for i in commonsunused.values():
            #print('find noutofrelic loop')
            if i['unslotted']:
                noutofrelic +=1

        #print(noutofrelic)
        #print(commonsunused)

        def updateexclude(cset, oset, crelic, unuseddict):

            #if len(oset) < 1:
                #print('adding exclude')

            for xk, xv in unuseddict.items():
                #print('updateexclude main loop')
                #print(cset + '   ' + str(xk))
                if cset in xk and crelic not in xv['excluded']:
                    #print(xv['excluded'])
                    #print('adding ' + crelic)
                    xv['excluded'].append(crelic)
                    #print(xv['excluded'])

            if len(oset) > 1:
                #print('removing exclude')
                for xk, xv in unuseddict.items():
                    #print('updateexclude secondary loop')
                    #print(oset + '   ' + str(xk))
                    if oset in xk:
                        #print(xv['excluded'])
                        #print('removing ' + crelic)
                        xv['excluded'].remove(crelic)
                        #print(xv['excluded'])

            return unuseddict


        newrelicsfix = newrelics.copy()

        while noutofrelic > 0:
            #print('Number of items not slotted: ' + str(noutofrelic))
            #print('noutofrelic loop')
            possible = True
            commonforma = False
            commonformaloc = ''
            commonformarelic = ''

            for ck, cv in commonsunused.items():
                #print('counting common excluded parts loop')
                if cv['unslotted']:
                    currentpart = ck
                    currentset = ck.split('Prime')[0]
                    currentexcluded = cv['excluded'].copy()
                    if tempcurrentpart != currentpart:
                        tempcurrentpart = currentpart
                        #tempcurrentpartcnt=0
                    else:
                        tempcurrentpartcnt += 1
                    break

            #print(tempcurrentpartcnt)

            if currentpart == '':
                break

            currentpossible = []
            for x in list(newrelicsfix):
                #print('finding possible relics loop')
                if x not in currentexcluded:
                    currentpossible.append(x)
                    #print(newrelicsfix[x])
            
            random.shuffle(currentpossible)
            #print(currentpart + '   ' + str(currentpossible))
            #print(commonsunused)

            if tempcurrentpartcnt > 15 and tempcurrentpartcnt <= 20:
                currentpossible = []
                for crelic in newrelicsfix:
                    #print('S10 main loop')
                    possiblebool = True
                    for dcheckkk, dcheckvv in newrelicsfix[crelic].items():
                        #print('S10 inner loop')
                        if currentpart.split('Prime')[0] in dcheckvv and ('Common' in dcheckkk or 'Uncommon' in dcheckkk):
                            possiblebool = False
                            break
                    if possiblebool:
                        currentpossible.append(crelic)
                tempexcluded = commonsunused[currentpart]['excluded']
                for x in commonsunused[currentpart]['excluded']:
                    #print('S10 updates excluded list if possible')
                    if x in currentpossible:
                        tempexcluded.remove(x)
                commonsunused[currentpart]['excluded'] = tempexcluded.copy()
                s10 = True

            if tempcurrentpartcnt > 20:
                currentpossible = []
                for crelic in newrelicsfix:
                    #print('E5 main loop')
                    possiblebool = True
                    for dcheckkk, dcheckvv in newrelicsfix[crelic].items():
                        #print('E5 inner loop')
                        if currentpart.split('Prime')[0] in dcheckvv and 'Common' in dcheckkk:
                            possiblebool = False
                            break
                    if possiblebool:
                        currentpossible.append(crelic)
                tempexcluded = commonsunused[currentpart]['excluded']
                for x in commonsunused[currentpart]['excluded']:
                    #print('E5 updates excluded if possible')
                    if x in currentpossible:
                        tempexcluded.remove(x)
                commonsunused[currentpart]['excluded'] = tempexcluded.copy()
                e5 = True

            for crelic in currentpossible:
                #print('finding forma loop')
                for fcheckk, fcheckv in newrelicsfix[crelic].items():
                    #print('finding forma inner loop')
                    if 'Common' in fcheckk and 'Forma Blueprint' in fcheckv:
                        commonforma = True
                        commonformaloc = fcheckk
                        commonformarelic = crelic
                        #print(commonformarelic + '   ' + commonformarelic)
                        break

            if commonforma:
                newrelicsfix[commonformarelic][commonformaloc] = currentpart if '2' not in currentpart else currentpart.split(' 2')[0]
                commonsunused[currentpart]['unslotted'] = False
                commonsunused = updateexclude(currentset, '', commonformarelic, commonsunused)

            else:
                for crelic in currentpossible:
                    #print('finding replacable parts loop')
                    currentrelic = crelic
                    for relick, relicv in newrelicsfix[currentrelic].items():
                        #print(relick)
                        #print(relicv)
                        #print(commonsunused)
                        #print('finding replacable parts inner loop')
                        if 'Common' in relick and len(commonsunused[relicv]['excluded']) < len(newrelicsfix):
                            newrelicsfix[currentrelic][relick] = currentpart if '2' not in currentpart else currentpart.split(' 2')[0]
                            commonsunused = updateexclude(currentset, relicv.split('Prime')[0], currentrelic, commonsunused)
                            commonsunused[currentpart]['unslotted'] = False
                            commonsunused[relicv]['unslotted'] = True
                            break
                    
                    if not commonsunused[currentpart]['unslotted']:
                        break

            noutofrelic = 0
            for i in commonsunused.values():
                #print('noutofrelic loop 2')
                if i['unslotted']:
                    noutofrelic +=1

            if tempcurrentpartcnt > 50:
                validrelics = False
                invalidcnt += 1
                break

            if invalidcnt == 5:
                goodrelics = False
                break

            #print(tempcurrentpartcnt)
        
        unslotted = 0
        unslotteddict = {}
        for com in commons:
            #print('find common unslotted loop')
            if commons[com]['uses'] < 1 and '2' not in com:
                unslotteddict[com] = commons[com].copy()
                unslotted += 1

        for unc in uncommons:
            #print('find uncommon unslotted loop')
            if uncommons[unc]['uses'] < 1 and '2' not in unc:
                unslotteddict[unc] = uncommons[unc].copy()
                unslotted += 1

        #print(commons)
        #print('')
        #print(uncommons)

        for i in newrelics:
            for k, v in newrelics[i].items():
                if 'Forma' not in v:
                    if 'Common' in k:
                        commons[v.split(' 2')[0]]['uses'] = 0
                        #print(f"{v.split(' 2')[0]} :  {commons[v.split(' 2')[0]]['uses']}")
                    if 'Uncommon' in k:
                        uncommons[v.split(' 2')[0]]['uses'] = 0
                        #print(f"{v.split(' 2')[0]} :  {uncommons[v.split(' 2')[0]]['uses']}")
        
        for i in newrelics:
            for k, v in newrelics[i].items():
                if 'Forma' not in v:
                    if 'Common' in k:
                        commons[v.split(' 2')[0]]['uses'] += 1
                        #print(f"{v.split(' 2')[0]} :  {commons[v.split(' 2')[0]]['uses']}")
                    if 'Uncommon' in k:
                        uncommons[v.split(' 2')[0]]['uses'] += 1
                        #print(f"{v.split(' 2')[0]} :  {uncommons[v.split(' 2')[0]]['uses']}")
                
        
        #print('- - - -')
        for i in newrelics:
            #print('replacing dupe parts with forma loop')
            if 'Forma Blueprint' not in list(newrelics[i].values()):
                #print(list(newrelics[i].values()))
                #print(f"Trying to remove dupe from {i}:\n{newrelics[i]}")
                breakloops = False
                for j in newrelics[i]:
                    #print('brute force parts comparison loop')
                    for k in newrelics[i]:
                        #print('brute force parts comparison inner loop')
                        if newrelics[i][j].split(' Prime')[0] in newrelics[i][k].split(' Prime')[0] and newrelics[i][j] != newrelics[i][k]:
                            #print(f"Removed duplicate of {newrelics[i][j]} and {newrelics[i][k]} in:\n{newrelics[i]}")
                            replaced = False
                            #print(f"{j}   {k}")
                            if 'Common' in j and not replaced:
                                #print(f"Common j\n{newrelics[i][j]} :  {commons[newrelics[i][j]]['uses']}")
                                if commons[newrelics[i][j]]['uses'] > 1:
                                    #print('Common Replaced')
                                    commons[newrelics[i][j]]['uses'] -= 1
                                    newrelics[i][j] = 'Forma Blueprint'
                                    replaced = True
                            if 'Common' in k and not replaced:
                                #print(f"Common k\n{newrelics[i][k]} :  {commons[newrelics[i][k]]['uses']}")
                                if commons[newrelics[i][k]]['uses'] > 1:
                                    #print('Common Replaced 2')
                                    commons[newrelics[i][k]]['uses'] -= 1
                                    newrelics[i][k] = 'Forma Blueprint'
                                    replaced = True
                            if 'Uncommon' in j and not replaced:
                                #print(f"Uncommon j\n{newrelics[i][j]} :  {uncommons[newrelics[i][j]]['uses']}")
                                if uncommons[newrelics[i][j]]['uses'] > 1:
                                    #print('Uncommon Replaced')
                                    uncommons[newrelics[i][j]]['uses'] -= 1
                                    newrelics[i][j] = 'Forma Blueprint'
                                    replaced = True
                            if 'Uncommon' in k and not replaced:
                                #print(f"Uncommon k\n{newrelics[i][k]} :  {uncommons[newrelics[i][k]]['uses']}")
                                if uncommons[newrelics[i][k]]['uses'] > 1:
                                    #print('Uncommon Replaced 2')
                                    uncommons[newrelics[i][k]]['uses'] -= 1
                                    newrelics[i][k] = 'Forma Blueprint'
                                    replaced = True
                            
                            breakloops = True
                            break
                    if breakloops:
                        break
        #print('- - - -')

        #print(newrelics)
        

        if goodrelics:
            if reliciter == 0:
                finalnewrelics = newrelics.copy()
                beste5 = e5
                bests10 = s10
            if not s10 and not e5 and unslotted == 0:
                finalnewrelics = newrelics.copy()
                beste5 = e5
                bests10 = s10
                reliciter += 100
            elif not s10 and not e5:
                finalnewrelics = newrelics.copy()
                beste5 = e5
                bests10 = s10
                reliciter += 100
            elif s10 and not e5 and not bests10:
                finalnewrelics = newrelics.copy()
                beste5 = e5
                bests10 = s10
            elif e5 and not s10 and not (beste5 or bests10):
                finalnewrelics = newrelics.copy()
                beste5 = e5
                bests10 = s10

            if finalnewrelics == newrelics:
                commons_final = commons
                uncommons_final = uncommons
                rares_final = rares

            reliciter+=1
        
        totalcnt += 1

    gen_relics_data = {}
    for part in rares_final:
        gen_relics_data[part] = rares_final[part]
    for part in uncommons_final:
        gen_relics_data[part] = uncommons_final[part]
    for part in commons_final:
        gen_relics_data[part] = commons_final[part]

    new_gen_relics_data(gen_relics_data)
    new_gen_relics(finalnewrelics)

    return goodrelics

def takeinput(framelist, dupebool):
    framesets = []
    stuffsets = []

    for frame in framelist:
        if frame in prime_access:
            framesets.append(frame)
            for val in prime_access[frame]:
                stuffsets.append(val)


    return buildrelics(framesets, stuffsets, dupebool)
