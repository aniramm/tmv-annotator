# /usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import absolute_import
import sys, re, codecs

# author: Anita Ramm

parsed_file_name = sys.argv[1]
parsed = codecs.open(parsed_file_name, "r", encoding='utf8')
out_file = codecs.open("./output/" + sys.argv[2] + ".verbs", "w", encoding='utf8')


def extractVerbalDepDictFR(fin_pos, dep_dict, pos_dict):
    verbal_tags = ["VINF", "VPP", "VPR", "ADV"]
    verbal_rels = []

    def checkInf(inf_deps, dep_dict, pos_dict):

        res = False

        for ch in inf_deps:
            if pos_dict[ch].split("\t")[5] == "VINF":
                res = True
                exit

        # print "checkInf", res
        return res

    def checkGer(ger_deps, dep_dict, pos_dict):

        res = False

        for ch in ger_deps:
            if pos_dict[ch].split("\t")[5] == "VPR":
                res = True
                exit

        # print "checkGer", res
        return res

    def checkPasseRec(fp, last_fin_pos, pos_dict):

        res = False

        if pos_dict[last_fin_pos].split("\t")[3].lower() in ["venir"]:
            res = True

        # print "checkPasseRec", res
        return res

    def checkFurProc(fp, last_fin_pos, pos_dict):

        print
        "checkFurProc"

        res = False

        if pos_dict[last_fin_pos].split("\t")[3].lower() in ["aller"]:
            res = True

        return res

    def checkCoord(cc_deps, dep_dict, pos_dict):

        res = False

        for ch in cc_deps:
            if pos_dict[ch].split("\t")[5].startswith("V"):
                res = True
                exit

        return res

    def governedInf(inf_id, last_fin_pos, pos_dict):

        res = False

        # Passive auxiliary
        if pos_dict[inf_id].split("\t")[11] == "aux.pass":
            res = True
        # Governed by P
        elif pos_dict[last_fin_pos].split("\t")[5] in ["P"]:
            res = True
        # Governed by finite 'aller' (futur proche) or finite modal verbs
        elif pos_dict[last_fin_pos].split("\t")[3].lower() in ["aller", "vouloir", "pouvoir", "devoir"]:
            res = True
            # Governed by a non-finite  modal verb
        elif pos_dict[last_fin_pos].split("\t")[5] in ["VPP"]:
            if pos_dict[last_fin_pos].split("\t")[3].lower() in ["vouloir", "pouvoir", "devoir"]:
                res = True

        # print "Governed infinitive?", inf_id, last_fin_pos, res
        return res

    def createDepDict(dep_pos, fin_pos, last_fin_pos, inf_vcs, coord, dep_dict):

        if dep_pos not in dep_dict:
            return {}
        else:
            temp_res = {}
            for i in dep_dict[dep_pos]:
                # print i, "in", dep_dict[dep_pos]
                curr_id = int(pos_dict[i].split("\t")[0])
                curr_rel = pos_dict[i].split("\t")[11]
                curr_pos = pos_dict[i].split("\t")[5]
                curr_morph = pos_dict[i].split("\t")[7]
                curr_token = pos_dict[i].split("\t")[1].lower()
                curr_lemma = pos_dict[i].split("\t")[3].lower()
                if (curr_pos in verbal_tags):

                    if i not in fin_pos:

                        # If adverbial, add only negation
                        if curr_pos == "ADV" and curr_token in ["ne", "n'", "pas", "non"]:
                            # print "Negation found!", temp_res
                            temp_res[str(
                                i) + "#" + curr_pos + "#" + curr_rel + "#" + curr_morph + "#" + curr_token + "#" + curr_lemma + "#" + str(
                                last_fin_pos)] = createDepDict(i, fin_pos, last_fin_pos, inf_vcs, coord, dep_dict)

                        # Infinitival preposition
                        elif curr_pos == "P" and curr_lemma in ["de", u"à", "par", "en", "pour"]:
                            # print "Infinitival preposition!", temp_res
                            temp_res[str(
                                i) + "#" + curr_pos + "#" + curr_rel + "#" + curr_morph + "#" + curr_token + "#" + curr_lemma + "#" + str(
                                last_fin_pos)] = createDepDict(i, fin_pos, last_fin_pos, inf_vcs, coord, dep_dict)

                        # Infinitives are attached to the current dep chain if part of future compose
                        # or of an infinitive VC.
                        # Otherwise, they build their own VCs
                        elif curr_pos == "VINF":
                            if governedInf(curr_id, last_fin_pos, pos_dict):
                                temp_res[str(
                                    i) + "#" + curr_pos + "#" + curr_rel + "#" + curr_morph + "#" + curr_token + "#" + curr_lemma + "#" + str(
                                    last_fin_pos)] = createDepDict(i, fin_pos, last_fin_pos, inf_vcs, coord, dep_dict)
                            else:
                                if curr_id not in fin_pos:
                                    fin_pos.append(curr_id)
                                    inf_vcs.append((curr_id, last_fin_pos))

                        # Attach participles to the current dep chain
                        elif curr_pos in ["VPP"]:
                            # print "VC compl found", curr_id
                            if curr_rel == "dep.coord":
                                # print "Coordinated VC!", "last_fin_pos", last_fin_pos
                                coord.append(last_fin_pos)

                            last_fin_pos = curr_id
                            temp_res[str(
                                i) + "#" + curr_pos + "#" + curr_rel + "#" + curr_morph + "#" + curr_token + "#" + curr_lemma + "#" + str(
                                last_fin_pos)] = createDepDict(i, fin_pos, last_fin_pos, inf_vcs, coord, dep_dict)


                        # Gerund: attach to the current chain if governed by P
                        # Otherwise make new dep chain
                        elif curr_pos in ["VPR"]:
                            if curr_rel in ["obj.p"]:  # Gerund governed by P
                                temp_res[str(
                                    i) + "#" + curr_pos + "#" + curr_rel + "#" + curr_morph + "#" + curr_token + "#" + curr_lemma + "#" + str(
                                    last_fin_pos)] = createDepDict(i, fin_pos, last_fin_pos, inf_vcs, coord, dep_dict)
                                fin_pos.remove(curr_id)

                            if curr_rel == "dep.coord":
                                # print "Coordinated VC!", "last_fin_pos", last_fin_pos
                                coord.append(last_fin_pos)

                    else:
                        # Gerund: attach to the current chain if governed by P
                        # Otherwise make new dep chain
                        if curr_pos in ["VPR"]:
                            # print "Gerund", curr_rel
                            if curr_rel in ["obj.p"]:  # Gerund governed by P
                                temp_res[str(
                                    i) + "#" + curr_pos + "#" + curr_rel + "#" + curr_morph + "#" + curr_token + "#" + curr_lemma + "#" + str(
                                    last_fin_pos)] = createDepDict(i, fin_pos, last_fin_pos, inf_vcs, coord, dep_dict)
                                fin_pos.remove(curr_id)

                else:

                    # Attach to-Infs to the current dep chain if part of passe recent
                    if curr_pos == "P":
                        if curr_lemma in ["de", u"à", "par", "en", "pour"]:
                            if checkPasseRec(fp, last_fin_pos, pos_dict):
                                res[str(
                                    fp) + "#" + curr_pos + "#" + curr_rel + "#" + curr_morph + "#" + curr_token + "#" + curr_lemma + "#" + str(
                                    last_fin_pos)] = createDepDict(fp, fin_pos, fp, inf_vcs, coord, dep_dict)

                    # Attach coordination if part of the verb chain
                    elif curr_pos in ["CC"]:
                        if checkCoord(dep_dict[i], dep_dict, pos_dict):
                            # print "VC coordination found", curr_pos, temp_res

                            temp_res[str(
                                i) + "#" + curr_pos + "#" + curr_rel + "#" + curr_morph + "#" + curr_token + "#" + curr_lemma + "#" + str(
                                last_fin_pos)] = createDepDict(i, fin_pos, last_fin_pos, inf_vcs, coord, dep_dict)

                    elif curr_rel in ["coord", "dep.coord"]:
                        # print "Not CC coordination of the verbs!"
                        if checkCoord(dep_dict[i], dep_dict, pos_dict):
                            # print "VC coordination found", curr_pos, temp_res
                            createDepDict(i, fin_pos, last_fin_pos, inf_vcs, coord, dep_dict)

                verbal_rels.append(curr_rel)

            return temp_res

    res = {}
    inf_vcs = []
    coord = []
    last_fin_pos = 0
    for fp in fin_pos:
        curr_rel = pos_dict[fp].split("\t")[11]
        curr_pos = pos_dict[fp].split("\t")[5]
        curr_morph = pos_dict[fp].split("\t")[7]
        curr_token = pos_dict[fp].split("\t")[1].lower()
        curr_lemma = pos_dict[fp].split("\t")[3].lower()
        # print "fp+token", fp, curr_token, curr_pos

        if curr_pos == "P":
            if curr_lemma in ["de", u"à", "par", "en", "pour"]:
                # Add to-Infs as separate dictionary entries if not part of passe recent
                if (checkInf(dep_dict[fp], dep_dict, pos_dict) or checkGer(dep_dict[fp], dep_dict,
                                                                           pos_dict)) and not checkPasseRec(fp,
                                                                                                            last_fin_pos,
                                                                                                            pos_dict):
                    res[str(
                        fp) + "#" + curr_pos + "#" + curr_rel + "#" + curr_morph + "#" + curr_token + "#" + curr_lemma + "#" + str(
                        last_fin_pos)] = createDepDict(fp, fin_pos, fp, inf_vcs, coord, dep_dict)
                    inf_vcs.append((fp, last_fin_pos))

        elif curr_pos == "VPR":
            if curr_rel == "mod":
                res[str(
                    fp) + "#" + curr_pos + "#" + curr_rel + "#" + curr_morph + "#" + curr_token + "#" + curr_lemma + "#" + str(
                    last_fin_pos)] = createDepDict(fp, fin_pos, fp, inf_vcs, coord, dep_dict)
                inf_vcs.append((fp, last_fin_pos))

        else:
            last_fin_pos = fp
            res[str(
                fp) + "#" + curr_pos + "#" + curr_rel + "#" + curr_morph + "#" + curr_token + "#" + curr_lemma + "#" + str(
                last_fin_pos)] = createDepDict(fp, fin_pos, last_fin_pos, inf_vcs, coord, dep_dict)

    return (res, list(set(verbal_rels)), inf_vcs, coord)


def getVerbSequences(verb_dep_dict):
    res = []
    res_id = []

    def getVerbSeq(fin, temp_dict, temp_res1, temp_res2):
        if temp_dict == {}:
            return ""
        else:
            curr_id = int(fin.split("#")[0])
            curr_token = fin.split("#")[4]
            curr_pos = fin.split("#")[1]
            if curr_pos not in ["CC", "P"]:  # Exclude coordination/preposition
                temp_res1.append(curr_token)
                temp_res2.append((curr_id, curr_token))
            for dep_verb in temp_dict[fin]:
                getVerbSeq(dep_verb, temp_dict[fin], temp_res1, temp_res2)

            return sorted(temp_res2)

    for fin in verb_dep_dict:
        temp_res1 = []
        temp_res2 = []
        ret_val = getVerbSeq(fin, verb_dep_dict, temp_res1, temp_res2)
        res.append(ret_val)
        res_id.append(temp_res2)

    final_res = []
    final_res_id = []
    for v_seq in res:
        curr_seq = []
        curr_id = []
        for pair in v_seq:
            curr_seq.append(pair[1])
            curr_id.append(str(pair[0]))
        final_res.append(curr_seq)
        final_res_id.append(curr_id)

    return (final_res, final_res_id)


def mergeVerbsTensesFR(verb_seq, verb_ids, tense_seq, inf_vcs, coord):
    res = []

    for i in range(len(verb_seq)):
        verbs = ""
        ids = ""
        coord_vc = "no"
        for v in verb_seq[i]:
            verbs += v + " "
        for j in verb_ids[i]:
            ids += j + ","
            if int(j) in coord:
                coord_vc = "yes"
        res.append((ids.strip()[:-1] + "\t" + verbs.strip(), tense_seq[i] + "\t" + coord_vc))

    return res


def outputVerbTensePairsFull(sent_nr, verb_tenses, pos_dict, out_file):
    # print "outputVerbTensePairs", sent_nr, verb_tenses, pos_dict,
    if verb_tenses != []:
        for pair in verb_tenses:
            # No clause identification for EN!
            # curr_clause = getCurrClause(pair[0].split("\t")[0].split(","), "-", pos_dict)
            # print "curr_clause", curr_clause
            out_file.write(str(sent_nr) + "\t" + pair[0] + "\t" + pair[1] + "\t" + "-" + "\n")


def getTenseFR(chain_dict):
    res = []

    def getCleanPosSeq(fin, temp_dict, temp_res):

        if temp_dict == {}:
            return ""
        else:
            curr_pos = fin.split("#")[1]
            curr_rel = fin.split("#")[2]
            if "CC" in curr_pos:  # Don't go over coordination
                # if temp_dict[fin] == {}:
                #   print "Koord without conjunct!"
                return ""
            else:
                temp_res.append(curr_pos)
                for dep_verb in temp_dict[fin]:
                    getCleanPosSeq(dep_verb, temp_dict[fin], temp_res)

            return temp_res

    def deriveTMFR(pos_seq, fin, chain_dict):

        def getVPtag(fin, chain_dict):  # Morph feat to string (Sharid)

            morph_list = []
            lemma_list = []
            finV = fin.split("#")[4]

            def getVmorph(v):

                res = {}
                curr_morph = v.split("#")[3].split("|")
                for m in curr_morph:
                    res[m.split("=")[0]] = m.split("=")[1]

                return res

            def getVPinfo(v, chain_dict):

                curr_pos = v.split("#")[1]
                if curr_pos.startswith("V"):
                    curr_morph = getVmorph(v)
                    curr_lemma = v.split("#")[5]
                    lemma_list.append(curr_lemma)
                    curr_morph_val = "V-"
                    if 'm' in curr_morph:
                        curr_morph_val += curr_morph['m']
                    if 't' in curr_morph:
                        curr_morph_val += curr_morph['t']
                    morph_list.append(curr_morph_val)

                for ch in chain_dict:
                    getVPinfo(ch, chain_dict[ch])

            getVPinfo(fin, chain_dict)

            return (' '.join(morph_list), finV, lemma_list)

        def getTenseFromVPtag(pos_seq, fr, simple_tag, LemmaList):

            finite = "yes"
            tense = "err"
            mood = "indicative"
            voice = "err"
            negation = "no"

            # Negation
            if "ADV" in pos_seq:
                negation = "yes"

            semiAuxFut = ["vais", "vas", "va", "allons", "allez", "vont"]
            semiAuxPast = ["viens", "vient", "venons", "venez", "viennent"]

            intransSharid = [u"aller", u"arriver", u"décéder", u"devenir", u"échoir", u"entrer", u"mourir", u"naître",
                             u"partir", u"rester", u"retourner", u"sortir", u"tomber", u"venir"]

            intrans = ["aller", "arriver", u"décéder", "descendre", "demeurer", "devenir", u"être", u"échoir", "entrer",
                       "monter", "mourir", u"naître", "partir", "passer", "quitter", "rencontrer", "rester", "retourner",
                       "sortir", "tomber", "venir"]

            pres = "V-indpst"
            passe_comp = "V-indpst V-partpast"  # la maison est construite (passive) vs jean est parti (passé composé)
            imparfait = "V-indimpft"
            plus_que_parf = "V-indimpft V-partpast"
            passe_sim = "V-indpast"
            passe_ant = "V-indpast V-partpast"
            passe_rec = "V-indpst V-inf"
            futur = "V-indfut"
            futur_ant = "V-indfut V-partpast"
            futur_proche = "V-indpst V-inf"
            imperatif = "V-imppst"
            subjonctif1 = "V-subjpst"
            subjonctif2 = "V-subjimpft V-participepasse"
            conditionnel1 = "V-indcond"
            conditionnel2 = "V-indcond V-partpast"
            infinitive1 = "V-inf"
            infinitive2 = "V-inf V-inf"  # de voir épouser
            gerund1 = "V-partpst"
            gerund2 = "V-partpst V-inf"
            gerund3 = "V-partpst V-partpast V-inf"  # pouvant être utilisées

            PApres = passe_comp  #### regarder lemma
            PApasse_comp = "V-indpst V-partpast V-partpast"
            PAimparfait = plus_que_parf  ###regarder lemma
            PAplus_que_parf = "V-indimpft V-partpast V-partpast"
            PApasse_sim = passe_ant
            PApasse_ant = "V-indpast V-partpast V-partpast"
            PAfutur = futur_ant
            PAfutur_ant = "V-indfut V-partpast V-partpast"
            PAfutur_proche = "V-indpst V-inf V-partpast"
            PAsubjonctif = "V-subjpst V-partpast"
            PAsubjontif2 = "V-subjimpft V-partpast"
            PAconditionnel = "V-indcond V-partpast"
            PAinfinitive = "V-inf V-partpast"

            if PApasse_comp in simple_tag:
                tense = "perfect"
                voice = "passive"

            elif PAplus_que_parf in simple_tag:
                tense = "pluperfect"
                voice = "passive"

            elif (plus_que_parf in simple_tag) and (u"être" in LemmaList):  # il était parti
                for x in LemmaList:
                    if x in intrans:
                        tense = "pluperfect"
                        voice = "active"
                        break
                    else:
                        tense = "imperfect"  # la lettre était finie
                        voice = "passive"

            elif plus_que_parf in simple_tag:
                tense = "pluperfect"
                voice = "active"

            elif imparfait in simple_tag:
                tense = "imperfect"
                voice = "active"

            elif PApasse_ant in simple_tag:
                tense = "pastPerf"
                voice = "passive"

            elif (passe_ant in simple_tag) and (u"être" in LemmaList):
                tense = "pastSimp"
                voice = "passive"

            elif passe_ant in simple_tag:
                tense = "pastPerf"
                voice = "active"

            elif (passe_rec in simple_tag) and (fr in semiAuxPast):
                tense = "presPerf"
                voice = "active"

            elif passe_sim in simple_tag:
                tense = "pastSimp"
                voice = "active"

            elif PAfutur_ant in simple_tag:
                tense = "futureII"
                voice = "passive"

            elif (PAfutur_proche in simple_tag) and (fr in semiAuxFut):
                tense = "futureProc"
                voice = "passive"

            elif (futur_proche in simple_tag) and (fr in semiAuxFut):
                tense = "futureProc"
                voice = "active"

            elif (futur_ant in simple_tag) and (u"être" in LemmaList):  # il sera parti
                for x in LemmaList:
                    if x in intrans:
                        tense = "futureII"
                        voice = "active"
                        break
                    else:
                        tense = "futureI"  # la lettre sera finie
                        voice = "passive"

            elif futur_ant in simple_tag:
                tense = "futureII"
                voice = "active"

            elif futur in simple_tag:
                tense = "futureI"
                voice = "active"

            elif imperatif in simple_tag:
                tense = "pres"
                mood = "imperative"
                voice = "active"

            elif (PAsubjonctif in simple_tag) or (PAsubjontif2 in simple_tag):
                if PAsubjonctif in simple_tag:
                    tense = "pres"
                    voice = "passive"
                    mood = "subjunctive"
                else:
                    tense = "imperfect"
                    voice = "passive"
                    mood = "subjunctive"

            elif subjonctif2 in simple_tag:
                tense = "past"
                voice = "active"
                mood = "subjunctive"

            elif subjonctif1 in simple_tag:
                tense = "pres"
                voice = "active"
                mood = "subjunctive"

            elif PAconditionnel in simple_tag:
                tense = "condII"
                voice = "passive"

            elif conditionnel2 in simple_tag:
                tense = "condII"
                voice = "active"

            elif conditionnel1 in simple_tag:
                tense = "condI"
                voice = "active"

            elif PAinfinitive == simple_tag:
                finite = "no"
                tense = "-"
                mood = "-"
                voice = "passive"

            elif infinitive1 == simple_tag or infinitive2 == simple_tag:
                finite = "no"
                tense = "-"
                mood = "-"
                voice = "active"

            elif gerund1 == simple_tag or gerund2 == simple_tag or gerund3 == simple_tag:
                finite = "no"
                tense = "-"
                mood = "-"
                voice = "active"

            elif (passe_comp in simple_tag) and (u"être" in LemmaList):  # il est passé
                for x in LemmaList:
                    if x in intrans:
                        tense = "perfect"
                        voice = "active"
                        break
                    else:
                        tense = "pres"  # la lettre est envoyé
                        voice = "passive"

            elif passe_comp in simple_tag:
                tense = "perfect"
                voice = "active"

            elif pres in simple_tag:
                tense = "pres"
                voice = "active"

            # Correcting voice if tense and voice are empty
            if tense == "err" or voice == "err":
                tense = "err"
                mood = "err"
                voice = "err"
                progressive = "err"

            return (finite, tense, mood, voice, negation)

        #### MAIN of deriveFRTM ####
        (vp_morph, finV, lemmas) = getVPtag(fin, chain_dict)
        # print "vp_morph", vp_morph, "finV", finV, vp_morph, "lemmas", lemmas
        finite, tense, mood, voice, negation = getTenseFromVPtag(pos_seq, finV, vp_morph, lemmas)
        return (finite, tense, mood, voice, negation)
        #####################

    def getMainVerbFR(dep_dict):

        res = []
        res_string = ""

        def verbSubCat(dep_dict):

            res = False

            for v in dep_dict:
                curr_pos = v.split("#")[1]
                curr_lemma = v.split("#")[5]
                if curr_pos.startswith("V"):
                    res = True
                else:
                    verbSubCat(dep_dict[v])

            return res

        def searchVV(dep_dict):

            for v in dep_dict:
                curr_pos = v.split("#")[1]
                curr_verb = v.split("#")[4]
                curr_rel = v.split("#")[2]
                if dep_dict[v] != {}:
                    v_child = dep_dict[v].keys()[0]
                    v_child_pos = v_child.split("#")[1]
                    v_child_token = v_child.split("#")[4]
                    v_child_rel = v_child.split("#")[2]
                    # print curr_pos, curr_verb, v_child_pos, v_child_token, v_child_rel
                    if curr_pos != "ADV":
                        if v_child_pos == "ADV":  # Negation
                            if not verbSubCat(dep_dict[v]):  # Append as mainV if no further main verbs
                                res.append(curr_verb)
                        elif v_child_pos in ["CC"]:  # Coordination
                            res.append(curr_verb)
                        elif v_child_pos.startswith("V"):
                            if v_child_token in [u"être"] and v_child_rel == "aux.pass":
                                res.append(curr_verb)
                else:
                    if curr_pos not in ["CC", "ADV"]:
                        if curr_rel != "aux.pass":
                            res.append(curr_verb)

                searchVV(dep_dict[v])

        searchVV(dep_dict)

        for v in res:
            if res_string == "":
                res_string += v
            else:
                res_string += "," + v

        return res_string

    for fin in chain_dict:
        temp_res = []
        tense = ""
        mood = ""
        pos_seq = getCleanPosSeq(fin, chain_dict, temp_res)
        # print "derive tense", pos_seq, fin, chain_dict[fin]
        (finite, tense, mood, voice, negation) = deriveTMFR(pos_seq, fin, chain_dict[fin])
        mainV = getMainVerbFR({fin: chain_dict[fin]})
        # print "RESULT:", finite, tense, mood, voice, negation, mainV
        temp_res = finite + "\t" + str(mainV) + "\t" + tense + "\t" + mood + "\t" + voice + "\t" + negation
        res.append(temp_res)

    return res


def getDepsForFins(fin_pos, dep_dict, dep_dict_rev):
    res = dep_dict

    # Add reversed dependecy for the finite verb
    for fp in fin_pos:
        if fp not in dep_dict:
            if fp in dep_dict_rev:
                res[fp] = dep_dict_rev[fp]
                # Remove dependencies to the finite verb from the dictionary
                for k in res:
                    if fp in res[k]:
                        res[k].remove(fp)

    return res


def checkCoordVCs(verb_seqs):
    res = False

    for i in verb_seqs:
        for j in verb_seqs:
            if i != j:
                for k in i:
                    if k in j:
                        res = True
                        # print k, res
    return res


def extractVerbDeps(parsed_file):
    sent_nr = 1
    parsed_line = parsed_file.readline()
    verbal_rels = []
    verbal_pos_seqs = []

    while parsed_line:

        print
        "Derving TMV for French ...", sent_nr, "\r",

        pos_dict = {}  # Dict: {sent_position1: line, sent_position2:line, ...}
        dep_dict = {}  # Dict: {dependency_position1: [sent_position1, sent_position2, ...], ...}
        dep_dict_rev = {}  # Reversed dep_dict
        dep_rel = {}  # Dict: {sent_position1: dependency_relation, sent_position2: dependency_relation, ...}
        fin_pos = []
        verb_dep_dict = {}  # Dict: {root_position: {...}, ...}
        sent_lines = []

        while parsed_line != "\n":

            sent_lines.append(parsed_line.strip())
            line_split = parsed_line.strip().split("\t")

            try:
                pos_dict[int(line_split[0])] = parsed_line.strip()
                dep_rel[int(line_split[0])] = line_split[11]

                # collect root dependencies and all non-finite verbs
                # Note: in FR, non-finite verbs govern finite verbs!
                if line_split[5] in ["V", "VS", "VPR", "P"]:
                    fin_pos.append(int(line_split[0]))

                if int(line_split[9]) in dep_dict:
                    dep_dict[int(line_split[9])].append(int(line_split[0]))
                else:
                    if int(line_split[9]) != 0:
                        dep_dict[int(line_split[9])] = [int(line_split[0])]

                if int(line_split[0]) in dep_dict_rev:
                    if int(line_split[9]) != 0:
                        dep_dict_rev[int(line_split[0])].append(int(line_split[9]))
                else:
                    if int(line_split[9]) != 0:
                        dep_dict_rev[int(line_split[0])] = [int(line_split[9])]


            except Exception as inst:
                print
                "Error ", inst

            parsed_line = parsed_file.readline()

        try:

            # Sentence collected; now get the chain verbal dependencies of the root
            corrected_fin_deps = getDepsForFins(fin_pos, dep_dict, dep_dict_rev)

            (chain_deps, verb_rels, inf_vcs, coord) = extractVerbalDepDictFR(fin_pos, corrected_fin_deps, pos_dict)

            (verb_seqs, verb_ids) = getVerbSequences(chain_deps)

            tenses = getTenseFR(chain_deps)

            verb_tenses = mergeVerbsTensesFR(verb_seqs, verb_ids, tenses, inf_vcs, coord)
            # print "verb_tenses", verb_tenses

            outputVerbTensePairsFull(sent_nr, verb_tenses, pos_dict, out_file)

        except:
            continue

        sent_nr += 1
        parsed_line = parsed_file.readline()


############# MAIN ###############

verb_dep_dict = extractVerbDeps(parsed)

parsed.close()
out_file.close()
