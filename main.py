# Author: Jacob Smith
# Date: 10/07/2022

from Package import Package
from PackageHashTable import PackageHashTable
from Address import Address
from Truck import Truck
import csv
from datetime import timedelta, datetime

# defining the hash table for Packages, the 2D array of distance values, and the list of Addresses.
packageTable = PackageHashTable()
distancesTable = []
addressList = []
CAPACITY = 16  # The capacity of each truck.
truck1, truck2, truck3 = {Truck(CAPACITY), Truck(CAPACITY), Truck(CAPACITY)}

# function to look up a street address and get a numeric value that matches it, corresponding with
# the distance data. (O n)
def address_lookup(address):
    for i in range(len(addressList)):
        if address == addressList[i].streetAddress:
            return i
    return None

# Function to load the three trucks with packages in a logical distribution.
def load_trucks():
    specialPkgs = []
    normalPkgs = []

    # First, sort between packages with special instructions and those without. (O n^2)
    for i in range(len(packageTable.table)):
        for j in range(len(packageTable.table[i])):
            thisBucket = packageTable.table[i]
            if thisBucket[j].specialNotes != "":
                specialPkgs.append(int(thisBucket[j].id))
            else:
                normalPkgs.append(int(thisBucket[j].id))

    # bubble sort used to sort normal packages (without special notes) by zipcode in ascending order. (O n^2)
    for i in range(len(normalPkgs)):
        for j in range(len(normalPkgs) - 1):
            package = packageTable.search(normalPkgs[j])
            nextPkg = packageTable.search(normalPkgs[j + 1])
            if package.zipcode > nextPkg.zipcode:
                tempPkg = normalPkgs[j]
                normalPkgs[j] = normalPkgs[j + 1]
                normalPkgs[j + 1] = tempPkg

    # The packages with special instructions need to be loaded first. This is the part of the code which would have to
    # be changed in the future depending on the special notes required. (O n)
    for i in range(len(specialPkgs)):
        package = packageTable.search(specialPkgs[i])
        note = package.specialNotes
        id = package.id
        if note == "Can only be on truck 2":
            truck2.add_package(id)
        elif note == "Must be delivered with 13":
            truck2.add_package(id)
        elif note == "Must be delivered with 13, 15":
            truck2.add_package(id)
        elif note == "Must be delivered with 13, 19":
            truck2.add_package(id)
        elif note == "Must be delivered with 15, 19":
            truck2.add_package(id)
        elif note == "Wrong address listed":
            truck3.add_package(id)
        elif note == "Delayed on flight---will not arrive to depot until 9:05 am":
            if package.deadline != "EOD":
                truck1.add_package(id)
                truck1.priorityPkgs.append(id)
            else:
                truck3.add_package(id)
            continue
        if package.deadline != "EOD":
            truck2.priorityPkgs.append(id)

    # Load the normal packages (O n)
    for i in range(len(normalPkgs)):
        package = packageTable.search(normalPkgs[i])
        id = package.id
        if id == '2' or id == '33' or id == '7':
            truck3.add_package(id)
            continue
        if id == '1' or id == '40':
            truck1.add_package(id)
            truck1.priorityPkgs.append(id)
            continue
        if id == '24':
            truck3.add_package(id)
            continue
        if len(truck1.packages) < (truck1.capacity - 6):
            truck1.add_package(id)
            if package.deadline != "EOD":
                truck1.priorityPkgs.append(id)
        elif package.zipcode == '84107':
            truck3.add_package(id)
        elif len(truck2.packages) < truck2.capacity and package.zipcode == '84115':
            truck2.add_package(id)
        elif len(truck2.packages) < truck2.capacity:
            truck2.add_package(id)
            if package.deadline != "EOD":
                truck2.priorityPkgs.append(id)
        else:
            if len(truck1.packages) < truck1.capacity and package.deadline != "EOD":
                truck1.add_package(id)
                truck1.priorityPkgs.append(id)
                continue
            truck3.add_package(id)
            if package.deadline != "EOD":
                truck3.priorityPkgs.append(id)


# Function to deliver the packages up until the specified time and display the package statuses. The nearest
# neighbor algorithm is used.
def deliver_packages(statusTime, pkgId):
    # Arrays to hold the complete starting list of packages on each truck that can be referenced after packages
    # have been delivered off of the trucks.
    t1 = truck1.packages.copy()
    t2 = truck2.packages.copy()
    t3 = truck3.packages.copy()
    HUB_ADDRESS = 0
    # Loop through each truck's deliveries, incrementing the time and mileage for each package until either the user
    # entered time or the end of the route has been reached. (O n^3)
    currentTime = datetime.strptime('09:05:00', '%H:%M:%S')
    previousAddress = HUB_ADDRESS
    previousDistance = 0
    nearestNeighbor = 0
    nearestNeighborAddress = 0
    distance = 0
    addressCorrected = 0  # Variable to check if the address for package 9 has been corrected yet.
    if currentTime < statusTime:
        for i in range(len(truck1.packages)):
            packageTable.search(int(truck1.packages[i])).update_status('in route')
    while currentTime < statusTime and len(truck1.packages) > 0:
        # Deliver the priority packages in truck 1 first (those with an early delivery deadline).
        while len(truck1.priorityPkgs) > 0:
            for i in range(len(truck1.priorityPkgs)):
                package = packageTable.search(int(truck1.priorityPkgs[i]))
                pkgAddress = address_lookup(package.address)
                if float(distancesTable[pkgAddress][previousAddress]) < previousDistance or previousDistance == 0 or len(truck1.priorityPkgs) == 1:
                    nearestNeighbor = truck1.priorityPkgs[i]
                    distance = float(distancesTable[pkgAddress][previousAddress])
                    previousDistance = distance
                    nearestNeighborAddress = pkgAddress
            currentTime = currentTime + timedelta(hours=(distance / 18))
            if currentTime > statusTime:
                break
            truck1.add_mileage(distance)
            previousAddress = nearestNeighborAddress
            truck1.priorityPkgs.remove(nearestNeighbor)
            truck1.remove_package(nearestNeighbor)
            packageTable.search(int(nearestNeighbor)).update_status('delivered')
            packageTable.search(int(nearestNeighbor)).deliver(currentTime)
            previousDistance = 0

        # Deliver the rest of the packages in truck 1 and return to the Hub ("truck 1" then becomes "truck 3"). (O n)
        if currentTime > statusTime:
            break
        previousDistance = 0
        if currentTime >= datetime.strptime('10:20:00', '%H:%M:%S') and addressCorrected == 0:
            packageNine = packageTable.search(9)
            packageNine.address = '410 S State St'
            packageNine.city = 'Salt Lake City'
            packageNine.state = 'UT'
            packageNine.zipcode = '84111'
            addressCorrected = 1
        for i in range(len(truck1.packages)):
            package = packageTable.search(int(truck1.packages[i]))
            pkgAddress = address_lookup(package.address)
            if float(distancesTable[pkgAddress][previousAddress]) < previousDistance or previousDistance == 0 or len(truck1.packages) == 1:
                nearestNeighbor = truck1.packages[i]
                distance = float(distancesTable[pkgAddress][previousAddress])
                previousDistance = distance
                nearestNeighborAddress = pkgAddress
        currentTime = currentTime + timedelta(hours=(distance / 18))
        if currentTime > statusTime:
            break
        truck1.add_mileage(distance)
        previousAddress = nearestNeighborAddress
        truck1.remove_package(nearestNeighbor)
        packageTable.search(int(nearestNeighbor)).update_status('delivered')
        packageTable.search(int(nearestNeighbor)).deliver(currentTime)

    # Continue to deliver packages as "Truck 3" if the user requested time has not yet been exceeded. (O n^2)
    if currentTime < statusTime and len(truck1.packages) == 0:
        distance = float(distancesTable[previousAddress][HUB_ADDRESS])
        truck1.add_mileage(distance)
        currentTime = currentTime + timedelta(hours=(distance / 18))
        distance = 0
        for i in range(len(truck3.packages)):
            packageTable.search(int(truck3.packages[i])).update_status('in route')
        while currentTime < statusTime and len(truck3.packages) > 0:
            # Deliver the priority packages in truck 3 first (those with an early delivery deadline).
            while len(truck1.priorityPkgs) > 0:
                for i in range(len(truck3.priorityPkgs)):
                    package = packageTable.search(int(truck3.priorityPkgs[i]))
                    pkgAddress = address_lookup(package.address)
                    if float(distancesTable[pkgAddress][
                                 previousAddress]) < previousDistance or previousDistance == 0 or len(
                            truck3.priorityPkgs) == 1:
                        nearestNeighbor = truck3.priorityPkgs[i]
                        distance = float(distancesTable[pkgAddress][previousAddress])
                        previousDistance = distance
                        nearestNeighborAddress = pkgAddress
                currentTime = currentTime + timedelta(hours=(distance / 18))
                if currentTime > statusTime:
                    break
                truck3.add_mileage(distance)
                previousAddress = nearestNeighborAddress
                truck3.priorityPkgs.remove(nearestNeighbor)
                truck3.remove_package(nearestNeighbor)
                packageTable.search(int(nearestNeighbor)).update_status('delivered')
                packageTable.search(int(nearestNeighbor)).deliver(currentTime)
                previousDistance = 0

            # Deliver the rest of the packages in truck 3. (O n)
            if currentTime > statusTime:
                break
            previousDistance = 0
            for i in range(len(truck3.packages)):
                package = packageTable.search(int(truck3.packages[i]))
                if currentTime >= datetime.strptime('10:20:00', '%H:%M:%S') and addressCorrected == 0:
                    packageNine = packageTable.search(9)
                    packageNine.address = '410 S State St'
                    packageNine.city = 'Salt Lake City'
                    packageNine.state = 'UT'
                    packageNine.zipcode = '84111'
                    addressCorrected = 1
                pkgAddress = address_lookup(package.address)
                if float(distancesTable[pkgAddress][previousAddress]) < previousDistance or previousDistance == 0 or len(truck3.packages) == 1:
                    nearestNeighbor = truck3.packages[i]
                    if currentTime < datetime.strptime('10:20:00', '%H:%M:%S') and nearestNeighbor == '9':
                        continue
                    distance = float(distancesTable[pkgAddress][previousAddress])
                    previousDistance = distance
                    nearestNeighborAddress = pkgAddress
            currentTime = currentTime + timedelta(hours=(distance / 18))
            if currentTime > statusTime:
                break
            truck3.add_mileage(distance)
            previousAddress = nearestNeighborAddress
            truck3.remove_package(nearestNeighbor)
            packageTable.search(int(nearestNeighbor)).update_status('delivered')
            packageTable.search(int(nearestNeighbor)).deliver(currentTime)

    # Deliver packages on Truck 2 until the user requested time is exceeded. Leaves the Hub at the same time as
    # Truck 1.
    currentTime = datetime.strptime('08:00:00', '%H:%M:%S')
    previousAddress = HUB_ADDRESS
    previousDistance = 0
    nearestNeighbor = 0
    nearestNeighborAddress = 0
    distance = 0
    # Loop through each truck's deliveries, incrementing the time and mileage for each package until either the user
    # entered time or the end of the route has been reached. (O n^2)
    for i in range(len(truck2.packages)):
        packageTable.search(int(truck2.packages[i])).update_status('in route')
    while currentTime < statusTime and len(truck2.packages) > 0:
        # Deliver the priority packages in truck 2 first (those with an early delivery deadline).
        while len(truck2.priorityPkgs) > 0:
            for i in range(len(truck2.priorityPkgs)):
                package = packageTable.search(int(truck2.priorityPkgs[i]))
                pkgAddress = address_lookup(package.address)
                if float(distancesTable[pkgAddress][previousAddress]) < previousDistance or previousDistance == 0 or len(truck2.priorityPkgs) == 1:
                    nearestNeighbor = truck2.priorityPkgs[i]
                    distance = float(distancesTable[pkgAddress][previousAddress])
                    previousDistance = distance
                    nearestNeighborAddress = pkgAddress
            currentTime = currentTime + timedelta(hours=(distance / 18))
            if currentTime > statusTime:
                break
            truck2.add_mileage(distance)
            previousAddress = nearestNeighborAddress
            truck2.priorityPkgs.remove(nearestNeighbor)
            truck2.remove_package(nearestNeighbor)
            packageTable.search(int(nearestNeighbor)).update_status('delivered')
            packageTable.search(int(nearestNeighbor)).deliver(currentTime)
            previousDistance = 0

        # Deliver the rest of the packages in truck 2. (O n)
        if currentTime > statusTime:
            break
        for i in range(len(truck2.packages)):
            package = packageTable.search(int(truck2.packages[i]))
            pkgAddress = address_lookup(package.address)
            if float(distancesTable[pkgAddress][previousAddress]) < previousDistance or previousDistance == 0 or len(
                    truck2.packages) == 1:
                nearestNeighbor = truck2.packages[i]
                distance = float(distancesTable[pkgAddress][previousAddress])
                previousDistance = distance
                nearestNeighborAddress = pkgAddress
        currentTime = currentTime + timedelta(hours=(distance / 18))
        if currentTime > statusTime:
            break
        truck2.add_mileage(distance)
        previousAddress = nearestNeighborAddress
        truck2.remove_package(nearestNeighbor)
        packageTable.search(int(nearestNeighbor)).update_status('delivered')
        packageTable.search(int(nearestNeighbor)).deliver(currentTime)
        previousDistance = 0

    # Display the correct information depending on what the user asked for. (O n)
    if pkgId == '0': # Display all information about all packages as well as truck mileages at the requested time.
        miles1 = truck1.mileage
        miles2 = truck2.mileage
        miles3 = truck3.mileage
        totalMiles = miles1 + miles2 + miles3
        print('\n\n\nTruck 1 (mileage:', '%.2f' % miles1, '):\n')
        for i in range(len(t1)):
            package = packageTable.search(int(t1[i]))
            if package.deliveryTime != datetime.strptime('00:00:00', '%H:%M:%S'):
                print('\tID:', package.id, '\tStatus:', package.status, '\tDelivered at', package.deliveryTime.strftime('%H:%M:%S'))
            else:
                print('\tID:', package.id, '\tStatus:', package.status)
            print('\t\tAddress:', package.address, package.city, package.zipcode)
            print('\t\tDelivery Deadline:', package.deadline, 'Package Weight:', package.mass)
        print('\nTruck 2 (mileage:', '%.2f' % miles2, '):\n')
        for i in range(len(t2)):
            package = packageTable.search(int(t2[i]))
            if package.deliveryTime != datetime.strptime('00:00:00', '%H:%M:%S'):
                print('\tID:', package.id, '\tStatus:', package.status, '\tDelivered at', package.deliveryTime.strftime('%H:%M:%S'))
            else:
                print('\tID:', package.id, '\tStatus:', package.status)
            print('\t\tAddress:', package.address, package.city, package.zipcode)
            print('\t\tDelivery Deadline:', package.deadline, 'Package Weight:', package.mass)
        print('\nTruck 3 (mileage:', '%.2f' % miles3, '):\n')
        for i in range(len(t3)):
            package = packageTable.search(int(t3[i]))
            if package.deliveryTime != datetime.strptime('00:00:00', '%H:%M:%S'):
                print('\tID:', package.id, '\tStatus:', package.status, '\tDelivered at', package.deliveryTime.strftime('%H:%M:%S'))
            else:
                print('\tID:', package.id, '\tStatus:', package.status)
            print('\t\tAddress:', package.address, package.city, package.zipcode)
            print('\t\tDelivery Deadline:', package.deadline, 'Package Weight:', package.mass)
        print('\nTotal Mileage:', '%.2f' % totalMiles)
    else:  # Display only the information about the requested package at the requested time.
        package = packageTable.search(int(pkgId))
        if package.deliveryTime != datetime.strptime('00:00:00', '%H:%M:%S'):
            print('\tID:', package.id, '\tStatus:', package.status, '\tDelivered at',
                  package.deliveryTime.strftime('%H:%M:%S'))
        else:
            print('\tID:', package.id, '\tStatus:', package.status)
        print('\t\tAddress:', package.address,  package.city, package.zipcode)
        print('\t\tDelivery Deadline:', package.deadline, 'Package Weight:', package.mass)
        print('Mileage of Truck 1:', '%.2f' % truck1.mileage, 'Truck 2:', '%.2f' % truck2.mileage, 'Truck 3:', '%.2f' % truck3.mileage)

# Main Program
# Reading the package data and creating the Package objects, as well as inserting them into
# the hash table. (O n)
with open("packages.csv", 'r') as csvfile:
    csvReader = csv.reader(csvfile)
    for row in csvReader:
        currentPackage = Package(row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7])
        packageTable.insert(currentPackage)
csvfile.close()

# reading the distance values and populating the distance table. (O n)
with open("distances.csv", 'r') as csvfile:
    csvReader = csv.reader(csvfile)
    for row in csvReader:
        distancesTable.append(row)
csvfile.close()

# reading the address data and creating the Address objects, as well as inserting them into
# the Address list. (O n)
with open("addresses.csv", 'r') as csvfile:
    csvReader = csv.reader(csvfile)
    for row in csvReader:
        currentAddress = Address(row[0], row[1], row[2], row[3])
        addressList.append(currentAddress)
csvfile.close()

load_trucks()

# Get user input for a specific time to see the package status(es) and the desired package ID.
cont = input("Would you like to check the status at a specific time? (y/n): ")
if cont != 'y' and cont != 'Y':
    print("Goodbye")
else:
    userTime = input("\n\n\nCHECK PACKAGE STATUS\nEnter a time (HH:MM:ss): ")
    userId = input('Enter the ID number of the package to check, or enter "0" to see all packages: ')
    statusTime = datetime.strptime(userTime, '%H:%M:%S')
    deliver_packages(statusTime, userId)

