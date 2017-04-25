#/usr/bin/env python
# -*- coding: utf-8 -*-

import sys, re
import codecs

vfeat_file_name = sys.argv[1]
parsed_file_name = sys.argv[2]
lang = sys.argv[3]
vfeat = codecs.open(vfeat_file_name, "r", encoding='utf8')

parsed_file = codecs.open(parsed_file_name, "r", encoding='utf8')
out_file = codecs.open(vfeat_file_name + ".html", "w", encoding='utf8')

# Different functions
def readSent():

   res = ""

   parsed_line = parsed_file.readline()
   
   while parsed_line != "\n":
      
      try:
         res  += " " + parsed_line.strip().split("\t")[1]
      except Exception as inst:
         break
      parsed_line = parsed_file.readline()
      

   return res.strip()

def getVCgroup(idx, vc_groups):

   res = []

   for group in vc_groups:
      if str(idx) in group:
         res = group

   return group

def VCcolors(vc_groups, colors):

   res = {}

   for i in range(len(vc_groups)):
      res[vc_groups[i]] = colors[i]

   return res

def getColor(idx, vccolor_dict):

   res = 'Black'

   for k in vccolor_dict:
      #print "k", k, k.split(","), str(idx)
      k_split = k.split(",")
      idx_split = str(idx).split(",")
      for i in idx_split:
         if i in k_split:
            res = vccolor_dict[k]
            break
         
   #print "getColor", idx, vccolor_dict, "->", res

   return res

def getVCgroup(idx, vc_groups):

   res = ""

   for g in vc_groups:
      g_split = g.split(",")
      if str(idx) in g_split:
         res = g

   return res

# Create language-specific header
if lang == "de":
   out_file.write("<!doctype html> \n<html> \n<head> \n<meta charset=\"utf-8\"> \n<title>DE VCs</title>\n</head> \n<body>\n<table border=\"1\" width=\"100%\"> \n<colgroup> <col width=\"2%\"> <col width=\"20%\"> <col width=\"20%\"> <col width=\"15%\"> <col width=\"2%\"><col width=\"10%\"></colgroup>\n<tr style=\"background-color:rgb(77, 166, 255);text-align:center;font-weight:bold\">\n<td>\nsent nr\n</td>\n<td>sent\n</td>\n<td>clause\n</td>\n<td>\nverbal complex\n</td>\n<td>\nfinite</td>\n<td>main\n</td>\n<td>tense\n</td>\n<td>mood\n</td>\n<td>voice\n</td>\n<td>neg\n</td>\n<td>coord\n</td>\n")
elif lang == "fr":
   out_file.write("<!doctype html> \n<html> \n<head> \n<meta charset=\"utf-8\"> \n<title>FR VCs</title>\n</head> \n<body>\n<table border=\"1\" width=\"100%\"> \n<colgroup> <col width=\"2%\"> <col width=\"20%\"> <col width=\"5%\"> <col width=\"15%\"> <col width=\"5%\"><col width=\"10%\"><col width=\"10%\"></colgroup>\n<tr style=\"background-color:rgb(77, 166, 255);text-align:center;font-weight:bold\">\n<td>\nsent nr\n</td>\n<td>sent\n</td>\n<td>clause\n</td>\n<td>\nverbal complex\n</td>\n<td>\nfinite</td>\n<td>main\n</td>\n<td>tense\n</td>\n<td>mood\n</td>\n<td>voice\n</td>\n<td>neg\n</td>\n<td>coord\n</td>\n")
elif lang == "en":
   out_file.write("<!doctype html> \n<html> \n<head> \n<meta charset=\"utf-8\"> \n<title>EN VCs</title>\n</head> \n<body>\n<table border=\"1\" width=\"100%\"> \n<colgroup> <col width=\"2%\"> <col width=\"20%\"> <col width=\"2%\"> <col width=\"15%\"> <col width=\"2%\"><col width=\"10%\"></colgroup>\n<tr style=\"background-color:rgb(77, 166, 255);text-align:center;font-weight:bold\">\n<td>\nsent nr\n</td>\n<td>sent\n</td>\n<td>clause\n</td>\n<td>\nverbal complex\n</td>\n<td>\nfinite</td>\n<td>main\n</td>\n<td>tense\n</td>\n<td>mood\n</td>\n<td>voice\n</td>\n<td>progr\n</td>\n<td>neg\n</td>\n<td>coord\n</td>\n")

# List of colors for displaying VC annotations 
colors = ['Crimson',  'BlueViolet', 'DeepPink', 'DarkGreen', 'GoldenRod', 'IndianRed', 'Brown', 'CadetBlue', 'Chocolate', 'CornflowerBlue', 'DarkGoldenRod', 'DeepPink', 'DimGray', 'FireBrick', 'Fuchsia']
# Alternating row colors for better readibility
#row_colors = ["#eeeeee", "#ffdab9"]
#row_colors = ["rgb(41,79,157)", "rgb(43,119,188)"]
row_colors = ["rgb(153, 204, 255)", "rgb(204, 230, 255)"]

###### MAIN ######


tmv_line = vfeat.readline().strip()
row_color_idx = 0
sent_nr = 1
while tmv_line:

   color_nr = 0
   text = readSent()
   
   # Read in tense annotations for the current sent
   tmv_dict = {}
   vc_groups = []
   read_more = True
   while read_more and len(tmv_line) != 0:
      
      tmv_line_split = tmv_line.strip().split("\t")
      
      if int(tmv_line_split[0]) == sent_nr:
         verb_idx_split = tmv_line_split[1].split(",")
         vc_groups.append(tmv_line_split[1])
         for i in verb_idx_split:
            
            if lang == "de":
               tmv_dict[int(i)] = (tmv_line_split[2] + "/" + tmv_line_split[3] + "/" + tmv_line_split[4] + "/" + tmv_line_split[5] + "/" + tmv_line_split[6] + "/" + tmv_line_split[7]+ "/" + tmv_line_split[8]+ "/" + tmv_line_split[9] , tmv_line_split[10])
               
            elif lang == "en":
               tmv_dict[int(i)] = (tmv_line_split[2] + "/" + tmv_line_split[3] + "/" + tmv_line_split[4] + "/" + tmv_line_split[5] + "/" + tmv_line_split[6] + "/" + tmv_line_split[7]+ "/" + tmv_line_split[8]+ "/" + tmv_line_split[9] + "/" + tmv_line_split[10] , tmv_line_split[11])

            elif lang == "fr":
               tmv_dict[int(i)] = (tmv_line_split[2] + "/" + tmv_line_split[3] + "/" + tmv_line_split[4] + "/" + tmv_line_split[5] + "/" + tmv_line_split[6] + "/" + tmv_line_split[7]+ "/" + tmv_line_split[8]+ "/" + tmv_line_split[9], tmv_line_split[10])
               
         tmv_line = vfeat.readline()
         
      elif int(tmv_line_split[0]) > sent_nr:
         read_more = False
         
   #print "\n", sent_nr, "Tenses:", tmv_dict
   #print "VCs", vc_groups
   colors_dict = VCcolors(vc_groups, colors)
   #print sent_nr, "colors_dict", colors_dict
   tmv_dict_rev = dict(zip(tmv_dict.values(), tmv_dict.keys()))
   #print "DE tenses rev:", tmv_dict_rev

   out_sent = ""
   out_vfeat_list = []
   out_vfeat = ""
   text_split = text.split()
   if tmv_dict != {}:
      for w in range(1, len(text.split())+1):
         if w in tmv_dict:
            out_sent += "<b><font color=\"" + getColor(getVCgroup(w, vc_groups), colors_dict) + "\">" + text_split[w-1] + "</font></b> "        
            vc_group = getVCgroup(w, vc_groups)
            out_vfeat_list.append((tmv_dict[w][0], tmv_dict[w][1], vc_group))
               
         else:
            out_sent += text_split[w-1] + " "
            
      set_vfeat =  list(set(out_vfeat_list))
  

      for (v, c, g) in set_vfeat:
         v_split = v.split("/")
         if out_vfeat == "":
            out_vfeat += "\n<td>" + c + "\n</td>"
            for i in range(len(v_split)):
               if i == 0:
                  out_vfeat += "<td>\n<font color=\"" + getColor(g, colors_dict) + "\">" + v_split[i] + "\n</td>"
               else:
                  out_vfeat += "<td>\n" + v_split[i] + "\n</td>"
         else:
            #out_vfeat += "\n<tr bgcolor=\"" + row_colors[row_color_idx%2] + "\"><td>" + c + "\n</td>"
            out_vfeat += "\n<tr style=\"background-color:" + row_colors[row_color_idx%2] + "\"><td>" + c + "\n</td>"
            for i in range(len(v_split)):
               if i == 0:
                  out_vfeat += "<td>\n<font color=\"" + getColor(g, colors_dict) + "\">" + v_split[i] + "\n</td>"
               else:
                  out_vfeat += "<td>\n" + v_split[i] + "\n</td>"
            out_vfeat += "</tr>\n"
      clause_num = len(set_vfeat)
      if out_sent != "" and out_vfeat != "":
         #out_file.write("<tr bgcolor=\"" + row_colors[row_color_idx%2] + "\">\n<td rowspan=\"" + str(clause_num) + "\">\n" + str(sent_nr) + "\n</td>\n<td rowspan=\"" + str(clause_num) + "\">\n" + out_sent + "\n</td>\n")
         out_file.write("<tr style=\"background-color:" + row_colors[row_color_idx%2] + "\">\n<td rowspan=\"" + str(clause_num) + "\">\n" + str(sent_nr) + "\n</td>\n<td rowspan=\"" + str(clause_num) + "\">\n" + out_sent + "\n</td>\n")
         row_color_idx += 1
         out_file.write(out_vfeat + "</tr>\n")
   
   sent_nr += 1
      

out_file.write("</table></body> </html>")
