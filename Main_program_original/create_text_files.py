import glob as glob
import cv2
import numpy as np
import random

def create_files():
    labels = []
    images = []
    tupple = []
    path = ['E/', 'P/', 'L/', 'R/', 'D/', 'T/']
    output = ['E/label.txt', 'P/label.txt', 'L/label.txt', 'R/label.txt', 'D/label.txt', 'T/label.txt']
    ii = 0
    for single in range(len(path)):
        ff = open(output[ii], 'w')
        ii += 1
        folder =  glob.glob(str(path[single]))
        for file in folder:
            img = cv2.imread(file, 1)
            img = cv2.resize(img, (28, 28))
            img = np.array(img).astype('float')
            tupple.append((img, single+1)))
            ff.write(path.index(single)+1)

        ff.close()

    random.shuffle(tupple)

    print "Data read and shuffled...."
    print "size: ", len(tupple)

    for obj in tupple:
        images.append(obj[0])
        labels.append(obj[1])

    print "images size: ", len(images)
    print "labels size: ", len(labels)

    np.savez('trafficsigns@teknofest.npz', train = images, train_labels = labels)



create_files()