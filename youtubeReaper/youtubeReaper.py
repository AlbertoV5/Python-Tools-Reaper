#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Import a youtube video audio from url to reaper

1. Create a new empty item
2. Name that item with the url of the video
3. Run script/action

"""

from pytube import YouTube
from reapy import reascript_api as reaper
from pathlib import Path

projPath = Path(reaper.GetProjectPath('',512)[0])

class Item():
    def __init__(self, item):
        self.item = item
        self.itemLength = reaper.GetMediaItemInfo_Value(item, 'D_LENGTH')
        self.position = reaper.GetMediaItemInfo_Value(item, 'D_POSITION')
        self.activeTake = reaper.GetActiveTake(item)
        self.takeName = reaper.GetSetMediaItemTakeInfo_String(self.activeTake, 'P_NAME', '', False)[3]
        self.itemTrack = reaper.GetMediaItem_Track(item)

smi = reaper.CountSelectedMediaItems(0)

if smi > 0:
    items = [Item(reaper.GetSelectedMediaItem(0,i)) for i in range(smi)]
    for i in items:
        try:            
            yt = YouTube(i.takeName) 
            audio = yt.streams.filter(only_audio=True).all()[0]
            audio.download(projPath)
            fileName = projPath / str(yt.title.replace('\\','').replace('/','') + '.' + str(audio.subtype)) # Solve path issues as pytube does
    
            user = reaper.ShowMessageBox(yt.title, 'Downloaded!', 0)
            
            newItem = reaper.AddMediaItemToTrack(i.itemTrack)
            reaper.SetMediaItemLength(newItem, i.itemLength, False)
            reaper.SetMediaItemPosition(newItem, i.position, False)
            
            activeTake = reaper.AddTakeToMediaItem(newItem) # Create take for item
            reaper.SetMediaItemTake_Source(activeTake,reaper.PCM_Source_CreateFromFile(str(fileName))) #
            reaper.GetSetMediaItemTakeInfo_String(activeTake, 'P_NAME', yt.author + ' - ' + yt.title, True)
        except:
            reaper.ShowMessageBox('Something went wrong, make sure the url is correct.', 'Error', 0)
            
    reaper.Main_OnCommand(40697,1) #Remove url Items
    reaper.Main_OnCommand(40047,1) #Build missing peaks
    reaper.UpdateArrange()

else:    
    reaper.ShowMessageBox('No items selected.', 'Error', 0)

