import os
import pickle
import warnings
import librosa
import numpy as np
import pandas as pd
from sklearn.cluster import AgglomerativeClustering
from sklearn.preprocessing import StandardScaler, normalize
from sklearn.mixture import *
from matplotlib import pyplot as plt
import numpy as np


class VoiceActivitySpeakerDiarization:
    def __init__(self, audio, segLen=3, frameRate=50, numMix=128):
        self.segLen = segLen
        self.frameRate = frameRate
        self.numMix = numMix
        self.mfcc = None
        self.vad = None
        self.wavFile = None
        self.audio = audio


    def VoiceActivityDetection(self, wavData):
        # uses the librosa library to compute short-term energy
        ste = librosa.feature.rms(y = wavData,hop_length=int(16000/self.frameRate)).T
        thresh = 0.1*(np.percentile(ste,97.5) + 9*np.percentile(ste,2.5))    # Trim 5% off and set threshold as 0.1x of the ste range
        return (ste>thresh).astype('bool')


    # GMM Training
    def trainGMM(self):
        wavFile = self.audio
        wavData, _ = librosa.load(wavFile,sr=16000)
        vad = self.VoiceActivityDetection(wavData)

        mfcc = librosa.feature.mfcc(y = wavData, sr=16000, n_mfcc=20,hop_length=int(16000/self.frameRate)).T
        vad = np.reshape(vad,(len(vad),))
        if mfcc.shape[0] > vad.shape[0]:
            vad = np.hstack((vad,np.zeros(mfcc.shape[0] - vad.shape[0]).astype('bool'))).astype('bool')
        elif mfcc.shape[0] < vad.shape[0]:
            vad = vad[:mfcc.shape[0]]
        mfcc = mfcc[vad, :]

        wavData,_ = librosa.load(wavFile,sr=16000)
        mfcc = librosa.feature.mfcc(y =wavData, sr=16000, n_mfcc=20,hop_length=int(16000/self.frameRate)).T
        vad = np.reshape(vad,(len(vad),))
        if mfcc.shape[0] > vad.shape[0]:
            vad = np.hstack((vad,np.zeros(mfcc.shape[0] - vad.shape[0]).astype('bool'))).astype('bool')
        elif mfcc.shape[0] < vad.shape[0]:
            vad = vad[:mfcc.shape[0]]
        mfcc = mfcc[vad, :]

        self.mfcc = mfcc
        self.vad = vad
        self.wavFile = wavFile

        print("Training GMM..")
        GMM = GaussianMixture(n_components=self.numMix,covariance_type='diag').fit(mfcc)
        var_floor = 1e-5
        segLikes = []
        segSize = self.frameRate*self.segLen
        for segI in range(int(np.ceil(float(mfcc.shape[0])/(self.frameRate*self.segLen)))):
            startI = segI*segSize
            endI = (segI+1)*segSize
            if endI > mfcc.shape[0]:
                endI = mfcc.shape[0]-1
            if endI==startI:    # Reached the end of file
                break
            seg = mfcc[startI:endI,:]
            compLikes = np.sum(GMM.predict_proba(seg),0)
            segLikes.append(compLikes/seg.shape[0])
        print("Training Done")
        return np.asarray(segLikes)

    
    def SegmentFrame(self, clust):#, numFrames):
        numFrames = self.mfcc.shape[0]

        frameClust = np.zeros(numFrames)
        for clustI in range(len(clust)-1):
            frameClust[clustI*self.segLen*self.frameRate:(clustI+1)*self.segLen*self.frameRate] = clust[clustI]*np.ones(self.segLen*self.frameRate)
        frameClust[(clustI+1)*self.segLen*self.frameRate:] = clust[clustI+1]*np.ones(numFrames-(clustI+1)*self.segLen*self.frameRate)
        return frameClust


    # Convert Segments to frame
    def speakerdiarisationdf(self, hyp, wavFile):
        audioname=[]
        starttime=[]
        endtime=[]
        speakerlabel=[]
                
        spkrChangePoints = np.where(hyp[:-1] != hyp[1:])[0]
        if spkrChangePoints[0]!=0 and hyp[0]!=-1:
            spkrChangePoints = np.concatenate(([0],spkrChangePoints))
        spkrLabels = []    
        for spkrHomoSegI in range(len(spkrChangePoints)):
            spkrLabels.append(hyp[spkrChangePoints[spkrHomoSegI]+1])
        for spkrI,spkr in enumerate(spkrLabels[:-1]):
            if spkr!=-1:
                audioname.append(wavFile.split('/')[-1].split('.')[0]+".wav")
                starttime.append((spkrChangePoints[spkrI]+1)/float(self.frameRate))
                endtime.append((spkrChangePoints[spkrI+1]-spkrChangePoints[spkrI])/float(self.frameRate))
                speakerlabel.append("Speaker "+str(int(spkr)))
        if spkrLabels[-1]!=-1:
            audioname.append(wavFile.split('/')[-1].split('.')[0]+".wav")
            starttime.append(spkrChangePoints[-1]/float(self.frameRate))
            endtime.append((len(hyp) - spkrChangePoints[-1])/float(self.frameRate))
            speakerlabel.append("Speaker "+str(int(spkrLabels[-1])))
        #
        speakerdf=pd.DataFrame({"Audio":audioname,"starttime":starttime,"endtime":endtime,"speakerlabel":speakerlabel})
        
        spdatafinal=pd.DataFrame(columns=['Audio','SpeakerLabel','StartTime','EndTime'])
        i=0
        k=0
        j=0
        spfind=""
        stime=""
        etime=""
        for i, row in enumerate(speakerdf.itertuples()):
            if(i==0):
                spfind=row.speakerlabel
                stime=row.starttime
            else:
                if(spfind==row.speakerlabel):
                    etime=row.starttime        
                else:
                    spdatafinal.loc[k]=[wavFile.split('/')[-1].split('.')[0]+".wav",spfind,stime,row.starttime]
                    k=k+1
                    spfind=row.speakerlabel
                    stime=row.starttime
            # i=i+1
        spdatafinal.loc[k]=[wavFile.split('/')[-1].split('.')[0]+".wav",spfind,stime,etime]
        return spdatafinal


    def main(self):
        clusterset = self.trainGMM()

        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(clusterset)  
        # Normalizing the data so that the data approximately 
        # follows a Gaussian distribution
        X_normalized = normalize(X_scaled)

        cluster = AgglomerativeClustering(n_clusters=2, affinity='euclidean', linkage='ward') 
        clust=cluster.fit_predict(X_normalized)

        frameClust = self.SegmentFrame(clust)

        pass1hyp = -1*np.ones(len(self.vad))
        pass1hyp[self.vad] = frameClust
        spkdf=self.speakerdiarisationdf(pass1hyp, self.wavFile)

        spkdf["TimeSeconds"]=spkdf.EndTime-spkdf.StartTime

        return spkdf