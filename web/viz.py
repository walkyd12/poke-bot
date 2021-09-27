import os

import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

from scipy import stats

def viz(static_path, csv_filename, plot_filename):
    full_csv_path = static_path + "/" + csv_filename
    full_plot_path = static_path + "/" + plot_filename

    fig, ax = plt.subplots(4)

    df = pd.read_csv(full_csv_path)

    b_z = np.abs(stats.zscore(df['b']))
    g_z = np.abs(stats.zscore(df['g']))
    r_z = np.abs(stats.zscore(df['r']))

    df['b_z'] = b_z
    df['g_z'] = g_z
    df['r_z'] = r_z

    rgb_array = []
    false_pos = []
    true_neg = []
    last_color = []

    for i in range(0, df.count()[0]):
        c = [df['b'][i],df['g'][i],df['r'][i]]
        if max(b_z[i], max(g_z[i], r_z[i])) < 4:
            rgb_array.append(c)
            true_neg.append(c)
        else:
            rgb_array.append([0,0,0])
            false_pos.append([df['r'][i],df['g'][i],df['b'][i]])
        if i == df.count()[0] - 1:
            last_color.append([df['r'][i],df['g'][i],df['b'][i]])

    img = np.array(rgb_array, dtype=int).reshape((1, len(rgb_array), 3))
    ax[0].imshow(img, extent=[0, len(rgb_array), 0, 1], aspect='auto')
    ax[0].set_ylabel('Timeline')
    ax[0].set_yticklabels([])

    img2 = np.array(false_pos, dtype=int).reshape((1, len(false_pos), 3))
    ax[1].imshow(img2, extent=[0, len(false_pos), 0, 1], aspect='auto')
    ax[1].set_ylabel('Shiny/False-Pos')
    ax[1].set_yticklabels([])

    img3 = np.array(true_neg, dtype=int).reshape((1, len(true_neg), 3))
    ax[2].imshow(img3, extent=[0, len(true_neg), 0, 1], aspect='auto')
    ax[2].set_ylabel('Not-shiny')
    ax[2].set_yticklabels([])

    img4 = np.array(last_color, dtype=int).reshape((1, len(last_color), 3))
    ax[3].imshow(img4, extent=[0, len(last_color), 0, 1], aspect='auto')
    ax[3].set_ylabel('Last Color')
    ax[3].set_yticklabels([])
    
    plt.xlabel('Encounters')

    plt.savefig(full_plot_path)