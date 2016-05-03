f = open("test", "r")
b = open("bernie_out", "r")
s = open("sshiang_out", "r")
lf = f.readlines()
lb = b.readlines()
ls = s.readlines()

out = open("vote_new", "w")
for l1, l2, l3 in zip(lf, lb, ls):
    count = [0, 0, 0]
    count[int(l1.split()[0])+1] += 1
    count[int(l2.split()[0])+1] += 1
    count[int(l3.split()[0])+1] += 1
    for i, c  in enumerate(count):
        if c >= 2:
            ans = i-1
            break
        ans = 1
    print >>out, ans



f.close()
b.close()
s.close()
out.close()
