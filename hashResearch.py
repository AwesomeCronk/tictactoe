import sys

from utils import *


def base3Str(src):
    numDigits = 1
    while 3 ** numDigits <= src: numDigits += 1
    digits = [0] * numDigits

    remaining = src

    for i0 in range(numDigits):
        exp = numDigits - 1 - i0
        digit = remaining // (3 ** exp)
        remaining -= digit * (3 ** exp)
        digits[i0] = digit

    return ''.join(str(digit) for digit in digits)


if __name__ == '__main__':
    uniqueHashes = []
    validUniqueHashes = []

    for hash in range(int(sys.argv[1])):

        # print('hash:', hash)

        bestAltHash = getBestAltHash(hash)

        if not bestAltHash in uniqueHashes:
            uniqueHashes.append(bestAltHash)

            if hashIsValidGameState(bestAltHash):
                validUniqueHashes.append(bestAltHash)

    print('numUniqueHashes:', len(uniqueHashes))
    print('maxUniqueHash:', max(uniqueHashes))

    print('numValidUniqueHashes:', len(validUniqueHashes))
    print('maxValidUniqueHash:', max(validUniqueHashes))

    with open('uniqueHashes.txt', 'w') as file:
        for validUniqueHash in validUniqueHashes:
            file.write('{:>5} {:>9}\n'.format(validUniqueHash, base3Str(validUniqueHash)))


