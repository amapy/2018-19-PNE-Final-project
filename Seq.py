class Seq:
    def __init__(self, strbase):
        self.strbase = strbase

    def len(self):
        return len(self.strbase)

    def complement(self):
        complement_list = []
        for n in self.strbase:
            if n == "A":
                complement_list.append("T")
            elif n == "T":
                complement_list.append("A")
            elif n == "G":
                complement_list.append("C")
            elif n == "C":
                complement_list.append("G")
        element1 = ','.join(complement_list).replace(",", "")
        element1_1 = Seq(element1)
        return element1_1.strbase

    def reverse(self):
        reverse_list = []
        n = len(self.strbase) - 1
        while n >= 0:
            reverse_list.append(self.strbase[n])
            n -= 1
        element2 = ','.join(reverse_list).replace(",", "")
        element2_1 = Seq(element2)
        return element2_1.strbase

    def count(self, base):
        self.base = base.upper()
        return self.strbase.count(self.base)

    def perc(self, base):
        self.base = base.upper()
        element3 = round(100.0 * self.count(base) / self.len(), 1)
        element3_1 = Seq(element3)
        return element3_1.strbase