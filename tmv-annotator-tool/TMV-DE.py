#/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import absolute_import
import sys, re, codecs


parsed_file_name = sys.argv[1]
parsed = open(parsed_file_name, "r")
out_file = open("./output/"+sys.argv[2]+".verbs", "w")
sein_verb_file = open(sys.argv[3], "r")


def readInSeinVerbs(sein_verb_file):

   res = []

   for line in sein_verb_file:
      res.append(line.strip().split("\t")[0])

   return res

def extractVerbalDepDict(fin_pos, dep_dict, pos_dict):

   verbal_tags =["VAFIN", "VMFIN", "VVFIN", "VAINF", "VMINF", "VVINF", "VAPP", "VMPP", "VVPP", "PTKZU", "VAIZU", "VMIZU", "VVIZU", "PTKNEG", "PTKVZ", "KON"]
   verbal_rels = []

   def checkZuInf(inf_deps, dep_dict, pos_dict):
      
      res = False
      
      for ch in inf_deps:
         if "PTKZU" in pos_dict[ch] or "VAIZU" in pos_dict[ch] or "VMIZU" in pos_dict[ch] or "VVIZU" in pos_dict[ch]:
            res = True
            exit
      return res
         
   
   def createDepDict(dep_pos, fin_pos, last_fin_pos, inf_vcs, coord):

      #print "createDepDict", dep_pos, fin_pos, last_fin_pos, inf_vcs, coord
      
      if dep_pos not in dep_dict:                 
         return {}                                                                                                   
      else:                                                                              
         temp_res = {}
         for i in dep_dict[dep_pos]:
            #print dep_dict, dep_dict[dep_pos], i
            curr_id = int(pos_dict[i].split("\t")[0])
            curr_rel = pos_dict[i].split("\t")[11]
            curr_pos = pos_dict[i].split("\t")[5]
            curr_morph = pos_dict[i].split("\t")[7]
            curr_token = pos_dict[i].split("\t")[1].lower()
            curr_lemma = pos_dict[i].split("\t")[3].lower()
            if (curr_pos in verbal_tags):
               
               if i not in fin_pos:
                  #Add zu-Infs as separate dictionary entries
                  if "INF" in curr_pos:
                     if checkZuInf(dep_dict[i], dep_dict, pos_dict): 
                        if curr_id not in fin_pos:
                           fin_pos.append(curr_id)
                           inf_vcs.append((curr_id, last_fin_pos))
                     else:

                        if ("INF" in curr_pos or "PP" in curr_pos) and curr_rel == "CJ":
                           #print "Coordinated VC!", "last_fin_pos", last_fin_pos
                           coord.append(last_fin_pos)
                        
                        temp_res[str(i)+"#"+curr_pos+"#"+curr_rel+"#"+curr_morph+"#"+curr_token+"#"+curr_lemma+"#"+str(last_fin_pos)] = createDepDict(i, fin_pos, last_fin_pos, inf_vcs, coord)
                  elif "IZU" in curr_pos:
                     if curr_id not in fin_pos:
                        fin_pos.append(curr_id)
                        inf_vcs.append((curr_id, last_fin_pos))
                  else:

                     if ("INF" in curr_pos or "PP" in curr_pos) and curr_rel == "CJ":
                           #print "Coordinated VC!", "last_fin_pos", last_fin_pos
                           coord.append(last_fin_pos)
                     
                     temp_res[str(i)+"#"+curr_pos+"#"+curr_rel+"#"+curr_morph+"#"+curr_token+"#"+curr_lemma+"#"+str(last_fin_pos)] = createDepDict(i, fin_pos, last_fin_pos, inf_vcs, coord)
                     
               else:
                  last_fin_pos = dep_pos
                  if "INF" in curr_pos or "IZU" in curr_pos:
                      temp_res[str(i)+"#"+curr_pos+"#"+curr_rel+"#"+curr_morph+"#"+curr_token+"#"+curr_lemma+"#"+str(last_fin_pos)] = createDepDict(i, fin_pos, inf_vcs, coord)

            verbal_rels.append(curr_rel)                                  
         return temp_res                                                                                   
                                                                                                                 
   res = {}
   inf_vcs = []
   coord = []
   for fp in fin_pos:
      #print "fp", fp
      curr_rel = pos_dict[fp].split("\t")[11]
      curr_pos = pos_dict[fp].split("\t")[5]
      curr_morph = pos_dict[fp].split("\t")[7]
      curr_token = pos_dict[fp].split("\t")[1].lower()
      curr_lemma = pos_dict[fp].split("\t")[3].lower()
      #print str(fp)+"#"+curr_pos+"#"+curr_rel+"#"+curr_morph+"#"+curr_token+"#"+str(fp)
      res[str(fp)+"#"+curr_pos+"#"+curr_rel+"#"+curr_morph+"#"+curr_token+"#"+curr_lemma+"#"] = createDepDict(fp, fin_pos, fp, inf_vcs, coord)

   return (res, list(set(verbal_rels)), inf_vcs, coord)

def getVerbalPosSequences(verb_dep_dict):

   res = []

   def getPosSeq(fin, temp_dict, temp_res):
      if temp_dict == {}:
         return ""
      else:
         curr_pos = fin.split("#")[1]
         temp_res.append(curr_pos)
         for dep_verb in temp_dict[fin]:
            getPosSeq(dep_verb, temp_dict[fin], temp_res)
         return temp_res

   for fin in verb_dep_dict:
      temp_res = []
      ret_val = getPosSeq(fin, verb_dep_dict, temp_res)
      res.append(ret_val)

   return res

def getPunctuationDeps(dep_dict, pos_dict):

   res = [1]

   def searchPunct(curr_id, temp_dict, pos_dict):

      if curr_id in pos_dict:
         if pos_dict[curr_id].split("\t")[11] == "--" and (pos_dict[curr_id].split("\t")[5] in ["$.", "$,"] or (pos_dict[curr_id].split("\t")[5] in ["$("] and not pos_dict[curr_id].split("\t")[1].lower() == "\"")):
            res.append(curr_id)
      if curr_id in temp_dict:
         for ch in temp_dict[curr_id]:
            searchPunct(ch, temp_dict, pos_dict)
   
   searchPunct(0, dep_dict, pos_dict)
   
   return sorted(res)

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
         if curr_pos != "KON":                    # Exclude coordination
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


def mergeVerbsTensesDE(verb_seq, verb_ids, tense_seq, inf_vcs, coord):
   
   res =  []

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

def getCurrClause(idx_list, clause_bounds, pos_dict):

   #print "getCurrClause", idx_list, clause_bounds, pos_dict

   res_idx = []
   res = ""
   
   for idx in idx_list:
      #print "range", range(len(clause_bounds))
      for i in range(len(clause_bounds)):
         if i == 0 and clause_bounds[i] == int(idx): # First clause index
            res_idx.append((clause_bounds[i] , clause_bounds[i+1]))
            break
         elif clause_bounds[i] >= int(idx):
            res_idx.append((clause_bounds[i-1] , clause_bounds[i]))
            break

   for clause in sorted(list(set(res_idx)), key=lambda tup: tup[0]):
      start_idx = clause[0]
      if start_idx != 1:
         start_idx += 1
      end_idx = clause[1] + 1
      for j in range(start_idx, end_idx):
         res += pos_dict[j].split("\t")[1] + " "
      res += "|| "
   
   #if len(list(set(res_idx))) > 1:
   #   print "Clausal problem!", list(set(res_idx))
      
   return res


def outputVerbTensePairsFull(sent_nr, verb_tenses, clause_bounds, pos_dict, out_file):

   #print "outputVerbTensePairs", sent_nr, verb_tenses, clause_bounds, pos_dict,
   if verb_tenses != []:
      for pair in verb_tenses:
         curr_clause = getCurrClause(pair[0].split("\t")[0].split(","), clause_bounds, pos_dict)
         #print "curr_clause", curr_clause
         out_file.write(str(sent_nr) + "\t" + pair[0] + "\t" + pair[1] + "\t" + curr_clause + "\n")

def getCleanPosSeq(fin, temp_dict, temp_res):
      
      
      if temp_dict == {}:
         return ""
      else:
         curr_pos = fin.split("#")[1]
         curr_rel = fin.split("#")[2]
         if "INF" in curr_pos:
            if not checkZuInf(temp_dict[fin]):
               #print "curr_rel", curr_rel, "temp_res last elem", temp_res[-1]
               if not (curr_rel == "CJ" and "INF" in temp_res[-1]):
                  #print "temp_res last elem", temp_res[-1]
                  temp_res.append(curr_pos)
            else:                                            # Exclude zu-infinitives
               return ""
         elif "PP" in curr_pos:
            #print "curr_rel", curr_rel, "temp_res last elem", temp_res[-1]
            if not (curr_rel == "CJ" and "PP" in temp_res[-1]):
                  #print "temp_res last elem", temp_res[-1]
                  temp_res.append(curr_pos)
            else:                                            # Exclude zu-infinitives
               return ""
         elif "KON" in curr_pos:                      # Don't go over coordination
            if temp_dict[fin] == {}:
               print "Koord without conjunct!"
            return ""
         else:
            if "IZU" not in curr_pos and "PTKVZ" not in curr_pos:
               temp_res.append(curr_pos)
         for dep_verb in temp_dict[fin]:
            getCleanPosSeq(dep_verb, temp_dict[fin], temp_res)
            
         return temp_res

def getTenseDE(chain_dict, sein_verb_list):

   res = []

   def checkZuInf(inf_deps):
      
      res = False
      
      for ch in inf_deps:
         if "PTKZU" in ch or "VAIZU" in ch or "VMIZU" in ch or "VVIZU" in ch:
            res = True
            
      return res

   def getCleanPosSeq(fin, temp_dict, temp_res):
      
      
      if temp_dict == {}:
         return ""
      else:
         curr_pos = fin.split("#")[1]
         curr_rel = fin.split("#")[2]
         if "INF" in curr_pos:
            if not checkZuInf(temp_dict[fin]):
               #print "curr_rel", curr_rel, "temp_res last elem", temp_res[-1]
               if not (curr_rel == "CJ" and "INF" in temp_res[-1]):
                  #print "temp_res last elem", temp_res[-1]
                  temp_res.append(curr_pos)
            else:                                            # Exclude zu-infinitives
               return ""
         elif "PP" in curr_pos:
            #print "curr_rel", curr_rel, "temp_res last elem", temp_res[-1]
            if not (curr_rel == "CJ" and "PP" in temp_res[-1]):
                  #print "temp_res last elem", temp_res[-1]
                  temp_res.append(curr_pos)
            else:                                            # Exclude zu-infinitives
               return ""
         elif "KON" in curr_pos:                      # Don't go over coordination
            #if temp_dict[fin] == {}:
            #   print "Koord without conjunct!"
            return ""
         else:
            if "IZU" not in curr_pos and "PTKVZ" not in curr_pos:
               temp_res.append(curr_pos)
         for dep_verb in temp_dict[fin]:
            getCleanPosSeq(dep_verb, temp_dict[fin], temp_res)
            
         return temp_res

   def getPosSeq(fin, temp_dict, temp_res):
      if temp_dict == {}:
         return ""
      else:
         curr_pos = fin.split("#")[1]
         temp_res.append(curr_pos)
         for dep_verb in temp_dict[fin]:
            getPosSeq(dep_verb, temp_dict[fin], temp_res)
         return temp_res

   def deriveTMDE(pos_seq, tensed_verb, dep_verbs_dict):

      finite = "yes"
      tense = "err"
      mood = "err"
      voice = "err"
      negation = "no"

      def checkForParticiple(pos_seq):

         res = False

         for p in pos_seq:
            if p in ["VAPP", "VMPP", "VVPP"]:
               res = True
               break

         return res

      def checkForInfinitive(pos_seq):

         res = False

         for p in pos_seq:
            if p in ["VAINF", "VMINF", "VVINF"]:
               res = True
               break

         return res

      def checkForWerden(fin):

         res = False
         
         token = fin.split("#")[4]
         
         if token in ["werden", "werde", "wirst", "wird", "werdet", "wurde", "wurdest", "wurden", "wurdet", "worden", "würde", "würdest", "würden", "würdet"]:
            res = True
            exit

         return res

      def checkForHaben(fin):

         res = False

         token = fin.split("#")[4]
         if token in ["haben", "habe", "hast", "hat", "habt", "hatte", "hattest", "hatten", "hattet"]:
               res = True
               exit

         return res

      def checkForSein(fin):

         res = False

         token = fin.split("#")[4]
         if token in ["bin", "bist", "ist", "sind", "seid", "war", "warst", "waren", "wart"]:
               res = True
               exit

         return res

      def getInf(verb, dep_dict, res):
         if "VAINF" in verb or "VMINF"in verb or "VVINF" in verb:
            res = verb
         else:
            if dep_dict[verb] != {}:
               for dep_verb in dep_dict[verb]:
                  res = getInf(dep_verb, dep_dict[verb], res)
               
         return res

      def getPart(verb, dep_dict, res):
         if "VAPP" in verb or "VMPP"in verb or "VVPP" in verb:
            res = verb.split("#")[5]
            if res == "_":
               res = verb.split("#")[4]
         else:
            if dep_dict[verb] != {}:
               for dep_verb in dep_dict[verb]:
                  res = getPart(dep_verb, dep_dict[verb], res)

         return res

      def checkSeinParticiple(part, sein_verb_list):

         res = False

         for sv in sein_verb_list:
            if sv in part:
               res = True
               exit

         return res

      # Check for the negation and remove negation from the
      # POS sequence list, if any
      if 'PTKNEG' in pos_seq:
         #print "NEG found"
         negation = "yes"
         pos_seq.remove('PTKNEG')

      if pos_seq == "" or pos_seq == []: # Infinitives
         
         finite = "no"
         tense = "-"
         mood = "-"
         voice = "-"
         
      # Tense/mood for a single finite verb ((ich) arbeite/arbeitete)
      elif len(pos_seq) == 1:
         voice = "active"
         morph = tensed_verb.split("#")[3]

         if "ind" in morph:
            mood = "indicative"
            if "pres" in morph:
               tense = "present"
              
            elif "past" in morph:
               tense = "imperfect"
               
       
         elif "subj" in morph:
            if "pres" in morph:           # (er) arbeite
               mood = "konjunktivI"
               tense = "present"
               
            else:                               # (er) täte
               mood = "konjunktivII"
               tense = "present"
               
         elif "imp" in morph:
            mood = "imperative"

      elif len(pos_seq) == 2 and checkForParticiple(pos_seq):

         # Active voice tenses (habe/hatte gearbeitet)
         if not checkForWerden(tensed_verb):
            voice = "active"
            morph = tensed_verb.split("#")[3]

            # Hier, we have to distinguish between active tenses and
            # stative passive!
            if "ind" in morph:
               mood = "indicative"
               if checkForSein(tensed_verb):
                  part_verb = ""
                  part_verb = getPart(tensed_verb, chain_dict, part_verb)
                  
                  if checkSeinParticiple(part_verb, sein_verb_list):
                     if "pres" in morph:              # ist gegangen
                        tense = "perfect"
                        
                     elif "past" in morph:            # war gegangen
                        tense = "pluperfect"
                        
                  else:
                     #print "Zustandspassiv!", part_verb
                     voice = "passive"
                     if "pres" in morph:              # ist geschrieben
                        tense = "present"
                        
                     elif "past" in morph:            # war geschrieben
                        tense = "imperfect"
                        
               else:
                  if "pres" in morph:              # hat gearbeitet
                     tense = "perfect"
                     
                  elif "past" in morph:            # hatte gearbeitet
                     tense = "pluperfect"
                  

            elif "subj" in morph:
               if "pres" in morph:           # (er) habe gearbeitet
                  mood = "konjunktivI"
                  tense = "past"
                  
               elif "past" in morph:
                  mood = "konjunktivII"  # (er) hätte gearbeitet
                  tense = "past"
                  
            elif "imp" in morph:
               mood = "imperative"
               
         # Passive voice tenses (wird/wurde gearbeitet)
         else:
            voice = "passive"
            morph = tensed_verb.split("#")[3]

            if "ind" in morph:
               mood = "indicative"
               if "pres" in morph:
                  tense = "present"
                  
               elif "past" in morph:
                  tense = "imperfect"
                  

            elif "subj" in morph:
               if "pres" in morph:          # (er) werde operiert
                  mood = "konjunktivI"
                  tense = "present"
                  
               elif "past" in morph:        # (er) würde operiert
                  mood = "konjunktivII"
                  tense = "present"
                  
            elif "imp" in morph:
               mood = "imperative"
         
      elif len(pos_seq) == 3 and checkForParticiple(pos_seq) and checkForInfinitive(pos_seq):

         inf_verb = ""
         inf_verb = getInf(tensed_verb, chain_dict, inf_verb)
         morph = tensed_verb.split("#")[3]
      
         # Active voice tenses ((ich) werde/soll gearbeitet haben)
         if not checkForWerden(inf_verb):
            voice = "active"

            if "ind" in morph:
               mood = "indicative"
               if "pres" in morph:
                  if checkForWerden(tensed_verb): #werde gearbeitet haben
                     tense = "futureII"
                     
                  else:
                     tense = "perfect"     # soll gearbeitet haben
                     
               elif "past" in morph: # musste gearbeitet haben
                  tense = "pluperfect"
                  

            elif "subj" in morph:
               if checkForWerden(tensed_verb): #werde gearbeitet haben
                  tense = "futureII"
                  if "pres" in morph:           # (er) werde gearbeitet haben
                     mood = "konjunktivI"
                     
                  elif "past" in morph:         # (er) würde gearbeitet haben
                     mood = "konjunktivII"
                     
               else:
                  tense = "perfect"
                  if "pres" in morph:           # (er) solle gearbeitet haben
                     mood = "konjunktivI"
                     
                  elif "past" in morph:         # (er) müsste gearbeitet haben
                     mood = "konjunktivII"
                     
                     
            elif "imp" in morph:
               mood = "imperative"

         # Passive voice (werde gefragt werden; soll/sollte gefragt werden)
         else:
            voice = "passive"
            if "ind" in morph:
                  mood = "indicative"
                  if checkForWerden(tensed_verb):  # (ich) werde gefragt werden/sein
                     if "pres" in morph:
                        tense = "futureI"

                  # Modals: difficult for sollen/wollen
                  else:
                     if "pres" in morph:     # (ich) soll gefragt werden
                        tense = "present"
                        
                     elif "past" in morph:   # (ich) musste gefragt werden
                        tense = "imperfect"
                        

            elif "subj" in morph:
               if "pres" in morph:
                  mood = "konjunktivI"
                  if checkForWerden(tensed_verb): # (er) werde gefragt werden
                     tense = "futureI"
                     
                  else:                                          # (er) solle gefragt werden
                     tense = "present"
                     
               elif "past" in morph:
                  mood = "konjunktivII"
                  if "würd" in tense_verb: # (er) würde gefragt werden
                     tense = "futureI"
                     
                  else:                            # (er) müsste gefragt werden
                     tense = "present"
                     
            elif "imp" in morph:
               mood = "imperative"

      elif (len(pos_seq) == 2 or len(pos_seq) == 3) and not checkForParticiple(pos_seq) and checkForInfinitive(pos_seq):
         
         voice = "active"
         morph = tensed_verb.split("#")[3]

         # Finite "werden"
         if checkForWerden(tensed_verb):
            if "ind" in morph:                           # (ich) werde arbeiten (sollen)
               mood = "indicative"
               if "pres" in morph:
                  tense = "futureI"
                  
                  
            elif "subj" in morph:
               if "pres" in morph:                            # (er) werde kommen (wollen)
                  mood = "konjunktivI"
                  tense = "futureI"
                          
               elif "past" in morph:       # (er) würde kommen (wollen)
                  mood = "konjunktivII"
                  tense = "present"
                  
               
         # Finite "haben" with modals (habe/hatte arbeiten sollen)
         elif checkForHaben(tensed_verb) and len(pos_seq) == 3:
            if "pres" in morph:
               tense = "perfect"
                   
            elif "past" in "morph":
               tense = "pluperfect"
               
               
         # Other cases (soll/sollte arbeiten (wollen))
         else:

            if "ind" in morph:
               mood = "indicative"
               if "pres" in morph:
                  tense = "present"
                  
               elif "past" in morph:
                  tense = "imperfect"
                  

            elif "subj" in morph:
               #print "BIN SUBJ"
               if "pres" in morph:
                  mood = "konjunktivI"
                  tense = "present"      # (er) solle kommen (wollen)
                        
               elif "past" in morph:       # (er) sollte/müsste kommen (wollen)
                  mood = "konjunktivII"
                  tense = "present"
                  
                  
            elif "imp" in morph:
               mood = "imperative"
       
      elif len(pos_seq) == 3 and not checkForInfinitive(pos_seq):
         voice = "passive"
         morph = tensed_verb.split("#")[3]

         if "ind" in morph:
            mood = "indicative"
            if "pres" in morph:           # (er) ist gefragt worden
               tense = "perfect"
               
            elif "past" in morph:         # (er) war gefragt worden
               tense = "pluperfect"
               
               
         elif "subj" in morph:
            if "pres" in morph:           # (er) sei operiert worden
               mood = "konjunktivI"
               tense = "past"
               
            elif "past" in morph:         # (er) wäre operiert worden
               mood = "konjunktivII"
               tense = "past"
               
         elif "imp" in morph:
            mood = "imperative"

      elif len(pos_seq) == 4: 

         voice = "passive"
         morph = tensed_verb.split("#")[3]

         if checkForWerden(tensed_verb): # (ich) werde gefragt worden sein
                                                          # MISSING: wird überprüfen lassen müssen (NOT PASSIVE!!)

            if "ind" in morph:
               mood = "indicative"
               if "pres" in morph:
                  tense = "futureII"
                  
               
            elif "subj" in morph:
               if "pres" in morph:           # (er) werde gefragt worden sein
                  mood = "konjunktivI"
                  tense = "futureII"
                  
                  
               elif "past" in morph:         # (er) würde gefragt worden sein
                  mood = "konjunktivII"
                  tense = "past"
                  
            elif "imp" in morph:
               mood = "imperative"
            
         else:

            if "ha" in tensed_verb or "hä" in tensed_verb:
               if "ind" in morph:
                  mood = "indicative"
                  if "pres" in morph:      # (ich) habe operiert werden müssen
                     tense = "perfect"
                     
                  else:                         # (ich) hatte operiert werden müssen
                     tense = "pluperfect"
                     
          
               elif "subj" in morph:
                  if "pres" in morph:           # (er) habe operiert werden müssen
                     mood = "konjunktivI"
                     tense = "past"
                     
                  elif "past" in morph:         # (er) hätte operiert werden müssen
                     mood = "konjunktivII"
                     tense = "past"
                     
               elif "imp" in morph:
                  mood = "imperative"
         
            else:
               if "ind" in morph:
                  mood = "indicative"
                  if "pres" in morph: # soll gefragt worden sein
                     tense = "perfect"
                     
                  elif "past" in morph: # musste gefragt worden sein
                     tense = "imperfect"
                     

               elif "subj" in morph:
                  if "pres" in morph:           # (er) solle/habe operiert werden müssen
                     mood = "konjunktivI"
                     tense = "present"
                     
                  elif "past" in morph:         # (er) sollte operiert werden müssen
                     mood = "konjunktivII"
                     tense = "present"
                     
                     
               elif "imp" in morph:
                  mood = "imperative"

                  

      # Correcting voice if tense and mood are empty
      if tense == "err" and mood == "err":
         voice = "err"

      return (finite, tense, mood, voice, negation)

   for fin in chain_dict:
      temp_res = []
      tense = ""
      mood = ""
      #pos_seq = getPosSeq(fin, chain_dict, temp_res)
      pos_seq = getCleanPosSeq(fin, chain_dict, temp_res)
      #print "derive tense", pos_seq, fin, chain_dict[fin]
      (finite, tense, mood, voice, negation) = deriveTMDE(pos_seq, fin, chain_dict[fin])
      mainV = getMainVerbDE({fin: chain_dict[fin]})
      #print "RESULT:", tense, mood, voice, negation, mainV
      temp_res = finite + "\t" + str(mainV) + "\t" + tense + "\t" + mood + "\t" + voice + "\t" + negation
      res.append(temp_res)
      
   return res

def getMainVerbDE(dep_dict):

   res = []
   res_string = ""

   #print "getMain", dep_dict

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
         curr_lemma = v.split("#")[5]
         if curr_lemma == "_":
            curr_lemma = curr_verb
         if "FIN" in curr_pos:
            if dep_dict[v] == {} or not verbSubCat(dep_dict[v]): # single finite verb available
               res.append(curr_verb)
         else:
            if "VV" in curr_pos: # non-finite full verb
               # exclude Rezipientenpassiv
               if curr_lemma not in ["lassen", "bleiben", "lernen", "bekommen", "kriegen"]:
                  res.append(curr_verb)
               else:
                  if dep_dict[v] == {}:
                     res.append(curr_verb)
            # non-finite auxiliaries/modals (without a full verb)
            elif ("VA" in curr_pos or "VM" in curr_pos) and (dep_dict[v] == {} or not verbSubCat(dep_dict[v])):
               res.append(curr_verb)
               
         searchVV(dep_dict[v])

   searchVV(dep_dict)
         
   #print "MAIN", len(res), res
   for v in res:
      if res_string == "":
         res_string += v
      else:
         res_string += "," + v
   
   return res_string

def extractVerbDeps(parsed_file):

    sent_nr = 1
    parsed_line = parsed_file.readline()
    verbal_rels = []
    verbal_pos_seqs = []

    sein_verb_list = readInSeinVerbs(sein_verb_file)

    while parsed_line:

        print "Deriving TMV for German ... ", sent_nr, "\r",

        pos_dict = {} # Dict: {sent_position1: line, sent_position2:line, ...}
        dep_dict = {} # Dict: {dependency_position1: [sent_position1, sent_position2, ...], ...}
        dep_rel = {} # Dict: {sent_position1: dependency_relation, sent_position2: dependency_relation, ...}
        fin_pos = []
        verb_dep_dict = {} # Dict: {root_position: {...}, ...}
        sent_lines = []
           
        while parsed_line != "\n":

            sent_lines.append(parsed_line.strip().decode("UTF-8"))
            line_split = parsed_line.strip().split("\t")
            try:
               pos_dict[int(line_split[0])] = parsed_line.strip()
               dep_rel[int(line_split[0])] = line_split[11]

               # collect root dependencies and all finite verbs and zu-particles 
               if line_split[11] == "__" or "FIN"in line_split[5]:
               
                  fin_pos.append(int(line_split[0]))
               
               if int(line_split[9]) in dep_dict:
                  dep_dict[int(line_split[9])].append(int(line_split[0]))
               else:
                  dep_dict[int(line_split[9])] = [int(line_split[0])]

            except Exception as inst:
               print "Error reading the parsed line:", parsed_line
                  
            parsed_line = parsed_file.readline()

        try:

            # Sentence collected; now get the chain verbal dependencies of the root
            (chain_deps, verb_rels, inf_vcs, coord) = extractVerbalDepDict(fin_pos, dep_dict, pos_dict)
            #print "dep_dict", dep_dict, fin_pos
            
            clause_bounds = getPunctuationDeps(dep_dict, pos_dict)
            
            (verb_seqs, verb_ids) = getVerbSequences(chain_deps)
            
            tenses = getTenseDE(chain_deps, sein_verb_list)
            #print "tenses", tenses
            
            verb_tenses = mergeVerbsTensesDE(verb_seqs, verb_ids, tenses, inf_vcs, coord)
            #print "verb_tenses", verb_tenses
           
            outputVerbTensePairsFull(sent_nr, verb_tenses, clause_bounds, pos_dict, out_file)
            verbal_rels += verb_rels
            #print sent_nr, "->", fin_pos, clause_bounds, "\n"
            
        except:
            continue
         
        sent_nr += 1
        parsed_line = parsed_file.readline()

        
############# MAIN ###############

verb_dep_dict = extractVerbDeps(parsed)


parsed.close()
out_file.close()
sein_verb_file.close()
