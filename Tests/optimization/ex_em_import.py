import numpy as np


def getEx():

    a = {}
    try:
        A = np.loadtxt('../ExEm/EX_GREEN.dat')
    except:
        A = np.loadtxt('./ExEmAbs-dummy/EX_GREEN.txt')

    a['wavelengths'] = A[:, 0]
    a['intensities'] = A[:, 1]

    return a


def getEm():

    a = {}
    try:
        A = np.loadtxt('../ExEm/EM_GREEN.dat')
    except:
        A = np.loadtxt('./ExEmAbs-dummy/EM_GREEN.txt')

    a['wavelengths'] = A[:, 0]
    a['intensities'] = A[:, 1]

    return a


def getAbs():

    a = {}
    try:
        A = np.loadtxt('../ExEm/Abs_GREEN.dat')
    except:
        A = np.loadtxt('./ExEmAbs-dummy/Abs_GREEN.txt')

    a['wavelengths'] = A[:, 0]
    a['intensities'] = A[:, 1]

    return a

def getExRed():

    a = {}
    try:
        A = np.loadtxt('../ExEm/EX_RED.dat')
    except:
        A = np.loadtxt('./ExEmAbs-dummy/EX_Red.txt')

    a['wavelengths'] = A[:, 0]
    a['intensities'] = A[:, 1]

    return a


def getEmRed():

    a = {}
    try:
        A = np.loadtxt('../ExEm/EM_GREEN.dat')
    except:
        A = np.loadtxt('./ExEmAbs-dummy/EM_Red.txt')

    a['wavelengths'] = A[:, 0]
    a['intensities'] = A[:, 1]

    return a


def getAbsRed():

    a = {}
    try:
        A = np.loadtxt('../ExEm/Abs_GREEN.dat')
    except:
        A = np.loadtxt('./ExEmAbs-dummy/Abs_Red.txt')

    a['wavelengths'] = A[:, 0]
    a['intensities'] = A[:, 1]

    return a


if __name__ == '__main__':
    print(getEx())
    print(getEm())
    print(getAbs())
