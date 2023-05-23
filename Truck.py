class Truck:
    def __init__(self, capacity):
        self.capacity = capacity
        self.packages = []
        self.priorityPkgs = []
        self.mileage = 0

    def add_package(self, packageId):
        if len(self.packages) < self.capacity:
            self.packages.append(packageId)
            return 0
        return None

    def remove_package(self, packageIndex):
        self.packages.remove(packageIndex)

    def add_mileage(self, miles):
        self.mileage = self.mileage + miles
