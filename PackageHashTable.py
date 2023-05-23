
class PackageHashTable:
    # Constructor with optional initial capacity parameter.
    # Assigns all buckets with an empty list.
    def __init__(self, initial_capacity=10):
        # initialize the hash table with empty bucket list entries.
        self.table = []
        for i in range(initial_capacity):
            self.table.append([])

    # Inserts a new package into the hash table.
    def insert(self, package):
        # get the bucket list where this package will go.
        bucket = hash(int(package.id)) % len(self.table)
        bucket_list = self.table[bucket]

        # insert the package to the end of the bucket list.
        bucket_list.append(package)

    # Searches for an item with matching id in the hash table.
    # Returns the item if found, or None if not found.
    def search(self, id):
        # get the bucket list where this id would be.
        bucket = hash(id) % len(self.table)
        bucket_list = self.table[bucket]

        # search for the id in the bucket list
        for i in range(len(bucket_list)):
            if id == int(bucket_list[i].id):
                return bucket_list[i]
        return None

    # Removes an item with matching id from the hash table.
    def remove(self, id):
        # get the bucket list where this item will be removed from.
        bucket = hash(id) % len(self.table)
        bucket_list = self.table[bucket]

        # remove the item from the bucket list if it is present.
        for i in range(len(bucket_list)):
            if id == int(bucket_list[i].id):
                bucket_list.remove(bucket_list[i])
                break

