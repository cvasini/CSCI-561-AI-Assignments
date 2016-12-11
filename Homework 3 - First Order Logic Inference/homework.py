import os.path
import collections
import itertools
import copy

f = open("input.txt")
lines = f.readlines()
noOfQueries = int(lines[0].rstrip('\n'))
queries = []
for i in range(1, noOfQueries + 1):
    queries.append(lines[i].rstrip('\n'))
noOfKB = int(lines[noOfQueries + 1])
kb = []
kb1 = []
kbWithoutParantheses = []
cleanKb = []
counter = 0

# create output file
if os.path.isfile("output.txt"):
    wf = open("output.txt", 'w')
    wf.truncate()
else:
    wf = open("output.txt", 'w')

for j in range(noOfQueries + 2, noOfQueries + noOfKB + 2):
    kbVal = (lines[j].rstrip('\n')).replace(" ", "")
    if list(kbVal)[0] != '(' and list(kbVal)[0] != '~':
        cleanKb.append(kbVal)
    elif kbVal.count('(') == 2 and kbVal.count('~') == 1:
        kbVal = kbVal[1:len(kbVal) - 1]
        cleanKb.append(kbVal)
    else:
        kb.append(kbVal)

#Return the index at which an unmatched '(' occurs
def findUnmatchedOpen(sentence):
    length = len(sentence)
    opens = []
    closes = []
    for i in range(length - 1, -1, -1):
        if sentence[i] == '(':
            opens.append(i)
        if sentence[i] == ')':
            closes.append(i)
        if len(opens) > len(closes):
            return opens[len(opens) - 1]

#Return the index at which an unmatched ')' occurs
def findUnmatchedClose(sentence):
    length = len(sentence)
    opens = []
    closes = []
    for i in range(length):
        if sentence[i] == '(':
            opens.append(i)
        if sentence[i] == ')':
            closes.append(i)
        if len(closes) > len(opens):
            return closes[len(closes) - 1]

#Adds a Negation to a clause surrounded by '(' and ')'
def addNegation(sN, fH):
    return fH[:sN] + '(~' + fH[sN:] + ')'

#Rule a => b is also (~a) | b
def replaceImpliesWithOr(startOfNegation, firstHalf, secondHalf):
    modifiedFH = addNegation(startOfNegation, firstHalf)
    s = modifiedFH + "|" + secondHalf
    return s

#Rule a => b is also (~a) | b
def replaceImplies(sentence):
    countOfImplies = sentence.count('=>')
    for i in range(countOfImplies):
        index = sentence.find('=>')
        unmatchedOpenIndex = findUnmatchedOpen(sentence[:index])
        sentence = replaceImpliesWithOr(unmatchedOpenIndex + 1, sentence[:index], sentence[index + 2:])
    return sentence


def negatePredicates(predicate1, operator, predicate2):
    #if predicate already contains negation, then remove negation else add negation
    if predicate1[0] + predicate1[1] == '(~':
        predicate1 = predicate1[2:len(predicate1) - 1]
    else:
        predicate1 = '(~' + predicate1 + ')'
    if predicate2[0] + predicate2[1] == '(~':
        predicate2 = predicate2[2:len(predicate2) - 1]
    else:
        predicate2 = '(~' + predicate2 + ')'
    sentence = predicate1 + operator + predicate2
    return sentence

#This moves ~ in to the parantheses
def moveNot(sentence):
    #if sentence only contains one '(' and ')' and no negation, simply add '~' and return
    if sentence[0] != '~' and sentence.count('(') == 1 and sentence.count(')') == 1 and sentence.count(
            '&') == 0 and sentence.count('|') == 0:
        return '~' + sentence
    #if sentence only contains one '(' and ')' and one negation, simply remove '~' and return
    elif sentence[0] == '~' and sentence.count('(') == 1 and sentence.count(')') == 1 and sentence.count(
            '&') == 0 and sentence.count('|') == 0:
        return sentence[1:]
    # if sentence only contains one '&' or '!' and one negation, find predicates around the oprators and negate them. Also flip '&' to '|' and '|' to '&'
    elif sentence.count('&') > 0 or sentence.count('|') > 0:
        indexOfOperator = -1
        outermostAnd = findOuterMostAnd('(' + sentence + ')')
        outermostOr = findOuterMostOr('(' + sentence + ')')
        listSen = list(sentence)
        if outermostAnd != -1:
            indexOfOperator = outermostAnd - 1
            listSen[outermostAnd - 1] = '|'
        elif outermostOr != -1:
            indexOfOperator = outermostOr - 1
            listSen[outermostOr - 1] = '&'
        sentence = "".join(listSen)
        sentence = negatePredicates(sentence[:indexOfOperator], sentence[indexOfOperator],
                                    sentence[indexOfOperator + 1:])
        return sentence

#This returns the position of '~' and where the predicate belonginf to not ends
def findAllPossiblePairsOfNot(sentence, pattern):
    pairs = collections.OrderedDict()
    for i in range(len(sentence)):
        if i + 1 != len(sentence) and sentence[i] + sentence[i + 1] == pattern:
            pairs[i] = i + 2 + findUnmatchedClose(sentence[i + 2:])
    return pairs

#This returns the innermost pair of not from all possible pairs of nots
def pickInnermostPair(pairs, length):
    innermostPairStart = 0
    innerMostPairEnd = length
    for eachKey, eachVal in pairs.items():
        if eachKey > innermostPairStart and eachVal < innerMostPairEnd:
            innermostPairStart = eachKey
            innerMostPairEnd = eachVal
    return [innermostPairStart, innerMostPairEnd]

#This function moves the negation in through the sentence
def moveNegationIn(sentence):
    while sentence.count('~(') != 0:
        pairs = findAllPossiblePairsOfNot(sentence, '~(')
        innermostPair = []
        if len(pairs.keys()) == 1:
            innermostPair = [pairs.keys()[0], pairs[pairs.keys()[0]]]
        else:
            innermostPair = pickInnermostPair(pairs, len(sentence))
        thirdPart = ""
        if innermostPair[1] + 1 != len(sentence):
            thirdPart = sentence[innermostPair[1] + 1:]
        sentence = sentence[:innermostPair[0]] + moveNot(sentence[innermostPair[0] + 2:innermostPair[1]]) + thirdPart
        moveNegationIn(sentence)
    return sentence

#This function removes parantheses if the sentence only had one '(', ')' and no '~'
def removeSinglePredicateParantheses(sentence):
    index = -1
    while index < len(sentence):
        indexOfOpen = sentence.find('(', index)
        if indexOfOpen != -1 and capitalVars.find(sentence[indexOfOpen + 1]) != -1:
            indeOfUnmatchedClose = findUnmatchedClose(sentence[indexOfOpen + 1:])
            sentenceAfterOpen = sentence[indexOfOpen + 1:indexOfOpen + indeOfUnmatchedClose + 1]
            if sentenceAfterOpen.count('(') == 1 and sentenceAfterOpen.count(')'):
                listSen = list(sentence)
                newSentence = ""
                for i, val in enumerate(listSen):
                    if i != indexOfOpen and i != indexOfOpen + 1 + indeOfUnmatchedClose:
                        newSentence += val
                sentence = newSentence
                index = 0
            else:
                index += 1
        else:
            index = index + 1
    return sentence

#This function removes parantheses if the sentence only had one '(', ')' and one '~'
def removeSingleNotPredicateParantheses(sentence):
    index = 0
    while index < len(sentence):
        pairs = findAllPossiblePairsOfNot(sentence, '(~')
        if len(pairs) != 0:
            for pair in pairs.items():
                eachKey = pair[0]
                eachVal = pair[1]
                sen = sentence[eachKey + 1:eachVal]
                if sen.count('(') == 1 and sen.count(')') == 1 and sen.count('&') == 0 and sen.count('|') == 0:
                    sentence = sentence[:eachKey] + sen + sentence[eachVal + 1:]
                    break
                else:
                    index += 1
        else:
            break
    return sentence


def findChar(sentence, ch):
    return [i for i, ltr in enumerate(sentence) if ltr == ch]

#returns indexes of '&' in sentence
def findIndexOfAnds(sentence):
    indexOfAnds = findChar(sentence, '&')
    return indexOfAnds

#finds the two predicates around an '&'
def findPredicatesAroundAndType(sentence, index):
    predicate1 = sentence[:index]
    predicate2 = sentence[index + 1:]
    unmatchedOpen = findUnmatchedOpen(predicate1)
    predicate1 = predicate1[unmatchedOpen + 1:]
    unmatchedClose = findUnmatchedClose(predicate2)
    predicate2 = predicate2[:unmatchedClose]
    return [predicate1, predicate2]

#finds the outermost '&' in a sentence
def findOuterMostAnd(sentence):
    list = []
    outermostIndex = -1
    for i in range(len(sentence)):
        if sentence[i] == '&' and len(list) == 1 and list[len(list) - 1] == '(':
            outermostIndex = i
            break
        elif sentence[i] == ')' and len(list) != 0:
            list.pop()
        elif sentence[i] == '(':
            list.append(sentence[i])
    return outermostIndex

#finds the outermost '|' in a sentence
def findOuterMostOr(sentence):
    list = []
    outermostIndex = -1
    for i in range(len(sentence)):
        if sentence[i] == '|' and len(list) == 1 and list[len(list) - 1] == '(':
            outermostIndex = i
            break
        elif sentence[i] == ')' and len(list) != 0:
            list.pop()
        elif sentence[i] == '(':
            list.append(sentence[i])
    return outermostIndex


# Distributes '&' over '|' of the formats: i.) a | (b & c) = (a | b) & (a | c)  ii.) (a & b) | c = (a | c) & (b | c)
def distributeOrOverAnd(sentence):
    type1 = distributeOrOverAndType1(sentence)
    type2 = distributeOrOverAndType2(type1)
    if type1 == type2:
        final = type1
    else:
        final = distributeOrOverAnd(type2)
    return final

#a | (b & c) = (a | b) & (a | c)
def distributeOrOverAndType1(sentence):
    index = 0
    while index < len(sentence):
        if sentence[index] == '|':
            leftSide = sentence[:index]
            rightSide = sentence[index + 1:]
            unmatchedOpen = findUnmatchedOpen(sentence[:index])
            front = sentence[:unmatchedOpen + 1]
            orPredicate = sentence[unmatchedOpen + 1:index]
            unmatchedClose = findUnmatchedClose(rightSide)
            indexOfAnds = findIndexOfAnds(rightSide[:unmatchedClose])
            rear = rightSide[unmatchedClose:]
            if len(indexOfAnds) != 0:
                rightAndOperands = rightSide[:unmatchedClose]
                indexOfAnd = findOuterMostAnd(rightAndOperands)
                if indexOfAnd != -1:
                    andPredicates = findPredicatesAroundAndType(rightAndOperands, indexOfAnd)
                    distributedPredicates = '(' + orPredicate + '|' + andPredicates[0] + ')&(' + orPredicate + '|' + \
                                            andPredicates[1] + ')'
                    sentence = front + distributedPredicates + rear
                    index = 0
                else:
                    index += 1
            else:
                index += 1
        else:
            index += 1
    return sentence

#(a & b) | c = (a | c) & (b | c)
def distributeOrOverAndType2(sentence):
    index = 0
    while index < len(sentence):
        if sentence[index] == '|':
            leftSide = sentence[:index]
            rightSide = sentence[index + 1:]
            unmatchedClose = findUnmatchedClose(sentence[index + 1:])
            orPredicate = rightSide[:unmatchedClose]
            rear = rightSide[unmatchedClose:]
            unmatchedOpen = findUnmatchedOpen(leftSide)
            front = sentence[:unmatchedOpen + 1]
            indexOfAnds = findIndexOfAnds(leftSide[unmatchedOpen + 1:])
            if len(indexOfAnds) != 0:
                leftAndOperands = leftSide[unmatchedOpen + 1:]
                indexOfAnd = findOuterMostAnd(leftAndOperands)
                if indexOfAnd != -1:
                    andPredicates = findPredicatesAroundAndType(leftAndOperands, indexOfAnd)
                    distributedPredicates = '(' + andPredicates[0] + '|' + orPredicate + ')&(' + andPredicates[
                        1] + '|' + orPredicate + ')'
                    sentence = front + distributedPredicates + rear
                    index = 0
                else:
                    index += 1
            else:
                index += 1
        else:
            index += 1
    return sentence

#Splits the sentence at all '&' => (a | b) & c is split into a | b and c
def splitSentenceAtAnds(sentence):
    index = findOuterMostAnd(sentence)
    if index == -1:
        kb1.append(sentence)
    else:
        left = sentence[:index]
        left1 = left[findUnmatchedOpen(left) + 1:]
        right = sentence[index + 1:]
        right1 = right[:findUnmatchedClose(right)]
        splitSentenceAtAnds(left1)
        splitSentenceAtAnds(right1)

#removes parantheses around '|' because of associativity i.e. ((a|b)|c) is just a|b|c
def dropParantheses(sentence):
    i = 0
    value = ""
    while i < len(sentence):
        if sentence[i] == '|':
            left = sentence[:i]
            right = sentence[i:]
            indexOfUnmatchedOpen = findUnmatchedOpen(left)
            indexOfUmatchedClose = findUnmatchedClose(right) + len(left)
            value = ""
            for j, val in enumerate(sentence):
                if j != indexOfUnmatchedOpen and j != indexOfUmatchedClose:
                    value = value + val
            sentence = value
        i += 1
    if value == "":
        kbWithoutParantheses.append(sentence)
    else:
        kbWithoutParantheses.append(value)

#creates combinations of variables for standardization
varArray = list("abcdefghijklmnopqrstuvwxyz")
varArray2 = []
varArray3 = []
for eachComb in itertools.permutations(varArray, 2):
    varArray2.append(eachComb[0] + eachComb[1])
for eachComb in itertools.permutations(varArray, 3):
    varArray3.append(eachComb[0] + eachComb[1] + eachComb[2])
varArray = varArray + varArray2 + varArray3
capitalVars = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"

#finds all unique variables in a sentence
def findAllVarsInSentence(sentence):
    vars = set()
    varPositions = collections.OrderedDict()
    for i in range(len(sentence)):
        if (sentence[i - 1] == '(' or sentence[i - 1] == ',') and capitalVars.find(sentence[i]) == -1:
            vars.add(sentence[i])
            varPositions[i] = sentence[i]
    return [vars, varPositions]

#Standardize variables in a sentence
def standardiseVars(vars):
    global counter
    correspondingVars = collections.OrderedDict()
    for eachVar in vars:
        correspondingVars[eachVar] = varArray[counter]
        counter = counter + 1
    return correspondingVars

#finds the predicates in a sentence and creates a map of where the predicates occur in the kb according to line numbers
def findPredicates(sentence):
    predicateMap = collections.OrderedDict()
    i = 0
    start = 0
    while i != -1:
        i = sentence.find('(')
        if i != -1:
            predicate = sentence[start:i]
            sentence = sentence[i:]
            closeIndex = sentence.find(')')
            vars = sentence[1:closeIndex].split(",")
            if predicate not in predicateMap.keys():
                predicateMap[predicate] = [vars]
            else:
                v = predicateMap[predicate]
                v.append(vars)
                predicateMap[predicate] = v
            i = sentence.find('|')
            if i != -1:
                i += 1
                sentence = sentence[i:len(sentence)]
    return predicateMap

#loops through all sentences in input file and converts them to CNF for use in resolution inference theorem
for sentence in kb:
    sentence = replaceImplies(sentence)
    sentence = moveNegationIn(sentence)
    sentence = removeSingleNotPredicateParantheses(sentence)
    sentence = removeSinglePredicateParantheses(sentence)
    sentence = distributeOrOverAnd(sentence)
    splitSentenceAtAnds(sentence)

for sentence in kb1:
    dropParantheses(sentence)

cleanKb = kbWithoutParantheses + cleanKb
standardisedKb = []

for sentence in cleanKb:
    varsInSentence = findAllVarsInSentence(sentence)
    vars = varsInSentence[0]
    correspondingVar = standardiseVars(vars)
    varPositions = varsInSentence[1]
    listSen = list(sentence)
    for eachPosition, eachVar in varPositions.items():
        listSen[eachPosition] = correspondingVar[eachVar]
    standardisedKb.append("".join(listSen))
kbMap = []
allPredicates = collections.defaultdict(list)
for index, eachSentence in enumerate(standardisedKb):
    sentenceMap = collections.OrderedDict()
    sentenceMap = findPredicates(eachSentence)
    for i in sentenceMap.keys():
        allPredicates[i].append(index)
    kbMap.append(sentenceMap)

#Checks if a value is a constant
def isConstant(str):
    if capitalVars.find(str[0]) != -1:
        return True
    else:
        return False

#finds a replacement for variable with another variable or constant
def replaceParam(paramArray, x, y):
    for index, eachVal in enumerate(paramArray):
        if eachVal == x:
            paramArray[index] = y
    return paramArray

#Unification
def unifyParams(params1, params2):
    newParams = collections.OrderedDict()
    for i in range(len(params1)):
        if params1[i] != params2[i] and isConstant(params1[i]) and isConstant(params2[i]):
            return []
        elif params1[i] == params2[i] and isConstant(params1[i]) and isConstant(params2[i]):
            if params1[i] not in newParams.keys():
                newParams[params1[i]] = params2[i]
        elif isConstant(params1[i]) and not isConstant(params2[i]):
            if params2[i] not in newParams.keys():
                newParams[params2[i]] = params1[i]
                params2 = replaceParam(params2, params2[i], params1[i])
        elif not isConstant(params1[i]) and isConstant(params2[i]):
            if params1[i] not in newParams.keys():
                newParams[params1[i]] = params2[i]
                params1 = replaceParam(params1, params1[i], params2[i])
        elif not isConstant(params1[i]) and not isConstant(params2[i]):
            if params1[i] not in newParams.keys():
                newParams[params1[i]] = params2[i]
                params1 = replaceParam(params1, params1[i], params2[i])
    return newParams

#Checks if the sentence contradicts with any other sentence in kb
def checkForContradiction(newSentence, stdKb):
    if newSentence.count("(") == 1 and newSentence.count(")") == 1:
        negatedSentence = negateQuery(newSentence)
        for sen in stdKb:
            if sen == negatedSentence:
                newSentenceMap = collections.OrderedDict()
                newSentenceMap = findPredicates(newSentence)
                oldSentenceMap = collections.OrderedDict()
                oldSentenceMap = findPredicates(sen)
                answer1 = True
                answer2 = True
                for k, v in newSentenceMap.items():
                    for val in v:
                        for val1 in val:
                            if not isConstant(val1):
                                answer1 = False
                                break
                for k, v in oldSentenceMap.items():
                    for val in v:
                        for val1 in val:
                            if not isConstant(val1):
                                answer2 = False
                                break
                return answer1 | answer2
        return False
    else:
        return False

#negates a query to be added ot the kb and then perform resolution
def negateQuery(query):
    if query[0] == '~':
        query = query[1:]
    else:
        query = '~' + query
    return query

#checks if all params in a predicate are constants
def checkIfAllParamsAreConstants(params):
    areConstants = True
    for k, v in params.items():
        if not isConstant(v):
            areConstants = False
            break
    return areConstants

#for all queries perform resolution inference
for q in queries:
    allPredicates1 = copy.deepcopy(allPredicates)
    result = False
    flagForBreak = 0
    standardisedKb1 = copy.deepcopy(standardisedKb)
    kbMap1 = copy.deepcopy(kbMap)
    q = q.replace(" ", "")
    q1 = negateQuery(q)
    standardisedKb1.append((q1))
    senMap = collections.OrderedDict()
    senMap = findPredicates(q1)
    kbMap1.append(senMap)
    for iMap1 in senMap.keys():
        allPredicates1[iMap1].append(len(kbMap1) - 1)
    i = 0
    while i < len(kbMap1) and i < 4000:
        j = 0
        if flagForBreak == 1:
            break
        sentenceMap1 = kbMap1[i]
        for predicate1, parameters1 in sentenceMap1.items():
            if flagForBreak == 1:
                break
            for p1Index, p1 in enumerate(parameters1):
                if flagForBreak == 1:
                    break
                ll = len(allPredicates1[negateQuery(predicate1)])
                while j < ll and ll < 100:
                    if flagForBreak == 1:
                        break
                    sentenceMap2 = kbMap1[allPredicates1[negateQuery(predicate1)][j]]

                    for predicate2, parameters2 in sentenceMap2.items():
                        if flagForBreak == 1:
                            break
                        for p2Index, p2 in enumerate(parameters2):
                            if predicate1 == negateQuery(predicate2) and cmp(sentenceMap1, sentenceMap2) != 0:
                                newParams = unifyParams(copy.deepcopy(p1), copy.deepcopy(p2))
                                if len(newParams) != 0:
                                    newSentence = ""
                                    for k, v in sentenceMap1.items():
                                        for kIndex, value in enumerate(v):
                                            if k == predicate1 and p1Index == kIndex:
                                                continue
                                            else:
                                                newSentence += k + ' ( ' + " , ".join(value) + ' ) |'
                                    for k1, v1 in sentenceMap2.items():
                                        for k1Index, value1 in enumerate(v1):
                                            if k1 == predicate2 and p2Index == k1Index:
                                                continue
                                            else:
                                                newSentence += k1 + ' ( ' + " , ".join(value1) + ' ) |'
                                    newSentence = newSentence[:len(newSentence) - 1]
                                    listSentence = newSentence.split()
                                    for k2, v2 in newParams.items():
                                        for indexOfVal, val in enumerate(listSentence):
                                            if val == k2:
                                                listSentence[indexOfVal] = v2
                                    newSentence = "".join(listSentence)
                                    if newSentence == "" and checkIfAllParamsAreConstants(newParams):
                                        result = True
                                    else:
                                        result = checkForContradiction(newSentence, standardisedKb1)
                                    if result:
                                        flagForBreak = 1
                                        break
                                    else:
                                        if newSentence != "":
                                            noMatch = True
                                            newSentenceMap = collections.OrderedDict()
                                            newSentenceMap = findPredicates(newSentence)
                                            for eachMap in kbMap1:
                                                if cmp(eachMap, newSentenceMap) == 0:
                                                    noMatch = False
                                                    break
                                            if noMatch:
                                                standardisedKb1.append(newSentence)
                                                kbMap1.append(newSentenceMap)
                                                for iMap in newSentenceMap.keys():
                                                    allPredicates1[iMap].append(len(kbMap1) - 1)
                    j = j + 1
        i = i + 1
    if result:
        output = 'TRUE'
    else:
        output = 'FALSE'
    wf.write(output)
    wf.write('\n')
wf.close()
