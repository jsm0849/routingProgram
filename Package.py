from datetime import datetime


class Package:
    def __init__(self, id, address, city, state, zipcode, deadline, mass, specialNotes):
        self.id = id
        self.address = address
        self.city = city
        self.state = state
        self.zipcode = zipcode
        self.deadline = deadline
        self.mass = mass
        self.specialNotes = specialNotes
        self.status = "at the hub"
        self.deliveryTime = datetime.strptime('00:00:00', '%H:%M:%S')

    def update_status(self, status):
        self.status = status

    def deliver(self, deliveryTime):
        self.deliveryTime = deliveryTime