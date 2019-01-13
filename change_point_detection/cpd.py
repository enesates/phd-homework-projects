import matplotlib.pyplot as plt
import numpy as np

y = []
x = []
size = 0
std = 0


# reading data from file
def read_data(fileName):
    global x, y, size, std

    with open(fileName) as f:
        y = map(float, f)
        y = list(filter(lambda x: x != 0, y))

        size = len(y)
        std = np.std(y)

        x = range(size)


def main():
    global x, y, size, std
    fig = plt.figure()

    # chart window
    ax1 = fig.add_subplot(211)
    ax1.set_title("Change Point Detection..")
    ax1.set_xlabel('Time')
    ax1.set_ylabel('Nuclear Response')

    # draw all data from file
    ax1.plot(x, y, c='r', label='the data')

    y = np.asarray(y)

    # group data
    jump = 50
    interval = int(size/jump)

    # find mean for grouped data
    points = []
    parts = []
    for i in range(jump):
        part = np.mean(y[i * interval:i * interval + interval])
        for j in range(interval):
            points.append(part)
        parts.append(part)

    # find where is global changes
    temp = parts[0]
    changePoints = []
    for i, j in enumerate(parts):
        if j > (temp+std) or j < (temp - std):
            changePoints.append(i * interval)

        temp = j

    # find local changes
    localChangePoints = []
    for i in changePoints:
        temp = y[i-interval]

        for j in range(i-interval, i+interval):
            if y[j] > (temp + std/2) or y[j] < (temp - std/2):
                avgLeft = np.mean(y[j-5:j])
                avgRight = np.mean(y[j+1:j+5])
                diff = abs(avgLeft - avgRight)
                if diff > std/2:
                    localChangePoints.append(j)

            temp = y[j]

    # clean similar points
    cleanedList = []
    passList = []
    for i in range(len(localChangePoints)-1):
        if i in passList:
            continue
        diff = localChangePoints[i+1] - localChangePoints[i]
        if diff < 5:
            avgg = np.mean(y[localChangePoints[i]:localChangePoints[i]+interval])
            diff1 = abs(y[localChangePoints[i]] - avgg)
            diff2 = abs(y[localChangePoints[i+1]] - avgg)

            if diff1 < diff2:
                cleanedList.append(localChangePoints[i])
                passList.append(i+1)

        else:
            cleanedList.append(localChangePoints[i])

    # draw line with changes point
    cleanedList.append(size-1)
    cleanedX = []
    cleanedY = []
    temp = 0
    for i in cleanedList:
        meann = np.mean(y[temp:i])
        for j in range(temp, i):
            cleanedX.append(j)
            cleanedY.append(meann)
        temp = i

    ax1.plot(cleanedX, cleanedY, c='b', label='the data')

    # draw change amount
    changesY = []
    for i in cleanedList:
        diff = abs(y[i] - y[i-1])
        changesY.append(diff)

    ax2 = fig.add_subplot(212)
    ax2.axis([0, 4000, 0, 15000])
    ax2.bar(cleanedList, changesY, 0.5, color="green")

    # print change points and their values
    print "Change  -  Values"
    for i in cleanedList:
        print i, "   - ", y[i]

    plt.show()
    plt.pause(0)

if __name__ == '__main__':
    fileName = "well_log_data_no_outliers.txt"
    read_data(fileName)
    main()
