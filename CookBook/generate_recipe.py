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
import re 

def color_section(x):
    if x == 'maroc':
        return 'antiquebrass'
    elif x == 'bretagne':
        return 'glaucous'
    elif x == 'famille':
        return 'jade'
    elif x == 'autriche':
        return 'manatee'
    else: 
        return 'gray'

def replace_name_plat(x):
    return x.replace('entree','Entr\\\'ees').replace('platPoisson', 'Plats de Poisson').replace('platViande','Plats de Viande').replace('dessert','Desserts').replace('sauce', 'Sauces et Condiments').replace('platLegume','Plats de L\\\'egume')

def timefloat2string(x):
    if x < 60: 
        return '{:2d} min'.format(int(x))
    else:
        if int(np.mod(x,60)) > 0: 
            return '{:2d} h : {:2d} min'.format(int(x)/60, int(np.mod(x,60)))
        else: 
            return '{:2d} h'.format(int(x)/60)

def write_time(x):
    if '-' in x: return '-'
    try:
        xx = float(x) 
        return timefloat2string(xx)
    except: 
        return 'mauvais format de temps: {:s}'.format(x)


def get_var_from_include_image(x):
    return line_2.split(x+'=')[1].split('" ')[0].replace('"','').strip()


#recipeDir = './recipeDir/'
recipeDir = '/home/paugam/Website/brignogan.github.io/_posts/'
recipeMMtitle_2skip = [] #[u'mayonnaise',]# u'lottepoivrevert'] # u'Sacher Torte',  u'R\xf4ti de sanglier sauce grand veneur', u'Hareng sous le manteau',   ]
imageDir = '/home/paugam/Website/brignogan.github.io/'
introCatDir = '/home/paugam/Website/brignogan.github.io/pages/'
introCatDir2 = '/home/paugam/Website/brignogan.github.io/CookBook/'
flag_use_Section_Intro_Website = False

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

category_def = [u'famille', u'bretagne', u'maroc', u'autriche']
plat_def     = [u'entree', u'platLegume', u'platPoisson', u'platViande', u'dessert', u'sauce']

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
    
    # activate to debug on specific recipe
    #if 'confitures' not in recipName: continue

    if recipeCat != recipeCat_prev: 
        final2_lines.append(u'\\newpage \n \
\\fancyhead[LE]{{\\bfseries\\nouppercase{{\\leftmark}} }} \n \
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

    if len(lines_txt_per_cat[0])>0: 
        recipeMMintro = lines_txt_per_cat[0]
    else: 
        lines_txt_per_cat.pop(0)
        recipeMMintro = ['']

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
        
        if '### Autres' in cat[0]: 
            recipeMMextra = cat[1:]
        
        recipeMMpreinstruction = None

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
        if 'recipeMMnewPage' in line:     line = line.replace('recipeMMnewPage', recipeMMnewPage)       ; flag_modified = 2                  
        if 'recipeMMtimeprep' in line:    line = line.replace('recipeMMtimeprep', recipeMMtimeprep)       ; flag_modified = 2           
        if 'recipeMMtimecooking' in line: line = line.replace('recipeMMtimecooking', recipeMMtimecooking) ; flag_modified = 2
        if 'recipeMMtimechill' in line:   line = line.replace('recipeMMtimechill', recipeMMtimechill)     ; flag_modified = 2
        if 'recipeMMserve' in line:       line = line.replace('recipeMMserve', recipeMMserve)             ; flag_modified = 2
        if 'recipeMMintro' in line:        line = line.replace('recipeMMintro', recipeMMintro[0])           ; flag_modified = 2

        if 'recipeMMimg' in line:  
            if os.path.isfile(recipeMMimg): 
                line = line.replace('recipeMMimg', recipeMMimg)                 ; flag_modified = 2
            else: 
                line = line.replace('recipeMMimg', '')                 ; flag_modified = 2

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
            for ii, line_ in enumerate(recipeMMvin):
                line_tmp = line_.replace('*','').strip()
                
                if ii == 0: line2p_ += u'\\vins \n'
                if line_tmp[:4] == '####': 
                    if (flag_envVin):
                        flag_envVin = False
                        line2p_ += '\\end{vin}\n'
                    if  u'end' in line2p_.strip().split('\n')[-1] : 
                        line2p_ += u'\\vskip 0.5em '
                    line2p_ += u'\\vins[{:s}]\n'.format(line_tmp.replace('####',''))
                    if not(flag_envVin):
                        flag_envVin = True
                        line2p_ += '\\begin{vin}\n'

                else:
                    if not(flag_envVin):
                        flag_envVin = True
                        line2p_ += '\\begin{vin}\n'
                    #this is here that we ll have to parse the wine list to access page number of corresponding wine
                    line2p_ += line_tmp.replace(u'Vin rouge : ',u'\\emph{Vin Rouge: }')\
                            .replace(u'Vin rouge doux : ',u'\\emph{Vin rouge doux: }')\
                            .replace(u'Vin blanc : ',u'\\emph{Vin blanc: }')\
                            .replace(u'Vin blanc doux : ',u'\\emph{Vin blanc doux: }')\
                            .replace(u'Vin ros\xe9 :',u'\\emph{Vin ros\xe9: }') + '\n \\par \n' 
            
                    

            if flag_envVin: line2p_ += '\\end{vin}\n'
            
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
                line_1 = line_.split('{%')[0].strip()
                line_2 = ''
                if len(line_.split('{%')) > 1: 
                    line_2 = line_.split('{%')[1].strip().split('%}')[0]
                    img_path    = get_var_from_include_image('file')
                    img_caption = get_var_from_include_image('caption') 
                if ('*' not in line_) | (len(recipeMMnote)==1):
                    line2p_intro_ += line_1.replace('*','').strip() 
                else:
                    line2p_ += line_1.replace('*','').strip() 
                    if line_2 != '':
                        line2p_ += '\\begin{center}' + ' {{\includegraphics[width=\\textwidth]{{{:s}}} }}'.format(imageDir+img_path) +  '\\end{center} \n \\par '                     
                    else:
                        if iline_ < len(recipeMMnote)-1:
                            line2p_ += '\n \\par ' 

            line2p.append(line.replace('recipeMMnote',      ''.join(line2p_) ).replace('recipeMM11note', ''.join(line2p_intro_) ) ) 
            
            flag_modified = 1
        
        if ('recipeMMextra' in line): # for extra confiture ingredient and preparation
            line2p = []
            if (len(recipeMMextra)>0): 
                line2p_ = ''
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
                    
                for ii, extra_name_ in enumerate(extra_name):
                    line2p_ += '\\begin{minipage}{\\textwidth}\n'
                    line2p_ += '\extra[{:s}]'.format(extra_name_.strip().replace('**','')) + '\n'
                    if len(extra_ingredient[ii])> 0:
                        line2p_ += '\\begin{petitingreds} \n'
                        for line__ in extra_ingredient[ii]:
                            line2p_ += line__ + '\n'
                        line2p_ += '\\end{petitingreds} \n'
                    else:
                         line2p_ += '\\par \n'
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
                    
                    line2p_ += '\\bigskip'
                    line2p_ += '\\end{minipage}'
                    if (len(recipeMMextra)>1) & (ii < len(recipeMMextra)-1): line2p_ += '\n'
                    
                 
                line2p.append(line.replace('recipeMMextra', line2p_.rstrip()))
                flag_modified = 1
            else: 
                flag_modified = 1

        if 'recipeMMpreinstruction' in line:
            if recipeMMpreinstruction is None:
                line2p = [line.replace('recipeMMpreinstruction', '')]
            else:
                line2p = [line.replace('recipeMMpreinstruction', recipeMMpreinstruction[0])]
            flag_modified = 1

        if flag_modified!=1: line2p = [line]

        for line_ in line2p:
            if '/home/' in line_:
                final2_lines.append(line_)
            elif 'vskip' in line_:
                final2_lines.append(line_)
            else:
                final2_lines.append(re.sub("[,]?[\d]+(?:,\d\d\d)*[\,]?\d*(?:[eE][-+]?\d+)?", lambda match: '${:}$'.format(match.group(0)), line_.replace('mn','min').replace('~','$\\sim$')) ) #parse number to set latex format


    #if 'sangl' in recipName: sys.exit()        

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
