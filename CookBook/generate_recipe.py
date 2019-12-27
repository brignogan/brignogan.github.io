import sys
import os
import glob
import numpy as np
reload(sys)
sys.setdefaultencoding('utf-8')
import io 
import pdb 
import operator 
import subprocess

def replace_name_plat(x):
    return x.replace('entree','Entree').replace('platPoisson', 'Plat de Poisson').replace('platViande','Plat de Viande').replace('dessert','Dessert').replace('sauce', 'Sauce')

def timefloat2string(x):
    if x < 60: 
        return '{:2d} min'.format(int(x))
    else:
        return '{:.1f} h'.format(round(x/60,1))

def write_time(x):
    if '-' in x: return '-'
    try:
        xx = float(x) 
        return timefloat2string(xx)
    except: 
        return 'mauvais format de temps: {:s}'.format(x)

#recipeDir = './recipeDir/'
recipeDir = '/home/paugam/Website/brignogan.github.io/_posts/'
recipeMMtitle_2skip = [u'mayonnaise', u'lottepoivrevert'] # u'Sacher Torte',  u'R\xf4ti de sanglier sauce grand veneur', u'Hareng sous le manteau',   ]
imageDir = '/home/paugam/Website/brignogan.github.io/'

recipeFiles = glob.glob(recipeDir+'*.md')

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
        
    tag_name.append(os.path.basename(recipeFile).split('-')[-1].split('.')[0])
    
    if tag_name[-1] in recipeMMtitle_2skip : 
        tag_name.pop()
        continue
    recipeFiles_all.append(recipeFile)
    for i, line in enumerate(lines_recipeFile):
        if i == 0: continue
        
        if 'tag_category:' in line: tag_category_all.append(line.split('_category:')[1].strip())
        if 'tag_plat:'     in line: tag_plat_all.append(line.split('_plat:')[1].strip())


category_def = [u'famille', u'bretagne', u'maroc', u'autriche']
plat_def     = [u'entree', u'platPoisson', u'platViande', u'dessert', u'sauce']

data = zip(recipeFiles_all, tag_name, tag_category_all, tag_plat_all)
data = sorted(data, key =  lambda x: ( category_def.index(x[2]), plat_def.index(x[3]), x[1]))

f= io.open("cookbook_template.tex","r", encoding='utf-8')
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

recipeCat_prev  = ''
recipePlat_prev = ''
iPlat = 0
for recipeFile, recipName, recipeCat, recipePlat in data:


    if recipeCat != recipeCat_prev: 
        final2_lines.append(u'\\newpage \section{{{:s}}}\n'.format(recipeCat.title()) )
        final2_lines.append(u'\subsection{{{:s}}}\n'.format(replace_name_plat(recipePlat)))
        iPlat = 0
    
    elif recipePlat != recipePlat_prev: 
        final2_lines.append(u'\\newpage \subsection{{{:s}}}\n'.format(replace_name_plat(recipePlat)))
        iPlat = 0 
    
    recipeCat_prev = recipeCat
    recipePlat_prev = recipePlat

    recipeMMnewPage = '' if iPlat == 0 else '\\newpage'
    iPlat += 1

    #parse md file from website
    f= io.open(recipeFile,"r", encoding='utf-8')
    lines_recipeFile = f.readlines()
    f.close()

    for i, line in enumerate(lines_recipeFile):
        if i == 0: continue
        
        if 'tag_category:' in line: tag_category = line.split('_category:')[1].strip()
        if 'tag_plat:'     in line: tag_plat     = line.split('_plat:')[1].strip()
        
        if 'title:'             in line: recipeMMtitle = line.split('itle:')[1].strip()

        if 'temps_preparation:' in line: recipeMMtimeprep    = write_time( line.split('_preparation:')[1].strip() )
        if 'temps_cuisson:'     in line: recipeMMtimecooking = write_time( line.split('_cuisson:')[1].strip()     )
        if 'temps_repos:'       in line: recipeMMtimechill   = write_time( line.split('_repos:')[1].strip()       )
        
        if 'nbre_personne:'     in line: recipeMMserve = line.split('_personne:')[1].\
                                                         strip().replace("\xe2\x80\x98",'').replace("\xe2\x80\x99",'')
        
        if 'image:'               in line: recipeMMimg = imageDir + line.split('mage:')[1].strip()
    
        if line == '---\n': 
            lineTxt = i
            break
    
        
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

    recipeMMintro = lines_txt_per_cat[0]
    recipeMMvin = []; recipeMMnote = []; recipeMMinstruction = []
    for i, cat in enumerate(lines_txt_per_cat):
        if cat[0] == '### Vin\n':
            recipeMMvin = cat[1:]

        if cat[0] == '### Notes\n':
            recipeMMnote = cat[1:]

        if '### Ingr' in cat[0]:
            recipeMMingredient = cat[1:]

        if '### P' in cat[0]:
            recipeMMinstruction= cat[1:]

        recipeMMpreinstruction = None

    #append to coockbook
    for line in lines_recipe_template:
        
        flag_modified = 0

        if 'recipeMMtitle' in line:       line = line.replace('recipeMMtitle', recipeMMtitle)             ; flag_modified = 2                  
        if 'recipeMMnewPage' in line:       line = line.replace('recipeMMnewPage', recipeMMnewPage)       ; flag_modified = 2                  
        if 'recipeMMtimeprep' in line:    line = line.replace('recipeMMtimeprep', recipeMMtimeprep)       ; flag_modified = 2           
        if 'recipeMMtimecooking' in line: line = line.replace('recipeMMtimecooking', recipeMMtimecooking) ; flag_modified = 2
        if 'recipeMMtimechill' in line:   line = line.replace('recipeMMtimechill', recipeMMtimechill)     ; flag_modified = 2
        if 'recipeMMserve' in line:       line = line.replace('recipeMMserve', recipeMMserve)             ; flag_modified = 2
        if 'recipeMMintro' in line:        line = line.replace('recipeMMintro', recipeMMintro[0])           ; flag_modified = 2

        if 'recipeMMimg' in line:  
            if os.path.isfile(recipeMMimg): 
                line = line.replace('recipeMMimg', recipeMMimg)                 ; flag_modified = 2
            else: 
                continue

        if 'recipeMMingredient' in line: 
            line2p = []

            recipeMMingredient_per_cat = [[]]
            recipeMMingredient_per_cat_title = []
            ii =0
            for i, line_ in enumerate(recipeMMingredient):
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

        if 'recipeMMinstruction' in line: 
            line2p = []
            flag_env = 0
            recipeMMinstruction_next = recipeMMinstruction[1:]; recipeMMinstruction_next.append('\n')
            for i, [line_,line_next] in enumerate(zip(recipeMMinstruction,recipeMMinstruction_next)):
                
                if (i==0) & (line_[:4] != '####'):
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

                elif (line_[:4] == '####') & (i==(len(recipeMMinstruction)-1)):
                    line2p.append( u'\\medskip') 
                    line2p.append( '\methods[{:s}]\n'.format(line_.replace('####','').replace(':','').rstrip().strip() ) )
                
                elif (line_[:4] == '####'): 
                    line2p.append( u'\\medskip') 
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
            for line_ in recipeMMvin:
               line2p_ += line_.replace('*','').strip() + '\n' 
            line2p.append(line.replace('recipeMMvin', line2p_.rstrip()))
            flag_modified = 1
        
        if 'recipeMMnote' in line: 
            line2p = []
            line2p_ = ''
            for line_ in recipeMMnote:
                line_1 = line_.split('{%')[0].strip()
                if len(line_.split('{%')) > 1: 
                    line_2 = line_.split('{%')[1].strip().split('%}')[0]
                line2p_ += line_1.replace('*','').strip() + '\n' 
                
            line2p.append(line.replace('recipeMMnote', line2p_.rstrip()))   
            flag_modified = 1
       
        if 'recipeMMpreinstruction' in line:
            if recipeMMpreinstruction is None:
                line2p = [line.replace('recipeMMpreinstruction', '')]
            else:
                line2p = [line.replace('recipeMMpreinstruction', recipeMMpreinstruction[0])]
            flag_modified = 1

        if flag_modified!=1: line2p = [line]

        for line_ in line2p: 
            final2_lines.append(line_)

#save file
f= io.open("cookbook.tex","w", encoding='utf-8')
for line in final1_lines+final2_lines+final3_lines:
    f.write( line.decode('utf-8') )
f.close()

#run latex
subprocess.call(['pdflatex', 'cookbook.tex'])
subprocess.call(['pdflatex', 'cookbook.tex'])

'''
	 \columnbreak
	 \ingredients[recipeMMingredient2title:]
	 recipeMMingredient2 	
'''
