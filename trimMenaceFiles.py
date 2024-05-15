import sys

from utils import *


def loadMatchboxes(matchboxPath):
    matchboxes = []
    with open(matchboxPath, 'r') as matchboxFile:
        for matchbox in matchboxFile:
            matchboxes.append([])
            for bead in matchbox[:-1].split():
                matchboxes[-1].append(int(bead))
    
    # If the matchbox file is incomplete, load empty matchboxes
    while len(matchboxes) < (3 ** 9):
        matchboxes.append([])
    
    return matchboxes

def saveMatchboxes(matchboxPath, matchboxes):
    with open(matchboxPath, 'w') as matchboxFile:
        for matchbox in matchboxes:
            matchboxFile.write(' '.join([str(spot) for spot in matchbox]))
            matchboxFile.write('\n')

if __name__ == '__main__':
    uniqueHashes = []
    validUniqueHashes = []

    matchboxes = loadMatchboxes(sys.argv[1])
    trimmedMatchboxes = 0

    for hash in range(3 ** 9):

        # print('hash:', hash)

        bestAltHash, transformations = getBestAltHash(hash)

        if bestAltHash < hash or not hashIsValidGameState(hash):
            matchboxes[hash] = []
            trimmedMatchboxes += 1
            
    saveMatchboxes(sys.argv[1], matchboxes)

    print('Trimmed {} matchboxes'.format(trimmedMatchboxes))