import bulldozer_2D
import matplotlib.pyplot as plt

start = 4e-1
rg = []
msize = []
nc = []
for i in range(1,12):
    ms = start / (2*i)
    print(ms)
    msize.append(ms)
    ct, xd = bulldozer_2D.bulldozer2D(ms)
    rg.append(abs(xd))
    nc.append(ct)


print(rg)
print(msize)
fig, ax = plt.subplots()  # Create a figure containing a single axes.
ax.plot(nc, rg)
ax.set_title("Number of Nodes - Displacement x ")
ax.set_xlabel("Number of Nodes")
ax.set_ylabel("Displacement")
plt.show()  