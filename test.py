import csv

results = {}
f = open("results/exploited/girvan_newman_inverted_2015.csv")
reader = csv.DictReader(f)
for row in reader:
    results.setdefault(row['community'], []).append(row)

for community, nodes in results.items():
    density = []
    for n in nodes:
        n['out_degree'] = int(n['weighted_degree']) - int(n['internal_weighted_degree'])
        density.append(n['out_degree'] < int(n['internal_weighted_degree']))

    internal_density = len([t for t in density if t is True])
    external_density = len([t for t in density if t is False])
    total = internal_density + external_density
    percentage = (internal_density * 100) / total

    print "Community %s has %s of internal density" % (community, str(percentage) + "%")