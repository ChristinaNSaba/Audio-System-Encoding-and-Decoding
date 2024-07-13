#Joud Hijaz 1200342
#Pierre Backleh 1201296
#Christina Saba 1201255

# phase2

# Importing necessary libraries
from tkinter import *
from tkinter import filedialog
import numpy as np
import scipy.io.wavfile as wav
from scipy.fft import fft
from scipy.signal import butter, lfilter
from scipy.signal import find_peaks

# Dictionary to map characters to their respective frequency sets
arr = np.array([])
CHARACTER_FREQUENCIES = {
# Character: (Low frequency, Middle frequency, High frequency)
    'a': (100, 1100, 2500),
    'b': (100, 1100, 3000),
    'c': (100, 1100, 3500),
    'd': (100, 1300, 2500),
    'e': (100, 1300, 3000),
    'f': (100, 1300, 3500),
    'g': (100, 1500, 2500),
    'h': (100, 1500, 3000),
    'i': (100, 1500, 3500),
    'j': (300, 1100, 2500),
    'k': (300, 1100, 3000),
    'l': (300, 1100, 3500),
    'm': (300, 1300, 2500),
    'n': (300, 1300, 3000),
    'o': (300, 1300, 3500),
    'p': (300, 1500, 2500),
    'q': (300, 1500, 3000),
    'r': (300, 1500, 3500),
    's': (500, 1100, 2500),
    't': (500, 1100, 3000),
    'u': (500, 1100, 3500),
    'v': (500, 1300, 2500),
    'w': (500, 1300, 3000),
    'x': (500, 1300, 3500),
    'y': (500, 1500, 2500),
    'z': (500, 1500, 3000),
    ' ': (500, 1500, 3500)  # Space character
}

# Global variable to hold the file path
global file_path
file_path = None

def uploadAudio():
    # Function to upload an audio file
    global file_path
    file_path = filedialog.askopenfilename(filetypes=[("WAV files", "*.wav")])
    if file_path:
        print("Selected file:", file_path)

def decodingFFT(filePath):
    # Read the WAV file
    rate, data = wav.read(filePath)
    if data.ndim > 1:
        data = data[:, 0]  # If stereo, just use one channel

    # The duration of each character in samples
    char_duration_samples = int(rate * 0.04)  # 40ms of samples

    # Split the signal into 40ms chunks
    chunks = [data[i:i + char_duration_samples] for i in range(0, len(data), char_duration_samples)]

    decoded_text = ''

    for chunk in chunks:
        global arr
        # Apply Fourier Transform to each chunk
        yf = fft(chunk)
        # Get the absolute values of the frequencies
        spectrum = np.abs(yf[:len(yf) // 2])
        # Determine a threshold for peak height dynamically based on the max amplitude
        threshold = np.max(spectrum) * 0.5  # Adjust the multiplier as needed

        # Find peaks to determine the three main frequencies
        peaks, _ = find_peaks(spectrum, height=threshold)

        # Get the frequencies corresponding to the peaks
        freqs = peaks * rate / len(chunk)
        arr = np.append(arr, freqs)

        # Decode the character based on the frequency peaks

        # Check if we found at least three peaks, which we need for a valid character encoding
        if len(freqs) < 3:
            continue  # Skip this chunk as it doesn't contain enough frequency components

        for char, freq_set in CHARACTER_FREQUENCIES.items():
            if len(freqs) == 0:
                continue  # No frequencies found, move to the next chunk

    for i in range(0, len(arr)):
        for char in CHARACTER_FREQUENCIES.keys():
            if (CHARACTER_FREQUENCIES[char][0] == arr[i] and
                    CHARACTER_FREQUENCIES[char][1] == arr[i+1] and
                    CHARACTER_FREQUENCIES[char][2] == arr[i+2]):
                decoded_text += char
    return decoded_text

# Bandpass Filters analysis
def rms(signal):
    # Calculate the root mean square of the signal
    return np.sqrt(np.mean(signal ** 2))

def bandpass_filter(signal, sample_rate, frequencies):
    """
    Apply bandpass filters to the signal for each frequency.

    Args:
        signal (numpy.ndarray): The audio signal.
        sample_rate (int): The sample rate of the audio signal.
        frequencies (list): List of frequencies to filter around.

    Returns:
        numpy.ndarray: Array of filtered signals for each frequency.
    """
    filtered_signals = []

    for center_freq in frequencies:
        # Define the frequency range for the bandpass filter
        lowcut = center_freq - 50  # Lower bound of the frequency range
        highcut = center_freq + 50  # Upper bound of the frequency range

        # Normalize the frequencies
        nyquist = 0.5 * sample_rate
        low = lowcut / nyquist
        high = highcut / nyquist

        # Design the bandpass filter
        b, a = butter(N=5, Wn=[low, high], btype='band')

        # Apply the filter
        filtered_signal = lfilter(b, a, signal)
        filtered_signals.append(filtered_signal)

    return filtered_signals
def decode_filtered_signals(filePath, character_frequencies):
    # Read the WAV file
    rate, data = wav.read(filePath)
    if data.ndim > 1:
        data = data[:, 0]  # If stereo, just use one channel

    # Set chunk_length for 40ms of samples
    chunk_length = int(rate * 0.04)

    # Apply the bandpass filters
    frequencies = list(set(f for freqs in character_frequencies.values() for f in freqs))
    filtered_signals = bandpass_filter(data, rate, frequencies)

    decoded_text = ''

    # Iterate over each character frequency set
    for chunk_start in range(0, len(data), chunk_length):
        chunk = data[chunk_start:chunk_start + chunk_length]
        char_rms_values = {}

        for char, freq_set in character_frequencies.items():
            char_rms = 0
            for freq in freq_set:
                index = frequencies.index(freq)
                signal_rms = rms(filtered_signals[index][chunk_start:chunk_start + chunk_length])
                char_rms += signal_rms
            char_rms_values[char] = char_rms

        # Find the character with the highest combined RMS value
        detected_char = max(char_rms_values, key=char_rms_values.get)
        if char_rms_values[detected_char] > 0:  # You might need to adjust this condition
            decoded_text += detected_char

    return decoded_text


def display_FFT_result(result):
    fftResultText.delete(1.0, END)
    fftResultText.insert(END, result)
def display_filter_result(result):
    filterResultText.delete(1.0, END)
    filterResultText.insert(END, result)



def on_fft_button_click():
    global file_path
    if file_path:
        decoded_text = decodingFFT(file_path)
        display_FFT_result(decoded_text)
    else:
        print("Please upload an audio file first.")

def on_bandpass_button_click():
    global file_path
    if file_path:
        decoded_text = decode_filtered_signals(file_path, CHARACTER_FREQUENCIES)
        display_filter_result(decoded_text)
    else:
        print("Please upload an audio file first.")

def restart():
    global file_path
    file_path = None  # Reset the file_path to None

    # Clear the contents of the text widgets
    fftResultText.delete(1.0, END)
    filterResultText.delete(1.0, END)

    print("Restarted: Everything has been cleared.")


root = Tk()
root.title("DSP project")
root.geometry("850x450+220+120")
root.resizable(False, False)
root.configure(bg="#3776ab")

# Load images
iconImg1 = PhotoImage(file="mainLogo2.png")  # Make sure the file paths are correct
Logo = PhotoImage(file="logo1.png")          # Make sure the file paths are correct

# Set window icon and header logo
root.iconphoto(False, iconImg1)

# Header Frame with Logo and Title
header_frame = Frame(root, bg="white", width=850, height=100)
header_frame.place(x=0, y=0)
Label(header_frame, image=Logo, bg="white").place(x=50, y=25)
Label(header_frame, text="EchoAlphaEncoder", font="Helvetica 18 bold", bg="white", fg="#333").place(x=150, y=35)

# Text Boxes for Results
fftResultLabel = Label(root, text="FFT Result", font="arial 14", bg="#3776ab")
fftResultLabel.place(x=50, y=120)
fftResultText= Text(root, font="arial 14", bg="white", relief=GROOVE, wrap=WORD)
fftResultText.place(x=50, y=150, width=350, height=60)

filterResultLabel = Label(root, text="Filter Result", font="arial 14", bg="#3776ab")
filterResultLabel.place(x=50, y=270)
filterResultText = Text(root, font="arial 14", bg="white", relief=GROOVE, wrap=WORD)
filterResultText.place(x=50, y=300, width=350, height=60)



# Buttons
button_upload = Button(root, text="Upload Audio", width=20, font="arial 12", command=uploadAudio)
button_upload.place(x=640, y=110)

button_fft = Button(root, text="Generate Signal with Frequency Analysis", width=40, font="arial 12", command=on_fft_button_click)
button_fft.place(x=450, y=180)

button_bandpass = Button(root, text="Generate Signal with Bandpass Filter", width=40, font="arial 12", command=on_bandpass_button_click)
button_bandpass.place(x=450, y=250)

button_restart = Button(root, text="Restart", width=20, font="arial 12", command=restart)
button_restart.place(x=640, y=320)

root.mainloop()
