#Writen by TH3EEuphoricFan1161
import argparse, textwrap
import matplotlib.pyplot as plt  # type: ignore
from matplotlib.lines import Line2D  # type: ignore
import numpy as np
from scipy import signal
from scipy.io import wavfile
from scipy.io import wavfile
from scipy.signal import ZoomFFT
from scipy.optimize import curve_fit
from scipy.fftpack import fft, ifft, fftshift
import math
import csv
import os



#================================================#
#                    Argparse                    #
#================================================#
parser = argparse.ArgumentParser()
parser.add_argument("-sw", "--scan_DTMF_write", action="store_true", help="Scan the waveform for DTMF frequencies and write results to a file")
parser.add_argument("-swI", "--scan_DTMF_write_file_in", type=str, default=None, help="Set the filepath for the input .wav file")
parser.add_argument("-sw1", "--DTMF_plot_LRD", type=str, default="left", help="Set channel type -- options: 'left' 'right' 'diff'")
parser.add_argument("-sw2", "--DTMF_plot_freq_type", type=str, default="nominal", help="Choose to use nominal or FFT fitted DTMF frequencies for frequency bin centers -- options: 'nominal' 'fitted'")
parser.add_argument("-sw3", "--DTMF_plot_f_width", type=int, default=12, help="Set the frequency width when calculating the AUC in Hz")
parser.add_argument("-sw4", "--DTMF_plot_window_len", type=int, default=5000, help="Set the N samples width when calculating the AUC")
parser.add_argument("-sw5", "--DTMF_plot_incr", type=int, default=1000, help="Set the size of the increments for the DTMF scan")

parser.add_argument("-dtmf", "--plot_DTMF_scan", action="store_true", help="Plot waveform scan for DTMF saved in .csv file -- Requires the -sw option to have been run to create the .csv file!")
parser.add_argument("-dtmfI", "--plot_DTMF_csv_in", type=str, default=None, help="Set the filepath for the input .csv file")
parser.add_argument("-dtmf1", "--DTMF_plot_type", type=str, default=None, help=textwrap.dedent('''"Display type for DTMF frequencies -- options:\
    \n'f' - Plots the area under the curve (AUC) of DTMF frequencies normalized in both N sample window and frequency window.
    \n'f/2f' - Plots the AUC of DTMF frequencies divided by the 2nd harmonics both normalized in both N sample window and frequency window.
    \n'log_f' - Plots the log of the AUC of DTMF frequencies normalized in both N sample window and frequency window.'''))
parser.add_argument("-dtmf2", "--DTMF_plot_time", action="store_true", default=True, help="Plot DTMF with time in seconds on the x-axis instead of the sample number")
parser.add_argument("-dtmf3", "--DTMF_plot_shift", action="store_true", default=True, help="Plot DTMF with shifted non-DTMF frequencies included")
parser.add_argument("-dtmf4", "--DTMF_plot_maxY", type=int, default=0, help="Set the maximum value on the y-axis when plotting")
parser.add_argument("-dtmf5", "--DTMF_plot_x_win", type=list, default=[], help="Set the min and max value on the x-axis as a list")
parser.add_argument("-dtmf6", "--DTMF_plot_save", type=str, default="", help="Set the save path and file for the DTMF plot")

parser.add_argument("-lrd", "--LRD", type=str, default="left", help="Set channel type for FFT, Cepstrum, and/or Waveform -- options: 'left' 'right' 'diff'")

parser.add_argument("-wav", "--plot_waveform", action="store_true", help="Plot the waveform")
parser.add_argument("-wav1", "--waveform_title", type=str, default="Waveform", help="Set waveform plot title")

parser.add_argument("-fft", "--do_FFT", action="store_true", help="Plot the FFT spectrum")
parser.add_argument("-fit", "--fit_FFT", action="store_true", help="Fit and plot the FFT spectrum")
parser.add_argument("-fftf", "--FFT_input_file", type=str, default="", help="Specify the input .wav file for the FFT")
parser.add_argument("-fft2", "--FFT_title", type=str, default="FFT", help="Set FFT plot title")
parser.add_argument("-fft3", "--fit_FFT_full_range", action="store_true", default=False, help="False plots a windows around the fit, true plots the full FFT range")

parser.add_argument("-c", "--plot_cepstrum", action="store_true", help="Plot the cepstrum of the waveform (see https://en.wikipedia.org/wiki/Cepstrum)")
parser.add_argument("-c1", "--cepstrum_title", type=str, default="Cepstrum", help="Set cepstrum plot title")
parser.add_argument("-c2", "--plot_modified_cepstrum", action="store_true", default=True, help="Plot a modified specturm to easily see peaks")
parser.add_argument("-c3", "--plot_imaginary_cepstrum", action="store_true", default=False, help="Plot the imaginary part of the cepstrum, default is the real part")

args = parser.parse_args()


#================================================#
#                Helper Functions                #
#================================================#
def set_style():
    plt.style.use('dark_background')

def load_wav(wav_file, cuts=[]):
    sample_rate, data = wavfile.read(f"{wav_file}")
    n_channels = data[0].size
    if n_channels == 1:
        data_ch1 = data
    elif n_channels == 2:
        data_ch1 = data[:, 0]
        data_ch2 = data[:, 1]
    elif n_channels > 2:
        print("TOO MANY CHANNELS!!!")
    if len(cuts) == 2:
        data_ch1 = data_ch1[cuts[0]:cuts[1]]
        if n_channels == 2:
            data_ch2 = data_ch2[cuts[0]:cuts[1]]
    data_linspace = np.linspace(1, data_ch1.size, data_ch1.size)
    out_list = [sample_rate, data_linspace, data_ch1]
    if n_channels == 2:
        out_list.append(data_ch2)
    return out_list

def package_wave_data(file_data, LRD):
    sample_rate = file_data[0]
    data_linspace = file_data[1]
    waveform = file_data[2]
    if LRD == "right":
        waveform = file_data[3]
    elif LRD == "diff":
        waveform = [x - y for x, y in zip(file_data[2], file_data[3])]
    return sample_rate, data_linspace, waveform

def zoom_FFT_analysis(pkg_wave_data, LRD, freq, f_width, win_len, incr):
    print(f"Starting ZoomFFT Analysis of DTMF Related Frequency {freq}Hz on {LRD} Waveform")
    data_array = np.array(pkg_wave_data[2])
    n_samples = len(pkg_wave_data[2])
    n_incr = math.floor((n_samples - win_len)/incr) + 1
    zoomFastFourierTransform_f = ZoomFFT(n=win_len, fn=[(freq-f_width), (freq+f_width)], m=win_len, fs=pkg_wave_data[0])
    zoomFastFourierTransform_2f = ZoomFFT(n=win_len, fn=[(2*freq-f_width), (2*freq+f_width)], m=win_len, fs=pkg_wave_data[0])
    f_info = [freq, 2*freq, f_width]
    AUC_f = []
    AUC_2f = []
    for i in range(0, n_incr, 1):
        selected_data_array = data_array[(i*incr):(i*incr+win_len)]
        spectrum_f = np.abs(zoomFastFourierTransform_f(selected_data_array))
        spectrum_2f = np.abs(zoomFastFourierTransform_2f(selected_data_array))
        AUC_f.append(float((np.sum(spectrum_f)/(2*f_width))/win_len))
        AUC_2f.append(float((np.sum(spectrum_2f)/(2*f_width))/win_len))
    return AUC_f, AUC_2f, f_info

def write_zoom_FFT_analyses_to_file(file, LRD, f_type, freqs, f_width, win_len, incr):
    wave_file = load_wav(file)
    pkg_wave_data = package_wave_data(wave_file, LRD)
    n_samples = len(pkg_wave_data[2])
    n_incr = math.floor((n_samples - win_len)/incr) + 1
    metadata = [pkg_wave_data[0], win_len, incr, n_incr, LRD, f_type]
    f_metadata = []
    with open(f"zoomFFT {file[:-4]} channel={LRD} f_type={f_type} f_width={f_width} winlen={win_len} incr={incr}.csv", "w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(metadata)
        for i in range(len(freqs)):
            AUC_f, AUC_2f, f_info = zoom_FFT_analysis(pkg_wave_data, LRD, freqs[i], f_width, win_len, incr)
            f_metadata.extend(f_info)
            writer.writerow(AUC_f)
            writer.writerow(AUC_2f)
        writer.writerow(f_metadata)

def get_label_info(f_type, plt_shft=False):
    if f_type == "nominal":
        color_names = ["red", "orange", "yellow", "lawngreen", "blue", "cyan", "blueviolet", "magenta"]
        label_names = ["Nominal DTMF = 697 [Hz]", "Nominal DTMF = 770 [Hz]", "Nominal DTMF = 852 [Hz]", "Nominal DTMF = 941 [Hz]", 
                        "Nominal DTMF = 1209 [Hz]", "Nominal DTMF = 1336 [Hz]", "Nominal DTMF = 1477 [Hz]", "Nominal DTMF = 1633 [Hz]"]
        this_linestyle = "-"
    if f_type == "fitted":
        color_names = ["red", "orange", "yellow", "lawngreen", "blue", "cyan", "blueviolet", "magenta"]
        label_names = ["Fitted DTMF = 697 [Hz]", "Fitted DTMF = 770 [Hz]", "Fitted DTMF = 852 [Hz]", "Fitted DTMF = 941 [Hz]", 
                        "Fitted DTMF = 1209 [Hz]", "Fitted DTMF = 1336 [Hz]", "Fitted DTMF = 1477 [Hz]", "Fitted DTMF = 1633 [Hz]"]
        this_linestyle = "-"
    if plt_shft:
        color_names = ["white", "palegreen"]
        label_names = ["Shifted DTMF = ~655 [Hz]", "Shifted DTMF = ~1142 [Hz]"]
        this_linestyle = "--"
    return label_names, color_names, this_linestyle

def get_title_info(plt_type, axs, LRD, win_len, incr, f_width, time):
    if plt_type == "f":
        axs.set_title(f"{LRD} Waveform | FFT Scan of Normalized AUC of DTMF Frequency Magnitudes")
        axs.set_ylabel(f"Normalized AUC of DTMF Magnitudes with Width {f_width}Hz\nBinning of {win_len} Samples with Incrementing {incr}")
    if plt_type == "f/2f":
        axs.set_title(f"{LRD} Waveform | FFT Scan of Normalized AUC of DTMF Frequency Magnitudes over\nNormalized AUC of DTMF 2nd Harmonic Magnitudes")
        axs.set_ylabel(f"Normalized AUC of DTMF Magnitudes over\nNormalized AUC of DTMF 2nd Harmonic Magnitudes with Width {f_width}Hz\nBinning of {win_len} Samples with Incrementing {incr}")
    if plt_type == "log_f":
        axs.set_title(f"{LRD} Waveform | FFT Scan of log(Normalized AUC of DTMF Frequency Magnitudes)")
        axs.set_ylabel(f"log(Normalized AUC of DTMF Magnitudes) with Width {f_width}Hz\nBinning of {win_len} Samples with Incrementing {incr}")
    if time:
        axs.set_xlabel("Time at the Start the Bin Window [s]")
    else:
        axs.set_xlabel("Waveform Sample Number at the Start the Bin Window")

def modify_plot_window(axs, max_str, x_win, time, sample_rate, win_len, incr, n_incr):
    if max_str != 0:
        axs.set_ylim(0, max_str)
    if len(x_win) == 2:
        if time:
            axs.set_xlim((x_win[0]/(n_incr*win_len))*(incr*(n_incr - 1)/sample_rate), (x_win[1]/(n_incr*win_len))*(incr*(n_incr - 1)/sample_rate))
        else:
            axs.set_xlim(x_win[0], x_win[1])

def plot_array_with_f_type(i, j, axs, linspace, csv_data, plt_type, color_names, label_names, this_linestyle):
    if plt_type == "f":
        axs.plot(linspace, np.array(csv_data[j+(2*i)], dtype=float), color=color_names[i], label=label_names[i], linestyle=this_linestyle)
        axs.fill_between(linspace, np.array(csv_data[j+(2*i)], dtype=float), color=color_names[i], alpha=0.25)
    if plt_type == "f/2f":
        axs.plot(linspace, np.array(csv_data[j+(2*i)], dtype=float)/np.array(csv_data[j+1+(2*i)], dtype=float), color=color_names[i], label=label_names[i], linestyle=this_linestyle)
        axs.fill_between(linspace, np.array(csv_data[j+(2*i)], dtype=float)/np.array(csv_data[j+1+(2*i)], dtype=float), color=color_names[i], alpha=0.25)
    if plt_type == "log_f":
        arr = np.log(np.array(csv_data[j+(2*i)], dtype=float))
        arr[arr < 0] = 0
        axs.plot(linspace, arr, color=color_names[i], label=label_names[i], linestyle=this_linestyle)
        axs.fill_between(linspace, arr, color=color_names[i], alpha=0.25)


#================================================#
#                  Fit Functions                 #
#================================================#
def gauss_2(x, a_1, x0_1, s_1, a_2, x0_2, s_2):
    return a_1*np.exp(-(x-x0_1)**2/(2*s_1**2)) + a_2*np.exp(-(x-x0_2)**2/(2*s_2**2))

def gauss_8(x, a_1, x0_1, s_1, a_2, x0_2, s_2, a_3, x0_3, s_3, a_4, x0_4, s_4, a_5, x0_5, s_5, a_6, x0_6, s_6, a_7, x0_7, s_7, a_8, x0_8, s_8):
    return a_1*np.exp(-(x-x0_1)**2/(2*s_1**2)) + a_2*np.exp(-(x-x0_2)**2/(2*s_2**2)) + a_3*np.exp(-(x-x0_3)**2/(2*s_3**2)) + a_4*np.exp(-(x-x0_4)**2/(2*s_4**2))+ a_5*np.exp(-(x-x0_5)**2/(2*s_5**2)) + a_6*np.exp(-(x-x0_6)**2/(2*s_6**2)) + a_7*np.exp(-(x-x0_7)**2/(2*s_7**2)) + a_8*np.exp(-(x-x0_8)**2/(2*s_8**2))

def gauss_10_c(x, a_0, a_1, x0_1, s_1, a_2, x0_2, s_2, a_3, x0_3, s_3, a_4, x0_4, s_4, a_5, x0_5, s_5, a_6, x0_6, s_6, a_7, x0_7, s_7, a_8, x0_8, s_8, a_9, x0_9, s_9, a_10, x0_10, s_10):
    return a_0 + a_1*np.exp(-(x-x0_1)**2/(2*s_1**2)) + a_2*np.exp(-(x-x0_2)**2/(2*s_2**2)) + a_3*np.exp(-(x-x0_3)**2/(2*s_3**2)) + a_4*np.exp(-(x-x0_4)**2/(2*s_4**2))+ a_5*np.exp(-(x-x0_5)**2/(2*s_5**2)) + a_6*np.exp(-(x-x0_6)**2/(2*s_6**2)) + a_7*np.exp(-(x-x0_7)**2/(2*s_7**2)) + a_8*np.exp(-(x-x0_8)**2/(2*s_8**2)) + a_9*np.exp(-(x-x0_9)**2/(2*s_9**2)) + a_10*np.exp(-(x-x0_10)**2/(2*s_10**2))


#================================================#
#               Plotting Functions               #
#================================================#
def plot_waveform(wave1, wave1_linspace, title, show=True, save_path=""):
    fig, axs = plt.subplots(1, 1, figsize=(12, 6), tight_layout=True)
    axs.plot(wave1_linspace, wave1, color="blue")
    axs.axhline(0, color='w', linestyle='-', linewidth=1)
    axs.set_title(title)
    axs.set_ylabel('Amplitude')
    axs.set_xlabel('Sample Index (Wav Data Point)')
    if save_path == "":
        print("Not saving plot")
    else:
        plt.savefig(f"{save_path}.png")
    if show:
        plt.show()

def plot_FFT(wave, sample_rate, title, show=True):
    data = np.array(wave)
    if len(data.shape) > 1:
        data = data[:, 0]
    data = data / np.max(np.abs(data))
    n = len(data)
    spectrum = np.fft.fft(data)
    freqs = np.fft.fftfreq(n, 1/sample_rate)
    magnitudes = np.abs(spectrum)
    plt.plot(freqs[:n//2], magnitudes[:n//2])
    plt.title(title)
    plt.xlabel('Frequency (Hz)')
    plt.ylabel('Magnitude')
    if show:
        plt.show()
    return [freqs, magnitudes]

def fit_FFT(wave, sample_rate, title, full_range=False, show=True, save_path=""):
    data = np.array(wave)
    if len(data.shape) > 1:
        data = data[:, 0]
    data = data / np.max(np.abs(data))
    n = len(data)
    spectrum = np.fft.fft(data)
    freqs = np.fft.fftfreq(n, 1/sample_rate)
    magnitudes = np.abs(spectrum)
    freqs_full = freqs
    magnitudes_full = magnitudes

    if full_range == False:
        mask = (freqs >= 450) & (freqs <= 1900)
        freqs = freqs[mask]
        magnitudes = magnitudes[mask]

    DMFT_1633 = [1200.0, 1633.0, 5.0]
    DMFT_1477 = [1200.0, 1477.0, 5.0]
    DMFT_1336 = [1200.0, 1336.0, 5.0]
    DMFT_1209 = [1200.0, 1209.0, 5.0]
    DMFT_941 = [1200.0, 941.0, 5.0]
    DMFT_852 = [1200.0, 852.0, 5.0]
    DMFT_770 = [1200.0, 770.0, 5.0]
    DMFT_697 = [1200.0, 697.0, 5.0]
    BKG_1142 = [50.0, 1140.0, 5.0]
    BKG_655 = [50.0, 655.0, 5.0]
    params_DTMF = [10, 
                   DMFT_1633[0], DMFT_1633[1], DMFT_1633[2], 
                   DMFT_1477[0], DMFT_1477[1], DMFT_1477[2], 
                   DMFT_1336[0], DMFT_1336[1], DMFT_1336[2], 
                   DMFT_1209[0], DMFT_1209[1], DMFT_1209[2], 
                   DMFT_941[0], DMFT_941[1], DMFT_941[2], 
                   DMFT_852[0], DMFT_852[1], DMFT_852[2], 
                   DMFT_770[0], DMFT_770[1], DMFT_770[2], 
                   DMFT_697[0], DMFT_697[1], DMFT_697[2],
                   BKG_1142[0], BKG_1142[1], BKG_1142[2],
                   BKG_655[0], BKG_655[1], BKG_655[2]]
    bounds_low_DTMF = [0, 0, 1555, 0, 0, 1406.5, 0, 0, 1272.5, 0, 0, 1145.5, 0, 0, 896.5, 0, 0, 811, 0, 0, 733.5, 0, 0, 660.5, 0, 0, 1100, 0, 0, 634, 0]
    bounds_high_DTMF = [100, math.inf, 1711, 25, math.inf, 1555, 25, math.inf, 1406.5, 25, math.inf, 1272.5, 25, math.inf, 985.5, 25, math.inf, 896.5, 25, math.inf, 811, 25, math.inf, 733.5, 25, math.inf, 1180, 25, math.inf, 676, 25]
    popt_DTMF, pcov_DTMF = curve_fit(gauss_10_c, freqs, magnitudes, p0 = params_DTMF, bounds=(bounds_low_DTMF,bounds_high_DTMF))
    perr_DTMF = np.sqrt(np.diag(pcov_DTMF))
    nSigma_DTMF = []
    for i in range(math.floor(len(popt_DTMF)/3)):
        value = popt_DTMF[3*i + 1]/perr_DTMF[3*i + 1]
        if(popt_DTMF[3*i + 1] < 1.0):
            value = "Norm < 1.0"
        elif(perr_DTMF[3*i + 1] < .001):
            value = "Err < .001"
        nSigma_DTMF.append(value)
    DMFT_fit_ev = ["1633", "1477", "1336", "1209", "941", "852", "770", "697", "BKG 1142", "BKG 655"]
    print(f"=======================  {title} - Fit Results  =======================")
    print("  DMFT [Hz]  |       Mean [Hz]      |   Stddev [Hz]   |    Normalization    |   N sigma   |")
    print("-------------+----------------------+-----------------+---------------------+-------------+")
    for i in range(len(DMFT_fit_ev)):
        if (i+1) == 9:
            print("-------------+----------------------+-----------------+---------------------+-------------+")
        tone = str(DMFT_fit_ev[i])
        for j in range((8-len(tone))):
            tone = " " + tone
        mean = "{:.3f}".format(popt_DTMF[int(3*i + 2)])
        mean_err = "{:.3f}".format(perr_DTMF[int(3*i + 2)])
        if perr_DTMF[int(3*i + 2)] >= 10000:
            mean_err = "{:.0f}".format(perr_DTMF[int(3*i + 2)])
        mean_info = mean + " \u00B1 " + mean_err
        for j in range((20-len(mean_info))):
            mean_info = mean_info + " "
        stddev = "{:.3f}".format(popt_DTMF[int(3*i + 3)])
        stddev_err = "{:.3f}".format(perr_DTMF[int(3*i + 3)])
        if perr_DTMF[int(3*i + 3)] >= 10000:
            stddev_err = "{:.0f}".format(perr_DTMF[int(3*i + 3)])
        stddev_info = stddev + " \u00B1 " + stddev_err
        for j in range((15-len(stddev_info))):
            stddev_info = stddev_info + " "
        norm = "{:.3f}".format(popt_DTMF[int(3*i + 1)])
        norm_err = "{:.3f}".format(perr_DTMF[int(3*i + 1)])
        if perr_DTMF[int(3*i + 1)] >= 10000:
            norm_err = "{:.0f}".format(perr_DTMF[int(3*i + 1)])
        norm_info = norm + " \u00B1 " + norm_err
        for j in range((19-len(norm_info))):
            norm_info = norm_info + " "
        nSigma_str = ""
        if isinstance(nSigma_DTMF[i], str):
            nSigma_str = nSigma_DTMF[i] + " "
        else:
            nSigma_str = "{:.3f}".format(nSigma_DTMF[i])
            for j in range((11-len(nSigma_str))):
                nSigma_str = nSigma_str + " "
        print(f"    {tone} |  {mean_info}|  {stddev_info}|  {norm_info}|  {nSigma_str}|")
    print("-------------+----------------------+-----------------+---------------------+-------------+")
    print(f"   Constant  |  {"{:.3f}".format(popt_DTMF[0])} \u00B1 {"{:.3f}".format(perr_DTMF[0])}")
    print("-------------+----------------------+-----------------+---------------------+-------------+")

    fig, axs = plt.subplots(1, 1, figsize=(12, 6), tight_layout=True)
    axs.plot(freqs[:n//2],magnitudes[:n//2], color="blue", label="Fast Fourier Transform")
    popt_DTMF_sig = popt_DTMF[1:25]
    popt_DTMF_bkg = popt_DTMF[25:]
    axs.plot(freqs[:n//2],(gauss_2(freqs, *popt_DTMF_bkg)[:n//2])/2, color="limegreen", label="Shifted Peaks at 1/2 Amplitude")
    axs.plot(freqs[:n//2],(gauss_8(freqs, *popt_DTMF_sig)[:n//2])/2, color="orange", label="DTMF Peaks at 1/2 Amplitude")
    axs.plot(freqs[:n//2],gauss_10_c(freqs, *popt_DTMF)[:n//2], color="red", label="Fit Result (All Peaks + Const Background)")
    axs.set_title(f"{title} - DTMF Fit by Gaussians")
    axs.set_ylabel('FFT Amplitude')
    axs.set_xlabel('Frequency [Hz]')
    
    axs.axvline(1644, color='w', linestyle='--', linewidth=1)
    axs.axvline(1652, color='yellow', linestyle='--', linewidth=1)
    axs.axvline(1636, color='yellow', linestyle='--', linewidth=1)
    
    axs.axvline(1642, color='yellow', linestyle='--', linewidth=1)
    axs.axvline(1624, color='yellow', linestyle='--', linewidth=1)
    axs.axvline(1486, color='yellow', linestyle='--', linewidth=1)
    axs.axvline(1468, color='yellow', linestyle='--', linewidth=1)
    axs.axvline(1345, color='yellow', linestyle='--', linewidth=1)
    axs.axvline(1327, color='yellow', linestyle='--', linewidth=1)
    axs.axvline(1218, color='yellow', linestyle='--', linewidth=1)
    axs.axvline(1200, color='yellow', linestyle='--', linewidth=1)

    axs.axvline(1633, color='w', linestyle='--', linewidth=1)
    axs.axvline(1477, color='w', linestyle='--', linewidth=1)
    axs.axvline(1336, color='w', linestyle='--', linewidth=1)
    axs.axvline(1209, color='w', linestyle='--', linewidth=1)
    axs.axvline(941, color='w', linestyle='--', linewidth=1)
    axs.axvline(852, color='w', linestyle='--', linewidth=1)
    axs.axvline(770, color='w', linestyle='--', linewidth=1)
    axs.axvline(697, color='w', linestyle='--', linewidth=1)

    plt.legend()
    if save_path != "":
        plt.savefig(f"{save_path}.png")
    if show:
        plt.show()

    ret_list = [freqs_full, magnitudes_full]
    if full_range == False:
        ret_list.append(freqs)
        ret_list.append(magnitudes)
    return ret_list

def plot_cepstrum(wave, title, show=True, modify=True, do_imag=False):
    spectrum = np.fft.fft(wave)
    if modify == False:
        cepstrum = np.fft.ifft(np.log(np.abs(spectrum)**2))
        real_cepstrum = np.real(cepstrum)
        imag_cepstrum = np.imag(cepstrum)
    else:
        cepstrum = np.fft.ifft(np.abs(spectrum))
        real_cepstrum = np.real(np.pow(cepstrum, .4))
        imag_cepstrum = np.imag(cepstrum)
    mod_title = ""
    if modify:
        mod_title = "Modified "
    if do_imag:
        fig, axs = plt.subplots(1, 2, figsize=(8, 8), tight_layout=True)
        axs[0].plot(real_cepstrum)
        axs[0].set_title(f"{title} - {mod_title}Cepstrum [Real Component]")
        axs[0].set_ylabel('Amplitude')
        if modify:
            axs[0].set_ylabel('Amplitude^(2/5)')
        axs[0].set_xlabel('Quefrequency')
        axs[1].plot(imag_cepstrum)
        axs[1].set_title(f"{title} - {mod_title}Cepstrum [Imaginary Component]")
        axs[1].set_ylabel('Amplitude')
        axs[1].set_xlabel('Quefrequency')
        if show:
            plt.show()
    else:
        fig, axs = plt.subplots(1, 1, figsize=(8, 8), tight_layout=True)
        axs.plot(real_cepstrum)
        axs.set_title(f"{title} - {mod_title}Cepstrum [Real Component]")
        axs.set_ylabel('Amplitude')
        if modify:
            axs.set_ylabel('Amplitude^(2/5)')
        axs.set_xlabel('Quefrequency')
        if show:
            plt.show()

def plot_zoom_FFT_analyses_from_file(csv_file, plt_type="f", time=False, plt_shft=True, max_str=0, x_win=[], save=False, save_path=""):
    with open(f"{csv_file}", mode='r', newline='') as file:
        reader = csv.reader(file)
        csv_data = list(reader)
        sample_rate = int(csv_data[0][0])
        win_len = int(csv_data[0][1])
        incr = int(csv_data[0][2])
        n_incr = int(csv_data[0][3])
        LRD = csv_data[0][4]
        f_type = csv_data[0][5]
        f_width = int(csv_data[-1][2])
        linspace = np.linspace(1, n_incr*win_len, n_incr)
        if time:
            linspace = np.linspace(0, incr*(n_incr - 1)/sample_rate, n_incr)
        fig, axs = plt.subplots(1, 1, figsize=(12, 6), tight_layout=True)
        label_names, color_names, this_linestyle = get_label_info(f_type)
        for i in range(len(label_names)):
            plot_array_with_f_type(i, 1, axs, linspace, csv_data, plt_type, color_names, label_names, this_linestyle)
        if plt_shft:
            label_names, color_names, this_linestyle = get_label_info(f_type, plt_shft)
            for i in range(len(label_names)):
                plot_array_with_f_type(i, 17, axs, linspace, csv_data, plt_type, color_names, label_names, this_linestyle)
        get_title_info(plt_type, axs, LRD, win_len, incr, f_width, time)
        modify_plot_window(axs, max_str, x_win, time, sample_rate, win_len, incr, n_incr)
        plt.legend()
        if save and (len(x_win) == 0 or len(x_win) == 2):
            file_name = f"{csv_file[:-4]}"
            if time:
                file_name = file_name + " timeAxis"
            if max_str != 0:
                file_name = file_name + f" y_max={max_str}"
            if len(x_win) == 2:
                file_name = file_name + f" {x_win[0]}_x_win_{x_win[1]}"
            plt.savefig(f"{save_path}.png")
        plt.show()


#================================================#
#                      Main                      #
#================================================#
if args.scan_DTMF_write:
    if args.scan_DTMF_write_file_in == None or args.scan_DTMF_write_file_out == None:
        print("The .wav file was not specified!")
        quit()
    freqs = []
    bin_centers = [697, 770, 852, 941, 1209, 1336, 1477, 1633]
    fitted_bin_centers = [699.35, 771.64, 852, 936.69, 1211.19, 1331.73, 1471.50, 1644.39]
    drifted_tone_centers = [655.20, 1142.46]
    if args.DTMF_plot_freq_type == "nominal":
        freqs.extend(bin_centers)
    elif args.DTMF_plot_freq_type == "fitted":
        freqs.extend(fitted_bin_centers)
    if args.DTMF_plot_shift:
        freqs.extend(drifted_tone_centers)
    write_zoom_FFT_analyses_to_file(args.scan_DTMF_write_file_in, args.DTMF_plot_LRD, args.DTMF_plot_type, 
                                    freqs, args.DTMF_plot_f_width, args.DTMF_plot_window_len, args.DTMF_plot_incr)

if args.plot_DTMF_scan:
    save_DTMF_plot = True
    if args.DTMF_plot_save != "":
        save_DTMF_plot = False
    plot_zoom_FFT_analyses_from_file(args.plot_DTMF_csv_in, args.DTMF_plot_type, args.DTMF_plot_time, args.DTMF_plot_shift, 
                                     args.DTMF_plot_maxY, args.DTMF_plot_x_win, save_DTMF_plot, args.DTMF_plot_save)

if args.do_FFT or args.fit_FFT or args.plot_cepstrum:
    if args.FFT_input_file == "":
        print("The .wav file was not specified!")
        quit()
    wav_data = load_wav(args.FFT_input_file)
    data, linspace, sample_rate = package_wave_data(wav_data, args.LRD)

    if args.plot_waveform:
        plot_waveform(data, linspace, args.waveform_title)
    
    if args.do_FFT:
        plot_FFT(data, sample_rate, args.FFT_title)
    
    if args.fit_FFT:
        fit_FFT(data, sample_rate, args.FFT_title, args.fit_FFT_full_range)
    
    if args.plot_cepstrum:
        title_additions = ""
        if args.plot_modified_cepstrum:
            title_additions = title_additions + " [Modified Cepstrum]"
        if args.plot_imaginary_cepstrum:
            title_additions = title_additions + " [Imaginary Cepstrum]"
        plot_cepstrum(data, args.cepstrum_title, modify=(args.plot_modified_cepstrum+title_additions), do_imag=args.plot_imaginary_cepstrum)




