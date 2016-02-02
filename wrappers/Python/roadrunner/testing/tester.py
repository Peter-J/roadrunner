# Test Module for RoadRunner
#
# Usage:
# import rrTester
# runTester (pathtoModelFile, modelFileName)


#-------------------------------------------------------------
# Tests for steady state and stoichiometric calculations in
# roadRunner. Herbert M Sauro November 2012
# Nov 2013: Modified to test Andy's SWIG API
#-------------------------------------------------------------

#------------------------------------------
# Change this line for different test files
#nameOfResultsFile = 'results_roadRunnerTest_1.txt'

from __future__ import print_function

import random
import string
import roadrunner
from roadrunner import Config
from roadrunner import Logger
import re
import numpy
from numpy import *


# Module wide file handle
fHandle = ''
rpadding = 45
#gFailedTests = 0
#gPassedTests = 0

# --------------------------------------------------------------------------
# SUPPORT ROUTINES
# --------------------------------------------------------------------------

def expectApproximately (a, b, tol):
    diff = a - b
    return abs(diff) < tol

def passMsg (errorFlag, msg = ""):
    global gFailedTests
    global gPassedTests
    if msg:
        msg = "\n    " + msg
    if not errorFlag:
        gPassedTests = gPassedTests+1
        return "PASS"
    gFailedTests = gFailedTests+1    
    return "*****FAIL*****" + msg

# Empty lines are ignored
# Lines starting with # are also ignored

def readLine ():
    line = fHandle.readline()

    while (line == '') or (line[0] == '#') or (line[0] == '\n'):
        if line == '':
            return line
        line = fHandle.readline();
    return line.strip('\n')

def divide(line):
    words = line.strip()
    words = words.strip('"')
    words = re.compile("[ \t=]").split(words)
    while "" in words: words.remove("")
    return words

def jumpToNextTest():
    line = readLine()
    #line = ''
    #while line == '':
    #      line = fHandle.readline().strip ('\n')
    while (line != "") and (line[0] != '['):
        line = readLine()
    # remove any leading or trailing whitespace
    return line.strip()

def getSBMLStr ():
    sbmlStr = ''
    line = fHandle.readline()
    while (line[0] != '['):
        sbmlStr = sbmlStr + line
        line = fHandle.readline()
    return sbmlStr, line.strip()

# ------------------------------------------------------------------------
# TESTS START HERE
# ------------------------------------------------------------------------

def checkMatrixVsUpcomingText(calc):
    errorFlag = False
    msg = ""
    rows = len(calc)
    if (not(isinstance(calc[0], numpy.ndarray))):
        compareUpcomingValuesWith(calc, 1e-4)
        return
    for i in range(0,rows):
        line = readLine ()
        words = line.split()
        cols = len(calc[0])
        if(len(words) != cols):
            msg = "Expected a row of length " + str(len(words)) + ", but calculated a row of length " + str(cols)
            errorFlag = True
            break
        for j in range(0,cols):
            expectedValue = float(words[j])
            calcValue = calc[i,j]
            if expectApproximately (expectedValue, calcValue, abs(1e-7+calcValue)*1E-4) == False:
                msg = "Expected " + words[j] + ", but calculated " + str(calcValue)
                errorFlag = True
                break
    print(passMsg (errorFlag, msg))
    

def checkComplexVecVsUpcomingText(calc):
    errorFlag = False
    msg = ""
    rows = len(calc)
    for i in range(0,rows):
        line = readLine ()
        words = line.split()
        if(len(words) != 2):
            msg = "Faulty test:  needed a row of length two for complex number, but found " + str(len(words))
            errorFlag = True
            break
            expectedValue =  complex(float(words[0], float(words[1])))
            if expectApproximately (expectedValue, calc[i], abs(calc+1e-7)*1E-4) == False:
                msg = "Expected " + words[j] + ", but calculated " + str(calc[i,j])
                errorFlag = True
                break
    print(passMsg (errorFlag, msg))
    

def compareUpcomingValuesWith(ss, error):
    errorFlag = False
    msg = ""
    words = divide(readLine())
    if (len(words)) == 1:
        for i in range(len(ss)):
            if expectApproximately(float (words[0]), ss[i], abs(ss[i]+1e-5)*error) == False:
                msg = "Expected " + words[0] + ", but calculated " + str(ss[i])
                errorFlag = True
                break;
            if i < len(ss) - 1:
                words = divide(readLine())
    else:
        for i in range (len (ss)):
            if expectApproximately(float (words[i]), ss[i], abs(ss[i]+1e-5)*error) == False:
                msg = "Expected " + words[i] + ", but calculated " + str(ss[i])
                errorFlag = True
                break;
    print(passMsg (errorFlag, msg))

def setConservationLaw(rrInstance, testId):
    line = readLine ()
    if line == 'True':
        rrInstance.conservedMoietyAnalysis = True
    else:
        rrInstance.conservedMoietyAnalysis = False

def checkSpeciesConcentrations(rrInstance, testId):
    words = []
    species = []
    m = rrInstance.model.getNumFloatingSpecies()
    for i in range (0,m):
        words = divide(readLine())
        words.append (rrInstance.model[words[0]])
        species.append (words)

    # Steady State Concentrations
    print(string.ljust ("Check " + testId, rpadding), end="")
    errorFlag = False
    for i in range (0,m):
        expectedValue =  float (species[i][1])
        if expectApproximately (expectedValue, species[i][2], abs(species[i][2]*1E-4)) == False:
            errorFlag = True
            break
    print(passMsg (errorFlag))


def checkSteadyStateFluxes(rrInstance, testId):
    words = []
    fluxes = []
    # Steady State Fluxes
    print("Computing Steady State.  Distance to SteadyState:", rrInstance.steadyState())
    print(string.ljust ("Check " + testId, rpadding), end="")
    errorFlag = False
    n = rrInstance.model.getNumReactions();
    for i in range (0,n):
        line = readLine ()
        words = line.split("=")
        words.append (rrInstance.model[words[0]])
        fluxes.append (words)

    for i in range (0,n):
        expectedValue = float (fluxes[i][1])
        if expectApproximately (expectedValue, fluxes[i][2], abs((expectedValue+(1e-3))*1E-5)) == False:
            errorFlag = True
            break
    print(passMsg (errorFlag))

def checkFullJacobian(rrInstance, testId):
    # Jacobian
    print(string.ljust ("Check " + testId, rpadding), end="")
    roadrunner.Config.setValue(Config.ROADRUNNER_JACOBIAN_MODE, Config.ROADRUNNER_JACOBIAN_MODE_CONCENTRATIONS)
    Jacobian = rrInstance.getFullJacobian()
    checkMatrixVsUpcomingText(Jacobian)


def checkReducedJacobian(rrInstance, testId):
    # Jacobian
    print(string.ljust ("Check " + testId, rpadding), end="")
    roadrunner.Config.setValue(Config.ROADRUNNER_JACOBIAN_MODE, Config.ROADRUNNER_JACOBIAN_MODE_CONCENTRATIONS)
    Jacobian = rrInstance.getReducedJacobian()
    checkMatrixVsUpcomingText(Jacobian)


def checkAmountJacobian(rrInstance, testId):
    # Jacobian
    print(string.ljust ("Check " + testId, rpadding), end="")
    roadrunner.Config.setValue(Config.ROADRUNNER_JACOBIAN_MODE, Config.ROADRUNNER_JACOBIAN_MODE_AMOUNTS)
    Jacobian = rrInstance.getFullJacobian()
    checkMatrixVsUpcomingText(Jacobian)


def checkIndividualEigenvalues(rrInstance, testId):
    # Eigenvalues
    print(string.ljust ("Check " + testId, rpadding), end="")
    errorFlag = False
    roadrunner.Config.setValue(Config.ROADRUNNER_JACOBIAN_MODE, Config.ROADRUNNER_JACOBIAN_MODE_CONCENTRATIONS)
    m = len(rrInstance.getEigenValueIds())
    try:
        for i in range(0,m):
            words = divide(readLine())
            eigenvalueName = words[0]
            calc = rrInstance.getValue ('eigenReal(' + eigenvalueName + ')')
            calc = complex(calc, rrInstance.getValue('eigenImag(' + eigenvalueName + ')'))
            expected = complex(float(words[1]), float(words[2]))

            if expectApproximately (calc, expected, abs(calc+1e-7)*1E-4) == False:
                errorFlag = True
                break
        print(passMsg (errorFlag))
    except Exception, e:
        print('Unexpected error in checkIndividualEigenvalues:' + str(e))


def checkIndividualAmountEigenvalues(rrInstance, testId):
    # Eigenvalues
    print(string.ljust ("Check " + testId, rpadding), end="")
    errorFlag = False
    roadrunner.Config.setValue(Config.ROADRUNNER_JACOBIAN_MODE, Config.ROADRUNNER_JACOBIAN_MODE_AMOUNTS)
    m = len(rrInstance.getEigenValueIds())
    try:
        for i in range(0,m):
            words = divide(readLine())
            eigenvalueName = words[0]
            realPart = rrInstance.getValue ('eigenReal(' + eigenvalueName + ')')
            realPart = float (realPart)

            if expectApproximately (realPart, float(words[1]), 1E-5) == False:
                errorFlag = True
                break
        print(passMsg (errorFlag))
    except Exception, e:
        print('Unexpected error in checkIndividualEigenvalues:' + str(e))


def checkEigenvalueMatrix(rrInstance, testId):
    # Eigenvalues
    print(string.ljust ("Check " + testId, rpadding), end="")
    roadrunner.Config.setValue(Config.ROADRUNNER_JACOBIAN_MODE, Config.ROADRUNNER_JACOBIAN_MODE_CONCENTRATIONS)
    eigenvalues = rrInstance.getFullEigenValues()
    checkComplexVecVsUpcomingText(eigenvalues)


def checkReducedEigenvalueMatrix(rrInstance, testId):
    # Eigenvalues
    print(string.ljust ("Check " + testId, rpadding), end="")
    roadrunner.Config.setValue(Config.ROADRUNNER_JACOBIAN_MODE, Config.ROADRUNNER_JACOBIAN_MODE_CONCENTRATIONS)
    eigenvalues = rrInstance.getReducedEigenValues()
    checkComplexVecVsUpcomingText(eigenvalues)


def checkEigenvalueAmountMatrix(rrInstance, testId):
    # Eigenvalues
    print(string.ljust ("Check " + testId, rpadding), end="")
    roadrunner.Config.setValue(Config.ROADRUNNER_JACOBIAN_MODE, Config.ROADRUNNER_JACOBIAN_MODE_AMOUNTS)
    eigenvalues = rrInstance.getFullEigenValues()
    checkComplexVecVsUpcomingText(eigenvalues)

def checkStoichiometryMatrix(rrInstance, testId):
    # Stoichiometry matrix
    print(string.ljust ("Check " + testId, rpadding), end="")
    st = rrInstance.getFullStoichiometryMatrix()
    checkMatrixVsUpcomingText(st)

def checkReducedStoichiometryMatrix(rrInstance, testId):
    # Stoichiometry matrix
    print(string.ljust ("Check " + testId, rpadding), end="")
    st = rrInstance.getReducedStoichiometryMatrix()
    checkMatrixVsUpcomingText(st)

def checkLinkMatrix(rrInstance, testId):
    # Link matrix
    print(string.ljust ("Check " + testId, rpadding), end="")
    st = rrInstance.getLinkMatrix()
    checkMatrixVsUpcomingText(st)

def checkUnscaledConcentrationControlMatrix(rrInstance, testId):
    # Unscaled Concentration Control matrix
    Config.setValue(Config.ROADRUNNER_JACOBIAN_MODE, Config.ROADRUNNER_JACOBIAN_MODE_CONCENTRATIONS)
    print(string.ljust ("Check " + testId, rpadding), end="")
    st = rrInstance.getUnscaledConcentrationControlCoefficientMatrix();
    checkMatrixVsUpcomingText(st)


def checkScaledConcentrationControlMatrix(rrInstance, testId):
    # Unscaled Concentration Control matrix
    Config.setValue(Config.ROADRUNNER_JACOBIAN_MODE, Config.ROADRUNNER_JACOBIAN_MODE_CONCENTRATIONS)
    print(string.ljust ("Check " + testId, rpadding), end="")
    st = rrInstance.getScaledConcentrationControlCoefficientMatrix();
    checkMatrixVsUpcomingText(st)


def checkUnscaledFluxControlCoefficientMatrix(rrInstance, testId):
    # Unscaled Flux Control matrix
    print(string.ljust ("Check " + testId, rpadding), end="")
    st = rrInstance.getUnscaledFluxControlCoefficientMatrix();
    checkMatrixVsUpcomingText(st)


def checkScaledFluxControlCoefficientMatrix(rrInstance, testId):
    # Unscaled Flux Control matrix
    print(string.ljust ("Check " + testId, rpadding), end="")
    st = rrInstance.getScaledFluxControlCoefficientMatrix()
    checkMatrixVsUpcomingText(st)


def checkUnscaledElasticityMatrix(rrInstance, testId):
    print(string.ljust ("Check " + testId, rpadding), end="")
    roadrunner.Config.setValue(Config.ROADRUNNER_JACOBIAN_MODE, Config.ROADRUNNER_JACOBIAN_MODE_CONCENTRATIONS)
    uee = rrInstance.getUnscaledElasticityMatrix()
    checkMatrixVsUpcomingText(uee)

def checkUnscaledElasticityAmountMatrix(rrInstance, testId):
    print(string.ljust ("Check " + testId, rpadding), end="")
    roadrunner.Config.setValue(Config.ROADRUNNER_JACOBIAN_MODE, Config.ROADRUNNER_JACOBIAN_MODE_AMOUNTS)
    uee = rrInstance.getUnscaledElasticityMatrix()
    checkMatrixVsUpcomingText(uee)

def checkScaledElasticityMatrix(rrInstance, testId):
    print(string.ljust ("Check " + testId, rpadding), end="")
    roadrunner.Config.setValue(Config.ROADRUNNER_JACOBIAN_MODE, Config.ROADRUNNER_JACOBIAN_MODE_CONCENTRATIONS)
    ee = rrInstance.getScaledElasticityMatrix()
    checkMatrixVsUpcomingText(ee)


def checkScaledElasticityAmountMatrix(rrInstance, testId):
    print(string.ljust ("Check " + testId, rpadding), end="")
    roadrunner.Config.setValue(Config.ROADRUNNER_JACOBIAN_MODE, Config.ROADRUNNER_JACOBIAN_MODE_AMOUNTS)
    ee = rrInstance.getScaledElasticityMatrix()
    checkMatrixVsUpcomingText(ee)


def checkGetFloatingSpeciesIds(rrInstance, testId):
    print(string.ljust ("Check " + testId, rpadding), end="")
    errorFlag = False
    line = readLine ()
    words = line.split()
    expected = rrInstance.model.getFloatingSpeciesIds()
    m = rrInstance.model.getNumFloatingSpecies()
    for i in range(0,m):
        if words[i] != expected[i]:
            errorFlag = True
            break
    print(passMsg (errorFlag))

def checkGetBoundarySpeciesIds(rrInstance, testId):
    print(string.ljust ("Check " + testId, rpadding), end="")
    errorFlag = False
    line = readLine ()
    words = line.split()
    expected = rrInstance.model.getBoundarySpeciesIds()
    m = rrInstance.model.getNumBoundarySpecies()
    for i in range(0,m):
        if words[i] != expected[i]:
            errorFlag = True
            break
    print(passMsg (errorFlag))


def checkGetGlobalParameterIds (rrInstance, testId):
    print(string.ljust ("Check " + testId, rpadding), end="")
    errorFlag = False
    line = readLine ()
    words = line.split()
    expected = rrInstance.model.getGlobalParameterIds()
    m = rrInstance.model.getNumGlobalParameters()
    for i in range(0,m):
        if words[i] != expected[i]:
            errorFlag = True
            break
    print(passMsg (errorFlag))


def checkGetCompartmentIds (rrInstance, testId):
    print(string.ljust ("Check " + testId, rpadding), end="")
    errorFlag = False
    line = readLine ()
    words = line.split()
    expected = rrInstance.model.getCompartmentIds()
    m = rrInstance.model.getNumCompartments()
    for i in range(0,m):
        if words[i] != expected[i]:
            errorFlag = True
            break
    print(passMsg (errorFlag))


def checkReactionIds (rrInstance, testId):
    print(string.ljust ("Check " + testId, rpadding), end="")
    errorFlag = False
    words = divide(readLine())
    expected = rrInstance.model.getReactionIds()
    m = rrInstance.model.getNumReactions();
    for i in range(0,m):
        if words[i] != expected[i]:
            errorFlag = True
            break
    print(passMsg (errorFlag))


def checkFloatingSpeciesInitialConcentrationIds (rrInstance, testId):
    print(string.ljust ("Check " + testId, rpadding), end="")

    words = divide(readLine())

    expected = rrInstance.model.getFloatingSpeciesInitConcentrationIds()


    print(passMsg (words != expected))


def checkEigenValueIds (rrInstance, testId):
    print(string.ljust ("Check " + testId, rpadding), end="")
    errorFlag = False
    words = divide(readLine())
    expected = rrInstance.getEigenValueIds()
    m = rrInstance.model.getNumFloatingSpecies()
    for i in range(0,m):
        if words[i] != expected[i]:
            errorFlag = True
            break
    print(passMsg (errorFlag))


def checkSetSteadyStateSelectionList(rrInstance, testId):
    print(string.ljust ("Check " + testId, rpadding), end="")
    errorFlag = False
    words = divide(readLine())
    rrInstance.conservedMoietyAnalysis = True
    rrInstance.steadyStateSelections = words
    print(passMsg (errorFlag))
    time = rrInstance.steadyState()
    if (time>0.00001):
        time = rrInstance.steadyState()
    print("Computing Steady State.  Distance to SteadyState:", time)


def checkGetSteadyStateSelectionList(rrInstance, testId):
    print(string.ljust ("Check " + testId, rpadding), end="")
    words = divide(readLine())
    result = str(rrInstance.steadyStateSelections)

    print(passMsg (result == words))


def checkSetTimeCourseSelectionList(rrInstance, testId):
    print(string.ljust ("Check " + testId, rpadding), end="")
    errorFlag = False
    words = divide(readLine())
    result = rrInstance.selections = words
    if result == False:
        errorFlag = True
    print(passMsg (errorFlag))


def checkGetTimeCourseSelectionList(rrInstance, testId):
    print(string.ljust ("Check " + testId, rpadding), end="")
    words = divide(readLine())
    result = str(rrInstance.selections)

    print(passMsg (result == words))

def checkComputeSteadyStateValues(rrInstance, testId):
    print(string.ljust ("Check " + testId, rpadding), end="")
    ss = rrInstance.getSteadyStateValues()
    compareUpcomingValuesWith(ss, 1E-6)


def checkFloatingSpeciesConcentrations(rrInstance, testId):
    print(string.ljust ("Check " + testId, rpadding), end="")
    ss = rrInstance.model.getFloatingSpeciesConcentrations()
    compareUpcomingValuesWith(ss, 1E-6)


def checkBoundarySpeciesConcentrations(rrInstance, testId):
    print(string.ljust ("Check " + testId, rpadding), end="")
    ss = rrInstance.model.getBoundarySpeciesConcentrations()
    compareUpcomingValuesWith(ss, 1E-6)


def checkGlobalParameterValues(rrInstance, testId):
    print(string.ljust ("Check " + testId, rpadding), end="")
    ss = rrInstance.model.getGlobalParameterValues()
    compareUpcomingValuesWith(ss, 1E-6)


def checkInitalFloatingSpeciesConcentations(rrInstance, testId):
    print(string.ljust ("Check " + testId, rpadding), end="")
    ss = rrInstance.model.getFloatingSpeciesInitConcentrations()

    words = readLine().split()

    same = len(words) == len(ss) and \
        len(words) == sum([1 for i,j in zip(words,ss) if expectApproximately(float (i), j, 1E-6)])

    print(passMsg (not same))


def checkReactionRates(rrInstance, testId):
    print(string.ljust ("Check " + testId, rpadding), end="")
    ss = rrInstance.model.getReactionRates()
    compareUpcomingValuesWith(ss, 1E-4)


def checkGetReactionRatesByIndex(rrInstance, testId):
    print(string.ljust ("Check " + testId, rpadding), end="")
    errorFlag = False
    words = readLine().split()
    n = rrInstance.model.getNumReactions()
    for i in range (n):
        value = rrInstance.model.getReactionRates()[i]
        if expectApproximately(float (words[i]), value, 1E-6) == False:
            errorFlag = True
            break;
    print(passMsg (errorFlag))

def checkGetSpeciesInitialConcentrationsByIndex(rrInstance, testId):
    print(string.ljust ("Check " + testId, rpadding), end="")
    errorFlag = False
    words = divide(readLine())
    n = rrInstance.model.getNumFloatingSpecies()
    values = rrInstance.model.getFloatingSpeciesInitConcentrations()
    for i in range (n):
        if expectApproximately(float (words[i]), values[i], 1E-6) == False:
            errorFlag = True
            break;
    print(passMsg (errorFlag))


def checkSetSpeciesInitialConcentrationsByIndex(rrInstance, testId):
    print(string.ljust ("Check " + testId, rpadding), end="")
    errorFlag = False
    words = divide(readLine())
    n = rrInstance.model.getNumFloatingSpecies()
    rrInstance.model.setFloatingSpeciesInitConcentrations(array(map(float, words)))
    rt = rrInstance.model.getFloatingSpeciesInitConcentrations()
    for i in range (n):
        if expectApproximately(float (words[i]), rt[i], 1E-6) == False:
            errorFlag = True
            break
    print(passMsg (errorFlag))


def checkSetSpeciesInitialConcentrations(rrInstance, testId):
    print(string.ljust ("Check " + testId, rpadding), end="")
    errorFlag = False
    n = rrInstance.model.getNumFloatingSpecies()
    for i in range (0,n):
        words = divide(readLine())
        if rrInstance.setValue(words[0], float(words[1])) == False:
            errorFlag = True
            break
        if expectApproximately(rrInstance.getValue(words[0]), float (words[1]), 1E-6) == False:
            errorFlag = True
            break
    print(passMsg (errorFlag))


def checkNumberOfDependentSpecies(rrInstance, testId):
    print(string.ljust ("Check " + testId, rpadding), end="")
    errorFlag = False
    value = int (readLine())
    n = rrInstance.model.getNumDepFloatingSpecies()
    if n != value:
        errorFlag = True
    print(passMsg (errorFlag))


def checkNumberOfIndependentSpecies(rrInstance, testId):
    print(string.ljust ("Check " + testId, rpadding), end="")
    errorFlag = False
    value = int (readLine())
    n = rrInstance.model.getNumIndFloatingSpecies()
    if n != value:
        errorFlag = True
    print(passMsg (errorFlag))


def checkNumberOfRateRules(rrInstance, testId):
    print(string.ljust ("Check " + testId, rpadding), end="")
    errorFlag = False
    value = int (readLine())
    if rrInstance.model.getNumRateRules() != value:
        errorFlag = True
    print(passMsg (errorFlag))


def checkGetRatesOfChange(rrInstance, testId):
    print(string.ljust ("Check " + testId, rpadding), end="")
    errorFlag = False
    words = divide(readLine())
    values = rrInstance.model.getFloatingSpeciesAmountRates()
    for i in range (len(words)):
        if expectApproximately (float (words[i]), values[i], abs(values[i]+1e-7)*1E-5) == False:
            errorFlag = True
    print(passMsg (errorFlag))


def checkGetReactionRatesEx (rrInstance, testId):
    print(string.ljust ("Check " + testId, rpadding), end="")
    errorFlag = False
    inputConcs = asarray (divide(readLine()).remove("indexes"), dtype=float64)
    values = rrInstance.getReactionRatesEx (inputConcs)
    outputRates = asarray (divide(readLine()).remove("rates"), dtype=float64)
    if not allclose (values, outputRates):
        errorFlag = True
    print(passMsg (errorFlag))


def checkGetRatesOfChangeEx (rrInstance, testId):
    print(string.ljust ("Check " + testId, rpadding), end="")
    errorFlag = False
    inputConcs = asarray (divide(readLine()).remove("indexes"), dtype=float64)
    values = rrInstance.model.getRatesOfChangeEx (inputConcs)
    outputRates = asarray (divide(readLine()).remove("rates"), dtype=float64)
    if not allclose (values, outputRates):
        errorFlag = True
    print(passMsg (errorFlag))


def checkGetRateOfChangeByIndex(rrInstance, testId):
    print(string.ljust ("Check " + testId, rpadding), end="")
    errorFlag = False
    n = rrInstance.getNumRatesOfChange()
    words = readLine().split()
    for i in range (n):
        value = rrInstance.model.getRatesOfChange()[i]
        if expectApproximately(float (words[i]), value, 1E-6) == False:
            errorFlag = True
            break;
    print(passMsg (errorFlag))

# ---------------------------------------------------------------------------

def setGetValues(rrInstance, IdList, testId):
    print(string.ljust ("Check " + testId, rpadding), end="")
    errorFlag = False
    for i in range (len(IdList)):
        value = random.random()*10
        rrInstance.model[dList[i]] = value
        if expectApproximately (rrInstance.model[IdList[i]], value, 1E-6) == False:
            errorFlag = True
            break
    print(passMsg (errorFlag))


def setGetTimeStart(rrInstance, testId):
    print(string.ljust ("Check " + testId, rpadding), end="")
    errorFlag = False
    value = random.random ()*10
    rrInstance.setTimeStart (value)
    if expectApproximately (rrInstance.getTimeStart (), value, 1E-6) == False:
        errorFlag = True
    print(passMsg (errorFlag))


def setGetTimeEnd(rrInstance, testId):
    print(string.ljust ("Check " + testId, rpadding), end="")
    errorFlag = False
    value = random.random ()*10
    rrInstance.setTimeEnd (value)
    if expectApproximately (rrInstance.getTimeEnd (), value, 1E-6) == False:
        errorFlag = True
    print(passMsg (errorFlag))


def setGetNumberOfPoints(rrInstance, testId):
    print(string.ljust ("Check " + testId, rpadding), end="")
    errorFlag = False
    value = random.randint (1, 100)
    rrInstance.setNumPoints (value)
    if rrInstance.getNumPoints () != value:
        errorFlag = True
    print(passMsg (errorFlag))


def setGetTimeCourseSelectionList(rrInstance, testId):
    print(string.ljust ("Check " + testId, rpadding), end="")
    errorFlag = False
    myList = rrInstance.getFloatingSpeciesIds()
    newList = list (myList)
    random.shuffle (newList)
    rrInstance.setTimeCourseSelectionList (newList)
    if rrInstance.getTimeCourseSelectionList() != newList:
        errorFlag = True
    print(passMsg (errorFlag))


def setGetSteadyStateSelectionList(rrInstance, testId):
    print(string.ljust ("Check " + testId, rpadding), end="")
    errorFlag = False
    myList = rrInstance.getFloatingSpeciesIds()
    newList = list (myList)
    while newList == myList:
        random.shuffle (newList)
    rrInstance.setSteadyStateSelectionList (newList)
    getList = rrInstance.getSteadyStateSelectionList()
    if getList != newList:
        errorFlag = True
    print(passMsg (errorFlag))


def setGetFloatingSpeciesByIndex(rrInstance, testId):
    print(string.ljust ("Check " + testId, rpadding), end="")
    errorFlag = False
    n = rrInstance.getNumFloatingSpecies()
    for i in range (n):
        value = random.random()*10
        rrInstance.setFloatingSpeciesByIndex (i, value)
        if expectApproximately(rrInstance.getFloatingSpeciesByIndex (i), value, 1E-6) == False:
            errorFlag = True
            break;
    print(passMsg (errorFlag))


def setGetBoundarySpeciesByIndex(rrInstance, testId):
    print(string.ljust ("Check " + testId, rpadding), end="")
    errorFlag = False
    n = rrInstance.getNumBoundarySpecies()
    for i in range (n):
        value = random.random()*10
        rrInstance.setBoundarySpeciesByIndex (i, value)
        if expectApproximately(rrInstance.getBoundarySpeciesByIndex (i), value, 1E-6) == False:
            errorFlag = True
            break;
    print(passMsg (errorFlag))


def setGetCompartmentByIndex(rrInstance, testId):
    print(string.ljust ("Check " + testId, rpadding), end="")
    errorFlag = False
    n = rrInstance.getNumCompartments()
    for i in range (n):
        value = random.random()*10
        rrInstance.setCompartmentByIndex (i, value)
        if expectApproximately(rrInstance.getCompartmentByIndex (i), value, 1E-6) == False:
            errorFlag = True
            break;
    print(passMsg (errorFlag))


def setGetGlobalParameterByIndex (rrInstance, testId):
    print(string.ljust ("Check " + testId, rpadding), end="")
    errorFlag = False
    n = rrInstance.getNumberOfGlobalParameters()
    for i in range (n):
        value = random.random()*10
        rrInstance.setGlobalParameterByIndex (i, value)
        if expectApproximately(rrInstance.getGlobalParameterByIndex (i), value, 1E-6) == False:
            errorFlag = True
            break;
    print(passMsg (errorFlag))


def setGetFloatingSpeciesConcentrations (rrInstance, testId):
    print(string.ljust ("Check " + testId, rpadding), end="")
    errorFlag = False
    getArray = rrInstance.getFloatingSpeciesConcentrations()
    setArray = zeros(len(getArray))
    for i in range(len(getArray)):
        value = random.random()*10
        setArray[i] = value
    rrInstance.setFloatingSpeciesConcentrations (setArray)
    if (setArray != rrInstance.getFloatingSpeciesConcentrations()).all():
        errorFlag = True
    print(passMsg (errorFlag))


def setGetBoundarySpeciesConcentrations (rrInstance, testId):
    print(string.ljust ("Check " + testId, rpadding), end="")
    errorFlag = False
    getArray = rrInstance.getBoundarySpeciesConcentrations()
    setArray = zeros(len(getArray))
    for i in range(len(getArray)):
        value = random.random()*10
        setArray[i] = value
    rrInstance.setBoundarySpeciesConcentrations (rrInstance.PythonArrayTorrVector (setArray))
    if (setArray != rrInstance.getBoundarySpeciesConcentrations()).all():
        errorFlag = True
    print(passMsg (errorFlag))


def setGetInitialFloatingSpeciesConcentrations (rrInstance, testId):
    print(string.ljust ("Check " + testId, rpadding), end="")
    errorFlag = False
    getArray = rrInstance.getFloatingSpeciesInitialConcentrations ()
    setArray = zeros(len(getArray))
    for i in range(len(getArray)):
        value = random.random()*10
        setArray[i] = value
    rrInstance.setFloatingSpeciesInitialConcentrations (setArray)
    if (setArray != rrInstance.getFloatingSpeciesInitialConcentrations()).all():
        errorFlag = True
    print(passMsg (errorFlag))


def setGetReset(rrInstance, testId):
    print(string.ljust ("Check " + testId, rpadding), end="")
    errorFlag = False
    values = zeros (rrInstance.getNumberOfFloatingSpecies())
    for i in range (len (values)):
        values[i] = random.random()*10
    initial = rrInstance.getFloatingSpeciesInitialConcentrations()
    rrInstance.setFloatingSpeciesConcentrations (values)
    # Should reset the floats by to the current initial condition
    rrInstance.reset()
    values = rrInstance.getFloatingSpeciesConcentrations()
    if(values != initial).all():
        errorFlag = True
    print(passMsg (errorFlag))


def checkJacobian(rrInstance, testId):
    # TODO need to update python 2.x printing
    print(string.ljust ("Check " + testId, rpadding), end="")
    import numpy as n

    errors = False

    # max difference between reduced and full
    maxDiff = 2e-10

    # save the old value
    saved = Config.getValue(Config.ROADRUNNER_JACOBIAN_MODE)

    # set to amounts mode
    Config.setValue(Config.ROADRUNNER_JACOBIAN_MODE, Config.ROADRUNNER_JACOBIAN_MODE_AMOUNTS)
    full = rrInstance.getFullJacobian()
    reduced = rrInstance.getReducedJacobian()

    m = n.max(n.abs(reduced-full))
    if (m > maxDiff):
        errors = True
        print("Jacobians different in amounts mode, max difference: " + str(m))

    # set to conc mode
    Config.setValue(Config.ROADRUNNER_JACOBIAN_MODE, Config.ROADRUNNER_JACOBIAN_MODE_CONCENTRATIONS)

    full = rrInstance.getFullJacobian()
    reduced = rrInstance.getReducedJacobian()

    m = n.max(n.abs(reduced-full))
    if (m > maxDiff):
        errors = True
        print("Jacobians different in concentrations mode, max difference: " + str(m))

    # restore previous value
    Config.setValue(Config.ROADRUNNER_JACOBIAN_MODE, saved)

    print(passMsg(errors))
	
def checkControlCoefficient(rrInstance, testId):
    print(string.ljust ("Check " + testId, rpadding), end="")
    errorFlag = False
    words = divide(readLine())
    n = rrInstance.getCC(words[0], words[1])
    if abs(n - float(words[2])) > 1e-6:
        errorFlag = True
    print(passMsg (errorFlag))

def checkVariableEndTime(rrInstance, testId):
    print(string.ljust ("Check " + testId, rpadding), end="")
    errorFlag = True
    words = divide(readLine())

    try:
        # passing variableStep to simulate should throw
        n1 = rrInstance.simulate(float(words[0]), float(words[1]), variableStep=True)
    except:
        errorFlag = False

    rrInstance.getIntegrator().resetSettings()
    rrInstance.getIntegrator().setValue('variable_step_size', True)
    n2 = rrInstance.simulate(float(words[0]), float(words[1]))

    if expectApproximately(n2[-1][0], float(words[1]), 1e-16) == False:
        errorFlag = True

    print(passMsg (errorFlag))

def checkDefaultTimeStep(rrInstance, testId):
    print(string.ljust ("Check " + testId, rpadding), end="")
    errorFlag = False
    words = divide(readLine())
    n = rrInstance.simulate()
    if n.shape[0] != int(words[0]):
        errorFlag = True
    print(passMsg (errorFlag))

def checkSimulateTimepointsVsIntervals(rrInstance, testId):
    '''
    Third positional argument is number of points.
    Steps keyword argument is number of intervals.
    '''
    print(string.ljust ("Check " + testId, rpadding), end="")
    errorFlag = False
    try:
        n1 = rrInstance.simulate(0, 10, steps=1)
        if n1.shape[0] != 2:
            errorFlag = True
        n2 = rrInstance.simulate(0, 10, 2)
        if n2.shape[0] != 2:
            errorFlag = True
    except:
        errorFlag = True
    print(passMsg (errorFlag))

def checkMonotonicTimepoints(rrInstance, testId):
    '''
    Timepoint values should only increase.
    No two timepoints should ever have the same time value.
    '''
    print(string.ljust ("Check " + testId, rpadding), end="")
    errorFlag = False
    try:
        words = divide(readLine())
        startTime = float(words[0])
        endTime = float(words[1])
        npoints = int(words[2])

        # For variable step
        rrInstance.getIntegrator().setValue('variable_step_size', True)
        n = rrInstance.simulate(startTime, endTime)
        for k in range(1,n.shape[0]):
            if n[k-1,0] >= n[k,0]:
                print('Monotonicity failure var step: {} >= {}'.format(n[k-1,0], n[k,0]))
                errorFlag = True

        # For fixed step
        rrInstance.reset()
        rrInstance.getIntegrator().setValue('variable_step_size', False)
        n = rrInstance.simulate(startTime, endTime, npoints)
        for k in range(1,n.shape[0]):
            if n[k-1,0] >= n[k,0]:
                print('Monotonicity failure fixed step: {} >= {}'.format(n[k-1,0], n[k,0]))
                errorFlag = True
    except(e):
        print('Caught exception: {}'.format(e))
        errorFlag = True
    print(passMsg (errorFlag))

def checkEventPreandPostfireTimepoints(rrInstance, testId):
    '''
    Timepoint values should only increase.
    No two timepoints should ever have the same time value.
    '''
    print(string.ljust ("Check " + testId, rpadding), end="")
    errorFlag = False
    try:
        words = divide(readLine())

        def find_close_timepoint(simdata, t, tol):
            '''
            Finds the index of the closest timepoint in the
            simulation results which is within tol of t
            '''
            for k in range(simdata.shape[0]):
                if abs(simdata[k,0] - t) <= tol:
                    return k
            return -1;

        rrInstance.getIntegrator().setValue('variable_step_size', True)
        simresult = rrInstance.simulate(0, 10)

        max_tol = 0.0001

        # iterate through each expected event timepoint
        for w in words:
            t = float(w)
            # expect two timepoints close by
            i = find_close_timepoint(simresult, t, max_tol)
            if i < 0 or i+1 >= simresult.shape[0]:
                errorFlag = True
            else:
                if abs(simresult[i+1,0] - simresult[i,0]) > max_tol:
                    errorFlag = True
    except(e):
        print('Caught exception: {}'.format(e))
        errorFlag = True
    print(passMsg (errorFlag))





def scriptTests():
    print("\nTesting Set and Get Functions")
    print("-----------------------------")
    setGetValues(rrInstance.getFloatingSpeciesIds(), 'Set/Get Value (Floats)')
    setGetValues(rrInstance.getBoundarySpeciesIds(), 'Set/Get Value (Boundary)')
    setGetValues(rrInstance.getGlobalParameterIds(), 'Set/Get Value (Global Parameters)')
    setGetValues(rrInstance.getCompartmentIds(), 'Set/Get Value (Compartments)')
    setGetTimeStart('Set/Get TimeStart')
    setGetTimeEnd ('Set/Get TimeEnd')
    setGetNumberOfPoints ('Set/Get Number Of Points')
    setGetTimeCourseSelectionList ('Set/Get Time Course Selection List')
    setGetSteadyStateSelectionList ('Set/Get Steady State Selection List')
    setGetFloatingSpeciesByIndex ('Set/Get Floating Species by Index')
    setGetBoundarySpeciesByIndex ('Set/Get Boundary Species by Index')
    setGetCompartmentByIndex ('Set/Get Compartment by Index')
    setGetGlobalParameterByIndex ('Set/Get Global Parameter buy Index')
    setGetBoundarySpeciesConcentrations ('Set/Get Boundary Species Concs')
    setGetFloatingSpeciesConcentrations ('Set/Get Floating Species Concs')
    setGetInitialFloatingSpeciesConcentrations ('Set/Get Initial Concs')
    setGetReset ('Set/Get Reset Method')


# ------------------------------------------------------------------------
# List of tests
functions = {'[Amount/Concentration Jacobians]' : checkJacobian,
             '[Amount Jacobian]' : checkAmountJacobian,
             '[Boundary Species Concentrations]': checkBoundarySpeciesConcentrations,
             '[Boundary Species Ids]': checkGetBoundarySpeciesIds,
             '[Check Default Time Step]': checkDefaultTimeStep,
             '[Check Monotonic Timepoints]': checkMonotonicTimepoints,
             '[Check Event Pre and Postfire Timepoints]': checkEventPreandPostfireTimepoints,
             '[Check Simulate Points vs Steps]': checkSimulateTimepointsVsIntervals,
             '[Compartment Ids]': checkGetCompartmentIds,
             '[Compute Steady State Values]': checkComputeSteadyStateValues,
             '[Conservation Laws]': setConservationLaw,
             '[Eigenvalue Matrix]': checkEigenvalueMatrix,
             '[Eigenvalue Amount Matrix]': checkEigenvalueAmountMatrix,
             '[Floating Species Concentrations]': checkFloatingSpeciesConcentrations,
             '[Floating Species Ids]': checkGetFloatingSpeciesIds,
             '[Full Jacobian]': checkFullJacobian,
             '[Get Control Coefficient]': checkControlCoefficient,
             '[Get Eigenvalue Ids]': checkEigenValueIds,
             '[Get Variable End Time]': checkVariableEndTime,
             '[Get Global Parameter Values]': checkGlobalParameterValues,
             '[Get Initial Floating Species Concs]': checkInitalFloatingSpeciesConcentations,
#             '[Get Rate of Change by Index]': checkGetRateOfChangeByIndex,
             '[Get Rates Of Change]': checkGetRatesOfChange,
#             '[Get Rates of Change Ex]': checkGetRatesOfChangeEx,
             '[Get Reaction Rates By Index]': checkGetReactionRatesByIndex,
#             '[Get Reaction Rates Ex]': checkGetReactionRatesEx,
             '[Get Reaction Rates]': checkReactionRates,
             '[Get Species Initial Concentrations By Index]': checkGetSpeciesInitialConcentrationsByIndex,
             '[Get Steady State Selection List]': checkGetSteadyStateSelectionList,
             '[Get Steady State Selection List 2]': checkGetSteadyStateSelectionList,
             '[Get Time Course Selection List]': checkGetTimeCourseSelectionList,
             '[Global Parameter Ids]': checkGetGlobalParameterIds,
             '[Individual Eigenvalues]': checkIndividualEigenvalues,
             '[Individual Amount Eigenvalues]': checkIndividualAmountEigenvalues,
             '[Link Matrix]': checkLinkMatrix,
             '[Number of Dependent Species]': checkNumberOfDependentSpecies,
             '[Number of Independent Species]': checkNumberOfIndependentSpecies,
             '[Number Of Rate Rules]': checkNumberOfRateRules,
             '[Reaction Ids]': checkReactionIds,
             '[Reduced Eigenvalue Matrix]': checkReducedEigenvalueMatrix,
             '[Reduced Jacobian]': checkReducedJacobian,
             '[Reduced Stoichiometry Matrix]': checkReducedStoichiometryMatrix,
             '[Scaled Concentration Control Matrix]': checkScaledConcentrationControlMatrix,
             '[Scaled Elasticity Matrix]': checkScaledElasticityMatrix,
             '[Scaled Elasticity Amount Matrix]': checkScaledElasticityAmountMatrix,
             '[Scaled Flux Control Matrix]': checkScaledFluxControlCoefficientMatrix,
             '[Set Species Initial Concentrations By Index]': checkSetSpeciesInitialConcentrationsByIndex,
             '[Set Species Initial Concentrations]': checkSetSpeciesInitialConcentrations,
             '[Set Steady State Selection List]': checkSetSteadyStateSelectionList,
             '[Set Steady State Selection List 2]': checkSetSteadyStateSelectionList,
             '[Set Time Course Selection List]': checkSetTimeCourseSelectionList,
             '[Species Concentrations]': checkSpeciesConcentrations,
             '[Species Initial Concentration Ids]': checkFloatingSpeciesInitialConcentrationIds,
             '[Steady State Fluxes]': checkSteadyStateFluxes,
             '[Stoichiometry Matrix]': checkStoichiometryMatrix,
             '[Unscaled Concentration Control Matrix]': checkUnscaledConcentrationControlMatrix,
             '[Unscaled Elasticity Matrix]': checkUnscaledElasticityMatrix,
             '[Unscaled Elasticity Amount Matrix]': checkUnscaledElasticityAmountMatrix,
             '[Unscaled Flux Control Matrix]': checkUnscaledFluxControlCoefficientMatrix,
              }


def getDefaultTestDir():
    import os.path as p
    d = p.dirname(__file__)
    return p.join(d,"test_data")


def runTester (testDir=None):
    """
    Run a series of tests from a testing dir.

    This enumerates all the files in a directory, and all the files ending with '.rrtest'
    are assumed to be testing files.
    """
    global fHandle
    global gFailedTests
    global gPassedTests

    import os.path as p
    from glob import glob
    
    gFailedTests = 0
    gPassedTests = 0
    
    if testDir is None:
        testDir = getDefaultTestDir()

    if not p.isdir(testDir):
        raise Exception("{} is NOT a directory".format(testDir))

    files = glob(p.join(testDir, "*.rrtest"))

    unknownTests = 0
    for file in files:
        print("\n\nStarting Test on ", file)

        # set the globals, these should be class instance vars...
        fHandle = open (file, 'r')
        testId = jumpToNextTest()

        

        if testId == '[SBML]':
            sbmlStr, testId = getSBMLStr ()
        else:
            Logger.log(Logger.LOG_WARNING, "rrtest file, \"" 
                       + file + "\" missing SBML section, ignoring test file")
            continue
        

        # Load any initialization actions
        if testId == '[INITIALIZATION]':
            testId = jumpToNextTest ()
            while testId != '[END_INITIALIZATION]':
                if functions.has_key(testId):
                    func = functions[testId]
                    func (rrInstance, testId)
                else:
                    print('No initialization function found for ' + testId)
                testId = jumpToNextTest()
            testId = jumpToNextTest()

        # create a RoadRunner obj with the sbml from the test file
        rrInstance = roadrunner.RoadRunner(sbmlStr)
        print('Successfully loaded model.\n')

        # Now start the tests proper
        while testId != '':
            if functions.has_key(testId):
                func = functions[testId]
                func(rrInstance, testId)
            else:
                #getFloatingSpeciesAmountRates
                unknownTests = unknownTests+1
                print(string.ljust (testId, rpadding), 'UNKNOWN TEST')
            testId = jumpToNextTest()
        
    print("\n\nTotal failed tests:\t", gFailedTests, \
    "\nTotal unknown tests:\t", unknownTests, \
    "\nTotal passed tests:\t", gPassedTests)

    return gFailedTests
