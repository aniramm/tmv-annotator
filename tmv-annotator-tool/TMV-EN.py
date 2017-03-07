# /usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import absolute_import
import sys, re, codecs

# author: Anita Ramm

parsed_file_name = sys.argv[1]
parsed = codecs.open(parsed_file_name, "r", encoding='utf8')
out_file = codecs.open("./output/" + sys.argv[2] + ".verbs", "w", encoding='utf8')


def extractVerbalDepDictEN(fin_pos, dep_dict, pos_dict):
    # print "extractVerbalDepDict", fin_pos, dep_dict#, pos_dict

    verbal_tags = ["VBD", "VBP", "VBZ", "MD", "VB", "VBG", "VBN", "TO", "RB", "RP", "CC"]
    verbal_rels = []

    def checkInf(inf_deps, dep_dict, pos_dict):

        # print "Checking inf", inf_deps

        res = False

        for ch in inf_deps:
            # print pos_dict[ch]
            if pos_dict[ch].split("\t")[5] == "VB":
                res = True
                exit
        # print "Inf", res
        return res

    def createDepDict(dep_pos, fin_pos, last_fin_pos, inf_vcs, coord):

        # print "createDepDict", dep_pos, fin_pos, last_fin_pos, inf_vcs

        if dep_pos not in dep_dict:  # or dep_pos in fin_pos:
            return {}
        else:
            temp_res = {}
            for i in dep_dict[dep_pos]:
                # print dep_dict, dep_dict[dep_pos], i
                curr_id = int(pos_dict[i].split("\t")[0])
                curr_rel = pos_dict[i].split("\t")[11]
                curr_pos = pos_dict[i].split("\t")[5]
                curr_morph = pos_dict[i].split("\t")[7]
                curr_token = pos_dict[i].split("\t")[1].lower()
                curr_lemma = pos_dict[i].split("\t")[3].lower()
                if (curr_pos in verbal_tags):

                    if i not in fin_pos:

                        # If adverbial, add only negation
                        if curr_pos == "RB" and curr_token in ["not", "'t", "n't"]:
                            temp_res[str(
                                i) + "#" + curr_pos + "#" + curr_rel + "#" + curr_morph + "#" + curr_token + "#" + curr_lemma + "#" + str(
                                last_fin_pos)] = createDepDict(i, fin_pos, last_fin_pos, inf_vcs, coord)

                        # Attach infinitives/participles/particles to the current dep chain
                        # Permitted relations:
                        # 1. VC: verb complex
                        # 2. IM: infinitive in to-infinitive clauses
                        # 3. CONJ: conjunct (coordinated verbs)
                        # 4. PRD: predicative argument
                        elif curr_pos in ["RP", "CC"] or (
                                curr_pos in ["VBN", "VB"] and curr_rel in ["VC", "IM", "CONJ", "PRD"]):
                            if curr_rel == "PRD":
                                print
                                "Predicative copula construction!"
                            # if curr_id not in fin_pos:
                            #   fin_pos.append(curr_id)
                            #   inf_vcs.append((curr_id, last_fin_pos))

                            if curr_rel == "CONJ":
                                # print "Coordinated VC!", "last_fin_pos", last_fin_pos
                                coord.append(last_fin_pos)

                            temp_res[str(
                                i) + "#" + curr_pos + "#" + curr_rel + "#" + curr_morph + "#" + curr_token + "#" + curr_lemma + "#" + str(
                                last_fin_pos)] = createDepDict(i, fin_pos, last_fin_pos, inf_vcs, coord)

                        elif curr_pos == "VBG":  # Gerundive VCs
                            if curr_rel in ["VC", "OPRD"]:  # Gerund within a VC
                                temp_res[str(
                                    i) + "#" + curr_pos + "#" + curr_rel + "#" + curr_morph + "#" + curr_token + "#" + curr_lemma + "#" + str(
                                    last_fin_pos)] = createDepDict(i, fin_pos, last_fin_pos, inf_vcs, coord)
                            # Gerund as a stand-alone verb within an infinitive clause
                            elif "MOD" in curr_rel:
                                if curr_id not in fin_pos:
                                    fin_pos.append(curr_id)
                                    inf_vcs.append((curr_id, last_fin_pos))

                            if curr_rel == "CONJ":
                                # print "Coordinated VC!", "last_fin_pos", last_fin_pos
                                coord.append(last_fin_pos)

                    else:
                        if curr_pos == "TO":
                            # Add to-Infs as separate dictionary entries
                            if checkInf(dep_dict[i], dep_dict, pos_dict):
                                if curr_id not in fin_pos:
                                    fin_pos.append(curr_id)
                                    inf_vcs.append((curr_id, last_fin_pos))
                        else:
                            last_fin_pos = dep_pos

                verbal_rels.append(curr_rel)
            return temp_res

    res = {}
    inf_vcs = []
    coord = []
    last_fin_pos = 0
    for fp in fin_pos:
        # print "fp", fp
        curr_rel = pos_dict[fp].split("\t")[11]
        curr_pos = pos_dict[fp].split("\t")[5]
        curr_morph = pos_dict[fp].split("\t")[7]
        curr_token = pos_dict[fp].split("\t")[1].lower()
        curr_lemma = pos_dict[fp].split("\t")[3].lower()
        # print str(fp)+"#"+curr_pos+"#"+curr_rel+"#"+curr_morph+"#"+curr_token+"#"+str(fp)
        if curr_pos == "TO":
            # Add to-Infs as separate dictionary entries
            if checkInf(dep_dict[fp], dep_dict, pos_dict):
                res[str(
                    fp) + "#" + curr_pos + "#" + curr_rel + "#" + curr_morph + "#" + curr_token + "#" + curr_lemma + "#"] = createDepDict(
                    fp, fin_pos, last_fin_pos, inf_vcs, coord)
        else:
            last_fin_pos = fp
            res[str(
                fp) + "#" + curr_pos + "#" + curr_rel + "#" + curr_morph + "#" + curr_token + "#" + curr_lemma + "#"] = createDepDict(
                fp, fin_pos, last_fin_pos, inf_vcs, coord)

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
            if curr_pos != "CC":  # Exclude coordination
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


def mergeVerbsTensesEN(verb_seq, verb_ids, tense_seq, inf_vcs, coord):
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


def outputVerbTensePairsFullEN(sent_nr, verb_tenses, pos_dict, out_file):
    if verb_tenses != []:
        for pair in verb_tenses:
            out_file.write(str(sent_nr) + "\t" + pair[0] + "\t" + pair[1] + "\t" + "-" + "\n")


def getTenseEN(chain_dict):
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

    def deriveTMEN(pos_seq, fin, chain_dict):

        mod = False
        fut_mod = False
        subj_mod = False
        finV = 0
        aux_pres = False
        aux_past = False  # auxiliary have
        aux_part = False
        aux_ger = False
        aux_be_ger = False
        aux_inf = False
        part = False
        inf = False
        ger = False
        aux_do_pres = False
        aux_do_past = False
        aux_be_pres = False
        aux_be_past = False
        aux_be_pass = False
        to = False
        main = "err"

        vp_properties = {'mod': False, 'fut_mod': False, 'subj_mod': False, 'finV': 0, 'aux_pres': False,
                         'aux_past': False, 'aux_part': False, 'aux_ger': False, 'aux_be_pres': False,
                         'aux_be_ger': False, 'aux_be_past': False, 'aux_inf': False, 'part': False, 'inf': False,
                         'ger': False, 'aux_do_pres': False, 'aux_do_past': False, 'aux_be_pass': False, 'to': False,
                         'main': "err"}

        def getVPinfo(fin, chain_dict, vp):

            curr_pos = fin.split("#")[1]
            curr_verb = fin.split("#")[4]

            if curr_pos == "MD":
                if curr_verb in ["shall", "will"]:
                    vp['fut_mod'] = True
                elif curr_verb in ["should", "would", "might", "could"]:
                    vp['subj_mod'] = True
                else:
                    vp['mod'] = True

            elif curr_pos == "VBN":
                if curr_verb in ["been"]:
                    vp['aux_part'] = True
                else:
                    vp['part'] = True

            elif curr_pos == "VBG":
                if curr_verb in ["being"]:
                    vp['aux_be_ger'] = True
                elif curr_verb == "having":
                    vp['aux_ger'] = True
                else:
                    vp['ger'] = True

            elif curr_pos == "VBZ":
                if curr_verb in ["does"]:
                    vp['aux_do_pres'] = True
                elif curr_verb in ["is"]:
                    vp['aux_be_pres'] = True
                if curr_verb in ["has"]:
                    vp['aux_pres'] = True
                vp['main'] = "pres"

            elif curr_pos == "VBP":
                if curr_verb in ["have"]:
                    vp['aux_pres'] = True
                elif curr_verb in ["do"]:
                    vp['aux_do_pres'] = True
                elif curr_verb in ["am", "are"]:
                    vp['aux_be_pres'] = True
                vp['main'] = "pres"

            elif curr_pos == "VBD":
                if curr_verb in ["did"]:
                    vp['aux_do_past'] = True
                elif curr_verb in ["was", "were"]:
                    vp['aux_be_past'] = True
                elif curr_verb in ["had"]:
                    vp['aux_past'] = True
                vp['main'] = "past"

            elif curr_pos == "VB":
                if curr_verb in ["be", "have"]:
                    if curr_verb in ["be"]:
                        vp['aux_be_pass'] = True
                    else:
                        vp['aux_inf'] = True
                else:
                    vp['inf'] = True

            elif curr_pos == "TO":
                vp['to'] = True

            for ch in chain_dict:
                getVPinfo(ch, chain_dict[ch], vp_properties)

        def getTenseFromVPinfo(pos_seq, vp):

            finite = "yes"
            tense = "err"
            mood = "err"
            voice = "err"
            progressive = "no"
            negation = "no"

            # Check for negation
            if "RB" in pos_seq:
                negation = "yes"

            # will have been speaking
            if vp['fut_mod'] and vp['aux_inf'] and vp['aux_part'] and vp['ger']:
                tense = "futureIIProg"
                mood = "indicative"
                voice = "active"
                progressive = "yes"

            # will have been spoken/done (passive)
            if vp['fut_mod'] and vp['aux_inf'] and vp['aux_part'] and (vp['part'] or vp['aux_part']):
                tense = "futureII"
                mood = "indicative"
                voice = "passive"

            # would have been speaking
            elif vp['subj_mod'] and ['aux_inf'] and vp['aux_part'] and vp['ger']:
                tense = "condIIProg"
                mood = "subjunctive"
                voice = "active"
                progressive = "yes"

            # would have been spoken (passive)
            elif vp['subj_mod'] and vp['aux_inf'] and vp['aux_part'] and (vp['part'] or vp['aux_part']):
                tense = "condII"
                mood = "subjunctive"
                voice = "passive"

            # have been speaking/having
            elif vp['aux_pres'] and vp['aux_part'] and (vp['ger'] or vp['aux_ger']):
                tense = "presPerfProg"
                mood = "indicative"
                voice = "active"
                progressive = "yes"

            # have been spoken/done (passive)
            elif vp['aux_pres'] and vp['aux_part'] and (vp['part'] or vp['aux_part']):
                tense = "presPerf"
                mood = "indicative"
                voice = "passive"

            # had been speaking/having
            elif vp['aux_past'] and vp['aux_part'] and (vp['ger'] or vp['aux_ger']):
                tense = "pastPerfProg"
                mood = "indicative"
                voice = "active"
                progressive = "yes"

            # had been spoken/done
            elif vp['aux_past'] and vp['aux_part'] and (vp['part'] or vp['aux_part']):
                tense = "pastPerf"
                mood = "indicative"
                voice = "active"

            # will be speaking/having
            elif vp['fut_mod'] and vp['aux_inf'] and (vp['ger'] or vp['aux_ger']):
                tense = "futureIProg"
                mood = "indicative"
                voice = "active"
                progressive = "yes"

                # will be spoken/done (passive)
            elif vp['fut_mod'] and vp['aux_be_pass'] and (vp['part'] or vp['aux_part']):
                tense = "futureI"
                mood = "indicative"
                voice = "passive"

                # can be spoken/done (passive)
            elif vp['mod'] and vp['aux_be_pass'] and (vp['part'] or vp['aux_part']):
                tense = "pres"
                mood = "indicative"
                voice = "passive"

            # will have spoken/had
            elif vp['fut_mod'] and vp['aux_inf'] and (vp['part'] or vp['aux_part']):
                tense = "futureII"
                mood = "indicative"
                voice = "active"

            # would be speaking/having
            elif vp['subj_mod'] and vp['aux_inf'] and (vp['ger'] or vp['aux_ger']):
                tense = "condIProg"
                mood = "subjunctive"
                voice = "active"
                progressive = "yes"

                # would be spoken/had (passive)
            elif vp['subj_mod'] and vp['aux_be_pass'] and (vp['part'] or vp['aux_part']):
                tense = "condI"
                mood = "subjunctive"
                voice = "passive"

                # would have spoken/had
            elif vp['subj_mod'] and vp['aux_inf'] and (vp['part'] or vp['aux_part']):
                tense = "condII"
                mood = "subjunctive"
                voice = "active"

                # was being spoken/done (passive)
            elif vp['aux_do_past'] and vp['aux_be_ger'] and (vp['part'] or vp['aux_part']):
                tense = "pastProg"
                mood = "indicative"
                voice = "passive"
                progressive = "yes"

            # is being spoken/done (passive)
            elif vp['aux_be_pres'] and vp['aux_be_ger'] and (vp['part'] or vp['aux_part']):
                tense = "presProg"
                mood = "indicative"
                voice = "passive"
                progressive = "yes"

            # am speaking/having
            elif vp['aux_do_pres'] and (vp['ger'] or vp['aux_ger']):
                tense = "presProg"
                mood = "indicative"
                voice = "active"
                progressive = "yes"

            # is written/done (passive)
            elif vp['aux_be_pres'] and (vp['part'] or vp['aux_part']):
                tense = "pres"
                mood = "indicative"
                voice = "passive"
                progressive = "no"

                # was speaking/being
            elif vp['aux_do_past'] and (vp['ger'] or vp['aux_ger']):
                tense = "pastProg"
                mood = "indicative"
                voice = "active"
                progressive = "yes"

            # was written (passive)
            elif vp['aux_be_past'] and (vp['part'] or vp['aux_part']):
                tense = "past"
                mood = "indicative"
                voice = "passive"
                progressive = "no"

            # did speak
            elif vp['aux_do_past'] and vp['inf']:
                tense = "past"
                mood = "indicative"
                voice = "active"

            # have spoken/been
            elif vp['aux_pres'] and (vp['part'] or vp['aux_part']):
                tense = "presPerf"
                mood = "indicative"
                voice = "active"

            # had spoken/been
            elif vp['aux_past'] and (vp['part'] or vp['aux_part']):
                tense = "pastPerf"
                mood = "indicative"
                voice = "active"

            # will speak/have
            elif vp['fut_mod'] and (vp['inf'] or vp['aux_inf']):
                tense = "futureI"
                mood = "indicative"
                voice = "active"

            # would speak/have
            elif vp['subj_mod'] and (vp['inf'] or vp['aux_inf']):
                tense = "condI"
                mood = "subjunctive"
                voice = "active"

            # can speak/have
            elif vp['mod'] and (vp['inf'] or vp['aux_inf']):
                tense = "pres"
                mood = "indicative"
                voice = "active"

            # [being seen]XCOMP
            elif vp['aux_be_ger'] and (vp['part'] or vp['aux_part']):
                tense = "-"
                mood = "-"
                voice = "passive"
                progressive = "yes"
                finite = "no"

            # [having seen]XCOMP
            elif vp['aux_ger'] and (vp['part'] or vp['aux_part']):
                tense = "-"
                mood = "-"
                voice = "active"
                progressive = "yes"
                finite = "no"

            elif vp['to']:
                tense = "-"
                mood = "-"
                voice = "-"
                progressive = "-"
                finite = "no"

            elif vp['ger']:
                tense = "-"
                mood = "-"
                voice = "-"
                progressive = "yes"
                finite = "no"

            else:
                tense = vp['main']
                mood = "indicative"
                voice = "active"

            # Correcting voice if tense and mood are empty
            if tense == "err" or mood == "err" or voice == "err":
                tense = "err"
                mood = "err"
                voice = "err"
                progressive = "err"

            return (finite, tense, mood, voice, progressive, negation)

        #### MAIN of deriveENTM ####
        getVPinfo(fin, chain_dict, vp_properties)
        # print "vp_properties", vp_properties
        finite, tense, mood, voice, progressive, negation = getTenseFromVPinfo(pos_seq, vp_properties)
        return (finite, tense, mood, voice, progressive, negation)
        #####################

    # Main verb is the last verb in the dep chain
    def getMainVerbEN(dep_dict):

        res = []
        res_string = ""

        def verbSubCat(dep_dict):

            res = False

            for v in dep_dict:
                curr_pos = v.split("#")[1]
                if curr_pos.startswith("V"):
                    res = True
                else:
                    verbSubCat(dep_dict[v])

            return res

        def searchVV(dep_dict):

            for v in dep_dict:
                curr_pos = v.split("#")[1]
                curr_verb = v.split("#")[4]
                if dep_dict[v] != {}:
                    v_child = dep_dict[v].keys()[0]
                    v_child_pos = v_child.split("#")[1]
                    if v_child_pos == "RB":  # Negation
                        if not verbSubCat(dep_dict[v]):  # Append as mainV if no further main verbs
                            res.append(curr_verb)
                    elif v_child_pos in ["RP", "CC"]:  # Particle
                        res.append(curr_verb)
                else:
                    if curr_pos not in ["CC", "RB"]:
                        if curr_pos == "RP":
                            res[-1] += "-" + curr_verb
                        else:
                            res.append(curr_verb)

                searchVV(dep_dict[v])

        searchVV(dep_dict)

        # print "MAIN", len(res), res
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
        (finite, tense, mood, voice, progressive, negation) = deriveTMEN(pos_seq, fin, chain_dict[fin])
        mainV = getMainVerbEN({fin: chain_dict[fin]})
        # print "RESULT:", finite, tense, mood, voice, progressive, negation, mainV
        temp_res = finite + "\t" + str(
            mainV) + "\t" + tense + "\t" + mood + "\t" + voice + "\t" + progressive + "\t" + negation
        res.append(temp_res)

    return res


def extractVerbDeps(parsed_file):
    sent_nr = 1
    parsed_line = parsed_file.readline()
    verbal_rels = []
    verbal_pos_seqs = []

    while parsed_line:

        print
        "Deriving TMV for English ...", sent_nr, "\r",

        pos_dict = {}  # Dict: {sent_position1: line, sent_position2:line, ...}
        dep_dict = {}  # Dict: {dependency_position1: [sent_position1, sent_position2, ...], ...}
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

                # collect root dependencies and all finite verbs since often wrongly parsed
                if line_split[11] == "__" or line_split[5] in ["VBD", "VBZ", "VBP", "MD", "TO"]:
                    fin_pos.append(int(line_split[0]))

                if int(line_split[9]) in dep_dict:
                    dep_dict[int(line_split[9])].append(int(line_split[0]))
                else:
                    dep_dict[int(line_split[9])] = [int(line_split[0])]

            except Exception as inst:
                print
                "Error reading the parsed line:", parsed_line

            parsed_line = parsed_file.readline()

        try:

            # Sentence collected; now get the chain verbal dependencies of the root
            (chain_deps, verb_rels, inf_vcs, coord) = extractVerbalDepDictEN(fin_pos, dep_dict, pos_dict)

            (verb_seqs, verb_ids) = getVerbSequences(chain_deps)

            tenses = getTenseEN(chain_deps)

            verb_tenses = mergeVerbsTensesEN(verb_seqs, verb_ids, tenses, inf_vcs, coord)

            outputVerbTensePairsFullEN(sent_nr, verb_tenses, pos_dict, out_file)

        except:
            continue

        sent_nr += 1
        parsed_line = parsed_file.readline()


############# MAIN ###############

verb_dep_dict = extractVerbDeps(parsed)

parsed.close()
out_file.close()
