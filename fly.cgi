#!/usr/bin/python

import cgi, cgitb
cgitb.enable()
import json, os
import random

MAX_SCORE = 30
MIN_SCORE = 5
AUTO_ON_SEX = 6
LINK_DISTANCE = 5
LINKED_GENES = 6
NOMENCLATURE = 0.5
DOM_REC = 1
MISSING_GENE = 4
WRONG_CH = 3
WRONG_CH_MAX = 6
EYE_COLOR = 6
GRADE_LEGEND = ['dom_rec: A dominant mutation is written as recessive or vice versa</br>']
GRADE_LEGEND.append('eye_color: Failure to resolve the eye color mutation into two genes</br>')
GRADE_LEGEND.append('link_distance: Link distance is off by 10% or more</br>')
GRADE_LEGEND.append('missing_genes: One or more genes in the karyotype are missing from the final answer</br>')
GRADE_LEGEND.append('wrong_ch: A gene was put on the wrong chromosome</br>')
GRADE_LEGEND.append('linked_genes: Linked genes were put on different chromosomes OR unlinked genes were put on the same chromosome</br>')
GRADE_LEGEND.append('nomenclature: Proper Drosophila nomenclature was not used</br>')
GRADE_LEGEND.append('auto_on_auto: An autosomal gene was placed on the sex chromosome or vice versa</br>')
GRADE_LEGEND = ''.join(GRADE_LEGEND)

def main():
    # grab user input from front end
    form = cgi.FieldStorage()

    print "Content-Type: text/html"
    print ''  # this blank line is necessary for some bizarre reason
    print '<html><head><title>Test</title></head><body><link rel="stylesheet" href="fly.css">'

    # get cross-making variables here
    student = form.getvalue("person")
    crosstype = form.getvalue('crosstype')
    real = form.getvalue('realsubmit')
    fake = form.getvalue('fakesubmit')

    ID_list = loadList("IDs.txt", True)
    # print ID_list

    if student[:5] == 'reset':
        # print "reset</br>"
        student = format_id(student[-7:])
        if os.path.isfile('data/' + student + '.json'):
            # print " exists </br>"
            info = ''
            k = loadKaryo('data/' + student + '.json')
            if k.has_key('raw_answer'):
                # print "raw"
                del k['raw_answer']
            if k.has_key('final_answer'):
                # print "final"
                info = k['final_answer']['info']
                del k['final_answer']
            if k.has_key('score_list'):
                del k['score_list']
            saveKaryo(k, 'data/' + student + '.json')
            print "Answer reset for ", info
        quit()
    elif student.lower() == 'grade report':
        print "Instructor grade report:</br></br>"
        for i in ID_list:
            # print i
            if os.path.isfile('data/' + i + '.json'):
                # print " exists"
                k = loadKaryo('data/' + i + '.json')
                if k.has_key('raw_answer'):
                    # print " has answer"
                    print print_answer(k)
                    print "</br>"
            # print "</br>"
        quit()
    elif student.lower() == 'grade csv':
        grade_str = "Student ID,Last name,First name,section,score,submission time,final answer,raw input\n"
        for i in ID_list:
            # print i
            if os.path.isfile('data/' + i + '.json'):
                # print " exists"
                k = loadKaryo('data/' + i + '.json')
                if k.has_key('raw_answer'):
                    # print " has answer"
                    st = str(k['raw_answer']['submit_time'])
                    st = st.replace(',', '')
                    ra = str(k['raw_answer'])
                    ra = ra.replace(',', ';')
                    ra = ra.replace("u'", "'")
                    score = k['final_answer']['score']
                    info = k['final_answer']['info']
                    info = info.replace(' ', '')
                    fa = str(k['final_answer'])
                    fa = fa.replace(',', ';')
                    fa = fa.replace("u'", "'")
                    # ID, last name, first name, section, score, submission time, final answer, raw user input
                    grade_str += ','.join([info, str(score), st, fa, ra])
                    grade_str += '\n'
        with open("grades.csv", 'w') as grades:
            grades.write(grade_str)
                        # print "</br>"
        print '<a href="grades.csv">Download the grade report</a>'
        quit()

    student = format_id(student)
    if student not in ID_list:
        print "Your student ID was not recognized, please try again."
        quit()

    file_name = "data/" + student + ".json"
    # print file_name, "</br>"
    # print cross output
    print '<h3>Student ID: ' + student + '</h3>'
    # printKaryo(k)

    if crosstype == 'Po':  # Initialization of karyotype, stocks, and initial crosses
        if os.path.exists(file_name):
            # read the student data from their own .json file
            k = loadKaryo(file_name)
            # print 'read from file</br>'
        else:
            # create new karyotype if none exists
            k = createKaryotype()
            saveKaryo(k, file_name)

        s = createStocks(k)
        mut = stock_labels(k)

        print 'Your unknown stock has the following mutant phenotypes:</br>'
        print k['genes'][1]['name'] + ' bristles</br>'
        print k['genes'][2]['name'] + ' eye texture</br>'
        print k['genes']['double_color'] + ' eye color</br>'
        c1 = crossStocks(k, s[4], s[9])
        c1_table = compose_table(c1, 1000)
        c2 = crossStocks(k, s[9], s[4])
        c2_table = compose_table(c2, 1000)
        c3 = crossStocks(k, s[4], s[0])
        c3_table = compose_table(c3, 1000)

        print "<hr>"
        print 'Cross 1: ' + mut[4] + ' males X wild type females</br></br>'
        print c1_table
        print '<hr>'

        print 'Cross 2: ' + mut[4] + ' females X wild type males</br></br>'
        print c2_table
        print '<hr>'

        print 'Cross 3: ' + mut[4] + ' males X Curly Dicheate females</br></br>'
        print c3_table
        print '<hr>'

        print 'Stocks for crosses:</br></br>'
        print '4 - ' + mut[4] + '</br>'
        print '5 - ' + mut[5] + '</br>'
        print '6 - ' + mut[6] + '</br>'
        print '7 - ' + mut[7] + '</br>'
        print '8 - ' + mut[8] + '</br>'
        print '9 - ' + mut[9]
    elif crosstype == 'F11':
        if os.path.isfile(file_name):
            # print "exists</br>"
            # read the student data from their own .json file
            k = loadKaryo(file_name)
            s = createStocks(k)
        else:
            print "You haven't even seen your karyotype yet! Try again."
            quit()
        # print k
        c11 = crossStocks(k, s[1], s[1])
        c11_table = compose_table(c11, 6000)
        print 'Cross 11: F1 males X F1 females</br>'
        # c11_table.encode('ascii', 'ignore')
        print c11_table
    elif crosstype == 'F12':
        if os.path.isfile(file_name):
            # read the student data from their own .json file
            k = loadKaryo(file_name)
            s = createStocks(k)
        else:
            print "You haven't even seen your karyotype yet! Try again."
            quit()
        c22 = crossStocks(k, s[2], s[2])
        c22_table = compose_table(c22, 6000)
        print 'Cross 22: F1 males X F1 females</br>'
        print c22_table
    elif crosstype == 'TC':
        if os.path.isfile(file_name):
            # read the student data from their own .json file
            k = loadKaryo(file_name)
            s = createStocks(k)
        else:
            print "You haven't even seen your karyotype yet! Try again."
            quit()
        mut = stock_labels(k)
        try:
            tmale = int(form.getvalue('tcmale'))
            tfemale = int(form.getvalue('tcfemale'))
        except:
            print "One or both of the parents was not entered correctly!"
            quit()

        lowrange = [1, 2]
        hirange = range(4, 10) # list from 4-9, inclusive
        if tmale in hirange and tfemale in lowrange:
            pass
        elif tfemale in hirange and tmale in lowrange:
            pass
        else:
            print 'This was not a good choice for a cross.  In reality, you would have spent a considerable amount of time and effort in collecting the appropriate flies, and the progeny of this cross would have given you no useful information. Check the lab manual to see what crosses you can make.'
            quit()
        try:
            cTC = crossStocks(k, s[tmale], s[tfemale])
            cTC_table = compose_table(cTC, 6000)
            print 'Cross ' + str(tmale) + str(tfemale) + ': ' + mut[tmale] + ' males' + ' X ' + mut[tfemale] + ' females</br>'
            print cTC_table
        except:
            print 'Error, one or both of the parents was not selected'
    elif crosstype == 'Cy':
        if os.path.isfile(file_name):
            # read the student data from their own .json file
            k = loadKaryo(file_name)
            s = createStocks(k)
        else:
            print "You haven't even seen your karyotype yet! Try again."
            quit()
        mut = stock_labels(k)
        # ch_loc cross requires the male be 3, the female homozygous recessive (>=4)
        try:
            cmale = int(form.getvalue('Cymale'))
            cfemale = int(form.getvalue('Cyfemale'))
        except:
            print "One or both of the parents was not entered correctly!"
            quit()

        if cmale != 3 or cfemale < 4:
            print 'Had you made this cross, you would have woken up early, removed the parents, let the flies mature, carefully identified the appropriate mutants, and set up that cross, and gotten no useful information. Please check your lab manual and try again.'
        elif cmale == 3 and cfemale > 3:
            cCY = crossStocks(k, s[cmale], s[cfemale])
            cCY_table = compose_table(cCY, 6000)
            print 'Cross 3' + str(cfemale) + ': ' + mut[cmale] + ' males X ' + mut[cfemale] + ' females</br>'
            print cCY_table
        else:
            print 'Unknown error, cmale: ' + str(cmale) + ' cfemale: ' + str(cfemale)
    elif real == 'Final Submit' or fake == 'Final Submit':
        if fake == 'Final Submit':
            print "You did not follow directions, please try again."
            quit()

        if not os.path.isfile(file_name):
            print "You don't even have a karyotype generated yet! Final submission is premature."
            quit()

        k = loadKaryo(file_name)
        if k.has_key('raw_answer'):
            print "You have already submitted your answer, see your results below</br>"
            print print_answer(k)
            print '</br>'
            print GRADE_LEGEND
            quit()

        section = form.getvalue("day")
        if section == "none":
            print "You need to select your section!"
            quit()

        penalty = 0
        lastname = str(form.getvalue('lastname'))
        firstname = str(form.getvalue('firstname'))
        final = {'xmut1': form.getvalue('xmut1')}
        ans_vars = ['xmut2', 'xrecomb', '2mut1', '2mut2', '2recomb', '3mut1', '3mut2', '3recomb', '4mut1', '4mut2', '4recomb']
        for i in ans_vars:
            final[i] = form.getvalue(i)
            if type(final[i]) == str:
                final[i] = final[i].replace(' ', '')
                final[i] = final[i].replace(',', '')  # sanitize user input for eventual CSV file

        # save their raw answer
        from time import strftime, localtime
        final['submit_time'] = strftime("%a, %d %b %Y %H:%M:%S", localtime())
        k['raw_answer'] = final
        # print k

        answer = list()
        answer.append([final['xmut1'], final['xmut2'], final['xrecomb']])
        answer.append([final['2mut1'], final['2mut2'], final['2recomb']])
        answer.append([final['3mut1'], final['3mut2'], final['3recomb']])
        answer.append([final['4mut1'], final['4mut2'], final['4recomb']])
        final_answer = dict()
        score_dict = {'link_distance': 0, 'nomenclature': 0, 'auto_on_auto': 0, 'linked_genes': 0, 'dom_rec': 0, 'eye_color': 0, 'wrong_ch': 0, 'missing_genes': 0}
        autosomes = [2, 3, 4]

        # check linkage distance (5 pts, max 5)
        distance = 0.0
        for i in range(4):
            try:
                distance = float(answer[i][-1])
                # print 'distance: ', distance
            except TypeError:
                pass
        if (k['linkage']['distance'] * 1.1) <= distance or distance <= (k['linkage']['distance'] * 0.9):
            # penalty += 5
            score_dict['link_distance'] = LINK_DISTANCE


        ans_genes = []
        # extract gene descriptions from user input
        for i in answer:  # cycle through each chromosome of the answer, attempt to extract their answers
            for j in [0, 1]:  # pull the two boxes that contain the genes per se
                try:
                    length = len(i[j])
                    if length in range(1, 4):
                        if length == 2:  # there should never be a 2 char input, proper nomenclature
                            # penalty += 0.5
                            score_dict['nomenclature'] += NOMENCLATURE
                        for l in i[j]:
                            if l.isalpha():
                                dom = True if l.isupper() else False
                                CH = answer.index(i) + 1
                                sid = len(final_answer)
                                ans_genes.append(l.lower())
                                final_answer[sid] = createGene(l, CH, dom)
                                # print fa[id]
                except:
                    pass
        final_answer['distance'] = distance
        k['final_answer'] = final_answer

        k_genes = []
        for i in range(1,5):
            a = k['genes'][i]['name'][0]
            k_genes.append(a)

        # pp.pprint(k)
        # print "their answers: ", ans_genes
        # print "karyo: ", k_genes

        wrong_ch_type = False
        for i in range(len(final_answer)-1):  # -1 here because we've added the distance key to the dict
            for j in range(1, 5):
                name = k['genes'][j]['name'][0]
                name = name.lower()
                # print final_answer[i]['name'], "</br>"
                if name == final_answer[i]['name'].lower():
                    # check for dom/rec properly assigned (1pt each)
                    if k['genes'][j]['dom'] != final_answer[i]['dom']:
                        # penalty += 1
                        score_dict['dom_rec'] += DOM_REC
                    # check for genes on the wrong chromosomes (3pts, max 6)
                    if k['genes'][j]['CH'] != final_answer[i]['CH']:
                        # temp_pen += 3
                        score_dict['wrong_ch'] += WRONG_CH
                    # check for autosomeal genes on autosomes, same for sex-linked
                    if (k['genes'][j]['CH'] in autosomes and final_answer[i]['CH'] not in autosomes) or (k['genes'][j]['CH'] not in autosomes and final_answer[i]['CH'] in autosomes):
                        wrong_ch_type = True

        if score_dict['wrong_ch'] > WRONG_CH_MAX:  # cap wrong chromosome penalty
            score_dict['wrong_ch'] = WRONG_CH_MAX
        if wrong_ch_type:
            score_dict['auto_on_auto'] = AUTO_ON_SEX

        # penalty += temp_pen

        # check for proper nomenclature (not using a, b, c, etc) (0.5pts each)
        for i in ans_genes:
            if i not in k_genes:
                score_dict['nomenclature'] += NOMENCLATURE
                # penalty += 0.5

        # check for resolution of eye color into two genes
        if k['genes']['double_color'][0] in ans_genes:
            score_dict['eye_color'] = EYE_COLOR
            # penalty += 6

        # check for linked genes on diff chromosomes or unlinked genes on same chromosome  ********
        g1k = k['linkage']['g1']
        g2k = k['linkage']['g2']
        linked_genes = [k['genes'][g1k]['name'][0], k['genes'][g2k]['name'][0]]
        ans_linked_genes = []
        # print "linked genes: ", linked_genes
        for i in range(len(final_answer)-1):   # -1 here becaue we haven't added the score or info keys yet
            if final_answer[i]['name'].lower() in linked_genes:
               ans_linked_genes.append(final_answer[i]['CH'])
        if len(ans_linked_genes) != 2 or ans_linked_genes[0] != ans_linked_genes[1]:
            # penalty += 6
            score_dict['linked_genes'] = LINKED_GENES

        # check for missing genes (4pts each)
        for i in k_genes:
            if i not in ans_genes:
                # penalty += 4
                score_dict['missing_genes'] += MISSING_GENE

        for i in score_dict:
            penalty += score_dict[i]

        # apply limit on penalty
        if (MAX_SCORE-penalty) < MIN_SCORE:
            penalty = MAX_SCORE - MIN_SCORE
        score = MAX_SCORE - penalty
        # print "penalty: ", penalty
        k['final_answer']['score'] = score
        info = ', '.join([student, lastname, firstname, section])
        k['final_answer']['info'] = info
        k['score_list'] = score_dict
        saveKaryo(k, file_name)

        print print_answer(k)
        print '</br>'
        print GRADE_LEGEND
    else:
        print "Error: invalid crosstype (" + crosstype + ")"

    print "</body></html>"


def stock_labels(k):
    mut = dict()
    mut[1] = 'F1'
    mut[2] = 'F1'
    mut[3] = 'Curly Dicheate ' + homo_rec(k)
    mut[4] = k['genes'][1]['name'] + ' ' + k['genes'][2]['name'] + ' ' + k['genes']['double_color']
    mut[5] = k['genes'][1]['name'] + ' ' + k['genes']['double_color']
    mut[6] = k['genes'][2]['name'] + ' ' + k['genes']['double_color']
    mut[7] = k['genes']['double_color']
    mut[8] = k['genes'][1]['name'] + ' ' + k['genes'][2]['name']
    mut[9] = 'wild type'

    return mut


def print_answer(karyo):
    k_list = [[], [], [], []]
    a_list = [[], [], [], []]
    for i in range(1,5):
        a = karyo['genes'][i]['CH'] - 1
        b = karyo['genes'][i]['name'][0].upper() if karyo['genes'][i]['dom'] else karyo['genes'][i]['name'][0].lower()
        k_list[a].append(b)

    for i in range(len(karyo['final_answer'])-3):
        try:
            a = karyo['final_answer'][i]['CH'] - 1
            a_list[a].append(karyo['final_answer'][i]['name'])
        except:
            print "ERROR: key not found, key=", i, "</br>"

    answer_table = karyo['final_answer']['info'] + "</br>"
    answer_table += "<table><tr><th>Chromosome</th><th>Karyotype</th><th>Your answer</th></tr>"
    answer_table += "<tr><td>1</td><td>" + ' '.join(k_list[0]) + "</td><td>" + ' '.join(a_list[0]) + "</td></tr>"
    answer_table += "<tr><td>2</td><td>" + ' '.join(k_list[1]) + "</td><td>" + ' '.join(a_list[1]) + "</td></tr>"
    answer_table += "<tr><td>3</td><td>" + ' '.join(k_list[2]) + "</td><td>" + ' '.join(a_list[2]) + "</td></tr>"
    answer_table += "<tr><td>4</td><td>" + ' '.join(k_list[3]) + "</td><td>" + ' '.join(a_list[3]) + "</td></tr>"
    answer_table += "<tr><td>Distance</td><td>" + str(karyo['linkage']['distance']) + "</td><td>" + str(karyo['final_answer']['distance']) + "</td></tr>"
    answer_table += "<tr><td>Score</td><td colspan=2>" + str(karyo['final_answer']['score']) + "/" + str(MAX_SCORE) + "</td></tr>"
    answer_table += "</table>"

    for i in karyo['score_list']:
        answer_table += str(i) + ": " + str(karyo['score_list'][i]) + "</br>"

    return answer_table


# returns the phenotype of homozygous recessive
def homo_rec(karyo):
    pheno = ''
    for i in [1, 2]:
        if karyo['genes'][i]['dom']:
            pass
        else:
            pheno += karyo['genes'][i]['name'] + ' '
    pheno += karyo['genes']['double_color']

    return pheno


# composes the data and html to display the results of the requested cross
def compose_table(cross, num_flies):
    table = ''
    table += '<table>'
    table += '<tr>'
    table += '<th id="headpheno">Phenotype</th>'
    table += '<th>Males</th>'
    table += '<th>Females</th>'
    table += '</tr>'
    num_progeny = 0
    for i in cross.keys():
        m_num = str(int(cross[i]['m'] * num_flies * random.uniform(0.9, 1.1)))
        f_num = str(int(cross[i]['f'] * num_flies * random.uniform(0.9, 1.1)))
        num_progeny += int(m_num) + int(f_num)
        table += '<tr>'
        table += '<td id="pheno">' + i + '</td>'
        table += '<td>' + m_num + '</td>'
        table += '<td>' + f_num + '</td>'
        table += '</tr>'
    table += '<tr><td id="pheno">Total</td><td id="total" colspan=2>' + str(num_progeny) + '</td></tr>'
    table += '</table>'
    # table += str(num_progeny)

    return table


# makes sure that the student ID is in a valid format
def format_id(student):
    try:
        temp = student[0:7]
        temp = temp.upper()
        return temp
    except:
        return 'AA00000'


# returns a dictionary with all phenotypes and their frequency, separated by sex
def crossStocks(karyo, male_stock, female_stock):
    # male and female are the stocks elements (s[0], s[4], s[9], etc)
    mgams = createGametes(karyo, male_stock, 'm')
    fgams = createGametes(karyo, female_stock, 'f')

    cross = dict()

    for f in fgams:
        for m in mgams:
            pheno = getPhenotype(m, f, karyo)
            if -1 in m:
                sex = 'm'
            else:
                sex = 'f'

            if cross.has_key(pheno):
                # print("yes")
                cross[pheno][sex] = cross[pheno][sex] + (m[-1] * f[-1])
            else:
                # print("no")
                cross[pheno] = {'m': 0.0, 'f': 0.0}
                cross[pheno][sex] = (m[-1] * f[-1])

    for i in cross.keys():
        for j in ['m', 'f']:
            cross[i][j] = round(cross[i][j], 7)
    return cross


# creates a list of gametes for the given sex with the probability of getting that gamete
def createGametes(karyo, stock, sex):
    # karyo = full karyotype, stock = an individual fly stock (stocks[1], stocks[5], etc)
    linked = [karyo['linkage']['g1'], karyo['linkage']['g2']]
    distance = karyo['linkage']['distance'] / 100.0
    unlinked = [1, 2, 3, 4]
    unlinked.remove(linked[0])
    unlinked.remove(linked[1])
    strands = ['rosalind', 'franklin']

    gametes = []
    ch_loc = False

    for i in [5, 6]:
        for j in ['m', 'f']:
            for k in strands:
                if stock[i][j][k] == 1:
                    ch_loc = True

    if sex == 'm' or ch_loc:   # create male gametes
        ch = [[], [], [], []]
        for i in range(1, 7):
            a = karyo['genes'][i]['CH'] - 1
            ch[a].append(i)

        # generates a set of all possible gametes, no duplicates
        for j in strands:
            for k in strands:
                for l in strands:
                    for m in strands:
                        for n in strands:
                            for o in strands:
                                c = [0, 0, 0, 0, 0, 0]
                                for i in range(len(ch)):
                                    for h in range(len(ch[i])):
                                        # print j,k,l,m,i,n
                                        a = ch[i][h]
                                        b = [j, k, l, m, n, o]
                                        c[a - 1] = stock[a][sex][b[i]]
                                # print c
                                gametes.append(c)
        gam_set = set()
        for i in gametes:
            gam_set.add(tuple(i))
        gams = []
        while len(gam_set) > 0:
            a = gam_set.pop()
            gams.append(list(a))

        probability = 1.0 / len(gams)

        for i in gams:
            i.append(probability)

        gametes = gams

    else:  # create female gametes
        # generate all possible combinations of female gametes
        g1 = linked[0] - 1
        g2 = linked[1] - 1

        for j in strands:
            for k in strands:
                for l in strands:
                    for m in strands:
                        for n in strands:
                            for o in strands:
                                cur_strands = [j, k, l, m, n, o]
                                if cur_strands[g1] == cur_strands[g2]:
                                    xo = False
                                else:
                                    xo = True
                                gametes.append([stock[1][sex][j], stock[2][sex][k], stock[3][sex][l], stock[4][sex][m], stock[5][sex][n], stock[6][sex][o], xo])

        for i in gametes:
            # g1 = i[linked[0]-1]
            # g2 = i[linked[1]-1]
            p_prob = 0.25 * ((1 - distance) / 2.0) / 4.0
            r_prob = 0.25 * (distance / 2.0) / 4.0
            # if i[4]:
            #     i.append(r_prob)
            # else:
            #     i.append(p_prob)
            if i[-1]:
                i[-1] = r_prob
            else:
                i[-1] = p_prob

    return gametes


def createKaryotype():
    # load the list of mutant names
    bristle_list = loadList("bristles.txt")
    color_list = loadList("color.txt")
    texture_list = loadList("texture.txt")
    twoColor_list = loadList("2color.txt")

    # print bristle_list
    # print color_list
    # print texture_list
    # print twoColor_list

    # randomly select mutations
    bristles = random.choice(bristle_list)
    texture = random.choice(texture_list)
    color1 = random.choice(color_list)
    color2 = random.choice(color_list)
    names = [bristles[0].upper()]  # create list of mutant initials and add the bristles initial to the list

    # pick texture such that first initial is different from bristles
    while texture[0].upper() in names:
        texture = random.choice(texture_list)

    # add texture initial to the list
    names.append(texture[0].upper())

    # pick color with unique first initial
    while color1[0].upper() in names:
        color1 = random.choice(color_list)

    # add initial to list
    names.append(color1[0].upper())
    color_list.remove(color1)  # this prevents the same color from being chosen twice

    # pick color with unique initial
    while color2[0].upper() in names:
        color2 = random.choice(color_list)
    names.append(color2[0].upper())

    # pick eye color double mutant
    twoColor = random.choice(twoColor_list)
    while twoColor[0].upper() in names:
        twoColor = random.choice(twoColor_list)

    # create karyotype
    karyo = dict()

    # bristles = 1, texture = 2, eye colors are 3 and 4, Curly = 5, Dicheate = 6
    # this chooses the sex-linked trait and which remaining genes are linked
    sex_linked = random.randint(1, 2)  # (0,2) includes possibility of NO sex-linked gene, (1,2) will always have a sex-linked gene
    link = [1, 2, 3, 4]  # possible linked genes
    try:
        link.remove(sex_linked)  # sex-linked trait isn't linked to anything else
    except:
        pass

    while len(link) > 2:
        c = random.choice(link)  # randomly pick among the remaining three
        link.remove(c)  # remove random choice, repeat until only two linked genes
    linked_ch = random.randint(2, 4)  # select which CH the linked genes are on
    unlinked_ch = [2, 3, 4]
    unlinked_ch.remove(linked_ch)

    # create students' unknown
    genes = dict()
    genes[1] = createGene(bristles, pickChromosome(sex_linked, link, linked_ch, unlinked_ch, 1), tof())
    genes[2] = createGene(texture, pickChromosome(sex_linked, link, linked_ch, unlinked_ch, 2), tof())
    genes[3] = createGene(color1, pickChromosome(sex_linked, link, linked_ch, unlinked_ch, 3), False)
    genes[4] = createGene(color2, pickChromosome(sex_linked, link, linked_ch, unlinked_ch, 4), False)
    genes[5] = createGene("Curly", 2, True)
    genes[6] = createGene('Dicheate', 3, True)
    karyo['genes'] = genes
    karyo['genes']['double_color'] = twoColor

    # define linkage parameters
    linkage = dict()
    linkage['g1'] = link[0]
    linkage['g2'] = link[1]
    dist = random.uniform(10,48)
    linkage['distance'] = round(dist, 1)
    karyo['linkage'] = linkage

    return karyo


def pickChromosome(sex_linked, link, linked_ch, unlinked_ch, gene_num):
    if gene_num == sex_linked:
        return 1
    elif gene_num in link:
        return linked_ch
    else:
        return random.choice(unlinked_ch)


# generates default, pure-breeding stocks for crosses, identified by a number code (1, 2, 3, etc)
def createStocks(karyotype):
    stocks = dict()  # force creation of empty dictionary

    for i in range(10):
        stocks[i] = {1: {'m': {'rosalind': 1, 'franklin': 1}, 'f': {'rosalind': 1, 'franklin': 1}}}

    # create blank stocks, by default all stocks are mutant, also initializes stock 4
    for i in range(10):
        for j in range(1, 7):
            stocks[i][j] = {'m': {'rosalind': 1, 'franklin': 1}, 'f': {'rosalind': 1, 'franklin': 1}}

    for i in range(10):
        for j in [5, 6]:
            stocks[i][j] = {'m': {'rosalind': 0, 'franklin': 0}, 'f': {'rosalind': 0, 'franklin': 0}}

    # stock 0, for making the Cy/D cross on the P0 data
    for i in range(1, 5):
        stocks[0][i]['m']['rosalind'] = 0
        stocks[0][i]['m']['franklin'] = 0
        stocks[0][i]['f']['rosalind'] = 0
        stocks[0][i]['f']['franklin'] = 0
    for i in [5, 6]:
        stocks[0][i]['m']['rosalind'] = 1
        stocks[0][i]['m']['franklin'] = 0
        stocks[0][i]['f']['rosalind'] = 1
        stocks[0][i]['f']['franklin'] = 0

    # stock 1, tetrahybrids
    for i in range(1, 5):
        stocks[1][i]['m']['rosalind'] = 1
        stocks[1][i]['m']['franklin'] = 0
        stocks[1][i]['f']['rosalind'] = 1
        stocks[1][i]['f']['franklin'] = 0

    # stock 2, reciprocal tetrahybrids
    for i in range(1, 5):
        stocks[2][i]['m']['rosalind'] = 0
        stocks[2][i]['m']['franklin'] = 1
        stocks[2][i]['f']['rosalind'] = 0
        stocks[2][i]['f']['franklin'] = 1

    # stock 3, chromosome localization
    for i in range(1, 7):
        stocks[3][i]['m']['rosalind'] = 1
        stocks[3][i]['m']['franklin'] = 0
        stocks[3][i]['f']['rosalind'] = 1
        stocks[3][i]['f']['franklin'] = 0

    # stock 5 (bristles, eye color)
    stocks[5][2]['m']['rosalind'] = 0
    stocks[5][2]['m']['franklin'] = 0
    stocks[5][2]['f']['rosalind'] = 0
    stocks[5][2]['f']['franklin'] = 0

    # stock 6 (texture, eye color)
    stocks[6][1]['m']['rosalind'] = 0
    stocks[6][1]['m']['franklin'] = 0
    stocks[6][1]['f']['rosalind'] = 0
    stocks[6][1]['f']['franklin'] = 0

    # stock 7 (eye color)
    for i in [1, 2]:
        stocks[7][i]['m']['rosalind'] = 0
        stocks[7][i]['m']['franklin'] = 0
        stocks[7][i]['f']['rosalind'] = 0
        stocks[7][i]['f']['franklin'] = 0

    # stock 8 (bristles, texture)
    for i in [3, 4]:
        stocks[8][i]['m']['rosalind'] = 0
        stocks[8][i]['m']['franklin'] = 0
        stocks[8][i]['f']['rosalind'] = 0
        stocks[8][i]['f']['franklin'] = 0

    # stock 9 (wild type)
    for i in range(1, 5):
        stocks[9][i]['m']['rosalind'] = 0
        stocks[9][i]['m']['franklin'] = 0
        stocks[9][i]['f']['rosalind'] = 0
        stocks[9][i]['f']['franklin'] = 0

    # set male chromosomes, "y" chromosome always on the franklin strand
    for i in range(10):
        for j in range(1, 5):
            if karyotype['genes'][j]['CH'] == 1:
                stocks[i][j]['m']['franklin'] = -1

    return stocks


# returns the mutant name or an empty string(WT) for a given gene
def getAllele(gene, mAll, fAll):
    if mAll == -1:
        if fAll:
            return gene['name']
        else:
            return ''

    if gene['dom']:
        if mAll == 1 or fAll == 1:
            return gene['name']
        else:
            return ''
    else:
        if mAll == 1 and fAll == 1:
            return gene['name']
        else:
            return ''


# returns the mutant phenotypes of a given fly. "wild type" if not mutant
def getPhenotype(mgam, fgam, karyo):
    # curly, dicheate, bristles, eye texture, eye color
    pheno = getAllele(karyo['genes'][5], mgam[4], fgam[4]) + " "
    pheno += getAllele(karyo['genes'][6], mgam[5], fgam[5]) + " "
    pheno += getAllele(karyo['genes'][1], mgam[0], fgam[0]) + " "
    pheno += getAllele(karyo['genes'][2], mgam[1], fgam[1]) + " "
    eye1 = getAllele(karyo['genes'][3], mgam[2], fgam[2])
    eye2 = getAllele(karyo['genes'][4], mgam[3], fgam[3])

    if eye1 != '':
        if eye2 != '':
            pheno += karyo['genes']['double_color']
        else:
            pheno += eye1
    else:
        if eye2 != '':
            pheno += eye2
        else:
            pheno += ''

    pheno = pheno.strip()
    pheno = pheno.replace('   ', ' ')
    pheno = pheno.replace('  ', ' ')

    if pheno == '':
        pheno = "wild type"

    return pheno


# creates the basic gene structure and fills in the relevant parameters
def createGene(name, CH, dom):
    gene = {"name": name, "CH": CH, "dom": dom}
    return gene


# randomly decides between true and false
def tof():
    if random.randint(0, 100) % 2:
        return True
    else:
        return False


def loadList(file, upper=False):
    with open(file, "r") as f:
        raw = f.read()

    if upper:
        raw = raw.upper()
    else:
        raw = raw[3:]
        raw = raw.lower()
    data = raw.split('\n')
    return data


def printKaryo(karyo):
    for i in range(1, len(karyo['genes'])):
        print karyo['genes'][i]['name'], karyo['genes'][i]['CH'], karyo['genes'][i]['dom']
    print karyo['genes']['double_color']
    print karyo['linkage']


def saveKaryo(karyo, id):
    with open(id, 'w') as save:
        temp = json.dumps(obj=karyo, indent=4)
        save.write(temp)


def loadKaryo(student):
    with open(student, 'r') as kfile:
        temp = kfile.read()

    karyo = json.loads(temp)
    karyo['genes'][1] = karyo['genes']['1']
    karyo['genes'][2] = karyo['genes']['2']
    karyo['genes'][3] = karyo['genes']['3']
    karyo['genes'][4] = karyo['genes']['4']
    karyo['genes'][5] = karyo['genes']['5']
    karyo['genes'][6] = karyo['genes']['6']
    del karyo['genes']['1']
    del karyo['genes']['2']
    del karyo['genes']['3']
    del karyo['genes']['4']
    del karyo['genes']['5']
    del karyo['genes']['6']

    if karyo.has_key('final_answer'):
        for i in range(len(karyo['final_answer']) - 3):
            karyo['final_answer'][i] = karyo['final_answer'][str(i)]
            del karyo['final_answer'][str(i)]

    return karyo


def init_test():
    karyotype = createKaryotype()
    stocks = createStocks(karyotype)

    return karyotype, stocks


def printList(l):
    for i in l:
        print l

# test_main()
main()
