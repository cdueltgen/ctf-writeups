ip_dict = {}
with open("merged.log", "r") as file:
    for line in file:
        a = line.split()
        ip_dict[a[0]] = ip_dict.setdefault(a[0], 0) + int(a[3])

print(ip_dict)
