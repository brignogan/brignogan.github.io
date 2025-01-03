from __future__ import print_function
from __future__ import division
from builtins import zip
from past.utils import old_div
import sys
import os
import glob
import importlib
import numpy as np
importlib.reload(sys)
#sys.setdefaultencoding('utf-8')
import io
import pdb
import operator
import subprocess
import re
import pickle
import argparse
import json
import copy
import unicodedata


#####################################################
def ensure_dir(f):
    d = os.path.dirname(f)
    if not os.path.exists(d):
        os.makedirs(d)

################################################
def string_2_bool(string):
    if  string in ['true', 'TRUE' , 'True' , '1', 't', 'y', 'yes', 'yeah', 'yup', 'certainly', 'uh-huh']:
        return  True
    else:
        return False

################################################
def find_ranges(nums):
    nums = sorted(set(nums))
    gaps = [[s, e] for s, e in zip(nums, nums[1:]) if s+1 < e]
    edges = iter(nums[:1] + sum(gaps, []) + nums[-1:])
    return list(zip(edges, edges))

################################################
def isArabic(text):
    flag = False
    indexText = np.zeros(len(text))
    for ii, ch in enumerate(text):
        if ch == '\n': continue
        try:
            name = unicodedata.name(ch).lower()
        except:
           pdb.set_trace()
        if ('arabic' in name) or ('persian' in name):
            indexText[ii] = 1
            flag = True
            #return True;
    if not(flag):
        return False, None

    idxs = find_ranges(np.where(indexText==1)[0])

    words = []
    for idx in idxs:
        words.append(text[idx[0]:idx[1]+1])

    for word in words:
        text = text.replace(word, '{{\setcode{{utf8}}\setarab\RL{{{:s}}}}}'.format(word))

    return True, text

################################################
def color_section(x):
    if x == 'maroc':
        return 'antiquebrass'
    elif x == 'bretagne':
        return 'glaucous'
    elif x == 'famille':
        return 'jade'
    elif x == 'amis':
        return 'cadmiumorange'
    elif x == 'autriche':
        return 'manatee'
    else:
        return 'gray'

def get_format_index(recipeCat,flag):
    if flag == 'clef':
        if recipeCat == 'famille': return 'colorF'
        if recipeCat == 'amis': return 'colorAm'
        if recipeCat == 'autriche': return 'colorA'
        if recipeCat == 'bretagne': return 'colorB'
        if recipeCat == 'maroc': return 'colorM'
    if flag == 'base':
        if recipeCat == 'famille': return 'colorFbf'
        if recipeCat == 'amis': return 'colorAmbf'
        if recipeCat == 'autriche': return 'colorAbf'
        if recipeCat == 'bretagne': return 'colorBbf'
        if recipeCat == 'maroc': return 'colorMbf'

def replace_name_plat(x):
    return x.replace('entree','Entr\\\'ees').replace('platPoisson', 'Plats de Poisson').replace('platViande','Plats de Viande').replace('dessert','Desserts').replace('sauce', 'Sauces et Condiments').replace('platLegume','Plats de L\\\'egume')


def timefloat2string(x):
    if x < 60:
        return '{:2d} min'.format(int(x))
    else:
        if int(np.mod(x,60)) > 0:
            return '{:2d} h : {:2d} min'.format(old_div(int(x),60), int(np.mod(x,60)))
        else:
            return '{:2d} h'.format(old_div(int(x),60))


def write_time(x):
    if '-' in x: return '-'
    try:
        xx = float(x)
        return timefloat2string(xx)
    except:
        return 'mauvais format de temps: {:s}'.format(x)


def get_var_from_include_image(x):
    return line_2.split(x+'=')[1].split('" ')[0].replace('"','').strip()


def parseVinList(string):

    if (string[:3] != 'Vin') & (string[:3] != 'Cid'): return []

    if (string[:3] == 'Vin'): couleur = string.split(':')[0].split(' ')[1].lower().strip()
    if (string[:3] == 'Cid'): couleur = string.split(':')[0].lower().strip()

    vins = re.findall(r'\(([^()]+)\)',string)

    try:
        string = string.split(':')[1].strip().replace('.','')
    except:
        pdb.set_trace()
    if len(vins)>0:
        for vin in vins:
            string = string.replace(vin,'')

        appellations = string.split('()')[:-1]

        for ii, appellation in enumerate(appellations):
            appellations[ii] = appellation.replace(',','').strip()
            if appellations[ii] == 'ou': appellations[ii] = appellations[-1]

        out = []
        for domCuv,appellation in zip(vins,appellations):
            if len(domCuv.split(',')) == 1:
                domain=domCuv.strip()
                cuvee = '-'
            else:
                domain=domCuv.split(',')[0].strip()
                cuvee=domCuv.split(',')[1].strip()

            out.append([couleur,appellation,domain,cuvee])

    else:
        out = []


    return out

def add_graphics(line2p_,imageDir,img_path):

    width_ = 1.
    if 'asperge' in recipName : width_ = .35

    if 'homardgrille' in recipName :
        line2p_ += '\n\\begin{center}'
        line2p_ += '\n{{\includegraphics[width={:.2f}\\textwidth]{{{:s}}} }}'.format(width_,imageDir+img_path.replace('recette','recetteCookbook'))
        line2p_ += '\n \\put(-310,0) {\\tiny $1$- sur le dos, avec le couteau.} '
        line2p_ += '\n \\put(-210,0) {\\tiny $2$- sur le ventre, avec le couteau.} '
        line2p_ += '\n \\put(-100,0) {\\tiny $3$- sur le ventre, avec les ciseaux.} '
        line2p_ += '\n\\end{center} \n \\par '

    elif 'kardinalchnitten' in recipName:
        line2p_ += '\n\\begin{center}'
        line2p_ += '\n{{\includegraphics[width={:.2f}\\textwidth]{{{:s}}} }}'.format(width_,imageDir+img_path.replace('recette','recetteCookbook').replace('.png','.pdf'))
        line2p_ += '\n\\end{center} \n \\par '

    elif 'sachertorte' in recipName :
        line2p_ += '\n\\begin{center}'
        line2p_ += '\n{{\includegraphics[width={:.2f}\\textwidth]{{{:s}}} }}'.format(width_,imageDir+img_path.replace('recette','recetteCookbook').replace('.png','.pdf'))
        line2p_ += '\n\\end{center} \n \\par '

    else:
        line2p_ += '\n\\begin{center}'
        line2p_ += '\n{{\includegraphics[width={:.2f}\\textwidth]{{{:s}}} }}'.format(width_,imageDir+img_path)
        line2p_ += '\n\\end{center} \n \\par '

    return line2p_

parser = argparse.ArgumentParser(description='generate cookboo.tex and run latex')
parser.add_argument('-l','--flag_latex',required=False)
parser.add_argument('-hd','--flag_hd',required=False)
args = parser.parse_args()
if args.flag_latex is None:
    flag_latex = True
else:
    flag_latex = string_2_bool(args.flag_latex)
if args.flag_hd is None:
    flag_hd = True
else:
    flag_hd = string_2_bool(args.flag_hd)

#recipeDir = './recipeDir/'
recipeDir = '../_posts/'
recipeMMtitle_2skip = [] #[u'mayonnaise',]# u'lottepoivrevert'] # u'Sacher Torte',  u'R\xf4ti de sanglier sauce grand veneur', u'Hareng sous le manteau',   ]
imageDir = '../'
introCatDir = '../pages/'
introCatDir2 = './InputTex/'
flag_use_Section_Intro_Website = False

recipeFiles = glob.glob(recipeDir+'*.md')

ensure_dir('./LogError/')

if flag_latex: 
    files_to_remove = glob.glob('cookbook.*')
    # Remove each file
    for file in files_to_remove:
        os.remove(file)

#load tag
tag_category_all = []
tag_plat_all     = []
tag_name         = []
recipeFiles_all = []
for recipeFile in recipeFiles:

    #parse md file from website
    f= io.open(recipeFile,"r", encoding='utf-8')
    lines_recipeFile = f.readlines()
    f.close()

    tag_name.append( ' '.join(os.path.basename(recipeFile).split('-')[3:]).split('.')[0])
    #tag_name.append(os.path.basename(recipeFile).split('-')[-1].split('.')[0])

    if tag_name[-1] in recipeMMtitle_2skip :
        tag_name.pop()
        continue

    recipeFiles_all.append(recipeFile)
    for i, line in enumerate(lines_recipeFile):
        if i == 0: continue

        if 'tag_category:' in line: tag_category_all.append(line.split('_category:')[1].strip())
        if 'tag_plat:'     in line: tag_plat_all.append(line.split('_plat:')[1].strip())

category_def = [u'famille', u'amis', u'bretagne', u'maroc', u'autriche']
plat_def     = [u'entree', u'platLegume', u'platPoisson', u'platViande', u'dessert', u'sauce']

data = list(zip(recipeFiles_all, tag_name, tag_category_all, tag_plat_all))
data = sorted(data, key =  lambda x: ( category_def.index(x[2]), plat_def.index(x[3]), x[1]))

f= io.open("./InputTex/cookbook_template.tex","r", encoding='utf-8')
lines_ori = f.readlines()
f.close()

lineXX = np.where(np.array(lines_ori)=='XX\n')[0][0]
final1_lines = lines_ori[:lineXX]
final2_lines = []
final3_lines = lines_ori[lineXX+1:]

#load template recipe
f= io.open("recipe_template.txt","r", encoding='utf-8')
lines_recipe_template = f.readlines()
f.close()

#load vinDictionary: key=appellation+domain+cuvee
vinDictionary = pickle.load(open('./vinDictionary_fromExcelFile.pickle', 'rb'))

recetteDictionary = {}
recetteDictionary2 = {} if not(os.path.isfile('./recetteDictionary.pickle')) else pickle.load(open('./recetteDictionary.pickle', 'rb'))

specialWords         = [u"N\u01b0\u1edbc M\u1eafm",        u"Ph\u1edf",  u"G\u1ecfi", u'Cu\u1ed1n']
specialWords_inLatex = ["N\\uhorn\\\'{\ohorn}c M{\\\'\\abreve}m", "Ph\h{\\ohorn}",  "G\h{o}i", "Cu{\\\'\ocircumflex}n"]

recetteNoImg = []
recetteNoImgHD = []
line_missingIndex = []
recipeCat_prev  = ''
recipePlat_prev = ''
iPlat = 0
lineVin_error = ['recette, couleur, appelation, domaine, cuvee']
for recipeFile, recipName, recipeCat, recipePlat in data:

    for ispec, specialWord in enumerate(specialWords):
        if specialWord in recipName :
            recipName = recipName.replace(specialWord,specialWords_inLatex[ispec])


    # activate to debug on specific recipe
    #if 'confitures' not in recipName: continue

    if recipeCat != recipeCat_prev:
        if recipeCat_prev != '':
            final2_lines.append(u'\\addImgSection{{./SectionImg/{:s}.png}}                                           \n \
\\fancyhead[LE]{{\\bfseries\\nouppercase{{\\leftmark}} }} \n \
\\fancyhead[RO]{{\\bfseries\\nouppercase{{\\leftmark}} }} \n \
\\fancyhead[LO]{{\\bfseries\\nouppercase{{\\rightmark}} }}\n \
\\fancyhead[RE]{{\\bfseries\\nouppercase{{\\rightmark}} }}\n \
\\section{{{:s}}}\n                                          \
\\addthumb{{{:s}}}{{\\thumbsIcon}}{{white}}{{{:s}}}'.format(recipeCat, recipeCat.title(), recipeCat.title(), color_section(recipeCat))
                )
        else:
            final2_lines.append(u'\\fancyhead[LE]{{\\bfseries\\nouppercase{{\\leftmark}} }} \n \
\\fancyhead[RO]{{\\bfseries\\nouppercase{{\\leftmark}} }} \n \
\\fancyhead[LO]{{\\bfseries\\nouppercase{{\\rightmark}} }}\n \
\\fancyhead[RE]{{\\bfseries\\nouppercase{{\\rightmark}} }}\n \
\\section{{{:s}}}\n                                          \
\\addthumb{{{:s}}}{{\\thumbsIcon}}{{white}}{{{:s}}}'.format(recipeCat.title(), recipeCat.title(), color_section(recipeCat))
                )


        if flag_use_Section_Intro_Website:
            #add introCat
            lines_introCat_ = io.open(introCatDir+'{:s}.md'.format(recipeCat),"r", encoding='utf-8').readlines()
            lines_introCat = []
            count_mark = 0
            for lines_ in lines_introCat_:
                if count_mark >=2: lines_introCat.append(lines_)
                if lines_[:3] == '---': count_mark += 1
        else:
            with open(introCatDir2+'{:s}.tex'.format(recipeCat),'r') as f:
                lines_introCat = f.readlines()

        for lines_ in lines_introCat: final2_lines.append(lines_)
        if len(lines_introCat)>0: final2_lines.append('\\newpage')
        final2_lines.append(u'\\fakesubsection{{{:s}}}\n'.format(replace_name_plat(recipePlat)))
        iPlat = 0

    elif recipePlat != recipePlat_prev:
        final2_lines.append(u'\\newpage \\fakesubsection{{{:s}}}\n'.format(replace_name_plat(recipePlat)))
        iPlat = 0

    recipeCat_prev = recipeCat
    recipePlat_prev = recipePlat

    recipeMMnewPage = '' if iPlat == 0 else '\\newpage'
    iPlat += 1

    #parse md file from website
    f= io.open(recipeFile,"r", encoding='utf-8')
    lines_recipeFile = f.readlines()
    f.close()
    recipeMMmotClef = []
    recipeMMmotClefB = []


    #deal with special character
    lines_recipeFile_copy = lines_recipeFile
    for iline, line in  enumerate(lines_recipeFile_copy):
        for ispec, specialWord in enumerate(specialWords):
            if specialWord in line :
                lines_recipeFile[iline] = lines_recipeFile[iline].replace(specialWord,specialWords_inLatex[ispec])


    for i, line in enumerate(lines_recipeFile):

        if i == 0: continue

        if 'tag_category:' in line: tag_category = line.split('_category:')[1].strip()
        if 'tag_plat:'     in line: tag_plat     = line.split('_plat:')[1].strip()

        if 'title:'             in line: recipeMMtitle = line.split('itle:')[1].strip()

        if 'temps_preparation:' in line: recipeMMtimeprep    = write_time( line.split('_preparation:')[1].strip() )
        if 'temps_cuisson:'     in line: recipeMMtimecooking = write_time( line.split('_cuisson:')[1].strip()     )
        if 'temps_repos:'       in line: recipeMMtimechill   = write_time( line.split('_repos:')[1].strip()       )

        if 'nbre_personne:'     in line: recipeMMserve = line.split('_personne:')[1].\
                                                         strip().replace('‘','').replace('’','')
        if 'image:'             in line: recipeMMimg = imageDir + line.split('mage:')[1].strip()

        if 'index_motClefIngredient:'     in line:
            for ispec, specialWord in enumerate(specialWords):
                if specialWord in line :
                    line = line.replace(specialWord,specialWords_inLatex[ispec])
            recipeMMmotClef = [xx.strip() for xx in line.split('ClefIngredient:')[1].strip().split(',')]

        if 'index_motClefBase:'     in line:
            for ispec, specialWord in enumerate(specialWords):
                if specialWord in line :
                    line = line.replace(specialWord,specialWords_inLatex[ispec])
            recipeMMmotClefB = [xx.strip() for xx in line.split('ClefBase:')[1].strip().split(',')]

        if line == '---\n':
            lineTxt = i
            break

    recetteDictionary[recipName] = recipeMMtitle.split('(')[0].strip()

    lines_txt = lines_recipeFile[lineTxt+1:]
    lines_txt_per_cat = [[]]
    ii = 0
    lines_txt_next = lines_txt[1:]; lines_txt_next.append('\n')
    for i, [line, line_next] in enumerate(zip(lines_txt,lines_txt_next)):
        if (line == '\n') & (line_next[:4] == '### ') :
            lines_txt_per_cat.append([])
            ii += 1
            continue
        elif (line == '\n'):
            continue
        lines_txt_per_cat[ii].append(line)

    if len(lines_txt_per_cat[0])>0:
        recipeMMintro = lines_txt_per_cat[0]

        #special font
        for iline__, line__ in enumerate(recipeMMintro):
            #for cyrillic
            if 'selyodka' in line__:
                line___ = line__.split('Le nom russe')
                recipeMMintro[iline__] = line___[0] + ' Le nom russe de ce plat est : {{\cyrrm{selyodka pod shuboy}}} (selyodka pod shuboy).'

            #for arabic font
            # {\setcode{utf8}\setarab\RL{اَلْعَرَبيَّةُ}.
            if isArabic(line__)[0]:
                recipeMMintro[iline__] = isArabic(line__)[1]

        
        for ii_line_, line_ in enumerate(recipeMMintro):
            #add index entry
            recipeMMmotClefB2 = copy.deepcopy(recipeMMmotClefB)
            for ii_mot, mot_ in enumerate(recipeMMmotClefB2):
                if u'|' in mot_:
                    mot_ori  = mot_
                    mot = mot_.split('|')[1].strip()
                    mot_ = mot_.split('|')[0].strip()
                else:
                    mot_ori  = mot_
                    mot = mot_.strip()
                    mot_ = mot_.split(' ')[0].strip()

                if (' '+mot_ in ' '+line_) |  ("'"+mot_ in ' '+line_) | (u"\u2019"+mot_ in u' '+line_):
                    line_ = line_.replace(mot_, r'{:s}\index{{{:s}|{:s}}}'.format(mot_, mot, get_format_index(recipeCat,'base')))
                    try:
                        idx_ = np.where(np.array(recipeMMmotClefB) == mot_ori )[0]
                        if len(idx_) != 1: pdb.set_trace()
                        recipeMMmotClefB.pop(idx_[0])
                        recipeMMintro[ii_line_] = line_
                    except:
                        pdb.set_trace()
    else:
        lines_txt_per_cat.pop(0)
        recipeMMintro = ['']


    #convert link to biblio
    #if recipName == 'soupecarottescumin': pdb.set_trace()
    recipeMMintro2 = recipeMMintro[:]
    recipeMMintro = []
    for line in recipeMMintro2:
        if "| relative_url }" in line:
            ref_ = line.split('[ [')[1].split('#')[1].split("'")[0]
            line_ = line.split('[ [')[0] + u"\\" + "cite{{{:s}}}.".format(ref_)
            recipeMMintro.append(line_)
        else:
            recipeMMintro.append(line)

    recipeMMvin = []; recipeMMnote = []; recipeMMinstruction = []; recipeMMextra = []
    for i, cat in enumerate(lines_txt_per_cat):

        if ('### Vin' in cat[0]) | ('### Vins' in cat[0]):
            recipeMMvin = cat[1:]

        if cat[0] == '### Notes\n':
            recipeMMnote = cat[1:]

        if '### Ingr' in cat[0]:
            recipeMMingredient = cat[1:]

        if '### P' in cat[0]:
            recipeMMinstruction= cat[1:]

        if '### Autre' in cat[0]:
            recipeMMextra = cat[1:]

        recipeMMpreinstruction = None


    for iline_, line_ in enumerate(recipeMMingredient):
        if '%' in line_ :
            recipeMMingredient[iline_] = recipeMMingredient[iline_].replace('%','\%')

    #check if subtitle for the main recipy is present
    subtitle_mainRecipy = None
    if '####' in lines_txt_per_cat[0][-1]:
        subtitle_mainRecipy =  lines_txt_per_cat[0][-1].replace('**','').replace('####','')


    #append to coockbook
    for line in lines_recipe_template:


        flag_modified = 0

        if 'recipeMMtitle' in line:       line = '%###########\n' +\
                                                 line.replace('recipeMMtitle', recipeMMtitle) + \
                                                 '%###########\n'             ; flag_modified = 2
        if 'recipeMMTag' in line:     line = line.replace('recipeMMTag',recipName.replace(' ','').lower() )       ; flag_modified = 2

        if 'recipeMMnewPage' in line:     line = line.replace('recipeMMnewPage', recipeMMnewPage)       ; flag_modified = 2
        if 'recipeMMRef'     in line:     line = line.replace('recipeMMRef', recipeMMtitle.replace('\h{\ohorn}','o'))       ; flag_modified = 2
        if 'recipeMMtimeprep' in line:    line = line.replace('recipeMMtimeprep', recipeMMtimeprep)       ; flag_modified = 2
        if 'recipeMMtimecooking' in line: line = line.replace('recipeMMtimecooking', recipeMMtimecooking) ; flag_modified = 2
        if 'recipeMMtimechill' in line:   line = line.replace('recipeMMtimechill', recipeMMtimechill)     ; flag_modified = 2
        if 'recipeMMserve' in line:       line = line.replace('recipeMMserve', recipeMMserve)             ; flag_modified = 2
        if 'recipeMMintro' in line:        line = line.replace('recipeMMintro', recipeMMintro[0])           ; flag_modified = 2

        if 'recipeMMimg' in line:
            recipeMMimgHD = recipeMMimg.replace('.png','HD.png').replace('recette/','recette_HD/')
            if (flag_hd) & (os.path.isfile(recipeMMimgHD)):
                line = line.replace('recipeMMimg', recipeMMimgHD)                 ; flag_modified = 2
            elif os.path.isfile(recipeMMimg):
                if (recipName not in recetteNoImgHD): recetteNoImgHD.append(recipName)
                line = line.replace('recipeMMimg', recipeMMimg)                 ; flag_modified = 2
                if (os.path.basename(recipeMMimg) == 'untitled.png') & (recipName not in recetteNoImg): recetteNoImg.append(recipName)
            else:
                line = line.replace('recipeMMimg', '')                 ; flag_modified = 2
                if (recipName not in recetteNoImg):recetteNoImg.append(recipName+'**')

        if 'recipeMMSubTitle' in line:
            line2p = []
            if subtitle_mainRecipy != None:
                line2p.append('\extra[{:s}] \n'.format(subtitle_mainRecipy))
            flag_modified = 1

        if 'recipeMMingredient' in line:
            line2p = []

            recipeMMingredient_per_cat = [[]]
            recipeMMingredient_per_cat_title = []
            ii =0
            for i, line_ in enumerate(recipeMMingredient):
                if (i==0) & (line_[:4] != '####'):
                    recipeMMingredient_per_cat_title.append('')
                if (line_[:4] == '####'):
                    if (len(recipeMMingredient_per_cat[ii])!=0 ):
                        recipeMMingredient_per_cat.append([])
                        ii += 1
                    recipeMMingredient_per_cat_title.append(line_.replace('####',''))
                    continue
                recipeMMingredient_per_cat[ii].append(line_)

            if len(recipeMMingredient_per_cat_title) == 0: recipeMMingredient_per_cat_title.append('')

            for i, recipeMMingredient_per_cat_title_ in enumerate(recipeMMingredient_per_cat_title):
                if recipeMMingredient_per_cat_title_ != '':
                    line2p.append( '\ingredients[{:s}]\n'.format(recipeMMingredient_per_cat_title_.replace(':','').rstrip().strip() ) )
                for line_ in recipeMMingredient_per_cat[i]:
                    line2p.append(line_.replace('*','').strip())
                    line2p.append('\n')

            flag_modified = 1

            for ii_line_, line_ in enumerate(line2p):
                #add index entry
                recipeMMmotClef2 = copy.deepcopy(recipeMMmotClef)
                for ii_mot, mot_ in enumerate(recipeMMmotClef2):
                    if u'|' in mot_:
                        mot_ori  = mot_
                        mot = mot_.split('|')[1].strip()
                        mot_ = mot_.split('|')[0].strip()
                    else:
                        mot_ori  = mot_
                        mot = mot_.strip()
                        mot_ = mot_.split(' ')[0].strip()

                    if (' '+mot_ in ' '+line_) |  ("'"+mot_ in ' '+line_) | (u"\u2019"+mot_ in u' '+line_):
                        line_ = line_.replace(mot_, r'{:s}\index{{{:s}|{:s}}}'.format(mot_, mot, get_format_index(recipeCat,'clef')))
                        idx_ = np.where(np.array(recipeMMmotClef) == mot_ori )[0]
                        if len(idx_) != 1: pdb.set_trace()
                        recipeMMmotClef.pop(idx_[0])
                        line2p[ii_line_] = line_

        if 'recipeMMinstruction' in line:
            line2p = []
            flag_env = 0
            recipeMMinstruction_next = recipeMMinstruction[1:]; recipeMMinstruction_next.append('\n')
            for i, [line_,line_next] in enumerate(zip(recipeMMinstruction,recipeMMinstruction_next)):
                flag_img = False
                if len(line_.split('{% include ')) > 1:
                    line_2 = line_.split('{% include')[1].strip().split('%}')[0]
                    img_path    = get_var_from_include_image('file')
                    img_caption = get_var_from_include_image('caption')
                    line_ = add_graphics(line_.split('{% include')[0].strip(),imageDir,img_path)

                if len(line_.split(']({% post_url ')) > 1:
                    line_3 = '' + line_.split('%})')[1].strip()
                    if line_3[0] != '.': line_3 = ' ' + line_3
                    #get link
                    line_2 = line_.split(']({% post_url')[1].strip().split('%}')[0]
                    try:
                        idx_ = np.where( np.array(recipeFiles_all) == '../_posts/'+line_2.strip()+'.md')[0][0]
                    except:
                        print("###################")
                        print("j'ai pas trouve dans les noms de post la reference '{:s}' qui se trouve le poste '{:s}'".format(line_2,recipName))
                        print("###################")
                        raise NameError('')
                    sectionName = tag_name[idx_].replace(' ','').lower()
                    ref_ = u' (voir page \pageref{{sec:{:s}}})'.format(sectionName)
                    line_ = line_.split(']({% post_url ')[0].replace('[','') + ref_ + line_3

                if (i==0) & (line_[:4] != '####'):
                    ii = i+1
                    ii_ori = ii
                    while (ii<len(recipeMMinstruction)):
                        if recipeMMinstruction[ii][:4] != '####': ii += 1
                        else: break
                    if ii-ii_ori >= 1:
                        line2p.append( u'\\begin{method}\n')
                        line2p.append(line_.replace('*','').strip())
                        line2p.append('\n')
                        line2p.append('\n')
                        flag_method = 1
                    else:
                        line2p.append( u'\\begin{method_noNumber}\n')
                        line2p.append(line_.replace('*','').strip())
                        line2p.append('\n')
                        line2p.append('\n')
                        flag_method = 2

                    if (line_next[:4] == '####'):
                        if    flag_method == 1: line2p.append( '\end{method}\n')
                        elif  flag_method == 2: line2p.append( '\end{method_noNumber}\n')
                        else: pdb.set_trace()

                elif (line_[:4] == '####') & (i==(len(recipeMMinstruction)-1)):
                    line2p.append( u'\\vskip 0.5em')
                    line2p.append( '\methods[{:s}]\n'.format(line_.replace('####','').replace(':','').rstrip().strip() ) )

                elif (line_[:4] == '####'):
                    line2p.append( u'\\vskip 0.5em')
                    line2p.append( '\methods[{:s}]\n'.format(line_.replace('####','').replace(':','').rstrip().strip() ) )
                    ii = i+1
                    ii_ori = ii
                    while (ii<len(recipeMMinstruction)):
                        if recipeMMinstruction[ii][:4] != '####': ii += 1
                        else: break
                    if ii-ii_ori > 1:
                        line2p.append( u'\\begin{method}\n')
                        flag_method = 1
                    else:
                        line2p.append( u'\\begin{method_noNumber}\n')
                        flag_method = 2

                elif (line_next[:4] == '####'):
                    if line_.strip() != '\n': line2p.append(line_.replace('*','').strip())
                    if    flag_method == 1: line2p.append( '\end{method}\n')
                    elif  flag_method == 2: line2p.append( '\end{method_noNumber}\n')
                    else: pdb.set_trace()
                elif (i==len(recipeMMinstruction)-1):
                    if line_.strip() != '\n': line2p.append(line_.replace('*','').strip())
                    if    flag_method == 1: line2p.append( '\end{method}\n')
                    elif  flag_method == 2: line2p.append( '\end{method_noNumber}\n')
                    else: pdb.set_trace()

                else:
                    line2p.append(line_.replace('*','').strip())
                    line2p.append('\n')
                    line2p.append('\n')

            flag_modified = 1


        if 'recipeMMvin' in line:
            line2p = []
            line2p_ = ''
            flag_envVin = False
            labelwidth = 1.9
            for ii, line_ in enumerate(recipeMMvin):
                if (u'Vin rouge doux :' in line_) | (u'Vin blanc doux :' in line_):
                    labelwidth = 2.75
                    break

            for ii, line_ in enumerate(recipeMMvin):
                line_tmp = line_.replace('*','').strip()

                if ii == 0: line2p_ += u'\\vins \n'
                if line_tmp[:4] == '####':
                    if (flag_envVin):
                        flag_envVin = False
                        line2p_ += '\\end{enumerate}\n'+'\\end{vin}\n'
                    if  u'end' in line2p_.strip().split('\n')[-1] :
                        line2p_ += u'\\vskip 0.5em '
                    line2p_ += u'\\vins[{:s}]\n'.format(line_tmp.replace('####',''))
                    if not(flag_envVin):
                        flag_envVin = True
                        line2p_ += '\\begin{vin}\n' + '\\begin{{enumerate}}[labelindent=1.em,labelwidth={0:3.1f}cm,leftmargin={0:3.1f}cm,align=left,itemindent=0pt,labelsep=0pt]\n'.format(labelwidth)

                else:
                    if not(flag_envVin):
                        flag_envVin = True
                        line2p_ += '\\begin{vin}\n'+ '\\begin{{enumerate}}[labelindent=1.em,labelwidth={0:3.1f}cm,leftmargin={0:3.1f}cm,align=left,itemindent=0pt,labelsep=0pt]\n'.format(labelwidth)
                    #this is here that we ll have to parse the wine list to access page number of corresponding wine

                    recipeListVins = parseVinList(line_tmp) #appellation,domain,cuvee

                    if len(recipeListVins)>0:
                        for vin in recipeListVins:
                            #add page to cookook
                            if vin[3] == '-':
                                vin_ = '{:s}'.format(vin[2])
                            else:
                                vin_ = '{:s}, {:s}'.format(vin[2],vin[3])
                            line_tmp = line_tmp.replace( vin_, vin_+\
                                                         ', p. \pageref{{{:s}}}'.format('sec:'+vin[2].replace(' ','').lower()))

                            #add recipe to wine lookuptable
                            key = vin[0].replace(' ','').lower()+vin[1].replace(' ','').lower()+vin[2].replace(' ','').lower()+vin[3].replace(' ','').lower()
                            if key in list(vinDictionary.keys()):
                                if recipName in list(recetteDictionary2.keys()):
                                    vinDictionary[key].append( '{:s} (p. \pageref{{{:s}}})'.format(recetteDictionary2[recipName],'sec:'+recipName.replace(' ','').lower() ) )
                            else:
                                lineVin_error.append( '{:s}, {:s}, {:s}, {:s}, {:s}'.format(recipName,
                                                          vin[0].replace(' ',''),
                                                          vin[1].replace(' ',''),
                                                          vin[2].replace(' ',''),
                                                          vin[3].replace(' ','') ) )

                    line2p_ += line_tmp.replace(u'Vin rouge : ',u'\\item[\\emph{Vin rouge}:]')\
                            .replace(u'Vin rouge doux : ',u'\\item[\\emph{Vin rouge doux}:]')\
                            .replace(u'Vin blanc : ',u'\\item[\\emph{Vin blanc}:]')\
                            .replace(u'Vin blanc doux : ',u'\\item[\\emph{Vin blanc doux}:]')\
                            .replace(u'Cidre : ',u'\\item[\\emph{Cidre}:]')\
                            .replace(u'Vin ros\xe9 :',u'\\item[\\emph{Vin ros\xe9}:]') + '\n' #\\par \n'



            if flag_envVin: line2p_ += '\\end{enumerate}\n'+'\\end{vin}\n'

            if line2p_ != '' : line2p_ += u'\\vskip 3mm \n'

            line2p.append(line.replace('recipeMMvin', line2p_.rstrip()))
            flag_modified = 1



        if 'recipeMMnote' in line:
            line2p = []
            line2p_intro_ = ''
            line2p_ = ''
            for iline_, line_ in enumerate(recipeMMnote):
                if 'vimeoPlayer' in line_:
                    continue
                flag_img = False
                flag_link = False
                line_1 = line_.split('{%')[0].strip()
                line_2 = ''
                if len(line_.split('{% include ')) > 1:
                    line_2 = line_.split('{% include')[1].strip().split('%}')[0]
                    img_path    = get_var_from_include_image('file')
                    img_caption = get_var_from_include_image('caption')
                    line_3 = line_.split('%}')[1].strip()
                    flag_img = True

                if len(line_.split(']({% post_url ')) > 1:
                    line_33 = '' + line_.split('%})')[1].strip()
                    if line_33[0] != '.': line_33 = ' ' + line_33
                    #get link
                    line_22 = line_.split(']({% post_url')[1].strip().split('%}')[0]
                    try:
                        idx_ = np.where( np.array(recipeFiles_all) == '../_posts/'+line_22.strip()+'.md')[0][0]
                    except:
                        print("###################")
                        print("j'ai pas trouve dans les noms de post la reference '{:s}' qui se trouve le poste '{:s}'".format(line_22,recipName))
                        print("###################")
                        raise NameError('')
                    sectionName = tag_name[idx_].replace(' ','').lower()
                    ref_ = u' (voir page \pageref{{sec:{:s}}})'.format(sectionName)
                    line_1 = line_.split(']({% post_url ')[0].replace('[','') + ref_ + line_33   # here need to add pageref according to line_2
                    flag_link = True

                if ('*' not in line_) | (len(recipeMMnote)==1):
                    line2p_intro_ += line_1.replace('*','').strip()
                    if (flag_img) & (line_2 != ''):
                        line2p_intro_ = add_graphics(line2p_intro_,imageDir,img_path)
                else:
                    line2p_ += line_1.replace('*','').strip()
                    if line_2 != '':
                        line2p_ = add_graphics(line2p_,imageDir,img_path)
                        #width_ = 1.
                        #if recipName == 'sauce mousseline': width_ = .35
                        #line2p_ += '\n \\begin{center}' + ' {{\includegraphics[width={:.1f}\\textwidth]{{{:s}}} }}'.format(width_,imageDir+img_path)\
                        #                             +  '\\end{center} \n \\par '
                    else:
                        if iline_ < len(recipeMMnote)-1:
                            line2p_ += '\n \\par '

            line2p.append(line.replace('recipeMMnote',      ''.join(line2p_) ).replace('recipeMM11note', ''.join(line2p_intro_) ) )

            flag_modified = 1

        if ('recipeMMextra' in line): # for extra confiture ingredient and preparation
            #line2p = []
            if (len(recipeMMextra)>0):
                line2p_ = ''
                #add section name
                line2p_+=r'\parindent0pt'+'\n'
                line2p_+=r'\noindent'+'\n'
                title_ = recipeMMtitle.split(' ')[0].lower()
                if title_[-1] == 's': title_ = title_[:-1]

                #split per recipe
                extra_name = []; extra_ingredient = []; extra_prep = []
                ii = -1
                flag_ing = 0; flag_prep = 0
                for line_ in recipeMMextra:

                    if line_[:5] == '#### ':
                        extra_name.append(line_.replace('####','').rstrip())
                        extra_ingredient.append([])
                        extra_prep.append([])
                        ii += 1
                        flag_ing = 0; flag_prep = 0
                    if ('##### Ingr' in  line_):
                        flag_ing = 1; flag_prep = 0
                        continue
                    if ('##### Pr' in  line_):
                        flag_ing = 0; flag_prep = 1
                        continue
                    if (flag_ing == 1):
                        extra_ingredient[ii].append(line_.replace('*','').rstrip())
                    if (flag_prep == 1):
                        extra_prep[ii].append(line_.replace('*','').rstrip())

                if len(extra_name) > 1:
                    title_ = 'Autres {:s}s'.format(title_)
                else:
                    title_ = 'Autre {:s}'.format(title_)

                line2p_+=r'{\color{orangecolor}\Large\textbf{'+title_+'}}%    \parindent0pt'+'\n'
                line2p_+=r'\par'+'\n'
                if 'g' in title_:
                    line2p_+=r'\vskip 2mm'+'\n'
                else:
                    line2p_+=r'\vskip 4mm'+'\n'

                for ii, extra_name_ in enumerate(extra_name):
                    flag_noIngr = True
                    if len(extra_ingredient[ii])> 0:
                        flag_noIngr = False
                        if 'Confiture de poire au gingembre' in extra_name_: line2p_ += '\\newpage\n'
                        #line2p_ += '\\begin{minipage}{\\textwidth}\n'
                        line2p_ += '\\begin{tcolorbox}[blanker,width=\\textwidth,]\n'
                        line2p_ += '\extra[{:s}]'.format(extra_name_.strip().replace('**','')) + '\n'
                        line2p_ += '\\begin{petitingreds} \n'
                        for line__ in extra_ingredient[ii]:
                            line2p_ += line__ + '\n'
                        line2p_ += '\\end{petitingreds} \n'
                        #line2p_ += '\\end{minipage}'
                        line2p_ += '\\end{tcolorbox}'
                        line2p_ += '\\par \n'
                        #line2p_ += '\\medskip'
                        #line2p_ += '\\smallskip'
                        #line2p_ += '\\vskip 1mm \n'
                    else:
                        #line2p_ += '\\begin{minipage}{\\textwidth}\n'
                        line2p_ += '\\begin{tcolorbox}[blanker,width=\\textwidth,]\n'
                        line2p_ += '\extra[{:s}]'.format(extra_name_.strip().replace('**','')) + '\n'
                    if len(extra_prep[ii]) > 1:
                        line2p_ += '\\begin{petitprep} \n'
                        for line__ in extra_prep[ii]:
                            line2p_ += '\\par' + line__ + '\n'
                        line2p_ += '\\end{petitprep} \n'
                    elif len(extra_prep[ii]) == 1:
                        line2p_ += '\\begin{petitprep_noNumber} \n'
                        for line__ in extra_prep[ii]:
                            line2p_ += '\\par' + line__ + '\n'
                        line2p_ += '\\end{petitprep_noNumber} \n'

                    if flag_noIngr:
                        #line2p_ += '\\end{minipage}'
                        line2p_ += '\\end{tcolorbox}'
                        line2p_ += '\\par \n'

                    line2p_ += '\\bigskip'
                    if (len(recipeMMextra)>1) & (ii < len(recipeMMextra)-1): line2p_ += '\n'


                line2p = line.replace('recipeMMextra', line2p_.rstrip())
                flag_modified = 1

                line2p = line2p.split('\n')
                for i_, line2p_ in enumerate(line2p):
                    line2p[i_] = line2p_ + '\n'

                for ii_line_, line_ in enumerate(line2p):
                    #add index entry
                    if 'orangecolor' in line_: continue
                    recipeMMmotClef2 = copy.deepcopy(recipeMMmotClef)
                    for ii_mot, mot_ in enumerate(recipeMMmotClef2):
                        if u'|' in mot_:
                            mot_ori  = mot_
                            mot = mot_.split('|')[1].strip()
                            mot_ = mot_.split('|')[0].strip()
                        else:
                            mot_ori  = mot_
                            mot = mot_.strip()
                            mot_ = mot_.split(' ')[0].strip()

                        if (' '+mot_ in ' '+line_) |  ("'"+mot_ in ' '+line_) | (u"\u2019"+mot_ in u' '+line_):
                            line_ = line_.replace(mot_, r'{:s}\index{{{:s}|{:s}}}'.format(mot_, mot, get_format_index(recipeCat,'clef')))
                            idx_ = np.where(np.array(recipeMMmotClef) == mot_ori )[0]
                            if len(idx_) != 1: pdb.set_trace()
                            recipeMMmotClef.pop(idx_[0])
                            line2p[ii_line_] = line_

            else:
                flag_modified = 1

        #if 'recipeMMpreinstruction' in line:
        #    if recipeMMpreinstruction is None:
        #        line2p = [line.replace('recipeMMpreinstruction', '')]
        #    else:
        #        line2p = [line.replace('recipeMMpreinstruction', recipeMMpreinstruction[0])]
        #    flag_modified = 1

        if flag_modified!=1: line2p = [line]

        if 'recipeMMextraImg' in line:
            imgextras = glob.glob('.'.join(recipeMMimg.split('.')[:-1])+'-extra*.png')
            if len(imgextras) == 0:
                line2p = [line.replace('recipeMMextraImg', '')]
            else:
                line2p = []
                for img_ in imgextras:
                    configImgFile = os.path.dirname(img_).replace('_HD','')+'/'+os.path.basename(img_).split('.')[0]+'.txt'
                    if os.path.isfile(configImgFile):
                        with open(configImgFile,'r') as f:
                            lines_confImg = f.readlines()
                            widthImg = float(lines_confImg[0].split(':')[1])
                            vertivalSpaveImg = '{:3.1f}mm'.format(float(lines_confImg[1].split(':')[1]))
                    else:
                        widthImg = 0.6
                        vertivalSpaveImg = r'-\abovedisplayskip'
                    line2p.append('\showExtraImg{{{:s}}}{{{:3.1f}}}{{{:s}}}'.format(img_,widthImg,vertivalSpaveImg))

        for line_ in line2p:

            percentnumbers = re.findall(r'\d+(?=%)', line_)
            if 'parindent' in line_:
                final2_lines.append(line_)
            elif len(percentnumbers) > 0:
                for percentnumber in percentnumbers:
                    line_ = line_.replace( '{:s}%'.format(percentnumber) ,'{:s}\%'.format(percentnumber) )

            elif 'img/recette' in line_:
                final2_lines.append(line_)
            elif 'vskip' in line_:
                final2_lines.append(line_)
            elif 'includegraphics' in line_:
                final2_lines.append(line_)
            else:
                if '1/2' in line_: line_=line_.replace('1/2','\sfrac{1}{2}')
                if '\xc2\xbd'   in line_: line_=line_.replace('\xc2\xbd',  '\sfrac{1}{2}')
                if '1/3' in line_: line_=line_.replace('1/3','\sfrac{1}{3}')
                if '1/4' in line_: line_=line_.replace('1/4','\sfrac{1}{4}')
                if '\xc2\xbc' in line_: line_=line_.replace('\xc2\xbc','\sfrac{1}{4}')
                if '3/4' in line_: line_=line_.replace('3/4','\sfrac{3}{4}')
                if '\xc2\xbe' in line_: line_=line_.replace('\xc2\xbe','\sfrac{3}{4}')
                final2_lines.append( re.sub("[,]?[\d]+(?:,\d\d\d)*[\,]?\d*(?:[eE][-+]?\d+)?", lambda match: '${:}$'.format(match.group(0)), line_.replace('mn','min').replace('~','$\\sim$')) ) #parse number to set latex format

    if len(recipeMMmotClef) > 0:
        line_missingIndex.append('##'+recipName)
        for xx in recipeMMmotClef:  line_missingIndex.append(xx)

    #if 'sangl' in recipName: sys.exit()

#save missing index
f = io.open("LogError/missinIndex.txt","w", )
for line in line_missingIndex:
    f.writelines((line+'\n'))
f.close()


#save error in matching wine
f = io.open("LogError/errorVinDansRecette.csv","w", )
for line in lineVin_error:
    print(line)
    f.writelines((line+'\n'))
f.close()


#save missing index
f = io.open("LogError/RecetteNoImg.txt","w", )
for line in recetteNoImg:
    f.writelines((line+'\n'))
f.close()
if flag_hd:
    f = io.open("LogError/RecetteNoImgHD.txt","w", )
    for line in recetteNoImgHD:
        f.writelines((line+'\n'))
    f.close()
else:
    if os.path.isfile("LogError/RecetteNoImgHD.txt"): os.remove("LogError/RecetteNoImgHD.txt")
#save file
f= io.open("cookbook.tex","w", )
for line in final1_lines+final2_lines+final3_lines:
    f.write( line )
f.close()

pickle.dump(vinDictionary,open('./vinDictionary_fromWebSiteParsing.pickle','wb'))
pickle.dump(recetteDictionary,open('./recetteDictionary.pickle','wb'))

#with open('vinDictionary_fromExcelFile.json', 'w') as fp:
#    json.dump(vinDictionary, fp)

if flag_latex:
#run latex
    subprocess.call(['pdflatex', '-shell-escape', 'cookbook.tex'])
    #subprocess.call(['texindy','-M mystyle.xdy','-C utf8','-L french','cookbook.idx'])
    subprocess.call(['bash','run_xindy.sh', 'mystyle.xdy', 'cookbook.idx'])
    subprocess.call(['pdflatex', '-shell-escape', 'cookbook.tex'])
    subprocess.call(['bibtex', 'cookbook.aux'])
    subprocess.call(['pdflatex', '-shell-escape', 'cookbook.tex'])
    subprocess.call(['pdflatex', '-shell-escape', 'cookbook.tex'])
    subprocess.call(['bibtex', 'cookbook.aux'])
    subprocess.call(['pdflatex', '-shell-escape', 'cookbook.tex'])

print('')
if flag_hd:
    print('nombre recette avec image HD non presentes: {:4d}.'.format(len(recetteNoImgHD)))
else:
    print("images HD n'ont pas ete prise en compte, flag_hd=", flag_hd)
print('nombre recette avec aucune image          : {:4d}.'.format(len(recetteNoImg)))
print('voir LogError/RecetteNoImg.txt et  LogError/RecetteNoImgHD.txt pour plus de details')

'''
	 \columnbreak
	 \ingredients[recipeMMingredient2title:]
	 recipeMMingredient2
'''
