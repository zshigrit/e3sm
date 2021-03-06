from netCDF4 import Dataset
import math
import matplotlib.pyplot as plt
import matplotlib as mpl
import numpy as np

#--------------------------------------------------------

def L2_norm(numerical, analytical, nPoints, areaCell):

    norm  = 0.0
    denom = 0.0

    for iPoint in range(0,nPoints):

        norm  += areaCell[iPoint] * math.pow(numerical[iPoint] - analytical[iPoint],2)

        denom += areaCell[iPoint] * math.pow(analytical[iPoint],2)

    norm = math.sqrt(norm / denom)

    return norm

#--------------------------------------------------------

def get_norm_area(filename):

    fileMPAS = Dataset(filename, "r")

    nCells = len(fileMPAS.dimensions["nCells"])

    areaCell = fileMPAS.variables["areaCell"][:]

    iceAreaCategory = fileMPAS.variables["iceAreaCategory"][:]
    iceAreaCell = np.sum(iceAreaCategory,axis=(2,3))

    iceAreaCellInitial = iceAreaCell[0,:]
    iceAreaCellFinal   = iceAreaCell[-1,:]

    norm = L2_norm(iceAreaCellFinal, iceAreaCellInitial, nCells, areaCell)

    fileMPAS.close()

    return norm

#--------------------------------------------------------

def get_norm_thickness(filename):

    fileMPAS = Dataset(filename, "r")

    nCells = len(fileMPAS.dimensions["nCells"])

    areaCell = fileMPAS.variables["areaCell"][:]

    iceAreaCategoryInitial = fileMPAS.variables["iceAreaCategory"][0,:,0,0]
    iceAreaCategoryFinal   = fileMPAS.variables["iceAreaCategory"][-1,:,0,0]

    iceVolumeCategoryInitial = fileMPAS.variables["iceVolumeCategory"][0,:,0,0]
    iceVolumeCategoryFinal   = fileMPAS.variables["iceVolumeCategory"][-1,:,0,0]

    iceThicknessCategoryInitial = np.zeros(nCells)
    iceThicknessCategoryFinal   = np.zeros(nCells)

    for iCell in range(0,nCells):
        if (iceAreaCategoryInitial[iCell] > 0.0):
            iceThicknessCategoryInitial[iCell] = iceVolumeCategoryInitial[iCell] / iceAreaCategoryInitial[iCell]
        if (iceAreaCategoryFinal[iCell] > 0.0):
            iceThicknessCategoryFinal[iCell] = iceVolumeCategoryFinal[iCell] / iceAreaCategoryFinal[iCell]

    norm = L2_norm(iceThicknessCategoryFinal, iceThicknessCategoryInitial, nCells, areaCell)

    fileMPAS.close()

    return norm

#--------------------------------------------------------

def get_resolution(filename):

    fileMPAS = Dataset(filename, "r")

    nCells = len(fileMPAS.dimensions["nCells"])
    nEdges = len(fileMPAS.dimensions["nEdges"])

    # mean distance between cells
    dcEdge = fileMPAS.variables["dcEdge"][:]

    resolution = 0.0
    for iEdge in range(0,nEdges):
        resolution = resolution + dcEdge[iEdge]

    resolution = resolution / float(nEdges)

    fileMPAS.close()

    return resolution / 1000.0

#--------------------------------------------------------

def get_grid_size(filename):

    fileMPAS = Dataset(filename, "r")

    nCells = len(fileMPAS.dimensions["nCells"])

    return nCells

#--------------------------------------------------------

def advection_error_convergence():

    resolutions = [2562,10242,40962,163842]

    methods = ["IR", "upwind"]
    #methods = ["IR"]
    experiments = ["cosine_bell","slotted_cylinder"]

    legendLabels = ["CB IR", "CB Upwind", "SC IR", "SC Upwind"]
    #legendLabels = ["CB IR", "SC IR"]

    markers = ['o','o','^','^']
    #markers = ['o','^']
    linestyles = ["-", "--", "-", "--"]
    #linestyles = ["-", "-"]
    dashes=[(1,0),(5,2.5),(1,0),(5,2.5)]

    xMin = 60
    xMax = 120

    yMin = 3e-2
    yMax = 1

    scaleArea1 = 0.15 / math.pow(xMax,1)
    scaleMinArea1 = math.pow(xMin,1) * scaleArea1
    scaleMaxArea1 = math.pow(xMax,1) * scaleArea1

    scaleArea2 = 0.15 / math.pow(xMax,2)
    scaleMinArea2 = math.pow(xMin,2) * scaleArea2
    scaleMaxArea2 = math.pow(xMax,2) * scaleArea2

    scaleThickness = 10e-1 / math.pow(xMin,1)

    scaleMinThickness = math.pow(xMin,1) * scaleThickness
    scaleMaxThickness = math.pow(xMax,1) * scaleThickness

    #plot
    cm = 1/2.54  # centimeters in inches
    plt.rcParams["font.family"] = "Times New Roman"
    #mpl.rc('text', usetex=True)
    SMALL_SIZE = 8
    MEDIUM_SIZE = 8
    BIGGER_SIZE = 8
    plt.rc('font', size=SMALL_SIZE)          # controls default text sizes
    plt.rc('axes', titlesize=SMALL_SIZE)     # fontsize of the axes title
    plt.rc('axes', labelsize=MEDIUM_SIZE)    # fontsize of the x and y labels
    plt.rc('xtick', labelsize=SMALL_SIZE)    # fontsize of the tick labels
    plt.rc('ytick', labelsize=SMALL_SIZE)    # fontsize of the tick labels
    plt.rc('legend', fontsize=SMALL_SIZE)    # legend fontsize
    plt.rc('figure', titlesize=BIGGER_SIZE)  # fontsize of the figure title
    #mpl.rcParams['axes.linewidth'] = 0.5

    fig, axes = plt.subplots(1, 1, figsize=(8*cm,6.5*cm))


    axes.loglog([xMin, xMax], [scaleMinArea1, scaleMaxArea1], linestyle=':', color='k', label="_nolegend_", lw=1)
    axes.loglog([xMin, xMax], [scaleMinArea2, scaleMaxArea2], linestyle=':', color='k', label="_nolegend_", lw=1)

    iPlot = 0
    for experiment in experiments:
        for method in methods:

            xArea = []
            yArea = []

            xVolume = []
            yVolume = []

            for resolution in resolutions:

                filename = "./output_%s_%s_%i/output.2000.nc" %(method,experiment,resolution)

                norm = get_norm_area(filename)
                xArea.append(get_resolution(filename))
                yArea.append(norm)

                norm = get_norm_thickness(filename)
                xVolume.append(get_resolution(filename))
                yVolume.append(norm)

            print(xArea,yArea)
            axes.loglog(xArea, yArea, marker=markers[iPlot], dashes=dashes[iPlot], color="black", markersize=5.0)

            iPlot = iPlot + 1


    axes.legend(legendLabels, frameon=False, loc=4, fontsize=8, handlelength=4)

    # area

    plt.minorticks_off()

    #axes.set_title("Ice concentration")
    axes.set_xlabel("Grid resolution (km)")
    axes.set_ylabel(r"$L_2$ error norm")
    axes.set_xticklabels(["60","120","240","480"])
    axes.set_xticks([60,120,240,480])
    axes.tick_params(
        axis='x',          # changes apply to the x-axis
        which='minor',      # both major and minor ticks are affected
        bottom='off',      # ticks along the bottom edge are off
        top='off',         # ticks along the top edge are off
        labelbottom='off')

    plt.tight_layout(pad=0.2, w_pad=0.2, h_pad=0.2)
    plt.savefig("advection_error_convergence.png",dpi=300)
    plt.savefig("advection_error_convergence.eps")

#-------------------------------------------------------------------------------

if __name__ == "__main__":

    advection_error_convergence()
