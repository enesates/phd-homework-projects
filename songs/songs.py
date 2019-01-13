import numpy as np
import librosa
from ann import ANN
from kmeans import KMeans
import sys

ann = ANN()
kmeans = KMeans()
trainPath = "music/train/"
testPath = "music/test/"
numberOfTrainFile = 8
numberOfTestFile = 2
trainFileNames = []
testFileNames = []


# HELPER CLASSES
class Genre:
    CLASSICAL = "classical"
    METAL = "metal"
    POP = "pop"
    ROCK = "rock"

genres = [Genre.CLASSICAL, Genre.METAL, Genre.POP, Genre.ROCK]


class Track:
    """
        y : np.ndarray [shape=(n,) or (2, n)]
            audio time series
        sr : number > 0 [scalar]
            sampling rate of `y`
    """

    def __init__(self, filename, y, sr, trainValue=0, type=None):
        self.filename = filename
        self.type = type
        self.y = y
        self.sr = sr
        self.features = []  # tempo
        self.trainValue = trainValue


# HELPER FUNCTIONS
def load_track(filename):
    y, sr = librosa.load(filename, sr=44100, offset=60.0, duration=30.0)
    return y, sr


def get_tracks(directory, path, fileNames, limit=None):
    allTracks = []

    for i, d in enumerate(directory):
        fileList = librosa.util.find_files(path + d, limit=limit)
        tracks = []
        for filename in fileList:
            fileNames.append(filename)
            sys.stdout.flush()
            y, sr = load_track(filename)
            sys.stdout.flush()

            track = Track(filename, y, sr, i, d)
            tracks.append(track)

        allTracks.append(tracks)

    return allTracks


# FEATURE EXTRACTION
def extract_features(track):
    tempo = ft_tempo(track.y, track.sr)
    mfcc_mean, mfcc_max, mfcc_min, mfcc_std = ft_mfcc(track.y, track.sr)
    chroma_mean, chroma_max, chroma_min, chroma_std = ft_chroma(track.y, track.sr)
    mel_mean, mel_max, mel_min, mel_std = ft_melspectrogram(track.y, track.sr)
    rmse_mean, rmse_max, rmse_min, rmse_std = ft_rmse(track.y)
    sc_mean, sc_max, sc_min, sc_std = ft_spectral_centroid(track.y, track.sr)
    poly_mean, poly_max, poly_min, poly_std = ft_poly_features(track.y, track.sr)
    tonnetz_mean, tonnetz_max, tonnetz_min, tonnetz_std = ft_tonnetz(track.y, track.sr)
    zcr_mean, zcr_max, zcr_min, zcr_std = ft_zero_crossing_rate(track.y)

    features = [tempo, mfcc_mean, mfcc_std,
                chroma_mean, chroma_std,
                mel_mean, mel_std,
                rmse_mean, rmse_std,
                sc_mean, sc_std,
                poly_mean, poly_std,
                tonnetz_mean, tonnetz_std,
                zcr_mean, zcr_std]

    return features


def ft_tempo(y, sr):
    # Estimate the tempo (beats per minute) from an onset envelope
    onset_env = librosa.onset.onset_strength(y, sr=sr)
    tempo = librosa.beat.estimate_tempo(onset_env, sr=sr)

    return tempo


def ft_mfcc(y, sr):
    # Mel-frequency cepstral coefficients
    mfcc = librosa.feature.mfcc(y=y, sr=sr)
    mean, mx, mn, std = np.mean(mfcc), np.max(mfcc), np.min(mfcc), np.std(mfcc)
    return mean, mx, mn, std


def ft_chroma(y, sr):
    # Compute a chromagram from a waveform or power spectrogram.
    chroma = librosa.feature.chroma_stft(y=y, sr=sr)
    mean, mx, mn, std = np.mean(chroma), np.max(chroma), np.min(chroma), np.std(chroma)
    return mean, mx, mn, std


def ft_melspectrogram(y, sr):
    # Compute a Mel-scaled power spectrogram.
    melspectrogram = librosa.feature.melspectrogram(y=y, sr=sr)
    mean, mx, mn, std = np.mean(melspectrogram), np.max(melspectrogram), np.min(melspectrogram), np.std(melspectrogram)
    return mean, mx, mn, std


def ft_rmse(y):
    # Compute root-mean-square (RMS) energy for each frame.
    rmse = librosa.feature.rmse(y=y)
    mean, mx, mn, std = np.mean(rmse), np.max(rmse), np.min(rmse), np.std(rmse)
    return mean, mx, mn, std


def ft_spectral_centroid(y, sr):
    # Compute the spectral centroid.
    centroid = librosa.feature.spectral_centroid(y=y, sr=sr)
    mean, mx, mn, std = np.mean(centroid), np.max(centroid), np.min(centroid), np.std(centroid)
    return mean, mx, mn, std


def ft_poly_features(y, sr):
    # Get coefficients of fitting an nth-order polynomial to the columns of a spectrogram.
    S = np.abs(librosa.stft(y))
    poly = librosa.feature.poly_features(S=S, sr=sr)
    mean, mx, mn, std = np.mean(poly), np.max(poly), np.min(poly), np.std(poly)
    return mean, mx, mn, std


def ft_tonnetz(y, sr):
    # Computes the tonal centroid features (tonnetz), following the method of [R16].
    y = librosa.effects.harmonic(y)
    tonnetz = librosa.feature.tonnetz(y=y, sr=sr)
    mean, mx, mn, std = np.mean(tonnetz), np.max(tonnetz), np.min(tonnetz), np.std(tonnetz)
    return mean, mx, mn, std


def ft_zero_crossing_rate(y):
    # Compute the zero-crossing rate of an audio time series.
    zcr = librosa.feature.zero_crossing_rate(y=y)
    mean, mx, mn, std = np.mean(zcr), np.max(zcr), np.min(zcr), np.std(zcr)
    return mean, mx, mn, std


# AI METHODS
def train_ann(inputs, targets):
    # use feed forward multilayer perceptron (newff) to train the network
    ann.estimateNEWFF(inputs, targets)


def activate_ann(inputs):
    result = ann.activate(inputs)
    return result


def cluster_kmeans(inputs, clusterCount):
    results = kmeans.cluster(inputs, clusterCount)

    print("\nClusters\n--------")
    for (result, filename) in zip(results, trainFileNames + testFileNames):
        print(str(result) + ": " + filename)

    return results


def run_kmeans(trainFeatures, testFeatures, clusterCount):
    cluster_kmeans(trainFeatures + testFeatures, clusterCount)


def run_ann(trainFeatures, testFeatures, targets):
    train_ann(trainFeatures, targets)

    print("\nClasses\n------")
    for feature, filename in zip(testFeatures, testFileNames):
        result = activate_ann(feature)
        cluster = 0 if result < 0.5 else 1 if result < 1.5 else 2 if result < 2.5 else 3
        print(genres[cluster] + ": " + filename)


if __name__ == "__main__":
    trainTracks = get_tracks(genres, trainPath, trainFileNames)
    testTracks = get_tracks(genres, testPath, testFileNames)

    trainFeatures = []
    testFeatures = []
    targets = []

    for tracks in trainTracks:
        for track in tracks:
            print("Loading: " + track.filename)
            track.features = extract_features(track)
            trainFeatures.append(track.features)
            targets.append(track.trainValue)

    for tracks in testTracks:
        for track in tracks:
            print("Loading: " + track.filename)
            track.features = extract_features(track)
            testFeatures.append(track.features)

    run_kmeans(trainFeatures, testFeatures, len(genres))
    run_ann(trainFeatures, testFeatures, targets)
